import streamlit as st

st.set_page_config(
    page_title="MyElement",
    page_icon="assets/logo/icon-close.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

import datetime as dt
from bazi_calculator import compute_bazi_result, get_day_stem
from display_helpers import (
    display_custom_css, display_hero_image, display_main_input_form, display_identity_card, display_pillars_table, display_element_star_meter, display_element_score_breakdown, display_time_info,
    display_all_feature_cards, display_hero_section, display_footer, display_identity_expanded_paragraphs, display_privacy_note, display_paywall_card, display_pdf_request_form, display_user_summary,
    section_divider, my_scroll_callback, display_accuracy_survey
)
from gsheet_helpers import append_survey_response
from bazi_constants import DAY_MASTER_IDENTITIES
from product_constants import PRODUCT_NAME, STRIPE_CHECKOUT, PRODUCT_PDF_COVER, PRODUCT_PDF_CONTENT, LEFT_BULLETS, RIGHT_BULLETS

# ── Session helpers ───────────────────────────────────────────
def _init_state():
    """Ensure all the keys we use later exist in st.session_state."""
    defaults = dict(
        email_submitted=False,
        submitted_email="",
        awaiting_confirm=False,
        bazi_result=None,
        timezone_str=""
    )
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)

# Inject CSS for the submit button to match hero call-to-action styling.
display_custom_css()

# Initialise session state once per user.
_init_state()

# Display the landing and hero section.
display_hero_section()

# Display Hero Image
display_hero_image()

section_divider()

# Display feature spotlights
display_all_feature_cards(my_scroll_callback)

# Main input form (with card background)
name, gender, country, dob, hour, minute, generate_clicked = display_main_input_form()# with st.form("star_meter_form"):
   
# Handle generate logic and confirmation
if generate_clicked:
    if not name.strip():
        st.warning("Please enter your name before continuing.")
    else:
        st.session_state["awaiting_confirm"] = True

# Show confirmation UI when needed
if st.session_state["awaiting_confirm"]:
    col1, col2, col3 = st.columns([0.5, 1, 0.5])
    with col2:
        if st.button("✔ Yes, my birth time is accurate — generate my result"):
            birth_time = dt.time(hour, minute)
            with st.spinner("Calculating your Elemental Star Meter..."):
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
                st.session_state["awaiting_confirm"] = False   # Hide confirmation banner

# Results, star meter, and email form
if "bazi_result" in st.session_state and st.session_state["bazi_result"]:
    # Show user's input summary at the top of the results section
    name = st.session_state.get("name", "")
    gender = st.session_state.get("gender", "")
    country = st.session_state.get("country", "")
    dob = st.session_state.get("dob", "")
    birth_time = st.session_state.get("birth_time", "")
    
    section_divider()
    display_user_summary(name, gender, country, dob, birth_time)

    # Identity header
    dm_stem = get_day_stem(st.session_state["bazi_result"])
    dm_info = DAY_MASTER_IDENTITIES[dm_stem]
    
    display_identity_card(dm_info)   
    st.caption(
        "🔍 **Disclaimer:** Your Elemental chart is a powerful lens, but it can’t capture every life influence. "
        "Family, culture, choices, and experiences all shape who you are today—treat this blueprint as a guide, not a verdict."
    )
    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
    # display_pillars_table(st.session_state["bazi_result"])
    # display_element_score_breakdown(st.session_state["bazi_result"])

    section_divider()
    
    display_element_star_meter(
        st.session_state["bazi_result"],
        identity_element=dm_info["element"],
        identity_polarity=dm_info["polarity"]
    )
    
    section_divider()

    display_identity_expanded_paragraphs(dm_info)
    
    section_divider()
    
    if (
        "bazi_result" in st.session_state
        and st.session_state["bazi_result"]
        and not st.session_state.get("survey_completed")
    ):
        rating = display_accuracy_survey()
        if rating is not None:
            user_id = st.session_state.get("submitted_email", "anon")
            user_name = st.session_state.get("name", "")
            append_survey_response(rating, user_id, user_name)
            st.session_state["survey_completed"] = True

    section_divider()

    # Paywall: dual-row layout with image and split bullet points
    display_paywall_card(
        PRODUCT_NAME, 
        STRIPE_CHECKOUT, 
        PRODUCT_PDF_COVER, 
        PRODUCT_PDF_CONTENT, 
        LEFT_BULLETS, 
        RIGHT_BULLETS)

    # Display the Standard Time, Solar-Corrected Time and Timezone
    # section_divider()
    # display_time_info(st.session_state["bazi_result"], st.session_state["timezone_str"])

    # section_divider()

    # PDF email snapshot request section
    # display_pdf_request_form(st.session_state)

# Footer
display_footer()