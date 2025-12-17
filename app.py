import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime, timedelta

# --- CONFIGURATION ---
st.set_page_config(page_title="AutoSage Ecosystem", layout="wide", page_icon="🚗")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .reportview-container { background: #0e1117; }
    .status-critical { color: #ff4b4b; font-weight: bold; }
    .status-warning { color: #ffa700; font-weight: bold; }
    .status-good { color: #21c354; font-weight: bold; }
    .notification-box { 
        padding: 10px; 
        border-radius: 5px; 
        background-color: #262730; 
        border-left: 5px solid #ff4b4b; 
        margin-bottom: 10px;
    }
    .stProgress > div > div > div > div { background-color: #f63366; }
</style>
""", unsafe_allow_html=True)

# --- 1. MOCK DATABASE WITH APPOINTMENTS ---
if 'db' not in st.session_state:
    st.session_state['db'] = {
        "users": {
            "admin": {"password": "123", "role": "admin", "name": "Service Manager (Hero MotoCorp)"},
            "user1": {"password": "123", "role": "user", "name": "Rahul Sharma", "cars": ["MH-01-AB-1234", "DL-3C-XY-9876"]},
            "user2": {"password": "123", "role": "user", "name": "Priya Verma", "cars": ["KA-05-ZZ-5555"]}
        },
        "vehicles": {
            "MH-01-AB-1234": {
                "model": "Mahindra XUV700",
                "owner": "user1",
                "status": "Critical",
                "health_score": 45,
                "mileage": "45,230 km",
                "history": [
                    {"date": "2024-12-10", "issue": "Fuel Pump Vibration", "action": "Sensor Alert Triggered", "status": "Pending"},
                ],
                "notifications": ["🚨 CRITICAL: Fuel pump failure imminent. Book immediately."]
            },
            "DL-3C-XY-9876": {
                "model": "Hero Splendor+ XTEC",
                "owner": "user1",
                "status": "Good",
                "health_score": 98,
                "mileage": "12,100 km",
                "history": [],
                "notifications": []
            },
            "KA-05-ZZ-5555": {
                "model": "Tata Nexon EV",
                "owner": "user2",
                "status": "Warning",
                "health_score": 78,
                "mileage": "22,500 km",
                "history": [],
                "notifications": ["⚠️ UPDATE: Software update available for BMS."]
            }
        },
        # NEW: Appointment Checklist Tracker
        "appointments": [
            {"id": 101, "vin": "MH-01-AB-1234", "owner": "Rahul Sharma", "service": "Fuel Pump Inspection", "time": "10:00 AM", "status": "Scheduled"},
            {"id": 102, "vin": "KA-05-ZZ-5555", "owner": "Priya Verma", "service": "BMS Update", "time": "11:30 AM", "status": "Arrived"},
            {"id": 103, "vin": "MH-12-TEST-00", "owner": "Amit Singh", "service": "General Service", "time": "02:00 PM", "status": "Completed"}
        ]
    }

# --- 2. AUTHENTICATION ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None

def login():
    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown("## 🔐 AutoSage Login")
        st.markdown("Enter your credentials to access the ecosystem.")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            users = st.session_state['db']['users']
            if username in users and users[username]['password'] == password:
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = users[username]['role']
                st.session_state['current_user'] = username
                st.rerun()
            else:
                st.error("Invalid credentials")
        
        st.markdown("---")
        st.caption("Try: `admin`/`123` or `user1`/`123`")

    with col2:
        st.info("ℹ️ **New Feature Update:** Real-time Service Tracking & Cost Estimation are now live.")

def logout():
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None
    st.session_state['current_user'] = None
    st.rerun()

# --- 3. ADMIN PORTAL (ENHANCED) ---
def admin_portal():
    st.title("🛡️ Admin Command Center")
    st.markdown(f"User: **{st.session_state['db']['users']['admin']['name']}**")
    
    tab1, tab2, tab3 = st.tabs(["📋 Service Bay Checklist", "📡 Fleet Overview", "📈 Analytics"])
    
    # --- NEW FEATURE: CHECKLIST ---
    with tab1:
        st.subheader("📅 Today's Appointments & Arrivals")
        st.caption("Mark users as 'Arrived' when they enter the service center.")
        
        appointments = st.session_state['db']['appointments']
        
        for i, appt in enumerate(appointments):
            c1, c2, c3, c4, c5 = st.columns([2, 2, 3, 2, 2])
            c1.write(f"**{appt['time']}**")
            c2.write(appt['owner'])
            c3.write(f"{appt['service']} ({appt['vin']})")
            
            # Status Badge logic
            if appt['status'] == "Scheduled":
                c4.warning("⏳ Scheduled")
            elif appt['status'] == "Arrived":
                c4.info("🚙 In Service Bay")
            elif appt['status'] == "Completed":
                c4.success("✅ Ready for Pickup")
            
            # Action Buttons
            with c5:
                if appt['status'] == "Scheduled":
                    if st.button(f"Mark Arrived", key=f"btn_arr_{i}"):
                        appt['status'] = "Arrived"
                        st.rerun()
                elif appt['status'] == "Arrived":
                    if st.button(f"Mark Complete", key=f"btn_comp_{i}"):
                        appt['status'] = "Completed"
                        st.rerun()
                else:
                    st.write("---")

    with tab2:
        st.markdown("### 📡 Global Fleet Health")
        vehicles = st.session_state['db']['vehicles']
        
        # Simple stats
        crit_count = sum(1 for v in vehicles.values() if v['status'] == 'Critical')
        st.metric("Vehicles Requiring Immediate Attention", crit_count, delta="High Priority", delta_color="inverse")
        
        # Fleet Table
        fleet_data = [{"VIN": k, "Model": v['model'], "Status": v['status'], "Score": v['health_score']} for k, v in vehicles.items()]
        st.dataframe(pd.DataFrame(fleet_data), use_container_width=True)

    with tab3:
        st.subheader("💡 AI Insights")
        st.bar_chart({"Fuel Pump": 45, "Battery": 30, "Tires": 15, "Brakes": 10})
        st.caption("Most Frequent Component Failures (Last 30 Days)")

# --- 4. USER PORTAL (ENHANCED) ---
def user_portal():
    user_id = st.session_state['current_user']
    user_data = st.session_state['db']['users'][user_id]
    
    st.title(f"👋 Welcome, {user_data['name']}")
    
    # Check for active appointments for this user
    user_appts = [a for a in st.session_state['db']['appointments'] if a['owner'] == user_data['name']]
    
    # --- NEW FEATURE: LIVE TRACKER ---
    if user_appts:
        latest = user_appts[0] # Just showing the first one for demo
        st.markdown("### 🚙 Live Service Tracker")
        st.info(f"Upcoming Service: **{latest['service']}** at {latest['time']}")
        
        # Progress Bar Logic
        if latest['status'] == "Scheduled":
            st.progress(10, text="Status: Booking Confirmed (Waiting for Arrival)")
        elif latest['status'] == "Arrived":
            st.progress(60, text="Status: Vehicle in Bay (Work in Progress)")
        elif latest['status'] == "Completed":
            st.progress(100, text="Status: Ready for Pickup! 🏁")
            st.balloons()

    # Tabs
    tab1, tab2, tab3 = st.tabs(["🚗 My Garage", "💰 Cost Estimator", "🔔 Alerts"])

    with tab1:
        selected_vin = st.selectbox("Select Vehicle", user_data['cars'])
        car = st.session_state['db']['vehicles'][selected_vin]
        
        c1, c2 = st.columns([3, 1])
        c1.metric(label="Vehicle Health Score", value=f"{car['health_score']}/100", delta=car['status'])
        c2.metric("Odometer", car['mileage'])
        
        if car['status'] == "Critical":
            st.error("⚠️ Critical Issues Detected. Please check Alerts tab.")

    # --- NEW FEATURE: COST ESTIMATOR ---
    with tab2:
        st.subheader("🧮 AI Repair Cost Estimator")
        st.write("Select a potential issue to see estimated costs based on your car model.")
        
        part = st.selectbox("Select Component", ["Fuel Pump", "Brake Pads", "Battery Replacement", "General Service"])
        
        if st.button("Calculate Estimate"):
            with st.spinner("AI Analysis in progress..."):
                time.sleep(1)
            
            costs = {
                "Fuel Pump": ("₹12,000 - ₹15,000", "High Urgency"),
                "Brake Pads": ("₹2,500 - ₹4,000", "Medium Urgency"),
                "Battery Replacement": ("₹6,000 - ₹8,500", "Medium Urgency"),
                "General Service": ("₹4,500", "Routine")
            }
            
            est, urg = costs[part]
            st.success(f"**Estimated Cost:** {est}")
            st.caption(f"Urgency Level: {urg}")
            st.info("💡 **AutoSage Tip:** Booking via the app saves you 15% on labor charges.")

    with tab3:
        st.subheader("🔔 Active Notifications")
        for vin in user_data['cars']:
            notifs = st.session_state['db']['vehicles'][vin]['notifications']
            if notifs:
                for n in notifs:
                    st.markdown(f"<div class='notification-box'>{n}</div>", unsafe_allow_html=True)
            else:
                st.caption(f"No alerts for {vin}")

# --- 5. MAIN ROUTER ---
def main():
    if not st.session_state['logged_in']:
        login()
    else:
        # Sidebar
        st.sidebar.title("AutoSage Nav")
        st.sidebar.write(f"Logged in as: **{st.session_state['user_role'].upper()}**")
        if st.sidebar.button("🚪 Logout"):
            logout()
            
        st.sidebar.markdown("---")
        
        if st.session_state['user_role'] == 'admin':
            admin_portal()
        else:
            user_portal()

if __name__ == "__main__":
    main()
