# Previous code ... (st.set_page_config, imports, dataclasses, etc.)
# Define our new color palette
FOREST_GREEN = "#228B22"
PRIMARY_BLUE = "#006AFF"
LIGHT_BACKGROUND = "#F8F9FA"
SECONDARY_BACKGROUND = "#E9ECEF"
NAVY_BLUE = "#000080" 
TEXT_LIGHT = "#FFFFFF"

# In Prophealth_3.py

# ... (Keep the existing st.set_page_config call)
# ... (Keep imports, dataclasses, get_weather_data, PropertyHealthCalculator, AuthenticationManager)

def apply_global_styles():
    st.markdown(f"""
        <style>
            /* --- Global Font --- */
            html, body, [class*="st-"], .stApp {{
                font-family: sans-serif !important; /* CHANGED TO SANS-SERIF */
            }}

            /* --- Main Backgrounds --- */
            .stApp {{
                background-color: {LIGHT_BACKGROUND} !important;
            }}
            
            /* --- Text Colors --- */
            body, .stMarkdown {{ 
                color: {NAVY_BLUE} !important;
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: {FOREST_GREEN} !important; 
                font-family: sans-serif !important; /* CHANGED TO SANS-SERIF */
            }}
            .st-emotion-cache-10trblm.e1nzilvr1, p.caption, div.caption, span.caption {{ 
                color: {PRIMARY_BLUE} !important; 
            }}
            .stTextInput label, .stNumberInput label, .stDateInput label, 
            .stSelectbox label, .stTextArea label, .stFileUploader label {{
                color: {NAVY_BLUE} !important;
                font-family: sans-serif !important; /* CHANGED TO SANS-SERIF */
            }}

            /* --- Button Styling --- */
            .stButton>button {{
                border: 2px solid {FOREST_GREEN};
                background-color: {FOREST_GREEN};
                color: {TEXT_LIGHT};
                font-family: sans-serif !important; /* CHANGED TO SANS-SERIF */
                border-radius: 0.3rem;
                padding: 0.5rem 1rem;
            }}
            .stButton>button:hover {{
                border-color: #1A661A; 
                background-color: #1A661A;
                color: {TEXT_LIGHT};
            }}
            .stButton button[kind="secondary"], 
            .stButton button.st-emotion-cache-7ym5gk {{ 
                border: 2px solid {PRIMARY_BLUE} !important;
                background-color: transparent !important;
                color: {PRIMARY_BLUE} !important;
                font-family: sans-serif !important; /* Ensure font for secondary buttons */
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
                font-family: sans-serif !important; /* CHANGED TO SANS-SERIF */
            }}
            .metric-card p.value {{ 
                font-size: 2rem; 
                font-weight: bold; 
                color: {TEXT_LIGHT} !important; 
                margin-bottom: 0.1rem;
                line-height: 1.2;
                font-family: sans-serif !important; /* CHANGED TO SANS-SERIF */
            }}
            .metric-card small.delta {{
                font-size: 0.85rem;
                opacity: 0.9;
                color: {TEXT_LIGHT} !important;
                font-family: sans-serif !important; /* CHANGED TO SANS-SERIF */
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
                font-family: sans-serif !important; /* CHANGED TO SANS-SERIF */
            }}
            div.st-emotion-cache-r421ms {{ 
                 border: 1px solid #D3D3D3 !important;
                 border-radius: 0.3rem !important;
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
                font-family: sans-serif !important; /* CHANGED TO SANS-SERIF */
            }}
            .stTabs [data-baseweb="tab"][aria-selected="true"] {{
                background-color: {PRIMARY_BLUE}; 
                color: {TEXT_LIGHT}; 
                border-radius: 0.3rem;
            }}

            /* --- Input fields --- */
            .stTextInput input, 
            .stNumberInput input,
            .stDateInput input,
            .stTextArea textarea,
            .stSelectbox > div[data-baseweb="select"] > div,
            .stFileUploader button {{
                border-radius: 0.3rem !important;
                border: 1px solid #CED4DA !important; 
                font-family: sans-serif !important; /* CHANGED TO SANS-SERIF */
                background-color: #FFFFFF !important; 
                color: {NAVY_BLUE} !important; 
            }}
            .stFileUploader > label {{ 
                 font-family: sans-serif !important; /* CHANGED TO SANS-SERIF */
                 color: {NAVY_BLUE} !important;
            }}
            .stTextInput input::placeholder, 
            .stTextArea textarea::placeholder,
            .stNumberInput input::placeholder,
            .stDateInput input::placeholder {{
                color: #6A7077 !important; 
                opacity: 1; 
                font-family: sans-serif !important; /* CHANGED TO SANS-SERIF */
            }}
             .stSelectbox > div[data-baseweb="select"] > div > div {{
                color: {NAVY_BLUE} !important;
                font-family: sans-serif !important; /* CHANGED TO SANS-SERIF */
             }}
        </style>
    """, unsafe_allow_html=True)

# The rest of your Python code (Dashboard class, other functions, etc.) remains the same.
# Ensure this `apply_global_styles()` function is called in `Dashboard.run()` as before.
