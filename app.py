import streamlit as st
import datetime as dt
import re
import pycountry
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
from bazi_calculator import calculate_bazi_with_solar_correction
from display_helpers import display_pillars_table, display_element_star_meter, display_element_score_breakdown, display_time_info
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# 1. CSS and landing section (palette, header, hero, CTA)
st.set_page_config(page_title="MyElement | Discover Your Elemental Self", page_icon="🌿", layout="centered")

st.markdown("""
<div style='display: flex; flex-direction: column; align-items: center; margin-bottom: 38px;'>
    <div style='display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 13px; margin-bottom: 18px;'>
        <span class='my-logo' style='font-weight: 600; font-size: 2.8rem; color: #00B079;'>ME</span>
        <div class='my-title' style='font-size: 2.1rem; font-weight: 700; letter-spacing: 1px; color: #fff;'>MyElement</div>
    </div>
    <div class='hero-title' style='font-size: 2.1rem; font-weight: 700; text-align: center; color: #fff; margin-bottom: 12px;'>
        Turn Birth Data into Actionable Self-Insights
    </div>
    <div class='hero-desc' style='text-align: center; font-size: 1.23rem; color: #B0B5BA; margin-bottom: 30px; max-width: 600px;'>
        Our Five-Element engine converts your birth date and time into a bar-chart of strengths, gaps, and next-step tips—no sign-up, no data stored.
    </div>
    <div style='display: flex; justify-content: center; margin-top: 18px;'>
        <a class='hero-btn' href='#element-form' style='padding: 0.5em 2.1em; font-size: 1.18rem; font-weight: 700; border-radius: 10px; background: #1DBF73; color: white; text-decoration: none; box-shadow: 0 2px 12px #1dbf7322; transition: background 0.2s, outline 0.2s;'>
            Run My Free Analysis
        </a>
    </div>
</div>
<style>
.hero-btn:hover, .hero-btn:focus {
    background: #14975f !important;
    outline: 2px solid #eafff6;
}
</style>
""", unsafe_allow_html=True)

# Inject CSS for the submit button to match hero CTA
st.markdown("""
<style>
    div.stButton > button:first-child {
        padding: 0.5em 2.1em;
        font-size: 1.18rem;
        font-weight: 700;
        border-radius: 10px;
        background: #1DBF73;
        color: white;
        box-shadow: 0 2px 12px #1dbf7322;
        transition: background 0.2s, outline 0.2s;
        border: none;
        cursor: pointer;
    }
    div.stButton > button:first-child:hover, div.stButton > button:first-child:focus {
        background: #14975f !important;
        outline: 2px solid #eafff6;
    }
</style>
""", unsafe_allow_html=True)

# 2. Form Section Anchor
st.markdown("<div id='element-form'></div>", unsafe_allow_html=True)

# 3. Main Input Form (with card background) inside a st.form
st.markdown("<div class='card'>", unsafe_allow_html=True)
with st.form("star_meter_form"):
    name = st.text_input("Name")
    gender = st.selectbox("Gender", ["Male", "Female"])
    country_list = sorted([c.name for c in pycountry.countries])
    country = st.selectbox(
        "Country of Birth",
        country_list,
        index=country_list.index("Malaysia")
    )
    dob = st.date_input(
        "Date of Birth",
        value=dt.date(1990, 1, 1),
        min_value=dt.date(1900, 1, 1),
        max_value=dt.date.today() + dt.timedelta(days=365*2)
    )
    col1, col2 = st.columns([1, 1])
    with col1:
        hour = st.selectbox("Hour (H)", list(range(0, 24)), index=12)
    with col2:
        minute = st.selectbox("Minute (M)", list(range(0, 60)), index=0)
        
    st.markdown(
        "<div style='background: #274559; color: #eaf7fa; border-radius: 8px; padding: 13px 7px; text-align:center; margin-bottom:13px; font-size:1.09em;'>"
        "Your birth details are private and never stored on our server."
        "</div>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        submit_star_meter = st.form_submit_button("✨ Generate My Elemental Star Meter")
   
st.markdown("</div>", unsafe_allow_html=True)

# --- Google Sheets integration helper ---
def append_to_gsheet(data):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = json.loads(st.secrets["google_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("MyElement Leads").sheet1  # Adjust if needed
    sheet.append_row(data)

def is_valid_email(email):
    pattern = r"^[A-Za-z0-9\._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email.strip()) is not None

if "email_submitted" not in st.session_state:
    st.session_state["email_submitted"] = False
if "submitted_email" not in st.session_state:
    st.session_state["submitted_email"] = ""

# 4. Generate Button & BaZi Calculation triggered by form submit
if 'submit_star_meter' in locals() and submit_star_meter:
    birth_time = dt.time(hour, minute)
    try:
        geolocator = Nominatim(user_agent="my_bazi_app", timeout=5)
        tf = TimezoneFinder()
        location = geolocator.geocode(country)
        if not location:
            st.error("Country not found! Try a different spelling.")
        else:
            timezone_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)
            if not timezone_str:
                st.error("Could not determine timezone for this country.")
            else:
                local_dt = dt.datetime.combine(dob, birth_time)
                try:
                    local_dt = local_dt.replace(tzinfo=ZoneInfo(timezone_str))
                    utc_offset = local_dt.utcoffset().total_seconds() / 3600
                except Exception as e:
                    st.error(f"Timezone error: {e}")
                    utc_offset = 8  # fallback

                result = calculate_bazi_with_solar_correction(
                    dob, birth_time, location.longitude, utc_offset
                )
                st.session_state["bazi_result"] = result
                st.session_state["timezone_str"] = timezone_str
                st.session_state["name"] = name
                st.session_state["gender"] = gender
                st.session_state["country"] = country
                st.session_state["dob"] = dob
                st.session_state["birth_time"] = birth_time
    except Exception as e:
        st.error(f"❌ Something went wrong: {e}")

# 5. Results, Star Meter, Email form
if "bazi_result" in st.session_state:
    st.markdown("---")
    display_pillars_table(st.session_state["bazi_result"])
    display_element_score_breakdown(st.session_state["bazi_result"])
    st.markdown("---")
    display_element_star_meter(st.session_state["bazi_result"])
    st.markdown("---")
    display_time_info(st.session_state["bazi_result"], st.session_state["timezone_str"])

    # --- PDF Email Request Section ---
    st.markdown("---")
    with st.form("email_form"):
        st.markdown(
            "<h4 style='text-align:left;'>Get Your Full PDF Report</h4>",
            unsafe_allow_html=True
        )
        email = st.text_input(
            "Enter your email to receive your personalized report and join our newsletter:",
            placeholder="you@email.com"
        ).strip()
        st.markdown(
            "<div style='text-align:left; color:#89acc0; font-size:0.98em;'>"
            "By submitting, you agree to receive your PDF result and occasional updates from us. You can unsubscribe at any time."
            "</div>",
            unsafe_allow_html=True
        )
        send_pdf = st.form_submit_button("Send to my email")
        message = ""
        if send_pdf:
            if is_valid_email(email):
                timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                row = [
                    timestamp,
                    st.session_state.get("name"),
                    email,
                    st.session_state.get("country"),
                    st.session_state.get("dob").strftime("%Y-%m-%d"),
                    st.session_state.get("birth_time").strftime("%H:%M"),
                    st.session_state.get("gender"),
                ]
                try:
                    append_to_gsheet(row)
                    message = "success"
                except Exception as e:
                    message = f"error:{e}"
            else:
                message = "warning"
        if message == "success":
            st.success("✅ Row sent to Google Sheet!")
            st.info(f"Email submitted: **{email}**")
        elif message.startswith("error:"):
            st.error("Unable to log to Google Sheet: " + message[6:])
        elif message == "warning":
            st.warning("Please enter a valid email address.")

# 6. Footer
st.markdown(
    """
    <hr>
    <div style='text-align:center; color: #a8b6b3; font-size:0.95em; margin-top:10px;'>
    Made with ❤️ by MyElement • © 2025
    </div>
    """,
    unsafe_allow_html=True
)