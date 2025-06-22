import random
import datetime as dt
import pycountry
import streamlit as st
import streamlit.components.v1 as components
from gsheet_helpers import append_to_gsheet, is_valid_email, make_unique_key, append_survey_response
from bazi_constants import ELEMENT_EMOJIS, ELEMENT_COLORS, BG_GRADIENT, ELEMENT_SHADOW, SUPPORT_EMAIL
from ui_constants import LOGO_ICON_PATH, CAREER_IMAGE_PATH, GROWTH_IMAGE_PATH, RELATIONSHIP_IMAGE_PATH, IDENTITY_COLORS, SOCIAL_LINKS

# --- Standalone human check function ---
def display_human_check():
    """Display a simple human check question and return True if correct, else False."""
    if "captcha_a" not in st.session_state or "captcha_b" not in st.session_state:
        st.session_state["captcha_a"] = random.randint(2, 9)
        st.session_state["captcha_b"] = random.randint(2, 9)
    a = st.session_state["captcha_a"]
    b = st.session_state["captcha_b"]
    human_answer = st.text_input(f"Human check: What is {a} + {b}?")
    if human_answer and human_answer.strip() == str(a + b):
        # Refresh question for next time (optional, or do on submit)
        st.session_state["captcha_a"] = random.randint(2, 9)
        st.session_state["captcha_b"] = random.randint(2, 9)
        return True
    elif human_answer:
        st.warning("Human check failed. Please try again.")
    return False

def display_custom_css():
    """
    Injects custom CSS styles for Streamlit buttons to enhance appearance and interactivity.

    Returns:
        None
    """
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

def display_identity_section(title, color, image_path, paragraph):
    # Use columns for layout: image and text, with vertical alignment
    col1, col2 = st.columns([1, 2], gap="medium")
    with col1:
        st.image(image_path, use_container_width=False)
    with col2:
        st.markdown(
            f'''
            <div style="display: flex; flex-direction: column; justify-content: center; height: 100%; min-height: 160px;">
                <span style="font-size:2rem; font-weight:800; color:{color}; margin-bottom: 0.22em;">{title}</span>
                <div style="color:#efecde; font-size:1.15em; line-height:1.74;">
                    {paragraph}
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )

def display_top_logo_bar():
    """
    Displays the logo and app name at the top left of the page.
    """
    cols = st.columns([0.10, 0.90])
    with cols[0]:
        st.image(LOGO_ICON_PATH, width=68)
    with cols[1]:
        st.markdown(
            """
            <div style='display: flex; align-items: center; height: 60px; margin-left: -10px;'>
                <span style='font-size:2rem; font-weight:800; color:#fff; letter-spacing:0.5px;'>
                    MyElement
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

def display_hero_section():
    """
    Displays the hero section with logo and app name on the top left, headline centered.
    """
    display_top_logo_bar()

    # Main hero section, centered
    st.markdown(
        """
        <div style='display: flex; flex-direction: column; align-items: center; margin-bottom: 38px; margin-top: 24px;'>
            <div class='hero-title' style='font-size: 2.1rem; font-weight: 700; text-align: center; color: #fff; margin-bottom: 12px;'>
                Turn Birth Data into Actionable Self-Insights
            </div>
            <div class='hero-desc' style='text-align: center; font-size: 1.23rem; color: #B0B5BA; margin-bottom: 30px; max-width: 600px;'>
                Our Five-Element engine converts your birth date and time into a bar-chart of strengths, gaps, and next-step tips—no sign-up, no data stored.
            </div>
            <div style='display: flex; justify-content: center; margin-top: 18px;'>
                <a class='hero-btn' href='/methodology' style='padding: 0.5em 2.1em; font-size: 1.18rem; font-weight: 700; border-radius: 10px; background: #1DBF73; color: white; text-decoration: none; box-shadow: 0 2px 12px #1dbf7322; transition: background 0.2s, outline 0.2s;'>
                    Learn More
                </a>
            </div>
        </div>
        <style>
        .hero-btn:hover, .hero-btn:focus {
            background: #14975f !important;
            outline: 2px solid #eafff6;
        }
        </style>
        """, unsafe_allow_html=True
    )
    
def display_feature_card(
        color, label, headline, body, image_path, image_on="right", button_text=None, button_callback=None
):
    """
    Displays a feature card with optional CTA button.

    Args:
        color (str): Color for label.
        label (str): Short label above card.
        headline (str): Title of card.
        body (str): Main body text.
        image_path (str): Path to image.
        image_on (str): 'right' or 'left' (default 'right').
        button_text (str, optional): CTA button label.
        button_callback (function, optional): Function to call if button is clicked.

    Returns:
        None
    """
    st.markdown(f":{color}[{label}]")

    with st.container():
        if image_on == "right":
            col_text, col_img = st.columns([1.5, 1])
        else:
            col_img, col_text = st.columns([1, 1.5])

        with col_text:
            st.subheader(headline)
            st.text(body)
            if button_text:
                if st.button(button_text, key=f"feature-card-btn-{headline}"):
                    if button_callback:
                        button_callback()
        with col_img:
            st.image(image_path, use_container_width=True)

def display_main_input_form():
    """
    Displays the main input form for the user to enter their name, gender, country of birth, date of birth, and birth time.

    Returns:
        tuple: (name (str), gender (str), country (str), dob (date), hour (int), minute (int), generate_clicked (bool))
    """
    st.markdown('<div id="main-input-form"></div>', unsafe_allow_html=True)
    with st.form("star_meter_form"):
        # 1. Add section heading at the very start
        st.markdown("### Enter Your Birth Details")

        # 2. Add helper text for each field
        name = st.text_input("Name", help="What should we call you? Nicknames are fine.")
        gender = st.selectbox("Gender", ["Male", "Female"], help="Needed for accurate element analysis.")
        country_list = sorted([c.name for c in pycountry.countries])
        country = st.selectbox(
            "Country of Birth",
            country_list,
            index=country_list.index("Malaysia"),
            help="This ensures the right solar time and element mapping."
        )
        dob = st.date_input(
            "Date of Birth",
            value=dt.date(1990, 1, 1),
            min_value=dt.date(1900, 1, 1),
            max_value=dt.date.today() + dt.timedelta(days=365*2),
            help="Accurate date ensures the correct pillar calculation."
        )
        col1, col2 = st.columns([1, 1])
        with col1:
            hour = st.selectbox("Hour (H)", list(range(0, 24)), index=12)
        with col2:
            minute = st.selectbox("Minute (M)", list(range(0, 60)), index=0)
        # 3. Add error/validation for hour and minute
        if not (0 <= hour < 24):
            st.warning("Hour must be between 0 and 23.")
        if not (0 <= minute < 60):
            st.warning("Minute must be between 0 and 59.")

        # 4. Add advanced timezone/DST confidence helper before the warning about exact time
        with st.expander("Advanced: Need manual UTC offset or daylight saving?"):
            st.write(
                "If you know your birth time was affected by daylight saving time, or you want to adjust for a specific UTC offset, contact us or check our methodology page."
            )

        st.warning(
            "⏱ **Exact birth time matters.** Even a five‑minute difference can change your results."
        )

        display_privacy_note()

        # 5. Human check
        passed_human_check = display_human_check()
        col1, col2, col3 = st.columns([2, 3, 2])
        with col2:
            generate_clicked = st.form_submit_button(
                "✨ Generate My Elemental Star Meter"
            )

        # 6. Improve mobile spacing by adding a spacing div after the submit button
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # After the form context: Show warning if form was submitted but human check not passed
    if generate_clicked and not passed_human_check:
        st.warning("Please pass the human check before generating your Star Meter.")

    # Return all input values and the button state
    return name, gender, country, dob, hour, minute, generate_clicked and passed_human_check

def display_user_summary(name: str, gender: str, country: str, dob, birth_time) -> None:
    """
    Displays a summary card of the user's input information at the top of the results section.

    Args:
        name (str): The user's name.
        gender (str): The user's gender.
        country (str): The user's country of birth.
        dob (date): The user's date of birth.
        birth_time (time): The user's birth time.

    Returns:
        None
    """
    st.markdown(
        f"""
        <div style='background-color:rgba(220,220,230,0.08); border-radius:12px; padding:16px 22px; margin-bottom:16px; text-align:center;'>
            <span style='font-weight:600; font-size:1.04em;'>Name:</span> {name}
            &nbsp; | &nbsp;
            <span style='font-weight:600; font-size:1.04em;'>Gender:</span> {gender}
            &nbsp; | &nbsp;
            <span style='font-weight:600; font-size:1.04em;'>Country:</span> {country}
            &nbsp; | &nbsp;
            <span style='font-weight:600; font-size:1.04em;'>Date of Birth:</span> {dob}
            &nbsp; | &nbsp;
            <span style='font-weight:600; font-size:1.04em;'>Birth Time:</span> {birth_time}
        </div>
        """,
        unsafe_allow_html=True
    )
    
def display_identity_card(dm_info: dict) -> None:
    """
    Displays the Identity Spotlight card, highlighting the user's Day Master, key traits, and main takeaway.

    Args:
        dm_info (dict): Dictionary containing identity header, traits, element, color, emoji, and takeaway.

    Returns:
        None
    """
    # ---- Identity header ----
    header  = dm_info["header"]
    trait   = dm_info["traits"]
    elem    = dm_info["element"]
    color   = dm_info["color"]
    emoji   = dm_info["emoji"]
  
    st.markdown(
        f"""
        <div style='
            background: radial-gradient(circle at center 40%, rgba(255,255,255,0.12) 0%, rgba(0,0,0,0) 60%), 
                        {BG_GRADIENT[elem]};
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


# --- New function: Display expanded Career, Growth, and Relationship advice paragraphs ---
def display_identity_expanded_paragraphs(dm_info: dict) -> None:
    display_identity_section(
        "Career", IDENTITY_COLORS["Career"], CAREER_IMAGE_PATH, dm_info.get("career", "")
    )

    section_divider()
    
    display_identity_section(
        "Growth", IDENTITY_COLORS["Growth"], GROWTH_IMAGE_PATH, dm_info.get("growth", "")
    )
    
    section_divider()
    
    display_identity_section(
        "Relationship", IDENTITY_COLORS["Relationship"], RELATIONSHIP_IMAGE_PATH, dm_info.get("relationship", "")
    )
    st.markdown('</div>', unsafe_allow_html=True)

def display_pillars_table(result: dict) -> None:
    """
    Displays the Four Pillars Table, showing Heavenly Stems and Earthly Branches for each pillar, and the Day Master strength verdict.

    Args:
        result (dict): Dictionary containing pillar information and strength verdict.

    Returns:
        None
    """
    # Centered, matching-width title
    st.markdown("""
    <div style='
        width:88%; 
        margin-left:auto; 
        margin-right:auto; 
        margin-bottom:0; 
        margin-top:0;
    '>
        <h4 style='
            text-align:center; 
            color:#ffe9b4;
            font-size:1.32em;
            letter-spacing:0.01em;
            margin: 0 0 8px 0;
            font-weight: 800;
        '>
            Four Pillars Table
        </h4>
    </div>
    """, unsafe_allow_html=True)

    pillars = [
        {"label": "Year",  "stem": result['year'][0],  "branch": result['year'][1],  "hidden": result['hidden_stems'][0]},
        {"label": "Month", "stem": result['month'][0], "branch": result['month'][1], "hidden": result['hidden_stems'][1]},
        {"label": "Day",   "stem": result['day'][0],   "branch": result['day'][1],   "hidden": result['hidden_stems'][2]},
        {"label": "Hour",  "stem": result['hour'][0],  "branch": result['hour'][1],  "hidden": result['hidden_stems'][3]},
    ]
    verdict = result.get("strength", "")
    strength_color = "#fab74b" if verdict == "Strong" else "#44c4fa"

    st.markdown("""
    <style>
        .pillar-table-clean {
            border-collapse: separate;
            border-spacing: 0;
            border-radius:13px;
            box-shadow:0 1px 12px #23272e;
            background:#23262c;
            width:88%; margin:auto;
            overflow: hidden;
        }
        .pillar-table-clean th, .pillar-table-clean td {
            padding:14px 18px;
            border:none;
            color: #eaeaea !important;
            text-align: center !important;
            vertical-align: middle !important;
        }
        .pillar-table-clean th {
            background: #21242a;
            color: #ffe9b4 !important;
            font-size:1.09em;
        }
        .pillar-table-clean tr:first-child th {
            border-top-left-radius: 13px;
            border-top-right-radius: 13px;
        }
        .pillar-table-clean tr:last-child td {
            border-bottom-left-radius: 13px;
            border-bottom-right-radius: 13px;
        }
        .strength-row {
            background: #272c32;
            text-align: center;
            font-size: 1.13em;
            font-weight: bold;
            letter-spacing: 0.01em;
            padding: 14px 18px !important;
            border-bottom-left-radius: 13px;
            border-bottom-right-radius: 13px;
        }
        .pillar-table-clean tr:not(.strength-row) {
            transition: background 0.20s, transform 0.20s;
            position: relative;
        }
        .pillar-table-clean tr:not(.strength-row):hover {
            background: #262b32 !important;
            transform: scale(1.035);
            z-index: 2;
        }
    </style>
    """, unsafe_allow_html=True)

    table = "<table class='pillar-table-clean'>"
    table += "<tr><th>Pillar</th><th>Heavenly Stem</th><th>Earthly Branch</th></tr>"
    for p in pillars:
        stem_html = f"<span style='font-weight:bold; font-size:1.07em'>{p['stem']}</span>"
        branch_html = f"<span style='font-weight:500; font-size:1.07em'>{p['branch']}</span>"
        table += (
            f"<tr style='background-color:#23262c;'>"
            f"<td>{p['label']}</td>"
            f"<td>{stem_html}</td>"
            f"<td>{branch_html}</td>"
            f"</tr>"
        )
    # (Removed Day Master Strength verdict row from pillars table)
    table += "</table>"
    st.markdown(table, unsafe_allow_html=True)

    # Add expander to show hidden stems details
    with st.expander("Show details (hidden stems)"):
        hidden_table = "<table style='width: 88%; margin-left: auto; margin-right: auto; border-collapse: collapse;'>"
        hidden_table += "<tr><th style='text-align:left; padding: 6px 12px;'>Pillar</th><th style='text-align:left; padding: 6px 12px;'>Hidden Stem(s)</th></tr>"
        for p in pillars:
            hidden_stems_str = " · ".join(p['hidden']) if p['hidden'] else "-"
            hidden_table += (
                f"<tr style='background-color:#23262c; color:#eaeaea;'>"
                f"<td style='padding: 6px 12px;'>{p['label']}</td>"
                f"<td style='padding: 6px 12px;'>{hidden_stems_str}</td>"
                f"</tr>"
            )
        hidden_table += "</table>"
        st.markdown(hidden_table, unsafe_allow_html=True)

def display_element_star_meter(result: dict, identity_element: str = None, identity_polarity: str = None) -> None:
    """
    Displays the Five Elements Star Meter, showing star ratings and strength labels for each element.

    Args:
        result (dict): Dictionary containing element strengths.
        identity_element (str, optional): The user's Day Master element for highlighting.
        identity_polarity (str, optional): The polarity ("Yin" or "Yang") of the Day Master element for displaying its Yin/Yang nature.

    Returns:
        None
    """
    # Center the title
    st.markdown("<h4 style='text-align:center;'>Five Elements Star Meter</h4>", unsafe_allow_html=True)

    element_strengths = result['element_strengths']

    def star_meter(score, color="#ffd700"):
        max_stars = 5
        capped_score = min(score, max_stars)
        n_full = int(capped_score)
        remainder = capped_score - n_full
        n_half = 0
        plus = " +" if score > max_stars else ""
        if abs(capped_score - 0.5) < 1e-8:
            n_full = 0
            n_half = 1
        else:
            if remainder >= 0.5:
                n_half = 1
        stars_html = "<span style='font-size:1.09em; vertical-align:middle;'>"
        stars_html += f"<span style='color:{color}; font-weight:600;'>★</span>" * n_full
        if n_half == 1:
            stars_html += f"<span style='color:{color}; font-weight:600;'>☆</span>"
        n_faded = max_stars - n_full - n_half
        if n_faded > 0:
            stars_html += f"<span style='color:#555555;'>☆</span>" * n_faded
        stars_html += f"{plus}</span>"
        return stars_html

    st.markdown("""
    <style>
    .star-meter-table-dark {
        width: 80% !important;
        margin-left: auto;
        margin-right: auto;
        border-radius: 13px;
        box-shadow: 0 1px 10px #23272e;
        background: #23262c;
        overflow: hidden;
    }
    .star-meter-table-dark th, .star-meter-table-dark td {
        font-size: 1.11em !important;
        padding: 8px 14px !important;
        font-weight: 600;
        border: none;
    }
    .star-meter-table-dark th {
        background: #21242a;
        color: #ffe9b4 !important;
        font-size:1.09em;
    }
    .star-meter-table-dark tr:first-child th {
        border-top-left-radius: 13px;
        border-top-right-radius: 13px;
    }
    .star-meter-table-dark tr:last-child td {
        border-bottom-left-radius: 13px;
        border-bottom-right-radius: 13px;
    }
    .star-meter-legend {
        text-align: center;
        margin-top: 8px;
        color: #a9b7c6;
        font-size: 0.95em;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)

    def get_strength_label(score):
        if score >= 4.0:
            return "Very Strong"
        elif score >= 3.0:
            return "Strong"
        elif score >= 2.0:
            return "Balanced"
        elif score >= 1.0:
            return "Weak"
        else:
            return "Very Weak"

    table = "<table class='star-meter-table-dark'>"
    table += "<tr><th>Element</th><th>Star Meter</th></tr>"
    for elem, val in element_strengths.items():
        label = f"{ELEMENT_EMOJIS.get(elem, '')}&nbsp;<span style='color:{ELEMENT_COLORS[elem]}; font-weight:700'>{elem}</span>"
        if identity_element and elem == identity_element:
            yin_yang = ""
            if identity_polarity:
                yin_yang = "☀️" if "Yang" in identity_polarity else "🌙"
            label = f"{label} <span style='color:#44c4fa; font-size:0.99em; margin-left:4px;'>{yin_yang}</span>"
        stars = star_meter(val, color=ELEMENT_COLORS[elem])
        # label_strength = get_strength_label(val)  # No longer needed for table row
        table += f"<tr style='background-color:#23262c;'><td>{label}</td><td>{stars}</td></tr>"
    # Add Day Master strength verdict row to the star meter table
    if identity_element and result.get("strength"):
        strength_color = "#fab74b" if result["strength"] == "Strong" else "#44c4fa"
        table += (
            f"<tr>"
            f"<td colspan='2' style='background:#272c32; text-align:center; font-size:1.13em; font-weight:bold; letter-spacing:0.01em; padding:14px 18px; border-bottom-left-radius:13px; border-bottom-right-radius:13px;'>"
            f"Day Master Strength: <span style='color:{strength_color};'>{result['strength']}</span>"
            f"</td></tr>"
        )
    table += "</table>"
    st.markdown(table, unsafe_allow_html=True)

    st.markdown(
        "<div style='color:#edc96d; background:rgba(64,44,0,0.08); text-align:center; font-size:1.03em; margin:12px 0 18px 0; border-radius:8px; padding:8px 10px 6px 10px;'>"
        "<b>Note:</b> <em>Your Elemental Identity (☀️/🌙) is not always your strongest star.</em>"
        "</div>",
        unsafe_allow_html=True
    )

def display_element_score_breakdown(result: dict) -> None:
    """
    Displays a detailed scoring breakdown table for the Five Elements, showing visible, hidden, season, and DM bonus points.

    Args:
        result (dict): Dictionary containing the element_score_breakdown data.

    Returns:
        None
    """
    with st.expander("See how we calculate (advanced)"):
        st.markdown(
            "<h4 style='text-align:center;'>Five Elements Scoring Breakdown</h4>",
            unsafe_allow_html=True,
        )

        breakdown = result["element_score_breakdown"]
        element_order = ["Wood", "Fire", "Earth", "Metal", "Water"]

        st.markdown(
            '''
            <style>
            .element-breakdown-table th, .element-breakdown-table td {
                font-size: 1.09em !important;
                padding: 7px 12px !important;
                border: none;
                text-align: center;
            }
            .element-breakdown-table {
                width: 94% !important;
                margin-left: auto;
                margin-right: auto;
                border-radius: 11px;
                box-shadow: 0 1px 10px #23272e;
                background: #23262c;
            }
            .element-breakdown-table th {
                background: #21242a;
                color: #ffe9b4 !important;
            }
            .element-breakdown-table tr {
                background-color: #23262c;
            }
            </style>
            ''',
            unsafe_allow_html=True,
        )

        table = "<table class='element-breakdown-table'>"
        table += (
            "<tr>"
            "<th>Element</th>"
            "<th>Visible pts</th>"
            "<th>Hidden pts</th>"
            "<th title='Season bonus (季节加分)'>Season bonus</th>"
            "<th title='Day Master self-point (日主加分)'>DM bonus</th>"
            "<th>Total</th>"
            "</tr>"
        )

        for elem in element_order:
            b = breakdown[elem]
            emoji = ELEMENT_EMOJIS.get(elem, "")
            table += (
                f"<tr>"
                f"<td>{emoji} {elem}</td>"
                f"<td>{b['visible']}" + (f" ({b['visible_desc']})" if b.get('visible_desc') else "") + "</td>"
                f"<td>{b['hidden']}" + (
                    f" ({' + '.join(s.split()[0] for s in b['hidden_desc'].split(' + '))})" if b.get('hidden_desc') else ""
                ) + "</td>"
                f"<td>{b['season']}</td>"
                f"<td>{b['dm']}</td>"
                f"<td><strong>{b['total']}</strong></td>"
                f"</tr>"
            )
        table += "</table>"
        st.markdown(table, unsafe_allow_html=True)

def display_time_info(result: dict, timezone_str: str) -> None:
    """
    Displays time-related information, including standard time, solar-corrected time, and timezone.

    Args:
        result (dict): Dictionary containing 'standard_dt' and 'solar_dt' datetime objects.
        timezone_str (str): String representation of the timezone.

    Returns:
        None
    """
    st.markdown(
        f"<div style='text-align:center; color:#78908b; margin-top:-0px; margin-bottom:0px; font-size:1.08em;'>"
        f"<div><b>Standard Time:</b> {result['standard_dt'].strftime('%Y-%m-%d %H:%M')}</div>"
        f"<div><b>Solar-corrected:</b> {result['solar_dt'].strftime('%Y-%m-%d %H:%M')}</div>"
        f"<div><b>Timezone:</b> {timezone_str}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

def display_privacy_note() -> None:
    """
    Displays a privacy note informing users that calculations run locally and data is only stored with explicit consent.

    Returns:
        None
    """
    st.markdown(
        "<span style='font-size:1em; color:#a9b7c6;'>🔒 All calculations run locally. <a href='/privacy' style='color:#1DBF73;'>Learn more</a></span>",
        unsafe_allow_html=True,
    )

def display_paywall_card(
    product_name: str,
    stripe_checkout: str,
    product_pdf_cover,
    product_pdf_content,
    left_bullets: list,
    right_bullets: list,
) -> None:
    """
    Displays the paywall card for the premium PDF report, including product details, images, and payment flow.

    Args:
        product_name (str): The name of the premium product.
        stripe_checkout (str): Stripe checkout URL.
        product_pdf_cover (str or image): Cover image for the PDF.
        product_pdf_content (str or image): Content preview image for the PDF.
        left_bullets (list): List of feature bullet points for the left column.
        right_bullets (list): List of feature bullet points for the right column.

    Returns:
        None
    """
    # Session state setup
    if "paywall_confirm" not in st.session_state:
        st.session_state["paywall_confirm"] = False
    if "show_paywall_popup" not in st.session_state:
        st.session_state["show_paywall_popup"] = False

    st.header(product_name)

    with st.container():
        row1_left, row1_right = st.columns([1.5, 1])
        with row1_left:
            st.subheader("What You Get")
            st.markdown("\n".join([f"- {item}" for item in left_bullets]))
        with row1_right:
            st.image(product_pdf_cover, use_container_width=True)
        
        section_divider()
        
        row2_left, row2_right = st.columns([1.5, 1])
        with row2_left:
            st.subheader("Why It Matters")
            st.markdown("\n".join([f"- {item}" for item in right_bullets]))
        with row2_right:
            st.image(product_pdf_content, use_container_width=True)

        st.markdown(
            "<div style='margin: 0.8em 0 1.1em 0; font-size:1.75rem; color:#24cc80; "
            "background:rgba(25,60,40,0.13); border-radius:7px; display:inline-block; "
            "padding:5px 16px 5px 9px; font-weight:700;'>"
            "🛡 30-Day Guarantee · Secure payment"
            "</div>",
            unsafe_allow_html=True
        )

        paywall_email = st.text_input(
            "Email for delivery (required):",
            value=st.session_state.get("paywall_email", ""),
            key="paywall_email"
        ).strip()
        paywall_btn_disabled = not (paywall_email and is_valid_email(paywall_email))

        if not st.session_state["paywall_confirm"]:
            if st.button("RM 29 · Get My Blueprint →", disabled=paywall_btn_disabled):
                if not paywall_email or not is_valid_email(paywall_email):
                    st.warning("Please enter a valid email address before proceeding.")
                else:
                    st.session_state["show_paywall_popup"] = True

            if st.session_state.get("show_paywall_popup", False):
                st.warning(
                    "Are you sure your birth data above is correct? "
                    "This info will be used for your personalized report."
                )
                if st.button("✔ Yes, proceed to payment"):
                    st.session_state["paywall_confirm"] = True
                    st.session_state["show_paywall_popup"] = False

                    key = make_unique_key(paywall_email, st.session_state.get('dob'), st.session_state.get('birth_time'), kind="FULL")
                    paywall_row = [
                        key,
                        dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        st.session_state.get("name"),
                        paywall_email,
                        st.session_state.get("country"),
                        st.session_state.get("dob").strftime("%Y-%m-%d") if st.session_state.get("dob") else "",
                        st.session_state.get("birth_time").strftime("%H:%M") if st.session_state.get("birth_time") else "",
                        st.session_state.get("gender"),
                        "FULL"
                    ]
                    try:
                        append_to_gsheet(paywall_row)
                    except Exception as e:
                        st.warning(f"Failed to log prospect to Google Sheet: {e}")

                    # Open Stripe Checkout in new tab, more reliably
                    components.html(
                        f"""
                        <script>
                        window.open('{stripe_checkout}', '_blank');
                        </script>
                        """,
                        height=0,
                        width=0
                    )
                    st.markdown(
                        f"""
                        <div style='background:#224c38; color:#fff; border-radius:9px; padding:18px 16px 14px 16px; font-size:1.1em; margin-top:10px; margin-bottom:8px;'>
                            You are being redirected to the payment page.<br>
                            <span style='font-size:1.08em; color:#e1c972;'>
                            <b>Pop-up blocked?</b> 
                            <a href="{stripe_checkout}" target="_blank" style="color:#fff; background:#19be6b; padding:7px 22px; border-radius:7px; text-decoration:none; font-weight:700; margin-left:10px; font-size:1.07em; display:inline-block;">
                                👉 Click here to pay
                            </a>
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        if st.session_state["paywall_confirm"]:
            # st.success("✅ Confirmed! [Proceed to payment](%s)" % stripe_checkout)
            st.markdown("**Your provided details:**")
            st.json({
                "Name": st.session_state.get("name"),
                "Email": paywall_email,
                "Gender": st.session_state.get("gender"),
                "Country": st.session_state.get("country"),
                "DOB": str(st.session_state.get("dob")),
                "Time": str(st.session_state.get("birth_time"))
            })

def display_pdf_request_form(state_dict: dict) -> None:
    """
    Displays a form for users to request a free PDF snapshot via email, including consent and input validation.

    Args:
        state_dict (dict): Dictionary for managing form submission state and user data.

    Returns:
        None
    """
    with st.form("email_form"):
        st.markdown(
            "<h4 style='text-align:left;'>Get Your Free Blueprint Snapshot</h4>",
            unsafe_allow_html=True
        )
        email = st.text_input(
            "Enter your email to receive your free snapshot and join our newsletter:",
            placeholder="you@email.com"
        ).strip()
        consent = st.checkbox(
            "I allow MyElement to save my birth data and email so it can generate "
            "and send my free PDF snapshot. I can delete this data at any time.",
            value=False
        )
        st.markdown(
            "<div style='text-align:left; color:#89acc0; font-size:0.98em;'>"
            "If you’d like the complete 6-page Elemental Blueprint, just click the <b>Get My Blueprint</b> button above—"
            "it’s right on this page!"
            "</div>",
            unsafe_allow_html=True
        )
        send_pdf = st.form_submit_button(
            "Send to my email",
            disabled=state_dict.get("email_submitted", False)
        )
        message = ""
        if send_pdf:
            if not consent:
                message = "consent"
            elif not is_valid_email(email):
                message = "warning"
            else:
                key = make_unique_key(email, st.session_state.get('dob'), st.session_state.get('birth_time'), kind="SIMPLE")
                row = [
                    key,
                    dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    state_dict.get("name"),
                    email,
                    state_dict.get("country"),
                    state_dict.get("dob").strftime("%Y-%m-%d"),
                    state_dict.get("birth_time").strftime("%H:%M"),
                    state_dict.get("gender"),
                    "SIMPLE"
                ]
                try:
                    result = append_to_gsheet(row)
                    if result in (None, False, "duplicate"):
                        state_dict["email_submitted"] = True
                        message = "duplicate"
                    else:
                        state_dict["email_submitted"] = True
                        message = "success"
                except Exception as e:
                    message = f"error:{e}"
        if message == "success":
            st.success(
                f"✅ Request received! Your personalised PDF snapshot will land in your inbox "
                f"within 48 hours. If you don’t see it, check spam or write us at "
                f"{SUPPORT_EMAIL}."
            )
        elif message == "duplicate":
            st.info("Looks like we already have your request — your PDF snapshot is on its way!")
        elif message.startswith("error:"):
            st.error("Unable to log to Google Sheet: " + message[6:])
        elif message == "warning":
            st.warning("Please enter a valid email address.")
        elif message == "consent":
            st.warning("Please tick the consent box to let us store your details.")

def display_footer() -> None:
    """
    Displays a modern footer with copyright (left) and social icons (right).
    """
    social_html = "".join(
        f'<a href="{s["url"]}" target="_blank" title="{s["title"]}">{s["svg"]}</a>'
        for s in SOCIAL_LINKS.values()
    )
    st.markdown(
        f"""
        <style>
        .footer-flex {{
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            padding: 18px 0 7px 0;
            color: #a9b7c6;
            font-size: 1.05em;
            margin-top: 18px;
        }}
        @media (max-width: 600px) {{
            .footer-flex {{
                flex-direction: column;
                gap: 11px;
            }}
        }}
        .footer-social a {{ 
            margin-left: 27px; 
            display: inline-block; 
            vertical-align: middle; 
            transition: transform 0.15s;
        }}
        .footer-social a:first-child {{
            margin-left: 0;
        }}
        .footer-social a:hover {{ 
            transform: scale(1.18) rotate(-7deg); 
        }}
        </style>
        <hr style="margin-top:26px; border:0; border-top:1px solid #333a44;">
        <div class="footer-flex">
            <div>© 2025 MyElement. All rights reserved.</div>
            <div class="footer-social">
                {social_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def my_scroll_callback():
    import streamlit.components.v1 as components
    components.html(
        """
        <script>
            const el = window.parent.document.getElementById('main-input-form');
            if (el) {
                el.scrollIntoView({ behavior: 'smooth' });
            }
        </script>
        """,
        height=0,
        width=0,
    )

def section_divider() -> None:
    """
    Displays a horizontal divider line to separate sections in the UI.

    Returns:
        None
    """
    st.markdown("---")
    
def display_accuracy_survey():
    """
    Displays a micro-survey asking the user to rate the result from 1-5 stars.
    Returns the rating value if submitted, else None.
    """
    st.markdown("""
        <h3 style='margin-bottom: 1.1em; font-size:1.44em;'>How accurate was your result?</h3>
        <style>
        .star-rating-bar {
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 2.02rem;
            gap: 0.06em;
            margin-bottom: 1.10em;
        }
        .star-btn button {
            min-width: 36px !important;
            max-width: 36px !important;
            height: 36px !important;
            font-size: 1.59rem !important;
            padding: 0 !important;
            margin: 0 0px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if "accuracy_star" not in st.session_state:
        st.session_state["accuracy_star"] = 0
    if "accuracy_star_submitted" not in st.session_state:
        st.session_state["accuracy_star_submitted"] = False

    # Use much narrower columns for tighter spacing
    star_cols = st.columns([0.12, 0.12, 0.12, 0.12, 0.12, 1])
    for i in range(5):
        with star_cols[i]:
            star = "★" if st.session_state["accuracy_star"] >= i + 1 else "☆"
            if st.button(star, key=f"star_btn_{i+1}", help=f"{i+1} star{'s' if i > 0 else ''}"):
                st.session_state["accuracy_star"] = i + 1

    # Show selected rating as (N/5) in yellow, slightly bold, after stars, same line
    with star_cols[5]:
        if st.session_state["accuracy_star"] > 0:
            st.markdown(
                f"""
                <div style='
                    display:inline-block;
                    color:#ffe066;
                    font-weight:600;
                    font-size:1.21rem;
                    margin-left:0.33em;
                    vertical-align:middle;
                    line-height: 1;
                    letter-spacing: 0.01em;
                '>
                    ({st.session_state["accuracy_star"]}/5)
                </div>
                """,
                unsafe_allow_html=True
            )

    # Submit button, centered below stars
    submitted = st.button("Submit Rating", disabled=st.session_state["accuracy_star"] == 0)
    if submitted:
        st.session_state["accuracy_star_submitted"] = True
        st.success(f"Thank you for rating {st.session_state['accuracy_star']} star{'s' if st.session_state['accuracy_star']>1 else ''}!")
        return st.session_state["accuracy_star"]

    return st.session_state["accuracy_star"] if st.session_state["accuracy_star_submitted"] else None