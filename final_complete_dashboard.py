#!/usr/bin/env python3
import streamlit as st
st.set_page_config(page_title="Property Health Intelligence Platform", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")
import pandas as pd
import numpy as np
import datetime
from dataclasses import dataclass
from typing import List, Dict

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

@dataclass
class MaintenanceRecord:
    date: str
    category: str
    description: str
    cost: float
    contractor: str
    urgency: str

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
        if zip_code[0] in self.regional_multipliers:
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
            return 100 - (ratio * 20)
        elif ratio <= 0.8:
            return 90 - ((ratio - 0.5) * 100)
        else:
            return max(0, 60 - ((ratio - 0.8) * 150))

    def calculate_structural_score(self, property_data: Property) -> Dict:
        age = 2024 - property_data.year_built
        foundation_scores = {'Concrete Slab': 85, 'Basement': 90, 'Crawl Space': 75, 'Pier & Beam': 70}
        roof_scores = {'Asphalt Shingles': 80, 'Metal': 90, 'Tile': 95, 'Slate': 98, 'Wood': 70}
        age_score = self.calculate_age_score(age, 80)
        foundation_score = foundation_scores.get(property_data.foundation_type, 75)
        roof_score = roof_scores.get(property_data.roof_material, 80)
        overall_score = (age_score * 0.4 + foundation_score * 0.3 + roof_score * 0.3)
        return {'score': round(overall_score, 1), 'components': {'Age Factor': round(age_score, 1), 'Foundation': foundation_score, 'Roof': roof_score}}

    def calculate_systems_score(self, property_data: Property) -> Dict:
        hvac_score = self.calculate_age_score(property_data.hvac_age, 15)
        electrical_score = self.calculate_age_score(property_data.electrical_age, 40)
        plumbing_score = self.calculate_age_score(property_data.plumbing_age, 50)
        overall_score = (hvac_score * 0.4 + electrical_score * 0.3 + plumbing_score * 0.3)
        return {'score': round(overall_score, 1), 'components': {'HVAC': round(hvac_score, 1), 'Electrical': round(electrical_score, 1), 'Plumbing': round(plumbing_score, 1)}}

    def calculate_safety_score(self, property_data: Property) -> Dict:
        base_score = 85
        age = 2024 - property_data.year_built
        if age > 30:
            base_score -= 10
        if age > 50:
            base_score -= 10
        return {'score': round(base_score, 1), 'components': {'Code Compliance': base_score, 'Safety Systems': base_score, 'Accessibility': base_score - 5}}

    def calculate_environmental_score(self) -> Dict:
        base_score = 80
        return {'score': round(base_score, 1), 'components': {'Weather Exposure': base_score, 'Natural Disasters': base_score + 5, 'Air Quality': base_score - 5}}

    def calculate_overall_score(self, property_data: Property) -> Dict:
        structural = self.calculate_structural_score(property_data)
        systems = self.calculate_systems_score(property_data)
        safety = self.calculate_safety_score(property_data)
        environmental = self.calculate_environmental_score()
        overall = (structural['score'] * self.weights['structural'] + systems['score'] * self.weights['systems'] + safety['score'] * self.weights['safety'] + environmental['score'] * self.weights['environmental'])
        return {'overall_score': round(overall, 1), 'category_scores': {'Structural': structural, 'Systems': systems, 'Safety': safety, 'Environmental': environmental}}

    def generate_maintenance_schedule(self, property_data: Property, zip_code: str = "22701") -> List[Dict]:
        schedule = []
        current_date = datetime.datetime.now()
        
        # HVAC
        if property_data.hvac_age <= 5:
            cost_est = self.get_local_cost_estimate("hvac_service", zip_code)
            schedule.append({"task": "HVAC Filter Replacement", "frequency": "Every 3 months", "next_due": current_date + datetime.timedelta(days=90), "priority": "routine", "estimated_cost": cost_est["min"] // 3, "description": "Replace air filters"})
        elif property_data.hvac_age <= 10:
            cost_est = self.get_local_cost_estimate("hvac_service", zip_code)
            schedule.append({"task": "HVAC Annual Service", "frequency": "Annually", "next_due": current_date + datetime.timedelta(days=365), "priority": "important", "estimated_cost": cost_est["avg"], "description": "Professional tune-up"})
        else:
            cost_est = self.get_local_cost_estimate("hvac_replacement", zip_code)
            schedule.append({"task": "HVAC Replacement Planning", "frequency": "Within 2-3 years", "next_due": current_date + datetime.timedelta(days=540), "priority": "high", "estimated_cost": cost_est["avg"], "description": "Plan for system replacement"})
        
        # Electrical
        if property_data.electrical_age > 30:
            cost_est = self.get_local_cost_estimate("electrical_panel", zip_code)
            schedule.append({"task": "Electrical Panel Upgrade", "frequency": "One-time (urgent)", "next_due": current_date + datetime.timedelta(days=180), "priority": "high", "estimated_cost": cost_est["avg"], "description": "Upgrade aging electrical panel"})
        
        # Plumbing
        if property_data.plumbing_age > 40:
            cost_est = self.get_local_cost_estimate("plumbing_repair", zip_code)
            schedule.append({"task": "Plumbing System Overhaul", "frequency": "One-time", "next_due": current_date + datetime.timedelta(days=720), "priority": "high", "estimated_cost": cost_est["max"] * 3, "description": "Major plumbing updates"})
        
        # Seasonal
        schedule.append({"task": "Gutter Cleaning", "frequency": "Twice yearly", "next_due": current_date + datetime.timedelta(days=180), "priority": "routine", "estimated_cost": 150, "description": "Clean gutters and inspect"})
        
        schedule.sort(key=lambda x: ({"high": 1, "important": 2, "routine": 3}[x["priority"]], x["next_due"]))
        return schedule

class AuthenticationManager:
    def __init__(self):
        self.password = "PropHealth2025!"

    def render_auth_screen(self):
        st.markdown("""<style>.auth-container {max-width: 800px; margin: 0 auto; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; box-shadow: 0 10px 30px rgba(0,0,0,0.2);}</style>""", unsafe_allow_html=True)
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown("# 🏠 Property Health Intelligence Platform")
        st.markdown("### *Prototype Access Portal*")
        
        st.markdown("## 📋 Confidential Preview Access")
        st.info("🔒 This is a confidential prototype demonstration. By accessing this platform, you agree to treat all information as proprietary and confidential.")
        
        col1, col2 = st.columns(2)
        with col1:
            confidential_understood = st.checkbox("I understand this is confidential", key="conf_checkbox")
            respect_ip = st.checkbox("I will respect intellectual property", key="ip_checkbox")
        with col2:
            professional_courtesy = st.checkbox("I agree to professional standards", key="courtesy_checkbox")
            authorized_access = st.checkbox("I am an authorized stakeholder", key="auth_checkbox")

        st.markdown("## ✍️ Digital Signature")
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name *", placeholder="Enter your full name")
        with col2:
            email_address = st.text_input("Email Address *", placeholder="your.email@company.com")
        
        company_org = st.text_input("Company/Organization", placeholder="Your company")
        access_purpose = st.selectbox("Purpose of Access *", ["", "Potential Investor", "Business Partner", "Industry Professional", "Other"])
        
        st.markdown("## 🔑 Access Code")
        password_input = st.text_input("Enter access code:", type="password", placeholder="Access code required")

        all_acknowledged = confidential_understood and respect_ip and professional_courtesy and authorized_access
        password_correct = password_input == self.password
        signature_complete = full_name.strip() != "" and email_address.strip() != "" and access_purpose != ""
        email_valid = "@" in email_address and "." in email_address if email_address else False

        if st.button("🚀 ACCESS PREVIEW", type="primary", disabled=not (all_acknowledged and password_correct and signature_complete and email_valid)):
            if all_acknowledged and password_correct and signature_complete and email_valid:
                st.session_state.access_info = {'name': full_name, 'email': email_address, 'company': company_org, 'purpose': access_purpose, 'timestamp': datetime.datetime.now()}
                st.session_state.authenticated = True
                st.session_state.access_timestamp = datetime.datetime.now()
                st.success("✅ Access granted! Loading platform...")
                st.rerun()
            else:
                st.error("❌ Please complete all required fields and acknowledgments")
        
        st.markdown("**Contact:** JESquared24@gmail.com")
        st.markdown('</div>', unsafe_allow_html=True)

    def is_authenticated(self):
        return st.session_state.get('authenticated', False)

    def render_session_info(self):
        if self.is_authenticated():
            access_info = st.session_state.get('access_info', {})
            st.sidebar.markdown("---")
            st.sidebar.markdown("**🔒 Authorized Session**")
            if access_info.get('name'):
                st.sidebar.markdown(f"**User:** {access_info['name']}")
            if st.sidebar.button("🚪 End Session", type="secondary"):
                st.session_state.authenticated = False
                st.rerun()

class Dashboard:
    def __init__(self):
        self.calculator = PropertyHealthCalculator()
        self.auth_manager = AuthenticationManager()
        self.init_session_state()

    def init_session_state(self):
        if 'properties' not in st.session_state:
            st.session_state.properties = []
        if 'maintenance_records' not in st.session_state:
            st.session_state.maintenance_records = []
        if 'property_zip_codes' not in st.session_state:
            st.session_state.property_zip_codes = {}

    def render_header(self):
        st.title("🏠 Property Health Intelligence Dashboard")
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Properties", len(st.session_state.properties))
        with col2:
            if st.session_state.properties:
                avg_score = np.mean([self.calculator.calculate_overall_score(prop)['overall_score'] for prop in st.session_state.properties])
                st.metric("Average Health Score", f"{avg_score:.1f}")
            else:
                st.metric("Average Health Score", "N/A")
        with col3:
            urgent_items = len([r for r in st.session_state.maintenance_records if r.urgency == "High"])
            st.metric("Urgent Items", urgent_items)
        with col4:
            total_cost = sum([r.cost for r in st.session_state.maintenance_records])
            st.metric("Total Maintenance Cost", f"${total_cost:,.0f}")

    def render_property_management(self):
        st.sidebar.header("Property Management")
        with st.sidebar.expander("➕ Add New Property", expanded=True):
            with st.form("property_form"):
                address = st.text_input("Property Address")
                year_built = st.number_input("Year Built", min_value=1800, max_value=2024, value=2000)
                square_footage = st.number_input("Square Footage", min_value=500, max_value=10000, value=2000)
                property_type = st.selectbox("Property Type", ["Single Family", "Townhouse", "Condo", "Multi-Family", "Commercial"])
                roof_material = st.selectbox("Roof Material", ["Asphalt Shingles", "Metal", "Tile", "Slate", "Wood"])
                foundation_type = st.selectbox("Foundation Type", ["Concrete Slab", "Basement", "Crawl Space", "Pier & Beam"])
                hvac_age = st.number_input("HVAC Age (years)", min_value=0, max_value=50, value=5)
                electrical_age = st.number_input("Electrical Age (years)", min_value=0, max_value=100, value=15)
                plumbing_age = st.number_input("Plumbing Age (years)", min_value=0, max_value=100, value=20)
                zip_code = st.text_input("ZIP Code", value="22701", help="For regional cost estimates")
                last_inspection = st.date_input("Last Inspection Date").strftime("%Y-%m-%d")
                
                if st.form_submit_button("Add Property", type="primary") and address:
                    new_property = Property(address, year_built, square_footage, property_type, roof_material, foundation_type, hvac_age, electrical_age, plumbing_age, last_inspection)
                    st.session_state.properties.append(new_property)
                    st.session_state.property_zip_codes[address] = zip_code
                    st.success(f"✅ Added property: {address}")
                    st.rerun()

        if st.session_state.properties:
            with st.sidebar.expander("🗑️ Delete Property"):
                property_addresses = [f"{i+1}. {prop.address}" for i, prop in enumerate(st.session_state.properties)]
                selected_to_delete = st.selectbox("Select property to delete:", property_addresses, key="delete_selector")
                if selected_to_delete and st.button("🗑️ Delete", type="secondary"):
                    idx = int(selected_to_delete.split('.')[0]) - 1
                    deleted_property = st.session_state.properties[idx]
                    del st.session_state.properties[idx]
                    st.success(f"🗑️ Deleted: {deleted_property.address}")
                    st.rerun()

    def render_maintenance_input(self):
        if not st.session_state.properties:
            return
        st.sidebar.header("Add Maintenance Record")
        with st.sidebar.form("maintenance_form"):
            property_addresses = [prop.address for prop in st.session_state.properties]
            selected_address = st.selectbox("Property", property_addresses)
            date = st.date_input("Date").strftime("%Y-%m-%d")
            category = st.selectbox("Category", ["HVAC", "Plumbing", "Electrical", "Roofing", "Foundation", "General"])
            description = st.text_area("Description")
            cost = st.number_input("Cost ($)", min_value=0.0, value=0.0, step=50.0)
            contractor = st.text_input("Contractor")
            urgency = st.selectbox("Urgency", ["Low", "Medium", "High"])
            
            if st.form_submit_button("Add Record") and description:
                new_record = MaintenanceRecord(date, category, description, cost, contractor, urgency)
                st.session_state.maintenance_records.append(new_record)
                st.success("Added maintenance record")
                st.rerun()

    def render_property_selector(self, key_suffix=""):
        if not st.session_state.properties:
            st.info("👈 Add a property to get started!")
            return None
        addresses = [prop.address for prop in st.session_state.properties]
        selected_address = st.selectbox("Select Property", addresses, key=f"property_selector_{key_suffix}")
        return st.session_state.properties[addresses.index(selected_address)]

    def render_health_score_visualization(self, property_data: Property):
        scores = self.calculator.calculate_overall_score(property_data)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Overall Health Score", f"{scores['overall_score']:.1f}/100")
            if scores['overall_score'] >= 90:
                st.success("Excellent condition! 🟢")
            elif scores['overall_score'] >= 75:
                st.info("Good condition 🟡")
            elif scores['overall_score'] >= 60:
                st.warning("Needs attention ⚠️")
            else:
                st.error("Requires immediate action! 🔴")
        with col2:
            st.write("**Category Breakdown:**")
            for category in scores['category_scores'].keys():
                score = scores['category_scores'][category]['score']
                color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                st.write(f"{color} **{category}:** {score:.1f}")

    def render_detailed_breakdown(self, property_data: Property):
        scores = self.calculator.calculate_overall_score(property_data)
        st.subheader("Detailed Breakdown")
        for category, data in scores['category_scores'].items():
            with st.expander(f"{category} - Score: {data['score']}"):
                for component, score in data['components'].items():
                    color = "green" if score >= 80 else "orange" if score >= 60 else "red"
                    st.markdown(f"**{component}:** <span style='color:{color}'>{score}</span>", unsafe_allow_html=True)

    def render_maintenance_history(self, property_data: Property):
        st.subheader("Maintenance History")
        property_records = [r for r in st.session_state.maintenance_records]
        if not property_records:
            st.info("No maintenance records found.")
            return
        records_data = [{'Date': r.date, 'Category': r.category, 'Description': r.description, 'Cost': f"${r.cost:,.0f}", 'Contractor': r.contractor, 'Urgency': r.urgency} for r in property_records]
        st.dataframe(pd.DataFrame(records_data), use_container_width=True)

    def render_predictions_and_recommendations(self, property_data: Property):
        st.subheader("Predictions & Recommendations")
        property_zip = st.session_state.property_zip_codes.get(property_data.address, "22701")
        schedule = self.calculator.generate_maintenance_schedule(property_data, property_zip)
        
        tab1, tab2 = st.tabs(["🔮 Upcoming Tasks", "💰 Cost Planning"])
        
        with tab1:
            st.write("**Next 6 Months - Priority Actions:**")
            upcoming_tasks = [task for task in schedule if task["next_due"] <= datetime.datetime.now() + datetime.timedelta(days=180)][:5]
            if not upcoming_tasks:
                st.info("✅ No urgent tasks in the next 6 months!")
            else:
                for task in upcoming_tasks:
                    priority_icon = {"high": "🔴", "important": "🟡", "routine": "🟢"}[task["priority"]]
                    days_until = (task["next_due"] - datetime.datetime.now()).days
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"{priority_icon} **{task['task']}**")
                        st.write(task["description"])
                    with col2:
                        st.write(f"**${task['estimated_cost']:,}**")
                    with col3:
                        if days_until <= 30:
                            st.warning(f"{days_until} days")
                        else:
                            st.info(f"{days_until} days")
        
        with tab2:
            st.write("**Cost Estimates by Category:**")
            user_zip = st.text_input("ZIP code for pricing:", value=property_zip)
            if user_zip:
                regional_info = self.calculator.get_regional_info(user_zip)
                st.info(f"**Region:** {regional_info['region']}")
                
                cost_categories = [("HVAC Service", "hvac_service"), ("Roof Repair", "roof_repair"), ("Plumbing", "plumbing_repair"), ("Electrical", "electrical_panel")]
                for category_name, cost_key in cost_categories:
                    estimates = self.calculator.get_local_cost_estimate(cost_key, user_zip)
                    st.write(f"**{category_name}:** ${estimates['min']:,} - ${estimates['max']:,} (avg: ${estimates['avg']:,})")

    def render_contractor_marketplace(self):
        st.subheader("Find Certified Professionals")
        contractors = [
            {'name': 'ABC HVAC Services', 'category': 'HVAC', 'rating': 4.8, 'reviews': 234, 'price': '$$'},
            {'name': 'Reliable Plumbing Co.', 'category': 'Plumbing', 'rating': 4.6, 'reviews': 156, 'price': '$'},
            {'name': 'Elite Electrical', 'category': 'Electrical', 'rating': 4.9, 'reviews': 89, 'price': '$$$'}
        ]
        for contractor in contractors:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{contractor['name']}** ({contractor['category']})")
                st.write(f"⭐ {contractor['rating']} ({contractor['reviews']} reviews)")
            with col2:
                st.write(f"**{contractor['price']}**")
            with col3:
                if st.button("Contact", key=f"contact_{contractor['name']}"):
                    st.success(f"Contact request sent!")

    def run(self):
        if not self.auth_manager.is_authenticated():
            self.auth_manager.render_auth_screen()
            return
        
        self.render_header()
        self.render_property_management()
        self.render_maintenance_input()
        self.auth_manager.render_session_info()
        
        tab1, tab2, tab3 = st.tabs(["Property Health", "Maintenance", "Find Contractors"])
        
        with tab1:
            selected_property = self.render_property_selector("health")
            if selected_property:
                self.render_health_score_visualization(selected_property)
                self.render_detailed_breakdown(selected_property)
                self.render_predictions_and_recommendations(selected_property)
        
        with tab2:
            selected_property = self.render_property_selector("maintenance")
            if selected_property:
                self.render_maintenance_history(selected_property)
        
        with tab3:
            self.render_contractor_marketplace()

def main():
    dashboard = Dashboard()
    dashboard.run()

if __name__ == "__main__":
    main()