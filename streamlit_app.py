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
    {"date": "10/24", "hours": 4.77, "day": "Thu", "formattedTime": "4:46", "hourlyPay": True},
    {"date": "10/25", "hours": 3.02, "day": "Fri", "formattedTime": "3:01", "hourlyPay": True}
]

# Constants
HOURLY_RATE = 4

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'view_type' not in st.session_state:
    st.session_state.view_type = 'weekly'
if 'current_date' not in st.session_state:
    st.session_state.current_date = datetime.now()
if 'payment_history' not in st.session_state:
    st.session_state.payment_history = []
if 'time_data' not in st.session_state:
    st.session_state.time_data = TIME_DATA.copy()

def login():
    st.title("Time Tracking Dashboard")
    password = st.text_input("Enter Password", type="password")
    if st.button("Login"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid password")

def calculate_remaining_hours(paid_hours):
    hourly_entries = [entry for entry in st.session_state.time_data if entry['hourlyPay']]
    total_hours = sum(entry['hours'] for entry in hourly_entries)
    remaining_hours = max(0, total_hours - paid_hours)
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

def filter_data_by_period(df):
    current_date = st.session_state.current_date
    df['datetime'] = pd.to_datetime(df['date'] + '/2024', format='%m/%d/%Y')
    
    if st.session_state.view_type == 'weekly':
        start_date = current_date - timedelta(days=current_date.weekday())
        end_date = start_date + timedelta(days=6)
    elif st.session_state.view_type == 'monthly':
        start_date = current_date.replace(day=1)
        end_date = (start_date.replace(month=start_date.month % 12 + 1, day=1) - timedelta(days=1))
    else:
        start_date = current_date.replace(month=1, day=1)
        end_date = current_date.replace(month=12, day=31)
    
    dates = pd.date_range(start=start_date, end=end_date)
    date_range_df = pd.DataFrame({
        'date': dates.strftime('%m/%d'),
        'day': dates.strftime('%a'),
        'hours': 0,
        'hourlyPay': True,
        'formattedTime': '0:00'
    })
    
    result = pd.merge(
        date_range_df,
        df[['date', 'hours', 'hourlyPay', 'formattedTime']],
        on='date',
        how='left'
    )
    
    result['hours'] = result['hours_y'].fillna(result['hours_x'])
    result['hourlyPay'] = result['hourlyPay_y'].fillna(result['hourlyPay_x'])
    result['formattedTime'] = result['formattedTime_y'].fillna(result['formattedTime_x'])
    
    result = result.drop(columns=[col for col in result.columns if col.endswith('_x') or col.endswith('_y')])
    
    return result

def create_time_chart(df):
    filtered_df = filter_data_by_period(df.copy())
    
    fig = px.bar(
        filtered_df,
        x='date',
        y='hours',
        color='hourlyPay',
        labels={'hours': 'Hours', 'date': 'Date'},
        color_discrete_map={True: '#9333ea', False: '#94a3b8'},
        title='Time Overview'
    )
    
    fig.update_layout(
        showlegend=False,
        xaxis_tickangle=-45,
        xaxis={'tickmode': 'array', 'ticktext': filtered_df['date'] + '\n' + filtered_df['day']}
    )
    
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
    df = pd.DataFrame(st.session_state.time_data)
    
    # Time chart
    st.plotly_chart(create_time_chart(df), use_container_width=True)

    # Payment Summary and Time Breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Payment Summary")
        total_hours, remaining_hours = calculate_remaining_hours(
            sum(payment['amount'] for payment in st.session_state.payment_history)
        )
        
        # Payment calculator
        st.markdown("##### Make a Payment")
        payment_amount = st.number_input(
            "Hours to pay:",
            min_value=0.0,
            max_value=remaining_hours,
            value=remaining_hours,
            step=0.5,
            help="Enter the number of hours you want to pay for"
        )
        
        if st.button("Submit Payment"):
            if payment_amount > 0:
                payment = {
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'amount': payment_amount,
                    'total': payment_amount * HOURLY_RATE
                }
                st.session_state.payment_history.append(payment)
                st.success(f"Payment recorded: {payment_amount} hours (${payment_amount * HOURLY_RATE:.2f})")
                st.rerun()

        # Add new time entry
        st.markdown("##### Add Time Entry")
        with st.form("add_time_entry"):
            cols = st.columns([2, 2, 1])
            with cols[0]:
                entry_date = st.date_input(
                    "Date",
                    value=datetime.now(),
                    min_value=datetime(2024, 1, 1),
                    max_value=datetime(2024, 12, 31)
                )
            with cols[1]:
                hours = st.number_input(
                    "Hours Worked",
                    min_value=0.0,
                    max_value=24.0,
                    value=0.0,
                    step=0.25,
                    help="Enter the number of hours worked (in decimal format)"
                )
            with cols[2]:
                hourly_pay = st.checkbox("Hourly Pay", value=True)
            
            submitted = st.form_submit_button("Add Entry")
            if submitted and hours > 0:
                # Format the entry
                formatted_hours = f"{int(hours)}:{int((hours % 1) * 60):02d}"
                new_entry = {
                    "date": entry_date.strftime("%m/%d"),
                    "hours": hours,
                    "day": entry_date.strftime("%a"),
                    "formattedTime": formatted_hours,
                    "hourlyPay": hourly_pay
                }
                
                # Add to time data
                st.session_state.time_data.append(new_entry)
                st.success(f"Added {hours} hours for {new_entry['date']}")
                st.rerun()

        # Visual payment progress
        st.markdown("##### Payment Progress")
        paid_hours = sum(payment['amount'] for payment in st.session_state.payment_history)
        
        # Progress bar showing paid vs total hours
        if total_hours > 0:
            progress = min(1.0, paid_hours / total_hours)
            st.progress(progress)
            
            # Color-coded hour breakdown
            st.markdown(f'''
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <div style="color: #28a745">✓ Paid: {paid_hours:.2f}h (${paid_hours * HOURLY_RATE:.2f})</div>
                <div style="color: #dc3545">○ Remaining: {remaining_hours:.2f}h (${remaining_hours * HOURLY_RATE:.2f})</div>
            </div>
            ''', unsafe_allow_html=True)

        # Payment history log
        st.markdown("##### Payment History")
        if not st.session_state.payment_history:
            st.info("No payments recorded yet")
        else:
            for payment in reversed(st.session_state.payment_history):
                st.markdown(f'''
                <div style="padding: 10px; border-left: 3px solid #28a745; margin-bottom: 10px;">
                    <div style="color: #666; font-size: 0.8em;">{payment['date']}</div>
                    <div>{payment['amount']} hours paid (${payment['total']:.2f})</div>
                </div>
                ''', unsafe_allow_html=True)

    with col2:
        st.subheader("Detailed Time Breakdown")
        for entry in st.session_state.time_data:
            with st.container():
                cols = st.columns([3, 2])
                with cols[0]:
                    st.markdown(f"**{entry['day']} {entry['date']}**")
                    st.markdown(f"{entry['formattedTime']}")
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
