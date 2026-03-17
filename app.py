# app.py
import streamlit as st
from pathlib import Path
import pandas as pd
from PIL import Image

from components.hero import hero_section

from upload.upload import read_any_csv
from validation.validasi import validate_absensi

from processing.attendance_processor_absen import process_attendance_absen
from processing.attendance_processor_izin import process_attendance_izin

from download.download_section import (
    download_absen,
    download_izin
)


# ======================
# PAGE CONFIG
# ======================
st.set_page_config(
    page_title="Sistem Rekap Absensi",
    page_icon="📋",
    layout="wide"
)


# ======================
# LOAD CSS
# ======================
def load_css():
    with open("styles/main.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css()


# ======================
# NAVBAR
# ======================
st.markdown('<div class="navbar">', unsafe_allow_html=True)

nav_col1, nav_col2 = st.columns([1, 6])

with nav_col1:
    logo = Image.open(Path("images/logo japfa.png"))
    st.image(logo, width=120)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="shadow-line"></div>', unsafe_allow_html=True)


# ======================
# HERO SECTION
# ======================
file_absen, file_izin = hero_section()

if file_absen is None and file_izin is None:
    st.info("Silakan upload minimal satu file: absensi atau izin.")
    st.stop()


# ======================
# FUNCTION BACA FILE
# ======================
def read_file(uploaded_file):

    if uploaded_file.name.lower().endswith(".csv"):
        return read_any_csv(uploaded_file)

    return pd.read_excel(uploaded_file, dtype=str)


# ======================
# PROCESS FILE ABSEN
# ======================
final_absen = None
filename_absen = None

if file_absen is not None:
    try:
        df_absen_raw = read_file(file_absen)
        filename_absen = file_absen.name

        df_absen_clean = validate_absensi(df_absen_raw)

        final_absen, _ = process_attendance_absen(
            df_absen_clean
        )

    except Exception as e:
        st.error(f"Gagal memproses file absensi: {e}")
        st.stop()

# ======================
# PROCESS FILE IZIN
# ======================
final_izin = None
filename_izin = None

if file_izin is not None:

    try:

        df_izin_raw = read_file(file_izin)

        filename_izin = file_izin.name

        final_izin, _ = process_attendance_izin(
            df_izin_raw
        )

    except Exception as e:

        st.error(f"Gagal memproses file izin: {e}")
        st.stop()

# ======================
# VALIDASI DATA
# ======================
results = []

if final_absen is not None and not final_absen.empty:
    results.append(final_absen)

if final_izin is not None and not final_izin.empty:
    results.append(final_izin)

if not results:
    st.warning("Tidak ada data valid untuk diproses.")
    st.stop()


st.success("✅ Data berhasil diproses")

st.markdown("---")
st.subheader("📥 Download Rekap")


col1, col2 = st.columns(2)

# ======================
# BUTTON REKAP ABSEN
# ======================
with col1:

    if final_absen is not None and not final_absen.empty:

        download_absen(
            final_absen=final_absen,
            final_izin=final_izin,
            filename_absen=filename_absen
        )

# ======================
# BUTTON REKAP IZIN
# ======================
with col2:

    if final_izin is not None and not final_izin.empty:

        download_izin(
            final_izin=final_izin,
            filename_absen=filename_izin
        )
