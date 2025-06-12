import streamlit as st
import pandas as pd
import datetime as dt
import pycountry
from bazi_constants import BG_GRADIENT, ELEMENT_SHADOW
from gsheet_helpers import append_to_gsheet, is_valid_email, make_unique_key

def display_custom_css():
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

def display_hero_section():
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

def display_main_input_form():
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

        st.warning(
            "⏱ **Exact birth time matters.** Even a five‑minute difference can change your results."
        )

        display_privacy_note()

        col1, col2, col3 = st.columns([2, 3, 2])
        with col2:
            generate_clicked = st.form_submit_button("✨ Generate My Elemental Star Meter")
    
    # Return all input values and the button state
    return name, gender, country, dob, hour, minute, generate_clicked

def display_user_summary(name, gender, country, dob, birth_time):
    st.markdown(
        f"""
        <div style='background-color:rgba(220,220,230,0.08); border-radius:12px; padding:16px 22px; margin-bottom:16px; text-align:center;'>
            <span style='font-weight:600; font-size:1.04em;'>Name:</span> {name}
            &nbsp; | &nbsp;
            <span style='font-weight:600; font-size:1.04em;'>Gender:</span> {gender}
            &nbsp; | &nbsp;
            <span style='font-weight:600; font-size:1.04em;'>Country:</span> {country}
            <br>
            <span style='font-weight:600; font-size:1.04em;'>Date of Birth:</span> {dob}
            &nbsp; | &nbsp;
            <span style='font-weight:600; font-size:1.04em;'>Birth Time:</span> {birth_time}
        </div>
        """,
        unsafe_allow_html=True
    )

def display_identity_card(dm_info):
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

def display_pillars_table(result):
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
    # ---- Add merged cell row for strength verdict ----
    table += f"""
        <tr>
            <td colspan="3" class="strength-row">
                Day Master Strength: <span style="color:{strength_color};">{verdict}</span>
            </td>
        </tr>
    """
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

def display_element_star_meter(result, identity_element=None):
    # Center the title
    st.markdown("<h4 style='text-align:center;'>Five Elements Star Meter</h4>", unsafe_allow_html=True)

    element_strengths = result['element_strengths']
    element_emojis = {
        "Wood": "🌳", "Fire": "🔥", "Earth": "🪨", "Metal": "🪙", "Water": "💧"
    }
    element_colors = {
        "Wood": "#58a862",
        "Fire": "#f25f3a",
        "Earth": "#c1915b",
        "Metal": "#d1b24a",
        "Water": "#378fcf",
    }

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
    .star-meter-table-dark th, .star-meter-table-dark td {
        font-size: 1.11em !important;
        padding: 8px 14px !important;
        font-weight: 600;
        border: none;
    }
    .star-meter-table-dark {
        width: 80% !important;
        margin-left: auto;
        margin-right: auto;
        border-radius: 11px;
        box-shadow: 0 1px 10px #23272e;
        background: #23262c;
    }
    .star-meter-table-dark tr {
        transition: background 0.18s, transform 0.25s;
        position: relative;
    }
    .star-meter-table-dark tr:hover {
        background: #242d34 !important;
        transform: scale(1.06);
        z-index: 2;
    }
    .star-meter-table-dark th {
        background: #21242a;
        color: #ffe9b4 !important;
        font-size:1.09em;
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
    table += "<tr><th>Element</th><th>Star Meter</th><th>Strength</th></tr>"
    for elem, val in element_strengths.items():
        label = f"{element_emojis.get(elem, '')}&nbsp;<span style='color:{element_colors[elem]}; font-weight:700'>{elem}</span>"
        if identity_element and elem == identity_element:
            label = f"{label} 🌟"
        stars = star_meter(val, color=element_colors[elem])
        label_strength = get_strength_label(val)
        table += f"<tr style='background-color:#23262c;'><td>{label}</td><td>{stars}</td><td>{label_strength}</td></tr>"
    table += "</table>"
    st.markdown(table, unsafe_allow_html=True)

    st.markdown(
        "<div style='color:#edc96d; background:rgba(64,44,0,0.08); text-align:center; font-size:1.03em; margin:12px 0 18px 0; border-radius:8px; padding:8px 10px 6px 10px;'>"
        "<b>Note:</b> <em>Your Elemental Identity (🌟) is not always your strongest star.</em>"
        "</div>",
        unsafe_allow_html=True
    )

# ---- Five Elements Scoring Breakdown Table ----
def display_element_score_breakdown(result):
    with st.expander("See how we calculate (advanced)"):
        st.markdown(
            "<h4 style='text-align:center;'>Five Elements Scoring Breakdown</h4>",
            unsafe_allow_html=True,
        )

        breakdown = result["element_score_breakdown"]
        element_order = ["Wood", "Fire", "Earth", "Metal", "Water"]
        element_emojis = {
            "Wood": "🌳",
            "Fire": "🔥",
            "Earth": "🪨",
            "Metal": "🪙",
            "Water": "💧",
        }

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
            emoji = element_emojis.get(elem, "")
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

def display_time_info(result, timezone_str):
    st.markdown(
        f"<div style='text-align:center; color:#78908b; margin-top:-0px; margin-bottom:0px; font-size:1.08em;'>"
        f"<div><b>Standard Time:</b> {result['standard_dt'].strftime('%Y-%m-%d %H:%M')}</div>"
        f"<div><b>Solar-corrected:</b> {result['solar_dt'].strftime('%Y-%m-%d %H:%M')}</div>"
        f"<div><b>Timezone:</b> {timezone_str}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

def display_privacy_note():
    st.markdown(
        """
        <div style='text-align:center; margin-top: 8px; margin-bottom: 14px;'>
            <span style='font-size:0.99em; color:#a9b7c6;'>
                <em>All calculations run locally. We only store your details if you ask us to email the full PDF report.</em>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

def display_paywall_card(
        product_name, stripe_checkout, product_pdf_cover, product_pdf_content, left_bullets, right_bullets
):
    # Session state setup
    if "paywall_confirm" not in st.session_state:
        st.session_state["paywall_confirm"] = False
    if "show_paywall_popup" not in st.session_state:
        st.session_state["show_paywall_popup"] = False

    st.header(
        f"{product_name}",
        help="6-page PDF report: core Five-Element analysis, chart visuals, guidance, and custom advice."
    )

    with st.container():
        row1_left, row1_right = st.columns([1.5, 1])
        with row1_left:
            st.subheader("What You Get")
            st.markdown("\n".join([f"- {item}" for item in left_bullets]))
        with row1_right:
            st.image(product_pdf_cover, use_container_width=True)

        row2_left, row2_right = st.columns([1, 1.5])
        with row2_left:
            st.image(product_pdf_content, use_container_width=True)
        with row2_right:
            st.subheader("Why It Matters")
            st.markdown("\n".join([f"- {item}" for item in right_bullets]))

        st.markdown(
            "<div style='margin: 0.8em 0 1.1em 0; font-size:1.07rem; color:#24cc80; "
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
                        st.info("Your upgrade request was logged!")
                    except Exception as e:
                        st.warning(f"Failed to log prospect to Google Sheet: {e}")

        if st.session_state["paywall_confirm"]:
            st.success("✅ Confirmed! [Proceed to payment](%s)" % stripe_checkout)
            st.markdown("**Your provided details:**")
            st.json({
                "Name": st.session_state.get("name"),
                "Email": paywall_email,
                "Gender": st.session_state.get("gender"),
                "Country": st.session_state.get("country"),
                "DOB": str(st.session_state.get("dob")),
                "Time": str(st.session_state.get("birth_time"))
            })

def display_pdf_request_form(state_dict):
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
                "✅ Request received! Your personalised PDF snapshot will land in your inbox "
                "within 48 hours. If you don’t see it, check spam or write us at "
                "myelement@gmail.com."
            )
        elif message == "duplicate":
            st.info("Looks like we already have your request — your PDF snapshot is on its way!")
        elif message.startswith("error:"):
            st.error("Unable to log to Google Sheet: " + message[6:])
        elif message == "warning":
            st.warning("Please enter a valid email address.")
        elif message == "consent":
            st.warning("Please tick the consent box to let us store your details.")

def display_footer():
    st.markdown(
        """
        <hr style="margin-top:30px; margin-bottom:10px; border:0; border-top:1px solid #333a44;">
        <div style='text-align:center; color:#a9b7c6; font-size:0.99em; margin-bottom:8px;'>
            &copy; 2025 MyElement. All rights reserved.
        </div>
        """,
        unsafe_allow_html=True,
    )

def section_divider():
    st.markdown("---")