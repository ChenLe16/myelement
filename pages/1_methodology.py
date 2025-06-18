import streamlit as st
from display_helpers import display_top_logo_bar, display_footer

display_top_logo_bar()

st.title("How We Calculate Your Results")

st.markdown("""
> **Our method in six clear steps**  
> No mysticism—just a data model built on the classical Five‑Element calendar.

### 1.&nbsp;&nbsp;Enter your birth details  
Your **date and exact time** act like a natural timestamp—just as tides follow the Moon, elemental cycles follow the Sun.

---

### 2.&nbsp;&nbsp;Turn that timestamp into four “pillars”  
We break the moment you were born into four time‑lenses—**Year, Month, Day, Hour**—so we can see long‑term trends (Year), everyday style (Month), core personality (Day), and your preferred problem‑solving rhythm (Hour). No fortune‑telling—just different zoom levels on the same moment.

| Pillar | What it highlights |
|---|---|
| **Year** | Early environment & social influence |
| **Month** | Work habits & operating style |
| **Day** | Core personality & values |
| **Hour** | Hidden potential & focus cycle |

---

### 3.&nbsp;&nbsp;Spot the natural elements in each pillar  
Every pillar carries one of the **Five Elements**.  These are classic nature‑analogies, not zodiac signs; they describe *how* an energy shows up, not whether it’s “good” or “bad”.

| Emoji | Element | Core themes |
|---|---|---|
| 🌳 | Wood  | Vision • Learning |
| 🔥 | Fire  | Expression • Motivation |
| 🪨 | Earth | Stability • Support |
| ⚔️ | Metal | Structure • Precision |
| 💧 | Water | Strategy • Adaptability |

---

### 4.&nbsp;&nbsp;Count visible **and hidden** elements  
We scan all four pillars—including background layers and seasonal boost—to count how many times each element really appears.  
*Example:* someone born in the middle of winter automatically gets extra points for **Water** (because winter is a Water season). If a tiny hint of **Metal** sits inside their Hour pillar, we add a small top‑up for Metal too. These tweaks make sure the meter reflects climate and hidden influences—not just the obvious symbols.

---

### 5.&nbsp;&nbsp;Convert counts into a star meter  
Your **Element Star Meter** (★☆☆☆☆ → ★★★★★) shows influence, not “good” or “bad.”  
More ★ = stronger presence; balance is ideal.  
*Example star meter:*

| Element | Stars |
|---|---|
| Wood  | ★★☆☆☆ |
| **Fire**  | **★★★★☆** |
| Earth | ★★☆☆☆ |
| Metal | ★★☆☆☆ |
| **Water** | **★☆☆☆☆** |

*(More ★ = stronger presence; balance beats maxing every bar.)*


*Quick takeaways*  

- **Fire (Expression • Motivation)** is your core driver — you thrive on energy, visibility, and inspiring others.  
- **Water (Strategy • Adaptability)** is your quietest element — strategic planning, research, or flexibility may require conscious effort.  
- Lean on your creative Fire spark and intentionally schedule reflection or long‑term planning (Water) to stay balanced.

---

### 6.&nbsp;&nbsp;Translate numbers into insights  
From the meter we generate clear guidance for **Personality**, **Career**, and **Relationships**.  
Think of it as a mirror, not a mold—you decide how to use the reflection.
""")

# Optional sample meter image (comment out if not available)
# st.image("assets/star_meter_sample.png", width=320,
#          caption="Example Element Star Meter")

st.info("🔒 **Privacy:** Calculations run in‑browser. We only store your data if you request a PDF report.")

# if st.button("Dive deeper on the blog 👉"):
#     st.switch_page("pages/4_blog.py")   # requires Streamlit multipage setup

# Footer
display_footer()