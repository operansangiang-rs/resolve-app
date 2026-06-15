import streamlit as st

# 1. SETUP & KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Resolve App",
    page_icon="🛠️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 2. INISIALISASI DATABASE (Menggunakan Session State agar data tersimpan sementara)
if "database" not in st.session_state:
    st.session_state.database = [
        {
            "topik": "Rasio Campuran Pertalite & Pertamax CR-V Gen 4",
            "solusi": "Gunakan rasio 1:1 (misal 20 Liter Pertalite + 20 Liter Pertamax) untuk menghasilkan oktan RON 91. Ini sangat aman untuk mesin non-turbo Gen 4 dan lebih hemat di kantong.",
            "kategori": "Otomotif"
        },
        {
            "topik": "Cara Cepat Pindah Desktop 1 & 2 di Laptop",
            "solusi": "Di Windows: Tekan tombol kombinasi 'Ctrl + Windows + Panah Kiri/Kanan', atau geser touchpad ke kiri/kanan menggunakan 4 jari sekaligus.",
            "kategori": "Sistem Operasi"
        }
    ]

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# 3. SISTEM AKSES ADMIN TUNGGAL DI SIDEBAR
st.sidebar.title("🔐 Akses Admin")

if not st.session_state.is_admin:
    st.sidebar.write("Masukkan password khusus admin untuk menambah/mengelola topik baru.")
    
    # Input password khusus admin (Langsung password '123' tanpa perlu mengetik username)
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
    if st.sidebar.button("Keluar (Logout)", use_container_width=True):
        st.session_state.is_admin = False
        st.sidebar.info("Anda telah logout.")
        st.rerun()

# 4. TAMPILAN UTAMA APLIKASI
st.title("🛠️ Resolve App")
st.write("Temukan solusi cepat untuk berbagai kendala operasional dan teknis Anda.")
st.markdown("---")

# Membuat Tab Navigasi
tab_cari, tab_tambah = st.tabs(["🔍 Cari Solusi", "➕ Tambah Topik (Khusus Admin)"])

# ================= TAB 1: CARI & LIHAT SOLUSI (DAPAT DIAKSES SEMUA ORANG) =================
with tab_cari:
    st.subheader("Pusat Solusi & Troubleshooting")
    
    # Input pencarian (Hanya bisa dibaca/dilihat, pengunjung biasa tidak bisa menambah data di sini)
    search_query = st.text_input("Cari topik masalah di sini...", placeholder="Ketik kata kunci (misal: CR-V, desktop, dll)...")
    
    # Filter pencarian secara real-time
    filtered_data = [
        item for item in st.session_state.database 
        if search_query.lower() in item["topik"].lower() or search_query.lower() in item["solusi"].lower()
    ]
    
    st.write(f"Menampilkan **{len(filtered_data)}** solusi yang cocok:")
    
    # Menampilkan hasil pencarian dalam bentuk box ekspander yang rapi
    if filtered_data:
        for index, item in enumerate(filtered_data):
            with st.expander(f"📌 {item['topik']} ({item['kategori']})", expanded=True if search_query else False):
                st.info(item["solusi"])
    else:
        st.warning("Maaf, topik atau solusi yang Anda cari tidak ditemukan.")

# ================= TAB 2: TAMBAH TOPIK BARU (HANYA UNTUK ADMIN) =================
with tab_tambah:
    st.subheader("Kelola Solusi Baru")
    
    # Validasi apakah user sudah login sebagai admin (Mas Lian)
    if st.session_state.is_admin:
        st.write("Silakan masukkan topik kendala beserta solusinya di bawah ini:")
        
        with st.form("form_tambah_solusi", clear_on_submit=True):
            input_topik = st.text_input("Judul Topik / Masalah:", placeholder="Contoh: Mengatasi Printer Paper Jam")
            input_kategori = st.selectbox("Kategori:", ["Umum", "Otomotif", "Sistem Operasi", "Hardware", "Software"])
            input_solusi = st.text_area("Solusi Lengkap:", placeholder="Tuliskan langkah-langkah solusinya secara detail di sini...")
            
            submit_button = st.form_submit_button("Simpan Solusi", use_container_width=True)
            
            if submit_button:
                if input_topik.strip() == "" or input_solusi.strip() == "":
                    st.error("Gagal menyimpan! Judul topik dan isi solusi tidak boleh kosong.")
                else:
                    # Menambahkan data baru ke dalam session state database
                    st.session_state.database.append({
                        "topik": input_topik,
                        "solusi": input_solusi,
                        "kategori": input_kategori
                    })
                    st.success(f"Sukses! Topik '{input_topik}' berhasil ditambahkan ke sistem.")
    else:
        # Tampilan jika user biasa mencoba mengakses menu input
        st.warning("⚠️ Akses Dibatasi!")
        st.info("Menu menulis topik dan solusi baru ini dikunci untuk umum. Silakan masukkan password **Admin** terlebih dahulu melalui kolom di sidebar sebelah kiri.")
