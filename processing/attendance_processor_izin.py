import pandas as pd
import re


# ======================================================
# PARSER TANGGAL BAHASA INDONESIA
# ======================================================
def parse_tanggal_indo(series: pd.Series) -> pd.Series:
    bulan_map = {
        "januari": "January",
        "februari": "February",
        "maret": "March",
        "april": "April",
        "mei": "May",
        "juni": "June",
        "juli": "July",
        "agustus": "August",
        "september": "September",
        "oktober": "October",
        "november": "November",
        "desember": "December",
    }

    def convert(val):
        if pd.isna(val):
            return pd.NaT

        # Jika sudah datetime
        if isinstance(val, pd.Timestamp):
            return val

        s = str(val).strip().lower()

        # Ganti nama bulan indo → english
        for indo, eng in bulan_map.items():
            s = re.sub(rf"\b{indo}\b", eng, s, flags=re.IGNORECASE)

        return pd.to_datetime(
            s,
            errors="coerce",
            dayfirst=True   # : format Indonesia
        )

    return series.apply(convert)


# ======================================================
# PROCESSOR IZIN
# ======================================================
def process_attendance_izin(df_raw: pd.DataFrame):

    df = df_raw.copy()

    # Normalisasi nama
    df["Nama"] = df["Nama"].astype(str).str.strip().str.title()

    df["Nama"] = (
        df["Nama"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )

    # ======================
    # VALIDASI KOLOM WAJIB
    # ======================
    required_cols = {
        "Nama",
        "Departemen",
        "Tanggal Mulai Izin",
        "Tanggal Akhir Izin",
        "Alasan"
    }

    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(f"Kolom wajib tidak lengkap: {missing}")

    # ======================
    # NORMALISASI DEPARTEMEN
    # ======================
    df["Departemen"] = (
        df.groupby("Nama")["Departemen"]
        .transform(lambda x: x.ffill().bfill())
    )

    # ======================
    # NORMALISASI KOSONG DI TANGGAL AKHIR
    # ======================
    df["Tanggal Akhir Izin"] = (
        df["Tanggal Akhir Izin"]
        .replace(["", " ", "-"], pd.NA)
    )

    # ======================
    # PARSE TANGGAL
    # ======================
    df["Tanggal Mulai Izin"] = parse_tanggal_indo(df["Tanggal Mulai Izin"])
    df["Tanggal Akhir Izin"] = parse_tanggal_indo(df["Tanggal Akhir Izin"])

    # ======================
    # DROP jika tanggal mulai kosong
    # ======================
    df = df.dropna(subset=["Tanggal Mulai Izin"])

    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    # ======================
    # JIKA TANGGAL AKHIR KOSONG
    # ISI DENGAN TANGGAL MULAI
    # ======================
    df["Tanggal Akhir Izin"] = df["Tanggal Akhir Izin"].fillna(
        df["Tanggal Mulai Izin"]
    )

    # ======================
    # PERBAIKI JIKA TERBALIK
    # ======================
    mask_terbalik = df["Tanggal Akhir Izin"] < df["Tanggal Mulai Izin"]

    df.loc[mask_terbalik, [
        "Tanggal Mulai Izin",
        "Tanggal Akhir Izin"
    ]] = df.loc[mask_terbalik, [
        "Tanggal Akhir Izin",
        "Tanggal Mulai Izin"
    ]].values

    # ======================
    # HITUNG DURASI
    # ======================
    df["Jumlah Hari Izin"] = (
        (df["Tanggal Akhir Izin"] - df["Tanggal Mulai Izin"])
        .dt.days + 1
    )

    # ======================
    # SORT DATA
    # ======================
    df = df.sort_values(
        by=["Tanggal Mulai Izin", "Nama"]
    )

    # ======================
    # FINAL RESULT
    # ======================
    final_result = df[
        [
            "Nama",
            "Departemen",
            "Tanggal Mulai Izin",
            "Tanggal Akhir Izin",
            "Jumlah Hari Izin",
            "Alasan",
        ]
    ].reset_index(drop=True)

    rekap = df.copy()

    return final_result, rekap


