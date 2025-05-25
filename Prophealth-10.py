# Previous code ... (st.set_page_config, imports, dataclasses, etc.)
# Define our new color palette
FOREST_GREEN = "#228B22"
PRIMARY_BLUE = "#006AFF"
LIGHT_BACKGROUND = "#F8F9FA"
SECONDARY_BACKGROUND = "#E9ECEF"
NAVY_BLUE = "#000080" # Changed from TEXT_COLOR
TEXT_LIGHT = "#FFFFFF"

# In Prophealth_3.py

# ... (Keep the existing st.set_page_config call that removed theme=None)
# ... (Keep imports, dataclasses, get_weather_data, PropertyHealthCalculator, AuthenticationManager)

def apply_global_styles():
    st.markdown(f"""
        <style>
            /* --- Global Font --- */
            html, body, [class*="st-"], .stApp {{
                font-family: 'Times New Roman', Times, serif !important;
            }}

            /* --- Main Backgrounds --- */
            .stApp {{
                background-color: {LIGHT_BACKGROUND} !important;
            }}
            /* Sidebar specific background if Streamlit's default doesn't match theme.
               Streamlit typically handles sidebar theming well based on its internal logic.
               If direct override is needed:
            section[data-testid="stSidebar"] > div:first-child {{
                background-color: {SECONDARY_BACKGROUND} !important; 
            }}
            */

            /* --- Text Colors --- */
            body, .stMarkdown {{ /* General text and markdown */
                color: {NAVY_BLUE} !important;
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: {FOREST_GREEN} !important; 
                font-family: 'Times New Roman', Times, serif !important;
            }}
            /* Caption color */
            .st-emotion-cache-10trblm.e1nzilvr1, p.caption, div.caption, span.caption {{ 
                color: {PRIMARY_BLUE} !important; 
            }}
            /* Labels for widgets - making them Navy Blue */
            .stTextInput label, .stNumberInput label, .stDateInput label, 
            .stSelectbox label, .stTextArea label, .stFileUploader label {{
                color: {NAVY_BLUE} !important;
                font-family: 'Times New Roman', Times, serif !important; /* Ensure font */
            }}


            /* --- Button Styling --- */
            .stButton>button {{
                border: 2px solid {FOREST_GREEN};
                background-color: {FOREST_GREEN};
                color: {TEXT_LIGHT};
                font-family: 'Times New Roman', Times, serif !important;
                border-radius: 0.3rem;
                padding: 0.5rem 1rem;
            }}
            .stButton>button:hover {{
                border-color: #1A661A; 
                background-color: #1A661A;
                color: {TEXT_LIGHT};
            }}
            /* Secondary button styling for Streamlit's type="secondary" */
            .stButton button[kind="secondary"], 
            .stButton button.st-emotion-cache-7ym5gk {{ /* More specific class if needed, can change */
                border: 2px solid {PRIMARY_BLUE} !important;
                background-color: transparent !important;
                color: {PRIMARY_BLUE} !important;
            }}
            .stButton button[kind="secondary"]:hover,
            .stButton button.st-emotion-cache-7ym5gk:hover {{
                background-color: {PRIMARY_BLUE} !important;
                color: {TEXT_LIGHT} !important;
            }}


            /* --- Metric Cards --- */
            .metric-card {{
                padding: 1rem 1.5rem;
                border-radius: 0.5rem; 
                color: {TEXT_LIGHT}; 
                margin-bottom: 1rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                transition: all 0.3s ease-in-out;
                border: 1px solid #ddd; 
            }}
            .metric-card:hover {{
                transform: translateY(-3px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }}
            .metric-card h3 {{ 
                color: {TEXT_LIGHT} !important; 
                margin-bottom: 0.3rem;
                font-size: 0.9rem; 
                font-weight: normal; 
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .metric-card p.value {{ 
                font-size: 2rem; 
                font-weight: bold; 
                color: {TEXT_LIGHT} !important; 
                margin-bottom: 0.1rem;
                line-height: 1.2;
            }}
            .metric-card small.delta {{
                font-size: 0.85rem;
                opacity: 0.9;
                color: {TEXT_LIGHT} !important;
            }}

            .metric-bg-forest-green {{ background-color: {FOREST_GREEN}; }}
            .metric-bg-primary-blue {{ background-color: {PRIMARY_BLUE}; }}
            .metric-bg-positive {{ background-color: {FOREST_GREEN}; }} 
            .metric-bg-neutral {{ background-color: {PRIMARY_BLUE}; }} 
            .metric-bg-warning {{ background-color: #FFC107; }} 
            .metric-bg-warning h3, .metric-bg-warning p.value, .metric-bg-warning small.delta {{ color: #333 !important; }} 
            .metric-bg-alert {{ background-color: #DC3545; }} 
            

            /* --- Containers and Expanders --- */
            .stExpander {{
                border: 1px solid #D3D3D3 !important; 
                border-radius: 0.3rem;
            }}
            .stExpander header {{
                background-color: {SECONDARY_BACKGROUND} !important; 
                color: {FOREST_GREEN} !important; 
                border-radius: 0.3rem 0.3rem 0 0;
                font-family: 'Times New Roman', Times, serif !important;
            }}
            /* Styling for st.container(border=True) */
            div.st-emotion-cache-r421ms {{ /* This class is for bordered container, can change with Streamlit versions */
                 border: 1px solid #D3D3D3 !important;
                 border-radius: 0.3rem !important;
                 /* padding: 1rem; /* Streamlit usually adds its own padding */
            }}


            /* --- Tabs --- */
            .stTabs [data-baseweb="tab-list"] {{
                background-color: {SECONDARY_BACKGROUND}; 
                border-radius: 0.3rem;
                padding: 0.25rem;
            }}
            .stTabs [data-baseweb="tab"] {{
                background-color: transparent;
                color: {PRIMARY_BLUE}; 
                font-family: 'Times New Roman', Times, serif !important;
            }}
            .stTabs [data-baseweb="tab"][aria-selected="true"] {{
                background-color: {PRIMARY_BLUE}; 
                color: {TEXT_LIGHT}; 
                border-radius: 0.3rem;
            }}

            /* --- Input fields (text, number, select, date, textarea, file_uploader button) --- */
            .stTextInput input, 
            .stNumberInput input,
            .stDateInput input,
            .stTextArea textarea,
            .stSelectbox > div[data-baseweb="select"] > div, /* Target the inner div that shows selected value */
            .stFileUploader button {{
                border-radius: 0.3rem !important;
                border: 1px solid #CED4DA !important; 
                font-family: 'Times New Roman', Times, serif !important;
                background-color: #FFFFFF !important; /* Explicitly light background for inputs */
                color: {NAVY_BLUE} !important; /* Text color inside input */
            }}
            /* Placeholder text for inputs */
            .stTextInput input::placeholder, 
            .stTextArea textarea::placeholder,
            .stNumberInput input::placeholder, /* NumberInput might not show placeholder conventionally */
            .stDateInput input::placeholder {{
                color: #6A7077 !important; /* A slightly darker placeholder, adjust as needed */
                opacity: 1; /* Ensure it's not too transparent */
                font-family: 'Times New Roman', Times, serif !important;
            }}
            /* Selectbox selected value text color (if not covered by general input color) */
             .stSelectbox > div[data-baseweb="select"] > div > div {{
                color: {NAVY_BLUE} !important;
             }}


        </style>
    """, unsafe_allow_html=True)

# The rest of your Dashboard class and other functions (PropertyHealthCalculator, AuthenticationManager, etc.)
# would follow here, unchanged from the previous full script.
# Make sure this apply_global_styles() function is called in your Dashboard.run() method
# after authentication, as before.
