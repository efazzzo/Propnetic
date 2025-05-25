class AuthenticationManager:
    def __init__(self):
        self.password = "PropHealth2025!"

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
        s_company_org = st.session_state.get("auth_company_org", "") # For access_info
        s_access_purpose = st.session_state.get("auth_access_purpose", "")
        s_password_input = st.session_state.get("auth_password_input", "")

        all_acknowledged = confidential_understood and respect_ip and professional_courtesy and authorized_access
        password_correct = s_password_input == self.password
        signature_complete = s_full_name.strip() != "" and s_email_address.strip() != "" and s_access_purpose != ""
        email_valid = "@" in s_email_address and "." in s_email_address.split('@')[-1] if s_email_address else False

        access_button_disabled = not (all_acknowledged and signature_complete and email_valid and s_password_input)

        if st.button("🚀 ACCESS PREVIEW", type="primary", disabled=access_button_disabled):
            if password_correct:
                st.session_state.access_info = {
                    'name': st.session_state.get("auth_full_name", ""), # Added default
                    'email': st.session_state.get("auth_email_address", ""), # Added default
                    'company': st.session_state.get("auth_company_org", ""), # Added default
                    'purpose': st.session_state.get("auth_access_purpose", ""), # Added default
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
                other_session_keys = ['access_info', 'authenticated', 'access_timestamp']

                for key_to_del in auth_keys_to_clear + other_session_keys:
                    if key_to_del in st.session_state:
                        del st.session_state[key_to_del]

                st.success("Logged out successfully.")
                st.rerun()
