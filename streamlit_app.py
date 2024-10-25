import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Configure the page
st.set_page_config(page_title="Time Tracking Dashboard", layout="wide")

# Password for authentication
PASSWORD = "3987q89deb789dnq98a8dnal2neoiedn1209e"

# Time tracking data
TIME_DATA = [
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

# Constants
HOURLY_RATE = 4
PAID_HOURS = 4

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'view_type' not in st.session_state:
    st.session_state.view_type = 'weekly'
if 'current_date' not in st.session_state:
    st.session_state.current_date = datetime.now()

def login():
    st.title("Time Tracking Dashboard")
    password = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid password")

def calculate_remaining_hours():
    hourly_entries = [entry for entry in TIME_DATA if entry['hourlyPay']]
    total_hours = sum(entry['hours'] for entry in hourly_entries)
    remaining_hours = total_hours - PAID_HOURS
    return total_hours, remaining_hours

def format_time_period():
    date = st.session_state.current_date
    if st.session_state.view_type == 'weekly':
        start = date - timedelta(days=date.weekday())
        end = start + timedelta(days=6)
        return f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"
    elif st.session_state.view_type == 'monthly':
        return date.strftime('%B %Y')
    else:
        return date.strftime('%Y')

def create_time_chart(df):
    fig = px.bar(
        df,
        x='date',
        y='hours',
        color='hourlyPay',
        labels={'hours': 'Hours', 'date': 'Date'},
        color_discrete_map={True: '#9333ea', False: '#94a3b8'},
        title='Time Overview'
    )
    fig.update_layout(showlegend=False)
    return fig

def dashboard():
    # Navigation bar
    col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 1, 1])
    with col1:
        st.session_state.view_type = st.selectbox(
            "View",
            ['weekly', 'monthly', 'yearly'],
            key='view_select'
        )
    with col2:
        if st.button("← Previous"):
            if st.session_state.view_type == 'weekly':
                st.session_state.current_date -= timedelta(days=7)
            elif st.session_state.view_type == 'monthly':
                st.session_state.current_date = st.session_state.current_date.replace(
                    day=1) - timedelta(days=1)
            else:
                st.session_state.current_date = st.session_state.current_date.replace(
                    year=st.session_state.current_date.year - 1)
    with col3:
        st.markdown(f"### {format_time_period()}")
    with col4:
        if st.button("Next →"):
            if st.session_state.view_type == 'weekly':
                st.session_state.current_date += timedelta(days=7)
            elif st.session_state.view_type == 'monthly':
                next_month = st.session_state.current_date.replace(
                    day=28) + timedelta(days=4)
                st.session_state.current_date = next_month.replace(day=1)
            else:
                st.session_state.current_date = st.session_state.current_date.replace(
                    year=st.session_state.current_date.year + 1)
    with col5:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

    # Convert time data to DataFrame
    df = pd.DataFrame(TIME_DATA)
    
    # Time chart
    st.plotly_chart(create_time_chart(df), use_container_width=True)

    # Payment Summary and Time Breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Payment Summary")
        total_hours, remaining_hours = calculate_remaining_hours()
        
        summary_container = st.container()
        with summary_container:
            st.markdown("##### Hourly Pay Structure ($4/hour)")
            st.markdown(f"**Total Hours Worked:** {total_hours:.2f} hours")
            st.markdown(f"**Hours Already Paid:** {PAID_HOURS} hours (${PAID_HOURS * HOURLY_RATE:.2f})")
            st.markdown(f"**Remaining Hours to Pay:** {remaining_hours:.2f} hours")
            st.markdown("---")
            st.markdown(f"**Amount Still Owed:** ${remaining_hours * HOURLY_RATE:.2f}")

    with col2:
        st.subheader("Detailed Time Breakdown")
        for entry in TIME_DATA:
            with st.container():
                cols = st.columns([3, 2])
                with cols[0]:
                    st.markdown(f"**{entry['day']} {entry['date']}**")
                    st.markdown(f"{entry['formattedTime']}" + 
                              (" (Performance Based)" if not entry['hourlyPay'] else ""))
                with cols[1]:
                    if entry['hourlyPay']:
                        st.markdown(f"**${entry['hours'] * HOURLY_RATE:.2f}**")

def main():
    if not st.session_state.authenticated:
        login()
    else:
        dashboard()

if __name__ == "__main__":
    main()
