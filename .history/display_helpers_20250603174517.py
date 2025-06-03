import streamlit as st
import pandas as pd

def display_pillars_table(result):
    st.markdown("#### Four Pillars Table (with Hidden Stems)")

    # Tooltip for each pillar
    pillar_tooltips = {
        "Year": "Ancestry, big environment, early life",
        "Month": "Parents, career foundation, youth/teen",
        "Day": "Your core self (Day Master), marriage, adult life",
        "Hour": "Children, thoughts, late life, ambitions"
    }
    pillar_emojis = {
        "Year": "🗓️",
        "Month": "🌙",
        "Day": "☀️",
        "Hour": "⏰"
    }
    pillar_colors = {
        "Year": "#8aa1b1",
        "Month": "#58a862",
        "Day": "#f25f3a",
        "Hour": "#378fcf"
    }
    pillars = [
        {"label": "Year",  "stem": result['year'][0],  "branch": result['year'][1],  "hidden": result['hidden_stems'][0]},
        {"label": "Month", "stem": result['month'][0], "branch": result['month'][1], "hidden": result['hidden_stems'][1]},
        {"label": "Day",   "stem": result['day'][0],   "branch": result['day'][1],   "hidden": result['hidden_stems'][2]},
        {"label": "Hour",  "stem": result['hour'][0],  "branch": result['hour'][1],  "hidden": result['hidden_stems'][3]},
    ]
    # Start HTML with custom CSS for hover
    st.markdown("""
    <style>
        .pillar-table { width:87%; margin:auto; border-radius:13px; box-shadow:0 1px 12px #e7e9f5; background:#fafbfd; }
        .pillar-table th, .pillar-table td { padding:9px 12px; border:none; }
        .pillar-table tr { transition: background 0.22s; }
        .pillar-table tr:hover { background:#e9f7f0 !important; }
        .pillar-table th { background: #e3edea; color: #346158; font-size:1.05em; }
    </style>
    """, unsafe_allow_html=True)
    table = "<table class='pillar-table'>"
    table += "<tr><th>Pillar</th><th>Heavenly Stem</th><th>Earthly Branch</th><th>Hidden Stem(s)</th></tr>"
    for p in pillars:
        emoji = pillar_emojis.get(p['label'], "")
        color = pillar_colors.get(p['label'], "#aaa")
        # Tooltip (HTML title)
        tooltip = pillar_tooltips.get(p['label'], "")
        # Day Master: bold, larger
        if p['label'] == "Day":
            stem_html = f"<span style='color:{color}; font-weight:900; font-size:1.20em'>{p['stem']}</span>"
        else:
            stem_html = f"<span style='color:{color}; font-weight:bold; font-size:1.08em'>{p['stem']}</span>"
        branch_html = f"<span style='color:#20403c; font-weight:500; font-size:1.08em'>{p['branch']}</span>"
        hidden_html = ", ".join(p['hidden']) if p['hidden'] else "-"
        table += (
            f"<tr style='background-color:#f7fafb;'>"
            f"<td title='{tooltip}' style='padding:9px 10px; font-weight:bold; color:{color}; cursor:help;'>{emoji}&nbsp;{p['label']}</td>"
            f"<td style='padding:9px 10px;'>{stem_html}</td>"
            f"<td style='padding:9px 10px;'>{branch_html}</td>"
            f"<td style='padding:9px 10px; color:#558'>{hidden_html}</td>"
            f"</tr>"
        )
    table += "</table>"
    st.markdown(table, unsafe_allow_html=True)

def star_meter(score, color="#ffd700"):
    n_full = int(score)
    n_half = 1 if score - n_full >= 0.5 else 0
    star_str = f"<span style='color:{color}; font-size:1.5em;'>"
    star_str += "★" * n_full
    if n_half:
        star_str += "☆"
    star_str += "</span>"
    return star_str

def display_element_star_meter(result):
    st.markdown("#### Five Elements Star Meter")
    element_strengths = result['element_strengths']
    element_emojis = {
        "Wood": "🌳", "Fire": "🔥", "Earth": "🪨", "Metal": "🪙", "Water": "💧"
    }
    element_colors = {
        "Wood": "#58a862",
        "Fire": "#f25f3a",
        "Earth": "#ddb76a",
        "Metal": "#8aa1b1",
        "Water": "#378fcf",
    }

    # Custom HTML table for better control over color/spacing
    table = "<table style='width:80%; margin:auto; border-radius:14px; box-shadow:0 1px 10px #dbeee8; background:#fafdfb;'>"
    table += "<tr><th style='text-align:left; padding:8px 10px;'>Element</th><th>Star Meter</th></tr>"
    for elem, val in element_strengths.items():
        label = f"{element_emojis.get(elem, '')}&nbsp;&nbsp;<span style='color:{element_colors[elem]}; font-weight:bold'>{elem}</span>"
        stars = star_meter(val, color=element_colors[elem])
        table += f"<tr style='background-color:#f8fcfa;'><td style='padding:9px 10px;'>{label}</td><td style='font-size:1.4em; padding:9px 10px;'>{stars}</td></tr>"
    table += "</table>"
    st.markdown(table, unsafe_allow_html=True)