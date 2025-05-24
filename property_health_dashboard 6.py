#!/usr/bin/env python3
"""
Property Health Intelligence Dashboard
A comprehensive dashboard application for property health monitoring and management.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import random

class AuthenticationManager:
    """Handle authentication and NDA agreement."""
    
    def __init__(self):
        self.password = "PropHealth2025!"  # Change this to your desired password
        
    def render_auth_screen(self):
        """Render the authentication and NDA agreement screen."""
        # Custom CSS for styling
        st.markdown("""
        <style>
        .auth-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .logo-section {
            text-align: center;
            margin-bottom: 2rem;
        }
        .nda-text {
            background: rgba(255,255,255,0.1);
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid #ffd700;
        }
        .warning-box {
            background: rgba(255,69,0,0.2);
            border: 2px solid #ff4500;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        
        # Logo and title section
        st.markdown('<div class="logo-section">', unsafe_allow_html=True)
        st.markdown("# 🏠 Property Health Intelligence Platform")
        st.markdown("### *Prototype Access Portal*")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # NDA Agreement
        st.markdown("## 📋 Confidential Preview Access & Professional Courtesy Agreement")
        
        st.markdown("""
        <div class="nda-text">
        <h4>🔒 PROPRIETARY INFORMATION PREVIEW</h4>
        
        Thank you for your interest in our Property Health Intelligence Platform. This is a confidential prototype demonstration containing proprietary business concepts and technical implementations.
        
        <strong>What you're about to see includes:</strong>
        • Proprietary algorithms and scoring methodologies
        • Business processes and operational strategies  
        • Technical implementations and system architecture
        • Market research and competitive intelligence
        • Product roadmaps and development plans
        
        <strong>We respectfully request that you:</strong>
        • Treat all information as confidential and proprietary
        • Refrain from sharing details with unauthorized parties
        • Avoid using our concepts for competitive purposes
        • Contact us directly for any business discussions
        
        <strong>Professional courtesy expectations:</strong>
        • This system represents significant time and investment
        • We are actively pursuing patent protection where applicable
        • We appreciate your discretion and professionalism
        • Formal NDAs available for serious business discussions
        
        <strong>Note:</strong> This demonstration is intended for evaluation purposes by potential investors, partners, and authorized stakeholders only.
        </div>
        """, unsafe_allow_html=True)
        
        # Warning box
        st.markdown("""
        <div class="warning-box">
        <strong>🛡️ INTELLECTUAL PROPERTY NOTICE:</strong> This platform contains proprietary concepts and implementations that are the exclusive property of JESquared. While this preview is provided in good faith, we reserve all rights to our intellectual property and business methods.
        </div>
        """, unsafe_allow_html=True)
        
        # Agreement checkboxes
        st.markdown("## ✅ Professional Courtesy Acknowledgments")
        
        col1, col2 = st.columns(2)
        
        with col1:
            confidential_understood = st.checkbox("I understand this information is confidential", key="conf_checkbox")
            respect_ip = st.checkbox("I will respect the intellectual property", key="ip_checkbox")
        
        with col2:
            professional_courtesy = st.checkbox("I agree to professional courtesy standards", key="courtesy_checkbox")
            authorized_access = st.checkbox("I am an authorized stakeholder", key="auth_checkbox")
        
        # Digital signature section
        st.markdown("## ✍️ Digital Signature & Contact Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input(
                "Full Name *", 
                placeholder="Enter your full name",
                help="This will be logged for security purposes"
            )
            
        with col2:
            email_address = st.text_input(
                "Email Address *", 
                placeholder="your.email@company.com",
                help="We'll send you updates and may follow up"
            )
        
        # Optional company/organization field
        company_org = st.text_input(
            "Company/Organization (Optional)", 
            placeholder="Your company or organization name"
        )
        
        # Purpose of access
        access_purpose = st.selectbox(
            "Purpose of Access *",
            ["", "Potential Investor", "Business Partner", "Industry Professional", "Academic/Research", "Other"],
            help="Help us understand your interest"
        )
        
        # Password entry
        st.markdown("## 🔑 Access Code")
    def render_session_info(self):
        """Render session information in sidebar."""
        if self.is_authenticated():
            access_time = st.session_state.get('access_timestamp', 'Unknown')
            access_info = st.session_state.get('access_info', {})
            
            st.sidebar.markdown("---")
            st.sidebar.markdown("**🔒 Authorized Session**")
            if access_info.get('name'):
                st.sidebar.markdown(f"**User:** {access_info['name']}")
            st.sidebar.markdown(f"**Access Time:** {access_time.strftime('%Y-%m-%d %H:%M')}")
            
            # Show access log for admin purposes
            if st.sidebar.expander("📊 Access Log (Demo)"):
                access_log = st.session_state.get('access_log', [])
                st.sidebar.write(f"Total accesses: {len(access_log)}")
                for i, log in enumerate(access_log[-3:]):  # Show last 3
                    st.sidebar.write(f"**{log['name']}** - {log['purpose']}")
            
            if st.sidebar.button("🚪 End Session", type="secondary"):
                st.session_state.authenticated = False
                                    st.rerun()
            "Enter access code to continue:", 
            type="password",
            placeholder="Access code required"
        )
        
        # Contact information
        st.markdown("## 📞 Questions or Issues?")
        with st.expander("Contact JESquared"):
            st.write("**Email:** JESquared24@gmail.com")
            st.write("**Company:** JESquared")
            st.write("**Response Time:** Within 24 hours")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 ACCESS PREVIEW", type="primary", disabled=not (all_acknowledged and password_correct)):
                if all_acknowledged and password_correct:
                    st.session_state.authenticated = True
                    st.session_state.access_timestamp = datetime.datetime.now()
                    st.success("✅ Access granted! Loading platform preview...")
                    st.rerun()
                elif not all_acknowledged:
                    st.error("❌ Please acknowledge all professional courtesy items")
                elif not password_correct:
                    st.error("❌ Incorrect access code")
        
        # Access button
        all_acknowledged = confidential_understood and respect_ip and professional_courtesy and authorized_access
        password_correct = password_input == self.password
        signature_complete = full_name.strip() != "" and email_address.strip() != "" and access_purpose != ""
        
        # Validate email format
        email_valid = "@" in email_address and "." in email_address if email_address else False
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def is_authenticated(self):
        """Check if user is authenticated."""
        return st.session_state.get('authenticated', False)
    
    def log_access_attempt(self, access_info):
        """Log access attempt - in production this would send email notification."""
        # In a real implementation, you would:
        # 1. Send email to JESquared24@gmail.com with access details
        # 2. Store in database for tracking
        # 3. Log IP address and other security info
        
        # For demo purposes, we'll store in session state
        if 'access_log' not in st.session_state:
            st.session_state.access_log = []
        
        st.session_state.access_log.append(access_info)
        
        # This is where you'd implement actual email sending:
        """
        import smtplib
        from email.mime.text import MIMEText
        
        subject = f"Property Health Platform Access: {access_info['name']}"
        body = f'''
        New access to Property Health Intelligence Platform:
        
        Name: {access_info['name']}
        Email: {access_info['email']}
        Company: {access_info['company']}
        Purpose: {access_info['purpose']}
        Timestamp: {access_info['timestamp']}
        
        This person has accessed the confidential preview.
        '''
        
        # Configure your email settings and send
        """
        pass

@dataclass
class Property:
    """Property data structure."""
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
    """Maintenance record data structure."""
    date: str
    category: str
    description: str
    cost: float
    contractor: str
    urgency: str

class PropertyHealthCalculator:
    """Calculate property health scores and predictions."""
    
    def __init__(self):
        self.weights = {
            'structural': 0.3,
            'systems': 0.4,
            'safety': 0.2,
            'environmental': 0.1
        }
    
    def calculate_age_score(self, age: int, expected_life: int) -> float:
        """Calculate score based on age vs expected lifespan."""
        if age <= 0:
            return 100
        ratio = age / expected_life
        if ratio <= 0.5:
            return 100 - (ratio * 20)  # Minimal degradation in first half
        elif ratio <= 0.8:
            return 90 - ((ratio - 0.5) * 100)  # Moderate degradation
        else:
            return max(0, 60 - ((ratio - 0.8) * 150))  # Rapid degradation
    
    def calculate_structural_score(self, property_data: Property) -> Dict:
        """Calculate structural integrity score."""
        age = 2024 - property_data.year_built
        foundation_scores = {
            'Concrete Slab': 85,
            'Basement': 90,
            'Crawl Space': 75,
            'Pier & Beam': 70
        }
        
        roof_scores = {
            'Asphalt Shingles': 80,
            'Metal': 90,
            'Tile': 95,
            'Slate': 98,
            'Wood': 70
        }
        
        age_score = self.calculate_age_score(age, 80)
        foundation_score = foundation_scores.get(property_data.foundation_type, 75)
        roof_score = roof_scores.get(property_data.roof_material, 80)
        
        overall_score = (age_score * 0.4 + foundation_score * 0.3 + roof_score * 0.3)
        
        return {
            'score': round(overall_score, 1),
            'components': {
                'Age Factor': round(age_score, 1),
                'Foundation': foundation_score,
                'Roof': roof_score
            }
        }
    
    def calculate_systems_score(self, property_data: Property) -> Dict:
        """Calculate core systems score."""
        hvac_score = self.calculate_age_score(property_data.hvac_age, 15)
        electrical_score = self.calculate_age_score(property_data.electrical_age, 40)
        plumbing_score = self.calculate_age_score(property_data.plumbing_age, 50)
        
        overall_score = (hvac_score * 0.4 + electrical_score * 0.3 + plumbing_score * 0.3)
        
        return {
            'score': round(overall_score, 1),
            'components': {
                'HVAC': round(hvac_score, 1),
                'Electrical': round(electrical_score, 1),
                'Plumbing': round(plumbing_score, 1)
            }
        }
    
    def calculate_safety_score(self, property_data: Property) -> Dict:
        """Calculate safety and compliance score."""
        # Simplified safety calculation based on age and type
        base_score = 85
        age = 2024 - property_data.year_built
        
        if age > 30:
            base_score -= 10
        if age > 50:
            base_score -= 10
            
        return {
            'score': round(base_score, 1),
            'components': {
                'Code Compliance': base_score,
                'Safety Systems': base_score,
                'Accessibility': base_score - 5
            }
        }
    
    def calculate_environmental_score(self, zip_code: str = "22701") -> Dict:
        """Calculate environmental exposure score."""
        # Simplified environmental scoring
        base_score = 80
        
        return {
            'score': round(base_score, 1),
            'components': {
                'Weather Exposure': base_score,
                'Natural Disasters': base_score + 5,
                'Air Quality': base_score - 5
            }
        }
    
    def calculate_overall_score(self, property_data: Property) -> Dict:
        """Calculate overall property health score."""
        structural = self.calculate_structural_score(property_data)
        systems = self.calculate_systems_score(property_data)
        safety = self.calculate_safety_score(property_data)
        environmental = self.calculate_environmental_score()
        
        overall = (
            structural['score'] * self.weights['structural'] +
            systems['score'] * self.weights['systems'] +
            safety['score'] * self.weights['safety'] +
            environmental['score'] * self.weights['environmental']
        )
        
        return {
            'overall_score': round(overall, 1),
            'category_scores': {
                'Structural': structural,
                'Systems': systems,
                'Safety': safety,
                'Environmental': environmental
            }
        }

class Dashboard:
    """Main dashboard class."""
    
    def __init__(self):
        self.calculator = PropertyHealthCalculator()
        self.auth_manager = AuthenticationManager()
        self.init_session_state()
    
    def init_session_state(self):
        """Initialize session state variables."""
        if 'properties' not in st.session_state:
            st.session_state.properties = []
        if 'maintenance_records' not in st.session_state:
            st.session_state.maintenance_records = []
        if 'selected_property_idx' not in st.session_state:
            st.session_state.selected_property_idx = 0
    
    def render_header(self):
        """Render dashboard header."""
        st.title("🏠 Property Health Intelligence Dashboard")
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Properties", len(st.session_state.properties))
        
        with col2:
            if st.session_state.properties:
                avg_score = np.mean([
                    self.calculator.calculate_overall_score(prop)['overall_score'] 
                    for prop in st.session_state.properties
                ])
                st.metric("Average Health Score", f"{avg_score:.1f}")
            else:
                st.metric("Average Health Score", "N/A")
        
        with col3:
            urgent_items = len([r for r in st.session_state.maintenance_records if r.urgency == "High"])
            st.metric("Urgent Items", urgent_items)
        
        with col4:
            total_maintenance_cost = sum([r.cost for r in st.session_state.maintenance_records])
            st.metric("Total Maintenance Cost", f"${total_maintenance_cost:,.0f}")
    
    def render_property_management(self):
        """Render property management section with add/delete functionality."""
        st.sidebar.header("Property Management")
        
        # Add new property section
        with st.sidebar.expander("➕ Add New Property", expanded=True):
            with st.form("property_form"):
                address = st.text_input("Property Address")
                year_built = st.number_input("Year Built", min_value=1800, max_value=2024, value=2000)
                square_footage = st.number_input("Square Footage", min_value=500, max_value=10000, value=2000)
                
                property_type = st.selectbox("Property Type", [
                    "Single Family", "Townhouse", "Condo", "Multi-Family", "Commercial"
                ])
                
                roof_material = st.selectbox("Roof Material", [
                    "Asphalt Shingles", "Metal", "Tile", "Slate", "Wood"
                ])
                
                foundation_type = st.selectbox("Foundation Type", [
                    "Concrete Slab", "Basement", "Crawl Space", "Pier & Beam"
                ])
                
                hvac_age = st.number_input("HVAC System Age (years)", min_value=0, max_value=50, value=5)
                electrical_age = st.number_input("Electrical System Age (years)", min_value=0, max_value=100, value=15)
                plumbing_age = st.number_input("Plumbing Age (years)", min_value=0, max_value=100, value=20)
                
                last_inspection = st.date_input("Last Inspection Date").strftime("%Y-%m-%d")
                
                submitted = st.form_submit_button("Add Property", type="primary")
                
                if submitted and address:
                    new_property = Property(
                        address=address,
                        year_built=year_built,
                        square_footage=square_footage,
                        property_type=property_type,
                        roof_material=roof_material,
                        foundation_type=foundation_type,
                        hvac_age=hvac_age,
                        electrical_age=electrical_age,
                        plumbing_age=plumbing_age,
                        last_inspection=last_inspection
                    )
                    st.session_state.properties.append(new_property)
                    st.success(f"✅ Added property: {address}")
                    st.rerun()
        
        # Delete property section
        if st.session_state.properties:
            with st.sidebar.expander("🗑️ Delete Property"):
                st.warning("⚠️ This action cannot be undone!")
                
                property_addresses = [f"{i+1}. {prop.address}" for i, prop in enumerate(st.session_state.properties)]
                selected_to_delete = st.selectbox(
                    "Select property to delete:", 
                    property_addresses,
                    key="delete_property_selector"
                )
                
                if selected_to_delete:
                    selected_idx = int(selected_to_delete.split('.')[0]) - 1
                    property_to_delete = st.session_state.properties[selected_idx]
                    
                    st.write(f"**Property:** {property_to_delete.address}")
                    st.write(f"**Built:** {property_to_delete.year_built}")
                    st.write(f"**Type:** {property_to_delete.property_type}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🗑️ Delete", type="secondary", key="confirm_delete"):
                            # Remove associated maintenance records
                            st.session_state.maintenance_records = [
                                r for r in st.session_state.maintenance_records 
                                if r not in self.get_property_maintenance_records(property_to_delete)
                            ]
                            
                            # Remove property
                            del st.session_state.properties[selected_idx]
                            
                            # Reset selected property index if needed
                            if st.session_state.selected_property_idx >= len(st.session_state.properties):
                                st.session_state.selected_property_idx = max(0, len(st.session_state.properties) - 1)
                            
                            st.success(f"🗑️ Deleted property: {property_to_delete.address}")
                            st.rerun()
                    
                    with col2:
                        st.button("Cancel", key="cancel_delete")
        
        # Property summary
        if st.session_state.properties:
            st.sidebar.markdown("---")
            st.sidebar.write(f"**Total Properties:** {len(st.session_state.properties)}")
            for i, prop in enumerate(st.session_state.properties):
                score = self.calculator.calculate_overall_score(prop)['overall_score']
                emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                st.sidebar.write(f"{emoji} {prop.address[:25]}{'...' if len(prop.address) > 25 else ''}")
    
    def get_property_maintenance_records(self, property_data: Property) -> List[MaintenanceRecord]:
        """Get maintenance records for a specific property."""
        return [
            r for r in st.session_state.maintenance_records 
            if property_data.address in [prop.address for prop in st.session_state.properties]
        ]
    
    def render_maintenance_input(self):
        """Render maintenance record input."""
        if not st.session_state.properties:
            return
            
        st.sidebar.header("Add Maintenance Record")
        
        with st.sidebar.form("maintenance_form"):
            property_addresses = [prop.address for prop in st.session_state.properties]
            selected_address = st.selectbox("Property", property_addresses)
            
            date = st.date_input("Date").strftime("%Y-%m-%d")
            category = st.selectbox("Category", [
                "HVAC", "Plumbing", "Electrical", "Roofing", "Foundation", "General"
            ])
            description = st.text_area("Description")
            cost = st.number_input("Cost ($)", min_value=0.0, value=0.0, step=50.0)
            contractor = st.text_input("Contractor")
            urgency = st.selectbox("Urgency", ["Low", "Medium", "High"])
            
            submitted = st.form_submit_button("Add Record")
            
            if submitted and description:
                new_record = MaintenanceRecord(
                    date=date,
                    category=category,
                    description=description,
                    cost=cost,
                    contractor=contractor,
                    urgency=urgency
                )
                st.session_state.maintenance_records.append(new_record)
                st.success("Added maintenance record")
                st.rerun()
    
    def render_property_selector(self, key_suffix=""):
        """Render property selector."""
        if not st.session_state.properties:
            st.info("👈 Add a property to get started!")
            return None
            
        addresses = [prop.address for prop in st.session_state.properties]
        selected_address = st.selectbox("Select Property", addresses, key=f"property_selector_{key_suffix}")
        
        selected_idx = addresses.index(selected_address)
        st.session_state.selected_property_idx = selected_idx
        
        return st.session_state.properties[selected_idx]
    
    def render_health_score_visualization(self, property_data: Property):
        """Render health score visualizations."""
        scores = self.calculator.calculate_overall_score(property_data)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Overall score display
            st.metric("Overall Health Score", f"{scores['overall_score']:.1f}/100")
            
            # Score interpretation
            if scores['overall_score'] >= 90:
                st.success("Excellent condition! 🟢")
            elif scores['overall_score'] >= 75:
                st.info("Good condition 🟡")
            elif scores['overall_score'] >= 60:
                st.warning("Needs attention ⚠️")
            else:
                st.error("Requires immediate action! 🔴")
        
        with col2:
            # Category scores display
            st.write("**Category Breakdown:**")
            categories = list(scores['category_scores'].keys())
            
            for category in categories:
                score = scores['category_scores'][category]['score']
                col_name, col_score = st.columns([3, 1])
                with col_name:
                    st.write(f"**{category}**")
                with col_score:
                    color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                    st.write(f"{color} {score:.1f}")
    
    def render_detailed_breakdown(self, property_data: Property):
        """Render detailed score breakdown."""
        scores = self.calculator.calculate_overall_score(property_data)
        
        st.subheader("Detailed Breakdown")
        
        for category, data in scores['category_scores'].items():
            with st.expander(f"{category} - Score: {data['score']}"):
                for component, score in data['components'].items():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{component}**")
                    with col2:
                        color = "green" if score >= 80 else "orange" if score >= 60 else "red"
                        st.markdown(f"<span style='color:{color}'>{score}</span>", unsafe_allow_html=True)
    
    def render_maintenance_history(self, property_data: Property):
        """Render maintenance history for selected property."""
        st.subheader("Maintenance History")
        
        property_records = self.get_property_maintenance_records(property_data)
        
        if not property_records:
            st.info("No maintenance records found for this property.")
            return
        
        # Convert to DataFrame for better display
        records_data = []
        for record in property_records:
            records_data.append({
                'Date': record.date,
                'Category': record.category,
                'Description': record.description,
                'Cost': f"${record.cost:,.0f}",
                'Contractor': record.contractor,
                'Urgency': record.urgency
            })
        
        df = pd.DataFrame(records_data)
        st.dataframe(df, use_container_width=True)
        
        # Simple cost summary
        total_cost = sum([r.cost for r in property_records])
        avg_cost = total_cost / len(property_records) if property_records else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Maintenance Cost", f"${total_cost:,.0f}")
        with col2:
            st.metric("Average Cost per Record", f"${avg_cost:,.0f}")
    
    def render_predictions_and_recommendations(self, property_data: Property):
        """Render predictions and recommendations."""
        st.subheader("Predictions & Recommendations")
        
        scores = self.calculator.calculate_overall_score(property_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Upcoming Maintenance Predictions:**")
            
            # Generate some sample predictions based on system ages
            predictions = []
            
            if property_data.hvac_age > 10:
                predictions.append({
                    'item': 'HVAC Filter Replacement',
                    'timeframe': '1-2 months',
                    'estimated_cost': '$50-100',
                    'priority': 'Medium'
                })
            
            if property_data.hvac_age > 12:
                predictions.append({
                    'item': 'HVAC System Service',
                    'timeframe': '3-6 months',
                    'estimated_cost': '$200-400',
                    'priority': 'High'
                })
            
            if property_data.electrical_age > 25:
                predictions.append({
                    'item': 'Electrical Panel Inspection',
                    'timeframe': '6-12 months',
                    'estimated_cost': '$150-300',
                    'priority': 'Medium'
                })
            
            for pred in predictions:
                priority_color = {
                    'Low': 'green',
                    'Medium': 'orange',
                    'High': 'red'
                }.get(pred['priority'], 'gray')
                
                st.markdown(f"""
                **{pred['item']}**  
                🕒 {pred['timeframe']} | 💰 {pred['estimated_cost']} | 
                <span style='color:{priority_color}'>●</span> {pred['priority']} Priority
                """, unsafe_allow_html=True)
                st.markdown("---")
        
        with col2:
            st.write("**Recommended Actions:**")
            
            # Generate recommendations based on scores
            for category, data in scores['category_scores'].items():
                if data['score'] < 70:
                    st.warning(f"**{category}**: Score below 70. Consider professional inspection.")
                elif data['score'] < 85:
                    st.info(f"**{category}**: Good condition. Monitor for changes.")
                else:
                    st.success(f"**{category}**: Excellent condition.")
    
    def render_contractor_marketplace(self):
        """Render contractor marketplace simulation."""
        st.subheader("Find Certified Professionals")
        
        # Sample contractors
        contractors = [
            {
                'name': 'ABC HVAC Services',
                'category': 'HVAC',
                'rating': 4.8,
                'reviews': 234,
                'price_range': '$$',
                'response_time': '2-4 hours'
            },
            {
                'name': 'Reliable Plumbing Co.',
                'category': 'Plumbing',
                'rating': 4.6,
                'reviews': 156,
                'price_range': '$',
                'response_time': '1-2 hours'
            },
            {
                'name': 'Elite Electrical',
                'category': 'Electrical',
                'rating': 4.9,
                'reviews': 89,
                'price_range': '$$$',
                'response_time': '4-6 hours'
            },
            {
                'name': 'Superior Roofing',
                'category': 'Roofing',
                'rating': 4.7,
                'reviews': 312,
                'price_range': '$$',
                'response_time': '24 hours'
            }
        ]
        
        category_filter = st.selectbox("Filter by Category", 
            ['All'] + list(set([c['category'] for c in contractors]))
        )
        
        filtered_contractors = contractors if category_filter == 'All' else [
            c for c in contractors if c['category'] == category_filter
        ]
        
        for contractor in filtered_contractors:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(f"**{contractor['name']}**")
                    st.write(f"Category: {contractor['category']}")
                    st.write(f"⭐ {contractor['rating']} ({contractor['reviews']} reviews)")
                
                with col2:
                    st.write(f"**Price: {contractor['price_range']}**")
                
                with col3:
                    st.write(f"**Response: {contractor['response_time']}**")
                
                with col4:
                    if st.button(f"Contact", key=f"contact_{contractor['name']}"):
                        st.success(f"Contact request sent to {contractor['name']}!")
                
                st.markdown("---")
    
    def render_analytics_dashboard(self):
        """Render analytics and insights."""
        if not st.session_state.properties:
            return
            
        st.subheader("Portfolio Analytics")
        
        # Calculate scores for all properties
        all_scores = []
        for prop in st.session_state.properties:
            score_data = self.calculator.calculate_overall_score(prop)
            all_scores.append({
                'address': prop.address,
                'overall_score': score_data['overall_score'],
                'structural': score_data['category_scores']['Structural']['score'],
                'systems': score_data['category_scores']['Systems']['score'],
                'safety': score_data['category_scores']['Safety']['score'],
                'environmental': score_data['category_scores']['Environmental']['score'],
                'year_built': prop.year_built,
                'property_type': prop.property_type
            })
        
        df_scores = pd.DataFrame(all_scores)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_score = df_scores['overall_score'].mean()
            st.metric("Average Score", f"{avg_score:.1f}")
        
        with col2:
            highest_score = df_scores['overall_score'].max()
            best_property = df_scores.loc[df_scores['overall_score'].idxmax(), 'address']
            st.metric("Highest Score", f"{highest_score:.1f}")
            st.caption(f"Property: {best_property}")
        
        with col3:
            lowest_score = df_scores['overall_score'].min()
            worst_property = df_scores.loc[df_scores['overall_score'].idxmin(), 'address']
            st.metric("Lowest Score", f"{lowest_score:.1f}")
            st.caption(f"Property: {worst_property}")
        
        # Display all property scores
        st.write("**All Property Scores:**")
        display_df = df_scores[['address', 'overall_score', 'structural', 'systems', 'safety', 'environmental']].round(1)
        st.dataframe(display_df, use_container_width=True)
    
    def run(self):
        """Run the main dashboard with authentication."""
        # Check authentication first
        if not self.auth_manager.is_authenticated():
            self.auth_manager.render_auth_screen()
            return
        
        # Main dashboard
        self.render_header()
        
        # Sidebar management
        self.render_property_management()
        self.render_maintenance_input()
        self.auth_manager.render_session_info()
        
        # Main content tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "Property Health", "Maintenance", "Find Contractors", "Analytics"
        ])
        
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
        
        with tab4:
            self.render_analytics_dashboard()

def main():
    """Main function to run the dashboard."""
    dashboard = Dashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
                priority_color = {
                    'Low': 'green',
                    'Medium': 'orange',
                    'High': 'red'
                }.get(pred['priority'], 'gray')
                
                st.markdown(f"""
                **{pred['item']}**  
                🕒 {pred['timeframe']} | 💰 {pred['estimated_cost']} | 
                <span style='color:{priority_color}'>●</span> {pred['priority']} Priority
                """, unsafe_allow_html=True)
                st.markdown("---")
        
        with col2:
            st.write("**Recommended Actions:**")
            
            # Generate recommendations based on scores
            for category, data in scores['category_scores'].items():
                if data['score'] < 70:
                    st.warning(f"**{category}**: Score below 70. Consider professional inspection.")
                elif data['score'] < 85:
                    st.info(f"**{category}**: Good condition. Monitor for changes.")
                else:
                    st.success(f"**{category}**: Excellent condition.")
    
    def render_contractor_marketplace(self):
        """Render contractor marketplace simulation."""
        st.subheader("Find Certified Professionals")
        
        # Sample contractors
        contractors = [
            {
                'name': 'ABC HVAC Services',
                'category': 'HVAC',
                'rating': 4.8,
                'reviews': 234,
                'price_range': '$$',
                'response_time': '2-4 hours'
            },
            {
                'name': 'Reliable Plumbing Co.',
                'category': 'Plumbing',
                'rating': 4.6,
                'reviews': 156,
                'price_range': '$',
                'response_time': '1-2 hours'
            },
            {
                'name': 'Elite Electrical',
                'category': 'Electrical',
                'rating': 4.9,
                'reviews': 89,
                'price_range': '$$$',
                'response_time': '4-6 hours'
            },
            {
                'name': 'Superior Roofing',
                'category': 'Roofing',
                'rating': 4.7,
                'reviews': 312,
                'price_range': '$$',
                'response_time': '24 hours'
            }
        ]
        
        category_filter = st.selectbox("Filter by Category", 
            ['All'] + list(set([c['category'] for c in contractors]))
        )
        
        filtered_contractors = contractors if category_filter == 'All' else [
            c for c in contractors if c['category'] == category_filter
        ]
        
        for contractor in filtered_contractors:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(f"**{contractor['name']}**")
                    st.write(f"Category: {contractor['category']}")
                    st.write(f"⭐ {contractor['rating']} ({contractor['reviews']} reviews)")
                
                with col2:
                    st.write(f"**Price: {contractor['price_range']}**")
                
                with col3:
                    st.write(f"**Response: {contractor['response_time']}**")
                
                with col4:
                    if st.button(f"Contact", key=f"contact_{contractor['name']}"):
                        st.success(f"Contact request sent to {contractor['name']}!")
                
                st.markdown("---")
    
    def render_analytics_dashboard(self):
        """Render analytics and insights."""
        if not st.session_state.properties:
            return
            
        st.subheader("Portfolio Analytics")
        
        # Calculate scores for all properties
        all_scores = []
        for prop in st.session_state.properties:
            score_data = self.calculator.calculate_overall_score(prop)
            all_scores.append({
                'address': prop.address,
                'overall_score': score_data['overall_score'],
                'structural': score_data['category_scores']['Structural']['score'],
                'systems': score_data['category_scores']['Systems']['score'],
                'safety': score_data['category_scores']['Safety']['score'],
                'environmental': score_data['category_scores']['Environmental']['score'],
                'year_built': prop.year_built,
                'property_type': prop.property_type
            })
        
        df_scores = pd.DataFrame(all_scores)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_score = df_scores['overall_score'].mean()
            st.metric("Average Score", f"{avg_score:.1f}")
        
        with col2:
            highest_score = df_scores['overall_score'].max()
            best_property = df_scores.loc[df_scores['overall_score'].idxmax(), 'address']
            st.metric("Highest Score", f"{highest_score:.1f}")
            st.caption(f"Property: {best_property}")
        
        with col3:
            lowest_score = df_scores['overall_score'].min()
            worst_property = df_scores.loc[df_scores['overall_score'].idxmin(), 'address']
            st.metric("Lowest Score", f"{lowest_score:.1f}")
            st.caption(f"Property: {worst_property}")
        
        # Display all property scores
        st.write("**All Property Scores:**")
        display_df = df_scores[['address', 'overall_score', 'structural', 'systems', 'safety', 'environmental']].round(1)
        st.dataframe(display_df, use_container_width=True)
    
    def run(self):
        """Run the main dashboard with authentication."""
        # Check authentication first
        if not self.auth_manager.is_authenticated():
            self.auth_manager.render_auth_screen()
            return
        
        # Main dashboard
        self.render_header()
        
        # Sidebar management
        self.render_property_management()
        self.render_maintenance_input()
        self.auth_manager.render_session_info()
        
        # Main content tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "Property Health", "Maintenance", "Find Contractors", "Analytics"
        ])
        
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
        
        with tab4:
            self.render_analytics_dashboard()

def main():
    """Main function to run the dashboard."""
    dashboard = Dashboard()
    dashboard.run()

if __name__ == "__main__":
    main()