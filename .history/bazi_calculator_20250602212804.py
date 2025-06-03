import datetime as dt
import math

# ————————————————————————————————————————————————————
# Solar Time Correction Functions
# ————————————————————————————————————————————————————

def equation_of_time(dt_date):
    """
    Approximate the equation of time (in minutes) for the given date.
    Formula: https://en.wikipedia.org/wiki/Equation_of_time#Calculating_the_equation_of_time
    """
    N = dt_date.timetuple().tm_yday
    B = 2 * math.pi * (N - 81) / 364
    EoT = 9.87 * math.sin(2*B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)
    return EoT  # in minutes

def longitude_correction(local_longitude, reference_longitude):
    """
    Return the longitude correction in minutes: (ref_long - local_long) * 4
    East is positive.
    """
    return (reference_longitude - local_longitude) * 4

def solar_corrected_time(dob, birth_time, local_longitude, utc_offset):
    """
    Returns solar-corrected datetime for BaZi (and breakdown for debugging).
    - dob: datetime.date
    - birth_time: datetime.time
    - local_longitude: float (degrees East)
    - utc_offset: float (hours, e.g. 8.0 for Malaysia)
    """
    naive_local_dt = dt.datetime.combine(dob, birth_time)
    reference_longitude = utc_offset * 15  # 15° per hour of timezone
    long_corr_min = longitude_correction(local_longitude, reference_longitude)
    EoT_min = equation_of_time(dob)
    corrected_dt = naive_local_dt - dt.timedelta(minutes=long_corr_min) + dt.timedelta(minutes=EoT_min)
    return corrected_dt, naive_local_dt, long_corr_min, EoT_min

# ————————————————————————————————————————————————————
# BaZi (Four Pillars) Core Logic (unchanged)
# ————————————————————————————————————————————————————

STEM   = "甲乙丙丁戊己庚辛壬癸"
BRANCH = "子丑寅卯辰巳午未申酉戌亥"
JIA_ZI = [STEM[i % 10] + BRANCH[i % 12] for i in range(60)]
ORD_EPOCH = dt.date(1899, 12, 22).toordinal()        # 甲子日

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

def month_branch_idx(lon):
    adj = (lon - 315) % 360          # measure FROM 315°, Tiger = 0
    return int(adj // 30)            # 0=寅, 1=卯, … 8=戌, 11=丑

def hour_branch_idx(hour):
    """子=0 covers 23:00–00:59 local."""
    return ((hour + 1) // 2) % 12

def four_pillars(local_dt, utc_offset):
    tz = dt.timezone(dt.timedelta(hours=utc_offset))
    local_dt = local_dt.replace(tzinfo=tz)
    utc_dt   = local_dt.astimezone(dt.timezone.utc)

    # Year pillar – based on Li-Chun (approx: solar lon ≥ 315°)
    jd_current = julian_day(utc_dt)
    lon = sun_lon(jd_current)

    if (local_dt.month, local_dt.day) < (2, 4):
        solar_year = local_dt.year - 1
    else:
        solar_year = local_dt.year
    y_stem_i   = (solar_year - 4) % 10
    y_branch_i = (solar_year - 4) % 12
    year_p     = STEM[y_stem_i] + BRANCH[y_branch_i]

    m_branch_i = month_branch_idx(lon)         # 0=寅
    m_stem_i   = (y_stem_i*2 + 2 + m_branch_i) % 10
    month_p = STEM[m_stem_i] + BRANCH[(m_branch_i + 2) % 12]

    offset     = local_dt.date().toordinal() - ORD_EPOCH
    day_p      = JIA_ZI[offset % 60]

    h_branch_i = hour_branch_idx(local_dt.hour)
    h_stem_i   = (2 * (offset % 10) + h_branch_i) % 10
    hour_p     = STEM[h_stem_i] + BRANCH[h_branch_i]

    return year_p, month_p, day_p, hour_p

# ————————————————————————————————————————————————————
# (Keep strength helpers as before)
# ————————————————————————————————————————————————————

STEM_ELEM   = ["Wood","Wood","Fire","Fire","Earth",
               "Earth","Metal","Metal","Water","Water"]
BRANCH_ELEM = ["Water","Earth","Wood","Wood","Earth","Fire",
               "Fire","Earth","Metal","Metal","Earth","Water"]

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
    productive = {"Wood":"Fire","Fire":"Earth","Earth":"Metal",
                  "Metal":"Water","Water":"Wood"}
    control    = {"Wood":"Earth","Earth":"Water","Water":"Fire",
                  "Fire":"Metal","Metal":"Wood"}

    if other == dm:                 return +1
    if productive[other] == dm:     return +1
    if control[other] == dm:        return -1
    if productive[dm] == other:     return -1
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

# ————————————————————————————————————————————————————
# MAIN CONVENIENCE FUNCTION (call from app.py)
# ————————————————————————————————————————————————————
def calculate_bazi_with_solar_correction(dob, birth_time, local_longitude, utc_offset):
    """
    Convenience function: does solar correction, returns pillars and debug info.
    Returns: dict with everything you need to show in app.py
    """
    solar_dt, standard_dt, long_corr_min, EoT_min = solar_corrected_time(
        dob, birth_time, local_longitude, utc_offset
    )
    Y, M, D, H = four_pillars(solar_dt, int(utc_offset))
    vis_stems    = [Y[0], M[0], D[0], H[0]]
    vis_branches = [Y[1], M[1], D[1], H[1]]
    strength, raw = judge_strength(
        day_stem=D[0],
        month_branch=M[1],
        vis_stems=vis_stems,
        vis_branches=vis_branches
    )
    return {
        "standard_dt": standard_dt,
        "solar_dt": solar_dt,
        "longitude_correction_min": long_corr_min,
        "EoT_min": EoT_min,
        "year": Y,
        "month": M,
        "day": D,
        "hour": H,
        "strength": strength,
        "strength_score": raw
    }