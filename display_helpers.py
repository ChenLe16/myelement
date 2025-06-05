import streamlit as st
import pandas as pd

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

    pillar_emojis = {
        "Year": "🗓️",
        "Month": "🌙",
        "Day": "☀️",
        "Hour": "⏰"
    }
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
    with st.expander("Show details ▸"):
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

def display_element_star_meter(result):
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
        stars_html = f"<span style='font-size:1.09em; vertical-align:middle;'>"
        if score == 0:
            # Show '0 ★' in muted grey
            stars_html = f"<span style='color:#a9b7c6; font-weight:600; font-size:1.09em;'>0 ★</span>"
            return stars_html
        n_full = int(score)
        remainder = score - n_full
        n_half = 0
        # If exactly 0.5, show as a filled star for clarity
        if abs(score - 0.5) < 1e-8:
            n_full = 0
            n_half = 1
        else:
            if remainder >= 0.5:
                n_half = 1

        # Filled stars
        stars_html += f"<span style='color:{color}; font-weight:600;'>★</span>" * n_full
        # Half star logic: show filled star for 0.5, else empty star for other half (but per instructions only 0.5 is special)
        if n_half == 1:
            stars_html += f"<span style='color:{color}; font-weight:600;'>☆</span>"
        # Faded stars for remainder to make total 5 stars
        n_faded = max_stars - n_full - n_half
        stars_html += f"<span style='color:#555555;'>☆</span>" * n_faded
        stars_html += "</span>"
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
        width: 66% !important;
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

    table = "<table class='star-meter-table-dark'>"
    table += "<tr><th>Element</th><th>Star Meter</th></tr>"
    for elem, val in element_strengths.items():
        label = f"{element_emojis.get(elem, '')}&nbsp;<span style='color:{element_colors[elem]}; font-weight:700'>{elem}</span>"
        stars = star_meter(val, color=element_colors[elem])
        table += f"<tr style='background-color:#23262c;'><td>{label}</td><td>{stars}</td></tr>"
    table += "</table>"
    st.markdown(table, unsafe_allow_html=True)
    st.markdown("<div class='star-meter-legend'>★ = 0.5 points</div>", unsafe_allow_html=True)


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