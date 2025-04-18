import json
from datetime import datetime

def load_age_tips(filepath="data/age_tips.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_age_in_months(birthdate_str):
    try:
        birthdate = datetime.strptime(birthdate_str, "%d.%m.%Y")
        today = datetime.today()
        age_in_months = (today.year - birthdate.year) * 12 + (today.month - birthdate.month)
        return max(age_in_months, 0)
    except ValueError:
        return None

def get_tip_for_age(age_tips, age_in_months):
    for key in age_tips:
        clean_key = key.split(" ")[0]  # get the "12-13" part
        range_parts = clean_key.split("-")
        if len(range_parts) == 2:
            try:
                start, end = int(range_parts[0]), int(range_parts[1])
                if start <= age_in_months <= end:
                    return age_tips[key]
            except ValueError:
                continue
    return "No tip found for this age."
