import streamlit as st
import pandas as pd
import time
import numpy as np
import sqlite3
import json
from streamlit_option_menu import option_menu
from io import BytesIO
import os
# DATABASE
DB_PATH = "database.db"
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)
def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS app_data (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)
    conn.commit()
    conn.close()
init_db()
def save_db(key, value):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    INSERT OR REPLACE INTO app_data (key, value)
    VALUES (?, ?)
    """, (key, json.dumps(value)))
    conn.commit()
    conn.close()
def load_db(key):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT value FROM app_data WHERE key=?", (key,))
    result = c.fetchone()
    conn.close()
    if result:
        return json.loads(result[0])
    return None
# CONFIG
st.set_page_config(layout="wide")
# AUTO DETECT SEPARATOR
def load_data(file):
    try:
        return pd.read_csv(file, sep=None, engine='python')
    except:
        try:
            return pd.read_csv(file, sep=';')
        except:
            return pd.read_csv(file)
# MODERN SIDEBAR CSS
st.markdown("""
<style>
[data-testid="stSidebar"]{
    background: linear-gradient(
        180deg,
        #0f766e 0%,
        #115e59 100%
    );
}
[data-testid="stSidebar"] > div:first-child{
    background: transparent !important;
}
.logo{
    text-align:center;
    font-size:72px;
    margin-top:10px;
    margin-bottom:10px;
}
.sidebar-title{
    text-align:center;
    color:white;
    font-size:22px;
    font-weight:800;
    line-height:1.5;
    margin-bottom:5px;
}
.sidebar-subtitle{
    text-align:center;
    color:#ccfbf1;
    font-size:13px;
    margin-bottom:30px;
}
.nav{
    background: transparent !important;
    display:flex !important;
    flex-direction:column !important;
    gap:14px !important;
}
.nav-link{
    background: rgba(255,255,255,0.10) !important;
    color:white !important;
    border-radius:16px !important;
    padding:14px 18px !important;
    border:1px solid rgba(255,255,255,0.10);
    transition: all 0.25s ease !important;
    margin:0 !important;
}
.nav-link:hover{
    background: rgba(255,255,255,0.18) !important;
    transform: translateX(5px);
}
.nav-link.active,
.nav-link-selected{
    background: white !important;
    color:#0f766e !important;
    font-weight:700 !important;
    box-shadow:0 8px 18px rgba(0,0,0,0.15);
}
.nav-link i{
    font-size:18px !important;
}
/* text */
.nav-link span{
    font-size:16px !important;
    font-weight:600 !important;
}
/* hapus ul putih */
ul{
    background: transparent !important;
    padding-left:0 !important;
}
.blue-btn button{
    background: linear-gradient(
        135deg,
        #0f766e,
        #14b8a6
    ) !important;
    color:white !important;
    border:none !important;
    border-radius:12px !important;
    padding:10px 16px !important;
    font-weight:700 !important;
}
</style>
""", unsafe_allow_html=True)
# SIDEBAR
if "menu" not in st.session_state:
    st.session_state.menu = "Beranda"
with st.sidebar:
    st.markdown("""
    <div class='logo'>🌾</div>
    <div class='sidebar-title'>
        Sistem Pendukung Keputusan
        <br>
        Varietas Benih Padi
    </div>
    <div class='sidebar-subtitle'>
        AHP • Fuzzy AHP • TOPSIS
    </div>
    """, unsafe_allow_html=True)
    selected = option_menu(
        menu_title=None,
        options=[
            "Beranda",
            "Upload Data",
            "Preprocessing Data",
            "Pembobotan",
            "Perangkingan",
            "Evaluasi",
            "Panduan Input"
        ],
        icons=[
            "house-fill",
            "cloud-upload-fill",
            "sliders",
            "bar-chart-fill",
            "trophy-fill",
            "clipboard-data-fill",
            "book-fill"
        ],
        default_index=[
            "Beranda",
            "Upload Data",
            "Preprocessing Data",
            "Pembobotan",
            "Perangkingan",
            "Evaluasi",
            "Panduan Input"
        ].index(st.session_state.menu),
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "transparent",
            },
            "nav-link": {
                "font-size": "16px",
                "font-weight": "600",
                "text-align": "left",
                "--hover-color": "transparent",
            },
            "nav-link-selected": {
                "background-color": "#ffffff",
                "color": "#0f766e",
            },
            "icon": {
                "font-size": "18px"
            }
        }
    )
st.session_state.menu = selected
# LOAD DATA DARI DATABASE
data_db = load_db("data_awal")
if data_db:
    try:
        st.session_state.data = pd.DataFrame(data_db)
    except:
        st.session_state.data = None
else:
    st.session_state.data = None
# LOAD PREPROCESSING DATA
pre = load_db("preprocess")
if pre:
    st.session_state.data_preprocessed = pd.DataFrame(pre)
# LOAD CONFIG
config = load_db("config")
if config:
    st.session_state.drop_cols = config.get("drop_cols", [])
    st.session_state.kriteria = config.get("kriteria", [])
    st.session_state.alternatif = config.get("alternatif", None)
    st.session_state.sub_config = config.get("sub_config", {})
    st.session_state.mapping_kriteria = config.get("mapping_kriteria", {})
    st.session_state.ahp_matrix = config.get("ahp_matrix", None)
# LOAD BOBOT
bobot = load_db("bobot")
if bobot:
    st.session_state.bobot_ahp = pd.Series(bobot.get("ahp", {}))
    st.session_state.bobot_fuzzy = pd.Series(bobot.get("fuzzy", {}))
# LOAD SKENARIO
skenario = load_db("skenario")
if skenario:
    st.session_state.skenario_list = skenario
# BERANDA 
if selected == "Beranda":
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    :root{
        --accent-1: #0f766e;
        --accent-2: #14b8a6;
        --muted: #6b7280;
    }
    body, .css-1d391kg, .main, .block-container {font-family: 'Inter', sans-serif; background: var(--page-bg);}
    .hero {
        background: linear-gradient(135deg,var(--accent-1),var(--accent-2));
        padding: 56px 36px;
        border-radius: 20px;
        color: white;
        text-align: left;
        display: flex;
        gap: 30px;
        align-items: center;
        box-shadow: 0 12px 40px rgba(12,34,31,0.12);
        margin-bottom: 28px;
    }
    .hero-left{flex:1}
    .hero-right{width:320px; text-align:center}
    .hero h1{font-size:40px; margin:0; font-weight:800; text-align:center}
    .hero h2{font-size:20px; margin:6px 0 12px; font-weight:600; opacity:0.95; text-align:center}
    .hero p{margin:0; color:rgba(255,255,255,0.95); line-height:1.6}
    .hero-icon{font-size:72px; margin:8px auto 12px; text-align:center; display:block; line-height:1}
    .cta {
        margin-top:18px;
        display:flex; gap:12px; align-items:center;
    }
    .btn-primary{background:rgba(255,255,255,0.12); color:white; padding:10px 16px; border-radius:10px; font-weight:600; border:1px solid rgba(255,255,255,0.08)}
    .btn-secondary{background:white; color:var(--accent-1); padding:10px 14px; border-radius:10px; font-weight:600}
        .hero-image{margin-top:18px; text-align:center}
        .hero-image img{width:100%; max-width:640px; border-radius:12px; box-shadow:0 8px 30px rgba(2,6,8,0.12)}
    .info-box{background:var(--card-bg); padding:20px; border-radius:14px; box-shadow:0 6px 20px rgba(15,23,42,0.06); margin-bottom:20px}
    .info-title{font-size:20px; font-weight:700; color:#0f172a; text-align:center}
    .info-text{color:var(--muted); line-height:1.7}
    .features{display:flex; gap:18px; margin-top:14px}
    .feature{flex:1; background:var(--card-bg); padding:18px; border-radius:12px; box-shadow:0 6px 18px rgba(10,15,20,0.04); transition:transform .22s ease, box-shadow .22s ease}
    .feature:hover{transform:translateY(-6px); box-shadow:0 18px 40px rgba(12,34,31,0.07)}
    .feature .icon{font-size:28px}
    .feature .title{font-weight:700; margin-top:8px}
    .feature .desc{color:var(--muted); font-size:14px; margin-top:6px}
    .footer-box{background:linear-gradient(135deg,var(--accent-1),var(--accent-2)); padding:18px; border-radius:12px; text-align:center; color:white; font-weight:600}
    @media (max-width:900px){
        .hero{flex-direction:column;text-align:center}
        .hero-right{width:100%}
        .features{flex-direction:column}
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="hero">
        <div>
            <h1>Sistem Pendukung Keputusan</h1>
            <div class="hero-icon">🌾</div>
            <h2>Pemilihan Varietas Benih Padi — Metode AHP-TOPSIS & Fuzzy AHP-TOPSIS</h2>
            <p>
                Membantu pemilihan varietas benih padi terbaik secara objektif dan terukur.
                Bandingkan alternatif, jalankan skenario, dan evaluasi hasil nilai correlation Spearman Rank & NDCG.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""<div class="info-box">
<div class="info-title">📌 Tentang Sistem</div>
<div class="info-text">
Sistem ini Menggunakan metode kombinasi AHP, Fuzzy AHP, dan TOPSIS untuk
menghasilkan rekomendasi varietas benih padi. Dapat digunakan oleh penyuluh, peneliti, dan pelaku usaha pertanian.
<hr>
<strong>Fitur dinamis yang dapat diinputkan pengguna:</strong>
<ul>
    <li><strong>Alternatif:</strong> Daftar varietas benih padi yang akan dibandingkan. Pengguna bisa menambah / menghapus alternatif melalui menu Preprocessing Data.</li>
    <li><strong>Kriteria & Subkriteria:</strong> Tambah, hapus, atau edit kriteria (mis. produktivitas, umur panen, ketahanan penyakit, harga, kebutuhan air). Subkriteria juga didukung untuk kriteria yang kompleks.</li>
    <li><strong>Bobot AHP / Fuzzy:</strong> Pengguna dapat memasukkan matriks perbandingan berpasangan AHP atau menggunakan antarmuka fuzzy untuk menilai preferensi; sistem menghitung bobot otomatis.</li>
    <li><strong>Data Alternatif (atribut):</strong> Semua atribut numerik atau kategori untuk tiap alternatif dapat diunggah lewat CSV/Excel atau diedit langsung di tabel aplikasi.</li>
    <li><strong>Skenario Sensitivitas:</strong> Jalankan skenario perubahan bobot untuk melihat efek pada ranking (contohnya pertukaran bobot).</li>
    <li><strong>Evaluasi & Metode Pembanding:</strong> Pilih metrik evaluasi (Spearman Rank, NDCG) dan bandingkan hasil antara AHP, Fuzzy AHP, dan TOPSIS.</li>
</ul>
<strong>Contoh alur dinamis:</strong>
<ol>
    <li>Upload dataset (CSV/Excel) dengan kolom alternatif + atribut.</li>
    <li>Pilih dan atur kriteria serta subkriteria di menu Preprocessing Data.</li>
    <li>Masukkan atau hitung bobot (AHP / Fuzzy AHP).</li>
    <li>Jalankan TOPSIS untuk menghasilkan peringkat, lalu evaluasi hasil dengan Spearman / NDCG.</li>
    <li>Simpan konfigurasi sebagai skenario dan ekspor hasil bila perlu.</li>
</ol>
</div>
</div>""", unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px">
        <div style="font-size:20px; font-weight:800">🚀 Fitur Utama Sistem</div>
        <div style="color:var(--muted); font-size:14px">Mudah digunakan · Responsif · Terukur</div>
    </div>
    """, unsafe_allow_html=True)
    cols = st.columns(3)
    with cols[0]:
        st.markdown("""<div class="feature">
<div class="icon">📁</div>
<div class="title">Upload Dataset</div>
<div class="desc">Upload CSV / Excel, validasi otomatis, dan simpan ke database lokal.</div>
</div>""", unsafe_allow_html=True)
    with cols[1]:
        st.markdown("""
        <div class="feature">
            <div class="icon">⚙️</div>
            <div class="title">Preprocessing Data</div>
            <div class="desc">Pembersihan data, pemilihan kriteria, dan konfigurasi alternatif secara interaktif.</div>
        </div>
        """, unsafe_allow_html=True)
    with cols[2]:
        st.markdown("""
        <div class="feature">
            <div class="icon">📊</div>
            <div class="title">Pembobotan & TOPSIS</div>
            <div class="desc">Perhitungan bobot AHP / Fuzzy dan perankingan TOPSIS untuk keputusan terbaik.</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("""
    <div style="height:18px"></div>
    """, unsafe_allow_html=True)
    cols2 = st.columns(3)
    with cols2[0]:
        st.markdown("""
        <div class="feature">
            <div class="icon">🏆</div>
            <div class="title">Perangkingan</div>
            <div class="desc">Menentukan alternatif terbaik berbasis bobot dan skor multi-kriteria.</div>
        </div>
        """, unsafe_allow_html=True)
    with cols2[1]:
        st.markdown("""
        <div class="feature">
            <div class="icon">🧪</div>
            <div class="title">Skenario</div>
            <div class="desc">Uji sensitivitas bobot dan bandingkan hasil dengan cepat.</div>
        </div>
        """, unsafe_allow_html=True)
    with cols2[2]:
        st.markdown("""
        <div class="feature">
            <div class="icon">📈</div>
            <div class="title">Evaluasi</div>
            <div class="desc">Analisis Spearman dan NDCG untuk menilai konsistensi dan kualitas ranking.</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("""
    <div class="footer-box">✅ Sistem siap digunakan — Mulai dengan upload dataset atau buka demo.</div>
    """, unsafe_allow_html=True)
# MENU UPLOAD
if selected == "Upload Data":
    st.title("Upload Dataset")
    file = st.file_uploader("Upload file (CSV / Excel)")
    st.caption("""
📌 Upload terbaru akan menggantikan data lama dan menghapus proses perhitungan data lama.
Mendukung CSV & Excel dan auto separator.
""")
    if file is not None:
        try:
            fname = (file.name or "").strip()
            fname_lower = fname.lower()
            if not (fname_lower.endswith(".csv") or fname_lower.endswith(".xlsx") or fname_lower.endswith(".xls")):
                notif = st.empty()
                notif.warning("⚠️ Format file tidak didukung. Silakan upload file CSV (.csv) atau Excel (.xlsx/.xls).")
                time.sleep(4)
                notif.empty()
                st.stop()
            df = None
            ext = os.path.splitext(fname_lower)[1]
            try:
                if ext == ".csv":
                    try:
                        file.seek(0)
                    except Exception:
                        pass
                    df = load_data(file)
                else:
                    try:
                        content = file.read()
                    except Exception:
                        try:
                            content = file.getvalue()
                        except Exception:
                            content = None
                    if content is None:
                        raise ValueError("Gagal membaca konten file")
                    bio = BytesIO(content)
                    if ext == ".xls":
                        try:
                            df = pd.read_excel(bio, engine="xlrd")
                        except Exception as e:
                            if isinstance(e, ImportError) or "xlrd" in str(e).lower():
                                st.error("❌ File gagal dibaca: file .xls memerlukan paket 'xlrd'. Jalankan: pip install xlrd")
                            else:
                                st.error("❌ File .xls tidak dapat dibaca. Pastikan file valid atau simpan ulang sebagai .xlsx.")
                            raise
                    else:
                        try:
                            df = pd.read_excel(bio, engine="openpyxl")
                        except Exception as e_open:
                            try:
                                bio.seek(0)
                                df = pd.read_excel(bio)
                            except Exception as e_all:
                                msg = str(e_all).lower()
                                if "openpyxl" in msg or isinstance(e_open, ImportError) or "openpyxl" in str(e_open).lower():
                                    st.error("❌ File gagal dibaca: paket 'openpyxl' tidak terinstal atau file tidak valid. Jalankan: pip install openpyxl")
                                else:
                                    st.error("❌ File gagal dibaca. Pastikan file Excel valid atau coba simpan ulang sebagai .xlsx.")
                                raise
            except Exception as e:
                notif = st.empty()
                notif.error("❌ File gagal dibaca! Pastikan format benar.")
                try:
                    st.write(f"(debug) error: {e}")
                except Exception:
                    pass
                time.sleep(4)
                notif.empty()
                st.stop()
            if df is None or df.empty:
                notif = st.empty()
                notif.warning("⚠️ File kosong!")
                time.sleep(4)
                notif.empty()
                st.stop()
            if df.shape[1] < 2:
                st.error("❌ Data minimal harus memiliki 2 kolom!")
                st.stop()
            save_db("data_awal", df.to_dict())
            save_db("filename", fname)
            st.session_state.data = df
            save_db("preprocess", None)
            save_db("config", None)
            save_db("bobot", None)
            save_db("skenario", None)
            keys_to_reset = [
                "drop_cols",
                "data_preprocessed",
                "skenario_list",
                "data_edit",
                "kriteria",
                "alternatif",
                "sub_config",
                "mapping_kriteria",
                "ahp_matrix",
                "bobot_ahp",
                "bobot_fuzzy",
                "df_merge",
                "spearman_rho",
                "ndcg_value",
                "rank_pakar_data"
            ]
            for k in keys_to_reset:
                st.session_state.pop(k, None) 
            notif = st.empty()
            notif.success("✅ Upload berhasil! Seluruh konfigurasi lama telah direset total. Data baru siap diproses.")
            time.sleep(4)
            notif.empty()
        except Exception as e:
            st.error(f"❌ Terjadi kesalahan saat upload: {e}")
    if st.session_state.data is not None:
        df = st.session_state.data
        last_file = load_db("filename") or "-"
        st.info(f"Dataset aktif: {last_file}")
        col1,col2 = st.columns(2)
        col1.info(f"Jumlah Data: {df.shape[0]}")
        col2.info(f"Jumlah Variabel: {df.shape[1]}")
        st.subheader("Tipe Data Variabel")
        st.dataframe(pd.DataFrame({
            "Variabel": df.columns,
            "Tipe": df.dtypes.astype(str)
        }), use_container_width=True)
        st.subheader("Preview Data")
        st.dataframe(df, use_container_width=True)
        colA,colB,colC = st.columns([6,1,2])
        with colC:
            st.markdown('<div class="blue-btn">', unsafe_allow_html=True)
            if st.button("➡️ Preprocessing Data"):
                st.session_state.menu = "Preprocessing Data"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
# MENU PREPROCESSING DATA
elif selected == "Preprocessing Data":
    st.title("Preprocessing Data")
    df = st.session_state.data
    if df is None:
        st.warning("Upload data dulu")
    else:
        pre_db = load_db("preprocess")
        if pre_db:
            st.session_state.data_preprocessed = pd.DataFrame(pre_db)
        if "data_preprocessed" in st.session_state:
            st.info("📌 Menggunakan hasil Preprocessing Data tersimpan")
            df_preview = (st.session_state.data_preprocessed.copy())
            config_db = load_db("config")
            list_kriteria = []
            if config_db:
                list_kriteria = (
                    config_db.get(
                        "kriteria",
                        []
                    )
                )
            kolom_baru = {}
            for i, k in enumerate(
                list_kriteria
            ):
                c_kode = f"C{i+1}"
                if c_kode in df_preview.columns:
                    kolom_baru[c_kode] = (
                        f"{c_kode} ({k})"
                    )
            df_preview = df_preview.rename(
                columns=kolom_baru
            )
            st.dataframe(
                df_preview,
                use_container_width=True
            )
        data_db = load_db("data_awal")
        if data_db:
            df = pd.DataFrame(data_db)
            st.session_state.data = df
        else:
            st.warning("⚠️ Data belum tersedia, silakan upload dulu")
        st.subheader("📊 Data Awal")
        st.markdown("""
        ### 📝 Penjelasan:
        Data dapat diedit langsung pada tabel seperti Excel.
        
        ### Fitur:
        - Edit semua nilai (numerik / string)
        - Tambah baris otomatis
        - Tambah variabel (kolom)
        - Simpan perubahan ke database
                            
        ### Ketentuan:
        - Data tidak boleh kosong
        - Kolom tidak boleh duplikat
        - Jika numerik kosong → otomatis 0
        - Jika string kosong → tetap kosong ("")
        - Jumlah data mengikuti dataset utama
        """)
        data_db = load_db("data_awal")
        if data_db:
            df = pd.DataFrame(data_db)
            st.session_state.data = df
        else:
            df = st.session_state.data
        if "data_edit" not in st.session_state:
            st.session_state.data_edit = df.copy()
        df_for_editor = st.session_state.data_edit.copy()
        for col in df_for_editor.columns:
            df_for_editor[col] = df_for_editor[col].astype(str) 
        df_edit = st.data_editor(
            df_for_editor, 
            use_container_width=True,
            num_rows="dynamic",  
            key="main_editor"
        )
        if st.session_state.main_editor != st.session_state.get("last_editor_state", None):
            st.session_state.data_edit = df_edit
            st.session_state.last_editor_state = st.session_state.main_editor
        with st.expander("🧩 Ubah Struktur Kolom (Tambah / Hapus)", expanded=False):
            col1, col2 = st.columns([3,2])
            with col1:
                quick_col_name = st.text_input("Nama Kolom Baru (langsung ke editor)")
                st.caption("Contoh: 'Kualitas', 'KadarAir' — gunakan nama unik tanpa spasi berlebih")
            with col2:
                quick_col_type = st.selectbox("Tipe", ["Numerik", "String"], index=0)
                st.caption("Pilih 'Numerik' untuk nilai angka, 'String' untuk teks/kategori")
            if st.button("➕ Tambahkan Kolom ke Editor", key="quick_add_col"):
                if not quick_col_name:
                    st.error("❌ Nama kolom harus diisi")
                else:
                    df_temp = st.session_state.get("data_edit", pd.DataFrame()).copy()
                    if quick_col_name in df_temp.columns:
                        st.error("❌ Kolom sudah ada di editor")
                    else:
                        df_temp[quick_col_name] = "0" if quick_col_type == "Numerik" else ""
                        st.session_state.data_edit = df_temp
                        st.success(f"✅ Kolom '{quick_col_name}' ditambahkan ke editor")
                        st.experimental_rerun()
            cols_removable = [c for c in st.session_state.data_edit.columns]
            sel_remove = st.multiselect("Pilih kolom untuk dihapus dari editor", cols_removable)
            st.caption("Pilih kolom yang ingin dihapus dari editor (tidak dihapus otomatis dari database sampai Anda klik 'Simpan Perubahan Data')")
            if st.button("🗑️ Hapus Kolom dari Editor", key="quick_remove_col"):
                if not sel_remove:
                    st.error("❌ Pilih minimal 1 kolom untuk dihapus")
                else:
                    df_temp = st.session_state.data_edit.copy()
                    for c in sel_remove:
                        if c in df_temp.columns:
                            df_temp.drop(columns=[c], inplace=True)
                    st.session_state.data_edit = df_temp
                    st.success(f"✅ Kolom {', '.join(sel_remove)} dihapus dari editor")
                    st.experimental_rerun()
            st.markdown("---")
            st.markdown("**Ubah Nama Kolom**")
            rcol1, rcol2 = st.columns([3,3])
            with rcol1:
                col_to_rename = st.selectbox("Pilih kolom yang akan diganti namanya", options=list(st.session_state.get('data_edit', pd.DataFrame()).columns), index=0 if len(st.session_state.get('data_edit', pd.DataFrame()).columns) > 0 else None, key='rename_select')
                st.caption("Pilih kolom yang ingin diganti namanya (hanya editor saat ini)")
            with rcol2:
                new_col_name = st.text_input("Nama Kolom Baru", key='rename_new_name')
                st.caption("Masukkan nama baru yang unik — perubahan akan terlihat setelah klik tombol")
            if st.button("🔁 Ganti Nama Kolom", key='rename_col_btn'):
                try:
                    if not col_to_rename:
                        st.error("❌ Tidak ada kolom yang dipilih untuk diganti")
                    elif not new_col_name or str(new_col_name).strip() == "":
                        st.error("❌ Nama kolom baru tidak boleh kosong")
                    else:
                        df_temp = st.session_state.get('data_edit', pd.DataFrame()).copy()
                        if new_col_name in df_temp.columns:
                            st.error("❌ Nama kolom baru sudah ada (duplikat)")
                        else:
                            df_temp.rename(columns={col_to_rename: new_col_name}, inplace=True)
                            st.session_state.data_edit = df_temp
                            st.success(f"✅ Kolom '{col_to_rename}' berhasil diganti menjadi '{new_col_name}'")
                            st.experimental_rerun()
                except Exception as e:
                    st.error(f"❌ Gagal mengganti nama kolom: {e}")
        col1, col2 = st.columns(2)
        col1.info(f"Jumlah Baris: {df_edit.shape[0]}")
        col2.info(f"Jumlah Kolom: {df_edit.shape[1]}")
        st.markdown("""
        **Penjelasan:**
        Klik tombol ini untuk menyimpan semua perubahan pada tabel.

        **Kondisi:**
        - Semua perubahan akan menggantikan data lama
        - Data akan disimpan ke database
        - Pastikan tidak ada error sebelum menyimpan
        """)
        if st.button("💾 Simpan Perubahan Data"):
            try:
                df_save = st.session_state.get("data_edit", pd.DataFrame()).copy()
                if isinstance(df_save, dict):
                    df_save = pd.DataFrame(df_save)
                if not isinstance(df_save, pd.DataFrame):
                    df_save = pd.DataFrame(df_save)
                if df_save.empty:
                    st.error("❌ Data tidak boleh kosong!")
                    st.stop()
                if df_save.columns.duplicated().any():
                    st.error("❌ Terdapat nama kolom duplikat!")
                    st.stop()
                for col in df_save.columns:
                    if df_save[col].dtype == object:
                        df_save[col] = df_save[col].fillna("")
                    else:
                        df_save[col] = pd.to_numeric(df_save[col], errors='coerce').fillna(0)
                save_db("data_awal", df_save.to_dict())
                st.session_state.data = df_save
                notif = st.empty()
                notif.success("✅ Perubahan data berhasil disimpan!")
                time.sleep(3)
                notif.empty()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")
        st.subheader("1️⃣ Hapus Kolom")
        st.markdown("""
        **Penjelasan:**
        Tahap ini digunakan untuk menghapus kolom yang tidak diperlukan dalam proses pengambilan keputusan.

        **Tujuan:**
        Mengurangi noise dan fokus hanya pada kriteria penting.

        **Contoh:**
        Kolom seperti ID, Nama, atau Timestamp biasanya tidak digunakan sebagai kriteria.
        """)
        default_drop = st.session_state.get("drop_cols", [])
        default_drop = [c for c in default_drop if c in df.columns]
        drop_cols = st.multiselect(
            "Pilih kolom yang dihapus",
            df.columns,
            default=default_drop
        )
        df_clean = df.drop(columns=drop_cols)
        st.dataframe(df_clean, use_container_width=True)
        st.subheader("2️⃣ Pilih Kriteria")
        st.markdown("""
        **Penjelasan:**
        Kriteria adalah variabel yang digunakan dalam proses penilaian.

        **Tujuan:**
        Menentukan faktor yang mempengaruhi keputusan.

        **Contoh:**
        Produktivitas, Harga, Ketahanan, dll.
        """)
        default_kriteria = st.session_state.get("kriteria", [])
        default_kriteria = [k for k in default_kriteria if k in df_clean.columns]
        kriteria = st.multiselect(
            "Pilih kriteria:",
            df_clean.columns,
            default=default_kriteria
        )
        mapping_kriteria = {f"C{i+1}": kriteria[i] for i in range(len(kriteria))}
        st.subheader("3️⃣ Pilih Alternatif")
        st.markdown("""
        **Penjelasan:**
        Alternatif adalah objek yang akan dibandingkan.

        **Contoh:**
        Varietas benih padi: A1, A2, A3, dll.
        """)
        opsi_alternatif = [col for col in df_clean.columns if col not in kriteria]
        if not opsi_alternatif:
            st.warning("⚠️ Tidak ada kolom tersisa untuk alternatif!")
            alternatif = None
        else:
            default_alt = st.session_state.get("alternatif", None)
            index_alt = 0
            if default_alt in opsi_alternatif:
                index_alt = opsi_alternatif.index(default_alt)
            alternatif = st.selectbox(
                "Pilih alternatif:",
                opsi_alternatif,
                index=index_alt
            )
        if kriteria:
            st.subheader("4️⃣ Penentuan Sub Kriteria")
            st.markdown("""
            **Penjelasan :**

            Pada tahap ini setiap kriteria dipecah menjadi sub-kriteria yang mengkonversi
            nilai mentah (numerik atau kategori) menjadi skor numerik.

            Jenis input yang didukung:
            - Numerik (Rentang): Anda menentukan beberapa rentang (min, max) dan skor
            untuk tiap rentang. Contoh: 0–2 → 1 poin, 2.1–4 → 2 poin, dst.
            - Kategorikal: Untuk variabel kategori (mis. WarnaGabah = Putih / Kuning / Merah)
            tentukan mapping kategori → skor (mis. Putih → 3, Kuning → 2, Merah → 1).

            Konversi dilakukan berdasarkan judgement pakar:
            - Penentuan batas rentang dan skor biasanya dibuat bersama pakar/peneliti yang
            memahami sifat agronomis tiap kriteria (produktivitas, ketahanan hama, tekstur, dll).
            - Skala harus konsisten benefit: semakin besar skor berarti semakin baik (atau sebaliknya
            kalau kriteria cost — maka skor yang lebih kecil lebih baik). Jika kriteria
            sifatnya cost (mis. kebutuhan air), tandai dan map ke skala yang konsisten.

            Contoh konversi (Tekstur Nasi - kategorikal):
            - Pulen → 3
            - Agak Pulen → 2
            - Keras → 1

            Silakan isi sub-kriteria pada form di bawah ini. Setelah selesai, klik **Simpan Preprocessing Data**
            untuk menyimpan mapping dan melanjutkan ke tahap pembobotan.
            """, unsafe_allow_html=True)
            sub_config = {}
            old_sub_config = st.session_state.get("sub_config", {})
            for idx, k in enumerate(kriteria):
                st.markdown(f"### C{idx+1} - {k}")
                old_sub = old_sub_config.get(k, {})
                tipe_options = ["Numerik (Rentang)", "Kategorikal"]
                tipe_default = old_sub.get("tipe", "Numerik (Rentang)")
                tipe_index = tipe_options.index(tipe_default) if tipe_default in tipe_options else 0
                tipe = st.selectbox(
                    f"Tipe Data {k}",
                    tipe_options,
                    index=tipe_index,
                    key=f"tipe_{k}"
                )
                opsi_list = []
                old_opsi = old_sub.get("opsi", [])
                jumlah = st.number_input(
                    f"Jumlah Sub Kriteria {k}",
                    min_value=1,
                    max_value=10,
                    value=len(old_opsi) if old_opsi else 3,
                    step=1,
                    key=f"jumlah_{k}"
                )
                for i in range(int(jumlah)):
                    st.markdown(f"**Sub Kriteria {i+1}**")
                    cols = st.columns(3 if tipe=="Numerik (Rentang)" else 2)
                    if tipe == "Numerik (Rentang)":
                        old_o = old_opsi[i] if i < len(old_opsi) else {}
                        range_min = cols[0].number_input(
                            "Range Minimal",
                            step=0.1,
                            value=float(old_o.get("min", 0.0)),
                            key=f"{k}_min_{i}"
                        )
                        range_max = cols[1].number_input(
                            "Range Maksimal",
                            step=0.1,
                            value=float(old_o.get("max", 0.0)),
                            key=f"{k}_max_{i}"
                        )
                        nilai = cols[2].number_input(
                            "Nilai",
                            step=1,
                            value=int(old_o.get("nilai", 0)),
                            key=f"{k}_nilai_{i}"
                        )
                        opsi_list.append({"min":range_min,"max":range_max,"nilai":nilai})
                    else:
                        old_o = old_opsi[i] if i < len(old_opsi) else {}
                        kategori = cols[0].text_input(
                            "Kategori",
                            value=old_o.get("kategori", ""),
                            key=f"{k}_kat_{i}"
                        )
                        nilai = cols[1].number_input(
                            "Nilai",
                            step=1,
                            value=int(old_o.get("nilai", 0)),
                            key=f"{k}_nilai_kat_{i}"
                        )
                        opsi_list.append({"kategori":kategori,"nilai":nilai})
                    st.markdown("<hr style='margin:8px 0'>", unsafe_allow_html=True)
                sub_config[k] = {"tipe":tipe,"opsi":opsi_list}
        if st.button("💾 Simpan Preprocessing Data"):
            try:
                if not kriteria:
                    st.error("❌ Kriteria belum dipilih!")
                    st.stop()
                if alternatif is None:
                    st.error("❌ Alternatif belum dipilih!")
                    st.stop()
                if not sub_config:
                    st.error("❌ Sub kriteria belum diisi!")
                    st.stop()
                for k in kriteria:
                    tipe_sub = sub_config[k]["tipe"]
                    opsi_list = sub_config[k]["opsi"]
                    if tipe_sub == "Kategorikal":
                        kategori_tercatat = []
                        for i, o in enumerate(opsi_list):
                            nama_kat = str(o["kategori"]).strip().lower()
                            if not nama_kat:
                                st.error(f"❌ Nama Kategori pada {k} (Sub Kriteria {i+1}) tidak boleh kosong!")
                                st.stop()
                            if nama_kat in kategori_tercatat:
                                st.error(f"❌ Duplikat ditemukan! Nama kategori '{o['kategori']}' pada kriteria {k} diinput lebih dari sekali.")
                                st.stop()
                            kategori_tercatat.append(nama_kat)  
                    elif tipe_sub == "Numerik (Rentang)":
                        for i in range(len(opsi_list)):
                            min_i = opsi_list[i]["min"]
                            max_i = opsi_list[i]["max"]
                            if min_i == max_i:
                                st.error(f"❌ Input salah pada kriteria {k} (Sub Kriteria {i+1}): Nilai Minimal dan Maksimal tidak boleh sama ({min_i})!")
                                st.stop()
                            if min_i > max_i:
                                st.error(f"❌ Batas terbalik pada kriteria {k} (Sub Kriteria {i+1}): Nilai Minimal ({min_i}) tidak boleh lebih besar dari Maksimal ({max_i})!")
                                st.stop()
                            for j in range(i + 1, len(opsi_list)):
                                min_j = opsi_list[j]["min"]
                                max_j = opsi_list[j]["max"]
                                if not (max_i < min_j or min_i > max_j):
                                    st.error(f"❌ Rentang angka bertabrakan pada kriteria {k} (Sub Kriteria {i+1}): Sub Kriteria {i+1} [{min_i} - {max_i}] saling tumpang tindih dengan Sub Kriteria {j+1} [{min_j} - {max_j}].")
                                    st.stop()
                df_final = pd.DataFrame()
                df_final["Alternatif"] = df_clean[alternatif]
                for k in kriteria:
                    hasil = []
                    for val in df_clean[k].astype(str):
                        skor = 0
                        if sub_config[k]["tipe"] == "Numerik (Rentang)":
                            for o in sub_config[k]["opsi"]:
                                try:
                                    val_float = float(str(val).replace(",", "."))
                                except:
                                    val_float = 0
                                if o["min"] <= val_float <= o["max"]:
                                    skor = o["nilai"]
                        else:
                            for o in sub_config[k]["opsi"]:
                                if str(val).strip().lower() == str(o["kategori"]).strip().lower():
                                    skor = o["nilai"]
                        hasil.append(skor)
                    kode = f"C{list(kriteria).index(k)+1}"
                    df_final[kode] = hasil
                if df_final.empty:
                    st.error("❌ Hasil Preprocessing Data kosong!")
                    st.stop()
                save_db("preprocess", df_final.to_dict())
                save_db("config", {
                    "drop_cols": drop_cols,
                    "kriteria": kriteria,
                    "alternatif": alternatif,
                    "sub_config": sub_config,
                    "mapping_kriteria": mapping_kriteria
                })
                st.session_state.data_preprocessed = df_final
                st.success("✅ Preprocessing Data berhasil disimpan! Mengalihkan ke Pembobotan...")
                time.sleep(3)
                st.session_state.menu = "Pembobotan"
                st.rerun()
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: {e}")
# PEMBOBOTAN (AHP)
elif selected == "Pembobotan":
    st.title("Pembobotan Kriteria (AHP)")
    df = st.session_state.get("data_preprocessed")
    if df is None:
        st.warning("Lakukan Preprocessing Data dulu")
    else:
        kriteria = [col for col in df.columns if col != "Alternatif"]
        kriteria = sorted(kriteria, key=lambda x: int(x.replace("C","")))
        n = len(kriteria)
        config_db = load_db("config") or {}
        bobot_db = load_db("bobot") or {}
        if "ahp_matrix" in config_db and "ahp_matrix" not in st.session_state:
            st.session_state.ahp_matrix = pd.DataFrame(config_db["ahp_matrix"])
            st.session_state.ahp_matrix = st.session_state.ahp_matrix.reindex(index=kriteria, columns=kriteria)
        if "ahp" in bobot_db:
            st.session_state.bobot_ahp = pd.Series(bobot_db["ahp"])
        mapping = st.session_state.get("mapping_kriteria", {})
        st.subheader("Mapping Kriteria")
        if mapping:
            mapping = {k: mapping.get(k, k) for k in kriteria}
            st.dataframe(pd.DataFrame({
                "Kode": list(mapping.keys()),
                "Nama Asli": list(mapping.values())
            }))
        display_map = {c: f"{c} ({mapping.get(c, c)})" for c in kriteria}
        def _disp_df(df_obj):
            try:
                return df_obj.rename(index=display_map, columns=display_map)
            except Exception:
                try:
                    if isinstance(df_obj, pd.Series):
                        s = df_obj.rename(index=display_map)
                        colname = df_obj.name if getattr(df_obj, 'name', None) else 'Value'
                        return s.to_frame(colname)
                except Exception:
                    pass
            return df_obj
        st.info("Gunakan kode C1, C2, dst untuk perhitungan")
        st.subheader("📊 Skala Saaty (AHP)")
        st.markdown("""
        **Penjelasan:**
        Skala Saaty digunakan untuk menentukan tingkat kepentingan antar kriteria.

        **Tujuan:**
        Membandingkan kriteria secara berpasangan.
        """)
        df_saaty = pd.DataFrame({
            "Intensitas": ["1","3","5","7","9","2,4,6,8","Kebalikan"],
            "Definisi": [
                "Sama penting","Sedikit lebih penting","Lebih penting",
                "Sangat lebih penting","Mutlak lebih penting",
                "Nilai kompromi","Kebalikan"
            ],
            "Keterangan": [
                "Kedua kriteria memiliki tingkat kepentingan yang sama",
                "Satu kriteria sedikit lebih penting dibandingkan kriteria lainnya",
                "Satu kriteria lebih penting dibandingkan kriteria lainnya",
                "Satu kriteria jelas lebih mutlak penting",
                "Satu kriteria memiliki kepentingan mutlak",
                "Nilai kompromi di antara dua tingkat kepentingan",
                "Jika elemen i memiliki nilai terhadap j, maka j bernilai kebalikannya"
            ]
        })
        st.dataframe(df_saaty, use_container_width=True)
        # AHP
        st.header("🔷 AHP")
        st.subheader("1️⃣ Matriks Perbandingan")
        st.latex(r"A = [a_{ij}]")
        st.markdown("""
        **Keterangan:**
        - A adalah matriks perbandingan berpasangan antar kriteria.
        - aᵢⱼ adalah nilai perbandingan antara kriteria i dan j berdasarkan skala Saaty.
                    
        **Penjelasan:**
        Matriks ini adalah hasil akhir dari input pengguna yang telah diperbaiki secara otomatis.

        **Aturan AHP yang diterapkan:**
        - Diagonal (C1 vs C1) = 1 → karena membandingkan dirinya sendiri
        - Hanya bagian atas diagonal yang dapat diinput oleh user
        - Bagian bawah diagonal **tidak dapat diisi** - otomatis dihitung sebagai kebalikan (reciprocal)
        - Bagian bawah diagonal ditampilkan berwarna merah sebagai informasi nilai reciprocal

        **Rumus:**
        Jika:
        aᵢⱼ = x  
        maka:
        aⱼᵢ = 1 / x  

        **Contoh:**
        Jika:
        C1 dibanding C2 = 3  

        Maka:
        C2 dibanding C1 = 1/3 = 0.333
        """)

        mapping_kriteria = st.session_state.get("mapping_kriteria", {})
        kriteria_display = []
        for k in kriteria:
            nama_asli = mapping_kriteria.get(k, "")
            if nama_asli:
                kriteria_display.append(f"{k} ({nama_asli})")
            else:
                kriteria_display.append(k)
        if "ahp_matrix" not in st.session_state or st.session_state.ahp_matrix is None:
            st.session_state.ahp_matrix = pd.DataFrame(
                [[1.0]*n for _ in range(n)],
                columns=kriteria,
                index=kriteria
            )
        om = st.session_state.ahp_matrix
        if isinstance(om, dict):
            prev_matrix = pd.DataFrame(om).astype(float)
        else:
            prev_matrix = pd.DataFrame(om).copy().astype(float)
        matrix = pd.DataFrame(1.0, index=kriteria, columns=kriteria)
        st.markdown("""
        <style>
        div[data-testid="stNumberInput"] input {
            text-align: center;
            font-size: 0.85rem;
            padding: 4px 2px;
        }
        div[data-testid="stNumberInput"] {
            margin: 0px !important;
            padding: 0px !important;
        }
        div[data-testid="column"] {
            padding: 2px 3px !important;
        }
        .header-cell {
            background-color: #f0f2f6;
            border-radius: 6px;
            padding: 6px 4px;
            text-align: center;
            font-weight: 600;
            font-size: 0.78rem;
            color: #1f2937;
            min-height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            word-break: break-word;
            line-height: 1.2;
        }
        .row-label {
            background-color: #f0f2f6;
            border-radius: 6px;
            padding: 6px 6px;
            font-weight: 600;
            font-size: 0.78rem;
            color: #1f2937;
            min-height: 48px;
            display: flex;
            align-items: center;
            word-break: break-word;
            line-height: 1.2;
        }
        .diag-cell {
            text-align: center;
            padding-top: 10px;
            color: #6b7280;
            font-weight: bold;
            font-size: 1rem;
        }
        .recip-cell {
            text-align: center;
            padding-top: 10px;
            color: #c0392b;
            font-style: italic;
            font-size: 0.85rem;
            font-weight: 500;
        }
        </style>
        """, unsafe_allow_html=True)
        st.markdown("**Isi nilai perbandingan berpasangan (bagian atas diagonal saja):**")
        col_widths = [2] + [1]*n
        header_cols = st.columns(col_widths)
        header_cols[0].markdown("<div class='header-cell'>Kriteria</div>", unsafe_allow_html=True)
        for j in range(n):
            header_cols[j+1].markdown(f"<div class='header-cell'>{kriteria_display[j]}</div>", unsafe_allow_html=True)
        for i in range(n):
            row_cols = st.columns(col_widths)
            row_cols[0].markdown(f"<div class='row-label'>{kriteria_display[i]}</div>", unsafe_allow_html=True)
            for j in range(n):
                if i < j:
                    prev_val = float(prev_matrix.iloc[i, j])
                    val = row_cols[j+1].number_input(
                        label=f"{kriteria_display[i]} vs {kriteria_display[j]}",
                        min_value=0.111,
                        max_value=9.0,
                        value=prev_val,
                        step=0.5,
                        format="%.3f",
                        key=f"ahp_{i}_{j}",
                        label_visibility="collapsed"
                    )
                    matrix.iloc[i, j] = val
                    matrix.iloc[j, i] = round(1.0 / val, 4)
                elif i == j:
                    row_cols[j+1].markdown("<div class='diag-cell'>1</div>", unsafe_allow_html=True)
                else:
                    recip = matrix.iloc[i, j]
                    row_cols[j+1].markdown(f"<div class='recip-cell'>{round(recip, 3)}</div>", unsafe_allow_html=True)
        st.session_state.ahp_matrix = matrix
        st.subheader("2️⃣ Jumlah Kolom")
        st.latex(r"\sum_{i=1}^{n} a_{ij}")
        st.markdown("""
        **Keterangan:**
        - a_ij adalah elemen pada baris i dan kolom j dari matriks perbandingan AHP, yang menunjukkan perbandingan antara kriteria i dan kriteria j.
        - Jumlah kolom a_ij menunjukkan penjumlahan dari semua elemen dalam kolom j, yang berarti kita menjumlahkan nilai perbandingan dari semua kriteria terhadap kriteria j.
                    
        **Penjelasan:**
        Menjumlahkan nilai setiap kolom pada matriks perbandingan berpasangan AHP sebelumnya.

        **Tujuan:**
        Digunakan untuk normalisasi.
        """)
        col_sum = matrix.sum(axis=0)
        st.markdown("**Hasil Perhitungan Jumlah Kolom:**")
        calc_exprs = []
        for col in col_sum.index:
            vals = matrix[col].tolist()
            vals_str = ' + '.join([f"{v:.3f}" for v in vals])
            total = f"{col_sum[col]:.3f}"
            calc_exprs.append(f"{vals_str} = {total}")
        df_col_sum = pd.DataFrame({
            'Kriteria': [display_map.get(c, c) for c in col_sum.index],
            'Perhitungan Jumlah Kolom a_ij': calc_exprs,
            'Jumlah Kolom a_ij': col_sum.values
        }).set_index('Kriteria')
        st.dataframe(df_col_sum[["Perhitungan Jumlah Kolom a_ij","Jumlah Kolom a_ij"]], use_container_width=True)
        st.subheader("3️⃣ Normalisasi Matriks")
        st.latex(r"n_{ij} = \frac{a_{ij}}{\sum a_{ij}}")
        st.markdown("""
        **Keterangan:**
        - n_ij adalah elemen pada baris i dan kolom j dari matriks ternormalisasi, yang menunjukkan nilai perbandingan kriteria i terhadap kriteria j setelah dinormalisasi.
        - a_ij adalah elemen pada baris i dan kolom j dari matriks perbandingan AHP, yang menunjukkan perbandingan antara kriteria i dan kriteria j.
        - Jumlah Kolom a_ij adalah jumlah dari semua elemen dalam kolom j pada matriks perbandingan AHP, yang digunakan sebagai pembagi untuk normalisasi.
                    
        **Penjelasan:**
        Setiap nilai pada matriks perbandingan (a_ij) dibagi dengan jumlah kolom terkait untuk memperoleh nilai ternormalisasi n_ij.

        **Tujuan:**
        Mengubah ke skala 0-1 agar kolom dapat dibandingkan secara proporsional.
        """)
        norm = matrix.div(col_sum, axis=1)
        example_rows = n
        example_cols = n
        st.markdown("**Perhitungan Normaliasasi Matriks - setiap nilai matriks perbandingan (a_ij) dibagi dengan jumlah nilai kolom setiap kriteria (Jumlah Kolom a_ij):**")
        ex_index = [display_map.get(matrix.index[i], matrix.index[i]) for i in range(example_rows)]
        ex_columns = [display_map.get(matrix.columns[j], matrix.columns[j]) for j in range(example_cols)]
        ex_data = []
        for i in range(example_rows):
            row = []
            for j in range(example_cols):
                aij = matrix.iat[i, j]
                sumj = col_sum.iat[j]
                nij = norm.iat[i, j]
                row.append(f"{aij:.3f} / {sumj:.3f} = {nij:.3f}")
            ex_data.append(row)
        examples_df = pd.DataFrame(ex_data, index=ex_index, columns=ex_columns)
        examples_df.index.name = 'Kriteria'
        examples_df_display = examples_df.reset_index()
        st.dataframe(examples_df_display, use_container_width=True)
        st.markdown("**Hasil Perhitungan Normalisasi Matriks (n_ij):**")
        df_norm = _disp_df(norm).copy()
        df_norm.index.name = 'Kriteria'
        df_norm_display = df_norm.reset_index()
        st.dataframe(df_norm_display, use_container_width=True)
        st.subheader("4️⃣ Bobot Kriteria")
        st.latex(r"w_i = \frac{1}{n} \sum n_{ij}")
        st.markdown("""
        **Keterangan:**
        - w_i adalah bobot untuk kriteria i, yang menunjukkan prioritas relatif dari kriteria tersebut dalam proses pengambilan keputusan.
        - n adalah jumlah total kriteria yang dibandingkan, yang digunakan untuk menghitung rata-rata.
        - Jumlah n_ij adalah penjumlahan dari semua nilai ternormalisasi dalam baris i, yang menunjukkan total kontribusi kriteria i terhadap semua kriteria lainnya setelah normalisasi.
                    
        **Penjelasan:**
        Rata-rata setiap baris pada matriks ternormalisasi (mean dari n_{ij}).

        **Tujuan:**
        Menentukan prioritas relatif (bobot) tiap kriteria.
        """)
        bobot = norm.mean(axis=1)
        perhitungan_rows = []
        for idx in bobot.index:
            row_vals = norm.loc[idx].tolist()
            vals_str = ' + '.join([f"{v:.3f}" for v in row_vals])
            avg = bobot[idx]
            expr = f"({vals_str}) / {n} = {avg:.4f}"
            perhitungan_rows.append(expr)
        st.markdown("**Hasil Perhitungan Bobot Kriteria:**")
        df_bobot = pd.DataFrame({
            'Kriteria': [display_map.get(idx, idx) for idx in bobot.index],
            'Perhitungan (Jumlah Normalisasi Kriteria (Jumlah n_ij) / Jumlah Kriteria (n))': perhitungan_rows,
            'Bobot (w_i)': bobot.values
        }).set_index('Kriteria')
        st.dataframe(df_bobot[['Perhitungan (Jumlah Normalisasi Kriteria (Jumlah n_ij) / Jumlah Kriteria (n))','Bobot (w_i)']], use_container_width=True)
        st.subheader("5️⃣ Weighted Sum Vector")
        st.latex(r"A \times w")
        st.markdown("""
        **Keterangan:**
        - A adalah matriks perbandingan (A = [a_ij]) di mana a_ij menunjukkan perbandingan kriteria i terhadap kriteria j.
        - w adalah vektor bobot hasil normalisasi (w = [w_j]) yang menunjukkan prioritas tiap kriteria.
        - Aw adalah vektor hasil perkalian matriks A dengan vektor bobot w (Aw = A × w), yang menghasilkan nilai untuk setiap kriteria berdasarkan bobotnya.

        **Tujuan:** Perhitungan Aw dilakukan dengan mengalikan setiap elemen baris A dengan bobot w dan menjumlahkannya:

        """)
        st.markdown("**Matriks A (digunakan dalam perhitungan):**")
        a_disp = _disp_df(matrix).copy()
        a_disp.index.name = 'Kriteria'
        a_disp_display = a_disp.reset_index()
        st.dataframe(a_disp_display, use_container_width=True)
        st.markdown("**Bobot w Kriteria (digunakan dalam perhitungan):**")
        w_display = bobot.copy()
        try:
            w_idx = [display_map.get(idx, idx) for idx in w_display.index]
        except Exception:
            w_idx = list(w_display.index)
        df_w_display = pd.DataFrame({'Kriteria': w_idx, 'Bobot (w_i)': w_display.values}).set_index('Kriteria')
        st.dataframe(df_w_display, use_container_width=True)
        Aw = matrix.dot(bobot)
        aw_rows = []
        col_labels = [display_map.get(col, col) for col in matrix.columns]
        for i in range(n):
            terms = [matrix.iat[i, j] * bobot.iat[j] for j in range(n)]
            row = {col_labels[j]: f"{matrix.iat[i,j]:.3f}×{bobot.iat[j]:.4f} = {terms[j]:.4f}" for j in range(n)}
            numeric_terms = [f"{terms[j]:.4f}" for j in range(n)]
            row["Jumlah Total"] = ' + '.join(numeric_terms) + f" = {sum(terms):.4f}"
            row["Aw"] = sum(terms)
            aw_rows.append(row)
        aw_df = pd.DataFrame(aw_rows, index=[display_map.get(idx, idx) for idx in Aw.index])
        ordered_cols = col_labels + ["Jumlah Total", "Aw"]
        aw_df = aw_df[ordered_cols]
        st.markdown("**Hasil Perhitungan Aw (Weighted Sum Vector):**")
        aw_df_display = aw_df.reset_index()
        aw_df_display.rename(columns={aw_df_display.columns[0]: 'Kriteria'}, inplace=True)
        st.dataframe(aw_df_display, use_container_width=True)
        st.subheader("6️⃣ Eigen Value")
        st.latex(r"\lambda_i = \frac{Aw}{w}")
        st.markdown("""
        **Keterangan:**
        - λ_i adalah nilai eigen untuk kriteria i, yang menunjukkan rasio antara nilai Aw (hasil perkalian matriks A dengan vektor bobot w) dan bobot w_i untuk kriteria i.
        - Aw adalah vektor hasil perkalian matriks A dengan vektor bobot w (Aw = A × w), yang menghasilkan nilai untuk setiap kriteria berdasarkan bobotnya.
        - w_i adalah bobot untuk kriteria i, yang menunjukkan prioritas relatif dari kriteria tersebut dalam proses pengambilan keputusan.
                    
        **Penjelasan:**
        Lambda_i dihitung sebagai Aw_i / w_i untuk masing-masing baris.

        **Tujuan:**
        Menentukan lambda_max (rata-rata lambda_i) yang digunakan pada CI.
        """)
        lambda_i = Aw.div(bobot)
        lambda_rows = []
        for i, idx in enumerate(lambda_i.index):
            aw_val = float(Aw.iloc[i])
            try:
                w_val = float(bobot.loc[idx])
            except Exception:
                w_val = float(bobot.iloc[i])
            lam = aw_val / w_val if w_val != 0 else float('nan')
            lambda_rows.append({
                'Kriteria': display_map.get(idx, idx),
                'Aw (Weighted Sum Vector)': aw_val,
                'w (bobot)': w_val,
                'Perhitungan λ_i (Aw / w)': f"{aw_val:.4f} / {w_val:.4f} = {lam:.4f}",
                'λ_i (Nilai Eigen)': lam
            })
        lambda_df = pd.DataFrame(lambda_rows).set_index('Kriteria')
        st.markdown("**Perhitungan λ_i (per baris):**")
        st.dataframe(lambda_df[['Aw (Weighted Sum Vector)','w (bobot)','Perhitungan λ_i (Aw / w)', 'λ_i (Nilai Eigen)']], use_container_width=True)
        lambda_max = lambda_df['λ_i (Nilai Eigen)'].mean()
        lam_vals = [f"{v:.4f}" for v in lambda_df['λ_i (Nilai Eigen)'].values]
        lam_expr = ' + '.join(lam_vals)
        st.markdown(f"**Hasil Perhitungan Nilai rata-rata λ max =** ({lam_expr}) / {len(lambda_df)} = {lambda_max:.6f}")
        st.subheader("7️⃣ Consistency Index (CI)")
        st.latex(r"CI = \frac{\lambda_{max} - n}{n - 1}")
        st.markdown("""
        **Keterangan:**
        - CI (Consistency Index) adalah ukuran yang digunakan untuk menilai tingkat konsistensi dalam matriks perbandingan berpasangan AHP. Nilai CI dihitung berdasarkan selisih antara nilai eigen maksimum (λ_max) dan jumlah kriteria (n), dibagi dengan jumlah kriteria dikurangi satu (n - 1).
        - λ_max adalah nilai eigen maksimum yang diperoleh dari matriks perbandingan berpasangan AHP, yang mencerminkan tingkat konsistensi penilaian. Semakin dekat λ_max dengan n, semakin konsisten penilaian tersebut.
        - n adalah jumlah total kriteria yang dibandingkan dalam matriks perbandingan berpasangan AHP, yang digunakan untuk menghitung CI dan CR.
        """)
        st.markdown("**Penjelasan & Tujuan:** Mengukur tingkat konsistensi")
        if n > 1:
            CI = (lambda_max - n) / (n - 1)
            CI = round(CI, 6)
            if CI == 0.0:
                CI = 0.0
        else:
            CI = 0.0
        st.markdown("**Perhitungan CI:**")
        st.markdown(f"- $\lambda_{{max}}$ (rata-rata $\lambda_i$) = {lambda_max:.6f}")
        st.markdown(f"- $n$ (jumlah kriteria) = {n}")
        if n > 1:
            st.markdown(f"- CI (Consistency Index) = ({lambda_max:.6f} - {n}) / ({n} - 1) = {CI:.6f}")
        else:
            st.markdown(f"- CI (Consistency Index) = **{CI:.6f}** (Matriks 1x1 selalu konsisten)")
        st.subheader("8️⃣ Consistency Ratio (CR)")
        st.markdown("**Nilai Random Index (RI)**, adalah nilai indeks acak yang digunakan sebagai standar pembanding dalam Analytical Hierarchy Process (AHP) untuk mengukur konsistensi penilaian.") 
        RI_full = {
            1:0.00, 2:0.00, 3:0.52, 4:0.89, 5:1.11,
            6:1.25, 7:1.35, 8:1.40, 9:1.45, 10:1.49
        }
        cols = [str(i) for i in range(1, 11)]
        vals = [f"{RI_full[i]:.2f}" for i in range(1, 11)]
        ri_horiz = pd.DataFrame([vals], columns=cols, index=["RI"])
        st.dataframe(ri_horiz, use_container_width=True)
        ri_used = RI_full.get(n, None)
        if ri_used is not None:
            st.info(f"RI yang digunakan untuk jumlah kriteria (n) = {n} : {ri_used:.2f}")
        else:
            st.info(f"RI untuk n={n} tidak tersedia di tabel; digunakan default internal.")
        st.latex(r"CR = \frac{CI}{RI}")
        st.markdown("""
        **Keterangan:**
        - CR (Consistency Ratio) adalah rasio yang digunakan untuk menilai tingkat konsistensi dalam matriks perbandingan berpasangan AHP. CR dihitung dengan membagi Consistency Index (CI) dengan Random Index (RI), yang merupakan nilai indeks acak yang digunakan sebagai standar pembanding untuk jumlah kriteria tertentu.
        - CI (Consistency Index) adalah ukuran tingkat konsistensi matriks berdasarkan selisih nilai eigen maksimum (λ_max) dan jumlah kriteria (n).
        - RI (Random Index) adalah nilai acak standar dari tabel referensi yang disesuaikan dengan jumlah kriteria (n).
                    
        **Penjelasan:**
        Membandingkan CI dengan nilai random index.

        **Interpretasi:**
        - CR ≤ 0.1 → Konsisten  
        - CR > 0.1 → Tidak Konsisten  
                    
        **Diketahui:**
        """)
        st.markdown(f"- CI (Consistency Index) = {CI:.6f}")
        ri_val = RI_full.get(n, 1.49)
        if ri_val > 0:
            CR = CI / ri_val
        else:
            CR = 0.00
        st.markdown(f"- RI (Random Index) = {ri_val:.2f}")
        st.write(f"CR = {CI:.6f} / {ri_val:.2f} = {CR:.6f}")
        st.write(CR)
        st.markdown("""
        **Interpretasi:**
        - CR ≤ 0.1 → Konsisten  
        - CR > 0.1 → Tidak Konsisten  
                    
        """)
        if CR <= 0.1:
            st.success("Konsisten")
        else:
            st.error("Tidak Konsisten")
            try:
                def nearest_saaty_scale(x):
                    """Return a reasonable Saaty suggestion for x.
                    If x < 1, return reciprocal as display (e.g. '1/2').
                    Cap extreme estimates to a milder scale (7) to avoid suggesting unrealistic 9 when estimate is huge.
                    Returns tuple (numeric_value, display_str, note_or_none).
                    """
                    scales = [1,2,3,4,5,6,7,8,9]
                    if x <= 0 or not np.isfinite(x):
                        return (1.0, '1', None)
                    note = None
                    if x < 1.0:
                        r = 1.0 / x
                        s = min(scales, key=lambda s: abs(np.log(r) - np.log(s)))
                        if s > 7:
                            s = 7
                            note = 'Estimate sangat kecil; menyarankan kompromi 1/7 sebagai nilai yang lebih masuk akal.'
                        if s == 1:
                            s = 2
                            note = (note or '') + ' Menghindari saran 1; menggunakan 1/2 sebagai kompromi.'
                        return (1.0 / float(s), f"1/{s}", note)
                    else:
                        s = min(scales, key=lambda s: abs(np.log(x) - np.log(s)))
                        if x > 15 and s == 9:
                            s = 7
                            note = 'Estimasi sangat besar; menyarankan kompromi 7 (lebih moderat dari 9).'
                        if s == 1:
                            s = 2
                            note = (note or '') + ' Menghindari saran 1; menggunakan 2 sebagai kompromi.'
                        return (float(s), str(s), note)
                def suggest_corrections(mat, top=3):
                    n = mat.shape[0]
                    suggestions = []
                    for i in range(n):
                        for j in range(i+1, n):
                            cands = []
                            for k in range(n):
                                if k == i or k == j:
                                    continue
                                denom = mat.iloc[j, k]
                                num = mat.iloc[i, k]
                                try:
                                    if denom != 0 and not np.isnan(denom) and not np.isnan(num):
                                        cand = float(num) / float(denom)
                                        if cand > 0 and np.isfinite(cand):
                                            cands.append(cand)
                                except Exception:
                                    continue
                            if not cands:
                                continue
                            geom = float(np.exp(np.mean(np.log(np.array(cands)))))
                            current_val = float(mat.iloc[i, j]) if mat.iloc[i, j] > 0 else geom
                            try:
                                compromise = float(np.sqrt(current_val * geom))
                            except Exception:
                                compromise = geom
                            suggested_num, suggested_str, suggested_note = nearest_saaty_scale(compromise)
                            suggestions.append({
                                "pair": f"{mat.index[i]} vs {mat.columns[j]}",
                                "current": float(mat.iloc[i, j]),
                                "target_est": geom,
                                "suggested_numeric": suggested_num,
                                "suggested_display": suggested_str,
                                "note": suggested_note,
                                "compromise": compromise
                            })
                    def score(s):
                        return abs(np.log(s["current"]) - np.log(s["target_est"])) if s["current"]>0 else float('inf')
                    suggestions = sorted(suggestions, key=score, reverse=True)
                    return suggestions[:top]
                if CR > 0.1:
                    suggestions = suggest_corrections(matrix)
                    if suggestions:
                        st.markdown("**Saran perbaikan otomatis (mis. ubah nilai atas-diagonal):**")
                        sugg_df = pd.DataFrame(suggestions)
                        if not sugg_df.empty:
                            display_df = sugg_df[["pair","current","suggested_display","note"]].copy()
                            display_df.columns = ["Pasangan","Nilai Sekarang","Saran (Nilai yang Disarankan dari kriteria terlalu ekstrem)","Catatan"]
                            for c in ["Nilai Sekarang"]:
                                display_df[c] = display_df[c].apply(lambda v: f"{v:.3f}" if pd.notna(v) else "-")
                            st.dataframe(display_df, use_container_width=True)
                            st.caption("Catatan: ubah hanya bagian atas diagonal (mis.: C1 vs C2). Bagian bawah akan terisi otomatis sebagai reciprocal.")
                            def simulate_with_suggestions(mat, suggestions_list):
                                tmp = mat.copy().astype(float)
                                for s in suggestions_list:
                                    try:
                                        left, _, right = s['pair'].partition(' vs ')
                                        i = list(tmp.index).index(left)
                                        j = list(tmp.columns).index(right)
                                        val = float(s.get('suggested_numeric', s.get('suggested_numeric', tmp.iloc[i,j])))
                                        if val <= 0 or not np.isfinite(val):
                                            continue
                                        tmp.iat[i, j] = val
                                        tmp.iat[j, i] = 1.0 / val
                                    except Exception:
                                        continue
                                try:
                                    n_tmp = tmp.shape[0]
                                    col_sum_tmp = tmp.sum(axis=0)
                                    norm_tmp = tmp / col_sum_tmp
                                    w_tmp = norm_tmp.mean(axis=1)
                                    Aw_tmp = tmp.dot(w_tmp)
                                    lambda_i_tmp = Aw_tmp / w_tmp
                                    lambda_max_tmp = lambda_i_tmp.mean()
                                    CI_tmp = (lambda_max_tmp - n_tmp) / (n_tmp - 1) if n_tmp > 1 else 0
                                    RI_tmp = RI_full.get(n_tmp, 1.49)
                                    CR_tmp = CI_tmp / RI_tmp if RI_tmp != 0 else 0
                                    return tmp, CI_tmp, CR_tmp
                                except Exception:
                                    return tmp, None, None
                        st.markdown("""
                        **Petunjuk Penyesuaian Nilai:**

                        - **Urutan Prioritas:** Pasangan yang muncul teratas adalah penyumbang nilai tidak konsisten terbesar.
                        - **Batas Minimum:** Nilai `1` dihindari karena tidak memperbaiki konsistensi. Nilai terkecil adalah `2` (atau `1/2`).
                        - **Batas Maksimum:** Nilai saran dibatasi maksimal `7` agar tetap realistis dan masuk akal.
                        - **Sifat Saran:** Angka ini hanya rekomendasi. Anda bebas mengubah nilai, lalu tabel dan nilai CR akan otomatis dihitung ulang.
                                    
                        """)
            except Exception:
                pass
        bypass = st.checkbox("Bypass Konsistensi (izinkan simpan meskipun CR > 0.1)", value=False, key="bypass_consistency")
        st.caption("Gunakan bypass jika Anda yakin dengan penilaian Anda meskipun tidak konsisten sempurna.")
        st.subheader("9️⃣ Bobot Final & Prioritas (AHP)")
        st.markdown("""
        **Penjelasan:**
        Bobot final adalah hasil akhir AHP.

        **Interpretasi:**
        Semakin besar → semakin penting.
        """)
        df_ahp_final = pd.DataFrame({
            "Kriteria": bobot.index,
            "Bobot Final AHP (w)": bobot.values
        })
        df_ahp_final = df_ahp_final.sort_values(by="Bobot Final AHP (w)", ascending=False).reset_index(drop=True)
        df_ahp_final["Ranking"] = df_ahp_final.index + 1
        try:
            df_ahp_final = df_ahp_final.copy()
            df_ahp_final['Kriteria'] = df_ahp_final['Kriteria'].apply(lambda x: f"{x} ({mapping.get(x, x)})")
        except Exception:
            pass
        st.dataframe(df_ahp_final)
        st.success(f"Prioritas tertinggi: {df_ahp_final.iloc[0]['Kriteria']}")
        # FUZZY AHP
        st.header("🔶 Fuzzy AHP")
        st.subheader("📊 Skala TFN untuk Perbandingan Berpasangan")
        st.markdown("""
        **Penjelasan:**
        Skala TFN digunakan untuk mengubah nilai AHP menjadi bilangan fuzzy segitiga (Triangular Fuzzy Number).

        Setiap nilai memiliki 3 komponen:
        - l = lower (nilai bawah)
        - m = middle (nilai tengah)
        - u = upper (nilai atas)

        **Tujuan:**
        Mengatasi ketidakpastian subjektif agar hasil keputusan menjadi lebih akurat dan realistis.
        """)
        tfn_data = [
            (1, "(1, 1, 1)",     (1.0, 1.0, 1.0),       "(1, 1, 1)",       (1.0,1.0,1.0),       "Perbandingan elemen yang sama pentingnya"),
            (2, "(1/2, 1, 3/2)", (0.5, 1.0, 1.5),       "(2/3, 1, 2)",     (2/3,1.0,2.0),       "Pertengahan antara sama penting dan cukup penting"),
            (3, "(1, 3/2, 2)",   (1.0, 1.5, 2.0),       "(1/2, 2/3, 1)",   (0.5,2/3,1.0),       "Satu elemen cukup penting"),
            (4, "(3/2, 2, 5/2)", (1.5, 2.0, 2.5),       "(2/5, 1/2, 2/3)", (2/5,0.5,2/3),       "Pertengahan antara cukup penting dan kuat penting"),
            (5, "(2, 5/2, 3)",   (2.0, 2.5, 3.0),       "(1/3, 2/5, 1/2)", (1/3,2/5,0.5),       "Satu elemen kuat penting"),
            (6, "(5/2, 3, 7/2)", (2.5, 3.0, 3.5),       "(2/7, 1/3, 2/5)", (2/7,1/3,2/5),       "Pertengahan antara kuat dan lebih kuat penting"),
            (7, "(3, 7/2, 4)",   (3.0, 3.5, 4.0),       "(1/4, 2/7, 1/3)", (0.25,2/7,1/3),     "Satu elemen lebih kuat penting"),
            (8, "(7/2, 4, 9/2)", (3.5, 4.0, 4.5),       "(2/9, 1/4, 2/7)", (2/9,0.25,2/7),     "Pertengahan antara lebih kuat dan mutlak penting"),
            (9, "(4, 9/2, 9/2)", (4.0, 4.5, 4.5),       "(2/9, 2/9, 1/4)", (2/9,2/9,0.25),     "Satu elemen mutlak lebih penting")
        ]
        df_tfn_scale = pd.DataFrame([(
            r[0], r[1], f"{r[2][0]:.3f}, {r[2][1]:.3f}, {r[2][2]:.3f}", r[3], f"{r[4][0]:.3f}, {r[4][1]:.3f}, {r[4][2]:.3f}", r[5]
        ) for r in tfn_data], columns=["Skala AHP", "Skala TFN (frac)", "Skala TFN (dec)", "Kebalikan (frac)", "Kebalikan (dec)", "Keterangan Variabel Linguistik"])
        st.markdown("**Tabel konversi Skala AHP → TFN & kebalikan (reciprocal)**")
        st.dataframe(df_tfn_scale, use_container_width=True)
        st.markdown("**Istilah:**")
        st.markdown("- Frac (Fraction): Nilai dalam bentuk pecahan (contoh: 1/2, 3/2, 5/2).")
        st.markdown("- Dec (Decimal): Nilai dalam bentuk desimal (contoh: 0.500, 1.000, 1.500).")
        st.subheader("1️⃣ Konversi Matriks AHP ke TFN")
        st.latex(r"\tilde{A} = (l,m,u)")
        st.markdown("""
        **Keterangan:**
        - l = lower (nilai bawah)
        - m = middle (nilai tengah)
        - u = upper (nilai atas)
        """)
        st.markdown("""
        **Penjelasan:**
        Nilai matriks perbandingan AHP dari sebelumnya dikonversi menjadi TFN (Triangular Fuzzy Number).
        """)
        def get_tfn_scale():
            return {
                1:(1,1,1),
                2:(0.5,1,1.5),
                3:(1,1.5,2),
                4:(1.5,2,2.5),
                5:(2,2.5,3),
                6:(2.5,3,3.5),
                7:(3,3.5,4),
                8:(3.5,4,4.5),
                9:(4,4.5,4.5)
            }
        def get_tfn_inverse(scale):
            l,m,u = scale
            return (1/u,1/m,1/l)
        def get_nearest_scale(x):
            skala = [1,2,3,4,5,6,7,8,9]
            if x >= 1:
                return min(skala, key=lambda s: abs(s - x))
            else:
                return min(skala, key=lambda s: abs(s - (1/x)))
        def to_tfn(x):
            if x == 0:
                return (0,0,0)
            scale = get_nearest_scale(x)
            if x >= 1:
                return get_tfn_scale()[scale]
            else:
                return get_tfn_inverse(get_tfn_scale()[scale])
        fuzzy = [[to_tfn(matrix.iloc[i,j]) for j in range(n)] for i in range(n)]
        df_fuzzy_full = pd.DataFrame(
            [[str(f) for f in row] for row in fuzzy],
            columns=kriteria,
            index=kriteria
        )
        st.markdown("**Matriks A (nilai AHP)** --> **Matriks TFN (l,m,u)**")
        colA, colB = st.columns(2)
        with colA:
            st.write("A (nilai AHP)")
            tmp_a = _disp_df(matrix).round(4).copy()
            tmp_a.index.name = 'Kriteria'
            st.dataframe(tmp_a, use_container_width=True)
        with colB:
            st.write("Matriks TFN (l,m,u)")
            tmp_tfn = _disp_df(df_fuzzy_full).copy()
            tmp_tfn.index.name = 'Kriteria'
            st.dataframe(tmp_tfn, use_container_width=True)
        try:
            conv_rows = []
            for i in range(n):
                idx = matrix.index[i]
                row = {}
                for j in range(n):
                    aij = matrix.iat[i, j]
                    tfn = fuzzy[i][j]
                    row[f"{display_map.get(matrix.columns[j], matrix.columns[j])}"] = f"{aij:.4f} → ({tfn[0]:.3f}, {tfn[1]:.3f}, {tfn[2]:.3f})"
                conv_rows.append(row)
            conv_df = pd.DataFrame(conv_rows, index=[display_map.get(idx, idx) for idx in matrix.index])
            conv_df.index.name = 'Kriteria'
            st.markdown("**Rincian Konversi (AHP -> TFN):**")
            st.dataframe(conv_df, use_container_width=True)
        except Exception:
            pass
        st.subheader("2️⃣ Matriks L, M, U")
        st.markdown("""
        **Penjelasan:**
        Matriks TFN dipisahkan menjadi 3 bagian:
        - l = lower (nilai bawah)
        - m = middle (nilai tengah)
        - u = upper (nilai atas)

        **Tujuan:**
        Agar perhitungan fuzzy dilakukan per komponen.
        """)
        st.markdown("**Penjelasan singkat L/M/U:** komponen L/M/U adalah elemen pertama/tengah/terakhir dari TFN (l,m,u). Contoh: (2,3,4) → L=2, M=3, U=4.")
        try:
            cell_rows = []
            for i in range(n):
                idx = matrix.index[i]
                row = {}
                for j in range(n):
                    tfn = fuzzy[i][j]
                    frac_str = str(fuzzy[i][j])
                    row[display_map.get(matrix.columns[j], matrix.columns[j])] = f"{frac_str} → l = {tfn[0]:.3f}, m = {tfn[1]:.3f}, u = {tfn[2]:.3f}"
                cell_rows.append(row)
            cell_df = pd.DataFrame(cell_rows, index=[display_map.get(idx, idx) for idx in matrix.index])
            cell_df.index.name = 'Kriteria'
            st.markdown("**Rincian : Tabel TFN → L / M / U**")
            st.dataframe(cell_df, use_container_width=True)
        except Exception:
            pass
        df_l = pd.DataFrame([[f[0] for f in r] for r in fuzzy], columns=kriteria, index=kriteria)
        df_m = pd.DataFrame([[f[1] for f in r] for r in fuzzy], columns=kriteria, index=kriteria)
        df_u = pd.DataFrame([[f[2] for f in r] for r in fuzzy], columns=kriteria, index=kriteria)
        st.write("Hasil Lower (L)")
        tmp_l = _disp_df(df_l).copy()
        tmp_l.index.name = 'Kriteria'
        st.dataframe(tmp_l, use_container_width=True)
        st.write("Hasil Middle (M)")
        tmp_m = _disp_df(df_m).copy()
        tmp_m.index.name = 'Kriteria'
        st.dataframe(tmp_m, use_container_width=True)
        st.write("Hasil Upper (U)")
        tmp_u = _disp_df(df_u).copy()
        tmp_u.index.name = 'Kriteria'
        st.dataframe(tmp_u, use_container_width=True)
        st.subheader("3️⃣ Geometric Mean")
        st.latex(r"G_i = (\prod a_{ij})^{1/n}")
        var_df = pd.DataFrame({
            'Simbol': ['n (1/n)', 'l_ij / m_ij / u_ij (a_ij)', 'Prod L / Prod M / Prod U','G_l (calc) / G_m (calc) / G_u (calc)', 'G_l / G_m / G_u', 'Jumlah G_i'],
            'Keterangan': [
                'Jumlah kriteria (n) (contoh: 1/8 jika ada 8 kriteria)',
                'Komponen TFN untuk tiap sel: lower / middle / upper (contoh: 1, 1.5, 2)',
                'Hasil perkalian semua elemen pada satu baris (digunakan untuk akar di perhitungan G_l (calc) / G_m (calc) / G_u (calc))',
                'Perhitungan Geometric Mean per komponen',
                'Geometric mean per komponen (hasil akar ke-1/n dari Prod)',
                'Jumlah nilai Geometric Mean per komponen (G_l / G_m / G_u) (digunakan untuk normalisasi selanjutnya)'
            ]
        })
        st.markdown("**Keterangan Variabel (penjelasan singkat):**")
        st.dataframe(var_df, use_container_width=True)
        st.markdown("""
        **Penjelasan:**
        Menghitung rata-rata geometrik tiap baris.

        **Tujuan:**
        Menggabungkan semua perbandingan menjadi satu nilai.
        """)
        gm_l = df_l.prod(axis=1)**(1/n)
        gm_m = df_m.prod(axis=1)**(1/n)
        gm_u = df_u.prod(axis=1)**(1/n)
        df_gm = pd.DataFrame({
            'Kriteria': [display_map.get(idx, idx) for idx in gm_l.index],
            "G_l (Nilai Geometric Mean lower)": gm_l.values,
            "G_m (Nilai Geometric Mean middle)": gm_m.values,
            "G_u (Nilai Geometric Mean upper)": gm_u.values
        }).set_index('Kriteria')
        try:
            gm_detail_rows = []
            for idx in df_l.index:
                l_vals = list(df_l.loc[idx].values)
                m_vals = list(df_m.loc[idx].values)
                u_vals = list(df_u.loc[idx].values)
                prod_l = float(pd.Series(l_vals).prod())
                prod_m = float(pd.Series(m_vals).prod())
                prod_u = float(pd.Series(u_vals).prod())
                root_l = prod_l ** (1.0 / n) if prod_l >= 0 else float('nan')
                root_m = prod_m ** (1.0 / n) if prod_m >= 0 else float('nan')
                root_u = prod_u ** (1.0 / n) if prod_u >= 0 else float('nan')
                l_list = ', '.join([f"{v:.3f}" for v in l_vals])
                m_list = ', '.join([f"{v:.3f}" for v in m_vals])
                u_list = ', '.join([f"{v:.3f}" for v in u_vals])
                expr_l = ' × '.join([f"{v:.3f}" for v in l_vals])
                expr_m = ' × '.join([f"{v:.3f}" for v in m_vals])
                expr_u = ' × '.join([f"{v:.3f}" for v in u_vals])
                perhitungan_l = f"G_l,{display_map.get(idx, idx)} = ({expr_l})^(1/{n}) = {root_l:.7f}"
                perhitungan_m = f"G_m,{display_map.get(idx, idx)} = ({expr_m})^(1/{n}) = {root_m:.7f}"
                perhitungan_u = f"G_u,{display_map.get(idx, idx)} = ({expr_u})^(1/{n}) = {root_u:.7f}"
                gm_detail_rows.append({
                    'Kriteria': display_map.get(idx, idx),
                    'l_ij (lower)': f"({l_list})",
                    'm_ij (middle)': f"({m_list})",
                    'u_ij (upper)': f"({u_list})",
                    'Perhitungan G_l': perhitungan_l,
                    'G_l (numeric)': f"{root_l:.7f}",
                    'Perhitungan G_m': perhitungan_m,
                    'G_m (numeric)': f"{root_m:.7f}",
                    'Perhitungan G_u': perhitungan_u,
                    'G_u (numeric)': f"{root_u:.7f}"
                })
            st.markdown("**Rincian perhitunganGeometric Mean (per kriteria) - Tabel terpisah untuk L / M / U:**")
            rows_L = []
            rows_M = []
            rows_U = []
            for row in gm_detail_rows:
                k = row['Kriteria']
                def parse_list(s):
                    t = s.strip()
                    if t.startswith('(') and t.endswith(')'):
                        t = t[1:-1]
                    parts = [p.strip() for p in t.split(',') if p.strip() != '']
                    vals = []
                    for p in parts:
                        try:
                            vals.append(float(p))
                        except Exception:
                            try:
                                vals.append(float(p.replace(',', '.')))
                            except Exception:
                                vals.append(0.0)
                    return vals
                l_vals_parsed = parse_list(row['l_ij (lower)'])
                m_vals_parsed = parse_list(row['m_ij (middle)'])
                u_vals_parsed = parse_list(row['u_ij (upper)'])
                def prod_expr(vals):
                    return ' × '.join([f"{v:.3f}" for v in vals])
                def prod_val(vals):
                    p = 1.0
                    for v in vals:
                        p *= v
                    return p
                prodL_val = prod_val(l_vals_parsed)
                rows_L.append({
                    'Kriteria': k,
                    'l_ij (komponen lower)': row['l_ij (lower)'],
                    'Prod L (Hasil perkalian komponen lower)': f"{prod_expr(l_vals_parsed)} = {prodL_val:.7f}",
                    'G_l (Perhitungan Geometric Mean lower)': f"({prodL_val:.7f})^(1/{n}) = {row['G_l (numeric)']}",
                    'G_l (Nilai Geometric Mean lower)': row['G_l (numeric)']
                })
                prodM_val = prod_val(m_vals_parsed)
                rows_M.append({
                    'Kriteria': k,
                    'm_ij (komponen middle)': row['m_ij (middle)'],
                    'Prod M (Hasil perkalian komponen middle)': f"{prod_expr(m_vals_parsed)} = {prodM_val:.7f}",
                    'G_m (Perhitungan Geometric Mean middle)': f"({prodM_val:.7f})^(1/{n}) = {row['G_m (numeric)']}",
                    'G_m (Nilai Geometric Mean middle)': row['G_m (numeric)']
                })
                prodU_val = prod_val(u_vals_parsed)
                rows_U.append({
                    'Kriteria': k,
                    'u_ij (komponen upper)': row['u_ij (upper)'],
                    'Prod U (Hasil perkalian komponen upper)': f"{prod_expr(u_vals_parsed)} = {prodU_val:.7f}",
                    'G_u (Perhitungan Geometric Mean upper)': f"({prodU_val:.7f})^(1/{n}) = {row['G_u (numeric)']}",
                    'G_u (Nilai Geometric Mean upper)': row['G_u (numeric)']
                })
            df_L_view = pd.DataFrame(rows_L).set_index('Kriteria')
            df_M_view = pd.DataFrame(rows_M).set_index('Kriteria')
            df_U_view = pd.DataFrame(rows_U).set_index('Kriteria')
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Lower (L)**")
                st.dataframe(df_L_view, use_container_width=True)
            with c2:
                st.markdown("**Middle (M)**")
                st.dataframe(df_M_view, use_container_width=True)
            with c3:
                st.markdown("**Upper (U)**")
                st.dataframe(df_U_view, use_container_width=True)
            st.markdown("**Hasil Nilai Geometric Mean & Jumlah Nilai Geometric Mean per komponen (l, m, u):**")
            df_gm_disp = df_gm.copy()
            df_gm_disp = df_gm_disp.applymap(lambda v: float(f"{v:.6f}"))
            def sum_expr(series):
                vals = [f"{v:.6f}" for v in series.values]
                s = ' + '.join(vals)
                total = f"{series.sum():.6f}"
                return f"{s} = {total}"
            sum_l_expr = sum_expr(df_gm['G_l (Nilai Geometric Mean lower)'])
            sum_m_expr = sum_expr(df_gm['G_m (Nilai Geometric Mean middle)'])
            sum_u_expr = sum_expr(df_gm['G_u (Nilai Geometric Mean upper)'])
            totals_row = pd.DataFrame([[sum_l_expr, sum_m_expr, sum_u_expr]], columns=df_gm_disp.columns, index=['Jumlah G_i'])
            df_gm_combined = pd.concat([df_gm_disp, totals_row])
            st.dataframe(_disp_df(df_gm_combined), use_container_width=True)
        except Exception:
            pass
        st.subheader("4️⃣ Normalisasi Fuzzy")
        st.latex(r"w_i = \frac{G_i}{\sum G_i}")
        st.markdown("""
        **Keterangan:**
        - G_i adalah nilai Geometric Mean untuk kriteria i (per komponen l, m, u).
        - ΣG_i adalah jumlah total nilai Geometric Mean untuk semua kriteria (per komponen l, m, u).
        - w_l / w_m / w_u adalah bobot fuzzy hasil normalisasi untuk komponen lower / middle / upper.
        **Penjelasan:**
        Membagi setiap nilai Geometric Mean dengan Jumlah totalnya.

        **Tujuan:**
        Normalisasi ini bertujuan untuk memperoleh bobot relatif setiap kriteria dalam bentuk fuzzy, sehingga bobot antar kriteria dapat dibandingkan secara proporsional.
        """)
        w_l = gm_l / gm_l.sum()
        w_m = gm_m / gm_m.sum()
        w_u = gm_u / gm_u.sum()
        df_w = pd.DataFrame({
            "Kriteria": [display_map.get(idx, idx) for idx in w_l.index],
            "w_l (Hasil Normalisasi Bobot Lower)": w_l.values,
            "w_m (Hasil Normalisasi Bobot Middle)": w_m.values,
            "w_u (Hasil Normalisasi Bobot Upper)": w_u.values
        }).set_index('Kriteria')
        try:
            sum_l = gm_l.sum()
            sum_m = gm_m.sum()
            sum_u = gm_u.sum()
            rows_L = []
            rows_M = []
            rows_U = []
            for idx in gm_l.index:
                k = display_map.get(idx, idx)
                gl = gm_l.loc[idx]
                gm = gm_m.loc[idx]
                gu = gm_u.loc[idx]
                wl_v = w_l.loc[idx]
                wm_v = w_m.loc[idx]
                wu_v = w_u.loc[idx]
                rows_L.append({
                    'Kriteria': k,
                    'G_l (Nilai Geometric Mean lower)': f"{gl:.6f}",
                    'Jumlah G_l (Total Geometric Mean lower)': f"{sum_l:.6f}",
                    'Rincian G_l x Jumlah G_l': f"{gl:.6f} / {sum_l:.6f} = {wl_v:.6f}",
                    'Hasil w_l (Hasil Normalisasi Bobot Lower)': f"{wl_v:.6f}"
                })
                rows_M.append({
                    'Kriteria': k,
                    'G_m (Nilai Geometric Mean middle)': f"{gm:.6f}",
                    'Jumlah G_m (Total Geometric Mean middle)': f"{sum_m:.6f}",
                    'Rincian G_m x Jumlah G_m': f"{gm:.6f} / {sum_m:.6f} = {wm_v:.6f}",
                    'Hasil w_m (Hasil Normalisasi Bobot Middle)': f"{wm_v:.6f}"
                })
                rows_U.append({
                    'Kriteria': k,
                    'G_u (Nilai Geometric Mean upper)': f"{gu:.6f}",
                    'Jumlah G_u (Total Geometric Mean upper)': f"{sum_u:.6f}",
                    'Rincian G_u x Jumlah G_u': f"{gu:.6f} / {sum_u:.6f} = {wu_v:.6f}",
                    'Hasil w_u (Hasil Normalisasi Bobot Upper)': f"{wu_v:.6f}"
                })
            df_L_norm = pd.DataFrame(rows_L).set_index('Kriteria')
            df_M_norm = pd.DataFrame(rows_M).set_index('Kriteria')
            df_U_norm = pd.DataFrame(rows_U).set_index('Kriteria')
            st.markdown("**Rincian Perhitungan Normalisasi Fuzzy (dipisah per komponen l, m, u):**")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Normalisasi L (w_l)**")
                st.dataframe(df_L_norm, use_container_width=True)
            with c2:
                st.markdown("**Normalisasi M (w_m)**")
                st.dataframe(df_M_norm, use_container_width=True)
            with c3:
                st.markdown("**Normalisasi U (w_u)**")
                st.dataframe(df_U_norm, use_container_width=True)
            st.markdown("**Hasil Normalisasi Fuzzy:**")
            st.dataframe(_disp_df(df_w), use_container_width=True)
        except Exception:
            pass
        st.subheader("5️⃣ Defuzzifikasi")
        st.latex(r"W_i = \frac{w_l + w_m + w_u}{3}")
        st.markdown("""
        **Penjelasan:**
        Mengubah nilai fuzzy menjadi satu nilai tegas.

        **Tujuan:**
        Defuzzifikasi bertujuan untuk mengubah bobot fuzzy menjadi bobot tegas (crisp) sehingga dapat digunakan pada tahap pengambilan keputusan selanjutnya.
        """)
        w_def = (w_l + w_m + w_u) / 3
        df_w_def = pd.DataFrame({
            'Kriteria': [display_map.get(idx, idx) for idx in w_def.index],
            'W_i (Hasil Defuzzifikasi)': w_def.values
        }).set_index('Kriteria')
        try:
            def_rows = []
            for idx in w_def.index:
                a = w_l.loc[idx]
                b = w_m.loc[idx]
                c = w_u.loc[idx]
                val = w_def.loc[idx]
                def_rows.append({
                    'Kriteria': display_map.get(idx, idx),
                    'w_l ( Hasil Normalisasi Bobot Lower)': f"{a:.6f}",
                    'w_m (Hasil Normalisasi Bobot Middle)': f"{b:.6f}",
                    'w_u (Hasil Normalisasi Bobot Upper)': f"{c:.6f}",
                    'Rincian Hasil Perhitungan Defuzzifikasi': f"({a:.6f} + {b:.6f} + {c:.6f}) / 3 = {val:.6f}"
                })
            def_df = pd.DataFrame(def_rows).set_index('Kriteria')
            st.markdown("**Rincian Defuzzifikasi (per kriteria):**")
            st.dataframe(def_df, use_container_width=True)
            st.markdown("**Hasil Defuzzifikasi (per kriteria):**")
            tmp_w_def = df_w_def.copy()
            tmp_w_def.index.name = 'Kriteria'
            st.dataframe(tmp_w_def, use_container_width=True)
        except Exception:
            pass
        st.subheader("6️⃣ Normalisasi Akhir")
        st.latex(r"w = \frac{W_i}{\sum W_i}")
        st.markdown("""
        **Penjelasan:**
        Menjadikan total bobot = 1.

        **Tujuan:**
        Normalisasi bertujuan untuk memastikan bahwa total bobot seluruh kriteria bernilai satu / 1, sehingga bobot tersebut dapat digunakan secara proporsional dalam proses pengambilan keputusan. 
        """)
        w_final = w_def / w_def.sum()
        df_w_final = pd.DataFrame({
            'Kriteria': [display_map.get(idx, idx) for idx in w_final.index],
            'Bobot Final Fuzzy-AHP (w)': w_final.values
        }).set_index('Kriteria')
        try:
            total_w = w_def.sum()
            final_rows = []
            for idx in w_final.index:
                numerator = w_def.loc[idx]
                denom = total_w
                final_rows.append({
                    'Kriteria': display_map.get(idx, idx),
                    'W_i (Hasil Defuzzifikasi)': f"{numerator:.6f}",
                    'Jumlah Total W_i (bobot)': f"{denom:.6f}",
                    'Bobot Final Fuzzy-AHP (w)': f"{w_final.loc[idx]:.6f}",
                    'Rincian Normalisasi (W_i / Jumlah Total W_i)': f"{numerator:.6f} / {denom:.6f} = {w_final.loc[idx]:.6f}"
                })
            final_detail_df = pd.DataFrame(final_rows).set_index('Kriteria')
            st.markdown("**Rincian Normalisasi Akhir (per kriteria):**")
            st.dataframe(final_detail_df, use_container_width=True)
            st.markdown("**Hasil Normalisasi Akhir (per kriteria):**")
            st.dataframe(df_w_final, use_container_width=True)
        except Exception:
            pass
        st.subheader("7️⃣ Bobot Final & Prioritas (Fuzzy AHP)")
        st.markdown("""
        **Penjelasan:**
        Bobot final adalah hasil akhir Fuzzy AHP.

        **Interpretasi:**
        Semakin besar → semakin penting.
        """)
        df_fuzzy_final = pd.DataFrame({
            "Kriteria": w_final.index,
            "Bobot Final Fuzzy-AHP (w)": w_final.values
        })
        df_fuzzy_final = df_fuzzy_final.sort_values(by="Bobot Final Fuzzy-AHP (w)", ascending=False).reset_index(drop=True)
        df_fuzzy_final["Ranking"] = df_fuzzy_final.index + 1
        try:
            df_fuzzy_final = df_fuzzy_final.copy()
            df_fuzzy_final['Kriteria'] = df_fuzzy_final['Kriteria'].apply(lambda x: f"{x} ({mapping.get(x, x)})")
        except Exception:
            pass
        st.dataframe(df_fuzzy_final)
        st.success(f"Prioritas tertinggi (Fuzzy): {df_fuzzy_final.iloc[0]['Kriteria']}")
        st.markdown("---")
        if st.button("💾 Simpan Bobot (AHP & Fuzzy)"):
            try:
                try:
                    if CR is not None and float(CR) > 0.1 and not bypass:
                        st.error("❌ Tabel Pembobotan Matriks AHP tidak konsisten. Perbaiki matriks AHP sebelum menyimpan dan melanjutkan ke tahap perangkingan, atau centang 'Bypass Konsistensi' jika Anda yakin ingin menyimpan.")
                        st.stop()
                except Exception:
                    pass
                if bobot is None or w_final is None:
                    st.error("❌ Bobot belum tersedia!")
                    st.stop()
                if matrix is None or matrix.empty:
                    st.error("❌ Matriks AHP kosong!")
                    st.stop()
                if bobot.sum() == 0 or w_final.sum() == 0:
                    st.error("❌ Bobot tidak valid (jumlah = 0)")
                    st.stop()
                config_db = load_db("config") or {}
                config_db.update({
                    "ahp_matrix": matrix.to_dict()
                })
                save_db("config", config_db)
                save_db("bobot", {
                    "ahp": bobot.to_dict(),
                    "fuzzy": w_final.to_dict()
                })
                st.session_state.bobot_ahp = bobot
                st.session_state.bobot_fuzzy = w_final
                st.success("✅ Bobot berhasil disimpan!")
                time.sleep(3)
                st.session_state.menu = "Perangkingan"
                st.rerun()
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: {e}")
# PERANGKINGAN (TOPSIS - AHP)
elif selected == "Perangkingan":
    st.title("Perangkingan Metode TOPSIS (AHP)")
    df = st.session_state.get("data_preprocessed")
    bobot_db = load_db("bobot") or {}
    if "ahp" in bobot_db:
        st.session_state.bobot_ahp = pd.Series(bobot_db["ahp"])
    bobot = st.session_state.get("bobot_ahp")
    if df is None:
        st.warning("Data belum ada")
    elif bobot is None:
        st.warning("Bobot AHP & Fuzzy AHP belum tersedia")
    else:
        alternatif = df.iloc[:, 0]
        X = df.iloc[:, 1:]
        mapping = st.session_state.get("mapping_kriteria", {})
        mapping = {k: mapping.get(k, k) for k in X.columns}
        display_map = {c: f"{c} ({mapping.get(c, c)})" for c in X.columns}
        st.subheader("1️⃣ Matriks Keputusan")
        st.markdown("""
        **Penjelasan:**
        Matriks keputusan data berisi nilai setiap alternatif terhadap setiap kriteria yang sudah di-Preprocessing Data.

        **Tujuan:**
        Menjadi dasar perhitungan TOPSIS.
        """)
        df_X = pd.concat([alternatif, X], axis=1)
        df_X_display = df_X.copy()
        df_X_display.columns = ['Alternatif'] + [display_map.get(c, c) for c in X.columns]
        st.markdown("**Matriks Keputusan (dengan Alternatif)**")
        st.dataframe(df_X_display, use_container_width=True)
        st.subheader("2️⃣ Normalisasi Matriks")
        st.latex(r"r_{ij} = \frac{x_{ij}}{\sqrt{\sum x_{ij}^2}}")
        st.markdown("""
        **Keterangan:**
        - r_ij adalah nilai normalisasi untuk alternatif i pada kriteria j.
        - x_ij adalah nilai alternatif i pada kriteria j.
        - Nilai Pembagi (x_ij) adalah akar dari jumlah kuadrat nilai pada kolom kriteria j.
                    
        **Penjelasan:**
        Normalisasi dilakukan untuk menyamakan skala antar kriteria.

        **Tujuan:**
        Agar semua kriteria dapat dibandingkan secara adil.
        """)
        pembagi = (X**2).sum()**0.5
        cols = X.columns
        col_labels = [display_map.get(c, c) for c in cols]
        calc_pembagi = []
        for j, c in enumerate(cols):
            vals = X[c].tolist()
            vals_str = ' + '.join([f"{v:.3f}^2" for v in vals])
            expr = f"sqrt({vals_str}) = {pembagi[c]:.6f}"
            calc_pembagi.append(expr)
        df_pembagi = pd.DataFrame({'Kriteria': col_labels, 'Perhitungan nilai pembagi akar (x_ij) kuadrat': calc_pembagi, 'Hasil Total Nilai Pembagi (x_ij)': pembagi.values}).set_index('Kriteria')
        st.markdown("**Perhitungan Pembagi Normalisasi per Kriteria:**")
        st.dataframe(df_pembagi, use_container_width=True)
        R = X / pembagi
        R_rows = []
        for i in range(R.shape[0]):
            row = {'Alternatif': alternatif.iat[i]}
            for j, c in enumerate(cols):
                xij = X.iat[i, j]
                denom = pembagi[c]
                rij = R.iat[i, j]
                row[col_labels[j]] = f"{xij:.3f} / {denom:.6f} = {rij:.6f}"
            R_rows.append(row)
        df_R_expr = pd.DataFrame(R_rows).set_index('Alternatif')
        st.markdown("**Perhitungan Matriks Normalisasi r_ij = (x_ij / pembagi):**")
        st.dataframe(df_R_expr, use_container_width=True)
        st.subheader("3️⃣ Matriks Ternormalisasi Terbobot")
        st.latex(r"y_{ij} = r_{ij} \times w_j")
        st.markdown("""
        **Keterangan:**
        - y_ij adalah nilai terbobot untuk alternatif i pada kriteria j setelah normalisasi.
        - r_ij adalah nilai normalisasi untuk alternatif i pada kriteria j.
        - w_j adalah nilai bobot ahp per kriteria j.
                    
        **Penjelasan:**
        Mengalikan hasil normalisasi dengan bobot AHP.

        **Tujuan:**
        Menentukan kontribusi tiap kriteria.
        """)
        st.markdown("**Tabel yang digunakan untuk menghitung Matriks Ternormalisasi Terbobot:**")
        st.markdown("**1. Hasil Matriks Normalisasi (r_ij)**")
        df_R = pd.concat([alternatif, R], axis=1)
        df_R_display = df_R.copy()
        df_R_display.columns = ['Alternatif'] + col_labels
        st.dataframe(df_R_display, use_container_width=True)
        try:
            ahp_vals = []
            for c in cols:
                try:
                    v = float(bobot.loc[c])
                except Exception:
                    v = float(bobot.iloc[list(X.columns).index(c)])
                ahp_vals.append(v)
            df_w_ahp = pd.DataFrame({'Kriteria': col_labels, 'Bobot AHP': ahp_vals}).set_index('Kriteria')
        except Exception:
            df_w_ahp = pd.DataFrame({'Kriteria': col_labels, 'Bobot AHP': [None]*len(col_labels)}).set_index('Kriteria')
        st.markdown("**2. Bobot AHP (w_j)**")
        st.dataframe(df_w_ahp, use_container_width=True)
        weights = [float(x) for x in df_w_ahp['Bobot AHP'].values]
        Y = R * np.array(weights)
        df_Y = pd.concat([alternatif, Y], axis=1)
        Y_rows_expr = []
        for i in range(Y.shape[0]):
            row = {'Alternatif': alternatif.iat[i]}
            for j, c in enumerate(cols):
                rij = R.iat[i, j]
                wj = weights[j]
                yij = Y.iat[i, j]
                row[col_labels[j]] = f"{rij:.6f} × {wj:.6f} = {yij:.6f}"
            Y_rows_expr.append(row)
        df_Y_expr = pd.DataFrame(Y_rows_expr).set_index('Alternatif')
        st.markdown("**Perhitungan Matriks Ternormalisasi Terbobot y_ij = (r_ij × w_j)**")
        st.dataframe(df_Y_expr, use_container_width=True)
        st.subheader("4️⃣ Solusi Ideal Positif & Negatif")
        st.latex(r"y_j^{+} = \max\left(y_{ij}\right),\quad y_j^{-} = \min\left(y_{ij}\right)")
        st.markdown("""
        **Keterangan:**
        - y_j+ = nilai maksimum untuk kriteria j
        - y_j- = nilai minimum untuk kriteria j
        - A+ = nilai maksimum (terbaik)
        - A- = nilai minimum (terburuk)
                    
        **Penjelasan:**
        Menentukan solusi ideal positif (A+) dan negatif (A-) untuk setiap kriteria.

        **Tujuan:**
        Menentukan titik referensi terbaik dan terburuk.
        """)
        df_Y = pd.concat([alternatif, Y], axis=1)
        df_Y_numeric = df_Y.copy()
        df_Y_numeric.columns = ['Alternatif'] + col_labels
        st.markdown("**Tabel yang digunakan untuk menentukan Solusi Ideal Positif (A+) dan Negatif (A-):**")
        st.markdown("**Hasil Matriks Ternormalisasi Terbobot (y_ij) - digunakan untuk menentukan Nilai (A+ & A-) atau (y_j+ dan y_j-) setiap kriteria dari seluruh alternatif**")
        st.dataframe(df_Y_numeric, use_container_width=True)
        A_plus = Y.max()
        A_minus = Y.min()
        df_Apm = pd.DataFrame({
            'Kriteria': col_labels,
            'A+ atau y_j+ (Positif)': A_plus.values,
            'A- atau y_j- (Negatif)': A_minus.values
        }).set_index('Kriteria')
        st.markdown("**Hasil Solusi Ideal Positif (A+) atau (y_j+) & Negatif (A-) atau (y_j-)**")
        st.dataframe(df_Apm, use_container_width=True)
        st.subheader("5️⃣ Jarak ke Solusi Ideal")
        st.latex(r"D_i^+ = \sqrt{\sum (y_{ij} - y_j^+)^2}")
        st.latex(r"D_i^- = \sqrt{\sum (y_{ij} - y_j^-)^2}")
        st.markdown("""
        **Keterangan:**
        - D_i+ = jarak alternatif i ke solusi ideal positif (A+)
        - D_i- = jarak alternatif i ke solusi ideal negatif (A-)
        - y_ij = nilai terbobot untuk alternatif i pada kriteria j
        - y_j+ = nilai solusi ideal positif untuk kriteria j
        - y_j- = nilai solusi ideal negatif untuk kriteria j
                    
        **Penjelasan:**
        Mengukur jarak setiap alternatif terhadap solusi ideal.

        **Tujuan:**
        Menentukan seberapa dekat alternatif dengan kondisi terbaik.
        """)
        st.markdown("**Tabel yang digunakan untuk perhitungan Jarak ke Solusi Ideal (D+ & D-):**")
        df_Y_used = pd.concat([alternatif, Y], axis=1)
        df_Y_used_disp = df_Y_used.copy()
        df_Y_used_disp.columns = ['Alternatif'] + col_labels
        st.markdown("**1.Hasil Matriks Ternormalisasi Terbobot (y_ij)**")
        st.dataframe(df_Y_used_disp, use_container_width=True)
        st.markdown("**2.Solusi Ideal (A+ & A-) atau (y_j+ & y_j-)**")
        st.dataframe(df_Apm, use_container_width=True)
        D_plus = ((Y - A_plus)**2).sum(axis=1)**0.5
        D_minus = ((Y - A_minus)**2).sum(axis=1)**0.5
        dplus_rows = []
        dminus_rows = []
        for i in range(Y.shape[0]):
            terms_p = []
            terms_m = []
            for j, c in enumerate(cols):
                yij = Y.iat[i, j]
                ap = A_plus.iloc[j]
                am = A_minus.iloc[j]
                tp = (yij - ap)**2
                tm = (yij - am)**2
                terms_p.append(f"({yij:.6f} - {ap:.6f})^2 = {tp:.6f}")
                terms_m.append(f"({yij:.6f} - {am:.6f})^2 = {tm:.6f}")
            sum_p = D_plus.iat[i]
            sum_m = D_minus.iat[i]
            expr_p = ' + '.join(terms_p) + f" = {sum_p:.6f}"
            expr_m = ' + '.join(terms_m) + f" = {sum_m:.6f}"
            dplus_rows.append({'Alternatif': alternatif.iat[i], 'Perhitungan D+ ((D_i+ = akar dari jumlah kuadrat y_ij - y_j+))': expr_p, 'Hasil D+ (Jarak ke Solusi Positif)': sum_p})
            dminus_rows.append({'Alternatif': alternatif.iat[i], 'Perhitungan D- ((D_i- = akar dari jumlah kuadrat y_ij - y_j-))': expr_m, 'Hasil D- (Jarak ke Solusi Negatif)': sum_m})
        df_D_plus = pd.DataFrame(dplus_rows).set_index('Alternatif')
        df_D_minus = pd.DataFrame(dminus_rows).set_index('Alternatif')
        st.markdown("**Perhitungan Jarak ke Solusi Ideal (D+ & D-) - rincian per data alternatif**")
        st.markdown("**Hasil Perhitungan D+ jarak ke solusi positif (D_i+ = akar dari jumlah kuadrat y_ij - y_j+)**")
        st.dataframe(df_D_plus, use_container_width=True)
        st.markdown("**Hasil Perhitungan D- jarak ke solusi negatif (D_i- = akar dari jumlah kuadrat y_ij - y_j-)**")
        st.dataframe(df_D_minus, use_container_width=True)
        st.subheader("6️⃣ Nilai Preferensi")
        st.latex(r"V_i = \frac{D_i^-}{D_i^+ + D_i^-}")
        st.markdown("""
        **Keterangan:**
        - V_i = nilai preferensi untuk alternatif i
        - D_i+ = jarak alternatif i ke solusi ideal positif (A+)
        - D_i- = jarak alternatif i ke solusi ideal negatif (A-)
                    
        **Penjelasan:**
        Nilai preferensi menunjukkan kualitas alternatif.

        **Interpretasi:**
        Semakin mendekati 1 → semakin baik.
        """)
        st.markdown("**Tabel yang digunakan untuk perhitungan Nilai Preferensi (V atau V_i):**")
        V = D_minus / (D_plus + D_minus)
        df_V_numeric = pd.DataFrame({
            'Alternatif': alternatif,
            'D+': D_plus,
            'D-': D_minus,
        }).reset_index(drop=True).set_index('Alternatif')
        st.markdown("**Hasil Perhitungan D+ (Jarak ke Solusi Positif) dan D- (Jarak ke Solusi Negatif)**")
        st.dataframe(df_V_numeric, use_container_width=True)
        V_rows = []
        for i in range(V.shape[0]):
            d_p = D_plus.iat[i]
            d_m = D_minus.iat[i]
            v = V.iat[i]
            rincian = f"{d_m:.6f} / ({d_p:.6f} + {d_m:.6f}) = {v:.6f}"
            V_rows.append({'Alternatif': alternatif.iat[i], 'Perhitungan Nilai Preferensi V (V_i = D_i-/(D_i+ + D_i-))': rincian, 'Hasil Nilai Preferensi (V atau V_i)': v})
        df_V = pd.DataFrame(V_rows).set_index('Alternatif')
        st.markdown("**Perhitungan Nilai Preferensi (V atau V_i) - rincian per alternatif**")
        st.dataframe(df_V, use_container_width=True)
        st.subheader("7️⃣ Rata-rata Preferensi & Ranking")
        st.markdown("""
        **Penjelasan:**
        Jika alternatif muncul lebih dari sekali, maka nilai preferensinya dirata-rata.

        **Tujuan:**
        Menghasilkan satu nilai final per alternatif.
        """)
        df_rank = df_V.reset_index().groupby('Alternatif', as_index=False).agg({'Hasil Nilai Preferensi (V atau V_i)': 'mean'})
        df_rank = df_rank.sort_values(by='Hasil Nilai Preferensi (V atau V_i)', ascending=False).reset_index(drop=True)
        df_rank['Ranking'] = df_rank.index + 1
        st.markdown("**Rata-rata Preferensi & Ranking**")
        st.dataframe(df_rank, use_container_width=True)
        st.success(f"🏆 Alternatif terbaik: {df_rank.iloc[0]['Alternatif']}")
        save_db('ranking_ahp', df_rank.to_dict())
        # PERANGKINGAN (TOPSIS - FUZZY AHP)
        st.markdown("---")
        st.title("Perangkingan Metode TOPSIS (Fuzzy AHP)")
        bobot_db = load_db("bobot") or {}
        if "fuzzy" in bobot_db:
            st.session_state.bobot_fuzzy = pd.Series(bobot_db["fuzzy"])
        bobot = st.session_state.get("bobot_fuzzy")
        if bobot is None:
            st.warning("Bobot Fuzzy belum tersedia")
        else:
            alternatif = df.iloc[:, 0]
            X = df.iloc[:, 1:]
            mapping = st.session_state.get("mapping_kriteria", {})
            mapping = {k: mapping.get(k, k) for k in X.columns}
            display_map = {c: f"{c} ({mapping.get(c, c)})" for c in X.columns}
            st.subheader("1️⃣ Matriks Keputusan (Fuzzy)")
            st.markdown("""
            **Penjelasan:**
            Matriks keputusan pada metode Fuzzy TOPSIS sama seperti AHP,
            namun bobot yang digunakan berasal dari hasil Fuzzy AHP.
                        
            **Tujuan:**
            Menjadi dasar perhitungan TOPSIS berbasis fuzzy.
            """)
            df_X = pd.concat([alternatif, X], axis=1)
            df_X_display = df_X.copy()
            df_X_display.columns = ['Alternatif'] + [display_map.get(c, c) for c in X.columns]
            st.markdown("**Matriks Keputusan (dengan Alternatif)**")
            st.dataframe(df_X_display, use_container_width=True)
            st.subheader("2️⃣ Normalisasi Matriks")
            st.latex(r"r_{ij} = \frac{x_{ij}}{\sqrt{\sum x_{ij}^2}}")
            st.markdown("""
            **Penjelasan:**
            Normalisasi dilakukan untuk menyamakan skala antar kriteria.

            **Tujuan:**
            Agar semua kriteria dapat dibandingkan secara adil.
            """)
            pembagi = (X**2).sum()**0.5
            cols = X.columns
            col_labels = [display_map.get(c, c) for c in cols]
            calc_pembagi = []
            for j, c in enumerate(cols):
                vals = X[c].tolist()
                vals_str = ' + '.join([f"{v:.3f}^2" for v in vals])
                expr = f"sqrt({vals_str}) = {pembagi[c]:.6f}"
                calc_pembagi.append(expr)
            df_pembagi = pd.DataFrame({'Kriteria': col_labels, 'Perhitungan nilai pembagi akar (x_ij) kuadrat': calc_pembagi, 'Hasil Total Nilai Pembagi (x_ij)': pembagi.values}).set_index('Kriteria')
            st.markdown("**Perhitungan Pembagi Normalisasi per Kriteria:**")
            st.dataframe(df_pembagi, use_container_width=True)
            R = X / pembagi
            R_rows = []
            for i in range(R.shape[0]):
                row = {'Alternatif': alternatif.iat[i]}
                for j, c in enumerate(cols):
                    xij = X.iat[i, j]
                    denom = pembagi[c]
                    rij = R.iat[i, j]
                    row[col_labels[j]] = f"{xij:.3f} / {denom:.6f} = {rij:.6f}"
                R_rows.append(row)
            df_R_expr = pd.DataFrame(R_rows).set_index('Alternatif')
            st.markdown("**Perhitungan Matriks Normalisasi r_ij = (x_ij / pembagi):**")
            st.dataframe(df_R_expr, use_container_width=True)
            st.subheader("3️⃣ Matriks Ternormalisasi Terbobot")
            st.latex(r"y_{ij} = r_{ij} \times w_j")
            st.markdown("""
            **Keterangan:**
            - y_ij adalah nilai terbobot untuk alternatif i pada kriteria j setelah normalisasi.
            - r_ij adalah nilai normalisasi untuk alternatif i pada kriteria j.
            - w_j adalah nilai bobot fuzzy per kriteria j.
            
            **Penjelasan:**
            Mengalikan hasil normalisasi dengan bobot Fuzzy AHP.

            **Tujuan:**
            Menentukan kontribusi tiap kriteria.
            """)
            st.markdown("**Tabel yang digunakan untuk menghitung Matriks Ternormalisasi Terbobot:**")
            st.markdown("**1. Hasil Matriks Normalisasi (r_ij)**")
            df_R = pd.concat([alternatif, R], axis=1)
            df_R_display = df_R.copy()
            df_R_display.columns = ['Alternatif'] + col_labels
            st.dataframe(df_R_display, use_container_width=True)
            try:
                fuzzy_vals = []
                for c in cols:
                    try:
                        v = float(bobot.loc[c])
                    except Exception:
                        v = float(bobot.iloc[list(X.columns).index(c)])
                    fuzzy_vals.append(v)
                df_w_fuzzy = pd.DataFrame({'Kriteria': col_labels, 'Bobot Fuzzy': fuzzy_vals}).set_index('Kriteria')
            except Exception:
                df_w_fuzzy = pd.DataFrame({'Kriteria': col_labels, 'Bobot Fuzzy': [None]*len(col_labels)}).set_index('Kriteria')
            st.markdown("**2. Bobot Fuzzy (w_j)**")
            st.dataframe(df_w_fuzzy, use_container_width=True)
            weights = [float(x) for x in df_w_fuzzy.iloc[:,0].values]
            Y = R * np.array(weights)
            df_Y = pd.concat([alternatif, Y], axis=1)
            Y_rows_expr = []
            for i in range(Y.shape[0]):
                row = {'Alternatif': alternatif.iat[i]}
                for j, c in enumerate(cols):
                    rij = R.iat[i, j]
                    wj = weights[j]
                    yij = Y.iat[i, j]
                    row[col_labels[j]] = f"{rij:.6f} × {wj:.6f} = {yij:.6f}"
                Y_rows_expr.append(row)
            df_Y_expr = pd.DataFrame(Y_rows_expr).set_index('Alternatif')
            st.markdown("**Perhitungan Matriks Ternormalisasi Terbobot y_ij = (r_ij × w_j)**")
            st.dataframe(df_Y_expr, use_container_width=True)
            st.subheader("4️⃣ Solusi Ideal Positif & Negatif")
            st.latex(r"y_j^{+} = \max\left(y_{ij}\right),\quad y_j^{-} = \min\left(y_{ij}\right)")
            st.markdown("""
            **Keterangan:**
            - y_j+ = nilai maksimum untuk kriteria j
            - y_j- = nilai minimum untuk kriteria j
            - A+ = nilai maksimum (terbaik)
            - A- = nilai minimum (terburuk)
                        
            **Penjelasan:**
            Menentukan solusi ideal positif (A+) dan negatif (A-) untuk setiap kriteria.

            **Tujuan:**
            Menentukan titik referensi terbaik dan terburuk.
            """)
            df_Y = pd.concat([alternatif, Y], axis=1)
            df_Y_numeric = df_Y.copy()
            df_Y_numeric.columns = ['Alternatif'] + col_labels
            st.markdown("**Tabel yang digunakan untuk menentukan Solusi Ideal Positif (A+) dan Negatif (A-):**")
            st.markdown("**Hasil Matriks Ternormalisasi Terbobot (y_ij) - digunakan untuk menentukan Nilai (A+ & A-) atau (y_j+ dan y_j-) setiap kriteria dari seluruh alternatif**")
            st.dataframe(df_Y_numeric, use_container_width=True)
            A_plus = Y.max()
            A_minus = Y.min()
            df_Apm = pd.DataFrame({
                'Kriteria': col_labels,
                'A+ atau y_j+ (Positif)': A_plus.values,
                'A- atau y_j- (Negatif)': A_minus.values
            }).set_index('Kriteria')
            st.markdown("**Hasil Solusi Ideal Positif (A+) atau (y_j+) & Negatif (A-) atau (y_j-)**")
            st.dataframe(df_Apm, use_container_width=True)
            st.subheader("5️⃣ Jarak ke Solusi Ideal")
            st.latex(r"D_i^+ = \sqrt{\sum (y_{ij} - y_j^+)^2}")
            st.latex(r"D_i^- = \sqrt{\sum (y_{ij} - y_j^-)^2}")
            st.markdown("""
            **Keterangan:**
            - D_i+ = jarak alternatif i ke solusi ideal positif (A+)
            - D_i- = jarak alternatif i ke solusi ideal negatif (A-)
            - y_ij = nilai terbobot untuk alternatif i pada kriteria j
            - y_j+ = nilai solusi ideal positif untuk kriteria j
            - y_j- = nilai solusi ideal negatif untuk kriteria j
                        
            **Penjelasan:**
            Mengukur jarak setiap alternatif terhadap solusi ideal.

            **Tujuan:**
            Menentukan seberapa dekat alternatif dengan kondisi terbaik.
            """)
            st.markdown("**Tabel yang digunakan untuk perhitungan Jarak ke Solusi Ideal (D+ & D-):**")
            df_Y_used = pd.concat([alternatif, Y], axis=1)
            df_Y_used_disp = df_Y_used.copy()
            df_Y_used_disp.columns = ['Alternatif'] + col_labels
            st.markdown("**1.Hasil Matriks Ternormalisasi Terbobot (y_ij)**")
            st.dataframe(df_Y_used_disp, use_container_width=True)
            st.markdown("**2.Solusi Ideal (A+ & A-) atau (y_j+ & y_j-)**")
            st.dataframe(df_Apm, use_container_width=True)
            D_plus = ((Y - A_plus)**2).sum(axis=1)**0.5
            D_minus = ((Y - A_minus)**2).sum(axis=1)**0.5
            dplus_rows = []
            dminus_rows = []
            for i in range(Y.shape[0]):
                terms_p = []
                terms_m = []
                for j, c in enumerate(cols):
                    yij = Y.iat[i, j]
                    ap = A_plus.iloc[j]
                    am = A_minus.iloc[j]
                    tp = (yij - ap)**2
                    tm = (yij - am)**2
                    terms_p.append(f"({yij:.6f} - {ap:.6f})^2 = {tp:.6f}")
                    terms_m.append(f"({yij:.6f} - {am:.6f})^2 = {tm:.6f}")
                sum_p = D_plus.iat[i]
                sum_m = D_minus.iat[i]
                expr_p = ' + '.join(terms_p) + f" = {sum_p:.6f}"
                expr_m = ' + '.join(terms_m) + f" = {sum_m:.6f}"
                dplus_rows.append({'Alternatif': alternatif.iat[i], 'Perhitungan D+ ((D_i+ = akar dari jumlah kuadrat y_ij - y_j+))': expr_p, 'Hasil D+ (Jarak ke Solusi Positif)': sum_p})
                dminus_rows.append({'Alternatif': alternatif.iat[i], 'Perhitungan D- ((D_i- = akar dari jumlah kuadrat y_ij - y_j-))': expr_m, 'Hasil D- (Jarak ke Solusi Negatif)': sum_m})
            df_D_plus = pd.DataFrame(dplus_rows).set_index('Alternatif')
            df_D_minus = pd.DataFrame(dminus_rows).set_index('Alternatif')
            st.markdown("**Perhitungan Jarak ke Solusi Ideal (D+ & D-) - rincian per data alternatif**")
            st.markdown("**Hasil Perhitungan D+ jarak ke solusi positif (D_i+ = akar dari jumlah kuadrat y_ij - y_j+)**")
            st.dataframe(df_D_plus, use_container_width=True)
            st.markdown("**Hasil Perhitungan D- jarak ke solusi negatif (D_i- = akar dari jumlah kuadrat y_ij - y_j-)**")
            st.dataframe(df_D_minus, use_container_width=True)
            st.subheader("6️⃣ Nilai Preferensi")
            st.latex(r"V_i = \frac{D_i^-}{D_i^+ + D_i^-}")
            st.markdown("""
            **Keterangan:**
            - V_i = nilai preferensi untuk alternatif i
            - D_i+ = jarak alternatif i ke solusi ideal positif (A+)
            - D_i- = jarak alternatif i ke solusi ideal negatif (A-)
                        
            **Penjelasan:**
            Nilai preferensi menunjukkan kualitas alternatif.

            **Interpretasi:**
            Semakin mendekati 1 → semakin baik.
            """)
            st.markdown("**Tabel yang digunakan untuk perhitungan Nilai Preferensi (V atau V_i):**")
            V = D_minus / (D_plus + D_minus)
            df_V_numeric = pd.DataFrame({
                'Alternatif': alternatif,
                'D+': D_plus,
                'D-': D_minus,
                'V': V
            }).reset_index(drop=True).set_index('Alternatif')
            st.markdown("**Hasil Perhitungan D+ (Jarak ke Solusi Positif) dan D- (Jarak ke Solusi Negatif)**")
            st.dataframe(df_V_numeric, use_container_width=True)
            V_rows = []
            for i in range(V.shape[0]):
                d_p = D_plus.iat[i]
                d_m = D_minus.iat[i]
                v = V.iat[i]
                rincian = f"{d_m:.6f} / ({d_p:.6f} + {d_m:.6f}) = {v:.6f}"
                V_rows.append({'Alternatif': alternatif.iat[i], 'Perhitungan Nilai Preferensi V (V_i = D_i-/(D_i+ + D_i-))': rincian, 'Hasil Nilai Preferensi (V atau V_i)': v})
            df_V = pd.DataFrame(V_rows).set_index('Alternatif')
            st.markdown("**Perhitungan Nilai Preferensi (V atau V_i) - rincian per alternatif**")
            st.dataframe(df_V, use_container_width=True)
            st.subheader("7️⃣ Rata-rata Preferensi & Ranking (Fuzzy)")
            st.markdown("""
            **Penjelasan:**
            Jika alternatif muncul lebih dari sekali, maka nilai preferensi dirata-rata.

            **Tujuan:**
            Menghasilkan satu nilai akhir per alternatif.
            """)
            df_rank = df_V.reset_index().groupby('Alternatif', as_index=False).agg({'Hasil Nilai Preferensi (V atau V_i)': 'mean'})
            df_rank = df_rank.sort_values(by='Hasil Nilai Preferensi (V atau V_i)', ascending=False).reset_index(drop=True)
            df_rank['Ranking'] = df_rank.index + 1
            st.markdown("**Rata-rata Preferensi & Ranking**")
            st.dataframe(df_rank, use_container_width=True)
            st.success(f"🏆 Alternatif terbaik (Fuzzy): {df_rank.iloc[0]['Alternatif']}")
            save_db('ranking_fuzzy', df_rank.to_dict())
            st.subheader("🔧 Skenario Ujicoba Bobot")
            st.markdown("""
            **Penjelasan singkat:**

            Skenario bobot memungkinkan Anda mencoba variasi bobot tiap kriteria untuk
            mengetahui dampaknya terhadap peringkat alternatif. Contoh: naikkan bobot
            "Produktivitas" atau turunkan bobot "Harga" lalu lihat apakah rekomendasi
            varietas berubah.

            Langkah-langkah penggunaan:
            1. Pilih sumber bobot (AHP atau Fuzzy AHP).
            2. Ubah hanya kolom "Bobot" pada tabel di bawah (kolom lain bersifat read-only/tidak bisa diubah).
            3. Lihat preview ranking yang dihitung otomatis dari bobot yang Anda masukkan.
            4. Jika ingin menyimpan, isi "Nama Skenario" dan "Catatan", lalu klik "Simpan Skenario".

            """, unsafe_allow_html=True)
            metode_skenario = st.selectbox(
                "Pilih Bobot",
                ["AHP", "Fuzzy AHP"]
            )
            if metode_skenario == "AHP":
                bobot_awal = st.session_state.get("bobot_ahp")
            else:
                bobot_awal = st.session_state.get("bobot_fuzzy")
            df_pre = st.session_state.get("data_preprocessed")
            if bobot_awal is None or df_pre is None:
                st.warning("Bobot / Data belum tersedia")
                st.stop()
            st.subheader("🔧 Input / Edit Bobot Skenario")
            alternatif = df_pre.iloc[:, 0]
            X = df_pre.iloc[:, 1:]
            criteria_order = list(X.columns)
            bobot_map = {k: float(v) for k, v in zip(bobot_awal.index, bobot_awal.values)}
            df_bobot = pd.DataFrame({
                "Kriteria": criteria_order,
                "Bobot": [
                    bobot_map.get(k, 0.0)
                    for k in criteria_order
                ]
            })
            config_db = load_db("config") or {}
            list_kriteria = config_db.get(
                "kriteria",
                []
            )
            mapping_label = {}
            for i, nama in enumerate(
                list_kriteria
            ):
                mapping_label[
                    f"C{i+1}"
                ] = (
                    f"C{i+1} ({nama})"
                )
            df_bobot_display = (df_bobot.copy())
            df_bobot_display["Kriteria"] = (df_bobot_display["Kriteria"].map(lambda x:mapping_label.get(x,x)))
            config_db = load_db("config") or {}
            list_kriteria = config_db.get(
                "kriteria",
                []
            )
            mapping_label = {}
            for i, nama in enumerate(
                list_kriteria
            ):
                mapping_label[
                    f"C{i+1}"
                ] = (
                    f"C{i+1} ({nama})"
                )
            df_editor = df_bobot.copy()
            df_editor["Display"] = (
                df_editor["Kriteria"]
                .map(
                    lambda x:
                    mapping_label.get(
                        x,
                        x
                    )
                )
            )
            df_editor = (df_editor[["Display", "Bobot"]].rename(columns={"Display":"Kriteria"}).set_index("Kriteria"))
            edited = st.data_editor(
                df_editor,
                use_container_width=True,
                key="perangkingan_bobot_editor"
            )
            if isinstance(edited, dict):
                bobot_list = edited.get("Bobot")
                if bobot_list is not None:
                    edited_df = pd.DataFrame({"Kriteria": criteria_order, "Bobot": bobot_list})
                else:
                    try:
                        edited_df = pd.DataFrame(edited)
                    except Exception:
                        edited_df = df_bobot.reset_index()[["Kriteria", "Bobot"]].copy()
            elif isinstance(edited, pd.DataFrame):
                try:
                    if "Kriteria" in edited.columns:
                        edited_df = edited[["Kriteria", "Bobot"]].copy()
                    else:
                        edited_df = edited.reset_index()[["Kriteria", "Bobot"]].copy()
                except Exception:
                    edited_df = df_bobot.reset_index()[["Kriteria", "Bobot"]].copy()
            else:
                edited_df = df_bobot.reset_index()[["Kriteria", "Bobot"]].copy()
            try:
                edited_df["Bobot"] = (edited_df["Bobot"].astype(float))
            except Exception:
                edited_df = df_bobot.copy()
            bobot_raw = pd.Series(edited_df["Bobot"].values,index=criteria_order).reindex(X.columns).fillna(0.0)
            total_weights = float(bobot_raw.sum())
            display_df_bobot = pd.DataFrame({"Kriteria": [mapping_label.get(k,k) for k in bobot_raw.index],"Bobot": bobot_raw.values})
            display_df_bobot = display_df_bobot.sort_values(by="Bobot", ascending=False).reset_index(drop=True)
            display_df_bobot["Ranking"] = display_df_bobot.index + 1
            st.markdown("**Preview Bobot (ranking otomatis berdasarkan Bobot yang diinput)**")
            st.dataframe(display_df_bobot, use_container_width=True)
            st.caption(f"Total bobot (sebelum normalisasi): {total_weights:.6f}")
            st.markdown("""
            **Kenapa total bobot harus 1?**

            Proses ini mengubah nilai absolut kriteria menjadi nilai relatif (persentase). Tujuannya agar seluruh kriteria berada pada skala universal yang sama. Dengan begitu, kontribusi tiap kriteria menjadi proporsional dan siap dikalikan dengan matriks TOPSIS tanpa merusak validitas perhitungan.

            **Tentang Bypass:** centang opsi bypass jika Anda ingin menyimpan skenario
            percobaan tanpa menormalkan atau memperbaiki jumlah bobot (mis. untuk
            pengujian cepat). Penggunaan bypass sebaiknya disertai catatan alasan.
            """)
            bypass_weights = st.checkbox("Bypass validasi total bobot (izinkan simpan meskipun total lebih/ kurang dari 1)", value=False, key="bypass_bobot_total")
            total_ok = abs(total_weights - 1.0) <= 1e-6
            if not total_ok and not bypass_weights:
                st.warning(f"⚠️ Total bobot harus 1. Saat ini total = {total_weights:.6f}. Sesuaikan bobot atau centang 'Bypass' untuk mengabaikan.")
            if total_weights != 0:
                bobot_skenario = bobot_raw / total_weights
            else:
                bobot_skenario = pd.Series([1.0 / len(X.columns)] * len(X.columns), index=X.columns)
            st.subheader("📊 Perhitungan TOPSIS Skenario")
            pembagi = np.sqrt((X**2).sum(axis=0))
            R_s = X / pembagi
            Y_s = R_s * bobot_skenario.values
            A_plus_s = Y_s.max(axis=0)
            A_minus_s = Y_s.min(axis=0)
            D_plus_s = np.sqrt(((Y_s - A_plus_s)**2).sum(axis=1))
            D_minus_s = np.sqrt(((Y_s - A_minus_s)**2).sum(axis=1))
            V_s = D_minus_s / (D_plus_s + D_minus_s)
            st.subheader("📊 Hasil Ranking Skenario")
            df_skenario = pd.DataFrame({
                "Alternatif": alternatif,
                "Preferensi": V_s
            })
            df_skenario = df_skenario.groupby("Alternatif", as_index=False).mean()
            df_skenario = df_skenario.sort_values(
                by="Preferensi",
                ascending=False
            ).reset_index(drop=True)
            df_skenario["Ranking"] = df_skenario.index + 1
            df_skenario["Preferensi"] = df_skenario["Preferensi"].round(4)
            st.dataframe(df_skenario, use_container_width=True)
            st.success(f"🏆 Terbaik: {df_skenario.iloc[0]['Alternatif']}")
            st.subheader("💾 Simpan Skenario")
            skenario_db = load_db("skenario") or []
            next_number = len(skenario_db) + 1
            default_nama = f"Skenario {next_number}"
            nama_skenario = st.text_input(
                "Nama Skenario",
                value=default_nama
            )
            name_ok = bool(nama_skenario and str(nama_skenario).strip())
            if not name_ok:
                st.warning("⚠️ Nama Skenario wajib diisi.")
            catatan_skenario = st.text_area(
                "Catatan / Keterangan Skenario",
                placeholder="""
            Contoh:
            - Pertukaran bobot antara C1 dan C2
            - Menguji sensitivitas bobot tertinggi
            - Skenario perubahan minor pada kriteria tengah
            - Rotasi bobot C6-C8
            """
            )
            nama_list = [s["nama"] for s in skenario_db]
            if nama_skenario in nama_list:
                st.error("❌ Nama skenario sudah ada!")
                st.stop()
            cat_ok = bool(catatan_skenario and str(catatan_skenario).strip())
            if not cat_ok:
                st.warning("⚠️ Catatan / Keterangan Skenario wajib diisi.")
            if st.button("💾 Simpan Skenario"):
                try:
                    if not (abs(total_weights - 1.0) <= 1e-6 or ("bypass_weights" in locals() and bypass_weights)):
                        st.error("❌ Total bobot tidak sama dengan 1. Sesuaikan bobot atau centang 'Bypass validasi total bobot' untuk memaksa simpan.")
                        st.stop()
                except Exception:
                    pass
                if not name_ok:
                    st.error("❌ Nama Skenario wajib diisi.")
                    st.stop()
                if not cat_ok:
                    st.error("❌ Catatan / Keterangan Skenario wajib diisi.")
                    st.stop()
                df_save = df_skenario.copy()
                skenario_db.append({
                    "nama": nama_skenario,
                    "metode": metode_skenario,
                    "catatan": catatan_skenario,
                    "bobot_raw": bobot_raw.to_dict(),
                    "bobot": bobot_skenario.to_dict(),
                    "ranking": df_save.to_dict(orient="records")
                })
                save_db("skenario", skenario_db)
                st.success(f"✅ {nama_skenario} berhasil disimpan!")
                st.rerun()
            st.subheader("📂 Daftar Skenario")
            if skenario_db:
                for sk in skenario_db:
                    with st.expander(f"{sk['nama']} ({sk.get('metode', 'N/A')})", expanded=False):
                        if sk.get("catatan"):
                            st.info(f"📌 Catatan: {sk['catatan']}")
                        if sk.get("bobot_raw"):
                            df_raw = pd.DataFrame(sk["bobot_raw"].items(), columns=["Kriteria", "Bobot"])
                            df_raw["Kriteria"] = (df_raw["Kriteria"].apply(lambda x:mapping_label.get(x,x)))
                            try:
                                df_raw["Bobot"] = df_raw["Bobot"].astype(float)
                            except Exception:
                                pass
                        else:
                            df_raw = pd.DataFrame(sk["bobot"].items(), columns=["Kriteria", "Bobot"])
                            df_raw["Kriteria"] = (df_raw["Kriteria"].apply(lambda x:mapping_label.get(x,x)))
                        df_raw = df_raw.sort_values(by="Bobot", ascending=False).reset_index(drop=True)
                        df_raw["Ranking"] = df_raw.index + 1
                        st.write("Bobot")
                        st.dataframe(df_raw)
                        st.write("Hasil Perangkingan tersimpan:")
                        st.dataframe(pd.DataFrame(sk["ranking"]))
            else:
                st.info("Belum ada skenario")
            st.subheader("🗑️ Hapus Skenario")
            sk_names = [s["nama"] for s in skenario_db]
            to_delete = st.multiselect("Pilih skenario untuk dihapus (pilih beberapa jika perlu):", sk_names)
            if to_delete:
                if st.button("🗑️ Hapus Terpilih"):
                    new_list = [s for s in skenario_db if s["nama"] not in to_delete]
                    save_db("skenario", new_list)
                    st.success(f"✅ {len(to_delete)} skenario terhapus.")
                    st.rerun()
            st.subheader("🗑️ Hapus Semua Skenario")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Hapus Semua Skenario"):
                    st.session_state.confirm_delete = True
            with col2:
                if st.session_state.get("confirm_delete"):
                    if st.button("⚠️ Yakin Hapus Semua?"):
                        save_db("skenario", [])
                        st.session_state.confirm_delete = False
                        st.success("✅ Semua skenario berhasil dihapus!")
                        st.rerun()
            st.markdown("---")
            if st.button("➡️ Lanjut ke Evaluasi"):
                st.session_state.menu = "Evaluasi"
                st.rerun()
elif selected == "Panduan Input":
    st.title("📘 Panduan Input — Langkah demi Langkah")
    st.markdown("""
    Halaman ini memberi panduan lengkap tentang apa yang harus disiapkan saat upload data, dari format file hingga tips singkat untuk Preprocessing Data dan pembobotan.
    """, unsafe_allow_html=True)
    example_df = pd.DataFrame({"Alternatif": ["Var_A","Var_B","Var_C"],"Produktivitas": [9, 7, 5],"Harga": [1200, 1000, 1500],"Ketahanan": ["Tinggi","Sedang","Rendah"]})
    with st.expander("📥 Panduan Upload Data", expanded=False):
        st.markdown("""
        Catatan singkat: gunakan uploader demo di bawah untuk mencoba format file. Contoh uploader ini hanya untuk preview dan TIDAK mengubah data utama aplikasi.
        """, unsafe_allow_html=True)
        st.subheader("Contoh file (preview)")
        st.dataframe(example_df, use_container_width=True)
        st.markdown("---")
        st.write("Demo: Uji upload file (preview saja)")
        demo_file = st.file_uploader("Pilih file CSV/XLSX untuk preview (demo)", key="demo_uploader")
        st.caption("File harus memiliki beberapa kolom kriteria dan kolom pilihan variabel untuk Alternatif. Data ini nantinya akan dipakai untuk Pembobotan (AHP / Fuzzy-AHP) + TOPSIS dan evaluasi (Spearman & NDCG). Ini hanya preview demo.")
        if demo_file is not None:
            file_name = demo_file.name
            if not (file_name.lower().endswith('.csv') or file_name.lower().endswith('.xlsx')):
                st.error("❌ Format File Salah! Sistem hanya mendukung file dengan ekstensi .csv atau .xlsx (Excel).")
            else:
                try:
                    if file_name.lower().endswith('.csv'):
                        demo_df_uploaded = pd.read_csv(demo_file, sep=None, engine='python')
                    else:
                        demo_df_uploaded = pd.read_excel(demo_file)
                    st.success("✅ File berhasil dimuat (demo). Format dokumen valid!")
                    st.markdown("### 📊 Preview Hasil Analisis & Evaluasi (Simulasi Contoh)")
                    st.info(f"📁 Dataset aktif: {file_name}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info(f"📊 Jumlah Data: {len(demo_df_uploaded)}")
                    with col2:
                        st.info(f"📋 Jumlah Variabel: {len(demo_df_uploaded.columns)}")
                    st.subheader("📋 Tipe Data Variabel")
                    tipe_data_list = []
                    for idx, col_name in enumerate(demo_df_uploaded.columns):
                        dtype_str = str(demo_df_uploaded[col_name].dtype)
                        tipe_data_list.append({"No": idx + 1,"Variabel": col_name,"Tipe": dtype_str})
                    df_tipe_variabel = pd.DataFrame(tipe_data_list)
                    st.dataframe(df_tipe_variabel, use_container_width=True, hide_index=True)
                    st.subheader("🔍 Preview Data")
                    st.dataframe(demo_df_uploaded.head(5), use_container_width=True)
                    st.caption("Preview hanya untuk demo — file ini tidak disimpan ke database oleh uploader demo.")   
                except Exception as e:
                    st.error(f"Gagal membaca file demo: {e}")
    # Panduan PREPROCESSING DATA
    with st.expander("🛠️ Panduan Preprocessing Data", expanded=False):
        st.markdown("""
        Ringkasan Preprocessing Data (singkat): gunakan kontrol di bawah untuk menyiapkan data.
        """, unsafe_allow_html=True)
        st.markdown("""
        ### Demo Interaktif (Contoh)
        Anda dapat mencoba langkah-langkah Preprocessing Data pada contoh data berikut. Pilih fitur untuk di-drop, pilih kriteria, tentukan alternatif, lalu buat mapping sub-kriteria.
        Setelah mengatur mapping, lihat preview hasil konversi (C1..Cn) di bawah.
        """, unsafe_allow_html=True)
        demo_df = example_df.copy()
        st.write("Contoh Data Awal (editable):")
        demo_edit = st.data_editor(demo_df, use_container_width=True, num_rows="dynamic", key="demo_editor")
        st.caption("Edit tabel di sini untuk mencoba perubahan struktur. Perubahan demo tidak disimpan kecuali Anda klik 'Simpan Perubahan Data (demo)'.")
        if isinstance(demo_edit, dict):
            try:
                demo_edit = pd.DataFrame(demo_edit)
            except Exception:
                pass
        if not isinstance(demo_edit, pd.DataFrame):
            try:
                demo_edit = pd.DataFrame(demo_edit)
            except Exception:
                demo_edit = demo_df.copy()
        demo_df = demo_edit
        with st.container():
            col1, col2 = st.columns([3,2])
            with col1:
                quick_col_name = st.text_input("Nama Kolom Baru (demo)", key="demo_quick_col_name")
                st.caption("Contoh: 'Kualitas', 'KadarAir' — demo saja")
            with col2:
                quick_col_type = st.selectbox("Tipe", ["Numerik", "String"], index=0, key="demo_quick_col_type")
            if st.button("➕ Tambahkan Kolom (demo)", key="demo_add_col_btn"):
                st.info(f"Kolom '{quick_col_name}' ditambahkan ke preview (demo). Ini tidak menyimpan ke database.")
            st.caption("Tambahkan/hapus/ganti nama kolom pada preview (demo). Gunakan ini untuk mencoba format kolom sebelum menyimpan di Preprocessing Data asli.")
            cols_removable = [c for c in demo_df.columns]
            sel_remove = st.multiselect("Pilih kolom untuk dihapus dari preview (demo)", cols_removable, key="demo_sel_remove")
            if st.button("🗑️ Hapus Kolom (demo)", key="demo_remove_col_btn"):
                st.info(f"Kolom {', '.join(sel_remove)} dihapus dari preview (demo). Ini tidak menyimpan ke database.")
            rcol1, rcol2 = st.columns([3,3])
            with rcol1:
                col_to_rename = st.selectbox("Pilih kolom yang akan diganti namanya (demo)", options=list(demo_df.columns), key="demo_rename_select")
            with rcol2:
                new_col_name = st.text_input("Nama Kolom Baru (demo)", key="demo_rename_new_name")
            if st.button("🔁 Ganti Nama Kolom (demo)", key="demo_rename_btn"):
                if not col_to_rename:
                    st.error("❌ Tidak ada kolom yang dipilih")
                elif not new_col_name or str(new_col_name).strip() == "":
                    st.error("❌ Nama kolom baru tidak boleh kosong")
                elif new_col_name in demo_df.columns:
                    st.error("❌ Nama kolom baru sudah ada (duplikat)")
                else:
                    st.info(f"Kolom '{col_to_rename}' diganti menjadi '{new_col_name}' di preview (demo). Ini tidak menyimpan ke database.")
            st.caption("Ganti nama kolom di preview untuk memastikan struktur data sebelum menyimpan di Preprocessing Data utama.")
        st.markdown("""
        <div style='display:flex; gap:16px; margin-top:12px'>
            <div style='background:#e6f2ff; padding:12px; border-radius:8px; flex:1'>Jumlah Baris: <strong>{rows}</strong></div>
            <div style='background:#e6f2ff; padding:12px; border-radius:8px; flex:1'>Jumlah Kolom: <strong>{cols}</strong></div>
        </div>
        """.format(rows=len(demo_df), cols=len(demo_df.columns)), unsafe_allow_html=True)
        st.markdown("**Penjelasan (demo):** Klik tombol ini untuk mensimulasikan menyimpan perubahan pada tabel. Ini hanya demo dan tidak akan mengubah database aplikasi.")
        if st.button("💾 Simpan Perubahan Data (demo)", key="demo_save_btn"):
            st.success("✅ Simulasi simpan selesai. Untuk menyimpan nyata, gunakan halaman Preprocessing Data dan klik 'Simpan Perubahan Data'.")
        st.caption("Simpan Perubahan Data (demo) hanya simulasi. Untuk menyimpan permanen, gunakan halaman Preprocessing Data dan tombol Simpan.")
        st.markdown("---")
        auto_preview = st.checkbox("Tampilkan preview otomatis", value=True, key="demo_auto_preview")
        st.caption("Centang untuk melihat preview konversi (C1..Cn) secara otomatis saat Anda mengubah mapping sub-kriteria.")
        drop_demo = st.multiselect("Pilih kolom untuk dihapus (drop)", options=list(demo_df.columns), default=["Harga"])
        st.caption("Pilih kolom yang tidak ingin dipakai sebagai kriteria. Ini hanya mengubah preview demo.")
        cols_after = [c for c in demo_df.columns if c not in drop_demo]
        st.markdown("**Pilih Kriteria** (kolom yang akan dipakai sebagai kriteria):")
        default_k = [c for c in cols_after if c != "Alternatif"]
        sel_kriteria = st.multiselect("Kriteria:", options=[c for c in cols_after if c != "Alternatif"], default=default_k)
        st.caption("Pilih kolom yang akan dijadikan kriteria (akan dipetakan menjadi C1..Cn pada preview).")
        st.markdown("**Pilih Alternatif**")
        sel_alternatif = st.selectbox("Alternatif:", options=[c for c in cols_after if c not in sel_kriteria], index=0 if any(c not in sel_kriteria for c in cols_after) else 0)
        st.caption("Pilih kolom yang berisi label alternatif (nama/ID tiap baris).")
        st.markdown("**Atur Sub-Kriteria (Contoh singkat untuk tiap kriteria yang dipilih)**")
        mapping_demo = {}
        st.caption("Untuk tiap kriteria, pilih tipe (Numerik atau Kategorikal) dan definisikan rentang/kategori ke skor. Preview konversi akan tampil di bawah.")
        for idx, k in enumerate(sel_kriteria):
            st.markdown(f"**C{idx+1} - {k}**")
            is_produk = "produktiv" in k.lower()
            is_ket = "ketahanan" in k.lower() or "ketah" in k.lower()
            tipe_idx = 0
            if is_ket:
                tipe_idx = 1  
            tipe = st.selectbox(f"Tipe {k}", options=["Numerik (Rentang)", "Kategorikal"], index=tipe_idx, key=f"tipe_demo_{k}")
            jumlah_default = 3
            jumlah = st.number_input(f"Jumlah sub-kriteria untuk {k}", min_value=1, max_value=6, value=jumlah_default, key=f"jumlah_demo_{k}")
            opsi = []
            if tipe.startswith("Numerik"):
                preset_ranges = [{"min": 7.1, "max": 1000.0, "nilai": 9},{"min": 5.1, "max": 7.0, "nilai": 7},{"min": 0.0, "max": 5.0, "nilai": 5}]
                for i in range(int(jumlah)):
                    cols = st.columns(3)
                    if is_produk and i < len(preset_ranges):
                        pr = preset_ranges[i]
                        mn = cols[0].number_input(f"{k} - Min {i+1}", value=float(pr["min"]), key=f"{k}_min_demo_{i}")
                        mx = cols[1].number_input(f"{k} - Max {i+1}", value=float(pr["max"]), key=f"{k}_max_demo_{i}")
                        val = cols[2].number_input(f"{k} - Nilai {i+1}", value=int(pr["nilai"]), key=f"{k}_val_demo_{i}")
                    else:
                        mn = cols[0].number_input(f"{k} - Min {i+1}", value=0.0, key=f"{k}_min_demo_{i}")
                        mx = cols[1].number_input(f"{k} - Max {i+1}", value=10.0, key=f"{k}_max_demo_{i}")
                        val = cols[2].number_input(f"{k} - Nilai {i+1}", value=i+1, key=f"{k}_val_demo_{i}")
                    opsi.append({"min": float(mn), "max": float(mx), "nilai": int(val)})
            else:
                preset_kats = [{"kategori": "Tinggi", "nilai": 9},{"kategori": "Sedang", "nilai": 7},{"kategori": "Rendah", "nilai": 5}]
                for i in range(int(jumlah)):
                    cols = st.columns(2)
                    if is_ket and i < len(preset_kats):
                        pk = preset_kats[i]
                        kat = cols[0].text_input(f"{k} - Kategori {i+1}", value=pk["kategori"], key=f"{k}_kat_demo_{i}")
                        val = cols[1].number_input(f"{k} - Nilai {i+1}", value=int(pk["nilai"]), key=f"{k}_valk_demo_{i}")
                    else:
                        kat = cols[0].text_input(f"{k} - Kategori {i+1}", value=f"K{i+1}", key=f"{k}_kat_demo_{i}")
                        val = cols[1].number_input(f"{k} - Nilai {i+1}", value=i+1, key=f"{k}_valk_demo_{i}")
                    opsi.append({"kategori": kat, "nilai": int(val)})
            mapping_demo[k] = {"tipe": tipe, "opsi": opsi}
        def compute_demo_preview():
            if not sel_kriteria or sel_alternatif is None:
                return None
            df_demo_final = pd.DataFrame()
            df_demo_final["Alternatif"] = demo_df[sel_alternatif]
            for k in sel_kriteria:
                hasil = []
                for val in demo_df[k].astype(str):
                    skor = 0
                    if mapping_demo[k]["tipe"].startswith("Numerik"):
                        for o in mapping_demo[k]["opsi"]:
                            try:
                                val_float = float(str(val).replace(",","."))
                            except:
                                val_float = 0
                            if o["min"] <= val_float <= o["max"]:
                                skor = o["nilai"]
                    else:
                        for o in mapping_demo[k]["opsi"]:
                            if str(val).lower() == str(o.get("kategori","")).lower():
                                skor = o["nilai"]
                    hasil.append(skor)
                kode = f"C{list(sel_kriteria).index(k)+1}"
                df_demo_final[kode] = hasil
            return df_demo_final
        if auto_preview:
            preview = compute_demo_preview()
            if preview is not None:
                st.markdown("**Hasil Konversi (C1..Cn) - Preview**")
                st.dataframe(preview, use_container_width=True)
    # Panduan Pembobotan
    with st.expander("🔷 Panduan Pembobotan AHP", expanded=False):
        st.markdown("""
        **Demo Contoh Interaktif Matriks Perbandingan AHP**
        
        Cobalah input nilai di atas dan lihat bagian bawah terisi otomatis sebagai reciprocal.
        Perhatikan nilai CI dan CR untuk memahami konsistensi matriks.
        """)
        def compute_ci_cr_guide(mat):
            n = mat.shape[0]
            col_sum = mat.sum(axis=0)
            norm = mat / col_sum
            w = norm.mean(axis=1)
            Aw = mat.dot(w)
            lambda_i = Aw / w
            lambda_max = lambda_i.mean()
            CI = (lambda_max - n) / (n - 1)
            RI = {1:0.0, 2:0.0, 3:0.52, 4:0.89, 5:1.11, 6:1.25, 7:1.35, 8:1.40, 9:1.45, 10:1.49}
            CR = CI / RI.get(n, 1.49)
            return CI, CR, w
        def find_worst_inconsistency(m):
            arr = np.array(m, dtype=float)
            n = arr.shape[0]
            best = None
            best_err = -1.0
            for i in range(n):
                for j in range(n):
                    for k in range(n):
                        if i != j and j != k and i != k:
                            aij = arr[i,j]
                            ajk = arr[j,k]
                            aik = arr[i,k]
                            if aij > 0 and ajk > 0 and aik > 0:
                                pred = aij * ajk
                                err = abs(pred - aik) / max(aik, 1e-9)
                                if err > best_err:
                                    best_err = err
                                    best = (i,j,k,aij,ajk,aik,err)
            return best
        A_consistent = pd.DataFrame([[1.0, 0.3333, 2.0],[3.0, 1.0,    3.0],[0.5, 0.3333, 1.0]],columns=["C1","C2","C3"],index=["C1","C2","C3"])
        A_inconsistent = pd.DataFrame([[1.0, 9.0, 7.0],[1.0/9.0, 1.0, 8.0],[1.0/7.0, 1.0/8.0, 1.0]],columns=["C1","C2","C3"],index=["C1","C2","C3"])
        pilihan = st.selectbox("📋 Pilih Contoh Matriks:",["Contoh Konsisten", "Contoh Tidak Konsisten"],index=0,key="panduan_example_select")
        st.caption("Pilih contoh untuk memuat matriks. Anda dapat mengubah nilai di bagian atas diagonal.")
        if pilihan == "Contoh Konsisten":
            default_matrix = A_consistent.copy()
        else:
            default_matrix = A_inconsistent.copy()
        if 'panduan_matrix' not in st.session_state:
            st.session_state.panduan_matrix = default_matrix.copy()
        if pilihan == "Contoh Konsisten" and not st.session_state.panduan_matrix.equals(A_consistent):
            st.session_state.panduan_matrix = A_consistent.copy()
        elif pilihan == "Contoh Tidak Konsisten" and not st.session_state.panduan_matrix.equals(A_inconsistent):
            st.session_state.panduan_matrix = A_inconsistent.copy()
        st.markdown("""
        <style>
        div[data-testid="stNumberInput"] input {
            text-align: center;
            font-size: 0.85rem;
            padding: 4px 2px;
        }
        div[data-testid="stNumberInput"] {
            margin: 0px !important;
            padding: 0px !important;
        }
        div[data-testid="column"] {
            padding: 2px 3px !important;
        }
        .header-cell {
            background-color: #f0f2f6;
            border-radius: 6px;
            padding: 6px 4px;
            text-align: center;
            font-weight: 600;
            font-size: 0.78rem;
            color: #1f2937;
            min-height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            word-break: break-word;
            line-height: 1.2;
        }
        .row-label {
            background-color: #f0f2f6;
            border-radius: 6px;
            padding: 6px 6px;
            font-weight: 600;
            font-size: 0.78rem;
            color: #1f2937;
            min-height: 48px;
            display: flex;
            align-items: center;
            word-break: break-word;
            line-height: 1.2;
        }
        .diag-cell {
            text-align: center;
            padding-top: 10px;
            color: #6b7280;
            font-weight: bold;
            font-size: 1rem;
        }
        .recip-cell {
            text-align: center;
            padding-top: 10px;
            color: #c0392b;
            font-style: italic;
            font-size: 0.85rem;
            font-weight: 500;
        }
        </style>
        """, unsafe_allow_html=True)
        st.markdown("**📊 Matriks Perbandingan Berpasangan AHP**")
        st.caption("Isi hanya bagian atas diagonal (di atas garis diagonal). Bagian bawah akan terisi otomatis sebagai reciprocal (1/nilai).")
        kriteria_guide = ["C1 (Kriteria 1)", "C2 (Kriteria 2)", "C3 (Kriteria 3)"]
        n_guide = len(kriteria_guide)
        matrix_guide = pd.DataFrame(1.0, index=kriteria_guide, columns=kriteria_guide)
        prev_matrix_guide = st.session_state.panduan_matrix.copy()
        col_widths = [2] + [1]*n_guide
        header_cols = st.columns(col_widths)
        header_cols[0].markdown("<div class='header-cell'>Kriteria</div>", unsafe_allow_html=True)
        for j in range(n_guide):
            header_cols[j+1].markdown(f"<div class='header-cell'>{kriteria_guide[j]}</div>", unsafe_allow_html=True)
        for i in range(n_guide):
            row_cols = st.columns(col_widths)
            row_cols[0].markdown(f"<div class='row-label'>{kriteria_guide[i]}</div>", unsafe_allow_html=True)
            for j in range(n_guide):
                if i < j:
                    prev_val = float(prev_matrix_guide.iloc[i, j])
                    val = row_cols[j+1].number_input(label=f"{kriteria_guide[i]} vs {kriteria_guide[j]}",min_value=0.111,max_value=9.0,value=prev_val,step=0.5,format="%.3f",key=f"panduan_ahp_{i}_{j}",label_visibility="collapsed")
                    matrix_guide.iloc[i, j] = val
                    matrix_guide.iloc[j, i] = round(1.0 / val, 4)
                elif i == j:
                    row_cols[j+1].markdown("<div class='diag-cell'>1</div>", unsafe_allow_html=True)
                else:
                    recip = matrix_guide.iloc[i, j]
                    row_cols[j+1].markdown(f"<div class='recip-cell'>{round(recip, 3)}</div>", unsafe_allow_html=True)
        st.session_state.panduan_matrix = matrix_guide.copy()
        st.markdown("---")
        try:
            CI_val, CR_val, w_val = compute_ci_cr_guide(matrix_guide.fillna(1.0))
        except Exception:
            CI_val, CR_val, w_val = None, None, None
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("CI (Consistency Index)", f"{CI_val:.6f}" if CI_val is not None else "N/A")
        with col2:
            st.metric("CR (Consistency Ratio)", f"{CR_val:.6f}" if CR_val is not None else "N/A")
        with col3:
            if CR_val is not None:
                if CR_val <= 0.1:
                    status = "✅ Konsisten"
                else:
                    status = "⚠️ Tidak Konsisten"
                st.metric("Status", status)
        st.markdown("**📋 Interpretasi Hasil:**")
        if CR_val is not None:
            if CR_val <= 0.1:
                st.success("""
                ✅ **Matriks Konsisten**
                
                CR ≤ 0.1 menunjukkan penilaian Anda konsisten dan dapat dipercaya.
                Nilai bobot yang dihasilkan valid untuk digunakan dalam pengambilan keputusan.
                """)
            else:
                st.warning("""
                ⚠️ **Matriks Tidak Konsisten**
                
                CR > 0.1 menunjukkan ada inkonsistensi dalam penilaian Anda.
                Ini kemungkinan terjadi ketika penilaian berpasangan saling bertentangan.
                """)
                worst = find_worst_inconsistency(matrix_guide.fillna(1.0))
                if worst is not None:
                    i, j, k, aij, ajk, aik, err = worst
                    st.info(f"""
                    **🔍 Penyebab Inkonsistensi Terdeteksi:**
                    
                    Perbandingan **{kriteria_guide[i]} vs {kriteria_guide[j]}** = {aij:.3f}
                    Perbandingan **{kriteria_guide[j]} vs {kriteria_guide[k]}** = {ajk:.3f}
                    
                    Secara logika, seharusnya **{kriteria_guide[i]} vs {kriteria_guide[k]}** ≈ {aij:.3f} × {ajk:.3f} = **{aij*ajk:.3f}**
                    
                    Namun nilai yang Anda masukkan adalah **{aik:.3f}**, terjadi selisih **{err:.1%}**.
                    
                    **💡 Saran Perbaikan:**
                    Coba ubah salah satu dari tiga nilai di atas agar lebih konsisten.
                    """)
        bypass_panduan = st.checkbox(
            "Bypass Konsistensi (izinkan simpan meskipun CR > 0.1)", value=False, key="bypass_consistency_panduan")
        st.caption("Gunakan bypass jika Anda yakin dengan penilaian Anda meskipun tidak konsisten sempurna.")
        if bypass_panduan:
            st.warning("⚠️ Bypass aktif: Anda dapat menyimpan meskipun matriks tidak konsisten.")
        st.markdown("")
        if st.button("💾 Simpan Bobot AHP & Fuzzy (Demo)", key="panduan_save_bobot"):
            blocked = False
            if CR_val is not None and float(CR_val) > 0.1 and not bypass_panduan:
                st.error("❌ Matriks tidak konsisten (CR > 0.1). Perbaiki matriks atau aktifkan bypass untuk melanjutkan.")
                blocked = True
            if not blocked:
                st.session_state['_panduan_demo_saved'] = {
                    'matrix': matrix_guide.fillna(1.0).to_dict(),
                    'bobot': w_val.tolist() if hasattr(w_val, 'tolist') else list(w_val) if w_val is not None else None,
                    'CI': float(CI_val) if CI_val is not None else None,
                    'CR': float(CR_val) if CR_val is not None else None,
                    'bypass': bypass_panduan
                }
                st.success("✅ Demo: Bobot berhasil disimpan (ini hanya untuk pembelajaran).")
        st.markdown("""
        **📚 Tips Menggunakan Panduan:**
        
        1. **Isi Hanya Bagian Atas** - Masukkan nilai perbandingan hanya di atas diagonal utama
        2. **Gunakan Skala Saaty** - Gunakan angka 1-9 sesuai tingkat kepentingan:
        - 1 = Sama penting
        - 3 = Sedikit lebih penting
        - 5 = Lebih penting
        - 7 = Sangat lebih penting
        - 9 = Mutlak lebih penting
        3. **Target CR ≤ 0.1** - Untuk hasil yang dapat dipercaya, konsistensi harus terjaga
        4. **Eksperimen** - Coba mengubah nilai untuk melihat bagaimana pengaruhnya terhadap CI dan CR
        
        Setelah memahami konsep dari panduan ini, lanjutkan ke halaman **Pembobotan** untuk melakukan analisis dengan data Anda sendiri.
        """)
    # 📈 PANDUAN PERANGKINGAN
    with st.expander("📈 Panduan Perangkingan", expanded=False):
        st.markdown("""
        Demo Perangkingan (TOPSIS) — ubah bobot pada tabel di bawah.
        Pilih metode AHP atau Fuzzy AHP.
        """)
        st.subheader("Demo: Uji Bobot & TOPSIS")
        st.caption("""
        Demo ini tidak mengubah halaman Perangkingan utama.
        Semua perubahan hanya untuk percobaan lokal dan tidak disimpan ke database.
        """)
        demo_metode = st.selectbox("(Demo) Pilih Metode",["AHP", "Fuzzy AHP"],index=0,key="demo2_metode")
        demo_df = pd.DataFrame({"Alternatif": ["Var_A","Var_B","Var_C","Var_D"],"C1 (UmurTanaman)": [9, 7, 5, 6],"C2 (Kerebahan)": [8, 6, 7, 5],"C3 (TeksturNasi)": [7, 9, 6, 8],"C4 (PotensiHasil)": [6, 5, 8, 7]})
        st.markdown("### Penjelasan")
        st.write("""
        Ubah nilai bobot pada tabel berikut.
        Sistem akan otomatis menghitung ulang nilai TOPSIS dan ranking alternatif.
        """)
        cols_demo = [c for c in demo_df.columns if c != "Alternatif"]
        default_demo_bobot = pd.Series([1 / len(cols_demo)] * len(cols_demo),index=cols_demo)
        df_demo_bobot = pd.DataFrame({"Kriteria": cols_demo,"Bobot": [float(b) for b in default_demo_bobot.values]})
        edited_demo = st.data_editor(df_demo_bobot,use_container_width=True,key="demo2_bobot_editor",hide_index=True)
        if isinstance(edited_demo, dict):
            try:
                edited_demo = pd.DataFrame(edited_demo)
            except Exception:
                edited_demo = df_demo_bobot.copy()
        try:
            edited_demo["Bobot"] = edited_demo["Bobot"].astype(float)
        except Exception:
            pass
        try:
            bobot_demo = pd.Series(edited_demo["Bobot"].values,index=edited_demo["Kriteria"]).reindex(cols_demo).fillna(0.0)
        except Exception:
            bobot_demo = pd.Series([1 / len(cols_demo)] * len(cols_demo),index=cols_demo)
        if bobot_demo.sum() != 0:
            bobot_demo = bobot_demo / bobot_demo.sum()
        st.markdown("### Preview Tabel Bobot Baru")
        preview_bobot = edited_demo.copy()
        preview_bobot["Bobot"] = pd.to_numeric(preview_bobot["Bobot"],errors="coerce").fillna(0)
        preview_bobot["Ranking"] = (preview_bobot["Bobot"].rank(method="dense",ascending=False).astype(int))
        preview_bobot = preview_bobot.sort_values(by=["Ranking", "Kriteria"])
        st.dataframe(preview_bobot,use_container_width=True,hide_index=True)
        st.caption("""
        Preview bobot terbaru sesuai input pengguna.
        Ranking menunjukkan prioritas kriteria
        berdasarkan besar bobot yang diinput.
        """)
        alternatif_demo = demo_df.iloc[:, 0]
        X_demo = demo_df.iloc[:, 1:]
        pembagi = np.sqrt((X_demo ** 2).sum(axis=0))
        R_demo = X_demo / pembagi
        Y_demo = R_demo * bobot_demo.values
        A_plus = Y_demo.max(axis=0)
        A_minus = Y_demo.min(axis=0)
        D_plus = np.sqrt(((Y_demo - A_plus) ** 2).sum(axis=1))
        D_minus = np.sqrt(((Y_demo - A_minus) ** 2).sum(axis=1))
        V_demo = D_minus / (D_plus + D_minus)
        df_demo_result = pd.DataFrame({"Alternatif": alternatif_demo,"Preferensi": V_demo})
        df_demo_result = (df_demo_result.sort_values(by="Preferensi",ascending=False).reset_index(drop=True))
        df_demo_result["Ranking"] = (df_demo_result.index + 1)
        st.markdown("### Hasil TOPSIS")
        st.dataframe(df_demo_result,use_container_width=True,hide_index=True)
        st.caption("""
        Hasil TOPSIS akan otomatis berubah
        ketika bobot pada tabel diubah.
        """)
        total_bobot = float(edited_demo["Bobot"].sum())
        st.caption(f"Total bobot (sebelum normalisasi): "f"{total_bobot:.6f}")
        valid_total = abs(total_bobot - 1.0) < 0.0001
        with st.container():
            st.markdown("### Kenapa total bobot harus 1?")
            st.write("""
            Proses ini mengubah nilai absolut kriteria menjadi
            nilai relatif (persentase). Tujuannya agar seluruh
            kriteria berada pada skala universal yang sama.

            Dengan begitu, kontribusi tiap kriteria menjadi
            proporsional dan siap dikalikan dengan matriks
            TOPSIS tanpa merusak validitas perhitungan.
            """)
            st.write("""
            **Tentang Bypass:** centang opsi bypass jika ingin
            menyimpan skenario percobaan tanpa memperbaiki
            total bobot (misalnya untuk pengujian cepat).
            Sebaiknya disertai alasan pada catatan.
            """)
        bypass_validasi = st.checkbox(
            "Bypass validasi total bobot "
            "(izinkan simpan meskipun total "
            "lebih/kurang dari 1)",
            key="demo2_bypass"
        )
        if not valid_total:
            if bypass_validasi:
                st.warning(
                    f"""
                    ⚠️ Total bobot saat ini = {total_bobot:.6f}
                    Sistem tetap mengizinkan penyimpanan
                    karena bypass aktif.
                    """
                )
            else:
                st.error(
                    f"""
                    ❌ Total bobot harus = 1
                    Saat ini total bobot = {total_bobot:.6f}
                    Silakan perbaiki bobot atau aktifkan bypass.
                    """
                )
        else:
            st.success(
                "✅ Total bobot valid (= 1)"
            )
        st.subheader("Simpan Skenario Demo")
        demo_nama = st.text_input("Nama Skenario *",value="",placeholder="Contoh: Skenario Uji Bobot",key="demo2_nama")
        demo_catatan = st.text_area("Catatan Skenario *",value="",placeholder="Tuliskan tujuan/alasan skenario...",key="demo2_catatan")
        if st.button("💾 Simpan Skenario (Demo)",key="demo2_save"):
            error_validasi = []
            if not demo_nama.strip():
                error_validasi.append("Nama skenario wajib diisi.")
            if not demo_catatan.strip():
                error_validasi.append("Catatan skenario wajib diisi.")
            if not valid_total and not bypass_validasi:
                error_validasi.append(
                    "Total bobot harus = 1 " "atau aktifkan bypass.")
            if (
                bypass_validasi
                and not demo_catatan.strip()
            ):
                error_validasi.append("Catatan wajib diisi saat bypass aktif.")
            if error_validasi:
                for err in error_validasi:
                    st.error(err)
            else:
                st.session_state["_panduan_perangkingan_demo"] = {"nama": demo_nama,"metode": demo_metode,"catatan": demo_catatan,"bypass": bypass_validasi,"total_bobot": total_bobot,"bobot": bobot_demo.to_dict(),"ranking": df_demo_result.to_dict(orient="records")}
                notif_placeholder = st.empty()
                if bypass_validasi and not valid_total:
                    notif_placeholder.success("✅ Skenario berhasil " "disimpan menggunakan bypass.")
                else:
                    notif_placeholder.success("✅ Skenario berhasil disimpan.")
                time.sleep(3)
                notif_placeholder.empty()
                st.rerun()
        st.subheader("📂 Contoh Skenario Pengujian")
        contoh_sken = [{"nama":"Skenario 1 (Baseline) (AHP)","catatan":"Menggunakan bobot seimbang.","bobot": {"C1 (UmurTanaman)": 0.25,"C2 (Kerebahan)": 0.25,"C3 (TeksturNasi)": 0.25,"C4 (PotensiHasil)": 0.25}},{"nama":"Skenario 2 (Produktivitas Tinggi) (AHP)","catatan":"Meningkatkan bobot C1.","bobot": {"C1 (UmurTanaman)": 0.5, "C2 (Kerebahan)": 0.2, "C3 (TeksturNasi)": 0.2, "C4 (PotensiHasil)": 0.1}}]
        for s in contoh_sken:
            st.markdown(f"## 📌 {s['nama']}")
            st.info(f"📌 Catatan: {s['catatan']}")
            st.markdown("### Bobot")
            df_bobot = pd.DataFrame({"Kriteria":list(s["bobot"].keys()),"Bobot":list(s["bobot"].values())})
            df_bobot["Ranking"] = (df_bobot["Bobot"].rank(method="dense",ascending=False).astype(int))
            df_bobot = df_bobot.sort_values(by="Ranking")
            st.dataframe(df_bobot,hide_index=True)
            bobot_sken = pd.Series(s["bobot"])
            pembagi = np.sqrt((X_demo ** 2).sum(axis=0))
            R_demo = X_demo / pembagi
            Y_demo = (R_demo * bobot_sken.values)
            A_plus = Y_demo.max(axis=0)
            A_minus = Y_demo.min(axis=0)
            D_plus = np.sqrt(((Y_demo - A_plus) ** 2).sum(axis=1))
            D_minus = np.sqrt(((Y_demo - A_minus) ** 2).sum(axis=1))
            V_demo = (D_minus / (D_plus + D_minus))
            hasil_skenario = pd.DataFrame({"Alternatif":alternatif_demo,"Preferensi":V_demo})
            hasil_skenario = (hasil_skenario.sort_values(by="Preferensi",ascending=False).reset_index(drop=True))
            hasil_skenario["Ranking"] = (hasil_skenario.index + 1)
            st.markdown("### Ranking Alternatif")
            st.dataframe(hasil_skenario,hide_index=True)
        st.markdown("---")
        st.header("🗑️ Hapus Skenario")
        st.caption("""
        Kelola dan hapus skenario percobaan yang
        sudah dibuat pada panduan perangkingan.
        Gunakan fitur ini untuk membersihkan data
        uji coba yang tidak diperlukan.
        """)
        list_skenario = []
        for k, v in st.session_state.items():
            if (
                k.startswith(
                    "_panduan_perangkingan_demo"
                )
                and isinstance(v, dict)
            ):
                nama_sken = v.get(
                    "nama",
                    "Tanpa Nama"
                )
                list_skenario.append(
                    nama_sken
                )
        st.markdown("### 🗑️ Hapus Skenario")
        st.write("""
        Pilih skenario untuk dihapus
        (pilih beberapa jika perlu):
        """)
        opsi_skenario = (
            list_skenario
            if list_skenario
            else ["Skenario Demo 1","Skenario Demo 2"])
        selected_skenario = st.multiselect("Choose an option",options=opsi_skenario,key="hapus_skenario_demo")
        if st.button("🗑️ Hapus Skenario Terpilih",key="hapus_selected_demo"):
            if not selected_skenario:
                st.warning("Pilih skenario yang ingin dihapus.")
            else:
                deleted = 0
                for k in list(
                    st.session_state.keys()
                ):
                    if (
                        k.startswith(
                            "_panduan_perangkingan_demo"
                        )
                    ):
                        data = st.session_state.get(
                            k, {}
                        )
                        if (
                            data.get("nama")
                            in selected_skenario
                        ):
                            st.session_state.pop(
                                k,
                                None
                            )
                            deleted += 1
                st.success(f"✅ skenario "f"berhasil dihapus.")
                time.sleep(2)
                st.rerun()
        st.markdown("### 🗑️ Hapus Semua Skenario")
        st.caption("""
        Menghapus seluruh skenario demo
        yang tersimpan pada sesi ini.
        """)
        if st.button(
            "🗑️ Hapus Semua Skenario",
            key="demo_clear_all_sken"
        ):
            for k in list(
                st.session_state.keys()
            ):
                if (
                    k.startswith(
                        "_panduan_"
                    )
                    or
                    k.startswith(
                        "demo2_"
                    )
                ):
                    st.session_state.pop(
                        k,
                        None
                    )
            notif_hapus = st.empty()
            notif_hapus.success("✅ Semua skenario demo " "berhasil dihapus.")
            time.sleep(3)
            notif_hapus.empty()
            st.rerun()
    # Panduan Evaluasi (Demo)
    with st.expander("🔎 Panduan Evaluasi (Demo)", expanded=False):
        st.markdown(
            "Demo Evaluasi: masukkan ranking pakar contoh (editable) dan pilih Top-K untuk NDCG. "
            "Tabel di bawah menampilkan metrik (Spearman & NDCG) untuk beberapa skenario demo. "
            "Semua input dan hasil bersifat demo dan tidak disimpan ke database."
        )
        alternatif_demo = ["Var_A", "Var_B", "Var_C", "Var_D"]
        df_pakar_demo = pd.DataFrame({"Alternatif": alternatif_demo,"Rank Pakar": range(1, len(alternatif_demo) + 1)})
        st.markdown("**Input Ranking Pakar (demo)**")
        st.caption("Masukkan peringkat pakar: angka unik 1..N (1 = terbaik).")
        df_pakar_demo = st.data_editor(df_pakar_demo, key="demo_pakar_rank", use_container_width=True)
        valid_pakar = True
        try:
            if df_pakar_demo["Rank Pakar"].duplicated().any():
                st.error("❌ Ranking pakar tidak boleh duplikat (demo).")
                valid_pakar = False
            if set(df_pakar_demo["Rank Pakar"]) != set(range(1, len(alternatif_demo) + 1)):
                st.error("❌ Ranking pakar harus berisi angka 1..N (demo).")
                valid_pakar = False
        except Exception:
            valid_pakar = False
        k_demo = st.number_input("Hitung NDCG Top-K (demo)", min_value=1, max_value=len(alternatif_demo), value=min(3, len(alternatif_demo)), key="demo_ndcg_k")
        st.caption("Top-K: gunakan untuk menghitung NDCG@K (semakin kecil K, fokus pada puncak peringkat).")
        demo_scenarios = [
            {"Nama Skenario": "Skenario A (Seimbang)", "Metode": "AHP-TOPSIS", "pred_rank": ["Var_A", "Var_B", "Var_C", "Var_D"], "Catatan": "Bobot kriteria seimbang"},
            {"Nama Skenario": "Skenario B (C1 Tinggi)", "Metode": "AHP-TOPSIS", "pred_rank": ["Var_A", "Var_C", "Var_B", "Var_D"], "Catatan": "C1 diberi bobot dominan"},
            {"Nama Skenario": "Skenario C (C3 Unggul)", "Metode": "Fuzzy-AHP TOPSIS", "pred_rank": ["Var_C", "Var_D", "Var_A", "Var_B"], "Catatan": "C3 menjadi penentu utama"},
        ]
        if valid_pakar:
            pakar_rank_map = dict(zip(df_pakar_demo["Alternatif"], df_pakar_demo["Rank Pakar"]))
            results = []
            n = len(alternatif_demo)
            for s in demo_scenarios:
                pred = s["pred_rank"]
                pred_rank_map = {alt: i + 1 for i, alt in enumerate(pred)}
                d2_sum = 0
                for alt in alternatif_demo:
                    d = pred_rank_map.get(alt, n) - pakar_rank_map.get(alt, n)
                    d2_sum += d * d
                rho = 1 - (6 * d2_sum) / (n * (n * n - 1)) if n > 1 else 0
                top_k = int(min(k_demo, n))
                dcg = 0.0
                rels = []
                for pos, alt in enumerate(pred[:top_k], start=1):
                    rel = 1.0 / pakar_rank_map.get(alt, n)
                    dcg += rel / np.log2(pos + 1)
                    rels.append(rel)
                idcg = 0.0
                ideal_rels = sorted([1.0 / pakar_rank_map[a] for a in alternatif_demo], reverse=True)[:top_k]
                for pos, rel in enumerate(ideal_rels, start=1):
                    idcg += rel / np.log2(pos + 1)
                ndcg_val = dcg / idcg if idcg != 0 else 0.0
                results.append({"Nama Skenario": s["Nama Skenario"],"Metode": s["Metode"],"Catatan": s["Catatan"],"Spearman": round(float(rho), 4),"NDCG": round(float(ndcg_val), 4)})
            df_results = pd.DataFrame(results)
            st.markdown("**Hasil Evaluasi (demo)**")
            st.caption("Metode: 'AHP-TOPSIS' = bobot AHP + perankingan TOPSIS; 'Fuzzy-AHP TOPSIS' = bobot fuzzy-AHP + TOPSIS.")
            st.dataframe(df_results, use_container_width=True)
            st.caption("Contoh: kolom 'Metode' menunjukkan metode yang diuji pada tiap skenario; tabel ini hanya demo — gunakan halaman Evaluasi untuk perhitungan nyata.")
        else:
            st.info("Lengkapi input 'Ranking Pakar' (demo) dengan angka 1..N tanpa duplikat agar metrik dapat dihitung.")
elif selected == "Evaluasi":
    st.title("Evaluasi Skenario (Spearman Rank Correlation & NDCG)")
    skenario_list = load_db("skenario") or []
    if not skenario_list:
        st.warning("Belum ada skenario yang disimpan")
        st.stop()
    # INPUT RANK PAKAR
    st.subheader("1️⃣ Input Ranking Pakar")
    st.markdown("""
    **Langkah Penggunaan (singkat):**

    1. Pastikan kolom `Alternatif` berisi label unik untuk tiap alternatif.
    2. Isi kolom `Rank Pakar` dengan urutan 1..N (1 = terbaik) tanpa duplikasi.
    3. Setelah valid, sistem akan menghitung Spearman dan NDCG untuk tiap skenario.

    **Aturan :** nilai harus unik dan lengkap Rank 1..N.
    """)
    df = st.session_state.get("data_preprocessed")
    alternatif = df["Alternatif"].drop_duplicates().reset_index(drop=True)
    df_pakar = pd.DataFrame({"Alternatif": alternatif,"Rank Pakar": range(1, len(alternatif)+1)})
    df_pakar_indexed = df_pakar.set_index("Alternatif")
    try:
        col_cfg = {"Alternatif": st.column_config.TextColumn("Alternatif", disabled=True)}
        edited = st.data_editor(df_pakar_indexed,use_container_width=True,key="pakar_rank",column_config=col_cfg)
    except Exception:
        st.caption("Kolom 'Alternatif' dikunci (read-only). Jika Anda melihatnya bisa diedit, sistem akan mengembalikan nilai asli pada saat menyimpan.")
        edited = st.data_editor(df_pakar_indexed,use_container_width=True,key="pakar_rank")
    if isinstance(edited, dict):
        try:
            edited_df = pd.DataFrame(edited).reset_index()
            if 'Alternatif' not in edited_df.columns:
                edited_df.columns = list(df_pakar_indexed.reset_index().columns)
        except Exception:
            edited_df = df_pakar_indexed.reset_index()
    elif isinstance(edited, pd.DataFrame):
        try:
            edited_df = edited.reset_index()
        except Exception:
            edited_df = df_pakar_indexed.reset_index()
    else:
        edited_df = df_pakar_indexed.reset_index()
    df_pakar = edited_df[["Alternatif", "Rank Pakar"]].copy()
    try:
        df_pakar["Alternatif"] = alternatif.values
    except Exception:
        df_pakar["Alternatif"] = alternatif.reset_index(drop=True)
    # VALIDASI
    if df_pakar["Rank Pakar"].duplicated().any():
        st.error("❌ Ranking tidak boleh ada yang sama!")
        st.stop()
    if set(df_pakar["Rank Pakar"]) != set(range(1, len(alternatif)+1)):
        st.error("❌ Ranking harus berisi angka 1 sampai N tanpa ada yang hilang!")
        st.stop()
    st.success("✅ Ranking pakar valid")
    st.session_state.rank_pakar = df_pakar.copy()
    st.subheader("2️⃣ Pengaturan NDCG")
    k = st.number_input("Hitung NDCG Top-K",min_value=1,max_value=len(alternatif),value=min(3, len(alternatif)))
    st.markdown(""" **Penjelasan singkat NDCG@K:**

    NDCG (Normalized Discounted Cumulative Gain) adalah metrik evaluasi
    untuk mengukur kualitas urutan (ranking) hasil sistem terhadap urutan
    referensi (pakar). NDCG@K menghitung seberapa baik daftar rekomendasi
    di bagian Top-K dibandingkan dengan urutan ideal.

    - DCG memberi bobot lebih besar pada item yang muncul di posisi atas.
    - NDCG menormalisasi DCG agar bernilai antara 0 dan 1 (1 = sempurna).

    Pilih K sesuai kebutuhan: jika pengguna hanya melihat 3 rekomendasi teratas,
    gunakan K=3. Untuk evaluasi umum, K=5 atau K=10. """, unsafe_allow_html=True)
    st.header("🔍 Detail Perhitungan per Skenario")
    sk_names = [s.get("nama", f"Skenario {i+1}") for i, s in enumerate(skenario_list)]
    sel_idx = st.selectbox("Pilih Skenario untuk dilihat detailnya:", options=sk_names, index=0, key="detail_skenario_select")
    sel_skenario = None
    for s in skenario_list:
        if s.get("nama") == sel_idx:
            sel_skenario = s
            break
    if sel_skenario is None:
        sel_skenario = skenario_list[0]
    st.markdown(f"**Menampilkan detail untuk:** {sel_skenario.get('nama','-')} ({sel_skenario.get('metode','-')})")
    df_rank = pd.DataFrame(sel_skenario.get("ranking", [])).copy()
    df_merge = df_rank.merge(df_pakar, on="Alternatif", how="inner")
    st.subheader("3️⃣ Tabel Perbandingan Ranking")
    st.markdown(""" **Penjelasan:**
    Tabel ini membandingkan hasil peringkat dari **Sistem** dengan peringkat asli dari **Pakar**. 
    Kami menghitung selisih peringkat untuk menguji keakuratan sistem.
                
    *   **Rank Sistem**: Urutan alternatif terbaik berdasarkan hasil perhitungan aplikasi/algoritma.
    *   **Rank Pakar**: Urutan alternatif terbaik menurut penilaian langsung dari ahlinya.
    *   **d (Selisih)**: Jarak/selisih antara peringkat sistem dan peringkat pakar. **Semakin mendekati 0, semakin akurat.**
    *   **d² (Kuadrat)**: Nilai selisih yang dikuadratkan (digunakan untuk rumus pencarian total error/Korelasi Spearman). """)
    df_detail = df_merge[["Alternatif", "Ranking", "Rank Pakar"]].copy()
    df_detail = df_detail.rename(columns={"Ranking": "Rank Sistem", "Rank Pakar": "Rank Pakar"})
    d_numeric = df_detail["Rank Sistem"] - df_detail["Rank Pakar"]
    d2_numeric = d_numeric**2
    df_detail["d (Selisih)"] = df_detail.apply(lambda r: f"{r['Rank Sistem']:.0f} - {r['Rank Pakar']:.0f} = {(r['Rank Sistem'] - r['Rank Pakar']):.0f}", axis=1)
    df_detail["d² (Kuadrat)"] = df_detail.apply(lambda r: f"({(r['Rank Sistem'] - r['Rank Pakar']):.0f})² = {((r['Rank Sistem'] - r['Rank Pakar'])**2):.0f}", axis=1)
    st.dataframe(df_detail, use_container_width=True)
    st.subheader("4️⃣ Spearman Rank Correlation - Langkah Perhitungan")
    df_detail = df_merge.copy()
    df_detail = df_detail.rename(columns={"Ranking": "Rank Sistem","Rank Pakar": "Rank Pakar"})
    df_detail["d_numeric"] = df_detail["Rank Sistem"] - df_detail["Rank Pakar"]
    df_detail["d2_numeric"] = df_detail["d_numeric"]**2
    df_detail["d (Selisih)"] = df_detail.apply(lambda r: f"{r['Rank Sistem']:.0f} - {r['Rank Pakar']:.0f} = {r['d_numeric']:.0f}", axis=1)
    df_detail["d² (Kuadrat Selisih)"] = df_detail.apply(lambda r: f"({r['d_numeric']:.0f})² = {r['d2_numeric']:.0f}", axis=1)
    st.markdown("**Tabel Perbandingan & Selisih Peringkat**")
    st.dataframe(df_detail[["Alternatif", "Rank Sistem", "Rank Pakar", "d (Selisih)", "d² (Kuadrat Selisih)"]], use_container_width=True)
    n = len(df_detail)
    if n > 1:
        sum_d2 = df_detail["d2_numeric"].sum()
        denom = n * (n**2 - 1)
        rho = 1 - (6 * sum_d2) / denom
        st.markdown("#### Langkah Perhitungan:")
        st.latex(r"\rho = 1 - \frac{6 \times \sum d^2}{n(n^2 - 1)}")
        st.markdown("**1. Komponen Nilai:**")
        st.markdown(f"- Jumlah alternatif ($n$) = **{n}** alternatif")
        d2_values = df_detail["d2_numeric"].tolist()
        d2_sum_text = " + ".join([f"{v:.0f}" for v in d2_values])
        st.markdown(f"- Total $d^2$ (kuadrat selisih) ($\\sum d^2$) = {d2_sum_text} = **{sum_d2:.0f}**")
        n_squared = n**2
        n_squared_min_1 = n_squared - 1
        st.markdown(f"- Nilai penyebut ($n(n^2 - 1)$) = {n} × ({n}² - 1) = {n} × ({n_squared} - 1) = {n} × {n_squared_min_1} = **{denom}**")
        st.markdown("**2. Proses Substitusi Rumus:**")
        numerator = 6 * sum_d2
        fraction = numerator / denom if denom != 0 else 0
        st.latex(rf"\rho = 1 - \frac{{6 \times {sum_d2:.0f}}}{{{denom}}}")
        st.latex(rf"\rho = 1 - \frac{{{numerator:.0f}}}{{{denom}}}")
        st.latex(rf"\rho = 1 - {fraction:.4f}")
        st.latex(rf"\rho = {rho:.4f}")
        st.success(f"**Nilai Koefisien Korelasi ($\\rho$) = {rho:.4f}**")
        st.markdown("**Cara Membaca Nilai Spearman Rank ($\\rho$):**")
        st.markdown(""" *   **Nilai mendekati 1**: Peringkat yang dihasilkan oleh sistem/aplikasi sangat akurat karena searah dengan keputusan pakar.
        *   **Nilai mendekati 0**: Tidak ada hubungan antara hasil sistem dengan pakar (hasilnya acak).
        *   **Nilai mendekati -1**: Hasil peringkat sistem terbalik total dengan urutan pilihan milik pakar. """)
    else:
        st.info("Tidak cukup data untuk menghitung Spearman (n <= 1)")
    st.subheader("5️⃣ Perhitungan NDCG - Langkah Perhitungan")
    st.markdown("#### 1) Hitung DCG (Discounted Cumulative Gain)")
    st.markdown("Menyusun hasil alternatif berdasarkan nilai **Preferensi tertinggi (Top-K)** dari sistem, lalu menghitung kontribusi skor kemiripannya.")
    st.latex(r"DCG_p = \sum_{i=1}^{p} \frac{rel_i}{\log_2(i + 1)}")
    st.markdown("""**Keterangan:**
    * $rel_i$ = nilai relevansi alternatif pada posisi ke-$i$
    * $i$ = posisi alternatif dalam peringkat
    * $p$ = jumlah alternatif yang dievaluasi ($Top-K$)""")
    df_ndcg = df_merge.sort_values("Preferensi", ascending=False).reset_index(drop=True)
    df_ndcg = df_ndcg.head(k).copy()
    df_ndcg["Posisi"] = df_ndcg.index + 1
    df_ndcg["rel_numeric"] = 1 / df_ndcg["Rank Pakar"]
    df_ndcg["log_numeric"] = np.log2(df_ndcg["Posisi"] + 1)
    df_ndcg["dcg_i_numeric"] = df_ndcg["rel_numeric"] / df_ndcg["log_numeric"]
    df_ndcg["Relevansi (1/Rank Pakar)"] = df_ndcg.apply(lambda r: f"1 / {r['Rank Pakar']:.0f} = {r['rel_numeric']:.4f}", axis=1)
    df_ndcg["log₂ (Posisi + 1)"] = df_ndcg.apply(lambda r: f"log₂({r['Posisi']:.0f} + 1) = {r['log_numeric']:.4f}", axis=1)
    df_ndcg["Proses Rumus DCG"] = df_ndcg.apply(lambda r: f"{r['rel_numeric']:.4f} / {r['log_numeric']:.4f}", axis=1)
    df_dcg_view = df_ndcg.rename(columns={"dcg_i_numeric": "Kontribusi DCG"})
    st.dataframe(df_dcg_view[[
        "Alternatif", "Posisi", "Rank Pakar", "Relevansi (1/Rank Pakar)", 
        "log₂ (Posisi + 1)", "Proses Rumus DCG", "Kontribusi DCG"
    ]], use_container_width=True)
    dcg = df_ndcg["dcg_i_numeric"].sum()
    dcg_elements = " + ".join([f"{x:.6f}" for x in df_ndcg["dcg_i_numeric"]])
    st.markdown(f"- **Total DCG ($\sum \text{{DCG}}_i$)** = {dcg_elements} = **{dcg:.6f}**")
    st.markdown("##### Langkah Perhitungan:")
    st.markdown("**A. Nilai Relevansi ($Rel$):**")
    st.latex(r"\text{Relevansi} = \frac{1}{\text{Rank Pakar}}")
    for idx, row in df_ndcg.iterrows():
        st.markdown(f"* Alternatif **{row['Alternatif']}**: $1 / {int(row['Rank Pakar'])} = \mathbf{{{row['rel_numeric']:.4f}}}$")  
    st.markdown("**B. Nilai $\log_2(\text{Posisi} + 1)$:**")
    st.latex(r" \log_2(\text{Posisi} + 1)")
    for idx, row in df_ndcg.iterrows():
        pos_val = int(row['Posisi'])
        st.markdown(f"* Posisi **{pos_val}**: $\log_2({pos_val} + 1) = \log_2({pos_val + 1}) = \mathbf{{{row['log_numeric']:.4f}}}$")
    st.markdown("#### 2) Hitung IDCG (Ideal DCG)")
    st.markdown("Menyusun ulang urutan alternatif di atas berdasarkan **Relevansi tertinggi** secara ideal menurut penilaian Pakar.")
    st.latex(r"IDCG_p = \sum_{i=1}^{p} \frac{rel_i^*}{\log_2(i + 1)}")
    st.markdown("""**Keterangan:**
    * $rel_i^*$ = nilai relevansi alternatif pada posisi ke-$i$ berdasarkan peringkat ideal (referensi pakar)""")
    df_idcg = df_ndcg.sort_values("rel_numeric", ascending=False).reset_index(drop=True)
    df_idcg["Posisi"] = df_idcg.index + 1
    df_idcg["log_numeric_ideal"] = np.log2(df_idcg["Posisi"] + 1)
    df_idcg["idcg_i_numeric"] = df_idcg["rel_numeric"] / df_idcg["log_numeric_ideal"]
    df_idcg["Relevansi (Ideal)"] = df_idcg.apply(lambda r: f"1 / {r['Rank Pakar']:.0f} = {r['rel_numeric']:.4f}", axis=1)
    df_idcg["log₂ (Posisi + 1)"] = df_idcg.apply(lambda r: f"log₂({r['Posisi']:.0f} + 1) = {r['log_numeric_ideal']:.4f}", axis=1)
    df_idcg["Proses Rumus IDCG"] = df_idcg.apply(lambda r: f"{r['rel_numeric']:.4f} / {r['log_numeric_ideal']:.4f}", axis=1)
    df_idcg_view = df_idcg.rename(columns={"idcg_i_numeric": "Kontribusi IDCG"})
    st.dataframe(df_idcg_view[[
        "Alternatif", "Posisi", "Rank Pakar", "Relevansi (Ideal)", 
        "log₂ (Posisi + 1)", "Proses Rumus IDCG", "Kontribusi IDCG"
    ]], use_container_width=True)
    idcg = df_idcg["idcg_i_numeric"].sum()
    idcg_elements = " + ".join([f"{x:.6f}" for x in df_idcg["idcg_i_numeric"]])
    st.markdown(f"- **Total IDCG ($\sum \text{{IDCG}}_i$)** = {idcg_elements} = **{idcg:.6f}**")
    st.markdown("#### 3) Process Normalisasi Akhir (NDCG)")
    st.markdown(f"Membagi total nilai DCG sistem dengan IDCG ideal pakar untuk mengukur akurasi urutan pada **Top-{k}**.")
    st.latex(r"\text{NDCG} = \frac{\text{DCG}}{\text{IDCG}}")
    ndcg_val = dcg / idcg if idcg != 0 else 0
    st.latex(rf"\text{{NDCG}}@{k} = \frac{{{dcg:.6f}}}{{{idcg:.6f}}}")
    st.success(f"**Nilai NDCG@{k} = {ndcg_val:.4f}**")
    st.markdown(f"**Cara Membaca Nilai NDCG@{k}:**")
    st.markdown(f""" *   **Nilai mendekati 1**: Rekomendasi peringkat sistem sangat akurat karena berhasil menempatkan alternatif pilihan terbaik pakar di bagian paling atas daftar.
    *   **Nilai mendekati 0**: Susunan rekomendasi sistem di bagian atas daftar sangat tidak sesuai dengan urutan ideal milik pakar.""")
    st.header("📊 Hasil Evaluasi Semua Skenario")
    hasil = []
    for s in skenario_list:
        df_rank = pd.DataFrame(s["ranking"]).copy()
        df_rank = df_rank.reset_index(drop=True)
        df_merge = df_rank.merge(df_pakar, on="Alternatif", how="inner")
        # SPEARMAN (FIX)
        df_merge["d"] = df_merge["Ranking"] - df_merge["Rank Pakar"]
        df_merge["d2"] = df_merge["d"]**2
        n = len(df_merge)
        if n > 1:
            sp = 1 - (6 * df_merge["d2"].sum()) / (n * (n**2 - 1))
        else:
            sp = 0
        # NDCG (FIX)
        df_eval = df_merge.sort_values("Preferensi", ascending=False).reset_index(drop=True)
        df_eval = df_eval.head(k).copy()
        df_eval["rel"] = 1 / df_eval["Rank Pakar"]
        dcg = (df_eval["rel"] / np.log2(np.arange(2, len(df_eval)+2))).sum()
        df_ideal = df_eval.sort_values("rel", ascending=False).reset_index(drop=True)
        idcg = (df_ideal["rel"] / np.log2(np.arange(2, len(df_ideal)+2))).sum()
        nd = dcg / idcg if idcg != 0 else 0
        hasil.append({"Skenario": s["nama"],"Metode": s["metode"],"Catatan": s.get("catatan","-"),"Spearman": round(sp,4),f"NDCG@{k}": round(nd,4)})
    df_hasil = pd.DataFrame(hasil)
    st.dataframe(df_hasil, use_container_width=True)
    st.markdown(""" 💡 **Panduan Nilai (Skala 0-1):** Semakin mendekati **1.00**, hasil skenario sistem semakin akurat.
    * **Spearman:** Mengukur korelasi kemiripan ranking secara **keseluruhan**.
    * **NDCG:** Mengukur ketepatan urutan alternatif pada ranking **teratas (Top-K)** saja. """)
    st.subheader("🏆 Alternatif Terbaik (rata-rata nilai preferensi tertinggi dari semua skenario)")
    st.markdown(""" **Penjelasan singkat sumber hasil:**

    - Hasil terbaik ditentukan dari *rata‑rata preferensi* (Mean Preferensi) setiap alternatif yang dihitung dari semua skenario yang tersimpan.
    - Untuk tiap skenario, aplikasi mengambil tabel `ranking` yang berisi kolom `Alternatif` dan `Preferensi`. Nilai preferensi tersebut digabung ke dalam satu daftar, lalu dihitung rata‑rata per alternatif.
    - Jika sebuah alternatif tidak muncul pada suatu skenario, skenario tersebut tidak dihitung untuk alternatif itu (nilai yang hilang diabaikan saat menghitung mean).

    **Makna "Mean Preferensi":**
    - Ini adalah skor agregat (floating) yang menunjukkan performa rata‑rata alternatif di seluruh skenario.
    - Semakin tinggi Mean Preferensi → semakin sering/tinggi alternatif tersebut muncul di posisi atas pada berbagai skenario.
    """)
    all_pref = []
    for s in skenario_list:
        try:
            df_rank = pd.DataFrame(s.get("ranking", []))
            if "Alternatif" in df_rank.columns and "Preferensi" in df_rank.columns:
                all_pref.append(df_rank[["Alternatif", "Preferensi"]])
        except Exception:
            continue
    if all_pref:
        pref_concat = pd.concat(all_pref, ignore_index=True)
        pref_summary = (pref_concat.groupby("Alternatif", as_index=False).agg({"Preferensi": "mean"}))
        pref_summary.columns = ["Alternatif", "MeanPreferensi"]
        pref_summary = pref_summary.sort_values(by="MeanPreferensi", ascending=False).reset_index(drop=True)
        best_alt = pref_summary.iloc[0]
        st.markdown("**Tabel Mean Preferensi (semua alternatif)**")
        st.dataframe(pref_summary, use_container_width=True)
        top_k = 3
        if not pref_summary.empty:
            top_val = pref_summary.iloc[0]['MeanPreferensi']
            top3 = pref_summary.head(top_k).copy()
            if len(pref_summary) > top_k:
                third_val = top3.iloc[-1]['MeanPreferensi']
                ties = pref_summary[pref_summary['MeanPreferensi'] == third_val]
                if len(ties) > 1:
                    top3 = pref_summary[pref_summary['MeanPreferensi'] >= third_val]
        st.success(f"🏅 Alternatif Terbaik : {best_alt['Alternatif']} — Mean Preferensi: {best_alt['MeanPreferensi']:.4f}")
    else:
        st.info("Belum ada data preferensi dari skenario yang tersimpan.")
    st.subheader("📊 Analisis Stabilitas Metode")
    df_stabil = df_hasil.groupby("Metode").agg({"Spearman": ["mean", "std"],f"NDCG@{k}": ["mean", "std"]}).reset_index()
    df_stabil.columns = ["Metode","Mean Spearman","Std Spearman",f"Mean NDCG@{k}",f"Std NDCG@{k}"]
    st.dataframe(df_stabil, use_container_width=True)
    st.markdown(""" **Keterangan singkat (Mean & Std):**

    - Mean (rata‑rata): menunjukkan nilai rata‑rata metrik (Spearman atau NDCG@K) untuk tiap metode di seluruh skenario. Mean tinggi berarti metode cenderung memberikan hasil yang lebih mirip dengan pakar (untuk Spearman) atau lebih mendekati urutan ideal (untuk NDCG).
    - Std (standar deviasi): mengukur variasi/metrik antar skenario. Std kecil berarti hasil metode stabil/konisten antar skenario; Std besar berarti hasil sangat berfluktuasi tergantung skenario.

    Penjelasan praktis:
    - Metode yang baik biasanya memiliki Mean tinggi dan Std kecil (konsisten & akurat).
    - Di halaman ini memilih "Metode Paling Stabil" berdasarkan Std (variansi Spearman terendah), karena stabilitas penting untuk konsistensi rekomendasi.""")
    terbaik_stabil = df_stabil.sort_values(by="Std Spearman").iloc[0]
    st.success(f""" 📌 Metode Paling Stabil: {terbaik_stabil['Metode']}

    Alasan:
    - Variasi Spearman paling kecil (Std = {terbaik_stabil['Std Spearman']:.4f})
    - Hasil ranking paling konsisten antar skenario""")
st.markdown(""" <style>.footer{position:fixed;left:0;bottom:0;width:100%;background:linear-gradient(90deg,#0f766e,#14b8a6);color:white;text-align:center;padding:10px;font-size:14px;font-weight:500;z-index:999;box-shadow:0 -2px 12px rgba(0,0,0,0.12);}
.footer span{font-weight:700;color:#ffffff;}
.block-container{padding-bottom:70px;}
</style><div class="footer">© 2026 Sistem Pendukung Keputusan Pemilihan Varietas Benih Padi | Developed by <span>Adi Sahrul Ramadhan</span></div>""", unsafe_allow_html=True)    
