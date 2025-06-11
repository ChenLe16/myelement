import streamlit as st
import datetime as dt
import pycountry
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
import hashlib

# Shadow colour per element — used to keep text crisp on matching backgrounds
ELEMENT_SHADOW = {
    "Wood":  "0 2px 6px rgba(9,39,25,0.65)",
    "Fire":  "0 2px 6px rgba(120,30,0,0.55)",
    "Earth": "0 2px 6px rgba(64,32,8,0.55)",
    "Metal": "0 2px 6px rgba(20,29,46,0.6)",
    "Water": "0 3px 10px rgba(0,0,0,0.75)",
}

# ── Identity mappings ───────────────────────────────────────

# Unified dictionary for Day Master identities and attributes
DAY_MASTER_IDENTITIES = {
    "甲": {
        "header": "The Resolute Oak Person",
        "traits": "Steady growth, long‑range vision; anchors big projects.",
        "takeaway": "Lean on your capacity for endurance when teams lose focus. Stay open to new methods so you don’t become rigid.",
        "element": "Wood",
        "color": "#2E8B57",
        "emoji": "🌳",
    },
    "乙": {
        "header": "The Adaptive Willow Person",
        "traits": "Flexible thinker; links ideas and people with ease.",
        "takeaway": "Your agility is a super-connector—use it to translate between specialists. Guard against spreading yourself too thin; pick one root project to deepen.",
        "element": "Wood",
        "color": "#2E8B57",
        "emoji": "🌿",
    },
    "丙": {
        "header": "The Radiant Sun Person",
        "traits": "Energises groups and sparks momentum.",
        "takeaway": "People mirror your enthusiasm, so set the tone deliberately. Schedule quiet “eclipse” time to keep from burning out.",
        "element": "Fire",
        "color": "#FF7518",
        "emoji": "🌞",
    },
    "丁": {
        "header": "The Enduring Ember Person",
        "traits": "Sustains warm focus; mentors and refines goals.",
        "takeaway": "Your steady glow excels in 1-to-1 guidance—cultivate mentorship roles. Beware of dimming when recognition is delayed; celebrate small wins.",
        "element": "Fire",
        "color": "#FF7518",
        "emoji": "🔥",
    },
    "戊": {
        "header": "The Grounded Mountain Person",
        "traits": "Reliable planner; sees the whole terrain before acting.",
        "takeaway": "Strategic patience lets you solve problems others rush past. Stay receptive to feedback so analysis doesn’t turn into immobility.",
        "element": "Earth",
        "color": "#C27C48",
        "emoji": "⛰️",
    },
    "己": {
        "header": "The Cultivating Marble Person",
        "traits": "Patient craftsman; turns rough ideas into polished results.",
        "takeaway": "Your eye for detail builds lasting value—own the refinement phase. Balance perfectionism with deadlines to keep momentum.",
        "element": "Earth",
        "color": "#C27C48",
        "emoji": "🪨",
    },
    "庚": {
        "header": "The Strategic Sword Person",
        "traits": "Decisive and direct—cuts through complexity to solutions.",
        "takeaway": "Teams rely on your clarity; wield it to unblock consensus. Temper rapid judgement with empathy to avoid unintended cuts.",
        "element": "Metal",
        "color": "#8E97A8",
        "emoji": "⚔️",
    },
    "辛": {
        "header": "The Discerning Jewel Person",
        "traits": "Precise, value‑driven; elevates hidden quality.",
        "takeaway": "You instinctively spot what’s precious—apply that to both tasks and people. Remember not everyone craves the same level of polish; choose battles.",
        "element": "Metal",
        "color": "#8E97A8",
        "emoji": "💎",
    },
    "壬": {
        "header": "The Dynamic Wave Person",
        "traits": "Exploratory, big‑picture thinker driving new ventures.",
        "takeaway": "Your breadth fuels innovation—map bold routes others don’t see. Anchor ideas with concrete milestones so they don’t dissipate.",
        "element": "Water",
        "color": "#5CD1E8",
        "emoji": "🌊",
    },
    "癸": {
        "header": "The Reflective Rain Person",
        "traits": "Calm insight‑giver; nourishes teams with clarity.",
        "takeaway": "Quiet observation lets you solve root issues others miss. Speak insights early; withholding too long can flood the project later.",
        "element": "Water",
        "color": "#5CD1E8",
        "emoji": "💧",
    },
}

# ── Helper: get the Day‑Master stem safely ───────────────────
def get_day_stem(bazi_dict: dict) -> str:
    """
    Return the Heavenly‑stem character of the Day pillar
    regardless of the dict shape returned by the calculator.
    Accepted keys:
      • "day_pillar": "壬寅"
      • "day":        "壬寅"
      • "pillars":    ["丁丑","庚戌","壬寅","戊申"]
    Raises KeyError if none found.
    """
    if "day_pillar" in bazi_dict:
        return bazi_dict["day_pillar"][0]
    if "day" in bazi_dict:
        return bazi_dict["day"][0]
    if "pillars" in bazi_dict and len(bazi_dict["pillars"]) >= 3:
        return bazi_dict["pillars"][2][0]
    raise KeyError("Day pillar not found in BaZi result")

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
    page_icon=":star:",
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
            st.session_state["awaiting_confirm"] = False   # ⇦ hide banner

# 5. Results, Star Meter, Email form
if "bazi_result" in st.session_state and st.session_state["bazi_result"]:
    st.markdown("---")
    # ---- Identity header ----
    dm_stem = get_day_stem(st.session_state["bazi_result"])
    dm_info = DAY_MASTER_IDENTITIES[dm_stem]
    header  = dm_info["header"]
    trait   = dm_info["traits"]
    elem    = dm_info["element"]
    color   = dm_info["color"]
    emoji   = dm_info["emoji"]

    # ── Elemental Identity Spotlight Section ──────────────
    bg_gradient = {
        "Wood":  "linear-gradient(135deg, #134e3a 0%, #2E8B57 100%)",
        "Fire":  "linear-gradient(135deg, #ff7518 0%, #ffb347 100%)",
        "Earth": "linear-gradient(135deg, #c27c48 0%, #ffe0b2 100%)",
        "Metal": "linear-gradient(135deg, #8e97a8 0%, #1d2431 100%)",
        "Water": "linear-gradient(135deg, #11998e 0%, #003344 100%)",
    }
  
    st.markdown(
    f"""
    <div style='
        background: radial-gradient(circle at center 40%, rgba(255,255,255,0.12) 0%, rgba(0,0,0,0) 60%), 
                    {bg_gradient[elem]};
        border-radius: 28px;
        margin: 3.3em 0 2em 0;
        box-shadow: 0 8px 38px #0007,
                    inset 0 0 0 0.5px #ffffff44,
                    inset 0 1.5px 0.5px #fff2;
        padding: 52px 12px 40px 12px;
        position: relative;
        border: 1.5px solid #fff3;
    '>
        <div style='
            font-size: 1.25rem;
            letter-spacing: 2.5px;
            color: #fff7e8;
            text-align: center;
            margin-bottom: 0.65em;
            text-shadow: 0 1px 12px #0025;
            font-weight: 800;
            text-transform: uppercase;
        '>
            IDENTITY SPOTLIGHT
        </div>
        <span style='
            display: block;
            text-align: center;
            font-size: 6.5rem;
            margin-bottom: 0.08em;
            filter: drop-shadow(0 8px 38px #0009) brightness(0.90);
            line-height: 1;
        '>
            {emoji}
        </span>
        <div style='
            font-size:2.68rem;
            font-weight:900;
            letter-spacing:1px;
            margin-bottom: 0.11em;
            margin-top: 0.04em;
            text-align: center;
        '>
            <span style='
                color:#fff;
                text-shadow:
                    0 1.5px 10px #0052,
                    0 1.5px 0px #fff9;
                font-weight:900;
            '>You are </span>
            <span style='
                color:{color};
                text-shadow: 0 1px 3px rgba(0,0,0,.35), {ELEMENT_SHADOW[elem]};
                font-weight:900;
                letter-spacing:1px;
                transition: color 0.4s;
            '>{header}</span>
        </div>
        <div style='
            font-size:1.45rem;
            color:#FFEFD3;
            letter-spacing:0.5px;
            font-weight: 600;
            margin-top:0.66em;
            margin-bottom: 1.25em;
            line-height:1.56;
            text-shadow: 0 2px 12px #0028;
            max-width: 650px;
            margin-left:auto;
            margin-right:auto;
            text-align: center;
        '>
            {trait}
        </div>
        <div style='
            font-size:1.13rem;
            color:#FFF3C4;
            font-style:italic;
            background:rgba(10,32,44,0.80);
            border-radius:12px;
            border: 1.5px solid #1DE1FC44;
            box-shadow:0 3px 26px #0008;
            margin: 0.9em auto 0.78em auto;
            padding: 14px 18px;
            max-width: 640px;
            line-height: 1.66;
            text-align: center;
        '>
            {dm_info["takeaway"]}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
   
    display_pillars_table(st.session_state["bazi_result"])
    display_element_score_breakdown(st.session_state["bazi_result"])
    st.markdown("---")
    display_element_star_meter(st.session_state["bazi_result"])
    st.markdown(
        "<div style='color:#edc96d; background:rgba(64,44,0,0.08); text-align:center; font-size:1.03em; margin:12px 0 18px 0; border-radius:8px; padding:8px 10px 6px 10px;'>"
        "<b>Note:</b> <em>Your Elemental Identity (Day Master) is not always your strongest star.</em>"
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    # ── Streamlit-native paywall card for MyElement Blueprint ──  
    product_name = "MyElement Blueprint"
    stripe_checkout = "https://buy.stripe.com/YOUR_PAYMENT_LINK"  # TODO: replace with your live Stripe link
    product_preview_image = "assets/blueprint_mock.png"

    with st.container():
        cols = st.columns([2, 1])
        with cols[0]:
            st.subheader(
                f"{product_name}",
                help="6-page PDF report: core Five-Element analysis, chart visuals, guidance, and custom advice."
            )
            st.markdown(
                "- 6-page Blueprint PDF — core Five-Element analysis, chart visuals, and easy guidance.\n"
                "- Career & relationship advice for your profile.\n"
                "- Custom growth recommendations for balance and strengths.\n"
                "- Delivered straight to your inbox."
            )
            st.link_button("Get my Blueprint ➔", url=stripe_checkout, use_container_width=True)
        with cols[1]:
            st.image(product_preview_image, use_container_width=True)

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