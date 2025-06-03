import streamlit as st
import pycountry
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import datetime as dt
from zoneinfo import ZoneInfo
from bazi_calculator import calculate_bazi_with_solar_correction
from display_helpers import display_pillars_table, display_element_star_meter

# --- 1. Inputs ---
st.title("🌿 MyElement – Discover Your Four Pillars")

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

# --- 2. On Button Click ---
if st.button("Generate My Pillars"):
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

                st.subheader("Your Four Pillars")
                st.write(f"**Year  :** {result['year']}")
                st.write(f"**Month :** {result['month']}")
                st.write(f"**Day   :** {result['day']}  ← *Day Master*")
                st.write(f"**Hour  :** {result['hour']}")

                display_pillars_table(result)
                st.markdown("---")
                display_element_star_meter(result)
                st.markdown("---")

                st.subheader("Day-Master Strength")
                st.success(f"{result['strength']}  (score {result['strength_score']:+d})")

                st.info(
                    f"Standard Time: {result['standard_dt'].strftime('%Y-%m-%d %H:%M')} | "
                    f"Solar-corrected (+EoT): {result['solar_dt'].strftime('%Y-%m-%d %H:%M')}  "
                    f"(Longitude correction: {result['longitude_correction_min']:.0f} min, "
                    f"EoT: {result['EoT_min']:.0f} min) | "
                    f"Timezone: `{timezone_str}` | UTC offset: {utc_offset:+.1f}"
                )

    except Exception as e:
        st.error(f"❌ Something went wrong: {e}")