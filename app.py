import streamlit as st
import pycountry
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import datetime as dt
from zoneinfo import ZoneInfo
from bazi_calculator import calculate_bazi_with_solar_correction
from display_helpers import display_pillars_table, display_element_star_meter, display_element_score_breakdown

# ----- Streamlit Page Config -----
st.set_page_config(page_title="MyElement - BaZi Analyzer", page_icon="🌿", layout="centered")

# ----- Hero Banner -----
st.markdown(
    """
    <div style='background: linear-gradient(90deg, #b1f0dc 0%, #f2edc6 100%); border-radius:14px; padding: 30px 20px 16px 20px; margin-bottom:20px; box-shadow:0 2px 12px #ddebe7;'>
        <h1 style='color: #20403c; margin-bottom: 0.5rem;'>🌿 MyElement</h1>
        <div style='font-size: 1.2rem; color: #456c67; font-weight:500; margin-bottom:4px;'>Discover Your Elemental Personality with BaZi</div>
        <img src="https://cdn-icons-png.flaticon.com/512/2601/2601236.png" width="66" style="margin-top:10px; margin-bottom:-32px;" />
    </div>
    """,
    unsafe_allow_html=True
)

# ----- Input Card -----
st.markdown(
    """
    <div style='background-color: #f6fbf9; border-radius:14px; padding: 22px 18px 5px 18px; box-shadow: 0 1px 10px #e0edea; margin-bottom: 22px;'>
    """,
    unsafe_allow_html=True
)
name = st.text_input("Name")
gender = st.selectbox("Gender", ["Male", "Female", "Other"])

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
col1, col2 = st.columns(2)
with col1:
    hour = st.selectbox("Hour (H)", list(range(0, 24)), index=12)
with col2:
    minute = st.selectbox("Minute (M)", list(range(0, 60)), index=0)
birth_time = dt.time(hour, minute)

st.caption("Tip: Country is enough for most cases; city support coming soon!")
st.markdown("</div>", unsafe_allow_html=True)

# ----- Button and Results -----
if st.button("✨ Generate My Elemental Star Meter"):
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

                st.markdown("---")
                display_pillars_table(result)
                display_element_score_breakdown(result)
                st.markdown(("---"))
                display_element_star_meter(result)
                st.markdown("---")

                st.info("Your birth details are private and never stored on our server.")

                st.markdown(
                    f"""
                    <div style='text-align:center; color:#78908b; margin-top:16px; font-size:1.05em;'>
                        Standard Time: <b>{result['standard_dt'].strftime('%Y-%m-%d %H:%M')}</b> &bull;
                        Solar-corrected: <b>{result['solar_dt'].strftime('%Y-%m-%d %H:%M')}</b> &bull;
                        Timezone: <b>{timezone_str}</b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    except Exception as e:
        st.error(f"❌ Something went wrong: {e}")

# ----- Footer -----
st.markdown(
    """
    <hr>
    <div style='text-align:center; color: #a8b6b3; font-size:0.95em; margin-top:10px;'>
    Made with ❤️ by MyElement • © 2025
    </div>
    """,
    unsafe_allow_html=True
)