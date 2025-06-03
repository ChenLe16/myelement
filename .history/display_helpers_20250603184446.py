import streamlit as st
import pandas as pd

def display_pillars_table(result):
    st.markdown("<h4 style='text-align:center;'>Four Pillars Table (with Hidden Stems)</h4>", unsafe_allow_html=True)

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
    # ---- verdict logic ----
    verdict = result.get("strength", "")

    st.markdown("""
    <style>
        .pillar-table-dark {
            border-collapse: separate;
            border-spacing: 0;
            border-radius:13px;
            box-shadow:0 1px 12px #23272e;
            background:#23262c;
            width:87%; margin:auto;
            overflow: hidden;
        }
        .pillar-table-dark th, .pillar-table-dark td {
            padding:9px 12px;
            border:none;
            color: #eaeaea !important;
        }
        .pillar-table-dark tr {
            transition: background 0.22s, transform 0.25s;
            position: relative;
        }
        .pillar-table-dark tr:hover {
            background:#242d34 !important;
            transform: scale(1.06);
            z-index: 2;
        }
        .pillar-table-dark tr:first-child th {
            border-top-left-radius: 13px;
            border-top-right-radius: 13px;
        }
        .pillar-table-dark tr:last-child td {
            border-bottom-left-radius: 13px;
            border-bottom-right-radius: 13px;
        }
        .pillar-table-dark tr:hover:first-child th {
            border-top-left-radius: 16px !important;
            border-top-right-radius: 16px !important;
        }
        .pillar-table-dark tr:hover:last-child td {
            border-bottom-left-radius: 16px !important;
            border-bottom-right-radius: 16px !important;
        }
        .pillar-table-dark th {
            background: #21242a;
            color: #ffe9b4 !important;
            font-size:1.09em;
        }
        .strength-row {
            background: #272c32;
            text-align: center;
            font-size: 1.19em;
            font-weight: bold;
            letter-spacing: 0.01em;
            padding: 15px 10px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    table = "<table class='pillar-table-dark'>"
    table += "<tr><th>Pillar</th><th>Heavenly Stem</th><th>Earthly Branch</th><th>Hidden Stem(s)</th></tr>"
    for p in pillars:
        emoji = pillar_emojis.get(p['label'], "")
        stem_html = f"<span style='font-weight:bold; font-size:1.07em'>{p['stem']}</span>"
        branch_html = f"<span style='font-weight:500; font-size:1.07em'>{p['branch']}</span>"
        hidden_html = ", ".join(p['hidden']) if p['hidden'] else "-"
        table += (
            f"<tr style='background-color:#23262c;'>"
            f"<td style='padding:9px 10px; font-weight:bold; color:#ffe9b4;'>{emoji}&nbsp;{p['label']}</td>"
            f"<td style='padding:9px 10px; color:#eaeaea'>{stem_html}</td>"
            f"<td style='padding:9px 10px; color:#eaeaea'>{branch_html}</td>"
            f"<td style='padding:9px 10px; color:#b2b2b2'>{hidden_html}</td>"
            f"</tr>"
        )
    # ---- Add merged cell row for strength verdict ----
    strength_color = "#fab74b" if verdict == "Strong" else "#44c4fa"
    table += f"""
        <tr>
            <td colspan="4" class="strength-row">
                Day Master Strength: <span style="color:{strength_color};">{verdict}</span>
            </td>
        </tr>
    """
    table += "</table>"
    st.markdown(table, unsafe_allow_html=True)

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
        n_full = int(score)
        n_half = 1 if score - n_full >= 0.5 else 0
        star_str = f"<span style='color:{color}; font-size:1.09em; vertical-align:middle;'>"
        star_str += "★" * n_full
        if n_half:
            star_str += "☆"
        star_str += "</span>"
        return star_str

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