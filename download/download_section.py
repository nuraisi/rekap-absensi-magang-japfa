import os
import re
import pandas as pd
import streamlit as st

from exports.excel_export_izin import export_excel_izin
from exports.excel_export_absen import export_excel_rekap


def extract_date_range(filename: str):

    match_bulan = re.search(
        r"(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)",
        filename,
        re.IGNORECASE
    )

    if not match_bulan:
        raise ValueError("Nama file harus mengandung nama bulan")

    bulan = match_bulan.group(1).capitalize()

    return bulan


# ======================
# DOWNLOAD REKAP ABSEN
# ======================
def download_absen(final_absen, final_izin, filename_absen):

    base_name = os.path.basename(filename_absen)
    nama_tanpa_ext = os.path.splitext(base_name)[0]

    excel_file = export_excel_rekap(
        final_absen=final_absen,
        final_izin=final_izin,
        filename_absen=filename_absen
    )

    st.download_button(
        label="📊 Unduh Rekap Absensi (Excel)",
        data=excel_file,
        file_name=f"{nama_tanpa_ext} (Sistem).xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ======================
# DOWNLOAD REKAP IZIN
# ======================
def download_izin(final_izin: pd.DataFrame, filename_absen):

    if final_izin is None or final_izin.empty:
        return

    df = final_izin.copy()

    expected_cols = [
        "Nama",
        "Departemen",
        "Tanggal Mulai Izin",
        "Tanggal Akhir Izin",
        "Jumlah Hari Izin",
        "Alasan",
    ]

    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        st.error(f"Kolom izin tidak lengkap: {missing}")
        return

    df = df[expected_cols]

    # ambil nama file tanpa path dan tanpa extension
    base_name = os.path.basename(filename_absen)
    nama_tanpa_ext = os.path.splitext(base_name)[0]

    excel_file = export_excel_izin(df)

    st.download_button(
        label="📄 Unduh Rekap Izin (Excel)",
        data=excel_file,
        file_name=f"{nama_tanpa_ext} (Sistem).xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
