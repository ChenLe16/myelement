import streamlit as st
import os
import re
from datetime import datetime

st.title("Blog")

BLOG_DIR = "blog_posts"
posts = []

# Helper to parse metadata
def parse_post(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    # Extract YAML-like metadata (date & title)
    meta_match = re.match(r"---\s*date:\s*(.+?)\s*title:\s*(.+?)\s*---\s*", content, re.DOTALL)
    if meta_match:
        date_str, title = meta_match.groups()
        date = datetime.strptime(date_str.strip(), "%Y-%m-%d")
        body = content[meta_match.end():]
    else:
        date = datetime.min
        title = os.path.basename(filepath).replace("-", " ").replace(".md", "").title()
        body = content
    return {"date": date, "title": title, "body": body, "file": filepath}

# Load all posts
for filename in os.listdir(BLOG_DIR):
    if filename.endswith(".md"):
        fullpath = os.path.join(BLOG_DIR, filename)
        posts.append(parse_post(fullpath))

# Sort posts by date (latest first)
posts.sort(key=lambda x: x["date"], reverse=True)

if not posts:
    st.info("No blog posts yet!")
else:
    for post in posts:
        st.markdown(f"#### {post['title']}")
        st.markdown(f"<span style='color:#b1b1b1; font-size:0.96em;'>Posted on {post['date'].strftime('%Y-%m-%d')}</span>", unsafe_allow_html=True)
        st.markdown(post["body"], unsafe_allow_html=True)
        st.markdown("---")