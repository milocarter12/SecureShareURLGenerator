import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Configure the page
st.set_page_config(page_title="Time Tracking Dashboard", layout="wide")

# Health check response
if st.query_params.get("health") == ["check"]:
    st.json({"status": "ok"})
    st.stop()

# Password for authentication
PASSWORD = "3987q89deb789dnq98a8dnal2neoiedn1209e"

# Rest of your existing code...
# [Previous code remains unchanged]
