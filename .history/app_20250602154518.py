import streamlit as st
import datetime as dt
from bazi_calculator import (
    four_pillars,       # main calc
    judge_strength,     # DM strength check
    STEM                # we need this for element lookup
)

st.set_page_config(page_title="MyElement – BaZi MVP", page_icon="🌿")

st.title("🌿 MyElement – Discover Your Four Pillars")

# ── 1. User Inputs ────────────────────────────────────────
MIN_DATE = dt.date(1900, 1, 1)
DEFAULT_D = dt.date.today()
MAX_DATE = dt.date.today() + dt.timedelta(days=365*2)

name   = st.text_input("Name")
gender = st.selectbox("Gender", ["Male", "Female"])
# the reason why is because the earliest date can be chosen is 2015.
dob = st.date_input(
    "Date of Birth",
    value=DEFAULT_D,
    min_value=MIN_DATE,
    max_value=MAX_DATE
)

col1, col2 = st.columns(2)

with col1:
    hour = st.selectbox("Hour (H)", list(range(0, 24)), index=12)
with col2:
    minute = st.selectbox("Minute (M)", list(range(0, 60)), index=0)

# Combine into a time object for your calculation
tob = dt.time(hour, minute)

utc_off = st.number_input("UTC offset (e.g. +8 for Malaysia)", value=8, step=1)

# ── 2. Run calculation when button clicked ───────────────
if st.button("Generate My Pillars"):
    try:
        # combine date & time into datetime object
        local_dt = dt.datetime.combine(dob, tob)

        # 2-A. Core Four-Pillars calculation
        Y, M, D, H = four_pillars(local_dt, int(utc_off))

        # 2-B. Judge Day-Master strength
        vis_stems    = [Y[0], M[0], D[0], H[0]]
        vis_branches = [Y[1], M[1], D[1], H[1]]
        strength, raw = judge_strength(
            day_stem=D[0],
            month_branch=M[1],
            vis_stems=vis_stems,
            vis_branches=vis_branches
        )

        # ── 3. Display results ────────────────────────────
        st.subheader("Your Four Pillars")
        st.write(f"**Year  :** {Y}")
        st.write(f"**Month :** {M}")
        st.write(f"**Day   :** {D}  ← *Day Master*")
        st.write(f"**Hour  :** {H}")

        st.markdown("---")
        st.subheader("Day-Master Strength")
        st.success(f"{strength}  (score {raw:+d})")

    except Exception as e:
        st.error(f"❌ Something went wrong: {e}")