import datetime as dt
import math
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
from bazi_constants import (
    STEM, BRANCH, JIA_ZI, ORD_EPOCH, STEM_ELEM, BRANCH_ELEM, BRANCH_HIDDEN, SEASON_BONUS
)

# ————————————————————————————————————————————————————
# Solar Time Correction
# ————————————————————————————————————————————————————
def equation_of_time(dt_date: dt.date) -> float:
    """Calculate the equation of time for a given date.

    Args:
        dt_date: Date object.

    Returns:
        Equation of time in minutes.
    """
    N = dt_date.timetuple().tm_yday
    B = 2 * math.pi * (N - 81) / 364
    EoT = 9.87 * math.sin(2*B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)
    return EoT  # in minutes

def longitude_correction(local_longitude: float, reference_longitude: float) -> float:
    """Calculate longitude correction in minutes.

    Args:
        local_longitude: Local longitude in degrees.
        reference_longitude: Reference longitude in degrees.

    Returns:
        Correction in minutes.
    """
    return (reference_longitude - local_longitude) * 4

def solar_corrected_time(dob: dt.date, birth_time: dt.time, local_longitude: float, utc_offset: float) -> tuple[dt.datetime, dt.datetime, float, float]:
    """Calculate solar time corrected datetime.

    Args:
        dob: Date of birth.
        birth_time: Birth time.
        local_longitude: Local longitude in degrees.
        utc_offset: UTC offset in hours.

    Returns:
        Tuple of (corrected datetime, naive local datetime, longitude correction in minutes, equation of time in minutes).
    """
    naive_local_dt = dt.datetime.combine(dob, birth_time)
    reference_longitude = utc_offset * 15  # 15° per hour of timezone
    long_corr_min = longitude_correction(local_longitude, reference_longitude)
    EoT_min = equation_of_time(dob)
    corrected_dt = naive_local_dt - dt.timedelta(minutes=long_corr_min) + dt.timedelta(minutes=EoT_min)
    return corrected_dt, naive_local_dt, long_corr_min, EoT_min

# ————————————————————————————————————————————————————
# Hidden Stems Helpers
# ————————————————————————————————————————————————————
def get_hidden_stems(branch: str) -> list[str]:
    """Get hidden stems for a given branch.

    Args:
        branch: Earthly branch character.

    Returns:
        List of hidden stem characters.
    """
    return BRANCH_HIDDEN.get(branch, [])

def get_pillar_hidden_stems(year_branch: str, month_branch: str, day_branch: str, hour_branch: str) -> list[list[str]]:
    """Get hidden stems for all four pillars.

    Args:
        year_branch: Year branch character.
        month_branch: Month branch character.
        day_branch: Day branch character.
        hour_branch: Hour branch character.

    Returns:
        List of lists of hidden stems for each pillar.
    """
    return [
        get_hidden_stems(year_branch),
        get_hidden_stems(month_branch),
        get_hidden_stems(day_branch),
        get_hidden_stems(hour_branch),
    ]

# ————————————————————————————————————————————————————
# BaZi Calculation Core
# ————————————————————————————————————————————————————
def sun_lon(jd: float) -> float:
    """Calculate the sun's longitude for a given Julian day.

    Args:
        jd: Julian day.

    Returns:
        Sun longitude in degrees.
    """
    T = (jd - 2451545.0) / 36525.0
    L0 = (280.46646 + 36000.76983*T + 0.0003032*T*T) % 360
    M  = (357.52911 + 35999.05029*T - 0.0001537*T*T) % 360
    M  = math.radians(M)
    C  = (1.914602 - 0.004817*T - 0.000014*T*T)*math.sin(M)
    C += (0.019993 - 0.000101*T)*math.sin(2*M)
    C += 0.000289*math.sin(3*M)
    return (L0 + C) % 360

def julian_day(utc: dt.datetime) -> float:
    """Calculate the Julian day from a UTC datetime.

    Args:
        utc: UTC datetime.

    Returns:
        Julian day as float.
    """
    y, m = utc.year, utc.month
    d = utc.day + (utc.hour + utc.minute/60 + utc.second/3600)/24
    if m <= 2:
        y, m = y - 1, m + 12
    A = y // 100
    B = 2 - A + A // 4
    return int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + B - 1524.5

def month_branch_idx(lon: float) -> int:
    """Calculate the month branch index based on sun longitude.

    Args:
        lon: Sun longitude in degrees.

    Returns:
        Month branch index (0-11).
    """
    adj = (lon - 315) % 360
    return int(adj // 30)

def hour_branch_idx(hour: int) -> int:
    """Calculate the hour branch index based on hour.

    Args:
        hour: Hour of day (0-23).

    Returns:
        Hour branch index (0-11).
    """
    return ((hour + 1) // 2) % 12

def four_pillars(local_dt: dt.datetime, utc_offset: int) -> tuple[str, str, str, str]:
    """Calculate the four pillars (year, month, day, hour) from local datetime.

    Args:
        local_dt: Local datetime with timezone info.
        utc_offset: UTC offset in hours.

    Returns:
        Tuple of four pillars as strings (year, month, day, hour).
    """
    tz = dt.timezone(dt.timedelta(hours=utc_offset))
    local_dt = local_dt.replace(tzinfo=tz)
    utc_dt   = local_dt.astimezone(dt.timezone.utc)

    # Year pillar
    jd_current = julian_day(utc_dt)
    lon = sun_lon(jd_current)
    if (local_dt.month, local_dt.day) < (2, 4):
        solar_year = local_dt.year - 1
    else:
        solar_year = local_dt.year
    y_stem_i   = (solar_year - 4) % 10
    y_branch_i = (solar_year - 4) % 12
    year_p     = STEM[y_stem_i] + BRANCH[y_branch_i]

    # Month pillar
    m_branch_i = month_branch_idx(lon)
    m_stem_i   = (y_stem_i*2 + 2 + m_branch_i) % 10
    month_p = STEM[m_stem_i] + BRANCH[(m_branch_i + 2) % 12]

    # Day pillar
    offset     = local_dt.date().toordinal() - ORD_EPOCH
    day_p      = JIA_ZI[offset % 60]

    # Hour pillar
    h_branch_i = hour_branch_idx(local_dt.hour)
    h_stem_i   = (2 * (offset % 10) + h_branch_i) % 10
    hour_p     = STEM[h_stem_i] + BRANCH[h_branch_i]

    return year_p, month_p, day_p, hour_p

# ————————————————————————————————————————————————————
# Strength/Support Calculation Helpers (legacy style)
# ————————————————————————————————————————————————————
def support_value(dm: str, other: str) -> int:
    """Calculate support value between two elements.

    Args:
        dm: Day master element.
        other: Other element.

    Returns:
        Support score: +1, 0, or -1.
    """
    productive = {"Wood":"Fire","Fire":"Earth","Earth":"Metal",
                  "Metal":"Water","Water":"Wood"}
    control    = {"Wood":"Earth","Earth":"Water","Water":"Fire",
                  "Fire":"Metal","Metal":"Wood"}

    if other == dm:                 return +1
    if productive[other] == dm:     return +1
    if control[other] == dm:        return -1
    if productive[dm] == other:     return -1
    return 0

def judge_strength(day_stem: str, month_branch: str, vis_stems: list[str], vis_branches: list[str]) -> tuple[str, int]:
    """Judge strength of the day master based on stems and branches.

    Args:
        day_stem: Day pillar stem character.
        month_branch: Month pillar branch character.
        vis_stems: List of visible stem characters.
        vis_branches: List of visible branch characters.

    Returns:
        Tuple of (verdict string "Strong"/"Weak", numeric score).
    """
    dm_elem = STEM_ELEM[STEM.index(day_stem)]
    score   = SEASON_BONUS[month_branch][dm_elem]

    for s in vis_stems:
        score += support_value(dm_elem, STEM_ELEM[STEM.index(s)])
    for b in vis_branches:
        score += support_value(dm_elem, BRANCH_ELEM[BRANCH.index(b)])

    if score >= 0:
        verdict = "Strong"
    else:
        verdict = "Weak"

    return verdict, score

# ————————————————————————————————————————————————————
# Five Elements Star Meter Calculation (new!)
# ————————————————————————————————————————————————————
def calculate_element_strengths(vis_stems: list[str], hidden_stems_per_pillar: list[list[str]], month_branch: str, day_stem: str) -> tuple[dict[str, float], dict[str, dict[str, object]]]:
    """Calculate element strengths based on visible and hidden stems, season, and day master.

    Args:
        vis_stems: List of visible stem characters.
        hidden_stems_per_pillar: List of lists of hidden stem characters per pillar.
        month_branch: Month pillar branch character.
        day_stem: Day pillar stem character.

    Returns:
        Tuple of:
            - Dictionary mapping element to total strength score.
            - Dictionary with detailed breakdown per element.
    """
    elements = ["Wood", "Fire", "Earth", "Metal", "Water"]
    elem_score = {e: 0 for e in elements}
    breakdown = {}
    # Visible stems
    vis_count = {e: 0 for e in elements}
    vis_desc = {e: [] for e in elements}
    for s in vis_stems:
        e = STEM_ELEM[STEM.index(s)]
        vis_count[e] += 1
        vis_desc[e].append(s)
    # Hidden stems
    hid_count = {e: 0.0 for e in elements}
    hid_desc = {e: [] for e in elements}
    for stem_list in hidden_stems_per_pillar:
        for s in stem_list:
            e = STEM_ELEM[STEM.index(s)]
            hid_count[e] += 0.5
            hid_desc[e].append(f"{s} 0.5")
    # Season
    season_bonus = {e: SEASON_BONUS.get(month_branch, {}).get(e, 0) for e in elements}
    # DM bonus
    DM_ELEM = STEM_ELEM[STEM.index(day_stem)]
    dm_bonus = {e: (1 if e == DM_ELEM else 0) for e in elements}
    # Total & breakdown
    for e in elements:
        total = vis_count[e] + hid_count[e] + season_bonus[e] + dm_bonus[e]
        breakdown[e] = {
            "visible": vis_count[e],
            "visible_desc": " + ".join(vis_desc[e]) if vis_desc[e] else "",
            "hidden": hid_count[e],
            "hidden_desc": " + ".join(hid_desc[e]) if hid_desc[e] else "",
            "season": season_bonus[e],
            "dm": dm_bonus[e],
            "total": round(total, 1)
        }
        elem_score[e] = round(total, 1)
    return elem_score, breakdown

# ————————————————————————————————————————————————————
# Main API Function
# ————————————————————————————————————————————————————
def calculate_bazi_with_solar_correction(dob: dt.date, birth_time: dt.time, local_longitude: float, utc_offset: float) -> dict[str, object]:
    """Calculate BaZi with solar time correction.

    Args:
        dob: Date of birth.
        birth_time: Time of birth.
        local_longitude: Local longitude in degrees.
        utc_offset: UTC offset in hours.

    Returns:
        Dictionary containing BaZi calculation results and metadata.
    """
    solar_dt, standard_dt, long_corr_min, EoT_min = solar_corrected_time(
        dob, birth_time, local_longitude, utc_offset
    )

    # For traditional day calculation: flip day at 子时 (23:00–23:59)
    if solar_dt.hour == 23:
        solar_dt_bazi = solar_dt + dt.timedelta(days=1)
    else:
        solar_dt_bazi = solar_dt

    # Calculate four pillars
    Y, M, _, _ = four_pillars(solar_dt, int(utc_offset))
    _, _, D, H = four_pillars(solar_dt_bazi, int(utc_offset))

    # Get hidden stems for each pillar
    hidden_stems_per_pillar = get_pillar_hidden_stems(
        Y[1], M[1], D[1], H[1]
    )

    vis_stems    = [Y[0], M[0], D[0], H[0]]
    vis_branches = [Y[1], M[1], D[1], H[1]]
    strength, raw = judge_strength(
        day_stem=D[0],
        month_branch=M[1],
        vis_stems=vis_stems,
        vis_branches=vis_branches
    )

    # NEW: calculate element strengths
    element_strengths, element_score_breakdown = calculate_element_strengths(
        vis_stems, hidden_stems_per_pillar, M[1], D[0]
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
        "strength_score": raw,
        "hidden_stems": hidden_stems_per_pillar,
        "element_strengths": element_strengths,
        "element_score_breakdown": element_score_breakdown,
    }

def compute_bazi_result(dob: dt.date, btime: dt.time, country: str) -> tuple[dict[str, object] | None, str]:
    """Compute BaZi result with geo lookup and timezone detection.

    Args:
        dob: Date of birth.
        btime: Time of birth.
        country: Country name for geolocation.

    Returns:
        Tuple of (result dictionary or None, timezone string or error message).
    """
    try:
        geolocator = Nominatim(user_agent="my_bazi_app", timeout=5)
        tf = TimezoneFinder()
        location = geolocator.geocode(country)
        if not location:
            return None, "Country not found."
        tz_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)
        if not tz_str:
            return None, "Could not determine timezone."
        local_dt = dt.datetime.combine(dob, btime).replace(tzinfo=ZoneInfo(tz_str))
        utc_off = local_dt.utcoffset().total_seconds() / 3600
        result = calculate_bazi_with_solar_correction(dob, btime, location.longitude, utc_off)
        return (result, tz_str)
    except Exception as err:
        return None, f"Error: {err}"
    
def get_day_stem(bazi_dict: dict[str, object]) -> str:
    """Extract the Heavenly-stem character of the Day pillar from BaZi dictionary.

    Args:
        bazi_dict: BaZi result dictionary.

    Returns:
        Day pillar stem character.

    Raises:
        KeyError: If day pillar not found in dictionary.
    """
    if "day_pillar" in bazi_dict:
        return bazi_dict["day_pillar"][0]
    if "day" in bazi_dict:
        return bazi_dict["day"][0]
    if "pillars" in bazi_dict and len(bazi_dict["pillars"]) >= 3:
        return bazi_dict["pillars"][2][0]
    raise KeyError("Day pillar not found in BaZi result")