# privacy.py  – Streamlit multipage
import streamlit as st

PRIVACY_EMAIL = "privacy@myelement.cc"

st.title("Privacy & Data Policy")

st.markdown(f"""
### What we store  
We save your name, email, birth details, and gender **only** when you tick the
consent box to receive a PDF report or newsletter.

### How we use it  
* Generate the PDF report you requested  
* Email you occasional product updates

### How to delete your data  
Send an email to **{PRIVACY_EMAIL}**, with the subject line **DELETE**.  
We will erase your record from our server within 24 hours and email you a confirmation.

### Third-party services  
* Google Sheets – secure storage of the rows you submit  
* SendGrid – emails (TLS-encrypted in transit)

We never sell or share your data with anyone else.
""")