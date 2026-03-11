import pandas as pd
from datetime import datetime, time

# ======================
# PARSE TANGGAL
# ======================
def parse_date_flexible(val):
    if pd.isna(val):
        return pd.NaT

    val = str(val).strip()
    if not val:
        return pd.NaT

    formats = [
        "%d/%m/%Y", "%d-%m-%Y",
        "%Y/%m/%d", "%Y-%m-%d"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(val, fmt).date()
        except:
            continue

    return pd.to_datetime(val, errors="coerce").date()


def parse_time_flexible(val):
    if pd.isna(val):
        return None

    val = str(val).strip().replace(".", ":")
    if not val:
        return None

    formats = ["%H:%M:%S", "%H:%M"]

    for fmt in formats:
        try:
            return datetime.strptime(val, fmt).time()
        except:
            continue

    return None


# ======================
# CLEAN & NORMALIZE
# ======================
def clean_and_normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # rapikan nama kolom
    df.columns = [str(c).strip() for c in df.columns]

    rename_map = {

        "Nama Karyawan": "Nama",
        "NAMA": "Nama",

        "Dept": "Departemen",
        "DEPARTEMEN": "Departemen",

        "Tanggal Absensi": "Tanggal",
        "TANGGAL": "Tanggal",

        "Jam": "Waktu",
        "WAKTU": "Waktu"
    }

    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    required_cols = ["Nama", "Departemen", "Tanggal"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom wajib tidak ditemukan: {missing}")

    # parsing
    df["Tanggal"] = df["Tanggal"].apply(parse_date_flexible)

    if "Waktu" in df.columns:
        df["Waktu"] = df["Waktu"].apply(parse_time_flexible)
    else:
        df["Waktu"] = None

    # normalisasi teks
    df["Nama"] = df["Nama"].astype(str).str.strip().str.upper()
    df["Departemen"] = df["Departemen"].astype(str).str.strip().str.upper()

    # drop data rusak
    df = df.dropna(subset=[ "Nama", "Departemen", "Tanggal"])

    return df

