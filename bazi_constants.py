import datetime as dt

SUPPORT_EMAIL = "hello@myelement.cc"

# ————————————————————————————————————————————————————
# Constants and Mappings
# ————————————————————————————————————————————————————
STEM   = "甲乙丙丁戊己庚辛壬癸"
BRANCH = "子丑寅卯辰巳午未申酉戌亥"
JIA_ZI = [STEM[i % 10] + BRANCH[i % 12] for i in range(60)]
ORD_EPOCH = dt.date(1899, 12, 22).toordinal()        # 甲子日

# Stem/branch to element
STEM_ELEM   = ["Wood","Wood","Fire","Fire","Earth",
               "Earth","Metal","Metal","Water","Water"]
BRANCH_ELEM = ["Water","Earth","Wood","Wood","Earth","Fire",
               "Fire","Earth","Metal","Metal","Earth","Water"]

# Earthly Branch hidden stems
BRANCH_HIDDEN = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "庚", "戊"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"],
}

# Seasonal bonus per month branch
SEASON_BONUS = {
    "寅":{"Wood":2,"Fire":1,"Earth":0,"Metal":-1,"Water":-2},
    "卯":{"Wood":2,"Fire":1,"Earth":0,"Metal":-1,"Water":-2},
    "辰":{"Wood":1,"Fire":0,"Earth":1,"Metal":0,"Water":-1},
    "巳":{"Fire":2,"Earth":1,"Wood":0,"Metal":-1,"Water":-2},
    "午":{"Fire":2,"Earth":1,"Wood":0,"Metal":-1,"Water":-2},
    "未":{"Earth":1,"Fire":1,"Wood":0,"Metal":0,"Water":-1},
    "申":{"Metal":2,"Water":1,"Earth":0,"Wood":-1,"Fire":-1},
    "酉":{"Metal":2,"Water":1,"Earth":0,"Wood":-1,"Fire":-1},
    "戌":{"Earth":1,"Metal":1,"Fire":0,"Wood":-1,"Water":0},
    "亥":{"Water":2,"Wood":1,"Earth":-1,"Fire":-2,"Metal":0},
    "子":{"Water":2,"Metal":0,"Earth":-1,"Fire":-2,"Wood":0},
    "丑":{"Earth":1,"Metal":1,"Water":0,"Wood":-1,"Fire":0},
}

# --- Shared constants for element emojis and colors ---
ELEMENT_EMOJIS = {
    "Wood": "🌳",
    "Fire": "🔥",
    "Earth": "🪨",
    "Metal": "⚔️",
    "Water": "💧",
}
ELEMENT_COLORS = {
    "Wood": "#58a862",
    "Fire": "#f25f3a",
    "Earth": "#c1915b",
    "Metal": "#d1b24a",
    "Water": "#378fcf",
}

# Shadow colour per element — used to keep text crisp on matching backgrounds
ELEMENT_SHADOW = {
    "Wood":  "0 2px 6px rgba(9,39,25,0.65)",
    "Fire":  "0 2px 6px rgba(120,30,0,0.55)",
    "Earth": "0 2px 6px rgba(64,32,8,0.55)",
    "Metal": "0 2px 6px rgba(20,29,46,0.6)",
    "Water": "0 3px 10px rgba(0,0,0,0.75)",
}

# ── Identity mappings ───────────────────────────────────────

# Unified dictionary for Day Master identities and attributes
DAY_MASTER_IDENTITIES = {
    "甲": {
        "header": "The Resolute Oak",
        "traits": "Steady growth, long‑range vision; anchors big projects.",
        "takeaway": "Lean on your capacity for endurance when teams lose focus. Stay open to new methods so you don’t become rigid.",
        "element": "Wood",
        "polarity": "Yang",
        "color": "#2E8B57",
        "emoji": "🌳",
        "stem": "Oak",
        "career": "Long-horizon projects—urban planning, R&D, policy—let your vision take root. Teams rely on your calm persistence and clear scaffolding of goals. You excel at mapping big forests before anyone else sees the trees.",
        "growth": "Growth comes from pruning: each quarter, drop one stagnant initiative so new branches get sunlight. Keep a “cut list” beside your to-do list; your energy soars when sap flows to fresh shoots.",
        "relationship": "Loyalty runs deep, but rigidity can harden bark. Before saying no, ask a clarifying question; flexibility in small moments keeps relationships from feeling fenced in.",
    },
    "乙": {
        "header": "The Adaptive Willow",
        "traits": "Flexible thinker; links ideas and people with ease.",
        "takeaway": "Your agility is a super-connector—use it to translate between specialists. Guard against spreading yourself too thin; pick one root project to deepen.",
        "element": "Wood",
        "polarity": "Yin",
        "color": "#2E8B57",
        "emoji": "🌿",
        "stem": "Vine",
        "career": "Connector roles—UX research, partnership building, diplomacy—benefit from your ability to weave people and ideas into sturdy lattices. You translate abstract vision into living networks.",
        "growth": "Anchor weekly “trellis points”: clear deliverables that keep you from spiraling into endless options. Small structure turns your adaptability into upward momentum instead of sideways sprawl.",
        "relationship": "You listen like light rain—people blossom. Share your own aspirations aloud so partners can wrap support around you instead of guessing your direction.",
    },
    "丙": {
        "header": "The Radiant Sun",
        "traits": "Energises groups and sparks momentum.",
        "takeaway": "People mirror your enthusiasm, so set the tone deliberately. Schedule quiet “eclipse” time to keep from burning out.",
        "element": "Fire",
        "polarity": "Yang",
        "color": "#FF7518",
        "emoji": "🌞",
        "stem": "Sun",
        "career": "Launch teams, sales rallies, classrooms: environments needing instant ignition thrive on your radiance. Your best work appears in sprints where optimism galvanises action.",
        "growth": "Schedule deliberate “eclipse hours” every day—phones off, blinds half-drawn—to let heat condense into new fuel. Without dusk, tomorrow’s sunrise dims.",
        "relationship": "Warmth attracts, but unfiltered glare scorches. Offer drafts of big ideas so loved ones co-create, rather than receiving finished orders.",
    },
    "丁": {
        "header": "The Enduring Ember",
        "traits": "Sustains warm focus; mentors and refines goals.",
        "takeaway": "Your steady glow excels in 1-to-1 guidance—cultivate mentorship roles. Beware of dimming when recognition is delayed; celebrate small wins.",
        "element": "Fire",
        "polarity": "Yin",
        "color": "#FF7518",
        "emoji": "🔥",
        "stem": "Ember",
        "career": "Editorial, coaching, craftsmanship: places where steady warmth cures raw material into durable quality. You excel at slow roasting complexity into clarity.",
        "growth": "Guard the hearth; reject one extra request daily. Your flame glows longest when tended, not spread thin.",
        "relationship": "Subtle encouragement is your love language. Speak discomfort early—small sparks are easier than sudden flare-ups later.",
    },
    "戊": {
        "header": "The Grounded Mountain",
        "traits": "Reliable planner; sees the whole terrain before acting.",
        "takeaway": "Strategic patience lets you solve problems others rush past. Stay receptive to feedback so analysis doesn’t turn into immobility.",
        "element": "Earth",
        "polarity": "Yang",
        "color": "#C27C48",
        "emoji": "⛰️",
        "stem": "Mountain",
        "career": "Operations management, infrastructure, finance—roles needing unshakable footing suit your geological patience. Crisis feels like mild weather to you.",
        "growth": "Invite a “seismic idea” each month—podcast, debate, prototype. Fresh layers keep the summit from eroding into routine.",
        "relationship": "Reliability comforts partners, yet surprise picnics or spontaneous road trips show there’s life beyond the trailhead and deepen intimacy.",
    },
    "己": {
        "header": "The Cultivating Marble",
        "traits": "Patient craftsman; turns rough ideas into polished results.",
        "takeaway": "Your eye for detail builds lasting value—own the refinement phase. Balance perfectionism with deadlines to keep momentum.",
        "element": "Earth",
        "polarity": "Yin",
        "color": "#C27C48",
        "emoji": "🪨",
        "stem": "Garden",
        "career": "HR, project coordination, health coaching—any space requiring steady cultivation benefits from your nutrient-rich presence.",
        "growth": "Over-tending saps soil. Designate one “hands-off” day weekly: watch your seedlings grow without intervention and gain trust in organic processes.",
        "relationship": "You serve love on porcelain plates; also ask plainly for what replenishes you. Balanced exchange keeps your ground fertile.",
    },
    "庚": {
        "header": "The Strategic Sword",
        "traits": "Decisive and direct—cuts through complexity to solutions.",
        "takeaway": "Teams rely on your clarity; wield it to unblock consensus. Temper rapid judgement with empathy to avoid unintended cuts.",
        "element": "Metal",
        "polarity": "Yang",
        "color": "#8E97A8",
        "emoji": "⚔️",
        "stem": "Sword",
        "career": "Consulting, surgery, cybersecurity: fields where precise cuts turn chaos into clean lines. People hire you to separate signal from noise fast.",
        "growth": "Pair every critique with a curiosity question—sharpening empathy protects your edge from turning cold.",
        "relationship": "Directness builds trust when wrapped in context. Offer the motive behind the slice so allies feel refined, not reduced.",
    },
    "辛": {
        "header": "The Discerning Jewel",
        "traits": "Precise, value‑driven; elevates hidden quality.",
        "takeaway": "You instinctively spot what’s precious—apply that to both tasks and people. Remember not everyone craves the same level of polish; choose battles.",
        "element": "Metal",
        "polarity": "Yin",
        "color": "#8E97A8",
        "emoji": "💎",
        "stem": "Jewel",
        "career": "QA, luxury branding, fine design—places valuing refinement, nuance, and polished detail showcase your brilliance.",
        "growth": "Reveal unfinished facets to a trusted peer each week. Collaboration buffs hidden angles faster than solo polishing.",
        "relationship": "Selective circles feel safe; occasionally invite novelty to avoid being locked in a display case of your own making.",
    },
    "壬": {
        "header": "The Dynamic Wave",
        "traits": "Exploratory, big‑picture thinker driving new ventures.",
        "takeaway": "Your breadth fuels innovation—map bold routes others don’t see. Anchor ideas with concrete milestones so they don’t dissipate.",
        "element": "Water",
        "polarity": "Yang",
        "color": "#5CD1E8",
        "emoji": "🌊",
        "stem": "Wave",
        "career": "Innovation strategy, investigative journalism, global sales—wide horizons feed your rolling curiosity and capacity to move ideas across borders.",
        "growth": "Build monthly “harbour checkpoints” for still-water reflection; depth turns restless surf into navigable current.",
        "relationship": "Your network is vast; deepen by choosing three anchors—people who receive the full tide, not just passing waves.",
    },
    "癸": {
        "header": "The Reflective Rain",
        "traits": "Calm insight‑giver; nourishes teams with clarity.",
        "takeaway": "Quiet observation lets you solve root issues others miss. Speak insights early; withholding too long can flood the project later.",
        "element": "Water",
        "polarity": "Yin",
        "color": "#5CD1E8",
        "emoji": "💧",
        "stem": "Rain",
        "career": "Research, therapy, novel-writing: quiet penetration of detail produces insights others overlook.",
        "growth": "Speak emotions aloud; mist condenses into clear water only when given shape. Journaling or voice notes lock insight into usable form.",
        "relationship": "Gentle nourishment builds trust, but vanish-and-return cycles confuse partners. Signal when clouds gather, and they’ll wait out the weather with you.",
    },
}

# ── Elemental Identity Spotlight Section ──────────────
BG_GRADIENT = {
    "Wood":  "linear-gradient(135deg, #134e3a 0%, #2E8B57 100%)",
    "Fire":  "linear-gradient(135deg, #ff7518 0%, #ffb347 100%)",
    "Earth": "linear-gradient(135deg, #c27c48 0%, #ffe0b2 100%)",
    "Metal": "linear-gradient(135deg, #8e97a8 0%, #1d2431 100%)",
    "Water": "linear-gradient(135deg, #11998e 0%, #003344 100%)",
}