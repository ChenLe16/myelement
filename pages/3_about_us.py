import streamlit as st

SUPPORT_EMAIL = "hello@myelement.cc"

st.title("About Us")

st.markdown(
    f"""
<div style='width:96%;margin:auto;margin-top:18px;'>

<h2 style='color:#ffe9b4;font-size:1.22em;font-weight:700;margin-bottom:4px;'>Vision</h2>
<p style='font-size:1.12em;color:#eaeaea; margin-bottom:18px;'>
Meaningful self-knowledge for everyone, powered by a timeless model and modern data.
</p>

<h2 style='color:#ffe9b4;font-size:1.14em;font-weight:700;margin-bottom:4px;'>What We Do</h2>
<p style='font-size:1.08em;color:#eaeaea;'>
We turn the classical Five-Element framework—<b>Wood · Fire · Earth · Metal · Water</b>—into a clear, numbers-first personality lens, as easy to use as MBTI or DISC.
</p>

<h2 style='color:#ffe9b4;font-size:1.14em;font-weight:700;margin-bottom:4px;'>Why It Works</h2>
<ol style='font-size:1.07em;color:#eaeaea;line-height:1.7em; margin-bottom:16px;'>
  <li><b>Historical data:</b> The model has guided East-Asian medicine and strategy for 2,000 years.</li>
  <li><b>Transparent maths:</b> Our open-source engine counts visible and hidden elemental tokens and weights them by season. No mystical “trust us”—you can inspect every rule.</li>
  <li><b>Actionable output:</b> Bar charts, strength scores, and plain-language insights you can apply to work, relationships, and habits.</li>
</ol>

<h2 style='color:#ffe9b4;font-size:1.14em;font-weight:700;margin-bottom:4px;'>What You’ll Get</h2>
<ul style='font-size:1.07em;color:#eaeaea;line-height:1.7em; margin-bottom:16px;'>
  <li>A private, instant report—generated in your browser, never stored on our servers.</li>
  <li>A single curated product recommendation (optional) that matches your elemental profile—nothing marketed as a cure-all.</li>
  <li>A growing library of evidence-based articles on creativity, focus, and stress viewed through the Five-Element lens.</li>
</ul>

<h2 style='color:#ffe9b4;font-size:1.14em;font-weight:700;margin-bottom:4px;'>Our Promise on Data</h2>
<p style='font-size:1.07em;color:#eaeaea;'>
We keep zero birth-data on our servers. Calculations run client-side; close the tab and the data disappears. End-to-end encryption secures any optional purchase details.
</p>

<h2 style='color:#ffe9b4;font-size:1.14em;font-weight:700;margin-bottom:4px;'>Join the Conversation</h2>
<p style='font-size:1.07em;color:#eaeaea;'>
Curious about the model, researching collaborations, or simply want to share feedback?<br>
→ <a href="mailto:{SUPPORT_EMAIL}" style='color:#ffe179;'>{SUPPORT_EMAIL}</a>
</p>

<p style='font-size:1.08em;color:#b1b1b1;margin-top:22px;font-style:italic;font-weight:600;'>
MyElement: tradition quantified, insight without superstition.
</p>

</div>
""", unsafe_allow_html=True)