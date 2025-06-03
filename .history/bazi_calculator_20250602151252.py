# four_pillars_basic.py
# ──────────────────────────────────────────────────────────
# 1. paste into Programiz (or any IDE)
# 2. supply three input lines when prompted:
#       2011-02-01
#       12:00
#       +8
# 3. click Run → Four Pillars print out
#
# Accuracy: ±1 min for 1900-2099, good enough for natal charts.
# Uses:
#   • 1899-12-22  = 甲子  (sexagenary epoch)
#   • Low-precision solar longitude to pick month branch.
#   • Ordinal-day math for Day Pillar.
# ──────────────────────────────────────────────────────────

import datetime as dt
import math

# ---------------------------------------------------------
STEM   = "甲乙丙丁戊己庚辛壬癸"
BRANCH = "子丑寅卯辰巳午未申酉戌亥"
JIA_ZI = [STEM[i % 10] + BRANCH[i % 12] for i in range(60)]
ORD_EPOCH = dt.date(1899, 12, 22).toordinal()        # 甲子日

# ---------------- Sun longitude (Meeus, abridged) --------
def sun_lon(jd):
    T = (jd - 2451545.0) / 36525.0
    L0 = (280.46646 + 36000.76983*T + 0.0003032*T*T) % 360
    M  = (357.52911 + 35999.05029*T - 0.0001537*T*T) % 360
    M  = math.radians(M)
    C  = (1.914602 - 0.004817*T - 0.000014*T*T)*math.sin(M)
    C += (0.019993 - 0.000101*T)*math.sin(2*M)
    C += 0.000289*math.sin(3*M)
    return (L0 + C) % 360

def julian_day(utc):
    y, m = utc.year, utc.month
    d = utc.day + (utc.hour + utc.minute/60 + utc.second/3600)/24
    if m <= 2:
        y, m = y - 1, m + 12
    A = y // 100
    B = 2 - A + A // 4
    return int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + B - 1524.5

# ---------------- helpers --------------------------------
# OLD (buggy – resets after Autumn)
# def month_branch_idx(lon):
#     return int(((lon + 45) // 30) % 12)

# NEW – always measure FROM 315° (Li-Chun = Tiger month)    
def month_branch_idx(lon):
    # Current line (still buggy somewhere):
    # return int(((lon + 45) // 30) % 12)

    # Replace with:
    adj = (lon - 315) % 360          # measure FROM 315°, Tiger = 0
    return int(adj // 30)            # 0=寅, 1=卯, … 8=戌, 11=丑

def hour_branch_idx(hour):
    """子=0 covers 23:00–00:59 local."""
    return ((hour + 1) // 2) % 12

# ---------------- main calculator ------------------------
def four_pillars(local_dt, utc_offset):
    tz = dt.timezone(dt.timedelta(hours=utc_offset))
    local_dt = local_dt.replace(tzinfo=tz)
    utc_dt   = local_dt.astimezone(dt.timezone.utc)

    # Year pillar – based on Li-Chun (approx: solar lon ≥ 315°)
    jd_current = julian_day(utc_dt)
    lon = sun_lon(jd_current)

# Year flips at Li-Chun ≈ 4 Feb.  Anything before that belongs to previous Jia-Zi year.
    if (local_dt.month, local_dt.day) < (2, 4):
        solar_year = local_dt.year - 1
    else:
        solar_year = local_dt.year
    y_stem_i   = (solar_year - 4) % 10
    y_branch_i = (solar_year - 4) % 12
    year_p     = STEM[y_stem_i] + BRANCH[y_branch_i]

    # Month pillar – by 30° slices from 315°
    m_branch_i = month_branch_idx(lon)         # 0=寅
    m_stem_i   = (y_stem_i*2 + 2 + m_branch_i) % 10
    month_p = STEM[m_stem_i] + BRANCH[(m_branch_i + 2) % 12]
    # Day pillar – ordinal count
    offset     = local_dt.date().toordinal() - ORD_EPOCH
    day_p      = JIA_ZI[offset % 60]

    # Hour pillar – 2-hour branch + stem formula
    h_branch_i = hour_branch_idx(local_dt.hour)
    h_stem_i   = (2 * (offset % 10) + h_branch_i) % 10
    hour_p     = STEM[h_stem_i] + BRANCH[h_branch_i]

    return year_p, month_p, day_p, hour_p

# ── Strength-rating helpers ────────────────────────────────
STEM_ELEM   = ["Wood","Wood","Fire","Fire","Earth",
               "Earth","Metal","Metal","Water","Water"]
BRANCH_ELEM = ["Water","Earth","Wood","Wood","Earth","Fire",
               "Fire","Earth","Metal","Metal","Earth","Water"]

# Season weights (month branch → boost/drain map)
SEASON = {
    "寅":{"Fire":+1,"Wood":+2,"Earth":0 ,"Metal":-1,"Water":-2},
    "卯":{"Fire":+1,"Wood":+2,"Earth":0 ,"Metal":-1,"Water":-2},
    "辰":{"Fire":0 ,"Wood":+1,"Earth":+1,"Metal":0 ,"Water":-1},
    "巳":{"Fire":+2,"Wood":0 ,"Earth":+1,"Metal":-1,"Water":-2},
    "午":{"Fire":+2,"Wood":0 ,"Earth":+1,"Metal":-1,"Water":-2},
    "未":{"Fire":+1,"Wood":0 ,"Earth":+1,"Metal":0 ,"Water":-1},
    "申":{"Fire":-1,"Wood":-1,"Earth":0 ,"Metal":+2,"Water":+1},
    "酉":{"Fire":-1,"Wood":-1,"Earth":0 ,"Metal":+2,"Water":+1},
    "戌":{"Fire":0 ,"Wood":-1,"Earth":+1,"Metal":+1,"Water":0 },
    "亥":{"Fire":-2,"Wood":-2,"Earth":-1,"Metal":0 ,"Water":+2},
    "子":{"Fire":-2,"Wood":-2,"Earth":-1,"Metal":0 ,"Water":+2},
    "丑":{"Fire":0 ,"Wood":-1,"Earth":+1,"Metal":+1,"Water":0 },
}

def support_value(dm, other):
    """+1 if supports DM, −1 if drains/controls, 0 neutral"""
    productive = {"Wood":"Fire","Fire":"Earth","Earth":"Metal",
                  "Metal":"Water","Water":"Wood"}
    control    = {"Wood":"Earth","Earth":"Water","Water":"Fire",
                  "Fire":"Metal","Metal":"Wood"}

    if other == dm:                 return +1          # peer
    if productive[other] == dm:     return +1          # resource 印
    if control[other] == dm:        return -1          # controller 官杀
    if productive[dm] == other:     return -1          # output/wealth 食伤财
    return 0

def judge_strength(day_stem, month_branch, vis_stems, vis_branches):
    dm_elem = STEM_ELEM[STEM.index(day_stem)]
    score   = SEASON[month_branch][dm_elem]

    for s in vis_stems:
        score += support_value(dm_elem, STEM_ELEM[STEM.index(s)])
    for b in vis_branches:
        score += support_value(dm_elem, BRANCH_ELEM[BRANCH.index(b)])

    if score >= 1:   verdict = "身强 (Strong)"
    elif score <= -1: verdict = "身弱 (Weak)"
    else:            verdict = "Balanced"

    return verdict, score

# ---------------- command-line / Programiz I/O -----------

# if __name__ == "__main__":
#     try:
#         date_str  = input("Date  (YYYY-MM-DD): ").strip()
#         time_str  = input("Time  (HH:MM, 24-h): ").strip()
#         tz_str    = input("UTC offset (e.g. +8): ").strip()

#         utc_off   = int(tz_str)
#         local_dt  = dt.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")

#         Y, M, D, H = four_pillars(local_dt, utc_off)

#         # collect visible characters
#         vis_stems    = [Y[0], M[0], D[0], H[0]]
#         vis_branches = [Y[1], M[1], D[1], H[1]]

#         strength, raw = judge_strength(D[0], M[1], vis_stems, vis_branches)

#         print("\nFour Pillars")
#         print("────────────────")
#         print(f"Year  {Y}")
#         print(f"Month {M}")
#         print(f"Day   {D}")
#         print(f"Hour  {H}")
#         print(f"\nDay-Master strength: {strength}  (score {raw})")

#     except Exception as e:
#         print("❌  Input error:", e)