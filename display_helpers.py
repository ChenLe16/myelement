import streamlit as st
import streamlit.components.v1 as components
import datetime as dt
import pycountry
import random
from bazi_constants import ELEMENT_EMOJIS, ELEMENT_COLORS, BG_GRADIENT, ELEMENT_SHADOW, SUPPORT_EMAIL
from gsheet_helpers import append_to_gsheet, is_valid_email, make_unique_key, append_survey_response

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
        st.image("assets/logo/icon-close.png", width=68)
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
        "Career", "#83e7a7", "assets/images/result-career.png", dm_info.get("career", "")
    )

    section_divider()
    
    display_identity_section(
        "Growth", "#fcd669", "assets/images/result-growth.png", dm_info.get("growth", "")
    )
    
    section_divider()
    
    display_identity_section(
        "Relationship", "#b3d1ff", "assets/images/result-relationship.png", dm_info.get("relationship", "")
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
    st.markdown(
        """
        <style>
        .footer-flex {
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            padding: 18px 0 7px 0;
            color: #a9b7c6;
            font-size: 1.05em;
            margin-top: 18px;
        }
        @media (max-width: 600px) {
            .footer-flex {
                flex-direction: column;
                gap: 11px;
            }
        }
        .footer-social a { 
            margin-left: 27px; 
            display: inline-block; 
            vertical-align: middle; 
            transition: transform 0.15s;
        }
        .footer-social a:first-child {
            margin-left: 0;
        }
        .footer-social a:hover { 
            transform: scale(1.18) rotate(-7deg); 
        }
        </style>
        <hr style="margin-top:26px; border:0; border-top:1px solid #333a44;">
        <div class="footer-flex">
            <div>© 2025 MyElement. All rights reserved.</div>
            <div class="footer-social">
                <!-- Instagram -->
                <a href="https://instagram.com/myelement.cc" target="_blank" title="Instagram">
                    <svg width="40" height="40" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="2" y="2" width="28" height="28" rx="6" fill="url(#paint0_radial_87_7153)"/>
                    <rect x="2" y="2" width="28" height="28" rx="6" fill="url(#paint1_radial_87_7153)"/>
                    <rect x="2" y="2" width="28" height="28" rx="6" fill="url(#paint2_radial_87_7153)"/>
                    <path d="M23 10.5C23 11.3284 22.3284 12 21.5 12C20.6716 12 20 11.3284 20 10.5C20 9.67157 20.6716 9 21.5 9C22.3284 9 23 9.67157 23 10.5Z" fill="white"/>
                    <path fill-rule="evenodd" clip-rule="evenodd" d="M16 21C18.7614 21 21 18.7614 21 16C21 13.2386 18.7614 11 16 11C13.2386 11 11 13.2386 11 16C11 18.7614 13.2386 21 16 21ZM16 19C17.6569 19 19 17.6569 19 16C19 14.3431 17.6569 13 16 13C14.3431 13 13 14.3431 13 16C13 17.6569 14.3431 19 16 19Z" fill="white"/>
                    <path fill-rule="evenodd" clip-rule="evenodd" d="M6 15.6C6 12.2397 6 10.5595 6.65396 9.27606C7.2292 8.14708 8.14708 7.2292 9.27606 6.65396C10.5595 6 12.2397 6 15.6 6H16.4C19.7603 6 21.4405 6 22.7239 6.65396C23.8529 7.2292 24.7708 8.14708 25.346 9.27606C26 10.5595 26 12.2397 26 15.6V16.4C26 19.7603 26 21.4405 25.346 22.7239C24.7708 23.8529 23.8529 24.7708 22.7239 25.346C21.4405 26 19.7603 26 16.4 26H15.6C12.2397 26 10.5595 26 9.27606 25.346C8.14708 24.7708 7.2292 23.8529 6.65396 22.7239C6 21.4405 6 19.7603 6 16.4V15.6ZM15.6 8H16.4C18.1132 8 19.2777 8.00156 20.1779 8.0751C21.0548 8.14674 21.5032 8.27659 21.816 8.43597C22.5686 8.81947 23.1805 9.43139 23.564 10.184C23.7234 10.4968 23.8533 10.9452 23.9249 11.8221C23.9984 12.7223 24 13.8868 24 15.6V16.4C24 18.1132 23.9984 19.2777 23.9249 20.1779C23.8533 21.0548 23.7234 21.5032 23.564 21.816C23.1805 22.5686 22.5686 23.1805 21.816 23.564C21.5032 23.7234 21.0548 23.8533 20.1779 23.9249C19.2777 23.9984 18.1132 24 16.4 24H15.6C13.8868 24 12.7223 23.9984 11.8221 23.9249C10.9452 23.8533 10.4968 23.7234 10.184 23.564C9.43139 23.1805 8.81947 22.5686 8.43597 21.816C8.27659 21.5032 8.14674 21.0548 8.0751 20.1779C8.00156 19.2777 8 18.1132 8 16.4V15.6C8 13.8868 8.00156 12.7223 8.0751 11.8221C8.14674 10.9452 8.27659 10.4968 8.43597 10.184C8.81947 9.43139 9.43139 8.81947 10.184 8.43597C10.4968 8.27659 10.9452 8.14674 11.8221 8.0751C12.7223 8.00156 13.8868 8 15.6 8Z" fill="white"/>
                    <defs>
                    <radialGradient id="paint0_radial_87_7153" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(12 23) rotate(-55.3758) scale(25.5196)">
                    <stop stop-color="#B13589"/>
                    <stop offset="0.79309" stop-color="#C62F94"/>
                    <stop offset="1" stop-color="#8A3AC8"/>
                    </radialGradient>
                    <radialGradient id="paint1_radial_87_7153" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(11 31) rotate(-65.1363) scale(22.5942)">
                    <stop stop-color="#E0E8B7"/>
                    <stop offset="0.444662" stop-color="#FB8A2E"/>
                    <stop offset="0.71474" stop-color="#E2425C"/>
                    <stop offset="1" stop-color="#E2425C" stop-opacity="0"/>
                    </radialGradient>
                    <radialGradient id="paint2_radial_87_7153" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(0.500002 3) rotate(-8.1301) scale(38.8909 8.31836)">
                    <stop offset="0.156701" stop-color="#406ADC"/>
                    <stop offset="0.467799" stop-color="#6A45BE"/>
                    <stop offset="1" stop-color="#6A45BE" stop-opacity="0"/>
                    </radialGradient>
                    </defs>
                    </svg>
                </a>
                <!-- TikTok -->
                <a href="https://tiktok.com/@myelement.cc" target="_blank" title="TikTok">
                    <svg width="40" height="40" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M8.45095 19.7926C8.60723 18.4987 9.1379 17.7743 10.1379 17.0317C11.5688 16.0259 13.3561 16.5948 13.3561 16.5948V13.2197C13.7907 13.2085 14.2254 13.2343 14.6551 13.2966V17.6401C14.6551 17.6401 12.8683 17.0712 11.4375 18.0775C10.438 18.8196 9.90623 19.5446 9.7505 20.8385C9.74562 21.5411 9.87747 22.4595 10.4847 23.2536C10.3345 23.1766 10.1815 23.0889 10.0256 22.9905C8.68807 22.0923 8.44444 20.7449 8.45095 19.7926ZM22.0352 6.97898C21.0509 5.90039 20.6786 4.81139 20.5441 4.04639H21.7823C21.7823 4.04639 21.5354 6.05224 23.3347 8.02482L23.3597 8.05134C22.8747 7.7463 22.43 7.38624 22.0352 6.97898ZM28 10.0369V14.293C28 14.293 26.42 14.2312 25.2507 13.9337C23.6179 13.5176 22.5685 12.8795 22.5685 12.8795C22.5685 12.8795 21.8436 12.4245 21.785 12.3928V21.1817C21.785 21.6711 21.651 22.8932 21.2424 23.9125C20.709 25.246 19.8859 26.1212 19.7345 26.3001C19.7345 26.3001 18.7334 27.4832 16.9672 28.28C15.3752 28.9987 13.9774 28.9805 13.5596 28.9987C13.5596 28.9987 11.1434 29.0944 8.96915 27.6814C8.49898 27.3699 8.06011 27.0172 7.6582 26.6277L7.66906 26.6355C9.84383 28.0485 12.2595 27.9528 12.2595 27.9528C12.6779 27.9346 14.0756 27.9528 15.6671 27.2341C17.4317 26.4374 18.4344 25.2543 18.4344 25.2543C18.5842 25.0754 19.4111 24.2001 19.9423 22.8662C20.3498 21.8474 20.4849 20.6247 20.4849 20.1354V11.3475C20.5435 11.3797 21.2679 11.8347 21.2679 11.8347C21.2679 11.8347 22.3179 12.4734 23.9506 12.8889C25.1204 13.1864 26.7 13.2483 26.7 13.2483V9.91314C27.2404 10.0343 27.7011 10.0671 28 10.0369Z" fill="#EE1D52"/>
                    <path d="M26.7009 9.91314V13.2472C26.7009 13.2472 25.1213 13.1853 23.9515 12.8879C22.3188 12.4718 21.2688 11.8337 21.2688 11.8337C21.2688 11.8337 20.5444 11.3787 20.4858 11.3464V20.1364C20.4858 20.6258 20.3518 21.8484 19.9432 22.8672C19.4098 24.2012 18.5867 25.0764 18.4353 25.2553C18.4353 25.2553 17.4337 26.4384 15.668 27.2352C14.0765 27.9539 12.6788 27.9357 12.2604 27.9539C12.2604 27.9539 9.84473 28.0496 7.66995 26.6366L7.6591 26.6288C7.42949 26.4064 7.21336 26.1717 7.01177 25.9257C6.31777 25.0795 5.89237 24.0789 5.78547 23.7934C5.78529 23.7922 5.78529 23.791 5.78547 23.7898C5.61347 23.2937 5.25209 22.1022 5.30147 20.9482C5.38883 18.9122 6.10507 17.6625 6.29444 17.3494C6.79597 16.4957 7.44828 15.7318 8.22233 15.0919C8.90538 14.5396 9.6796 14.1002 10.5132 13.7917C11.4144 13.4295 12.3794 13.2353 13.3565 13.2197V16.5948C13.3565 16.5948 11.5691 16.028 10.1388 17.0317C9.13879 17.7743 8.60812 18.4987 8.45185 19.7926C8.44534 20.7449 8.68897 22.0923 10.0254 22.991C10.1813 23.0898 10.3343 23.1775 10.4845 23.2541C10.7179 23.5576 11.0021 23.8221 11.3255 24.0368C12.631 24.8632 13.7249 24.9209 15.1238 24.3842C16.0565 24.0254 16.7586 23.2167 17.0842 22.3206C17.2888 21.7611 17.2861 21.1978 17.2861 20.6154V4.04639H20.5417C20.6763 4.81139 21.0485 5.90039 22.0328 6.97898C22.4276 7.38624 22.8724 7.7463 23.3573 8.05134C23.5006 8.19955 24.2331 8.93231 25.1734 9.38216C25.6596 9.61469 26.1722 9.79285 26.7009 9.91314Z" fill="#000000"/>
                    <path d="M4.48926 22.7568V22.7594L4.57004 22.9784C4.56076 22.9529 4.53074 22.8754 4.48926 22.7568Z" fill="#69C9D0"/>
                    <path d="M10.5128 13.7916C9.67919 14.1002 8.90498 14.5396 8.22192 15.0918C7.44763 15.7332 6.79548 16.4987 6.29458 17.354C6.10521 17.6661 5.38897 18.9168 5.30161 20.9528C5.25223 22.1068 5.61361 23.2983 5.78561 23.7944C5.78543 23.7956 5.78543 23.7968 5.78561 23.798C5.89413 24.081 6.31791 25.0815 7.01191 25.9303C7.2135 26.1763 7.42963 26.4111 7.65924 26.6334C6.92357 26.1457 6.26746 25.5562 5.71236 24.8839C5.02433 24.0451 4.60001 23.0549 4.48932 22.7626C4.48919 22.7605 4.48919 22.7584 4.48932 22.7564V22.7527C4.31677 22.2571 3.95431 21.0651 4.00477 19.9096C4.09213 17.8736 4.80838 16.6239 4.99775 16.3108C5.4985 15.4553 6.15067 14.6898 6.92509 14.0486C7.608 13.4961 8.38225 13.0567 9.21598 12.7484C9.73602 12.5416 10.2778 12.3891 10.8319 12.2934C11.6669 12.1537 12.5198 12.1415 13.3588 12.2575V13.2196C12.3808 13.2349 11.4148 13.4291 10.5128 13.7916Z" fill="#69C9D0"/>
                    <path d="M20.5438 4.04635H17.2881V20.6159C17.2881 21.1983 17.2881 21.76 17.0863 22.3211C16.7575 23.2167 16.058 24.0253 15.1258 24.3842C13.7265 24.923 12.6326 24.8632 11.3276 24.0368C11.0036 23.823 10.7187 23.5594 10.4844 23.2567C11.5962 23.8251 12.5913 23.8152 13.8241 23.341C14.7558 22.9821 15.4563 22.1734 15.784 21.2774C15.9891 20.7178 15.9864 20.1546 15.9864 19.5726V3H20.4819C20.4819 3 20.4315 3.41188 20.5438 4.04635ZM26.7002 8.99104V9.9131C26.1725 9.79263 25.6609 9.61447 25.1755 9.38213C24.2352 8.93228 23.5026 8.19952 23.3594 8.0513C23.5256 8.1559 23.6981 8.25106 23.8759 8.33629C25.0192 8.88339 26.1451 9.04669 26.7002 8.99104Z" fill="#69C9D0"/>
                    </svg>
                </a>
                <!-- YouTube -->
                <a href="https://youtube.com/@myelement_cc" target="_blank" title="YouTube">
                    <svg width="40" height="40" viewBox="0 -7 48 48" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
                    <g id="Icons" stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
                    <g id="Color-" transform="translate(-200.000000, -368.000000)" fill="#CE1312">
                    <path d="M219.044,391.269916 L219.0425,377.687742 L232.0115,384.502244 L219.044,391.269916 Z M247.52,375.334163 C247.52,375.334163 247.0505,372.003199 245.612,370.536366 C243.7865,368.610299 241.7405,368.601235 240.803,368.489448 C234.086,368 224.0105,368 224.0105,368 L223.9895,368 C223.9895,368 213.914,368 207.197,368.489448 C206.258,368.601235 204.2135,368.610299 202.3865,370.536366 C200.948,372.003199 200.48,375.334163 200.48,375.334163 C200.48,375.334163 200,379.246723 200,383.157773 L200,386.82561 C200,390.73817 200.48,394.64922 200.48,394.64922 C200.48,394.64922 200.948,397.980184 202.3865,399.447016 C204.2135,401.373084 206.612,401.312658 207.68,401.513574 C211.52,401.885191 224,402 224,402 C224,402 234.086,401.984894 240.803,401.495446 C241.7405,401.382148 243.7865,401.373084 245.612,399.447016 C247.0505,397.980184 247.52,394.64922 247.52,394.64922 C247.52,394.64922 248,390.73817 248,386.82561 L248,383.157773 C248,379.246723 247.52,375.334163 247.52,375.334163 L247.52,375.334163 Z" id="Youtube"/>
                    </g>
                    </g>
                    </svg>
                </a>
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