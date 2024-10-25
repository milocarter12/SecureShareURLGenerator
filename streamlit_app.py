import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import requests
from plotly.subplots import make_subplots

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'current_view' not in st.session_state:
    st.session_state.current_view = 'weekly'

if 'word_count_data' not in st.session_state:
    st.session_state.word_count_data = []

if 'word_count_logs' not in st.session_state:
    st.session_state.word_count_logs = []

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

def get_location_from_ip():
    try:
        response = requests.get('https://ipapi.co/json/')
        if response.status_code == 200:
            data = response.json()
            city = data.get('city', 'Unknown City')
            country = data.get('country_name', 'Unknown Country')
            return f"{city}, {country}"
    except:
        pass
    return "Local Development"

def login():
    st.title("Time Tracking Dashboard")
    password = st.text_input("Enter Password", type="password")
    
    if st.button("Login"):
        if password == "3987q89deb789dnq98a8dnal2neoiedn1209e":
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("Invalid password")

def create_time_chart():
    hourly_data = [x for x in TIME_DATA if x['hourlyPay']]
    performance_data = [x for x in TIME_DATA if not x['hourlyPay']]
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Hourly Pay bars
    fig.add_trace(
        go.Bar(
            name="Hourly Pay",
            x=[d['date'] for d in hourly_data],
            y=[d['hours'] for d in hourly_data],
            marker_color='#9333ea'
        ),
        secondary_y=False
    )
    
    # Performance Based bars
    fig.add_trace(
        go.Bar(
            name="Performance Based",
            x=[d['date'] for d in performance_data],
            y=[d['hours'] for d in performance_data],
            marker_color='#94a3b8'
        ),
        secondary_y=False
    )
    
    # Word Count line
    if st.session_state.word_count_data:
        fig.add_trace(
            go.Scatter(
                name="Word Count",
                x=[d['date'] for d in st.session_state.word_count_data],
                y=[d['totalWords'] for d in st.session_state.word_count_data],
                line=dict(color='#3b82f6')
            ),
            secondary_y=True
        )
    
    fig.update_layout(
        title="Time Overview",
        barmode='group',
        height=400,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    fig.update_yaxes(title_text="Hours", secondary_y=False)
    fig.update_yaxes(title_text="Word Count", secondary_y=True)
    
    return fig

def format_date(date):
    return date.strftime("%m/%d")

def main_dashboard():
    st.title("Time Tracking Dashboard")
    
    # View type selector
    view_type = st.selectbox(
        "View",
        ["weekly", "monthly", "yearly"],
        key="view_type"
    )
    
    # Time Overview Chart
    st.plotly_chart(create_time_chart(), use_container_width=True)
    
    # Word Count Tracking
    with st.expander("Word Count Tracking", expanded=True):
        with st.form("word_count_form"):
            date = st.date_input("Date")
            total_words = st.number_input("Total Words", min_value=0)
            price_per_word = st.number_input("Price per Word ($)", min_value=0.0, step=0.001, format="%.3f")
            
            if st.form_submit_button("Add Word Count"):
                entry = {
                    'date': format_date(date),
                    'totalWords': total_words,
                    'pricePerWord': price_per_word,
                    'totalAmount': total_words * price_per_word,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'location': get_location_from_ip()
                }
                
                st.session_state.word_count_data.append(entry)
                st.session_state.word_count_logs.append(entry)
                st.success("Word count added successfully!")
                st.experimental_rerun()
    
    # Activity Log
    with st.expander("Activity Log", expanded=True):
        if st.session_state.word_count_logs:
            log_data = [{
                'Timestamp': log['timestamp'],
                'Location': log['location'],
                'Date': log['date'],
                'Words': log['totalWords'],
                'Amount': f"${log['totalAmount']:.2f}"
            } for log in st.session_state.word_count_logs]
            
            st.table(log_data)
        else:
            st.info("No activity logged yet")
    
    # Payment Summary
    hourly_rate = 4
    paid_hours = 4
    remaining_hourly_hours = sum(day['hours'] for day in TIME_DATA 
                               if day['hourlyPay'] and day['date'] not in ['10/24', '10/25']) - paid_hours
    remaining_owed = remaining_hourly_hours * hourly_rate
    
    with st.expander("Payment Summary", expanded=True):
        st.write("### Hourly Pay Structure ($4/hour)")
        col1, col2 = st.columns(2)
        col1.metric("Total Hours Worked (Hourly)", f"{(remaining_hourly_hours + paid_hours):.2f} hours")
        col2.metric("Hours Already Paid", f"{paid_hours} hours (${paid_hours * hourly_rate:.2f})")
        col1.metric("Remaining Hours to Pay", f"{remaining_hourly_hours:.2f} hours")
        col2.metric("Amount Still Owed", f"${remaining_owed:.2f}")
        
        st.info("Hours tracked on Oct 24-25 (7h 47m total) are under the new performance-based structure and not calculated at hourly rate.")
    
    # Time Breakdown
    with st.expander("Time Breakdown", expanded=True):
        for entry in TIME_DATA:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{entry['day']} {entry['date']}**")
                    st.write(f"{entry['formattedTime']}{' (Performance Based)' if not entry['hourlyPay'] else ''}")
                with col2:
                    if entry['hourlyPay']:
                        st.write(f"**${entry['hours'] * hourly_rate:.2f}**")

if __name__ == "__main__":
    if not st.session_state.authenticated:
        login()
    else:
        main_dashboard()
