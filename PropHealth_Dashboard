#!/usr/bin/env python3
import streamlit as st
st.set_page_config(page_title="Property Health Intelligence Platform", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")
import pandas as pd
import numpy as np
import datetime
from dataclasses import dataclass, field # Added field
from typing import List, Dict, Optional, Any # Added Optional, Any

# 🎨 Visual Enhancements & Quick Wins: For item 2 (Color-code metrics)
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
            font-size: 1rem; /* Adjusted for consistency */
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric-card p.value {
            font-size: 2.2rem; /* Made value larger */
            font-weight: 700;
            margin-bottom: 0.1rem;
            line-height: 1.2;
        }
        .metric-card small.delta {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        .bg-green-custom { background-color: #28a745; /* Bootstrap success green */ }
        .bg-yellow-custom { background-color: #ffc107; color: #212529 !important; } /* Bootstrap warning yellow, ensuring text is dark */
        .bg-yellow-custom h3 { color: #212529 !important; }
        .bg-yellow-custom p.value { color: #212529 !important; }
        .bg-yellow-custom small.delta { color: #212529 !important; opacity: 0.7;}
        .bg-red-custom { background-color: #dc3545; /* Bootstrap danger red */ }
        .bg-blue-custom { background-color: #007bff; /* Bootstrap primary blue */ }
        .bg-teal-custom { background-color: #17a2b8; /* Bootstrap info teal */ }
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
    zip_code: str = "22701" # Store zip_code with property

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
        if zip_code and zip_code[0] in self.regional_multipliers: # check if zip_code is not empty
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
        if age <= 0:
            return 100
        ratio = age / expected_life
        if ratio <= 0.5:
            return 100 - (ratio * 20) # 100 down to 90
        elif ratio <= 0.8: # from 0.5 to 0.8 (30% of life)
            return 90 - ((ratio - 0.5) / 0.3 * 30) # 90 down to 60
        else: # from 0.8 to 1.0+ (20% of life)
            return max(0, 60 - ((ratio - 0.8) / 0.2 * 60)) # 60 down to 0

    def calculate_structural_score(self, property_data: Property) -> Dict:
        current_year = datetime.datetime.now().year
        age = current_year - property_data.year_built
        foundation_scores = {'Concrete Slab': 85, 'Basement': 90, 'Crawl Space': 75, 'Pier & Beam': 70}
        roof_scores = {'Asphalt Shingles': 80, 'Metal': 90, 'Tile': 95, 'Slate': 98, 'Wood': 70}
        age_score = self.calculate_age_score(age, 80) # Overall building age
        foundation_score = foundation_scores.get(property_data.foundation_type, 75)
        roof_score = roof_scores.get(property_data.roof_material, 80) # This should ideally use roof age, not just material
        overall_score = (age_score * 0.4 + foundation_score * 0.3 + roof_score * 0.3)
        return {'score': round(overall_score, 1), 'components': {'Age Factor': round(age_score, 1), 'Foundation': foundation_score, 'Roof Material': roof_score}}

    def calculate_systems_score(self, property_data: Property) -> Dict:
        hvac_score = self.calculate_age_score(property_data.hvac_age, 15) # Avg life 15-20
        electrical_score = self.calculate_age_score(property_data.electrical_age, 40) # Avg life 30-50
        plumbing_score = self.calculate_age_score(property_data.plumbing_age, 50) # Avg life 50-70
        overall_score = (hvac_score * 0.4 + electrical_score * 0.3 + plumbing_score * 0.3)
        return {'score': round(overall_score, 1), 'components': {'HVAC': round(hvac_score, 1), 'Electrical': round(electrical_score, 1), 'Plumbing': round(plumbing_score, 1)}}

    def calculate_safety_score(self, property_data: Property) -> Dict:
        base_score = 85 # Assume generally safe if systems are okay
        current_year = datetime.datetime.now().year
        age = current_year - property_data.year_built
        if age > 30: base_score -= 10
        if age > 50: base_score -= 10 # Cumulative, so -20 for 50+
        # Could be enhanced with last inspection date, smoke detector age etc.
        return {'score': round(base_score, 1), 'components': {'General Safety': base_score}}


    def calculate_environmental_score(self, property_data: Property) -> Dict:
        # Placeholder - could be enhanced with location-specific risks (flood zone, etc.)
        base_score = 80
        # Example: if property_type is "Single Family" with good yard, better air quality potential
        # This needs more inputs to be meaningful.
        return {'score': round(base_score, 1), 'components': {'General Environmental': base_score}}

    def calculate_overall_score(self, property_data: Property) -> Dict:
        structural = self.calculate_structural_score(property_data)
        systems = self.calculate_systems_score(property_data)
        safety = self.calculate_safety_score(property_data)
        environmental = self.calculate_environmental_score(property_data) # Pass property_data
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

        # HVAC
        if property_data.hvac_age <= 1: # Newer systems might just need filter changes
             cost_est = self.get_local_cost_estimate("hvac_service", zip_code)
             schedule.append({"task": "HVAC Filter Check/Replacement", "frequency": "Every 3 months", "next_due": current_date + datetime.timedelta(days=90), "priority": "routine", "estimated_cost": cost_est["min"] // 4 , "description": "Check and replace air filters as needed."})
        elif property_data.hvac_age <= 12: # Mature systems
            cost_est = self.get_local_cost_estimate("hvac_service", zip_code)
            schedule.append({"task": "HVAC Annual Service", "frequency": "Annually", "next_due": current_date + datetime.timedelta(days=365), "priority": "important", "estimated_cost": cost_est["avg"], "description": "Professional tune-up and inspection."})
        else: # Older systems
            cost_est_repl = self.get_local_cost_estimate("hvac_replacement", zip_code)
            schedule.append({"task": "HVAC Replacement Planning", "frequency": "Within 1-2 years", "next_due": current_date + datetime.timedelta(days=365), "priority": "high", "estimated_cost": cost_est_repl["avg"], "description": "Budget and plan for HVAC system replacement."})

        # Electrical
        if property_data.electrical_age > 30:
            cost_est = self.get_local_cost_estimate("electrical_panel", zip_code)
            schedule.append({"task": "Electrical System Inspection", "frequency": "Consider within 1 year", "next_due": current_date + datetime.timedelta(days=365), "priority": "important", "estimated_cost": cost_est["avg"] // 5, "description": "Inspect aging electrical panel and system."})
        if property_data.electrical_age > 40: # GFI, breaker checks
             schedule.append({"task": "Consider Electrical Panel Upgrade", "frequency": "Within 2-3 years", "next_due": current_date + datetime.timedelta(days=730), "priority": "high", "estimated_cost": self.get_local_cost_estimate("electrical_panel", zip_code)["avg"], "description": "Plan for upgrading an old electrical panel."})


        # Plumbing
        if property_data.plumbing_age > 40: # Water heater, pipe checks
            cost_est_wh = self.get_local_cost_estimate("water_heater", zip_code)
            schedule.append({"task": "Water Heater Check/Replacement Plan", "frequency": "Within 1-3 years", "next_due": current_date + datetime.timedelta(days=540), "priority": "important", "estimated_cost": cost_est_wh["avg"], "description": "Inspect water heater, plan for replacement if old."})
        if property_data.plumbing_age > 50:
             cost_est_repair = self.get_local_cost_estimate("plumbing_repair", zip_code)
             schedule.append({"task": "Major Plumbing Inspection", "frequency": "Within 2 years", "next_due": current_date + datetime.timedelta(days=730), "priority": "high", "estimated_cost": cost_est_repair["avg"], "description": "Inspect for potential major plumbing updates."})


        # Roof (assuming asphalt shingles ~20-25 year life) - This needs roof age, not just material.
        # For now, using general property age as a proxy, which is not ideal.
        if property_data.year_built < (current_date.year - 15) and property_data.roof_material == "Asphalt Shingles":
            cost_est = self.get_local_cost_estimate("roof_repair", zip_code)
            schedule.append({"task": "Roof Inspection & Minor Repairs", "frequency": "Annually", "next_due": current_date + datetime.timedelta(days=365), "priority": "important", "estimated_cost": cost_est["avg"], "description": "Inspect roof for wear, potential leaks, and clear debris."})

        # Seasonal
        cost_est_gutter = self.get_local_cost_estimate("gutter_replacement", zip_code) # Using this for cleaning cost basis
        schedule.append({"task": "Gutter Cleaning (Spring)", "frequency": "Annually (Spring)", "next_due": current_date + datetime.timedelta(days=120), "priority": "routine", "estimated_cost": max(150, cost_est_gutter["min"] // 10) , "description": "Clean gutters and downspouts after winter."})
        schedule.append({"task": "Gutter Cleaning (Fall)", "frequency": "Annually (Fall)", "next_due": current_date + datetime.timedelta(days=300), "priority": "routine", "estimated_cost": max(150, cost_est_gutter["min"] // 10), "description": "Clean gutters and downspouts before winter."})
        schedule.append({"task": "Exterior Caulking & Sealing Check", "frequency": "Annually", "next_due": current_date + datetime.timedelta(days=270), "priority": "routine", "estimated_cost": 100, "description": "Check windows, doors, and siding for gaps."})


        schedule.sort(key=lambda x: ({"high": 0, "important": 1, "routine": 2}[x["priority"]], x["next_due"]))
        return schedule


class AuthenticationManager:
    def __init__(self):
        # IMPORTANT: In a real application, use a secure way to store and check passwords.
        # Consider environment variables or a secrets management service.
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
            confidential_understood = st.checkbox("Acknowledge Confidentiality", key="conf_checkbox", value=st.session_state.get('conf_checkbox', False))
            respect_ip = st.checkbox("Respect Intellectual Property", key="ip_checkbox", value=st.session_state.get('ip_checkbox', False))
        with col2:
            professional_courtesy = st.checkbox("Agree to Professional Standards", key="courtesy_checkbox", value=st.session_state.get('courtesy_checkbox', False))
            authorized_access = st.checkbox("Authorized Stakeholder", key="auth_checkbox", value=st.session_state.get('auth_checkbox', False))

        st.markdown("#### Digital Signature")
        full_name = st.text_input("Full Name *", placeholder="Enter your full name", value=st.session_state.get('full_name', ''))
        email_address = st.text_input("Email Address *", placeholder="your.email@company.com", value=st.session_state.get('email_address', ''))
        company_org = st.text_input("Company/Organization", placeholder="Your company", value=st.session_state.get('company_org', ''))
        access_purpose = st.selectbox("Purpose of Access *", ["", "Potential Investor", "Business Partner", "Industry Professional", "Internal Review", "Other"], index=0, key="purpose_select")


        st.markdown("#### Access Code")
        password_input = st.text_input("Enter access code:", type="password", placeholder="Access code required")

        all_acknowledged = confidential_understood and respect_ip and professional_courtesy and authorized_access
        password_correct = password_input == self.password
        signature_complete = full_name.strip() != "" and email_address.strip() != "" and access_purpose != ""
        email_valid = "@" in email_address and "." in email_address.split('@')[-1] if email_address else False # Basic check

        # Store input values in session state to persist them on interactions
        st.session_state.conf_checkbox = confidential_understood
        st.session_state.ip_checkbox = respect_ip
        st.session_state.courtesy_checkbox = professional_courtesy
        st.session_state.auth_checkbox = authorized_access
        st.session_state.full_name = full_name
        st.session_state.email_address = email_address
        st.session_state.company_org = company_org
        # st.session_state.access_purpose = access_purpose # already handled by selectbox key

        access_button_disabled = not (all_acknowledged and signature_complete and email_valid and password_input) # Check if password_input is not empty

        if st.button("🚀 ACCESS PREVIEW", type="primary", disabled=access_button_disabled):
            if password_correct:
                st.session_state.access_info = {'name': full_name, 'email': email_address, 'company': company_org, 'purpose': access_purpose, 'timestamp': datetime.datetime.now()}
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
                for key in list(st.session_state.keys()):
                    if key not in ['properties', 'maintenance_records']: # Persist core data if desired, or clear all
                        del st.session_state[key]
                st.session_state.authenticated = False
                st.success("Logged out successfully.")
                st.rerun()

class Dashboard:
    def __init__(self):
        self.calculator = PropertyHealthCalculator()
        self.auth_manager = AuthenticationManager()
        self.init_session_state()
        render_custom_metric_card_style() # Quick Win 2: Inject CSS for cards

    def init_session_state(self):
        if 'properties' not in st.session_state:
            st.session_state.properties = [] # List[Property]
        if 'maintenance_records' not in st.session_state:
            st.session_state.maintenance_records = [] # List[MaintenanceRecord]
        # Removed property_zip_codes as it's now part of Property dataclass

        # For Quick Action 3: managing expander state
        if 'show_add_property_form' not in st.session_state:
            st.session_state.show_add_property_form = True # Default to open
        if 'show_add_maintenance_form' not in st.session_state:
            st.session_state.show_add_maintenance_form = False


    def render_header(self):
        st.title("🏠 Property Health Intelligence Dashboard")
        st.markdown("Your partner in proactive property care. *Beta Preview v0.3*")
        st.markdown("---")

        # Quick Win 2 & 4: Color-coded metrics & Cost Savings Tracker
        cols = st.columns([1,1,1,1,1]) # Now 5 columns for the new metric

        # 1. Total Properties
        total_props = len(st.session_state.properties)
        with cols[0]:
            st.markdown(f"""
                <div class="metric-card bg-blue-custom">
                    <h3>Total Properties</h3>
                    <p class="value">{total_props}</p>
                    <small class="delta">Currently Managed</small>
                </div>
            """, unsafe_allow_html=True)

        # 2. Average Health Score
        avg_score_val = 0
        avg_score_str = "N/A"
        avg_score_color = "bg-blue-custom" # Default
        if st.session_state.properties:
            avg_score_val = np.mean([self.calculator.calculate_overall_score(prop)['overall_score'] for prop in st.session_state.properties])
            avg_score_str = f"{avg_score_val:.1f}"
            if avg_score_val >= 85: avg_score_color = "bg-green-custom"
            elif avg_score_val >= 70: avg_score_color = "bg-yellow-custom"
            else: avg_score_color = "bg-red-custom"
        with cols[1]:
            st.markdown(f"""
                <div class="metric-card {avg_score_color}">
                    <h3>Average Health</h3>
                    <p class="value">{avg_score_str}</p>
                    <small class="delta">Overall Portfolio Score</small>
                </div>
            """, unsafe_allow_html=True)

        # 3. Urgent Items
        urgent_items_count = len([r for r in st.session_state.maintenance_records if r.urgency == "High"])
        urgent_color = "bg-green-custom"
        if urgent_items_count > 0: urgent_color = "bg-yellow-custom"
        if urgent_items_count >= 3: urgent_color = "bg-red-custom"
        with cols[2]:
            st.markdown(f"""
                <div class="metric-card {urgent_color}">
                    <h3>Urgent Items</h3>
                    <p class="value">{urgent_items_count}</p>
                    <small class="delta">Requiring Immediate Attention</small>
                </div>
            """, unsafe_allow_html=True)

        # 4. Total Maintenance Cost (YTD or Overall)
        total_cost = sum([r.cost for r in st.session_state.maintenance_records])
        with cols[3]:
            st.markdown(f"""
                <div class="metric-card bg-teal-custom">
                    <h3>Total Maint. Cost</h3>
                    <p class="value">${total_cost:,.0f}</p>
                    <small class="delta">Logged Expenditures</small>
                </div>
            """, unsafe_allow_html=True)

        # 5. Quick Win 4: Estimated Cost Savings Tracker
        # Simple estimation: 15% of non-urgent maintenance costs are "savings" from preventing bigger issues.
        preventative_maintenance_cost = sum(r.cost for r in st.session_state.maintenance_records if r.urgency in ["Low", "Medium"])
        estimated_savings = preventative_maintenance_cost * 0.15 # 15% factor
        with cols[4]:
            st.markdown(f"""
                <div class="metric-card bg-green-custom">
                    <h3>Est. Savings</h3>
                    <p class="value">${estimated_savings:,.0f}</p>
                    <small class="delta">From Proactive Care (Est.)</small>
                </div>
            """, unsafe_allow_html=True)


    def render_quick_actions(self): # Quick Win 3: Quick Actions Panel
        st.sidebar.subheader("⚡ Quick Actions")
        if st.sidebar.button("➕ Add New Property", use_container_width=True):
            st.session_state.show_add_property_form = not st.session_state.get('show_add_property_form', False)
            st.session_state.show_add_maintenance_form = False # Close other form
            st.rerun() # To reflect expander change

        if st.session_state.properties and st.sidebar.button("📝 Log Maintenance Task", use_container_width=True):
            st.session_state.show_add_maintenance_form = not st.session_state.get('show_add_maintenance_form', False)
            st.session_state.show_add_property_form = False # Close other form
            st.rerun() # To reflect expander change
        elif not st.session_state.properties and st.sidebar.button("📝 Log Maintenance Task", use_container_width=True, disabled=True):
            pass # Button is disabled if no properties

        if st.session_state.maintenance_records and st.sidebar.button("❗ View Urgent Tasks", use_container_width=True):
            # This could navigate to the maintenance tab and apply a filter
            # For now, a toast and user navigates.
            st.session_state.active_tab = "Maintenance" # Assuming we can set active tab
            st.session_state.maintenance_filter_urgency = "High"
            st.toast("Switched to Maintenance tab with 'High' urgency filter.")
            st.rerun()


    def render_property_management(self):
        st.sidebar.header("🏡 Property Portfolio")
        # Quick Win 3: Control expander with session state
        expanded_add_prop = st.session_state.get('show_add_property_form', True)
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
                last_inspection_date = st.date_input("Last Major Inspection Date", value=None)
                last_inspection = last_inspection_date.strftime("%Y-%m-%d") if last_inspection_date else "N/A"

                # Quick Win 1: Add property photos
                uploaded_photo = st.file_uploader("Upload Property Photo (Optional)", type=["png", "jpg", "jpeg"])

                submitted = st.form_submit_button("✅ Add Property to Portfolio", type="primary", use_container_width=True)

                if submitted:
                    if not address or not zip_code:
                        st.error("🚨 Address and ZIP Code are required!")
                    else:
                        image_bytes = uploaded_photo.getvalue() if uploaded_photo else None
                        new_property = Property(address, year_built, square_footage, property_type,
                                                roof_material, foundation_type, hvac_age, electrical_age,
                                                plumbing_age, last_inspection, image_bytes, zip_code)
                        st.session_state.properties.append(new_property)
                        st.session_state.show_add_property_form = False # Collapse form after adding
                        st.success(f"✅ Property '{address}' added successfully!")
                        st.rerun()

        if st.session_state.properties:
            with st.sidebar.expander("🗑️ Manage Properties"):
                # Simplified delete for now
                prop_options = {f"{i+1}. {prop.address} ({prop.zip_code})": i for i, prop in enumerate(st.session_state.properties)}
                selected_prop_label_to_delete = st.selectbox("Select property to remove:", list(prop_options.keys()), index=None, placeholder="Choose property...")
                
                if selected_prop_label_to_delete and st.button("🗑️ Delete Selected Property", type="secondary", use_container_width=True):
                    idx_to_delete = prop_options[selected_prop_label_to_delete]
                    deleted_property_address = st.session_state.properties[idx_to_delete].address
                    
                    # Also remove associated maintenance records
                    st.session_state.maintenance_records = [
                        record for record in st.session_state.maintenance_records
                        if record.property_address != deleted_property_address
                    ]
                    del st.session_state.properties[idx_to_delete]
                    st.success(f"🗑️ Property '{deleted_property_address}' and its maintenance records removed.")
                    st.rerun()


    def render_maintenance_input(self):
        if not st.session_state.properties:
            st.sidebar.info("Add a property first to log maintenance.")
            return

        st.sidebar.header("🛠️ Maintenance Log")
        expanded_add_maint = st.session_state.get('show_add_maintenance_form', False)
        with st.sidebar.expander("➕ Add New Maintenance Record", expanded=expanded_add_maint):
            property_addresses = [prop.address for prop in st.session_state.properties]
            if not property_addresses: return # Should not happen if properties exist

            with st.form("maintenance_form", clear_on_submit=True):
                selected_address = st.selectbox("Select Property *", property_addresses, index=0 if property_addresses else None)
                date = st.date_input("Date of Service/Record *", datetime.date.today())
                category = st.selectbox("Category *", ["HVAC", "Plumbing", "Electrical", "Roofing", "Foundation", "Appliances", "Pest Control", "Landscaping", "General Repair", "Inspection"])
                description = st.text_area("Description of Work / Issue *", height=100)
                cost = st.number_input("Cost ($)", min_value=0.0, value=0.0, step=10.0, format="%.2f")
                contractor = st.text_input("Contractor/Vendor (if any)")
                urgency = st.selectbox("Urgency *", ["Routine", "Medium", "High"]) # Changed Low to Routine

                submitted = st.form_submit_button("➕ Add Maintenance Record", type="primary", use_container_width=True)

                if submitted:
                    if not selected_address or not description or not date or not category or not urgency:
                        st.error("🚨 Please fill in all required fields for the maintenance record.")
                    else:
                        new_record = MaintenanceRecord(date.strftime("%Y-%m-%d"), category, description, cost, contractor, urgency, selected_address)
                        st.session_state.maintenance_records.append(new_record)
                        st.session_state.show_add_maintenance_form = False # Collapse form
                        st.success(f"✅ Maintenance record added for '{selected_address}'.")
                        st.rerun()


    def render_property_selector(self, key_suffix="main", allow_none=False):
        if not st.session_state.properties:
            st.info("👈 Add a property via the sidebar to get started!")
            return None

        addresses = ["Select a Property..."] + [prop.address for prop in st.session_state.properties] if allow_none else [prop.address for prop in st.session_state.properties]
        
        # Persist selection across reruns for the current tab/view
        session_key = f"selected_property_address_{key_suffix}"
        current_selection_idx = 0 # Default to first property if not 'Select...'
        
        if allow_none and st.session_state.get(session_key) is None:
             current_selection_idx = 0 # Index of "Select a Property..."
        elif st.session_state.get(session_key) in addresses:
            current_selection_idx = addresses.index(st.session_state.get(session_key))
        elif addresses and not allow_none: # Ensure it defaults to the first actual property
             st.session_state[session_key] = addresses[0]
             current_selection_idx = 0


        selected_address = st.selectbox("Select Property to View Details:", addresses, index=current_selection_idx, key=f"prop_select_box_{key_suffix}")
        
        if selected_address == "Select a Property..." and allow_none:
            st.session_state[session_key] = None
            return None
        
        st.session_state[session_key] = selected_address # Store the selection
        
        # Find the actual property object
        for prop in st.session_state.properties:
            if prop.address == selected_address:
                return prop
        return None # Should not be reached if addresses list is correct


    def render_health_score_visualization(self, property_data: Property):
        scores = self.calculator.calculate_overall_score(property_data)
        
        st.subheader(f"📊 Health Snapshot: {property_data.address}")
        
        cols = st.columns([0.4, 0.6]) # Image column, Score column
        
        with cols[0]: # Quick Win 1: Display property photo
            if property_data.image_data:
                st.image(property_data.image_data, caption=f"{property_data.property_type} at {property_data.address}", use_column_width=True)
            else:
                st.markdown("<div style='height: 200px; background-color: #f0f2f6; display: flex; align-items: center; justify-content: center; border-radius: 8px;'><span style='color: #aaa; font-style: italic;'>No property image</span></div>", unsafe_allow_html=True)

        with cols[1]:
            overall_score_val = scores['overall_score']
            st.metric("Overall Health Score", f"{overall_score_val:.1f} / 100")

            if overall_score_val >= 85: st.success("Excellent Condition! Keep up the great work. 👍")
            elif overall_score_val >= 70: st.info("Good Condition. Minor attention may be needed. 👌")
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
            with st.expander(f"{category} Details - Overall Score: {data['score']:.1f}", expanded=category=="Structural"): # Expand structural by default
                if not data['components']:
                    st.write(f"No specific components listed for {category}.")
                    continue
                
                comp_cols = st.columns(len(data['components']))
                idx = 0
                for component, score_val in data['components'].items():
                    with comp_cols[idx]:
                        # Normalize score_val if it's a dict (like from old safety score)
                        c_score = score_val
                        if isinstance(score_val, dict) and 'score' in score_val: c_score = score_val['score']
                        elif isinstance(score_val, dict): c_score = 70 # Default for unexpected dict

                        color = "green" if float(c_score) >= 80 else "orange" if float(c_score) >= 60 else "red"
                        # Use st.markdown for better control, or just simple text
                        st.markdown(f"**{component}:**")
                        st.markdown(f"<p style='font-size: 1.5em; color:{color}; font-weight:bold;'>{float(c_score):.1f}</p>", unsafe_allow_html=True)
                    idx+=1
                
                # Provide some context or advice based on component scores if possible
                if category == "Systems":
                    if data['components']['HVAC'] < 60 : st.caption("Consider HVAC inspection/service soon.")
                    if data['components']['Electrical'] < 50 : st.caption("🚨 Electrical system age/score is low. Recommend professional assessment.")
                # Add more insights here...
        st.markdown("---")

    def render_maintenance_history(self, property_address: str): # Pass address to filter
        st.subheader(f"🧰 Maintenance History for {property_address}")
        
        # Filter records for the selected property
        property_records = [r for r in st.session_state.maintenance_records if r.property_address == property_address]

        if not property_records:
            st.info("No maintenance records found for this property yet. Add some via the sidebar!")
            return

        # Allow filtering by urgency - for Quick Action "View Urgent Tasks"
        urgency_filter_options = ["All"] + sorted(list(set(r.urgency for r in property_records)))
        default_urgency_filter = "All"
        if st.session_state.get("maintenance_filter_urgency") in urgency_filter_options:
            default_urgency_filter = st.session_state.pop("maintenance_filter_urgency") # Use and clear

        selected_urgency = st.selectbox("Filter by Urgency:", urgency_filter_options, 
                                        index=urgency_filter_options.index(default_urgency_filter), 
                                        key=f"maint_urgency_filter_{property_address}")

        if selected_urgency != "All":
            property_records = [r for r in property_records if r.urgency == selected_urgency]


        records_df_data = [{'Date': r.date, 'Category': r.category, 'Description': r.description,
                             'Cost ($)': r.cost, 'Contractor': r.contractor, 'Urgency': r.urgency}
                           for r in property_records]
        records_df = pd.DataFrame(records_df_data)
        
        # Sort by Date (descending) then Urgency (High first)
        urgency_map = {"High":0, "Medium":1, "Routine":2}
        records_df['urgency_sort'] = records_df['Urgency'].map(urgency_map)
        records_df_sorted = records_df.sort_values(by=['Date', 'urgency_sort'], ascending=[False, True]).drop(columns=['urgency_sort'])
        
        st.dataframe(records_df_sorted, use_container_width=True, height=300,
                     column_config={
                         "Cost ($)": st.column_config.NumberColumn(format="$%.2f"),
                         "Description": st.column_config.TextColumn(width="large")
                     })
        
        total_cost_filtered = sum(r.cost for r in property_records) # Sum of currently filtered records
        st.markdown(f"**Total Cost (Filtered):** ${total_cost_filtered:,.2f}")
        st.markdown("---")


    def render_predictions_and_recommendations(self, property_data: Property):
        st.subheader("💡 Predictions & Proactive Recommendations")
        schedule = self.calculator.generate_maintenance_schedule(property_data) # Zip is in property_data

        tab1, tab2 = st.tabs(["🔮 Upcoming Maintenance Tasks", "💰 Cost Planning Tool"])

        with tab1:
            st.markdown("**Key Upcoming Maintenance:** (Sorted by Priority & Due Date)")
            if not schedule:
                st.info("✅ No specific system-triggered recommendations at this time. General upkeep is always good!")
            else:
                for task in schedule[:7]: # Show top 7
                    priority_icon = {"high": "🔴", "important": "🟡", "routine": "🔵"}[task["priority"]]
                    days_until = (task["next_due"] - datetime.datetime.now()).days
                    due_date_str = task["next_due"].strftime("%b %d, %Y")

                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3,1,1])
                        with col1:
                            st.markdown(f"{priority_icon} **{task['task']}** ({task['frequency']})")
                            st.caption(f"{task['description']}")
                        with col2:
                            st.metric(label="Est. Cost", value=f"${task['estimated_cost']:,}", delta=None, label_visibility="collapsed")
                        with col3:
                            if days_until <= 0:
                                st.error(f"Due: {due_date_str} (Overdue!)")
                            elif days_until <= 30:
                                st.warning(f"Due: {due_date_str} ({days_until} days)")
                            else:
                                st.info(f"Due: {due_date_str} ({days_until} days)")
        with tab2:
            st.markdown("**Regional Cost Estimator**")
            st.caption(f"Estimates based on ZIP: {property_data.zip_code} (Region: {self.calculator.get_regional_info(property_data.zip_code)['region']})")
            
            cost_item_types = list(self.calculator.national_cost_baseline.keys())
            selected_item = st.selectbox("Select Item for Cost Estimate:", cost_item_types, index =0)
            
            if selected_item:
                estimates = self.calculator.get_local_cost_estimate(selected_item, property_data.zip_code)
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Est. Min Cost", f"${estimates['min']:,}")
                col_b.metric("Est. Avg Cost", f"${estimates['avg']:,}")
                col_c.metric("Est. Max Cost", f"${estimates['max']:,}")
                st.caption(f"National Avg: ${estimates['national_avg']:,}. Confidence: {estimates['confidence'].title()}.")
        st.markdown("---")

    def render_comparative_health_chart(self): # Quick Win 5
        if len(st.session_state.properties) > 1:
            st.subheader("📊 Comparative Property Health Scores")
            
            prop_scores = []
            for p in st.session_state.properties:
                score_data = self.calculator.calculate_overall_score(p)
                prop_scores.append({
                    "Property Address": p.address,
                    "Overall Health Score": score_data['overall_score'],
                    "Structural": score_data['category_scores']['Structural']['score'],
                    "Systems": score_data['category_scores']['Systems']['score'],
                    "Safety": score_data['category_scores']['Safety']['score'],
                })
            
            df = pd.DataFrame(prop_scores)
            
            # Allow user to select which scores to compare
            score_types_to_plot = st.multiselect(
                "Select scores to compare:",
                options=["Overall Health Score", "Structural", "Systems", "Safety"],
                default=["Overall Health Score"]
            )

            if score_types_to_plot:
                # Prepare DataFrame for st.bar_chart (expects index as category labels)
                chart_df = df.set_index("Property Address")[score_types_to_plot]
                st.bar_chart(chart_df, height=400)
            else:
                st.info("Select at least one score type to display the chart.")

        elif st.session_state.properties:
            st.info("Add at least two properties to see a comparative health chart.")
        st.markdown("---")


    def render_contractor_marketplace(self): # Placeholder
        st.subheader("🛠️ Find Certified Professionals (Marketplace - Demo)")
        st.info("This section is a placeholder for a future contractor marketplace integration.")
        contractors = [
            {'name': 'Valley HVAC Experts', 'category': 'HVAC', 'rating': 4.9, 'reviews': 312, 'zip_coverage': ['22701', '22801'], 'contact_info': 'Call (555) 123-4567'},
            {'name': 'Old Dominion Plumbing Pros', 'category': 'Plumbing', 'rating': 4.7, 'reviews': 189, 'zip_coverage': ['22701', '22102', '20109'], 'contact_info': 'info@odplumbing.com'},
            {'name': 'Capital Electrical Solutions', 'category': 'Electrical', 'rating': 4.8, 'reviews': 250, 'zip_coverage': ['22102', '20001'], 'contact_info': 'Schedule online!'},
            {'name': 'RoofGuard Inc.', 'category': 'Roofing', 'rating': 4.6, 'reviews': 150, 'zip_coverage': ['22701', '90210'], 'contact_info': 'Free estimates!'}
        ]

        current_prop_zip = None
        if st.session_state.get(f"selected_property_address_contractors"):
            selected_prop_address = st.session_state[f"selected_property_address_contractors"]
            prop = next((p for p in st.session_state.properties if p.address == selected_prop_address), None)
            if prop:
                current_prop_zip = prop.zip_code
        
        if current_prop_zip:
            st.write(f"Showing contractors potentially serving ZIP: **{current_prop_zip}**")
            filtered_contractors = [c for c in contractors if current_prop_zip in c['zip_coverage'] or current_prop_zip[0] in [z[0] for z in c['zip_coverage']]]
        else:
            st.write("Select a property to see relevant contractors or showing general list.")
            filtered_contractors = contractors
        
        if not filtered_contractors:
            st.warning(f"No contractors found directly matching ZIP {current_prop_zip}. Showing general list.")
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
                    if st.button(f"Contact {contractor['name'].split(' ')[0]}", key=f"contact_{contractor['name']}"):
                        st.success(f"Contact info for {contractor['name']}: {contractor['contact_info']}")
                        # In a real app, this would open a modal or lead to a contact form.


    def run(self):
        if not self.auth_manager.is_authenticated():
            self.auth_manager.render_auth_screen()
            return

        # --- Main App Layout ---
        self.render_header() # Includes Quick Win 2 (Color Cards) & 4 (Savings Tracker)

        # Sidebar components
        with st.sidebar:
            self.auth_manager.render_session_info() # Session info first
            self.render_quick_actions() # Quick Win 3
            st.markdown("---")
            self.render_property_management() # Includes Quick Win 1 (Photo Upload)
            st.markdown("---")
            self.render_maintenance_input()
            st.markdown("---")
            st.sidebar.caption(f"© {datetime.datetime.now().year} Property Health Intel. All Rights Reserved.")


        # Main content tabs
        tab_options = ["📈 Property Health", "🧰 Maintenance Center", "🤝 Find Contractors", "📊 Analytics Hub"]
        # Manage active tab state for Quick Actions
        if 'active_tab' not in st.session_state:
            st.session_state.active_tab = tab_options[0]
        
        # Handle query param for tab switching if needed later
        # query_params = st.query_params
        # if "tab" in query_params and query_params["tab"] in tab_options:
        # st.session_state.active_tab = query_params["tab"]


        # Create actual tabs, setting the default based on session_state
        # Streamlit tabs don't have a direct way to set active tab programmatically after creation in the same run.
        # The rerun approach from quick actions is the most straightforward.
        active_tab_idx = tab_options.index(st.session_state.active_tab) if st.session_state.active_tab in tab_options else 0
        
        # We cannot directly set the active tab dynamically.
        # A workaround would be to use st.radio to simulate tabs or conditional rendering.
        # For simplicity with st.tabs, the user will be guided by the toast from quick actions.
        
        tab1, tab2, tab3, tab4 = st.tabs(tab_options)

        with tab1: # Property Health
            st.header("Property Health Dashboard")
            selected_property_health = self.render_property_selector("health")
            if selected_property_health:
                self.render_health_score_visualization(selected_property_health) # Includes Quick Win 1 (Photo Display)
                self.render_detailed_breakdown(selected_property_health)
                self.render_predictions_and_recommendations(selected_property_health)

        with tab2: # Maintenance Center
            st.header("Maintenance Center")
            selected_property_maint = self.render_property_selector("maintenance", allow_none=True) # Allow no selection to see all
            if selected_property_maint:
                self.render_maintenance_history(selected_property_maint.address)
            else:
                # Show all records if no property is selected (or a summary)
                st.info("Select a property above to view its specific maintenance history, or add records via the sidebar.")
                if st.session_state.maintenance_records:
                    st.subheader("All Maintenance Records (Portfolio Wide)")
                    all_records_df = pd.DataFrame([r.__dict__ for r in st.session_state.maintenance_records])
                    urgency_map = {"High":0, "Medium":1, "Routine":2}
                    all_records_df['urgency_sort'] = all_records_df['urgency'].map(urgency_map)
                    all_records_df_sorted = all_records_df.sort_values(by=['date', 'urgency_sort'], ascending=[False, True]).drop(columns=['urgency_sort'])

                    st.dataframe(all_records_df_sorted[['date', 'property_address', 'category', 'description', 'cost', 'urgency']],
                                 use_container_width=True, height=400,
                                 column_config={ "cost": st.column_config.NumberColumn(format="$%.2f")})
                else:
                    st.write("No maintenance records in the system yet.")


        with tab3: # Find Contractors
            st.header("Contractor Marketplace")
            # We need a property selector here too if contractors are zip specific
            selected_property_contractors = self.render_property_selector("contractors", allow_none=True)
            self.render_contractor_marketplace() # Placeholder content

        with tab4: # Analytics Hub
            st.header("Portfolio Analytics Hub")
            self.render_comparative_health_chart() # Quick Win 5
            # Future: ROI calculator, Market Value Impact, etc.
            st.info("More analytics features coming soon!")


def main():
    dashboard = Dashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
