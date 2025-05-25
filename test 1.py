# Prophealth_3.py (Temporary Test Content)
import streamlit as st
import sys
import pandas # Just to check a common import

st.set_page_config(page_title="Test App", layout="wide")

st.title("Minimal Test App")
st.write("If you see this, the basic Streamlit setup and Python environment are working.")
st.write(f"Python version: {sys.version}")
st.write(f"Streamlit version: {st.__version__}")
st.write(f"Pandas version: {pandas.__version__}")

print("Minimal test app script has run to completion.", flush=True)
