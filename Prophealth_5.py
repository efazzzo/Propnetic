#!/usr/bin/env python3
# Prophealth_3.py

import streamlit as st
st.set_page_config(page_title="Property Health Intelligence Platform", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")
import pandas as pd
import numpy as np
import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

# For item 2 (Color-code metrics) from "Quick Wins"
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
    year_built: int
    square_footage: int
    property_type: str
    roof_material: str
    foundation_type: str
    hvac_age: int
    electrical_age: int
    plumbing_age: int
    last_inspection: str
    image_data: Optional[bytes] = None # Quick Win 1: Add property photos
    zip_code: str = "22701"

@dataclass
class MaintenanceRecord:
    date: str
    category: str
    description: str
    cost: float
    contractor: str
    urgency: str
    property_address: str # Link record to a property

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
        if zip_code and zip_code[0] in self.regional_multipliers:
            return self.regional_multipliers[zip_code[0]]
        return self.regional_multipliers["default"]

    def get_local_cost_estimate(self, item_type: str, zip_code: str = "22701") -> Dict:
        if item_type not in self.national_cost_baseline:
            return {"min": 0, "max": 0, "avg": 0, "confidence": "low", "region": "Unknown"}
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
        if expected_life <=0: return 0.0 # Avoid division by zero if expected_life is invalid
        ratio = age / expected_life
        if ratio <= 0.5: return 100.0 - (ratio * 20.0)
        elif ratio <= 0.8: return 90.0 - ((ratio - 0.5) / 0.3 * 30.0)
        else: return max(0.0, 60.0 - ((ratio - 0.8) / 0.2 * 60.0))


    def calculate_structural_score(self, property_data: Property) -> Dict:
        current_year = datetime.datetime.now().year
        age = current_year - property_data.year_built
        foundation_scores = {'Concrete Slab': 85, 'Basement': 90, 'Crawl Space': 75, 'Pier & Beam': 70}
        roof_scores = {'Asphalt Shingles': 80, 'Metal': 90, 'Tile': 95, 'Slate': 98, 'Wood': 70, 'Composite': 75, 'Flat Roof (TPO/EPDM)': 70}
        age_score = self.calculate_age_score(age, 80)
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
        if age > 50: base_score -= 10
        return {'score': round(base_score, 1), 'components': {'General Safety': round(base_score,1)}}

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
        return {'overall_score': round(overall, 1),
                'category_scores': {'Structural': structural, 'Systems': systems, 'Safety': safety, 'Environmental': environmental}}

    def generate_maintenance_schedule(self, property_data: Property) -> List[Dict]:
        schedule = []
        current_date = datetime.datetime.now()
        zip_code = property_data.zip_code

        if property_data.hvac_age <= 1:
             cost_est = self.get_local_cost_estimate("hvac_service", zip_code)
             schedule.append({"task": "HVAC Filter Check/Replacement", "frequency": "Every 3 months", "next_due": current_date + datetime.timedelta(days=90), "priority": "routine", "estimated_cost": cost_est["min"] // 4 , "description": "Check and replace air filters as needed."})
        elif property_data.hvac_age <= 12:
            cost_est = self.get_local_cost_estimate("hvac_service", zip_code)
            schedule.append({"task": "HVAC Annual Service", "frequency": "Annually", "next_due": current_date + datetime.timedelta(days=365), "priority": "important", "estimated_cost": cost_est["avg"], "description": "Professional tune-up and inspection."})
        else:
            cost_est_repl = self.get_local_cost_estimate("hvac_replacement", zip_code)
            schedule.append({"task": "HVAC Replacement Planning", "frequency": "Within 1-2 years", "next_due": current_date + datetime.timedelta(days=365), "priority": "high", "estimated_cost": cost_est_repl["avg"], "description": "Budget and plan for HVAC system replacement."})

        if property_data.electrical_age > 30:
            cost_est_panel_check = self.get_local_cost_estimate("electrical_panel", zip_code) # using panel cost as a proxy for inspection basis
            schedule.append({"task": "Electrical System Inspection", "frequency": "Consider within 1 year", "next_due": current_date + datetime.timedelta(days=365), "priority": "important", "estimated_cost": max(150, cost_est_panel_check["min"] // 5) , "description": "Inspect aging electrical panel and system."})
        if property_data.electrical_age > 40:
             schedule.append({"task": "Consider Electrical Panel Upgrade", "frequency": "Within 2-3 years", "next_due": current_date + datetime.timedelta(days=730), "priority": "high", "estimated_cost": self.get_local_cost_estimate("electrical_panel", zip_code)["avg"], "description": "Plan for upgrading an old electrical panel."})

        if property_data.plumbing_age > 10 : # Water heater general check if > 10 years. Avg life 8-12.
            if property_data.plumbing_age > self.calculate_age_score(property_data.plumbing_age, 12): # Arbitrary, needs better WH age tracking
                cost_est_wh = self.get_local_cost_estimate("water_heater", zip_code)
                schedule.append({"task": "Water Heater Check/Service", "frequency": "Within 1 year", "next_due": current_date + datetime.timedelta(days=365), "priority": "important", "estimated_cost": cost_est_wh["min"] // 2, "description": "Inspect water heater, plan for replacement if old."})
        if property_data.plumbing_age > 40:
             cost_est_repair = self.get_local_cost_estimate("plumbing_repair", zip_code)
             schedule.append({"task": "Major Plumbing Inspection", "frequency": "Within 2 years", "next_due": current_date + datetime.timedelta(days=730), "priority": "high", "estimated_cost": cost_est_repair["avg"], "description": "Inspect for potential major plumbing updates (pipes, main lines)."})

        # This needs actual roof age if possible, not just property age/material.
        # For now, a generic reminder for older properties.
        if (current_date.year - property_data.year_built) > 15 :
            cost_est_roof_repair = self.get_local_cost_estimate("roof_repair", zip_code)
            schedule.append({"task": "Roof Inspection", "frequency": "Annually", "next_due": current_date + datetime.timedelta(days=365), "priority": "important", "estimated_cost": cost_est_roof_repair["min"], "description": "Inspect roof for wear, potential leaks, and clear debris."})

        cost_est_gutter_clean = max(150, self.get_local_cost_estimate("gutter_replacement", zip_code)["min"] // 10)
        schedule.append({"task": "Gutter Cleaning (Spring)", "frequency": "Annually (Spring)", "next_due": current_date + datetime.timedelta(days=120), "priority": "routine", "estimated_cost": cost_est_gutter_clean , "description": "Clean gutters and downspouts after winter."})
        schedule.append({"task": "Gutter Cleaning (Fall)", "frequency": "Annually (Fall)", "next_due": current_date + datetime.timedelta(days=300), "priority": "routine", "estimated_cost": cost_est_gutter_clean, "description": "Clean gutters and downspouts before winter."})
        schedule.append({"task": "Exterior Caulking & Sealing Check", "frequency": "Annually", "next_due": current_date + datetime.timedelta(days=270), "priority": "routine", "estimated_cost": 100, "description": "Check windows, doors, and siding for gaps."})

        schedule.sort(key=lambda x: ({"high": 0, "important": 1, "routine": 2}[x["priority"]], x["next_due"]))
        return schedule

class AuthenticationManager:
    def __init__(self):
        self.password = "PropHealth2025!" # Keep simple for prototype

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

        s_full_name = st.session_state.get("auth_full_name", "")
        s_email_address = st.session_state.get("auth_email_address", "")
        s_company_org = st.session_state.get("auth_company_org", "") 
        s_access_purpose = st.session_state.get("auth_access_purpose", "")
        s_password_input = st.session_state.get("auth_password_input", "")

        all_acknowledged = confidential_understood and respect_ip and professional_courtesy and authorized_access
        password_correct = s_password_input == self.password
        signature_complete = s_full_name.strip() != "" and s_email_address.strip() != "" and s_access_purpose != ""
        email_valid = "@" in s_email_address and "." in s_email_address.split('@')[-1] if s_email_address and "@" in s_email_address else False


        access_button_disabled = not (all_acknowledged and signature_complete and email_valid and s_password_input)

        if st.button("🚀 ACCESS PREVIEW", type="primary", disabled=access_button_disabled):
            if password_correct:
                st.session_state.access_info = {
                    'name': st.session_state.get("auth_full_name", ""),
                    'email': st.session_state.get("auth_email_address", ""),
                    'company': st.session_state.get("auth_company_org", ""),
                    'purpose': st.session_state.get("auth_access_purpose", ""),
                    'timestamp': datetime.datetime.now()
                }
                st.session_state.authenticated = True
                st.session_state.access_timestamp = datetime.datetime.now()
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
            if st.sidebar.button("🚪 End Session & Logout", type="secondary", use_container_width=True):
                auth_keys_to_clear = [k for k in st.session_state.keys() if k.startswith('auth_')]
                other_session_keys = ['access_info', 'authenticated', 'access_timestamp', 
                                      'show_add_property_form', 'show_add_maintenance_form', 'active_tab',
                                      'maintenance_filter_urgency'] # Include other transient states
                
                # Keys for property selectors might also need clearing if they persist unwantedly
                prop_selector_keys = [k for k in st.session_state.keys() if k.startswith('selected_property_address_')]

                for key_to_del in auth_keys_to_clear + other_session_keys + prop_selector_keys:
                    if key_to_del in st.session_state:
                        del st.session_state[key_to_del]
                
                # Optionally clear main data or keep it:
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
        if 'properties' not in st.session_state:
            st.session_state.properties = []
        if 'maintenance_records' not in st.session_state:
            st.session_state.maintenance_records = []
        if 'show_add_property_form' not in st.session_state:
            st.session_state.show_add_property_form = False # Default to closed
        if 'show_add_maintenance_form' not in st.session_state:
            st.session_state.show_add_maintenance_form = False # Default to closed
        if 'active_tab' not in st.session_state:
             st.session_state.active_tab = "📈 Property Health" # Default active tab

    def render_header(self):
        st.title("🏠 Property Health Intelligence Dashboard")
        st.markdown("Your partner in proactive property care. *Beta Preview v0.3.1*") # Minor version bump
        st.markdown("---")

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
                avg_score_val = np.mean([self.calculator.calculate_overall_score(prop)['overall_score'] for prop in st.session_state.properties])
                avg_score_str = f"{avg_score_val:.1f}"
                if avg_score_val >= 85: avg_score_color = "bg-green-custom"
                elif avg_score_val >= 70: avg_score_color = "bg-yellow-custom"
                else: avg_score_color = "bg-red-custom"
            except Exception as e: # Catch potential errors if a property score can't be calculated
                avg_score_str = "Error"
                avg_score_color = "bg-red-custom"
                print(f"Error calculating avg_score: {e}")


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
        estimated_savings = preventative_maintenance_cost * 0.15
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
                 st.session_state.show_add_maintenance_form = False 
            st.rerun()

        add_maint_disabled = not st.session_state.properties
        if st.sidebar.button("📝 Log Maintenance Task", use_container_width=True, disabled=add_maint_disabled, key="quick_log_maint_btn"):
            st.session_state.show_add_maintenance_form = not st.session_state.get('show_add_maintenance_form', False)
            if st.session_state.show_add_maintenance_form: # if we just opened it
                st.session_state.show_add_property_form = False
            st.rerun()
        
        view_urgent_disabled = not any(r.urgency == "High" for r in st.session_state.maintenance_records)
        if st.sidebar.button("❗ View Urgent Tasks", use_container_width=True, disabled=view_urgent_disabled, key="quick_view_urgent_btn"):
            st.session_state.active_tab = "🧰 Maintenance Center"
            st.session_state.maintenance_filter_urgency = "High"
            st.toast("Switched to Maintenance tab with 'High' urgency filter.", icon="❗")
            st.rerun()

    def render_property_management(self):
        st.sidebar.header("🏡 Property Portfolio")
        expanded_add_prop = st.session_state.get('show_add_property_form', False)
        with st.sidebar.expander("➕ Add New Property", expanded=expanded_add_prop):
            with st.form("property_form", clear_on_submit=True):
                address = st.text_input("Property Address *")
                zip_code = st.text_input("ZIP Code *", value="22701", help="For regional cost estimates and local context.")
                year_built = st.number_input("Year Built", min_value=1800, max_value=datetime.datetime.now().year, value=2000)
                square_footage = st.number_input("Square Footage", min_value=100, max_value=20000, value=1500, step=50)
                property_type = st.selectbox("Property Type", ["Single Family", "Townhouse", "Condo", "Multi-Family", "Commercial"])
                roof_material = st.selectbox("Roof Material", ["Asphalt Shingles", "Metal", "Tile", "Slate", "Wood", "Composite", "Flat Roof (TPO/EPDM)"])
                foundation_type = st.selectbox("Foundation Type", ["Concrete Slab", "Basement", "Crawl Space", "Pier & Beam"])
                hvac_age = st.number_input("HVAC Age (years)", min_value=0, max_value=50, value=5)
                electrical_age = st.number_input("Electrical System Age (years)", min_value=0, max_value=100, value=15)
                plumbing_age = st.number_input("Plumbing System Age (years)", min_value=0, max_value=100, value=20)
                last_inspection_date = st.date_input("Last Major Inspection Date", value=None) # Allow None
                
                uploaded_photo = st.file_uploader("Upload Property Photo (Optional)", type=["png", "jpg", "jpeg"])
                submitted = st.form_submit_button("✅ Add Property to Portfolio", type="primary", use_container_width=True)

                if submitted:
                    if not address or not zip_code:
                        st.error("🚨 Address and ZIP Code are required!")
                    else:
                        image_bytes = uploaded_photo.getvalue() if uploaded_photo else None
                        last_inspection_str = last_inspection_date.strftime("%Y-%m-%d") if last_inspection_date else "N/A"
                        new_property = Property(address, year_built, square_footage, property_type,
                                                roof_material, foundation_type, hvac_age, electrical_age,
                                                plumbing_age, last_inspection_str, image_bytes, zip_code)
                        st.session_state.properties.append(new_property)
                        st.session_state.show_add_property_form = False
                        st.success(f"✅ Property '{address}' added successfully!")
                        st.rerun()

        if st.session_state.properties:
            with st.sidebar.expander("🗑️ Manage Properties"):
                prop_options = {f"{i+1}. {prop.address} ({prop.zip_code})": i for i, prop in enumerate(st.session_state.properties)}
                selected_prop_label_to_delete = st.selectbox("Select property to remove:", [""] + list(prop_options.keys()), index=0, placeholder="Choose property...", key="delete_prop_select")
                
                if selected_prop_label_to_delete and selected_prop_label_to_delete != "":
                    if st.button("🗑️ Delete Selected Property", type="secondary", use_container_width=True, key="delete_prop_btn"):
                        idx_to_delete = prop_options[selected_prop_label_to_delete]
                        deleted_property_address = st.session_state.properties[idx_to_delete].address
                        
                        st.session_state.maintenance_records = [
                            record for record in st.session_state.maintenance_records
                            if record.property_address != deleted_property_address
                        ]
                        del st.session_state.properties[idx_to_delete]
                        st.success(f"🗑️ Property '{deleted_property_address}' and its maintenance records removed.")
                        st.rerun()
    
    def render_maintenance_input(self):
        if not st.session_state.properties:
            # This message is shown by the quick action button if disabled
            return

        st.sidebar.header("🛠️ Maintenance Log")
        expanded_add_maint = st.session_state.get('show_add_maintenance_form', False)
        with st.sidebar.expander("➕ Add New Maintenance Record", expanded=expanded_add_maint):
            if not st.session_state.properties: # Should be caught by quick action disable
                 st.warning("Please add a property first using the 'Quick Actions' panel.")
                 return

            property_addresses = [prop.address for prop in st.session_state.properties]
            with st.form("maintenance_form", clear_on_submit=True):
                selected_address = st.selectbox("Select Property *", property_addresses, index=0 if property_addresses else None)
                date = st.date_input("Date of Service/Record *", datetime.date.today())
                category = st.selectbox("Category *", ["HVAC", "Plumbing", "Electrical", "Roofing", "Foundation", "Appliances", "Pest Control", "Landscaping", "General Repair", "Inspection", "Other"])
                description = st.text_area("Description of Work / Issue *", height=100)
                cost = st.number_input("Cost ($)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
                contractor = st.text_input("Contractor/Vendor (if any)")
                urgency = st.selectbox("Urgency *", ["Routine", "Medium", "High"])
                submitted = st.form_submit_button("➕ Add Maintenance Record", type="primary", use_container_width=True)

                if submitted:
                    if not selected_address or not description or not date or not category or not urgency:
                        st.error("🚨 Please fill in all required fields for the maintenance record.")
                    else:
                        new_record = MaintenanceRecord(date.strftime("%Y-%m-%d"), category, description, cost, contractor, urgency, selected_address)
                        st.session_state.maintenance_records.append(new_record)
                        st.session_state.show_add_maintenance_form = False
                        st.success(f"✅ Maintenance record added for '{selected_address}'.")
                        st.rerun()

    def render_property_selector(self, key_suffix="main", allow_none=False, help_text="Select Property to View Details:"):
        if not st.session_state.properties:
            if key_suffix != "contractors": # Don't show for contractor tab if no props
                st.info("👈 Add a property via the sidebar to get started!")
            return None

        options = [prop.address for prop in st.session_state.properties]
        
        current_selection_val = None
        session_key_for_selection = f"selected_property_address_{key_suffix}"

        if allow_none:
            options_with_none = ["Select a Property..."] + options
            current_selection_val = st.session_state.get(session_key_for_selection) # Could be None or an address
            if current_selection_val not in options: # If it's None or an old address not in current options
                current_selection_idx = 0 # Default to "Select a Property..."
            else:
                current_selection_idx = options_with_none.index(current_selection_val)
            
            selected_address = st.selectbox(help_text, options_with_none, index=current_selection_idx, key=f"prop_select_box_{key_suffix}")
            st.session_state[session_key_for_selection] = selected_address if selected_address != "Select a Property..." else None

        else: # Not allowing None
            if not options: return None # No properties to select
            current_selection_val = st.session_state.get(session_key_for_selection)
            if current_selection_val not in options: # If current selection is invalid or None
                current_selection_idx = 0 # Default to first property
                st.session_state[session_key_for_selection] = options[0]
            else:
                current_selection_idx = options.index(current_selection_val)

            selected_address = st.selectbox(help_text, options, index=current_selection_idx, key=f"prop_select_box_{key_suffix}")
            st.session_state[session_key_for_selection] = selected_address
            
        # Return the actual property object
        if st.session_state.get(session_key_for_selection):
            for prop_obj in st.session_state.properties:
                if prop_obj.address == st.session_state[session_key_for_selection]:
                    return prop_obj
        return None


    def render_health_score_visualization(self, property_data: Property):
        scores = self.calculator.calculate_overall_score(property_data)
        st.subheader(f"📊 Health Snapshot: {property_data.address}")
        
        cols = st.columns([0.4, 0.6])
        with cols[0]:
            if property_data.image_data:
                st.image(property_data.image_data, caption=f"{property_data.property_type} at {property_data.address}", use_column_width=True)
            else:
                st.markdown("<div style='height: 200px; background-color: #f0f2f6; display: flex; align-items: center; justify-content: center; border-radius: 8px;'><span style='color: #aaa; font-style: italic;'>No property image</span></div>", unsafe_allow_html=True)

        with cols[1]:
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
                    # Check if comp_cols is a list or a single object (if num_components is 1)
                    current_col = comp_cols[idx] if num_components > 1 else comp_cols[0] 
                    with current_col:
                        c_score = float(score_val_raw) # Assume score is already a number
                        color = "green" if c_score >= 80 else "orange" if c_score >= 60 else "red"
                        st.markdown(f"**{component}:**")
                        st.markdown(f"<p style='font-size: 1.5em; color:{color}; font-weight:bold;'>{c_score:.1f}</p>", unsafe_allow_html=True)
                    idx+=1
        st.markdown("---")

    def render_maintenance_history(self, property_address: Optional[str]):
        if property_address:
            st.subheader(f"🧰 Maintenance History for {property_address}")
            property_records = [r for r in st.session_state.maintenance_records if r.property_address == property_address]
            if not property_records:
                st.info("No maintenance records found for this property yet.")
        else: # Portfolio wide view
            st.subheader("🧰 All Maintenance Records (Portfolio Wide)")
            property_records = st.session_state.maintenance_records
            if not property_records:
                st.info("No maintenance records in the system yet.")
        
        if not property_records: return

        urgency_options = ["All"] + sorted(list(set(r.urgency for r in property_records)))
        default_urgency = st.session_state.pop("maintenance_filter_urgency", "All") # Use and clear
        if default_urgency not in urgency_options: default_urgency = "All"
        
        selected_urgency = st.selectbox("Filter by Urgency:", urgency_options, 
                                        index=urgency_options.index(default_urgency), 
                                        key=f"maint_hist_urgency_filter_{property_address or 'all'}")

        filtered_records = property_records
        if selected_urgency != "All":
            filtered_records = [r for r in filtered_records if r.urgency == selected_urgency]

        if not filtered_records:
            st.info(f"No records match '{selected_urgency}' urgency.")
            return

        df_data = [{'Date': r.date, 
                    'Category': r.category, 
                    'Description': r.description,
                    'Cost ($)': r.cost, 
                    'Contractor': r.contractor, 
                    'Urgency': r.urgency} 
                   for r in filtered_records]
        if not property_address: # Add property address if it's portfolio view
            for i, r in enumerate(filtered_records):
                df_data[i]['Property'] = r.property_address
            column_order = ['Date', 'Property', 'Category', 'Description', 'Cost ($)', 'Contractor', 'Urgency']
        else:
            column_order = ['Date', 'Category', 'Description', 'Cost ($)', 'Contractor', 'Urgency']

        records_df = pd.DataFrame(df_data)
        urgency_map = {"High":0, "Medium":1, "Routine":2}
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
                for task in schedule[:7]:
                    priority_icon = {"high": "🔴", "important": "🟡", "routine": "🔵"}[task["priority"]]
                    days_until = (task["next_due"] - datetime.datetime.now()).days
                    due_date_str = task["next_due"].strftime("%b %d, %Y")
                    with st.container(border=True, height=130): # Added fixed height
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
            selected_item = st.selectbox("Select Item for Cost Estimate:", cost_item_types, index =0, key=f"cost_est_item_{property_data.address}")
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
                    "Property Address": p.address,
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
                chart_df = df.set_index("Property Address")[score_types_to_plot]
                st.bar_chart(chart_df, height=400)
            else:
                st.info("Select at least one score type to display the chart.")
        elif st.session_state.properties:
            st.info("Add at least two properties to see a comparative health chart.")
        st.markdown("---")

    def render_contractor_marketplace(self):
        st.subheader("🛠️ Find Certified Professionals (Marketplace - Demo)")
        st.info("This section is a placeholder for a future contractor marketplace integration.")
        # ... (contractor list and logic as before) ...
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
            st.write(f"Showing contractors potentially serving ZIP: **{current_prop_zip}**")
            filtered_contractors = [c for c in contractors if current_prop_zip in c['zip_coverage'] or current_prop_zip[0] in [z[0] for z in c['zip_coverage']]]
            if not filtered_contractors:
                 st.warning(f"No contractors found directly matching ZIP {current_prop_zip}. Showing general list.")
                 filtered_contractors = contractors # Fallback to all
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
                    st.caption(f"Serves: {', '.join(contractor['zip_coverage'][:2])}...")
                with col3:
                    if st.button(f"Contact {contractor['name'].split(' ')[0]}", key=f"contact_{contractor['name'].replace(' ', '_')}"): # Ensure key is valid
                        st.success(f"Contact info for {contractor['name']}: {contractor['contact_info']}")


    def run(self):
        if not self.auth_manager.is_authenticated():
            self.auth_manager.render_auth_screen()
            return

        self.render_header()
        with st.sidebar:
            self.auth_manager.render_session_info()
            self.render_quick_actions()
            st.markdown("---")
            self.render_property_management()
            st.markdown("---")
            self.render_maintenance_input()
            st.markdown("---")
            st.sidebar.caption(f"© {datetime.datetime.now().year} Property Health Intel. All Rights Reserved.")

        tab_options = ["📈 Property Health", "🧰 Maintenance Center", "🤝 Find Contractors", "📊 Analytics Hub"]
        
        # Default to first tab if active_tab is somehow invalid
        if st.session_state.get('active_tab') not in tab_options:
            st.session_state.active_tab = tab_options[0]

        # Create tabs. The active tab is primarily controlled by user clicks.
        # For programmatic tab switching (like from quick actions), we rely on st.rerun
        # and setting st.session_state.active_tab, then letting st.tabs pick it up if possible on next run,
        # or the user uses the toast as guidance. Direct control of st.tabs default is tricky post-render.
        
        # A way to somewhat control default tab selection using query params or more complex state
        # For now, we'll use st.tabs and let user navigate, guided by toast from quick actions if any.
        active_tab_key = st.session_state.get('active_tab', tab_options[0])

        # The actual tabs declaration; Streamlit manages their active state internally based on user clicks.
        # If `st.session_state.active_tab` is changed and a rerun happens, Streamlit does *not* automatically
        # switch the visible tab. The st.tabs widget maintains its own state.
        # The toast from quick actions serves as a guide for the user.
        
        tabs = st.tabs(tab_options)

        with tabs[0]: # Property Health
            if st.session_state.active_tab != tab_options[0]: st.session_state.active_tab = tab_options[0] # Keep state in sync if user clicks
            st.header("Property Health Dashboard")
            selected_property = self.render_property_selector("health", help_text="Select Property for Health View:")
            if selected_property:
                self.render_health_score_visualization(selected_property)
                self.render_detailed_breakdown(selected_property)
                self.render_predictions_and_recommendations(selected_property)

        with tabs[1]: # Maintenance Center
            if st.session_state.active_tab != tab_options[1]: st.session_state.active_tab = tab_options[1]
            st.header("Maintenance Center")
            selected_property_for_maint = self.render_property_selector("maintenance", allow_none=True, help_text="Select Property (or 'Select a Property...' for all):")
            self.render_maintenance_history(selected_property_for_maint.address if selected_property_for_maint else None)
        
        with tabs[2]: # Find Contractors
            if st.session_state.active_tab != tab_options[2]: st.session_state.active_tab = tab_options[2]
            st.header("Contractor Marketplace")
            self.render_contractor_marketplace()

        with tabs[3]: # Analytics Hub
            if st.session_state.active_tab != tab_options[3]: st.session_state.active_tab = tab_options[3]
            st.header("Portfolio Analytics Hub")
            self.render_comparative_health_chart()
            st.info("More analytics features (ROI calculator, Market Value Impact, etc.) coming soon!")

def main():
    # This is primarily for local testing if needed.
    # Streamlit Community Cloud will just run the script from the top.
    dashboard = Dashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
