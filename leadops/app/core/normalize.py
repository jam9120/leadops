import re
from typing import Optional


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def normalize_owner_name(name: str) -> str:
    if not name:
        return ""
    cleaned = normalize_whitespace(name.upper())
    cleaned = re.sub(r"[^\w\s&]", "", cleaned)
    return cleaned


def normalize_address(address: str) -> str:
    if not address:
        return ""
    addr = normalize_whitespace(address.upper())
    replacements = {
        r"\bSTREET\b": "ST",
        r"\bAVENUE\b": "AVE",
        r"\bROAD\b": "RD",
        r"\bDRIVE\b": "DR",
        r"\bLANE\b": "LN",
        r"\bCOURT\b": "CT",
        r"\bBOULEVARD\b": "BLVD",
        r"\bPLACE\b": "PL",
        r"\bAPARTMENT\b": "APT",
        r"\bSUITE\b": "STE",
        r"\bNORTH\b": "N",
        r"\bSOUTH\b": "S",
        r"\bEAST\b": "E",
        r"\bWEST\b": "W",
    }
    for pattern, replacement in replacements.items():
        addr = re.sub(pattern, replacement, addr)
    addr = re.sub(r"[^\w\s#-]", "", addr)
    return normalize_whitespace(addr)


def classify_trigger(raw_label: Optional[str], permit_type: Optional[str] = None, permit_subtype: Optional[str] = None) -> str:
    values = " ".join(
        [
            raw_label or "",
            permit_type or "",
            permit_subtype or "",
        ]
    ).lower()

    if "adu" in values or "accessory dwelling" in values:
        return "adu_permit"
    if "remodel" in values or "addition" in values:
        return "remodel_permit"
    if "roof" in values:
        return "roof_update"
    if "electrical" in values or "panel" in values:
        return "electrical_update"
    if "deed" in values:
        return "deed_change"
    if "lender" in values or "mortgage" in values or "refi" in values:
        return "lender_change"
    if "wildfire" in values or "fire zone" in values:
        return "wildfire_adjacent"
    return "unknown"


def owner_occupancy_proxy(owner_occupied_value: str) -> str:
    value = (owner_occupied_value or "").strip().lower()
    if value in {"yes", "y", "true", "1"}:
        return "owner_occupied"
    if value in {"no", "n", "false", "0"}:
        return "absentee"
    return "unknown"


def first_name_from_owner(owner_name: str) -> str:
    if not owner_name:
        return "There"
    cleaned = owner_name.replace("&", " ").replace(",", " ")
    token = cleaned.split()[0].title() if cleaned.split() else "There"
    return token