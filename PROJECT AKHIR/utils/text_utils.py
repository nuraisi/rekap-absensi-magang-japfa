import pandas as pd

def hari_indonesia(nama_hari):
    mapping = {
        "Monday":"Senin","Tuesday":"Selasa","Wednesday":"Rabu","Thursday":"Kamis",
        "Friday":"Jumat","Saturday":"Sabtu","Sunday":"Minggu"
    }
    return mapping.get(nama_hari, nama_hari)

def safe_text(val):
    if pd.isna(val) or str(val).strip().lower() in ["nan", "none"]:
        return ""
    return str(val).strip()
