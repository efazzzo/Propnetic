#!/usr/bin/env python3
# Prophealth_3.py

import streamlit as st
st.set_page_config(page_title="Property Health Intelligence Platform", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")
import pandas as pd
import numpy as np
import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import requests

def render_custom_metric_card_style():
    st.markdown("""
        <style>
        .metric-card {
            padding: 1rem 1.5rem;
            border-radius: 0.75rem;
            color: white;
            margin-bottom: 1rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease-in-out;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        .metric-card h3 {
            color: white !important;
            margin-bottom: 0.3rem;
            font-size: 1rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric-card p.value {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.1rem;
            line-height: 1.2;
        }
        .metric-card small.delta {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        .bg-green-custom { background-color: #28a745; }
        .bg-yellow-custom { background-color: #ffc107; color: #212529 !important; }
        .bg-yellow-custom h3 { color: #212529 !important; }
        .bg-yellow-custom p.value { color: #212529 !important; }
        .bg-yellow-custom small.delta { color: #212529 !important; opacity: 0.7;}
        .bg-red-custom { background-color: #dc3545; }
        .bg-blue-custom { background-color: #007bff; }
        .bg-teal-custom { background-color: #17a2b8; }
        </style>
    """, unsafe_allow_html=True)

@dataclass
class Property:
    address: str
    city: str
    state: str
    zip_code: str
    year_built: int
    square_footage: int
    property_type: str
    roof_material: str
    foundation_type: str
    hvac_age: int
    electrical_age: int
    plumbing_age: int
    last_inspection: str
    image_data: Optional[bytes] = None

@dataclass
class MaintenanceRecord:
    date: str
    category: str
    description: str
    cost: float
    contractor: str
    urgency: str
    property_address: str

@st.cache_data(ttl=600) 
def get_weather_data(zip_code: str, api_key: str) -> Optional[Dict[str, Any]]:
    if not api_key:
        return {"error": "API key not provided."}
    if not zip_code:
        return {"error": "ZIP code not provided."}

    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "zip": f"{zip_code.strip()},us",
        "appid": api_key,
        "units": "imperial"
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("cod") != 200:
             return {"error": data.get("message", "Unknown API error")}

        weather_info = {
            "temp": data.get("main", {}).get("temp"),
            "feels_like": data.get("main", {}).get("feels_like"),
            "humidity": data.get("main", {}).get("humidity"),
            "description": data.get("weather", [{}])[0].get("description", "N/A").capitalize(),
            "icon": data.get("weather", [{}])[0].get("icon"),
            "wind_speed": data.get("wind", {}).get("speed"),
            "city_name": data.get("name", "N/A"),
            "error": None
        }
        if weather_info["temp"] is None or weather_info["icon"] is None:
            return {"error": "Incomplete weather data received."}
        return weather_info
    except requests.exceptions.HTTPError as http_err:
        status_code = http_err.response.status_code if http_err.response is not None else None
        if status_code == 401:
            return {"error": "Invalid API key. Please check your key in Streamlit Secrets."}
        elif status_code == 404:
            return {"error": f"Weather data not found for ZIP code: {zip_code}."}
        else:
            return {"error": f"HTTP error: {http_err}"}
    except requests.exceptions.RequestException as req_err:
        return {"error": f"Network error: {req_err}"}
    except ValueError as json_err: 
        return {"error": f"Error parsing weather data: {json_err}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

class PropertyHealthCalculator:
    def __init__(self):
        self.weights = {'structural': 0.3, 'systems': 0.4, 'safety': 0.2, 'environmental': 0.1}
        self.national_cost_baseline = {
            "hvac_service": {"min": 200, "max": 500, "avg": 350},
            "hvac_replacement": {"min": 5000, "max": 12000, "avg": 7500},
            "roof_repair": {"min": 400, "max": 2000, "avg": 1000},
            "roof_replacement": {"min": 10000, "max": 30000, "avg": 15000},
            "electrical_panel": {"min": 1500, "max": 4000, "avg": 2500},
            "plumbing_repair": {"min": 250, "max": 1000, "avg": 600},
            "water_heater": {"min": 1000, "max": 3500, "avg": 1800},
            "foundation_repair": {"min": 3000, "max": 25000, "avg": 10000},
            "gutter_replacement": {"min": 1000, "max": 3000, "avg": 1700}
        }
        self.regional_multipliers = {
            "22701": {"multiplier": 0.85, "region": "Central Virginia - Rural", "confidence": "high"},
            "22102": {"multiplier": 1.35, "region": "Northern Virginia - DC Metro", "confidence": "high"},
            "10001": {"multiplier": 1.85, "region": "Manhattan, NY", "confidence": "high"},
            "90210": {"multiplier": 1.65, "region": "Los Angeles Metro", "confidence": "high"},
            "94102": {"multiplier": 1.75, "region": "San Francisco Bay Area", "confidence": "high"},
            "60601": {"multiplier": 1.25, "region": "Chicago Metro", "confidence": "high"},
            "2": {"multiplier": 1.45, "region": "Northeast Corridor", "confidence": "medium"},
            "9": {"multiplier": 1.40, "region": "West Coast", "confidence": "medium"},
            "default": {"multiplier": 1.00, "region": "National Average", "confidence": "low"}
        }

    def get_regional_info(self, zip_code: str) -> Dict:
        if zip_code in self.regional_multipliers:
            return self.regional_multipliers[zip_code]
        if zip_code and zip_code[0] in self.regional_multipliers: # Check first digit as fallback
            return self.regional_multipliers[zip_code[0]]
        return self.regional_multipliers["default"]

    def get_local_cost_estimate(self, item_type: str, zip_code: str = "22701") -> Dict:
        if item_type not in self.national_cost_baseline:
            return {"min": 0, "max": 0, "avg": 0, "confidence": "low", "region": "Unknown", "national_avg": 0}
        baseline = self.national_cost_baseline[item_type]
        regional_info = self.get_regional_info(zip_code)
        multiplier = regional_info["multiplier"]
        return {
            "min": int(baseline["min"] * multiplier),
            "max": int(baseline["max"] * multiplier),
            "avg": int(baseline["avg"] * multiplier),
            "confidence": regional_info["confidence"],
            "region": regional_info["region"],
            "national_avg": baseline["avg"]
        }

    def calculate_age_score(self, age: int, expected_life: int) -> float:
        if age <= 0: return 100.0
        if expected_life <=0: return 0.0 # Avoid division by zero
        ratio = age / expected_life
        if ratio <= 0.5: return 100.0 - (ratio * 20.0) # Linear decline from 100 to 90
        elif ratio <= 0.8: return 90.0 - ((ratio - 0.5) / 0.3 * 30.0) # Linear decline from 90 to 60
        else: return max(0.0, 60.0 - ((ratio - 0.8) / 0.2 * 60.0)) # Linear decline from 60 to 0

    def calculate_structural_score(self, property_data: Property) -> Dict:
        current_year = datetime.datetime.now().year
        age = current_year - property_data.year_built
        foundation_scores = {'Concrete Slab': 85, 'Basement': 90, 'Crawl Space': 75, 'Pier & Beam': 70}
        roof_scores = {'Asphalt Shingles': 80, 'Metal': 90, 'Tile': 95, 'Slate': 98, 'Wood': 70, 'Composite': 75, 'Flat Roof (TPO/EPDM)': 70}
        
        age_score = self.calculate_age_score(age, 80) # Assuming general building life
        foundation_score = foundation_scores.get(property_data.foundation_type, 75)
        roof_score = roof_scores.get(property_data.roof_material, 80)
        
        overall_score = (age_score * 0.4 + foundation_score * 0.3 + roof_score * 0.3)
        return {'score': round(overall_score, 1), 'components': {'Age Factor': round(age_score, 1), 'Foundation': foundation_score, 'Roof Material': roof_score}}

    def calculate_systems_score(self, property_data: Property) -> Dict:
        hvac_score = self.calculate_age_score(property_data.hvac_age, 15)
        electrical_score = self.calculate_age_score(property_data.electrical_age, 40)
        plumbing_score = self.calculate_age_score(property_data.plumbing_age, 50)
        overall_score = (hvac_score * 0.4 + electrical_score * 0.3 + plumbing_score * 0.3)
        return {'score': round(overall_score, 1), 'components': {'HVAC': round(hvac_score, 1), 'Electrical': round(electrical_score, 1), 'Plumbing': round(plumbing_score, 1)}}

    def calculate_safety_score(self, property_data: Property) -> Dict:
        base_score = 85.0
        current_year = datetime.datetime.now().year
        age = current_year - property_data.year_built
        if age > 30: base_score -= 10
        if age > 50: base_score -= 10 # Cumulative, so -20 if > 50
        # Placeholder: Could be enhanced with last_inspection date
        return {'score': round(base_score, 1), 'components': {'General Safety': round(base_score,1)}}

    def calculate_environmental_score(self, property_data: Property) -> Dict:
        base_score = 80.0
        # Placeholder: Could be enhanced with local environmental factors, weather data in future
        return {'score': round(base_score, 1), 'components': {'General Environmental': round(base_score,1)}}

    def calculate_overall_score(self, property_data: Property) -> Dict:
        structural = self.calculate_structural_score(property_data)
        systems = self.calculate_systems_score(property_data)
        safety = self.calculate_safety_score(property_data)
        environmental = self.calculate_environmental_score(property_data)
        
        overall = (structural['score'] * self.weights['structural'] +
                   systems['score'] * self.weights['systems'] +
                   safety['score'] * self.weights['safety'] +
                   environmental['score'] * self.weights['environmental'])
        return {
            'overall_score': round(overall, 1),
            'category_scores': {
                'Structural': structural,
                'Systems': systems,
                'Safety': safety,
                'Environmental': environmental
            }
        }

    def generate_maintenance_schedule(self, property_data: Property) -> List[Dict]:
        schedule = []
        current_date = datetime.datetime.now()
        zip_code = property_data.zip_code

        # HVAC
        if property_data.hvac_age <= 1: # New or very new
             cost_est_filter = self.get_local_cost_estimate("hvac_service", zip_code) # Use service as proxy for filter cost
             schedule.append({"task": "HVAC Filter Check/Replacement", "frequency": "Every 3 months", "next_due": current_date + datetime.timedelta(days=90), "priority": "routine", "estimated_cost": max(20, cost_est_filter["min"] // 10) , "description": "Check and replace air filters as needed."})
        elif property_data.hvac_age <= 12: # Mid-life
            cost_est_service = self.get_local_cost_estimate("hvac_service", zip_code)
            schedule.append({"task": "HVAC Annual Service", "frequency": "Annually", "next_due": current_date + datetime.timedelta(days=365), "priority": "important", "estimated_cost": cost_est_service["avg"], "description": "Professional tune-up and inspection."})
        else: # Old, nearing replacement
            cost_est_repl = self.get_local_cost_estimate("hvac_replacement", zip_code)
            schedule.append({"task": "HVAC Replacement Planning", "frequency": "Within 1-2 years", "next_due": current_date + datetime.timedelta(days=365), "priority": "high", "estimated_cost": cost_est_repl["avg"], "description": "Budget and plan for HVAC system replacement."})

        # Electrical
        if property_data.electrical_age > 30:
            cost_est_panel_check = self.get_local_cost_estimate("electrical_panel", zip_code) 
            schedule.append({"task": "Electrical System Inspection", "frequency": "Consider within 1 year", "next_due": current_date + datetime.timedelta(days=365), "priority": "important", "estimated_cost": max(150, cost_est_panel_check["min"] // 5) , "description": "Inspect aging electrical panel and system, especially if over 30 years old."})
        if property_data.electrical_age > 40:
             schedule.append({"task": "Consider Electrical Panel Upgrade", "frequency": "Within 2-3 years", "next_due": current_date + datetime.timedelta(days=730), "priority": "high", "estimated_cost": self.get_local_cost_estimate("electrical_panel", zip_code)["avg"], "description": "Plan for upgrading an old electrical panel if original."})

        # Plumbing & Water Heater (assuming general plumbing age might indicate water heater age too)
        if property_data.plumbing_age > 8 : # Water heaters typically last 8-12 years
            cost_est_wh_service = self.get_local_cost_estimate("water_heater", zip_code) # Using replacement as proxy for service/check
            schedule.append({"task": "Water Heater Check/Service", "frequency": "Annually if >8yrs old", "next_due": current_date + datetime.timedelta(days=365), "priority": "important", "estimated_cost": max(100, cost_est_wh_service["min"] // 10), "description": "Inspect water heater. Plan for replacement if near end-of-life."})
        if property_data.plumbing_age > 40: # Older home, check main pipes
             cost_est_pipe_repair = self.get_local_cost_estimate("plumbing_repair", zip_code)
             schedule.append({"task": "Major Plumbing Inspection (Pipes)", "frequency": "Consider within 2 years", "next_due": current_date + datetime.timedelta(days=730), "priority": "high", "estimated_cost": cost_est_pipe_repair["avg"], "description": "Inspect for potential major plumbing updates (pipes, main lines) if original."})

        # Roof (using property age as a very rough proxy if no specific roof age is available)
        property_age = current_date.year - property_data.year_built
        if property_age > 15 : # Generic roof inspection for older properties
            cost_est_roof_insp = self.get_local_cost_estimate("roof_repair", zip_code) # Using repair as proxy for inspection cost
            schedule.append({"task": "Roof Inspection", "frequency": "Annually", "next_due": current_date + datetime.timedelta(days=365), "priority": "important", "estimated_cost": max(150,cost_est_roof_insp["min"]), "description": "Inspect roof for wear, potential leaks, and clear debris."})

        # General / Seasonal
        cost_est_gutter = self.get_local_cost_estimate("gutter_replacement", zip_code)
        gutter_clean_cost = max(150, cost_est_gutter["min"] // 10 if cost_est_gutter["min"] > 0 else 150)

        schedule.append({"task": "Gutter Cleaning (Spring)", "frequency": "Annually (Spring)", "next_due": current_date + datetime.timedelta(days=120), "priority": "routine", "estimated_cost": gutter_clean_cost , "description": "Clean gutters and downspouts after winter."})
        schedule.append({"task": "Gutter Cleaning (Fall)", "frequency": "Annually (Fall)", "next_due": current_date + datetime.timedelta(days=300), "priority": "routine", "estimated_cost": gutter_clean_cost, "description": "Clean gutters and downspouts before winter."})
        schedule.append({"task": "Exterior Caulking & Sealing Check", "frequency": "Annually", "next_due": current_date + datetime.timedelta(days=270), "priority": "routine", "estimated_cost": 100, "description": "Check windows, doors, and siding for gaps to prevent drafts and water intrusion."})
        schedule.append({"task": "Smoke & CO Detector Test/Battery Change", "frequency": "Semi-Annually", "next_due": current_date + datetime.timedelta(days=180), "priority": "important", "estimated_cost": 10, "description": "Test all detectors and replace batteries as needed."})


        schedule.sort(key=lambda x: ({"high": 0, "important": 1, "routine": 2}[x["priority"]], x["next_due"]))
        return schedule

class AuthenticationManager:
    def __init__(self):
        self.password = "PropHealth2025!" # Simple prototype password

    def render_auth_screen(self):
        st.markdown("""<style>
        .auth-container {max-width: 600px; margin: 2rem auto; padding: 2rem 2.5rem; background: #ffffff; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); color: #333;}
        .auth-container h1 { color: #764ba2; text-align: center; }
        .auth-container h3 { color: #667eea; margin-top:1.5rem; margin-bottom:0.5rem; }
        .stButton>button {width: 100%; background-color: #667eea; color:white; border-radius: 8px; padding: 0.75rem 0;}
        .stButton>button:hover {background-color: #764ba2;}
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {border-radius: 8px !important;}
        .stAlert {border-radius: 8px;}
        </style>""", unsafe_allow_html=True)
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown("# 🏠 Property Health Intelligence Platform")
        st.markdown("### *Prototype Access Portal*")

        st.markdown("#### Confidential Preview Access")
        st.info("🔒 This is a confidential prototype demonstration. Access implies agreement to confidentiality and IP respect.", icon="ℹ️")

        col1, col2 = st.columns(2)
        with col1:
            confidential_understood = st.checkbox("Acknowledge Confidentiality", key="auth_conf_checkbox")
            respect_ip = st.checkbox("Respect Intellectual Property", key="auth_ip_checkbox")
        with col2:
            professional_courtesy = st.checkbox("Agree to Professional Standards", key="auth_courtesy_checkbox")
            authorized_access = st.checkbox("Authorized Stakeholder", key="auth_stakeholder_checkbox")

        st.markdown("#### Digital Signature")
        st.text_input("Full Name *", placeholder="Enter your full name", key="auth_full_name")
        st.text_input("Email Address *", placeholder="your.email@company.com", key="auth_email_address")
        st.text_input("Company/Organization", placeholder="Your company", key="auth_company_org")
        st.selectbox("Purpose of Access *",
                             ["", "Potential Investor", "Business Partner", "Industry Professional", "Internal Review", "Other"],
                             index=0, key="auth_access_purpose")

        st.markdown("#### Access Code")
        st.text_input("Enter access code:", type="password", placeholder="Access code required", key="auth_password_input")

        # Retrieve values from session state for logic
        s_full_name = st.session_state.get("auth_full_name", "")
        s_email_address = st.session_state.get("auth_email_address", "")
        s_access_purpose = st.session_state.get("auth_access_purpose", "")
        s_password_input = st.session_state.get("auth_password_input", "")

        all_acknowledged = confidential_understood and respect_ip and professional_courtesy and authorized_access
        password_correct = s_password_input == self.password
        signature_complete = s_full_name.strip() != "" and s_email_address.strip() != "" and s_access_purpose != ""
        # Basic email validation
        email_valid = "@" in s_email_address and "." in s_email_address.split('@')[-1] if s_email_address and "@" in s_email_address else False


        access_button_disabled = not (all_acknowledged and signature_complete and email_valid and s_password_input)

        if st.button("🚀 ACCESS PREVIEW", type="primary", disabled=access_button_disabled):
            if password_correct:
                st.session_state.access_info = {
                    'name': st.session_state.get("auth_full_name", ""), # Use .get for safety
                    'email': st.session_state.get("auth_email_address", ""),
                    'company': st.session_state.get("auth_company_org", ""),
                    'purpose': st.session_state.get("auth_access_purpose", ""),
                    'timestamp': datetime.datetime.now()
                }
                st.session_state.authenticated = True
                st.session_state.access_timestamp = datetime.datetime.now() # Record access time
                st.success("✅ Access granted! Loading platform...")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Invalid access code or missing required fields/acknowledgments. Please check all inputs.")
        
        st.markdown("<hr style='margin: 1.5rem 0;'/><p style='text-align:center; font-size:0.9rem;'>For inquiries, contact: JESquared24@gmail.com</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


    def is_authenticated(self):
        return st.session_state.get('authenticated', False)

    def render_session_info(self):
        if self.is_authenticated():
            access_info = st.session_state.get('access_info', {})
            st.sidebar.markdown("---")
            st.sidebar.markdown("**🛡️ Authorized Session**")
            if access_info.get('name'):
                st.sidebar.markdown(f"**User:** {access_info['name']}")
            # Logout button
            if st.sidebar.button("🚪 End Session & Logout", type="secondary", use_container_width=True):
                # Clear all relevant session state keys
                keys_to_clear = [k for k in st.session_state.keys() if k.startswith('auth_')]
                keys_to_clear.extend(['access_info', 'authenticated', 'access_timestamp', 
                                      'show_add_property_form', 'show_add_maintenance_form', 'active_tab',
                                      'maintenance_filter_urgency']) 
                # Clear property selector states
                keys_to_clear.extend([k for k in st.session_state.keys() if k.startswith('selected_property_address_')])
                # Clear ROI calculator states
                keys_to_clear.extend([k for k in st.session_state.keys() if k.startswith('roi_')])
                
                for key_to_del in keys_to_clear:
                    if key_to_del in st.session_state:
                        del st.session_state[key_to_del]
                
                # Optionally, clear properties and maintenance_records if desired on logout
                # if 'properties' in st.session_state: del st.session_state.properties
                # if 'maintenance_records' in st.session_state: del st.session_state.maintenance_records

                st.success("Logged out successfully. Session data cleared.")
                st.rerun()

class Dashboard:
    def __init__(self):
        self.calculator = PropertyHealthCalculator()
        self.auth_manager = AuthenticationManager()
        self.init_session_state()
        render_custom_metric_card_style()

    def init_session_state(self):
        # Initialize core data structures
        if 'properties' not in st.session_state:
            st.session_state.properties = [] # List to store Property objects
        if 'maintenance_records' not in st.session_state:
            st.session_state.maintenance_records = [] # List to store MaintenanceRecord objects

        # UI state flags
        if 'show_add_property_form' not in st.session_state:
            st.session_state.show_add_property_form = False # Default to closed
        if 'show_add_maintenance_form' not in st.session_state:
            st.session_state.show_add_maintenance_form = False # Default to closed
        if 'active_tab' not in st.session_state:
             st.session_state.active_tab = "📈 Property Health" # Default active tab

        # ROI calculator inputs
        if 'roi_property_address' not in st.session_state: # Stores the address string
            st.session_state.roi_property_address = None
        if 'roi_improvement_name' not in st.session_state:
            st.session_state.roi_improvement_name = ""
        if 'roi_estimated_cost' not in st.session_state:
            st.session_state.roi_estimated_cost = 0.0
        if 'roi_resale_value_increase' not in st.session_state:
            st.session_state.roi_resale_value_increase = 0.0
        if 'roi_annual_savings' not in st.session_state:
            st.session_state.roi_annual_savings = 0.0
        if 'roi_years_to_project' not in st.session_state:
            st.session_state.roi_years_to_project = 5
        # openweathermap_api_key is handled by st.secrets, not session state

    def render_header(self):
        st.title("🏠 Property Health Intelligence Dashboard")
        st.markdown("Your partner in proactive property care. *Beta Preview v0.6*")
        st.markdown("---")
        # Metric cards display...
        cols = st.columns(5) 
        total_props = len(st.session_state.properties)
        with cols[0]:
            st.markdown(f"""
                <div class="metric-card bg-blue-custom">
                    <h3>Total Properties</h3>
                    <p class="value">{total_props}</p>
                    <small class="delta">Currently Managed</small>
                </div>
            """, unsafe_allow_html=True)

        avg_score_val = 0
        avg_score_str = "N/A"
        avg_score_color = "bg-blue-custom"
        if st.session_state.properties:
            try:
                scores = [self.calculator.calculate_overall_score(prop)['overall_score'] for prop in st.session_state.properties]
                if scores: 
                    avg_score_val = np.mean(scores)
                    avg_score_str = f"{avg_score_val:.1f}"
                    if avg_score_val >= 85: avg_score_color = "bg-green-custom"
                    elif avg_score_val >= 70: avg_score_color = "bg-yellow-custom"
                    else: avg_score_color = "bg-red-custom"
            except Exception as e: # Catch potential errors if a property score can't be calculated
                avg_score_str = "Error"
                avg_score_color = "bg-red-custom"
                print(f"Error calculating avg_score: {e}") # Log error for debugging

        with cols[1]:
            st.markdown(f"""
                <div class="metric-card {avg_score_color}">
                    <h3>Average Health</h3>
                    <p class="value">{avg_score_str}</p>
                    <small class="delta">Overall Portfolio Score</small>
                </div>
            """, unsafe_allow_html=True)

        urgent_items_count = len([r for r in st.session_state.maintenance_records if r.urgency == "High"])
        urgent_color = "bg-green-custom" if urgent_items_count == 0 else "bg-yellow-custom" if urgent_items_count < 3 else "bg-red-custom"
        with cols[2]:
            st.markdown(f"""
                <div class="metric-card {urgent_color}">
                    <h3>Urgent Items</h3>
                    <p class="value">{urgent_items_count}</p>
                    <small class="delta">Requiring Immediate Attention</small>
                </div>
            """, unsafe_allow_html=True)

        total_cost = sum([r.cost for r in st.session_state.maintenance_records])
        with cols[3]:
            st.markdown(f"""
                <div class="metric-card bg-teal-custom">
                    <h3>Total Maint. Cost</h3>
                    <p class="value">${total_cost:,.0f}</p>
                    <small class="delta">Logged Expenditures</small>
                </div>
            """, unsafe_allow_html=True)

        preventative_maintenance_cost = sum(r.cost for r in st.session_state.maintenance_records if r.urgency in ["Routine", "Medium"])
        estimated_savings = preventative_maintenance_cost * 0.15 # Simple placeholder heuristic
        with cols[4]:
            st.markdown(f"""
                <div class="metric-card bg-green-custom">
                    <h3>Est. Savings</h3>
                    <p class="value">${estimated_savings:,.0f}</p>
                    <small class="delta">From Proactive Care (Est.)</small>
                </div>
            """, unsafe_allow_html=True)

    def render_quick_actions(self):
        st.sidebar.subheader("⚡ Quick Actions")
        if st.sidebar.button("➕ Add New Property", use_container_width=True, key="quick_add_prop_btn"):
            st.session_state.show_add_property_form = not st.session_state.get('show_add_property_form', False)
            if st.session_state.show_add_property_form: # if we just opened it
                 st.session_state.show_add_maintenance_form = False # close the other form
            st.rerun()

        add_maint_disabled = not st.session_state.properties # Disable if no properties
        if st.sidebar.button("📝 Log Maintenance Task", use_container_width=True, disabled=add_maint_disabled, key="quick_log_maint_btn"):
            st.session_state.show_add_maintenance_form = not st.session_state.get('show_add_maintenance_form', False)
            if st.session_state.show_add_maintenance_form: # if we just opened it
                st.session_state.show_add_property_form = False # close the other form
            st.rerun()
        
        # Button to quickly view urgent tasks
        view_urgent_disabled = not any(r.urgency == "High" for r in st.session_state.maintenance_records)
        if st.sidebar.button("❗ View Urgent Tasks", use_container_width=True, disabled=view_urgent_disabled, key="quick_view_urgent_btn"):
            st.session_state.active_tab = "🧰 Maintenance Center" # Switch to maintenance tab
            st.session_state.maintenance_filter_urgency = "High"  # Pre-set filter
            st.toast("Switched to Maintenance tab with 'High' urgency filter.", icon="❗")
            st.rerun()

    def render_property_management(self):
        st.sidebar.header("🏡 Property Portfolio")
        expanded_add_prop = st.session_state.get('show_add_property_form', False)
        with st.sidebar.expander("➕ Add New Property", expanded=expanded_add_prop):
            with st.form("property_form", clear_on_submit=True):
                address = st.text_input("Property Address *")
                city = st.text_input("City *")
                state = st.text_input("State *", max_chars=2, help="E.g., VA, NC, CA")
                zip_code = st.text_input("ZIP Code *", value="22701", help="For regional cost estimates and local context.")
                
                year_built = st.number_input("Year Built", min_value=1800, max_value=datetime.datetime.now().year, value=2000, step=1)
                square_footage = st.number_input("Square Footage", min_value=100, max_value=20000, value=1500, step=50)
                property_type = st.selectbox("Property Type", ["Single Family", "Townhouse", "Condo", "Multi-Family", "Commercial"])
                roof_material = st.selectbox("Roof Material", ["Asphalt Shingles", "Metal", "Tile", "Slate", "Wood", "Composite", "Flat Roof (TPO/EPDM)"])
                foundation_type = st.selectbox("Foundation Type", ["Concrete Slab", "Basement", "Crawl Space", "Pier & Beam"])
                hvac_age = st.number_input("HVAC Age (years)", min_value=0, max_value=50, value=5, step=1)
                electrical_age = st.number_input("Electrical System Age (years)", min_value=0, max_value=100, value=15, step=1)
                plumbing_age = st.number_input("Plumbing System Age (years)", min_value=0, max_value=100, value=20, step=1)
                last_inspection_date = st.date_input("Last Major Inspection Date", value=None) # Allow None
                
                uploaded_photo = st.file_uploader("Upload Property Photo (Optional)", type=["png", "jpg", "jpeg"])
                submitted = st.form_submit_button("✅ Add Property to Portfolio", type="primary", use_container_width=True)

                if submitted:
                    if not all([address, city, state, zip_code]):
                        st.error("🚨 Address, City, State, and ZIP Code are required!")
                    else:
                        image_bytes = uploaded_photo.getvalue() if uploaded_photo else None
                        last_inspection_str = last_inspection_date.strftime("%Y-%m-%d") if last_inspection_date else "N/A"
                        new_property = Property(
                            address=address, city=city, state=state.upper(), zip_code=zip_code, # Standardize state to upper
                            year_built=year_built, square_footage=square_footage, property_type=property_type,
                            roof_material=roof_material, foundation_type=foundation_type, 
                            hvac_age=hvac_age, electrical_age=electrical_age, plumbing_age=plumbing_age,
                            last_inspection=last_inspection_str, image_data=image_bytes
                        )
                        st.session_state.properties.append(new_property)
                        st.session_state.show_add_property_form = False # Close expander
                        st.success(f"✅ Property '{address}, {city}, {state.upper()}' added successfully!")
                        st.rerun()

        if st.session_state.properties:
            with st.sidebar.expander("🗑️ Manage Properties"):
                prop_options_display = {
                    f"{i+1}. {prop.address}, {prop.city}, {prop.state.upper()} ({prop.zip_code})": prop.address 
                    for i, prop in enumerate(st.session_state.properties)
                }
                prop_display_labels = [""] + list(prop_options_display.keys())
                
                selected_prop_display_label_to_delete = st.selectbox(
                    "Select property to remove:", 
                    prop_display_labels, 
                    index=0, 
                    key="delete_prop_select"
                )
                
                if selected_prop_display_label_to_delete and selected_prop_display_label_to_delete != "":
                    address_to_delete = prop_options_display[selected_prop_display_label_to_delete]
                    if st.button("🗑️ Delete Selected Property", type="secondary", use_container_width=True, key="delete_prop_btn"):
                        idx_to_delete = -1
                        for i, p_obj in enumerate(st.session_state.properties):
                            if p_obj.address == address_to_delete:
                                idx_to_delete = i
                                break
                        
                        if idx_to_delete != -1:
                            deleted_property_info = f"{st.session_state.properties[idx_to_delete].address}, {st.session_state.properties[idx_to_delete].city}"
                            
                            # Remove associated maintenance records
                            st.session_state.maintenance_records = [
                                record for record in st.session_state.maintenance_records
                                if record.property_address != address_to_delete
                            ]
                            # Remove property
                            del st.session_state.properties[idx_to_delete]
                            st.success(f"🗑️ Property '{deleted_property_info}' and its maintenance records removed.")
                            st.session_state.delete_prop_select = "" # Reset selectbox if needed by clearing key or options change
                            st.rerun()
                        else:
                            st.error("Error finding property to delete. Please refresh.")
    
    def render_maintenance_input(self):
        if not st.session_state.properties:
            return # Button to open this should be disabled anyway

        st.sidebar.header("🛠️ Maintenance Log")
        expanded_add_maint = st.session_state.get('show_add_maintenance_form', False)
        with st.sidebar.expander("➕ Add New Maintenance Record", expanded=expanded_add_maint):
            if not st.session_state.properties: # Should be caught by quick action disable
                 st.warning("Please add a property first using the 'Quick Actions' panel.")
                 return

            property_display_options = {
                f"{prop.address}, {prop.city}, {prop.state.upper()}": prop.address 
                for prop in st.session_state.properties
            }
            display_labels = list(property_display_options.keys())

            with st.form("maintenance_form", clear_on_submit=True):
                selected_display_address = st.selectbox("Select Property *", display_labels, index=0 if display_labels else None)
                actual_address_for_record = property_display_options.get(selected_display_address) if selected_display_address else None
                
                date = st.date_input("Date of Service/Record *", datetime.date.today())
                category = st.selectbox("Category *", ["HVAC", "Plumbing", "Electrical", "Roofing", "Foundation", "Appliances", "Pest Control", "Landscaping", "General Repair", "Inspection", "Other"])
                description = st.text_area("Description of Work / Issue *", height=100)
                cost = st.number_input("Cost ($)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
                contractor = st.text_input("Contractor/Vendor (if any)")
                urgency = st.selectbox("Urgency *", ["Routine", "Medium", "High"])
                submitted = st.form_submit_button("➕ Add Maintenance Record", type="primary", use_container_width=True)

                if submitted:
                    if not actual_address_for_record or not description or not date or not category or not urgency:
                        st.error("🚨 Please fill in all required fields for the maintenance record.")
                    else:
                        new_record = MaintenanceRecord(date.strftime("%Y-%m-%d"), category, description, cost, contractor, urgency, actual_address_for_record)
                        st.session_state.maintenance_records.append(new_record)
                        st.session_state.show_add_maintenance_form = False # Close expander
                        st.success(f"✅ Maintenance record added for '{actual_address_for_record}'.")
                        st.rerun()

    def render_property_selector(self, key_suffix="main", allow_none=False, help_text="Select Property to View Details:"):
        if not st.session_state.properties:
            if key_suffix not in ["contractors", "roi_calc"]: 
                st.info("👈 Add a property via the sidebar to get started!")
            return None

        options_map = { f"{p.address}, {p.city}, {p.state.upper()}" : p.address for p in st.session_state.properties }
        display_options = list(options_map.keys()) 

        session_key_for_selected_address = f"selected_property_address_{key_suffix}"
        
        current_selected_address_val = st.session_state.get(session_key_for_selected_address)
        current_display_selection = None
        if current_selected_address_val:
            for disp_label, addr_val in options_map.items():
                if addr_val == current_selected_address_val:
                    current_display_selection = disp_label
                    break
        
        default_index = 0

        if allow_none:
            display_options_with_none = ["Select a Property..."] + display_options
            if current_display_selection and current_display_selection in display_options_with_none:
                default_index = display_options_with_none.index(current_display_selection)
            elif current_selected_address_val is None: # "Select a Property..." is effectively None
                default_index = 0
            else: # Invalid selection, reset
                st.session_state[session_key_for_selected_address] = None
                default_index = 0
            
            selected_display_val = st.selectbox(help_text, display_options_with_none, index=default_index, key=f"prop_select_box_{key_suffix}")
            st.session_state[session_key_for_selected_address] = options_map.get(selected_display_val) if selected_display_val != "Select a Property..." else None
        
        else: # Not allowing None
            if not display_options: return None 
            if current_display_selection not in display_options or current_display_selection is None:
                st.session_state[session_key_for_selected_address] = options_map[display_options[0]]
                default_index = 0
            else:
                default_index = display_options.index(current_display_selection)
            
            selected_display_val = st.selectbox(help_text, display_options, index=default_index, key=f"prop_select_box_{key_suffix}")
            st.session_state[session_key_for_selected_address] = options_map.get(selected_display_val) 
            
        final_selected_address = st.session_state.get(session_key_for_selected_address)
        if final_selected_address:
            for prop_obj in st.session_state.properties:
                if prop_obj.address == final_selected_address:
                    return prop_obj
        return None

    def render_health_score_visualization(self, property_data: Property):
        scores = self.calculator.calculate_overall_score(property_data)
        
        st.subheader(f"📊 Health Snapshot: {property_data.address}, {property_data.city}, {property_data.state.upper()}")
        
        self.render_weather_display(property_data.zip_code, f"{property_data.address}, {property_data.city}")
        st.markdown("---") 

        cols_main = st.columns([0.4, 0.6]) 
        with cols_main[0]:
            if property_data.image_data:
                st.image(property_data.image_data, caption=f"{property_data.property_type} at {property_data.address}", use_column_width=True)
            else:
                st.markdown("<div style='height: 200px; background-color: #f0f2f6; display: flex; align-items: center; justify-content: center; border-radius: 8px;'><span style='color: #aaa; font-style: italic;'>No property image</span></div>", unsafe_allow_html=True)

        with cols_main[1]:
            overall_score_val = scores['overall_score']
            st.metric("Overall Health Score", f"{overall_score_val:.1f} / 100")

            if overall_score_val >= 85: st.success("Excellent Condition! 👍")
            elif overall_score_val >= 70: st.info("Good Condition. 👌")
            elif overall_score_val >= 55: st.warning("Fair Condition. Proactive maintenance advised. ⚠️")
            else: st.error("Needs Significant Attention! Prioritize repairs. 🔴")
            
            st.write("**Category Breakdown:**")
            for category_name, category_data in scores['category_scores'].items():
                score = category_data['score']
                icon = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                st.markdown(f"{icon} **{category_name}:** {score:.1f}")
        st.markdown("---")

    def render_weather_display(self, property_zip: str, property_address_display: str):
        st.subheader(f"🌦️ Current Weather for {property_address_display} (ZIP: {property_zip})")
        
        api_key = st.secrets.get("OPENWEATHERMAP_API_KEY")

        if not api_key:
            st.warning("OpenWeatherMap API Key not configured in Streamlit Secrets. Weather data unavailable.", icon="🔑")
            st.caption("If running locally, ensure you have a `.streamlit/secrets.toml` file with your key.")
            return

        weather_data = get_weather_data(property_zip, api_key)

        if weather_data:
            if weather_data.get("error"):
                st.error(f"Could not retrieve weather: {weather_data['error']}", icon="⚠️")
            else:
                col1, col2, col3 = st.columns(3)
                if weather_data.get("temp") is not None:
                    col1.metric("Temperature", f"{weather_data['temp']:.0f}°F", 
                                delta=f"Feels like {weather_data.get('feels_like', 'N/A'):.0f}°F" if weather_data.get('feels_like') is not None else None)
                else:
                    col1.metric("Temperature", "N/A")

                desc = weather_data.get('description', 'N/A')
                icon = weather_data.get('icon')
                
                if icon:
                    icon_url = f"https://openweathermap.org/img/wn/{icon}@2x.png"
                    col2.image(icon_url, caption=desc, width=80)
                else:
                    col2.write(desc)

                if weather_data.get("humidity") is not None:
                    col3.metric("Humidity", f"{weather_data['humidity']}%")
                else:
                    col3.metric("Humidity", "N/A")
                
                if weather_data.get("wind_speed") is not None:
                    st.markdown(f"**Wind:** {weather_data['wind_speed']:.1f} mph")
                if weather_data.get("city_name") and weather_data['city_name'] != "N/A":
                     st.caption(f"Reported Location: {weather_data['city_name']}")
        else:
            st.error("Failed to fetch weather data. Check API key or network.", icon="📡")

    def render_detailed_breakdown(self, property_data: Property):
        scores = self.calculator.calculate_overall_score(property_data)
        st.subheader("🔬 Detailed Component Scores")
        for category, data in scores['category_scores'].items():
            with st.expander(f"{category} Details - Overall Score: {data['score']:.1f}", expanded=(category=="Structural")):
                if not data['components']:
                    st.write(f"No specific components listed for {category}.")
                    continue
                
                num_components = len(data['components'])
                comp_cols = st.columns(num_components if num_components > 0 else 1)
                idx = 0
                for component, score_val_raw in data['components'].items():
                    current_col = comp_cols[idx] if num_components > 1 and idx < len(comp_cols) else comp_cols[0] 
                    with current_col:
                        c_score = float(score_val_raw)
                        color = "green" if c_score >= 80 else "orange" if c_score >= 60 else "red"
                        st.markdown(f"**{component}:**")
                        st.markdown(f"<p style='font-size: 1.5em; color:{color}; font-weight:bold;'>{c_score:.1f}</p>", unsafe_allow_html=True)
                    idx+=1
        st.markdown("---")

    def render_maintenance_history(self, property_address: Optional[str]):
        display_address_for_subheader = "Portfolio Wide" # Default for portfolio view
        if property_address:
            prop_obj = next((p for p in st.session_state.properties if p.address == property_address), None)
            if prop_obj:
                display_address_for_subheader = f"{prop_obj.address}, {prop_obj.city}, {prop_obj.state.upper()}"
            else: 
                display_address_for_subheader = property_address # Fallback

        st.subheader(f"🧰 Maintenance History for {display_address_for_subheader}")
        
        if property_address: # Filter records for a specific property
            property_records = [r for r in st.session_state.maintenance_records if r.property_address == property_address]
            if not property_records:
                st.info("No maintenance records found for this property yet.")
        else: # Portfolio wide view (display_address_for_subheader will be "Portfolio Wide")
            property_records = st.session_state.maintenance_records
            if not property_records:
                st.info("No maintenance records in the system for any property yet.")
        
        if not property_records: return # Exit if no records to display

        # Urgency filter
        urgency_options = ["All"] + sorted(list(set(r.urgency for r in property_records)))
        default_urgency_idx = 0 # Default to "All"
        # Use a unique key for the selectbox that includes context (property_address or 'all')
        filter_key_suffix = property_address.replace(" ", "_").replace(",", "") if property_address else "all"
        
        # Get or set default urgency filter state
        session_filter_key = f"maintenance_filter_urgency_{filter_key_suffix}"
        if session_filter_key not in st.session_state:
            st.session_state[session_filter_key] = st.session_state.pop("maintenance_filter_urgency", "All") # Use popped value if exists
        
        selected_urgency = st.selectbox("Filter by Urgency:", urgency_options, 
                                        index=urgency_options.index(st.session_state[session_filter_key]) if st.session_state[session_filter_key] in urgency_options else 0, 
                                        key=f"maint_hist_selectbox_{filter_key_suffix}")
        st.session_state[session_filter_key] = selected_urgency # Store current selection

        # Filter records based on selected urgency
        filtered_records = property_records
        if selected_urgency != "All":
            filtered_records = [r for r in filtered_records if r.urgency == selected_urgency]

        if not filtered_records:
            st.info(f"No records match '{selected_urgency}' urgency for {display_address_for_subheader}.")
            return

        # Prepare data for DataFrame
        df_data_list = []
        for r in filtered_records:
            item = {'Date': r.date, 
                    'Category': r.category, 
                    'Description': r.description,
                    'Cost ($)': r.cost, 
                    'Contractor': r.contractor, 
                    'Urgency': r.urgency}
            if not property_address: # For portfolio view, add property identifier
                prop_obj_for_record = next((p for p in st.session_state.properties if p.address == r.property_address), None)
                if prop_obj_for_record:
                    item['Property'] = f"{r.property_address}, {prop_obj_for_record.city}, {prop_obj_for_record.state.upper()}"
                else:
                    item['Property'] = r.property_address # Fallback if property details not found (should not happen)
            df_data_list.append(item)

        # Define column order based on view
        if not property_address: 
            column_order = ['Date', 'Property', 'Category', 'Description', 'Cost ($)', 'Contractor', 'Urgency']
        else:
            column_order = ['Date', 'Category', 'Description', 'Cost ($)', 'Contractor', 'Urgency']

        records_df = pd.DataFrame(df_data_list)
        if not records_df.empty:
            urgency_map = {"High":0, "Medium":1, "Routine":2} # For sorting by urgency
            records_df['urgency_sort_key'] = records_df['Urgency'].map(urgency_map)
            records_df_sorted = records_df.sort_values(by=['Date', 'urgency_sort_key'], ascending=[False, True]).drop(columns=['urgency_sort_key'])
            
            st.dataframe(records_df_sorted[column_order], use_container_width=True, height=300,
                        column_config={ "Cost ($)": st.column_config.NumberColumn(format="$%.2f"),
                                        "Description": st.column_config.TextColumn(width="large")})
        
        total_cost_filtered = sum(r.cost for r in filtered_records)
        st.markdown(f"**Total Cost (Filtered):** ${total_cost_filtered:,.2f}")
        st.markdown("---")


    def render_predictions_and_recommendations(self, property_data: Property):
        st.subheader("💡 Predictions & Proactive Recommendations")
        schedule = self.calculator.generate_maintenance_schedule(property_data)

        tab1, tab2 = st.tabs(["🔮 Upcoming Maintenance Tasks", "💰 Cost Planning Tool"])
        with tab1:
            st.markdown("**Key Upcoming Maintenance:** (Sorted by Priority & Due Date)")
            if not schedule:
                st.info("✅ No specific system-triggered recommendations at this time.")
            else:
                for task in schedule[:7]: # Show top 7
                    priority_icon = {"high": "🔴", "important": "🟡", "routine": "🔵"}[task["priority"]]
                    days_until = (task["next_due"] - datetime.datetime.now()).days
                    due_date_str = task["next_due"].strftime("%b %d, %Y")
                    with st.container(border=True, height=130): # Fixed height for consistency
                        col1, col2, col3 = st.columns([3,1,1])
                        with col1:
                            st.markdown(f"{priority_icon} **{task['task']}** ({task['frequency']})")
                            st.caption(f"{task['description']}")
                        with col2:
                            st.metric(label="Est. Cost", value=f"${task['estimated_cost']:,}", label_visibility="collapsed")
                        with col3:
                            if days_until <= 0: st.error(f"Due: {due_date_str} (Overdue!)")
                            elif days_until <= 30: st.warning(f"Due: {due_date_str} ({days_until}d)")
                            else: st.info(f"Due: {due_date_str} ({days_until}d)")
        with tab2:
            st.markdown("**Regional Cost Estimator**")
            st.caption(f"Estimates based on ZIP: {property_data.zip_code} (Region: {self.calculator.get_regional_info(property_data.zip_code)['region']})")
            cost_item_types = list(self.calculator.national_cost_baseline.keys())
            selected_item = st.selectbox("Select Item for Cost Estimate:", cost_item_types, index =0, key=f"cost_est_item_{property_data.address.replace(' ','_')}") # Make key more robust
            if selected_item:
                estimates = self.calculator.get_local_cost_estimate(selected_item, property_data.zip_code)
                ca, cb, cc = st.columns(3)
                ca.metric("Est. Min Cost", f"${estimates['min']:,}")
                cb.metric("Est. Avg Cost", f"${estimates['avg']:,}")
                cc.metric("Est. Max Cost", f"${estimates['max']:,}")
                st.caption(f"National Avg: ${estimates['national_avg']:,}. Confidence: {estimates['confidence'].title()}.")
        st.markdown("---")

    def render_comparative_health_chart(self):
        if len(st.session_state.properties) > 1:
            st.subheader("📊 Comparative Property Health Scores")
            prop_scores = []
            for p in st.session_state.properties:
                score_data = self.calculator.calculate_overall_score(p)
                prop_scores.append({
                    "Property": f"{p.address}, {p.city}", # Using a shorter label for chart
                    "Overall Score": score_data['overall_score'],
                    "Structural": score_data['category_scores']['Structural']['score'],
                    "Systems": score_data['category_scores']['Systems']['score'],
                    "Safety": score_data['category_scores']['Safety']['score'],
                })
            df = pd.DataFrame(prop_scores)
            score_types_to_plot = st.multiselect(
                "Select scores to compare:",
                options=["Overall Score", "Structural", "Systems", "Safety"],
                default=["Overall Score"], key="compare_multiselect"
            )
            if score_types_to_plot:
                chart_df = df.set_index("Property")[score_types_to_plot]
                st.bar_chart(chart_df, height=400)
            else:
                st.info("Select at least one score type to display the chart.")
        elif st.session_state.properties: # Only one property exists
            st.info("Add at least two properties to see a comparative health chart.")
        # No message if no properties, as the main tab will show guidance.
        st.markdown("---")


    def render_contractor_marketplace(self):
        st.subheader("🛠️ Find Certified Professionals (Marketplace - Demo)")
        st.info("This section is a placeholder for a future contractor marketplace integration.")
        contractors = [
            {'name': 'Valley HVAC Experts', 'category': 'HVAC', 'rating': 4.9, 'reviews': 312, 'zip_coverage': ['22701', '22801'], 'contact_info': 'Call (555) 123-4567'},
            {'name': 'Old Dominion Plumbing Pros', 'category': 'Plumbing', 'rating': 4.7, 'reviews': 189, 'zip_coverage': ['22701', '22102', '20109'], 'contact_info': 'info@odplumbing.com'},
            {'name': 'Capital Electrical Solutions', 'category': 'Electrical', 'rating': 4.8, 'reviews': 250, 'zip_coverage': ['22102', '20001'], 'contact_info': 'Schedule online!'},
            {'name': 'RoofGuard Inc.', 'category': 'Roofing', 'rating': 4.6, 'reviews': 150, 'zip_coverage': ['22701', '90210'], 'contact_info': 'Free estimates!'}
        ]
        selected_prop_for_contractor = self.render_property_selector("contractors", allow_none=True, help_text="Optionally, select a property to find relevant contractors:")
        
        current_prop_zip = None
        if selected_prop_for_contractor:
            current_prop_zip = selected_prop_for_contractor.zip_code
        
        if current_prop_zip:
            st.write(f"Showing contractors potentially serving ZIP: **{current_prop_zip}** for {selected_prop_for_contractor.address}, {selected_prop_for_contractor.city}")
            filtered_contractors = [c for c in contractors if current_prop_zip in c['zip_coverage'] or (c['zip_coverage'] and current_prop_zip[0] == c['zip_coverage'][0][0])] # Basic check by first digit
            if not filtered_contractors and contractors: # Fallback if no specific match
                 st.warning(f"No contractors found directly matching ZIP {current_prop_zip}. Showing general list.")
                 filtered_contractors = contractors
        else:
            st.write("Showing general list of contractors. Select a property to narrow down by ZIP code.")
            filtered_contractors = contractors

        for contractor in filtered_contractors:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2,1.5,1])
                with col1:
                    st.markdown(f"**{contractor['name']}**")
                    st.caption(f"Category: {contractor['category']}")
                with col2:
                    st.markdown(f"⭐ {contractor['rating']} ({contractor['reviews']} reviews)")
                    st.caption(f"Serves: {', '.join(contractor['zip_coverage'][:2])}...") # Show first few zips
                with col3:
                    if st.button(f"Contact {contractor['name'].split(' ')[0]}", key=f"contact_{contractor['name'].replace(' ', '_')}"): # Unique key
                        st.success(f"Contact info for {contractor['name']}: {contractor['contact_info']}")

    def render_roi_calculator(self):
        st.header("💰 Return on Investment (ROI) Calculator")
        st.caption("Estimate the potential ROI for property improvements. Fill in the details below.")
        st.markdown("---")

        st.subheader("1. Improvement Details & Costs")

        property_display_options_roi = {
            f"{p.address}, {p.city}, {p.state.upper()}": p.address 
            for p in st.session_state.properties
        }
        select_options_roi = ["Select a Property..."] + list(property_display_options_roi.keys())
        
        # Determine current display selection for ROI property selector
        current_roi_display_selection = "Select a Property..."
        if st.session_state.get('roi_property_address'): # This stores actual address
            for disp, addr_val in property_display_options_roi.items():
                if addr_val == st.session_state.roi_property_address:
                    current_roi_display_selection = disp
                    break
        
        selected_roi_display_label = st.selectbox(
            "Select Property (Optional, for context):",
            options=select_options_roi,
            index=select_options_roi.index(current_roi_display_selection) if current_roi_display_selection in select_options_roi else 0,
            key="roi_prop_select_sb" 
        )
        # Update session state with the actual address based on selection
        st.session_state.roi_property_address = property_display_options_roi.get(selected_roi_display_label) if selected_roi_display_label != "Select a Property..." else None
        actual_selected_property_address_for_roi = st.session_state.roi_property_address


        st.session_state.roi_improvement_name = st.text_input(
            "Name or Description of Improvement/Project:",
            value=st.session_state.get('roi_improvement_name', ""),
            key="roi_improvement_name_text_input"
        )

        suggested_cost = None
        if actual_selected_property_address_for_roi and st.session_state.roi_improvement_name:
            selected_prop_obj_for_roi = next((p for p in st.session_state.properties if p.address == actual_selected_property_address_for_roi), None)
            if selected_prop_obj_for_roi:
                cost_category_map = {
                    "hvac": "hvac_replacement", "air conditioner": "hvac_replacement", "furnace": "hvac_replacement",
                    "roof": "roof_replacement", "electrical panel": "electrical_panel",
                    "water heater": "water_heater", "plumbing repair": "plumbing_repair",
                }
                matched_category = None
                for keyword, category_key in cost_category_map.items():
                    if keyword.lower() in st.session_state.roi_improvement_name.lower():
                        matched_category = category_key
                        break
                if matched_category:
                    cost_estimate = self.calculator.get_local_cost_estimate(matched_category, selected_prop_obj_for_roi.zip_code)
                    if cost_estimate["avg"] > 0 : 
                        suggested_cost = cost_estimate["avg"]
                        st.info(f"Based on project name and ZIP {selected_prop_obj_for_roi.zip_code}, estimated average cost for a '{matched_category.replace('_', ' ')}' could be around ${suggested_cost:,.0f}. Adjust below as needed.")
        
        current_cost_val = st.session_state.get('roi_estimated_cost', 0.0)
        if suggested_cost is not None and current_cost_val == 0.0: # Auto-fill only if current cost is 0 and suggestion is valid
             current_cost_val = float(suggested_cost)
        
        st.session_state.roi_estimated_cost = st.number_input(
            "Total Estimated Cost of Improvement ($):",
            min_value=0.0, step=100.0, format="%.2f",
            value=float(current_cost_val), 
            key="roi_estimated_cost_num_input" 
        )

        st.markdown("---")
        st.subheader("2. Estimated Financial Benefits")

        st.session_state.roi_resale_value_increase = st.number_input(
            "Estimated Immediate Increase in Property Resale Value ($):",
            help="How much more do you believe the property would be worth immediately after this improvement?",
            min_value=0.0, step=100.0, format="%.2f",
            value=float(st.session_state.get('roi_resale_value_increase', 0.0)), 
            key="roi_resale_value_increase_num_input" 
        )

        st.session_state.roi_annual_savings = st.number_input(
            "Estimated Annual Operational Savings ($/year):",
            help="E.g., savings from lower energy bills, reduced maintenance costs, or insurance premiums.",
            min_value=0.0, step=10.0, format="%.2f",
            value=float(st.session_state.get('roi_annual_savings', 0.0)), 
            key="roi_annual_savings_num_input" 
        )

        st.session_state.roi_years_to_project = st.number_input(
            "Number of Years to Project Annual Savings:",
            help="For how many years do you expect to realize these annual savings?",
            min_value=1, max_value=30,
            value=int(st.session_state.get('roi_years_to_project', 5)), 
            step=1,
            key="roi_years_to_project_num_input" 
        )
        st.markdown("---")

        if st.button("📊 Calculate ROI", type="primary", use_container_width=True, key="roi_calculate_button"):
            cost = st.session_state.roi_estimated_cost
            resale_increase = st.session_state.roi_resale_value_increase
            annual_savings = st.session_state.roi_annual_savings
            years = st.session_state.roi_years_to_project
            improvement_name = st.session_state.roi_improvement_name

            if not improvement_name.strip():
                st.warning("Please enter a name or description for the improvement project.")
            elif cost <= 0: 
                st.warning("Please enter a 'Total Estimated Cost of Improvement' greater than $0.")
            else:
                total_operational_savings = annual_savings * years
                total_financial_benefit = resale_increase + total_operational_savings
                net_gain_loss = total_financial_benefit - cost
                roi_percentage = (net_gain_loss / cost) * 100.0 # Ensure cost > 0 for division
                
                payback_period_years_str = "N/A"
                if annual_savings > 0: # Avoid division by zero for payback period
                    payback_period_years = cost / annual_savings
                    payback_period_years_str = f"{payback_period_years:.1f} Years"

                st.subheader(f"📈 ROI Analysis for: {st.session_state.roi_improvement_name or 'Unnamed Project'}")
                
                res_col1, res_col2, res_col3 = st.columns(3)
                res_col1.metric("Net Gain/Loss", f"${net_gain_loss:,.2f}",
                            delta_color=("normal" if net_gain_loss >= 0 else "inverse"))
                res_col2.metric("Return on Investment (ROI)", f"{roi_percentage:.1f}%")
                res_col3.metric("Payback Period", payback_period_years_str)

                with st.expander("View Detailed Breakdown", expanded=True):
                    st.markdown(f"**Cost of Improvement:** ${cost:,.2f}")
                    st.markdown(f"**Projected Resale Value Increase:** ${resale_increase:,.2f}")
                    st.markdown(f"**Projected Annual Operational Savings:** ${annual_savings:,.2f}/year")
                    st.markdown(f"**Savings Projection Period:** {years} years")
                    st.markdown(f"**Total Projected Operational Savings:** ${total_operational_savings:,.2f}")
                    st.markdown(f"**Total Financial Benefit (Resale + Ops Savings):** ${total_financial_benefit:,.2f}")
                
                st.caption("*Disclaimer: Calculations are based on user-provided estimates and are for informational purposes only.*")
        else:
            st.info("Fill in the details above and click 'Calculate ROI' to see the analysis.")


    def run(self):
        if not self.auth_manager.is_authenticated():
            self.auth_manager.render_auth_screen()
            return

        self.render_header()
        with st.sidebar:
            self.auth_manager.render_session_info()
            
            with st.expander("⚙️ App Settings", expanded=False):
                st.caption("Weather API key is configured via Streamlit Secrets.")
                # Future app-wide settings can go here

            self.render_quick_actions()
            st.markdown("---")
            self.render_property_management()
            st.markdown("---")
            self.render_maintenance_input()
            st.markdown("---")
            st.sidebar.caption(f"© {datetime.datetime.now().year} Property Health Intel. All Rights Reserved.")

        tab_options = ["📈 Property Health", "🧰 Maintenance Center", "🤝 Find Contractors", "📊 Analytics Hub", "💰 ROI Calculator"]
        
        if 'active_tab' not in st.session_state or st.session_state.active_tab not in tab_options:
            st.session_state.active_tab = tab_options[0]
        
        tabs_tuple = st.tabs(tab_options)
        property_health_tab, maintenance_tab, contractors_tab, analytics_tab, roi_tab = tabs_tuple


        with property_health_tab:
            st.header("Property Health Dashboard")
            st.caption("View detailed health scores, upcoming maintenance, and local weather for your selected property.")
            if not st.session_state.properties:
                st.info("👋 Welcome! Add your first property using the '➕ Add New Property' button in the sidebar to get started.")
            else:
                selected_property = self.render_property_selector("health", help_text="Select Property for Health View:")
                if selected_property:
                    self.render_health_score_visualization(selected_property) 
                    self.render_detailed_breakdown(selected_property)
                    self.render_predictions_and_recommendations(selected_property)
                else: # Properties exist but none selected
                    st.info("👈 Select a property from the dropdown above to view its detailed health snapshot.")


        with maintenance_tab:
            st.header("Maintenance Center")
            st.caption("Log, view, and filter maintenance records for your properties.")
            if not st.session_state.properties:
                st.info("Add a property first to log and view maintenance records.")
            else:
                selected_property_for_maint = self.render_property_selector(
                    "maintenance", 
                    allow_none=True, 
                    help_text="Select Property (or 'Select a Property...' for all records):"
                )
                self.render_maintenance_history(selected_property_for_maint.address if selected_property_for_maint else None)
        
        with contractors_tab:
            st.header("Contractor Marketplace")
            st.caption("Discover local professionals for your property needs (Demo).")
            self.render_contractor_marketplace()

        with analytics_tab:
            st.header("Portfolio Analytics Hub")
            st.caption("Compare property health scores and view portfolio-wide analytics.")
            self.render_comparative_health_chart()
            # No need for "More analytics features coming soon!" if no properties are added yet
            if st.session_state.properties:
                st.info("More analytics features (e.g., detailed cost tracking, value impact) coming soon!")
            
        with roi_tab:
            # render_roi_calculator has its own header and caption
            if not st.session_state.properties:
                st.header("💰 Return on Investment (ROI) Calculator") # Ensure header shown even if no properties
                st.caption("Estimate the potential ROI for property improvements.")
                st.info("Add a property first to use the ROI Calculator.")
            else:
                self.render_roi_calculator()

def main():
    dashboard = Dashboard()
    dashboard.run()

if __name__ == "__main__":
    main()

