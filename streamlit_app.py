import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Configure the page
st.set_page_config(
    page_title="Time Tracking Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Health check response
if "health" in st.query_params and st.query_params["health"] == "check":
    st.json({"status": "ok"})
    st.stop()

# Password for authentication
PASSWORD = "3987q89deb789dnq98a8dnal2neoiedn1209e"

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def load_time_data():
    return [
        {"date": "10/17", "hours": 0.2, "day": "Thu", "formattedTime": "0:12", "hourlyPay": True},
        {"date": "10/18", "hours": 0.2, "day": "Fri", "formattedTime": "0:12", "hourlyPay": True},
        {"date": "10/19", "hours": 3.02, "day": "Sat", "formattedTime": "3:01", "hourlyPay": True},
        {"date": "10/20", "hours": 3, "day": "Sun", "formattedTime": "3:00", "hourlyPay": True},
        {"date": "10/21", "hours": 9.55, "day": "Mon", "formattedTime": "9:33", "hourlyPay": True},
        {"date": "10/22", "hours": 2.33, "day": "Tue", "formattedTime": "2:20", "hourlyPay": True},
        {"date": "10/23", "hours": 4.4, "day": "Wed", "formattedTime": "4:24", "hourlyPay": True},
        {"date": "10/24", "hours": 4.77, "day": "Thu", "formattedTime": "4:46", "hourlyPay": False},
        {"date": "10/25", "hours": 3.02, "day": "Fri", "formattedTime": "3:01", "hourlyPay": False}
    ]

def login():
    st.title("Time Tracking Dashboard")
    password = st.text_input("Enter Password", type="password")
    
    if st.button("Login"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")

def create_time_chart(df):
    fig = px.bar(
        df,
        x="date",
        y="hours",
        color="hourlyPay",
        color_discrete_map={True: "#9333ea", False: "#94a3b8"},
        labels={"date": "Date", "hours": "Hours", "hourlyPay": "Hourly Pay"},
        title="Time Overview"
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title_x=0.5
    )
    return fig

def dashboard():
    time_data = load_time_data()
    df = pd.DataFrame(time_data)
    
    hourly_rate = 4
    paid_hours = 4
    
    remaining_hourly_hours = sum(entry["hours"] for entry in time_data if entry["hourlyPay"]) - paid_hours
    remaining_owed = remaining_hourly_hours * hourly_rate
    
    st.title("Time Tracking Dashboard")
    
    # Time Overview
    st.plotly_chart(create_time_chart(df), use_container_width=True)
    
    # Payment Summary
    st.subheader("Payment Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Hours Worked", f"{(remaining_hourly_hours + paid_hours):.2f} hours")
        st.metric("Hours Already Paid", f"{paid_hours} hours (${paid_hours * hourly_rate:.2f})")
    
    with col2:
        st.metric("Remaining Hours to Pay", f"{remaining_hourly_hours:.2f} hours")
        st.metric("Amount Still Owed", f"${remaining_owed:.2f}")
    
    # Detailed Time Breakdown
    st.subheader("Detailed Time Breakdown")
    for entry in time_data:
        with st.expander(f"{entry['day']} {entry['date']} - {entry['formattedTime']}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write("Hours:", entry['hours'])
                st.write("Pay Type:", "Hourly" if entry['hourlyPay'] else "Performance Based")
            with col2:
                if entry['hourlyPay']:
                    st.write("Amount:", f"${entry['hours'] * hourly_rate:.2f}")

def main():
    if not st.session_state.authenticated:
        login()
    else:
        dashboard()

if __name__ == "__main__":
    main()
