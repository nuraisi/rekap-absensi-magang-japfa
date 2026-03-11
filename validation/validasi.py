import pandas as pd
import re
from utils.datetime_utils import clean_and_normalize


class ValidationError(Exception):
    pass


# ======================
# VALIDASI FILE ABSENSI
# ======================
def validate_absensi(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Validasi & normalisasi file absensi
    Kolom wajib: Emp No, Nama, Departemen, Tanggal
    """
    try:
        df_clean = clean_and_normalize(df_raw)
    except Exception as e:
        raise ValidationError(f"Gagal membersihkan data absensi: {e}")

    required_cols = {"Nama", "Departemen", "Tanggal"}
    if not required_cols.issubset(df_clean.columns):
        raise ValidationError(
            "Format file absensi tidak sesuai. "
            "Kolom wajib: Emp No, Nama, Departemen, Tanggal."
        )

    if df_clean.empty:
        raise ValidationError("File absensi menghasilkan data kosong.")

    return df_clean


# ======================
# VALIDASI MASTER DATA
# ======================
def validate_master(
    master_df: pd.DataFrame | None,
    filename: str | None = None
) -> tuple[pd.DataFrame | None, list[str]]:
    """
    Validasi master data
    Kolom wajib:
    - Emp No.
    - Nama
    - Departemen
    """
    if master_df is None:
        return None, []

    warnings: list[str] = []

    master_df = master_df.copy()
    master_df.columns = master_df.columns.str.strip()

    # ======================
    # DETEKSI KOLOM
    # ======================
    name_col = next(
        (c for c in master_df.columns if c.upper() == "NAMA"),
        None
    )

    dept_col = next(
        (c for c in master_df.columns if c.upper().startswith("DEPARTEMEN")),
        None
    )

    # ======================
    # VALIDASI
    # ======================
    if name_col is None:
        raise ValidationError("Master data tidak memiliki kolom Nama.")
    if dept_col is None:
        raise ValidationError("Master data tidak memiliki kolom Departemen.")

    # ======================
    # NORMALISASI
    # ======================
    master_norm = pd.DataFrame()
    master_norm["Nama"] = master_df[name_col].astype(str).str.strip()
    master_norm["Departemen"] = master_df[dept_col].astype(str).str.strip()

    # ======================
    # CEK NAMA FILE
    # ======================
    if filename:
        match = re.search(r"(\d+)-(\d+)", filename)
        if not match:
            warnings.append(
                "Nama file master tidak mengandung rentang tanggal (contoh: 12-17)."
            )

    return master_norm, warnings

