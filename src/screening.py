import re
import unicodedata
from datetime import datetime
from rapidfuzz import process, fuzz
import pandas as pd


def clean_name(name: str) -> str:
    """
    Standardise a name by:
    - Converting to uppercase
    - Removing accents (e.g., José -> JOSE)
    - Removing punctuation and extra spaces
    """
    if pd.isna(name):
        return ""
    
    # 1. uppercase
    name = name.upper()
    
    # 2. normalize
    name = unicodedata.normalize("NFKD", name).encode("ASCII", "ignore").decode("utf-8")
    
    # 3. punctuate
    name = re.sub(r"[^A-Z0-9\s]", "", name)
    
    # 4. handle extra spaces
    name = re.sub(r"\s+", " ", name).strip()
    
    return name


def match_name(vessel_name: str, sanctions_list: list, threshold: int = 85):
    """
    Compare a vessel name against the sanctions list using fuzzy matching.
    Returns:
      - best match name
      - similarity score
      - whether it passed the threshold
    """
    best_match = process.extractOne(vessel_name, sanctions_list, scorer=fuzz.WRatio)
    
    if best_match:
        match_name, score, _ = best_match
        return match_name, score, score >= threshold
    else:
        return None, 0, False


def run_screening(vessels_df: pd.DataFrame, sanctions_list: list, threshold: int = 85):
    """
    Run sanctions screening across all vessels.
    Returns a DataFrame with results.
    """
    results = []
    
    for idx, row in vessels_df.iterrows():
        vessel = row["vessel_name"]
        clean_vessel = clean_name(vessel)
        match, score, flag = match_name(clean_vessel, sanctions_list, threshold)
        
        results.append({
            "vessel_id": row.get("vessel_id", idx + 1),
            "vessel_name": vessel,
            "matched_sanction": match,
            "score": score,
            "is_flagged": flag,
            "screening_date": datetime.today().strftime("%Y-%m-%d")
        })
    
    return pd.DataFrame(results)


def calculate_risk(match_flag, score, ais_gap=0):
    risk = 0

    if match_flag:
        risk += 50

    if ais_gap >= 24:
        risk += 20

    return risk
