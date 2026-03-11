import streamlit as st
import pandas as pd
import csv

# ======================
# CSV AUTO DELIMITER
# ======================
def read_any_csv(uploaded_file):
    try:
        sample = uploaded_file.read(4096).decode("utf-8", errors="ignore")
        uploaded_file.seek(0)

        dialect = csv.Sniffer().sniff(sample, delimiters=";,|\t")
        delimiter = dialect.delimiter

        uploaded_file.seek(0)
        df = pd.read_csv(
            uploaded_file,
            sep=delimiter,
            engine="python"
        )

    except Exception:
        uploaded_file.seek(0)
        df = pd.read_csv(
            uploaded_file,
            sep=",",
            engine="python"
        )

    # No.Akun STRING
    if "No.Akun" in df.columns:
        df["No.Akun"] = df["No.Akun"].astype(str).str.strip()

    return df


# ======================
# READ EXCEL
# ======================
def read_excel_file(uploaded_file):
    df = pd.read_excel(uploaded_file)

    # No.Akun STRING
    if "No.Akun" in df.columns:
        df["No.Akun"] = df["No.Akun"].astype(str).str.strip()

    return df


# ======================
# MAIN UPLOAD FUNCTION
# ======================
def upload_file():
    uploaded_file = st.file_uploader(
        "Upload File Absensi",
        type=["csv", "xlsx", "xls"]
    )

    if uploaded_file is not None:

        file_name = uploaded_file.name.lower()

        # CSV
        if file_name.endswith(".csv"):
            df = read_any_csv(uploaded_file)

        # EXCEL
        elif file_name.endswith((".xlsx", ".xls")):
            df = read_excel_file(uploaded_file)

        else:
            st.error("Format file tidak didukung")
            return None

        return df


    return None
