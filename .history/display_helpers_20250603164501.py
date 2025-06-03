import streamlit as st
import pandas as pd

def display_pillars_table(result):
    st.markdown("#### Four Pillars Table (with Hidden Stems)")
    pillars = [
        {"stem": result['year'][0],  "branch": result['year'][1],  "hidden": result['hidden_stems'][0]},
        {"stem": result['month'][0], "branch": result['month'][1], "hidden": result['hidden_stems'][1]},
        {"stem": result['day'][0],   "branch": result['day'][1],   "hidden": result['hidden_stems'][2]},
        {"stem": result['hour'][0],  "branch": result['hour'][1],  "hidden": result['hidden_stems'][3]},
    ]
    table_data = {
        "Heavenly Stem": [p['stem'] for p in pillars],
        "Earthly Branch": [p['branch'] for p in pillars],
        "Hidden Stem(s)": [", ".join(p['hidden']) if p['hidden'] else "-" for p in pillars],
    }
    df = pd.DataFrame(table_data, index=["Year", "Month", "Day", "Hour"])
    st.dataframe(df, use_container_width=True)

def display_element_star_meter(result):
    st.markdown("#### Five Elements Star Meter")
    element_strengths = result['element_strengths']

    # Use: ★ (full), ☆ (half)
    def star_meter(score):
        n_full = int(score)
        n_half = 1 if score - n_full >= 0.5 else 0
        star_str = "★" * n_full
        if n_half:
            star_str += "☆"
        return star_str

    star_table = {
        "Element": [],
        "Strength": [],
        "Stars": [],
    }
    for elem, val in element_strengths.items():
        star_table["Element"].append(elem)
        star_table["Strength"].append(val)
        star_table["Stars"].append(star_meter(val))
    df_star = pd.DataFrame(star_table)
    st.dataframe(df_star, use_container_width=True)