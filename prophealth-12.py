#!/usr/bin/env python3
# Prophealth_3.py

import streamlit as st

# <<< THEME CONFIGURATION >>>
# Define our new color palette
FOREST_GREEN = "#228B22" 
PRIMARY_BLUE = "#006AFF" 
LIGHT_BACKGROUND = "#F8F9FA" 
NAVY_BLUE = "#000080" 
TEXT_LIGHT = "#FFFFFF"
SECONDARY_BACKGROUND = "#E9ECEF" # Kept for potential future use

st.set_page_config(
    page_title="Property Health Intelligence Platform", 
    page_icon="🏠", 
    layout="wide", 
    initial_sidebar_state="expanded"
    # theme=None was removed
)

import pandas as pd
import numpy as np
import datetime
from dataclasses import dataclass, field, asdict 
from typing import List, Dict, Optional, Any
import requests
import io 

# <<< SIMPLIFIED: Global Theming Function for Diagnosis >>>
def apply_global_styles():
    st.markdown(f"""
        <style>
            /* --- Minimal Global Font & Background --- */
            html, body, .stApp, [class*="st-"] {{
                font-family: sans-serif !important;
                background-color: {LIGHT_BACKGROUND} !important;
                color: {NAVY_BLUE} !important; /* General text color */
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: {FOREST_GREEN} !important; /* Headers */
                font-family: sans-serif !important;
            }}
            /* Basic button styling attempt */
            .stButton>button {{
                font-family: sans-serif !important;
                border: 1px solid {FOREST_GREEN} !important;
                background-color: {FOREST_GREEN} !important;
                color: {TEXT_LIGHT} !important;
            }}
            /* Basic input field styling attempt */
            .stTextInput input, .stNumberInput input, .stDateInput input,
            .stTextArea textarea, .stSelectbox > div[data-baseweb="select"] > div {{
                font-family: sans-serif !important;
                background-color: #FFFFFF !important;
                color: {NAVY_BLUE} !important;
                border: 1px solid #CCCCCC !important;
            }}
            .stTextInput label, .stNumberInput label, .stDateInput label, 
            .stSelectbox label, .stTextArea label, .stFileUploader label {{
                color: {NAVY_BLUE} !important;
                font-family: sans-serif !important;
            }}
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
    roof_age: int 
    foundation_type: str
    hvac_age: int
    electrical_age: int
    plumbing_age: int
    last_inspection: str 
    image_data: Optional[bytes] = None
    documents: List[Dict[str, Any]] = field(default_factory=list)

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
            "default": {"multiplier": 1.00, "region": "National Average", "confidence": "low"}
        }
        
        self.roof_material_expected_lifespans = {
            "Asphalt Shingles": 20, 
            "Metal": 50,
            "Tile": 50, 
            "Slate": 75, 
            "Wood": 25, 
            "Composite": 30, 
            "Flat Roof (TPO/EPDM)": 20 
        }
        self.foundation_scores = {'Concrete Slab': 85, 'Basement': 90, 'Crawl Space': 75, 'Pier & Beam': 70}

    def get_regional_info(self, zip_code: str) -> Dict:
        if zip_code in self.regional_multipliers:
            return self.regional_multipliers[zip_code]
        if zip_code and zip_code[0] in self.regional_multipliers: 
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
        if age < 0: age = 0 
        if expected_life <= 0: return 0.0 
        
        if age <= expected_life * 0.1: return 100.0 
        
        ratio = age / expected_life
        
        if ratio <= 0.5:  
            return 100.0 - (ratio * 20.0)  
        elif ratio <= 0.8:  
            return 90.0 - ((ratio - 0.5) / 0.3 * 30.0)  
        elif ratio < 1.0: 
             return 60.0 - ((ratio - 0.8) / 0.2 * 40.0) 
        else:  
            over_ratio = (age - expected_life) / (expected_life * 0.2) 
            return max(0.0, 20.0 - (over_ratio * 20.0))

    def calculate_structural_score(self, property_data: Property) -> Dict:
        current_year = datetime.datetime.now().year
        building_age = current_year - property_data.year_built
        building_age_score = self.calculate_age_score(building_age, 80) 
        foundation_score = self.foundation_scores.get(property_data.foundation_type, 75) 
        expected_roof_life = self.roof_material_expected_lifespans.get(property_data.roof_material, 20) 
        roof_condition_score = self.calculate_age_score(property_data.roof_age, expected_roof_life)
        overall_structural_score = (building_age_score * 0.4 + 
                                    foundation_score * 0.3 + 
                                    roof_condition_score * 0.3)
        return {
            'score': round(overall_structural_score, 1), 
            'components': {
                'Overall Building Age Factor': round(building_age_score, 1), 
                'Foundation Type': foundation_score, 
                'Roof Condition (Age/Material Adjusted)': round(roof_condition_score, 1)
            }
        }

    def calculate_systems_score(self, property_data: Property) -> Dict:
        hvac_score = self.calculate_age_score(property_data.hvac_age, 18) 
        electrical_score = self.calculate_age_score(property_data.electrical_age, 35) 
        plumbing_score = self.calculate_age_score(property_data.plumbing_age, 50) 
        overall_score = (hvac_score * 0.4 + electrical_score * 0.3 + plumbing_score * 0.3)
        return {'score': round(overall_score, 1), 'components': {'HVAC': round(hvac_score, 1), 'Electrical': round(electrical_score, 1), 'Plumbing': round(plumbing_score, 1)}}

    def calculate_safety_score(self, property_data: Property) -> Dict:
        base_score = 90.0 
        current_year = datetime.datetime.now().year
        age = current_year - property_data.year_built
        if age > 50: base_score -= 15 
        elif age > 30: base_score -= 7
        if property_data.electrical_age > 30: base_score -=5 
        if property_data.last_inspection == "N/A" and age > 20: base_score -= 5
        elif property_data.last_inspection != "N/A":
            try:
                last_insp_date = datetime.datetime.strptime(property_data.last_inspection, "%Y-%m-%d").date()
                if (datetime.date.today() - last_insp_date).days > 5 * 365: base_score -=5
            except ValueError: pass 
        return {'score': round(max(0, base_score), 1), 'components': {'General Safety Factors': round(max(0, base_score),1)}}

    def calculate_environmental_score(self, property_data: Property) -> Dict:
        base_score = 80.0
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
                'Structural': structural, 'Systems': systems,
                'Safety': safety, 'Environmental': environmental
            }
        }

    def generate_maintenance_schedule(self, property_data: Property) -> List[Dict]:
        schedule = []
        current_date = datetime.datetime.now()
        zip_code = property_data.zip_code
        if property_data.hvac_age <= 1: 
             cost_est_filter = self.get_local_cost_estimate("hvac_service", zip_code)
             schedule.append({"task": "HVAC Filter Check/Replacement", "frequency": "Every 3 months", "next_due": current_date + datetime.timedelta(days=90), "priority": "routine", "estimated_cost": max(20, cost_est_filter["min"] // 10) , "description": "Check and replace air filters as needed."})
        elif property_data.hvac_age <= 18 * 0.8 : 
            cost_est_service = self.get_local_cost_estimate("hvac_service", zip_code)
            schedule.append({"task": "HVAC Annual Service", "frequency": "Annually", "next_due": current_date + datetime.timedelta(days=365), "priority": "important", "estimated_cost": cost_est_service["avg"], "description": "Professional tune-up and inspection."})
        else: 
            cost_est_repl = self.get_local_cost_estimate("hvac_replacement", zip_code)
            schedule.append({"task": "HVAC Replacement Planning", "frequency": "Within 1-2 years", "next_due": current_date + datetime.timedelta(days=365), "priority": "high", "estimated_cost": cost_est_repl["avg"], "description": "Budget and plan for HVAC system replacement."})
        if property_data.roof_age > 10:
            cost_est_roof_insp = self.get_local_cost_estimate("roof_repair", zip_code) 
            schedule.append({"task": "Roof Inspection (detailed for age)", "frequency": "Annually", "next_due": current_date + datetime.timedelta(days=365), "priority": "important", "estimated_cost": max(150,cost_est_roof_insp["min"]), "description": "Inspect roof for wear, potential leaks, especially if older than 10 years."})
        if property_data.electrical_age > 30:
            cost_est_panel_check = self.get_local_cost_estimate("electrical_panel", zip_code) 
            schedule.append({"task": "Electrical System Inspection", "frequency": "Consider within 1 year", "next_due": current_date + datetime.timedelta(days=365), "priority": "important", "estimated_cost": max(150, cost_est_panel_check["min"] // 5) , "description": "Inspect aging electrical panel and system, especially if over 30 years old."})
        if property_data.electrical_age > 35 * 0.9: 
             schedule.append({"task": "Consider Electrical Panel Upgrade", "frequency": "Within 2-3 years", "next_due": current_date + datetime.timedelta(days=730), "priority": "high", "estimated_cost": self.get_local_cost_estimate("electrical_panel", zip_code)["avg"], "description": "Plan for upgrading an old electrical panel if original."})
        if property_data.plumbing_age > 8 : 
            cost_est_wh_service = self.get_local_cost_estimate("water_heater", zip_code) 
            schedule.append({"task": "Water Heater Check/Service", "frequency": "Annually if >8yrs old", "next_due": current_date + datetime.timedelta(days=365), "priority": "important", "estimated_cost": max(100, cost_est_wh_service["min"] // 10), "description": "Inspect water heater. Plan for replacement if near end-of-life."})
        if property_data.plumbing_age > 50*0.8: 
             cost_est_pipe_repair = self.get_local_cost_estimate("plumbing_repair", zip_code)
             schedule.append({"task": "Major Plumbing Inspection (Pipes)", "frequency": "Consider within 2 years", "next_due": current_date + datetime.timedelta(days=730), "priority": "high", "estimated_cost": cost_est_pipe_repair["avg"], "description": "Inspect for potential major plumbing updates (pipes, main lines) if original."})
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
        self.password = "PropHealth2025!" 

    def render_auth_screen(self):
        st.markdown("""<style>
        .auth-container {max-width: 600px; margin: 2rem auto; padding: 2rem 2.5rem; background: #ffffff; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); color: #333;}
        .auth-container h1 { color: #764ba2; text-align: center; font-family: 'Arial', sans-serif !important; }
        .auth-container h3 { color: #667eea; margin-top:1.5rem; margin-bottom:0.5rem; font-family: 'Arial', sans-serif !important; }
        .auth-container .stButton>button {width: 100%; background-color: #667eea; color:white; border-radius: 8px; padding: 0.75rem 0; font-family: 'Arial', sans-serif !important;}
        .auth-container .stButton>button:hover {background-color: #764ba2;}
        .auth-container .stTextInput input, .auth-container .stSelectbox div[data-baseweb="select"] > div {border-radius: 8px !important;}
        .auth-container .stAlert {border-radius: 8px;}
        .auth-container, .auth-container .stCheckbox label {{ font-family: 'Arial', sans-serif !important; color: #333 !important; }}
        </style>""", unsafe_allow_html=True)
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown("<h1>🏠 Property Health Intelligence Platform</h1>", unsafe_allow_html=True)
        st.markdown("<h3><em>Prototype Access Portal</em></h3>", unsafe_allow_html=True)
        st.markdown("<h4>Confidential Preview Access</h4>", unsafe_allow_html=True)
        st.info("🔒 This is a confidential prototype demonstration. Access implies agreement to confidentiality and IP respect.", icon="ℹ️")
        col1, col2 = st.columns(2)
        with col1:
            confidential_understood = st.checkbox("Acknowledge Confidentiality", key="auth_conf_checkbox")
            respect_ip = st.checkbox("Respect Intellectual Property", key="auth_ip_checkbox")
        with col2:
            professional_courtesy = st.checkbox("Agree to Professional Standards", key="auth_courtesy_checkbox")
            authorized_access = st.checkbox("Authorized Stakeholder", key="auth_stakeholder_checkbox")
        st.markdown("<h4>Digital Signature</h4>", unsafe_allow_html=True)
        st.text_input("Full Name *", placeholder="Enter your full name", key="auth_full_name")
        st.text_input("Email Address *", placeholder="your.email@company.com", key="auth_email_address")
        st.text_input("Company/Organization", placeholder="Your company", key="auth_company_org")
        st.selectbox("Purpose of Access *",
                             ["", "Potential Investor", "Business Partner", "Industry Professional", "Internal Review", "Other"],
                             index=0, key="auth_access_purpose")
        st.markdown("<h4>Access Code</h4>", unsafe_allow_html=True)
        st.text_input("Enter access code:", type="password", placeholder="Access code required", key="auth_password_input")
        s_full_name = st.session_state.get("auth_full_name", "")
        s_email_address = st.session_state.get("auth_email_address", "")
        s_access_purpose = st.session_state.get("auth_access_purpose", "")
        s_password_input = st.session_state.get("auth_password_input", "")
        all_acknowledged = confidential_understood and respect_ip and professional_courtesy and authorized_access
        password_correct = s_password_input == self.password
        signature_complete = s_full_name.strip() != "" and s_email_address.strip() != "" and s_access_purpose != ""
        email_valid = "@" in s_email_address and "." in s_email_address.split('@')[-1] if s_email_address and "@" in s_email_address else False
        access_button_disabled = not (all_acknowledged and signature_complete and email_valid and s_password_input)
        if st.button("🚀 ACCESS PREVIEW", type="primary", disabled=access_button_disabled, key="auth_access_button"): 
            if password_correct:
                st.session_state.access_info = {
                    'name': st.session_state.get("auth_full_name", ""), 'email': st.session_state.get("auth_email_address", ""),
                    'company': st.session_state.get("auth_company_org", ""), 'purpose': st.session_state.get("auth_access_purpose", ""),
                    'timestamp': datetime.datetime.now()
                }
                st.session_state.authenticated = True
                st.session_state.access_timestamp = datetime.datetime.now() 
                st.success("✅ Access granted! Loading platform...")
                st.balloons()
                st.rerun()
            else: st.error("❌ Invalid access code or missing required fields/acknowledgments. Please check all inputs.")
        st.markdown("<hr style='margin: 1.5rem 0;'/><p style='text-align:center; font-size:0.9rem;'>For inquiries, contact: JESquared24@gmail.com</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    def is_authenticated(self):
        return st.session_state.get('authenticated', False)

    def render_session_info(self):
        if self.is_authenticated():
            access_info = st.session_state.get('access_info', {})
            st.sidebar.markdown("---")
            st.sidebar.markdown("**🛡️ Authorized Session**")
            if access_info.get('name'): st.sidebar.markdown(f"**User:** {access_info['name']}")
            if st.sidebar.button("🚪 End Session & Logout", use_container_width=True, key="logout_button_main_app", type="secondary"):
                keys_to_clear = [k for k in st.session_state.keys() if k.startswith('auth_')]
                keys_to_clear.extend(['access_info', 'authenticated', 'access_timestamp', 
                                      'show_add_property_form_main', 'show_add_maintenance_form_main', 
                                      'editing_property_address', 'active_tab']) 
                keys_to_clear.extend([k for k in st.session_state.keys() if k.startswith('selected_property_address_')])
                keys_to_clear.extend([k for k in st.session_state.keys() if k.startswith('roi_')])
                keys_to_clear.extend([k for k in st.session_state.keys() if k.startswith('maintenance_filter_urgency_')])

                for key_to_del in keys_to_clear:
                    if key_to_del in st.session_state: del st.session_state[key_to_del]
                st.success("Logged out successfully. Session data cleared.")
                st.rerun()

class Dashboard:
    def __init__(self):
        self.calculator = PropertyHealthCalculator()
        self.auth_manager = AuthenticationManager()
        self.init_session_state()

    def init_session_state(self):
        if 'properties' not in st.session_state: st.session_state.properties = []
        if 'maintenance_records' not in st.session_state: st.session_state.maintenance_records = []
        if 'show_add_property_form_main' not in st.session_state: st.session_state.show_add_property_form_main = False 
        if 'show_add_maintenance_form_main' not in st.session_state: st.session_state.show_add_maintenance_form_main = False 
        if 'editing_property_address' not in st.session_state: st.session_state.editing_property_address = None 
        if 'active_tab' not in st.session_state: st.session_state.active_tab = "📈 Property Health"
        # ROI state
        for key, default in [('roi_property_address', None), ('roi_improvement_name', ""), 
                             ('roi_estimated_cost', 0.0), ('roi_resale_value_increase', 0.0),
                             ('roi_annual_savings', 0.0), ('roi_years_to_project', 5)]:
            if key not in st.session_state: st.session_state[key] = default

    def render_header(self):
        st.title("🏠 Property Health Intelligence") 
        st.markdown("---")
        cols = st.columns(5) 
        total_props = len(st.session_state.properties)
        cols[0].markdown(f"""<div class="metric-card metric-bg-primary-blue"><h3>Total Properties</h3><p class="value">{total_props}</p><small class="delta">Currently Managed</small></div>""", unsafe_allow_html=True)
        avg_score_str, avg_score_color_class = "N/A", "metric-bg-primary-blue"
        if st.session_state.properties:
            try:
                scores = [self.calculator.calculate_overall_score(prop)['overall_score'] for prop in st.session_state.properties]
                if scores: 
                    avg_score_val = np.mean(scores)
                    avg_score_str = f"{avg_score_val:.1f}"
                    if avg_score_val >= 85: avg_score_color_class = "metric-bg-positive"
                    elif avg_score_val >= 70: avg_score_color_class = "metric-bg-warning"
                    else: avg_score_color_class = "metric-bg-alert"
            except Exception: avg_score_str, avg_score_color_class = "Error", "metric-bg-alert"
        cols[1].markdown(f"""<div class="metric-card {avg_score_color_class}"><h3>Average Health</h3><p class="value">{avg_score_str}</p><small class="delta">Overall Portfolio Score</small></div>""", unsafe_allow_html=True)
        urgent_items_count = len([r for r in st.session_state.maintenance_records if r.urgency == "High"])
        urgent_color_class = "metric-bg-positive" if urgent_items_count == 0 else "metric-bg-warning" if urgent_items_count < 3 else "metric-bg-alert"
        cols[2].markdown(f"""<div class="metric-card {urgent_color_class}"><h3>Urgent Items</h3><p class="value">{urgent_items_count}</p><small class="delta">Requiring Attention</small></div>""", unsafe_allow_html=True)
        total_cost = sum([r.cost for r in st.session_state.maintenance_records])
        cols[3].markdown(f"""<div class="metric-card metric-bg-neutral"><h3>Total Maint. Cost</h3><p class="value">${total_cost:,.0f}</p><small class="delta">Logged Expenditures</small></div>""", unsafe_allow_html=True)
        preventative_maintenance_cost = sum(r.cost for r in st.session_state.maintenance_records if r.urgency in ["Routine", "Medium"])
        estimated_savings = preventative_maintenance_cost * 0.15 
        cols[4].markdown(f"""<div class="metric-card metric-bg-positive"><h3>Est. Savings</h3><p class="value">${estimated_savings:,.0f}</p><small class="delta">Proactive Care (Est.)</small></div>""", unsafe_allow_html=True)

    def render_quick_actions(self):
        st.sidebar.subheader("⚡ Quick Actions")
        if st.sidebar.button("➕ Add New Property", use_container_width=True, key="quick_add_prop_btn_main"):
            st.session_state.show_add_property_form_main = True
            st.session_state.show_add_maintenance_form_main = False 
            st.session_state.editing_property_address = None 
            st.rerun()
        add_maint_disabled = not st.session_state.properties
        if st.sidebar.button("📝 Log Maintenance Task", use_container_width=True, disabled=add_maint_disabled, key="quick_log_maint_btn_main"):
            st.session_state.show_add_maintenance_form_main = True
            st.session_state.show_add_property_form_main = False 
            st.session_state.editing_property_address = None 
            st.rerun()
        view_urgent_disabled = not any(r.urgency == "High" for r in st.session_state.maintenance_records)
        if st.sidebar.button("❗ View Urgent Tasks", use_container_width=True, disabled=view_urgent_disabled, key="quick_view_urgent_btn"):
            st.session_state.show_add_property_form_main = False 
            st.session_state.show_add_maintenance_form_main = False
            st.session_state.editing_property_address = None 
            st.session_state.active_tab = "🧰 Maintenance Center"
            st.session_state.maintenance_filter_urgency_all = "High" # Ensure specific key for global filter
            st.toast("Switched to Maintenance tab with 'High' urgency filter.", icon="❗")
            st.rerun()

    def render_property_management_sidebar(self):
        st.sidebar.header("🏡 Property Portfolio")
        if st.session_state.properties:
            with st.sidebar.expander("🗑️ Manage Properties", expanded=False): 
                prop_options_display = { f"{i+1}. {prop.address}, {prop.city}, {prop.state.upper()} ({prop.zip_code})": prop.address for i, prop in enumerate(st.session_state.properties) }
                prop_display_labels = [""] + list(prop_options_display.keys())
                selected_prop_display_label_to_delete = st.selectbox("Select property to remove:", prop_display_labels, index=0, key="delete_prop_select_sidebar" )
                if selected_prop_display_label_to_delete and selected_prop_display_label_to_delete != "":
                    address_to_delete = prop_options_display[selected_prop_display_label_to_delete]
                    if st.button("🗑️ Delete Selected Property", type="secondary", use_container_width=True, key="delete_prop_btn_sidebar"):
                        idx_to_delete = next((i for i, p_obj in enumerate(st.session_state.properties) if p_obj.address == address_to_delete), -1)
                        if idx_to_delete != -1:
                            deleted_property_info = f"{st.session_state.properties[idx_to_delete].address}, {st.session_state.properties[idx_to_delete].city}"
                            st.session_state.maintenance_records = [r for r in st.session_state.maintenance_records if r.property_address != address_to_delete]
                            del st.session_state.properties[idx_to_delete]
                            if st.session_state.editing_property_address == address_to_delete: st.session_state.editing_property_address = None
                            if st.session_state.get(f"selected_property_address_health") == address_to_delete: st.session_state.selected_property_address_health = None 
                            st.success(f"🗑️ Property '{deleted_property_info}' and its maintenance records removed.")
                            st.session_state.delete_prop_select_sidebar = "" 
                            st.rerun()
                        else: st.error("Error finding property to delete.")
        else: st.sidebar.caption("No properties added yet.")
    
    def render_add_property_form_main_panel(self):
        st.header("➕ Add New Property")
        st.caption("Fill in the details below to add a new property to your portfolio.")
        with st.container(border=True):
            with st.form("property_form_main", clear_on_submit=False): 
                address = st.text_input("Property Address *")
                city = st.text_input("City *")
                state = st.text_input("State *", max_chars=2, help="E.g., VA, NC, CA")
                zip_code = st.text_input("ZIP Code *", value="22701")
                col1, col2 = st.columns(2)
                with col1:
                    year_built = st.number_input("Year Built", min_value=1800, max_value=datetime.datetime.now().year, value=2000, step=1)
                    property_type = st.selectbox("Property Type", ["Single Family", "Townhouse", "Condo", "Multi-Family", "Commercial"])
                    roof_material = st.selectbox("Roof Material", list(self.calculator.roof_material_expected_lifespans.keys())) 
                    roof_age = st.number_input("Roof Age (years)", min_value=0, max_value=100, value=10, step=1) 
                    hvac_age = st.number_input("HVAC Age (years)", min_value=0, max_value=50, value=5, step=1)
                with col2:
                    square_footage = st.number_input("Square Footage", min_value=100, max_value=20000, value=1500, step=50)
                    foundation_type = st.selectbox("Foundation Type", list(self.calculator.foundation_scores.keys())) 
                    electrical_age = st.number_input("Electrical System Age (years)", min_value=0, max_value=100, value=15, step=1)
                    plumbing_age = st.number_input("Plumbing System Age (years)", min_value=0, max_value=100, value=20, step=1)
                last_inspection_date = st.date_input("Last Major Inspection Date", value=None)
                uploaded_photo = st.file_uploader("Upload Property Photo (Optional)", type=["png", "jpg", "jpeg"])
                submit_col, cancel_col = st.columns([0.8, 0.2]) 
                with submit_col: submitted = st.form_submit_button("✅ Add Property to Portfolio", type="primary", use_container_width=True)
                with cancel_col:
                    if st.form_submit_button("❌ Cancel", use_container_width=True, type="secondary"):
                        st.session_state.show_add_property_form_main = False; st.rerun()
                if submitted:
                    if not all([address, city, state, zip_code]): st.error("🚨 Address, City, State, and ZIP Code are required!")
                    else:
                        image_bytes = uploaded_photo.getvalue() if uploaded_photo else None
                        last_inspection_str = last_inspection_date.strftime("%Y-%m-%d") if last_inspection_date else "N/A"
                        new_property = Property(address, city, state.upper(), zip_code, year_built, square_footage, property_type, roof_material, roof_age, foundation_type, hvac_age, electrical_age, plumbing_age, last_inspection_str, image_bytes, [])
                        st.session_state.properties.append(new_property)
                        st.session_state.show_add_property_form_main = False 
                        st.success(f"✅ Property '{address}, {city}, {state.upper()}' added successfully! Returning to dashboard...")
                        st.balloons(); import time; time.sleep(2); st.rerun()

    def render_add_maintenance_form_main_panel(self):
        st.header("📝 Log New Maintenance Record")
        st.caption("Fill in the details for the maintenance task.")
        if not st.session_state.properties:
            st.warning("🚨 No properties available. Please add a property first.")
            if st.button("Go to Add Property"): st.session_state.show_add_maintenance_form_main = False; st.session_state.show_add_property_form_main = True; st.rerun()
            return
        with st.container(border=True):
            property_display_options = { f"{prop.address}, {prop.city}, {prop.state.upper()}": prop.address for prop in st.session_state.properties }
            display_labels = list(property_display_options.keys())
            with st.form("maintenance_form_main", clear_on_submit=False):
                selected_display_address = st.selectbox("Select Property *", display_labels, index=0 if display_labels else None)
                actual_address_for_record = property_display_options.get(selected_display_address) if selected_display_address else None
                date = st.date_input("Date of Service/Record *", datetime.date.today())
                category = st.selectbox("Category *", ["HVAC", "Plumbing", "Electrical", "Roofing", "Foundation", "Appliances", "Pest Control", "Landscaping", "General Repair", "Inspection", "Other"])
                description = st.text_area("Description of Work / Issue *", height=100)
                cost = st.number_input("Cost ($)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
                contractor = st.text_input("Contractor/Vendor (if any)")
                urgency = st.selectbox("Urgency *", ["Routine", "Medium", "High"])
                submit_col, cancel_col = st.columns([0.8, 0.2])
                with submit_col: submitted = st.form_submit_button("➕ Add Maintenance Record", type="primary", use_container_width=True)
                with cancel_col:
                    if st.form_submit_button("❌ Cancel", use_container_width=True, type="secondary"): st.session_state.show_add_maintenance_form_main = False; st.rerun()
                if submitted:
                    if not actual_address_for_record or not description or not date or not category or not urgency: st.error("🚨 Please fill in all required fields.")
                    else:
                        new_record = MaintenanceRecord(date.strftime("%Y-%m-%d"), category, description, cost, contractor, urgency, actual_address_for_record)
                        st.session_state.maintenance_records.append(new_record)
                        st.session_state.show_add_maintenance_form_main = False
                        st.success(f"✅ Maintenance record added for '{actual_address_for_record}'. Returning to dashboard..."); import time; time.sleep(2); st.rerun()

    def render_edit_property_form_main_panel(self):
        st.header("✏️ Edit Property Information")
        property_to_edit_address = st.session_state.editing_property_address
        prop_idx = next((i for i, p in enumerate(st.session_state.properties) if p.address == property_to_edit_address), -1)
        if prop_idx == -1:
            st.error("Could not find property to edit."); 
            if st.button("Back to Dashboard"): st.session_state.editing_property_address = None; st.rerun()
            return
        prop_to_edit = st.session_state.properties[prop_idx]
        st.caption(f"Modifying details for: {prop_to_edit.address}, {prop_to_edit.city}, {prop_to_edit.state.upper()}")
        with st.container(border=True):
            default_last_inspection = datetime.datetime.strptime(prop_to_edit.last_inspection, "%Y-%m-%d").date() if prop_to_edit.last_inspection and prop_to_edit.last_inspection != "N/A" else None
            with st.form(f"edit_property_form_{prop_to_edit.address.replace(' ','_')}", clear_on_submit=False):
                st.markdown("##### Property Location")
                address = st.text_input("Property Address *", value=prop_to_edit.address)
                city = st.text_input("City *", value=prop_to_edit.city)
                state = st.text_input("State *", value=prop_to_edit.state, max_chars=2)
                zip_code = st.text_input("ZIP Code *", value=prop_to_edit.zip_code)
                st.markdown("##### Property Details")
                col1, col2 = st.columns(2)
                with col1:
                    year_built = st.number_input("Year Built", value=prop_to_edit.year_built, step=1)
                    property_type_options = ["Single Family", "Townhouse", "Condo", "Multi-Family", "Commercial"]
                    property_type = st.selectbox("Property Type", property_type_options, index=property_type_options.index(prop_to_edit.property_type) if prop_to_edit.property_type in property_type_options else 0)
                    roof_material_options = list(self.calculator.roof_material_expected_lifespans.keys())
                    roof_material = st.selectbox("Roof Material", roof_material_options, index=roof_material_options.index(prop_to_edit.roof_material) if prop_to_edit.roof_material in roof_material_options else 0)
                    roof_age = st.number_input("Roof Age (years)", value=prop_to_edit.roof_age, step=1) 
                    hvac_age = st.number_input("HVAC Age (years)", value=prop_to_edit.hvac_age, step=1)
                with col2:
                    square_footage = st.number_input("Square Footage", value=prop_to_edit.square_footage, step=50)
                    foundation_type_options = list(self.calculator.foundation_scores.keys())
                    foundation_type = st.selectbox("Foundation Type", foundation_type_options, index=foundation_type_options.index(prop_to_edit.foundation_type) if prop_to_edit.foundation_type in foundation_type_options else 0)
                    electrical_age = st.number_input("Electrical System Age (years)", value=prop_to_edit.electrical_age, step=1)
                    plumbing_age = st.number_input("Plumbing System Age (years)", value=prop_to_edit.plumbing_age, step=1)
                st.markdown("##### Inspection & Photo")
                last_inspection_date = st.date_input("Last Major Inspection Date", value=default_last_inspection)
                if prop_to_edit.image_data: st.image(prop_to_edit.image_data, width=200)
                uploaded_photo = st.file_uploader("Upload New Property Photo", type=["png", "jpg", "jpeg"])
                submit_col, cancel_col = st.columns([0.8, 0.2])
                with submit_col: submitted = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
                with cancel_col:
                    if st.form_submit_button("❌ Cancel", use_container_width=True, type="secondary"): st.session_state.editing_property_address = None; st.rerun()
                if submitted:
                    if not all([address, city, state, zip_code]): st.error("🚨 Address, City, State, and ZIP Code are required!")
                    else:
                        p_edit = st.session_state.properties[prop_idx]
                        p_edit.address, p_edit.city, p_edit.state, p_edit.zip_code = address, city, state.upper(), zip_code
                        p_edit.year_built, p_edit.square_footage, p_edit.property_type = year_built, square_footage, property_type
                        p_edit.roof_material, p_edit.roof_age, p_edit.foundation_type = roof_material, roof_age, foundation_type
                        p_edit.hvac_age, p_edit.electrical_age, p_edit.plumbing_age = hvac_age, electrical_age, plumbing_age
                        p_edit.last_inspection = last_inspection_date.strftime("%Y-%m-%d") if last_inspection_date else "N/A"
                        if uploaded_photo: p_edit.image_data = uploaded_photo.getvalue()
                        st.session_state.editing_property_address = None
                        st.success(f"✅ Property '{address}' updated successfully!"); st.balloons(); import time; time.sleep(2); st.rerun()

    def render_property_documents(self, property_data: Property):
        with st.container(border=True):
            st.subheader("📎 Property Documents")
            prop_idx = next((i for i, p in enumerate(st.session_state.properties) if p.address == property_data.address), -1)
            if prop_idx == -1: st.error("Error: Could not find property."); return
            uploaded_files = st.file_uploader("Upload new document(s)", type=None, accept_multiple_files=True, key=f"doc_uploader_{property_data.address.replace(' ','_')}")
            if uploaded_files:
                files_added_count = 0
                for up_file in uploaded_files:
                    st.session_state.properties[prop_idx].documents.append({"name": up_file.name, "data": up_file.getvalue(), "type": up_file.type, "upload_time": datetime.datetime.now()})
                    files_added_count +=1
                if files_added_count > 0: st.success(f"{files_added_count} document(s) uploaded!"); st.rerun()
            if not st.session_state.properties[prop_idx].documents: st.info("No documents uploaded yet.")
            else:
                st.markdown("**Uploaded Documents:**")
                for i, doc in enumerate(st.session_state.properties[prop_idx].documents):
                    cols = st.columns([0.6, 0.2, 0.2])
                    cols[0].write(f"📄 **{doc['name']}** ({doc['upload_time'].strftime('%Y-%m-%d %H:%M')})")
                    cols[1].download_button("⬇️ Download", io.BytesIO(doc['data']), doc['name'], doc.get('type', 'application/octet-stream'), key=f"dl_doc_{prop_idx}_{i}")
                    if cols[2].button("🗑️ Delete", key=f"del_doc_{prop_idx}_{i}", type="secondary"):
                        del st.session_state.properties[prop_idx].documents[i]; st.success(f"Doc '{doc['name']}' deleted."); st.rerun()
                    st.caption(f"Type: {doc.get('type', 'N/A')}, Size: {len(doc['data'])/1024:.1f} KB")
                    if i < len(st.session_state.properties[prop_idx].documents) - 1: st.divider() 
        st.markdown("---")

    def render_health_score_visualization(self, property_data: Property):
        with st.container(border=True):
            st.subheader(f"📊 Health Snapshot: {property_data.address}, {property_data.city}, {property_data.state.upper()}")
            if st.button("✏️ Edit This Property", key=f"edit_prop_hs_{property_data.address.replace(' ','_')}"):
                st.session_state.editing_property_address = property_data.address; st.rerun()
            scores = self.calculator.calculate_overall_score(property_data)
            cols_main = st.columns([0.4, 0.6]) 
            with cols_main[0]:
                if property_data.image_data: st.image(property_data.image_data, caption=f"{property_data.property_type} at {property_data.address}", use_column_width=True)
                else: st.markdown("<div style='height: 200px; background-color: #f0f2f6; display: flex; align-items: center; justify-content: center; border-radius: 8px;'><span style='color: #aaa; font-style: italic;'>No property image</span></div>", unsafe_allow_html=True)
            with cols_main[1]:
                overall_score_val = scores['overall_score']
                st.metric("Overall Health Score", f"{overall_score_val:.1f} / 100") 
                if overall_score_val >= 85: st.success("Excellent Condition! 👍") 
                elif overall_score_val >= 70: st.info("Good Condition. 👌")
                elif overall_score_val >= 55: st.warning("Fair Condition. Proactive maintenance advised. ⚠️")
                else: st.error("Needs Significant Attention! Prioritize repairs. 🔴")
                st.write("**Category Breakdown:**")
                for cat_name, cat_data in scores['category_scores'].items():
                    score_val = cat_data['score']
                    icon = "🟢" if score_val >= 80 else "🟡" if score_val >= 60 else "🔴"
                    st.markdown(f"{icon} **{cat_name}:** {score_val:.1f}")
        st.markdown("---") 

    def render_weather_display(self, property_zip: str, property_address_display: str):
        with st.container(border=True): 
            st.subheader(f"🌦️ Current Weather for {property_address_display} (ZIP: {property_zip})")
            api_key = st.secrets.get("OPENWEATHERMAP_API_KEY")
            if not api_key: st.warning("OpenWeatherMap API Key not configured.", icon="🔑"); return
            weather_data = get_weather_data(property_zip, api_key)
            if weather_data:
                if weather_data.get("error"): st.error(f"Weather error: {weather_data['error']}", icon="⚠️")
                else:
                    c1, c2, c3 = st.columns(3)
                    if weather_data.get("temp") is not None: c1.metric("Temperature", f"{weather_data['temp']:.0f}°F", delta=f"Feels like {weather_data.get('feels_like', 'N/A'):.0f}°F" if weather_data.get('feels_like') is not None else None)
                    else: c1.metric("Temperature", "N/A")
                    if weather_data.get('icon'): c2.image(f"https://openweathermap.org/img/wn/{weather_data['icon']}@2x.png", caption=weather_data.get('description', 'N/A'), width=80)
                    else: c2.write(weather_data.get('description', 'N/A'))
                    if weather_data.get("humidity") is not None: c3.metric("Humidity", f"{weather_data['humidity']}%")
                    else: c3.metric("Humidity", "N/A")
                    if weather_data.get("wind_speed") is not None: st.markdown(f"**Wind:** {weather_data['wind_speed']:.1f} mph")
                    if weather_data.get("city_name") and weather_data['city_name'] != "N/A": st.caption(f"Location: {weather_data['city_name']}")
            else: st.error("Failed to fetch weather data.", icon="📡")
        st.markdown("---")

    def render_detailed_breakdown(self, property_data: Property):
        with st.container(border=True): 
            st.subheader("🔬 Detailed Component Scores")
            scores = self.calculator.calculate_overall_score(property_data)
            for category, data in scores['category_scores'].items():
                with st.expander(f"{category} Details - Score: {data['score']:.1f}", expanded=(category=="Structural")): 
                    if not data['components']: st.write(f"No components for {category}."); continue
                    comp_cols = st.columns(min(len(data['components']), 3))
                    for idx, (comp, val_raw) in enumerate(data['components'].items()):
                        with comp_cols[idx % len(comp_cols)]:
                            c_score = float(val_raw)
                            color = FOREST_GREEN if c_score >= 80 else PRIMARY_BLUE if c_score >= 60 else "#DC3545"
                            st.markdown(f"**{comp}:**<p style='font-size:1.5em;color:{color};font-weight:bold;'>{c_score:.1f}</p>", unsafe_allow_html=True)
                            # Add age/lifespan details
                            if category == "Structural" and comp.startswith("Roof"): st.caption(f"Age: {property_data.roof_age} yrs (Est. Life: {self.calculator.roof_material_expected_lifespans.get(property_data.roof_material, 'N/A')} yrs)")
                            elif category == "Systems" and comp == "HVAC": st.caption(f"Age: {property_data.hvac_age} yrs (Est. Life: 18 yrs)")
                            elif category == "Systems" and comp == "Electrical": st.caption(f"Age: {property_data.electrical_age} yrs (Est. Life: 35 yrs)")
                            elif category == "Systems" and comp == "Plumbing": st.caption(f"Age: {property_data.plumbing_age} yrs (Est. Life: 50 yrs)")
        st.markdown("---")

    def render_predictions_and_recommendations(self, property_data: Property):
        with st.container(border=True): 
            st.subheader("💡 Predictions & Proactive Recommendations")
            schedule = self.calculator.generate_maintenance_schedule(property_data)
            tab1, tab2 = st.tabs(["🔮 Upcoming Maintenance Tasks", "💰 Cost Planning Tool"]) 
            with tab1:
                st.markdown("**Key Upcoming Maintenance:**")
                if not schedule: st.info("✅ No specific recommendations now.")
                else:
                    for task in schedule[:7]: 
                        icon = {"high": "🔴", "important": "🟡", "routine": "🔵"}[task["priority"]]
                        due_str = task["next_due"].strftime("%b %d, %Y")
                        days_diff = (task["next_due"] - datetime.datetime.now()).days
                        with st.container(border=True, height=130):
                            c1,c2,c3 = st.columns([3,1,1])
                            c1.markdown(f"{icon} **{task['task']}** ({task['frequency']})<br><small>{task['description']}</small>", unsafe_allow_html=True)
                            c2.metric(label="Est. Cost", value=f"${task['estimated_cost']:,}", label_visibility="collapsed")
                            if days_diff <=0: c3.error(f"Due: {due_str} (Overdue!)")
                            elif days_diff <=30: c3.warning(f"Due: {due_str} ({days_diff}d)")
                            else: c3.info(f"Due: {due_str} ({days_diff}d)")
            with tab2:
                st.markdown("**Regional Cost Estimator**")
                st.caption(f"ZIP: {property_data.zip_code} (Region: {self.calculator.get_regional_info(property_data.zip_code)['region']})")
                item_types = list(self.calculator.national_cost_baseline.keys())
                sel_item = st.selectbox("Select Item:", item_types, key=f"cost_est_item_{property_data.address.replace(' ','_')}") 
                if sel_item:
                    est = self.calculator.get_local_cost_estimate(sel_item, property_data.zip_code)
                    ca,cb,cc = st.columns(3); ca.metric("Min", f"${est['min']:,}"); cb.metric("Avg", f"${est['avg']:,}"); cc.metric("Max", f"${est['max']:,}")
                    st.caption(f"National Avg: ${est['national_avg']:,}. Confidence: {est['confidence'].title()}.")

    def render_property_selector(self, key_suffix="main", allow_none=False, help_text="Select Property:"):
        if not st.session_state.properties:
            if key_suffix not in ["contractors", "roi_calc"]: st.info("👈 Add a property to get started!")
            return None
        options_map = { f"{p.address}, {p.city}, {p.state.upper()}" : p.address for p in st.session_state.properties }
        display_options = list(options_map.keys()) 
        session_key = f"selected_property_address_{key_suffix}"
        current_val = st.session_state.get(session_key)
        current_display = next((disp for disp, addr in options_map.items() if addr == current_val), None)
        default_idx = 0
        if allow_none:
            display_options_with_none = ["Select a Property..."] + display_options
            if current_display and current_display in display_options_with_none: default_idx = display_options_with_none.index(current_display)
            elif current_val is None: default_idx = 0
            else: st.session_state[session_key] = None; default_idx = 0
            selected_display = st.selectbox(help_text, display_options_with_none, index=default_idx, key=f"prop_sel_box_{key_suffix}")
            st.session_state[session_key] = options_map.get(selected_display) if selected_display != "Select a Property..." else None
        else: 
            if not display_options: return None 
            if current_display not in display_options or current_display is None: st.session_state[session_key] = options_map[display_options[0]]; default_idx = 0
            else: default_idx = display_options.index(current_display)
            selected_display = st.selectbox(help_text, display_options, index=default_idx, key=f"prop_sel_box_{key_suffix}")
            st.session_state[session_key] = options_map.get(selected_display) 
        final_selected_address = st.session_state.get(session_key)
        return next((prop for prop in st.session_state.properties if prop.address == final_selected_address), None)

    def render_maintenance_history(self, property_address: Optional[str]):
        display_address = "Portfolio Wide" 
        if property_address:
            prop_obj = next((p for p in st.session_state.properties if p.address == property_address), None)
            if prop_obj: display_address = f"{prop_obj.address}, {prop_obj.city}"
            else: display_address = property_address 
        st.subheader(f"🧰 Maintenance History for {display_address}")
        records_to_show = [r for r in st.session_state.maintenance_records if not property_address or r.property_address == property_address]
        if not records_to_show: st.info("No maintenance records found matching criteria."); return
        urgency_options = ["All"] + sorted(list(set(r.urgency for r in records_to_show)))
        filter_key_suffix = property_address.replace(" ", "_").replace(",", "") if property_address else "all"
        session_filter_key = f"maintenance_filter_urgency_{filter_key_suffix}"
        if session_filter_key not in st.session_state: st.session_state[session_filter_key] = "All"
        selected_urgency = st.selectbox("Filter by Urgency:", urgency_options, index=urgency_options.index(st.session_state[session_filter_key]), key=f"maint_hist_sel_{filter_key_suffix}")
        st.session_state[session_filter_key] = selected_urgency 
        if selected_urgency != "All": records_to_show = [r for r in records_to_show if r.urgency == selected_urgency]
        if not records_to_show: st.info(f"No records match '{selected_urgency}' urgency for {display_address}."); return
        df_data = [{'Date': r.date, 'Property': (next((f"{p.address}, {p.city}" for p in st.session_state.properties if p.address == r.property_address),"N/A")) if not property_address else None,
                    'Category': r.category, 'Description': r.description, 'Cost ($)': r.cost, 'Contractor': r.contractor, 'Urgency': r.urgency} for r in records_to_show]
        if property_address: df_data = [{k:v for k,v in item.items() if k != 'Property'} for item in df_data] # Remove property column if filtered
        
        cols_order = ['Date', 'Property', 'Category', 'Description', 'Cost ($)', 'Contractor', 'Urgency'] if not property_address else ['Date', 'Category', 'Description', 'Cost ($)', 'Contractor', 'Urgency']
        records_df = pd.DataFrame(df_data).sort_values(by=['Date', 'Urgency'], ascending=[False, True], key=lambda col: col.map({"High":0, "Medium":1, "Routine":2}) if col.name == 'Urgency' else col)
        st.dataframe(records_df[cols_order], use_container_width=True, height=300, column_config={"Cost ($)": st.column_config.NumberColumn(format="$%.2f"), "Description": st.column_config.TextColumn(width="large")})
        st.markdown(f"**Total Cost (Filtered):** ${sum(r['Cost ($)'] for r in df_data):,.2f}")
        st.markdown("---")

    def render_comparative_health_chart(self):
        if len(st.session_state.properties) > 1:
            st.subheader("📊 Comparative Property Health Scores")
            prop_scores = [{"Property": f"{p.address}, {p.city}", **{k:v['score'] for k,v in self.calculator.calculate_overall_score(p)['category_scores'].items()}, "Overall Score": self.calculator.calculate_overall_score(p)['overall_score']} for p in st.session_state.properties]
            df = pd.DataFrame(prop_scores)
            score_types = ["Overall Score", "Structural", "Systems", "Safety", "Environmental"]
            sel_scores = st.multiselect("Select scores to compare:", options=score_types, default=["Overall Score"], key="compare_multiselect")
            if sel_scores: st.bar_chart(df.set_index("Property")[sel_scores], height=400, color=[FOREST_GREEN, PRIMARY_BLUE, "#FFC107", "#DC3545"]) # Example colors
            else: st.info("Select score types to display chart.")
        elif st.session_state.properties: st.info("Add at least two properties for comparison.")
        st.markdown("---")

    def render_contractor_marketplace(self):
        st.subheader("🛠️ Find Certified Professionals (Demo)")
        st.info("Placeholder for contractor marketplace integration.")
        # Demo data and logic here...

    def render_roi_calculator(self):
        st.header("💰 Return on Investment (ROI) Calculator")
        # Demo data and logic here...
        if not st.session_state.properties: st.info("Add a property first to use ROI Calculator."); return
        # Full ROI calculator logic... (shortened for brevity of this diagnostic step)
        st.text_input("Improvement Name:", key="roi_improvement_name_text_input_diag")
        st.number_input("Cost:", key="roi_estimated_cost_num_input_diag")
        if st.button("Calculate ROI (Demo)", key="roi_calculate_button_diag"): st.write("ROI calculation pending full implementation.")


    def run(self):
        if not self.auth_manager.is_authenticated():
            self.auth_manager.render_auth_screen()
            return

        apply_global_styles() 
        self.render_header()

        with st.sidebar:
            self.auth_manager.render_session_info()
            with st.expander("⚙️ App Settings", expanded=False):
                st.caption("Weather API key configured via Streamlit Secrets.")
            self.render_quick_actions()
            st.markdown("---")
            self.render_property_management_sidebar() 
            st.markdown("---")
            st.sidebar.header("🛠️ Maintenance Log") 
            st.sidebar.caption("Use Quick Action button to log.") 
            st.markdown("---")
            st.sidebar.caption(f"© {datetime.datetime.now().year} Property Health Intel.") 

        if st.session_state.get('editing_property_address') is not None: self.render_edit_property_form_main_panel()
        elif st.session_state.get('show_add_property_form_main', False): self.render_add_property_form_main_panel()
        elif st.session_state.get('show_add_maintenance_form_main', False): self.render_add_maintenance_form_main_panel()
        else:
            tab_options = ["📈 Property Health", "🧰 Maintenance Center", "🤝 Find Contractors", "📊 Analytics Hub", "💰 ROI Calculator"]
            if 'active_tab' not in st.session_state or st.session_state.active_tab not in tab_options:
                st.session_state.active_tab = tab_options[0]
            
            # Simplified tab selection for stability, will render all content under their respective tabs
            tabs_tuple = st.tabs(tab_options) 
            
            with tabs_tuple[0]: # Property Health
                st.header("Property Health Dashboard")
                st.caption("View detailed health scores, upcoming maintenance, and local weather for your selected property.")
                if not st.session_state.properties: st.info("👋 Welcome! Add your first property to get started.")
                else:
                    selected_property = self.render_property_selector("health", help_text="Select Property for Health View:")
                    if selected_property:
                        self.render_health_score_visualization(selected_property) 
                        self.render_weather_display(selected_property.zip_code, f"{selected_property.address}, {selected_property.city}")
                        self.render_detailed_breakdown(selected_property)
                        self.render_predictions_and_recommendations(selected_property)
                        self.render_property_documents(selected_property) 
                    else: st.info("👈 Select a property to view its detailed health snapshot.")

            with tabs_tuple[1]: # Maintenance Center
                st.header("Maintenance Center")
                st.caption("Log, view, and filter maintenance records.")
                if not st.session_state.properties: st.info("Add a property first to log and view maintenance records.")
                else:
                    selected_prop_maint = self.render_property_selector("maintenance", allow_none=True, help_text="Filter by Property (or 'Select...' for all):")
                    self.render_maintenance_history(selected_prop_maint.address if selected_prop_maint else None)
            
            with tabs_tuple[2]: # Find Contractors
                st.header("Contractor Marketplace")
                self.render_contractor_marketplace()

            with tabs_tuple[3]: # Analytics Hub
                st.header("Portfolio Analytics Hub")
                self.render_comparative_health_chart()
                
            with tabs_tuple[4]: # ROI Calculator
                self.render_roi_calculator()

def main():
    dashboard = Dashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
