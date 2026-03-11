import pandas as pd

    # ======================
    # HITUNG JUMLAH UANG
    # ======================
TARIF_HARIAN = 20_000
POTONGAN_TELAT = 12_000
BONUS_LEMBUR = 12_000

def process_attendance_absen(
    df_clean: pd.DataFrame
):
    """
    PROCESSOR KHUSUS ABSENSI HADIR

    Return:
        final_result : Data siap PDF (pivot per tanggal)
        rekap        : Data rekap sederhana
    """

    df = df_clean.copy()

    # ======================
    # VALIDASI KOLOM WAJIB
    # ======================
    required_cols = {
        "No.Akun",
        "Nama",
        "Departemen",
        "Tanggal",
        "Masuk",
        "Pulang",
        "Telat",
        "ATT_Time"
    }

    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(f"Kolom wajib tidak lengkap: {missing}")

    # ======================
    # NORMALISASI DATA
    # ======================

    # No.Akun → jadikan string agar 0 di depan tidak hilang
    df["No.Akun"] = df["No.Akun"].astype(str).str.strip()

    # Normalisasi Departemen
    df["Departemen"] = (
        df.groupby("Nama")["Departemen"]
        .transform(lambda x: x.ffill().bfill())
    )

    df["Departemen"] = (
        df["Departemen"]
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # Normalisasi Nama
    df["Nama"] = (
        df["Nama"]
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .str.title()
    )

    # ======================
    # NORMALISASI TANGGAL
    # ======================

    df["Tanggal"] = pd.to_datetime(
        df["Tanggal"],
        errors="coerce",
        dayfirst=True   # karena format 09/02/2026
    )

    if df["Tanggal"].isna().all():
        raise ValueError("Semua nilai tanggal tidak valid.")

    # pastikan benar-benar datetime dulu
    df = df.dropna(subset=["Tanggal"])

    # baru boleh pakai .dt
    df["Tanggal"] = df["Tanggal"].dt.normalize()  # buang jam jadi 00:00:00
    df["Hari"] = df["Tanggal"].dt.day

    # ======================
    # FILTER HADIR VALID
    # ======================
    df_hadir = df[
        df["Masuk"].notna() | df["Pulang"].notna()
    ]

    if df_hadir.empty:
        return pd.DataFrame(), pd.DataFrame()

    # ======================
    # REKAP HARIAN
    # ======================
    hadir = (
        df_hadir
        .groupby(["No.Akun", "Nama", "Departemen", "Hari"])
        .size()
        .reset_index(name="Hadir")
    )

    hadir["Hadir"] = "1"

    # ======================
    # PIVOT PER TANGGAL
    # ======================
    final_result = hadir.pivot_table(
        index=["No.Akun", "Nama", "Departemen"],
        columns="Hari",
        values="Hadir",
        aggfunc="first",
        fill_value=""
    ).reset_index()

    # ======================
    # SORT BERDASARKAN DEPARTEMEN & NAMA
    # ======================
    final_result = final_result.sort_values(
        by=["Departemen", "Nama"],
        kind="mergesort"
    ).reset_index(drop=True)

    # ======================
    # SORT KOLOM TANGGAL (1-31)
    # ======================
    tanggal_cols = sorted(
        [c for c in final_result.columns if isinstance(c, int)]
    )



    final_result["Jumlah"] = (
        final_result[tanggal_cols]
        .apply(
            lambda x: sum(
                TARIF_HARIAN for v in x if v == "1"
            ),
            axis=1
        )
    )

    # ======================
    # POTONGAN & BONUS FINAL (TIDAK DOUBLE PER HARI)
    # ======================

    # Normalisasi Telat
    df["Telat"] = (
        df["Telat"]
        .replace("", 0)
        .fillna(0)
    )

    df["Telat"] = pd.to_numeric(
        df["Telat"], errors="coerce"
    ).fillna(0).astype(int)

    # Normalisasi ATT_Time (format HH:MM dari Excel)
    df["ATT_Time"] = df["ATT_Time"].astype(str).str.strip()

    df["ATT_Time"] = pd.to_timedelta(
        df["ATT_Time"] + ":00",   # tambahkan detik,
        errors="coerce"
    )
    # ======================================
    # LOGIKA NOMINAL
    # ======================================
    # -1  = Potong 12.000
    #  0  = Normal
    # +1  = Tambah 12.000

    telat = df["Telat"] == 1
    kurang_jam = df["ATT_Time"] < pd.Timedelta(hours=4)
    lembur = df["ATT_Time"] > pd.Timedelta(hours=12)

    # ======================
    # FLAG BONUS & POTONGAN
    # ======================

    df["Bonus_Flag"] = 0
    df["Potongan_Flag"] = 0

    # bonus lembur
    df.loc[lembur, "Bonus_Flag"] = 1

    # potongan telat
    df.loc[telat, "Potongan_Flag"] = 1

    # potongan kurang dari 4 jam
    df.loc[kurang_jam, "Potongan_Flag"] = 1

    # ======================
    # KHUSUS TELAT + <4 JAM
    # hanya 1 potongan
    # ======================

    df.loc[telat & kurang_jam, "Potongan_Flag"] = 1

    # ======================
    # TIDAK DOUBLE PER HARI
    # ======================

    bonus_per_hari = (
        df.groupby(["No.Akun","Tanggal"])["Bonus_Flag"]
        .max()
        .reset_index()
    )

    potongan_per_hari = (
        df.groupby(["No.Akun","Tanggal"])["Potongan_Flag"]
        .max()
        .reset_index()
    )

    # ======================
    # TOTAL PER ORANG
    # ======================

    bonus_total = (
        bonus_per_hari.groupby("No.Akun")["Bonus_Flag"]
        .sum()
        .reset_index()
    )

    potongan_total = (
        potongan_per_hari.groupby("No.Akun")["Potongan_Flag"]
        .sum()
        .reset_index()
    )

    bonus_total["Bonus"] = bonus_total["Bonus_Flag"] * BONUS_LEMBUR
    potongan_total["Potongan"] = potongan_total["Potongan_Flag"] * POTONGAN_TELAT

    nominal_total = bonus_total.merge(
        potongan_total,
        on="No.Akun",
        how="outer"
    )

    final_result = final_result.merge(
        nominal_total[["No.Akun","Bonus","Potongan"]],
        on="No.Akun",
        how="left"
    )

    final_result["Bonus"] = final_result["Bonus"].fillna(0)
    final_result["Potongan"] = final_result["Potongan"].fillna(0)

    # ======================
    # KETERANGAN
    # ======================
    final_result["Keterangan"] = ""

    # ======================
    # URUTKAN KOLOM FINAL
    # ======================
    final_result = final_result[
        ["No.Akun", "Nama", "Departemen"]
        + tanggal_cols
        + ["Bonus","Potongan","Jumlah","Keterangan"]
    ]

    # ======================
    # REKAP
    # ======================
    rekap = hadir.copy()


    return final_result, rekap
