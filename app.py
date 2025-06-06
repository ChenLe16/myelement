import streamlit as st
import datetime as dt
import pycountry
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
import hashlib
from bazi_calculator import calculate_bazi_with_solar_correction
from display_helpers import (
    display_pillars_table, display_element_star_meter, display_element_score_breakdown, display_time_info,
    display_hero_section, display_footer, display_privacy_note
)
from gsheet_helpers import append_to_gsheet, is_valid_email

st.set_page_config(
    page_title="MyElement | Discover Your Elemental Self",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Landing/Hero section
display_hero_section()

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
        
    display_privacy_note()

    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        submit_star_meter = st.form_submit_button("✨ Generate My Elemental Star Meter")
   
st.markdown("</div>", unsafe_allow_html=True)

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
        consent = st.checkbox(
            "I allow MyElement to save my birth data and email so it can generate "
            "and send my full PDF report. I can delete this data at any time.",
            value=False
        )
        st.markdown(
            "<div style='text-align:left; color:#89acc0; "
            "font-size:0.98em;'>"
            "Your detailed PDF is prepared by a human analyst and arrives by "
            "<strong>email within 48 hours (Mon-Fri)</strong>. "
            "We only store your data for that purpose."
            "</div>",
            unsafe_allow_html=True
        )
        send_pdf = st.form_submit_button(
            "Send to my email",
            disabled=st.session_state.get("email_submitted", False)
        )
        message = ""
        if send_pdf:
            if not consent:
                message = "consent"
            elif not is_valid_email(email):
                message = "warning"
            else:
                timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Generate a unique key using email, dob, and birth_time
                key_source = f"{email}-{st.session_state.get('dob').strftime('%Y-%m-%d')}-{st.session_state.get('birth_time').strftime('%H:%M')}"
                key = hashlib.sha256(key_source.encode("utf-8")).hexdigest()
                row = [
                    key,
                    timestamp,
                    st.session_state.get("name"),
                    email,
                    st.session_state.get("country"),
                    st.session_state.get("dob").strftime("%Y-%m-%d"),
                    st.session_state.get("birth_time").strftime("%H:%M"),
                    st.session_state.get("gender"),
                ]
                try:
                    result = append_to_gsheet(row)  # expected returns: "success" | "duplicate" | None
                    if result in (None, False, "duplicate"):
                        # Row already exists – treat as duplicate
                        st.session_state["email_submitted"] = True
                        message = "duplicate"
                    else:
                        st.session_state["email_submitted"] = True
                        message = "success"
                except Exception as e:
                    message = f"error:{e}"
        if message == "success":
            st.success(
                "✅ Request received! Your personalised PDF will land in your inbox "
                "within 48 hours. If you don’t see it, check spam or write us at "
                "hello@myelement.app."
            )
            st.info(f"Email submitted: **{email}**")
        elif message == "duplicate":
            st.info("Looks like we already have your request — your PDF is on its way!")
        elif message.startswith("error:"):
            st.error("Unable to log to Google Sheet: " + message[6:])
        elif message == "warning":
            st.warning("Please enter a valid email address.")
        elif message == "consent":
            st.warning("Please tick the consent box to let us store your details.")

# 6. Footer
display_footer()