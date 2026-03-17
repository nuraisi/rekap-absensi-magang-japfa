import streamlit as st
from PIL import Image


def load_css():
    with open("styles/main.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def load_html():
    with open("templates/hero.html", "r", encoding="utf-8") as f:
        return f.read()


def hero_section():

    load_css()

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown(load_html(), unsafe_allow_html=True)

    with col2:
        image = Image.open("images/depan.png")
        st.image(image, use_container_width=True)

    # SECTION HEADER
    st.markdown("""
    <div style='padding:50px 0; text-align:center;'>
        <h2 style='font-size:40px;'>Cara menggunakan Sistem Rekap Absensi Magang</h2>
        <p style='color:gray; font-size:20px'>Terdapat 2 tahap yang harus diperhatikan.</p>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
        <div class="card">
            <div class="card-title">❗Ketentuan File Absensi</div>
            <div class="card-desc">
                <ul style="text-align:left; padding-left:20px; margin:0;">
                    <li>Setelah menerima file dari Bu April, salin seluruh data ke file baru karena file asli diproteksi sehingga tidak dapat diedit.</li>
                    <li>Pastikan kolom <b>Departemen</b> telah disesuaikan dengan departemen masing-masing.</li>
                    <li>Pastikan kolom <b>Telat</b> telah dibersihkan kemudian isi dengan angka <b>1</b>.</li>
                    <li>Format penamaan file wajib mengikuti ketentuan berikut. (Contoh : Rekap_Absensi_Februari 9-14)</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="card">
            <div class="card-title">❗Ketentuan File Izin</div>
            <div class="card-desc">
                <ul style="text-align:left; padding-left:20px; margin:0;">
                    <li>Jika mahasiswa tidak mengisi tanggal akhir izin biarkan kosong.</li>
                    <li>Format penulisan tanggal harus dd/mm/yyyy.</li>
                    <li>Penulisan departemen tidak diperbolehkan menggunakan spasi.</li>
                    <li>Format penamaan file wajib mengikuti ketentuan.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div id="rekap-section" style="
        background-color: #f89a5b;
        padding: 30px 20px;
        text-align: center;
        max-width: 1500px;
        margin: 40px auto;
        border-radius: 12px;
        box-shadow: 0 0 40px rgba(243, 112, 33, 0.2);
    ">
        <h2 style="color:white;font-size: 40px;font-weight: 800; margin-bottom:10px;">
            Mulai Proses Rekap Sekarang
        </h2>
        <p style="color:white;font-size: 15px;font-weight: 800; margin:0;">
            Klik tombol di bawah untuk memulai sistem rekap absensi.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_d, col_e = st.columns(2)

    with col_d:
        st.markdown("""
        <div class="card" style="text-align:center;">
            <div style="font-size:26px; font-weight:700; margin-bottom:15px;">
                📝 Upload File Absensi
            </div>
        </div>
        """, unsafe_allow_html=True)

        file_absen = st.file_uploader(
            "",
            type=["csv", "xlsx", "xls"],
            key="absen_upload",
            label_visibility="collapsed"
        )


    with col_e:
        st.markdown("""
        <div class="card" style="text-align:center;">
            <div style="font-size:26px; font-weight:700; margin-bottom:15px;">
                📄 Upload File Izin
            </div>
        </div>
        """, unsafe_allow_html=True)

        file_izin = st.file_uploader(
            "",
            type=["csv", "xlsx", "xls"],
            key="izin_upload",
            label_visibility="collapsed"
        )


    return file_absen, file_izin
