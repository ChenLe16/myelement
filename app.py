import streamlit as st
import datetime as dt
import pycountry
from bazi_calculator import compute_bazi_result, get_day_stem
from display_helpers import (
    display_identity_card, display_pillars_table, display_element_star_meter, display_element_score_breakdown, display_time_info,
    display_hero_section, display_footer, display_privacy_note, display_paywall_card, display_pdf_request_form
)
from bazi_constants import ELEMENT_SHADOW, DAY_MASTER_IDENTITIES, BG_GRADIENT

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

# ────────────────────────────────────────────────────

st.set_page_config(
    page_title="MyElement",
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

# 3. Main Input Form (with card background) inside a st.form
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
        bazi, tz_or_err = compute_bazi_result(dob, birth_time, country)
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

st.markdown("---")

# 5. Results, Star Meter, Email form
if "bazi_result" in st.session_state and st.session_state["bazi_result"]:
    # ---- Identity header ----
    dm_stem = get_day_stem(st.session_state["bazi_result"])
    dm_info = DAY_MASTER_IDENTITIES[dm_stem]
    
    display_identity_card(dm_info)   
    display_pillars_table(st.session_state["bazi_result"])
    display_element_score_breakdown(st.session_state["bazi_result"])

    st.markdown("---")
    
    display_element_star_meter(
        st.session_state["bazi_result"],
        identity_element=dm_info["element"]
    )
    st.markdown(
        "<div style='color:#edc96d; background:rgba(64,44,0,0.08); text-align:center; font-size:1.03em; margin:12px 0 18px 0; border-radius:8px; padding:8px 10px 6px 10px;'>"
        "<b>Note:</b> <em>Your Elemental Identity (🌟) is not always your strongest star.</em>"
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    # --- Paywall: Dual-row layout with image + split bullet points ---
    product_name = "MyElement Blueprint"
    stripe_checkout = "https://buy.stripe.com/YOUR_PAYMENT_LINK"  # TODO: replace with your live Stripe link
    product_pdf_cover = "assets/pdf_cover.png"
    product_pdf_content = "assets/pdf_content.png"

    # Bulletpoints
    left_bullets = [
        "6-page personalised PDF  — identity snapshot, full colour star-meter, and chart visuals.",
        "Specifically crafted - non-superstitious.",
        "Action toolkit — four element-matched habits plus Quick Growth Tips you can start today.",
        "30-day money-back guarantee — full refund if you’re not delighted."
    ]
    right_bullets = [
        "Career playbook — best-fit roles, ideal work styles, and pitfalls to avoid.",
        "Relationship roadmap — loyalty strengths, conflict triggers, and partner matching by element.",
        "Final personalised advice + life motto—a memorable one-liner to keep you on track.",
        "Secure Stripe checkout — one-time RM 29, no hidden fees or subscriptions."
    ]

    display_paywall_card(
        product_name, 
        stripe_checkout, 
        product_pdf_cover, 
        product_pdf_content, 
        left_bullets, 
        right_bullets)

    st.markdown("---")

    display_time_info(st.session_state["bazi_result"], st.session_state["timezone_str"])

    st.markdown("---")

    # --- PDF Email Snapshot Request Section ---
    display_pdf_request_form(st.session_state)

# 6. Footer
display_footer()