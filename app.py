import streamlit as st
import json
import os
import requests
import base64

# =========================================================================
# 🛠️ MAS LIAN, ISI DATA GITHUB ANDA DI SINI (AGAR DATA TERSIMPAN PERMANEN)
# =========================================================================
GITHUB_TOKEN = "ghp_xxxxXXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # Masukkan Personal Access Token GitHub Anda
REPO_NAME = "operansangiang-rs/resolve-app"       # Contoh: "yulianto/resolve-app"
# =========================================================================

DB_FILE = "data_store.json"

st.set_page_config(
    page_title="Resolve App",
    page_icon="🛠️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# =========================================================================
# FUNGSI OTOMATIS SYNC KE GITHUB (ANTI REBOOT/TERHAPUS)
# =========================================================================
def push_to_github(data):
    """Mengirim dan memperbarui file data_store.json langsung ke repositori GitHub."""
    if GITHUB_TOKEN.startswith("ghp_") and "/" in REPO_NAME:
        try:
            url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # 1. Ambil SHA file lama dari GitHub
            res = requests.get(url, headers=headers)
            sha = res.json().get("sha") if res.status_code == 200 else None
            
            # 2. Encode data JSON baru ke Base64
            json_string = json.dumps(data, indent=4)
            content_base64 = base64.b64encode(json_string.encode("utf-8")).decode("utf-8")
            
            # 3. Push/Commit balik ke GitHub
            payload = {
                "message": "Sistem: Update data_store.json dari aplikasi",
                "content": content_base64
            }
            if sha:
                payload["sha"] = sha
                
            requests.put(url, headers=headers, json=payload)
        except Exception as e:
            print(f"Gagal sinkronisasi ke GitHub: {e}")

def load_shared_data():
    """Membaca data terpusat dari file JSON agar tersambung antar-browser."""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
            
    return {
        "database": [
            {
                "topik": "Integrasi Sistem Smartplus Pertama Kali",
                "solusi": "1. Pastikan semua modul gateway sudah terhubung ke jaringan internet lokal.\n2. Lakukan sinkronisasi data melalui menu pengaturan di dasbor utama.",
                "kategori": "Smartplus"
            },
            {
                "topik": "Kendala Autentikasi Pengguna Smarthis",
                "solusi": "1. Lakukan reset cache pada browser atau gunakan mode incognito.\n2. Jika masalah berlanjut, hubungi tim infrastruktur untuk verifikasi ulang lisensi aktif.",
                "kategori": "Smarthis"
            }
        ],
        "categories": ["Support", "Smartplus", "Smarthis"]
    }

def save_shared_data(data):
    """Menyimpan data langsung ke file JSON lokal dan memicu push ke GitHub."""
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)
    # Picu penyimpanan abadi ke GitHub
    push_to_github(data)

# Memuat data terbaru dari database file di setiap interaksi/rerun
shared_data = load_shared_data()
db_list = shared_data["database"]
categories_list = shared_data["categories"]

# State UI yang tetap unik untuk masing-masing browser
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "editing_index" not in st.session_state:
    st.session_state.editing_index = None

st.sidebar.title("🔐 Akses Admin")

if not st.session_state.is_admin:
    st.sidebar.write("Masukkan password admin untuk mengaktifkan fitur Tambah, Edit, dan Hapus topik.")
    admin_password = st.sidebar.text_input("Password Admin", type="password", placeholder="Ketik password di sini...")
    
    if st.sidebar.button("Masuk", use_container_width=True):
        if admin_password == "123":
            st.session_state.is_admin = True
            st.sidebar.success("Login Berhasil! Selamat datang Mas Lian.")
            st.rerun()
        else:
            st.sidebar.error("Password salah! Silakan coba lagi.")
else:
    st.sidebar.success("Status: Admin Aktif (Mas Lian)")
    
    # Cek konfigurasi GitHub di sidebar sebagai pengingat
    if not GITHUB_TOKEN.startswith("ghp_") or "username" in REPO_NAME:
        st.sidebar.warning("⚠️ GitHub Token/Repo belum diisi di baris kode paling atas. Data layar masih bersifat sementara!")
        
    if st.sidebar.button("Keluar (Logout)", use_container_width=True):
        st.session_state.is_admin = False
        st.session_state.editing_index = None  
        st.sidebar.info("Anda telah logout.")
        st.rerun()

st.title("🛠️ Resolve App")
st.write("Temukan solusi cepat untuk berbagai kendala Support, Smartplus, dan Smarthis Anda.")
st.markdown("---")

tab_cari, tab_admin = st.tabs(["🔍 Cari Solusi", "⚙️ Panel Admin (Khusus Admin)"])

with tab_cari:
    st.subheader("Pusat Solusi & Troubleshooting")
    
    col_search_input, col_sync_btn = st.columns([8, 2])
    with col_search_input:
        search_query = st.text_input("Cari topik masalah di sini...", placeholder="Ketik kata kunci (misal: Smartplus, integrasi, dll)...")
    with col_sync_btn:
        st.write("") 
        st.write("") 
        if st.button("🔄 Sinkron", use_container_width=True, help="Klik untuk memuat ulang data terbaru"):
            st.rerun()
            
    filter_kategori = st.selectbox("Filter Kategori:", ["Semua Kategori"] + categories_list)
    
    filtered_data = []
    for item in db_list:
        match_query = search_query.lower() in item["topik"].lower() or search_query.lower() in item["solusi"].lower()
        match_category = filter_kategori == "Semua Kategori" or item["kategori"] == filter_kategori
        
        if match_query and match_category:
            filtered_data.append(item)
            
    st.write(f"Menampilkan **{len(filtered_data)}** solusi yang cocok:")
    
    if filtered_data:
        for index, item in enumerate(filtered_data):
            emojis = ["🟢", "🔵", "🟣", "🟡", "🟠", "🔴", "🟤", "⚫"]
            try:
                idx_kat = categories_list.index(item['kategori']) % len(emojis)
                emoji_tag = emojis[idx_kat]
            except ValueError:
                emoji_tag = "⚪" 
                
            kategori_tag = f"{emoji_tag} {item['kategori']}"
            
            with st.expander(f"📌 {item['topik']} ({kategori_tag})", expanded=True if search_query else False):
                solusi_rapi = item["solusi"].replace("\n", "  \n")
                st.info(solusi_rapi)
    else:
        st.warning("Maaf, topik atau solusi yang Anda cari tidak ditemukan.")

with tab_admin:
    st.subheader("Pusat Kontrol & Manajemen Solusi")
    
    if st.session_state.is_admin:
        kategori_pilihan = categories_list
        
        if st.session_state.editing_index is not None:
            idx_edit = st.session_state.editing_index
            if idx_edit < len(db_list):
                item_edit = db_list[idx_edit]
                
                st.write("---")
                st.markdown("### ✏️ Form Edit Solusi")
                
                with st.form("form_edit_solusi", clear_on_submit=False):
                    edit_topik = st.text_input("Edit Judul/Topik:", value=item_edit["topik"])
                    default_kat_idx = kategori_pilihan.index(item_edit["kategori"]) if item_edit["kategori"] in kategori_pilihan else 0
                    edit_kategori = st.selectbox("Edit Kategori:", kategori_pilihan, index=default_kat_idx)
                    edit_solusi = st.text_area("Edit Solusi Lengkap:", value=item_edit["solusi"])
                    
                    col_edit_1, col_edit_2 = st.columns(2)
                    with col_edit_1:
                        save_button = st.form_submit_button("Simpan Perubahan", use_container_width=True)
                    with col_edit_2:
                        cancel_button = st.form_submit_button("Batal Edit", use_container_width=True)
                    
                    if save_button:
                        if edit_topik.strip() == "" or edit_solusi.strip() == "":
                            st.error("Gagal mengubah! Judul topik dan isi solusi tidak boleh kosong.")
                        else:
                            db_list[idx_edit] = {
                                "topik": edit_topik,
                                "solusi": edit_solusi,
                                "kategori": edit_kategori
                            }
                            save_shared_data({"database": db_list, "categories": categories_list})
                            st.session_state.editing_index = None  
                            st.success("Perubahan solusi berhasil disimpan dan di-sinkronkan ke GitHub!")
                            st.rerun()
                            
                    if cancel_button:
                        st.session_state.editing_index = None  
                        st.rerun()
            else:
                st.session_state.editing_index = None

        else:
            st.markdown("### ➕ Tambah Solusi Baru")
            with st.form("form_tambah_solusi", clear_on_submit=True):
                input_topik = st.text_input("Judul Topik / Masalah Baru:", placeholder="Contoh: Mengatasi Error Login Gagal")
                input_kategori = st.selectbox("Pilih Kategori
