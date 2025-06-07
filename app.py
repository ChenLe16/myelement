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

# ── Session helpers ───────────────────────────────────────────
def _init_state():
    """Ensure all the keys we use later exist in st.session_state."""
    defaults = dict(
        email_submitted=False,
        submitted_email="",
        awaiting_confirm=False,
        pending_inputs={},
        bazi_result=None,
        timezone_str=""
    )
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

# ── Calc helper ───────────────────────────────────────────────
def _compute_bazi_result(dob: dt.date, btime: dt.time, country: str):
    """
    Returns (result_dict, timezone_str) or (None, error_msg).
    Handles geo lookup, timezone, solar‑correction BaZi calc.
    """
    try:
        geolocator = Nominatim(user_agent="my_bazi_app", timeout=5)
        tf = TimezoneFinder()
        location = geolocator.geocode(country)
        if not location:
            return None, "Country not found."
        tz_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)
        if not tz_str:
            return None, "Could not determine timezone."
        local_dt = dt.datetime.combine(dob, btime).replace(tzinfo=ZoneInfo(tz_str))
        utc_off = local_dt.utcoffset().total_seconds() / 3600
        result = calculate_bazi_with_solar_correction(dob, btime, location.longitude, utc_off)
        return (result, tz_str)
    except Exception as err:
        return None, f"Error: {err}"

st.set_page_config(
    page_title="MyElement | Discover Your Elemental Self",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Landing/Hero section
display_hero_section()

# Initialise session once per user
_init_state()

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

    # Accuracy hint
    st.markdown(
        "<div style='text-align: center; color: #6c757d; font-size: 0.97em;'>"
        "⏱ <b>Exact birth time matters.</b> Even a five‑minute difference can "
        "shift the Hour Pillar and change your results."
        "</div>",
        unsafe_allow_html=True
    )

    display_privacy_note()

    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        generate_clicked = st.form_submit_button("✨ Generate My Elemental Star Meter")
   
st.markdown("</div>", unsafe_allow_html=True)

# ---- Handle Generate logic & confirmation ----
if generate_clicked:
    if not name.strip():
        st.warning("Please enter your name before continuing.")
    else:
        st.session_state["awaiting_confirm"] = True

# show confirmation UI when needed
if st.session_state["awaiting_confirm"]:
    st.warning(
        "Are you sure your birth time is accurate? "
        "Even a five‑minute difference can change your result."
    )
    if st.button("✔ Yes, my birth time is accurate — generate my result"):
        birth_time = dt.time(hour, minute)
        bazi, tz_or_err = _compute_bazi_result(dob, birth_time, country)
        if bazi is None:
            st.error(tz_or_err)
        else:
            st.session_state.update(
                dict(
                    bazi_result=bazi,
                    timezone_str=tz_or_err,
                    name=name,
                    gender=gender,
                    country=country,
                    dob=dob,
                    birth_time=birth_time
                )
            )

# 5. Results, Star Meter, Email form
if "bazi_result" in st.session_state and st.session_state["bazi_result"]:
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