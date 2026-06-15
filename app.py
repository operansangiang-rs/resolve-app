import streamlit as st

st.set_page_config(
    page_title="Resolve App",
    page_icon="🛠️",
    layout="centered",
    initial_sidebar_state="expanded"
)

if "database" not in st.session_state:
    st.session_state.database = [
        {
            "topik": "Integrasi Sistem Smartplus Pertama Kali",
            "solusi": "Pastikan semua modul gateway sudah terhubung ke jaringan internet lokal, lalu lakukan sinkronisasi data melalui menu pengaturan di dasbor utama.",
            "kategori": "Smartplus"
        },
        {
            "topik": "Kendala Autentikasi Pengguna Smarthis",
            "solusi": "Lakukan reset cache pada browser atau gunakan mode incognito. Jika masalah berlanjut, hubungi tim infrastruktur untuk verifikasi ulang lisensi aktif.",
            "kategori": "Smarthis"
        }
    ]

# Inisialisasi daftar kategori default jika belum ada di session state
if "categories" not in st.session_state:
    st.session_state.categories = ["Support", "Smartplus", "Smarthis"]

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
    if st.sidebar.button("Keluar (Logout)", use_container_width=True):
        st.session_state.is_admin = False
        st.session_state.editing_index = None  # Reset status edit saat logout
        st.sidebar.info("Anda telah logout.")
        st.rerun()

st.title("🛠️ Resolve App")
st.write("Temukan solusi cepat untuk berbagai kendala Support, Smartplus, dan Smarthis Anda.")
st.markdown("---")

tab_cari, tab_admin = st.tabs(["🔍 Cari Solusi", "⚙️ Panel Admin (Khusus Admin)"])

# ================= TAB 1: CARI & LIHAT SOLUSI (DAPAT DIAKSES SEMUA ORANG) =================
with tab_cari:
    st.subheader("Pusat Solusi & Troubleshooting")
    
    # Input pencarian data secara real-time
    search_query = st.text_input("Cari topik masalah di sini...", placeholder="Ketik kata kunci (misal: Smartplus, integrasi, dll)...")
    
    # Filter kategori dinamis dari session state
    filter_kategori = st.selectbox("Filter Kategori:", ["Semua Kategori"] + st.session_state.categories)
    
    # Proses pencarian dan pemfilteran data
    filtered_data = []
    for item in st.session_state.database:
        match_query = search_query.lower() in item["topik"].lower() or search_query.lower() in item["solusi"].lower()
        match_category = filter_kategori == "Semua Kategori" or item["kategori"] == filter_kategori
        
        if match_query and match_category:
            filtered_data.append(item)
            
    st.write(f"Menampilkan **{len(filtered_data)}** solusi yang cocok:")
    
    # Menampilkan hasil filter ke dalam box expander
    if filtered_data:
        for index, item in enumerate(filtered_data):
            # Warna penanda kategori dinamis menggunakan emoji berdasarkan indeksnya
            emojis = ["🟢", "🔵", "🟣", "🟡", "🟠", "🔴", "🟤", "⚫"]
            try:
                idx_kat = st.session_state.categories.index(item['kategori']) % len(emojis)
                emoji_tag = emojis[idx_kat]
            except ValueError:
                emoji_tag = "⚪" # Fallback jika kategori tidak ditemukan/terhapus
                
            kategori_tag = f"{emoji_tag} {item['kategori']}"
            
            with st.expander(f"📌 {item['topik']} ({kategori_tag})", expanded=True if search_query else False):
                # Mengganti karakter enter (\n) dengan spasi ganda + \n agar dibaca sebagai baris baru oleh Markdown
                solusi_rapi = item["solusi"].replace("\n", "  \n")
                st.info(solusi_rapi)
    else:
        st.warning("Maaf, topik atau solusi yang Anda cari tidak ditemukan.")

# ================= TAB 2: PANEL ADMIN (TAMBAH, EDIT, & HAPUS TOPIK) =================
with tab_admin:
    st.subheader("Pusat Kontrol & Manajemen Solusi")
    
    if st.session_state.is_admin:
        # Pilihan Kategori diambil dari session state dinamis
        kategori_pilihan = st.session_state.categories
        
        if st.session_state.editing_index is not None:
            idx_edit = st.session_state.editing_index
            # Pastikan index masih ada di list untuk menghindari error
            if idx_edit < len(st.session_state.database):
                item_edit = st.session_state.database[idx_edit]
                
                st.write("---")
                st.markdown("### ✏️ Form Edit Solusi")
                
                with st.form("form_edit_solusi", clear_on_submit=False):
                    edit_topik = st.text_input("Edit Judul/Topik:", value=item_edit["topik"])
                    
                    # Mencari index kategori yang sesuai saat ini
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
                            st.session_state.database[idx_edit] = {
                                "topik": edit_topik,
                                "solusi": edit_solusi,
                                "kategori": edit_kategori
                            }
                            st.session_state.editing_index = None  # Selesai mengedit
                            st.success("Perubahan solusi berhasil disimpan!")
                            st.rerun()
                            
                    if cancel_button:
                        st.session_state.editing_index = None  # Batalkan edit
                        st.rerun()
            else:
                st.session_state.editing_index = None

        else:
            st.markdown("### ➕ Tambah Solusi Baru")
            with st.form("form_tambah_solusi", clear_on_submit=True):
                input_topik = st.text_input("Judul Topik / Masalah Baru:", placeholder="Contoh: Mengatasi Error Login Gagal")
                input_kategori = st.selectbox("Pilih Kategori:", kategori_pilihan)
                input_solusi = st.text_area("Solusi Lengkap:", placeholder="Tuliskan langkah-langkah penanganan secara rinci di sini...")
                
                submit_button = st.form_submit_button("Simpan Solusi Baru", use_container_width=True)
                
                if submit_button:
                    if input_topik.strip() == "" or input_solusi.strip() == "":
                        st.error("Gagal menyimpan! Judul topik dan isi solusi tidak boleh kosong.")
                    else:
                        st.session_state.database.append({
                            "topik": input_topik,
                            "solusi": input_solusi,
                            "kategori": input_kategori
                        })
                        st.success(f"Sukses! Topik baru '{input_topik}' berhasil ditambahkan.")
                        st.rerun()
        
        # ================= FITUR BARU: MANAJEMEN KATEGORI (ADD/DELETE) =================
        st.write("---")
        st.markdown("### 📁 Kelola Kategori Aplikasi")
        with st.expander("⚙️ Buka Menu Tambah / Hapus Kategori"):
            col_kat_input, col_kat_btn = st.columns([7, 3])
            with col_kat_input:
                new_kat_input = st.text_input("Nama Kategori Baru:", placeholder="Contoh: Hardware, Network, Server...")
            with col_kat_btn:
                st.write("") # Spacing layout
                st.write("") # Spacing layout
                btn_add_kat = st.button("Tambah", use_container_width=True)
                
            if btn_add_kat:
                clean_kat = new_kat_input.strip()
                if clean_kat == "":
                    st.error("Nama kategori baru tidak boleh kosong!")
                elif clean_kat in st.session_state.categories:
                    st.warning(f"Kategori '{clean_kat}' sudah terdaftar.")
                else:
                    st.session_state.categories.append(clean_kat)
                    st.success(f"Kategori '{clean_kat}' berhasil ditambahkan!")
                    st.rerun()
            
            st.write("**Daftar Kategori Aktif Saat Ini:**")
            for kat in st.session_state.categories:
                col_name, col_del_kat = st.columns([8, 2])
                with col_name:
                    st.write(f"🔸 {kat}")
                with col_del_kat:
                    # Cegah penghapusan jika kategori sisa 1 demi estetika form dropdown
                    if st.button("Hapus", key=f"del_kat_{kat}", use_container_width=True):
                        if len(st.session_state.categories) <= 1:
                            st.error("Gagal! Minimal harus ada 1 kategori di aplikasi.")
                        else:
                            st.session_state.categories.remove(kat)
                            st.success(f"Kategori '{kat}' berhasil dihapus!")
                            st.rerun()

        st.write("---")
        st.markdown("### 📋 Daftar Kelola Topik Saat Ini")
        
        if st.session_state.database:
            for i, item in enumerate(st.session_state.database):
                # Membuat layout 3 kolom untuk menampilkan nama topik dan tombol aksi
                col_text, col_edit, col_del = st.columns([6, 1.5, 1.5])
                
                with col_text:
                    st.markdown(f"**{i+1}. {item['topik']}**  \n*Kategori: {item['kategori']}*")
                
                with col_edit:
                    if st.button("✏️ Edit", key=f"btn_edit_{i}", use_container_width=True):
                        st.session_state.editing_index = i
                        st.rerun()
                        
                with col_del:
                    if st.button("🗑️ Hapus", key=f"btn_del_{i}", use_container_width=True):
                        topik_deleted = st.session_state.database.pop(i)
                        st.success(f"Topik '{topik_deleted['topik']}' berhasil dihapus!")
                        # Jika sedang mengedit topik yang baru saja dihapus, matikan mode edit
                        if st.session_state.editing_index == i:
                            st.session_state.editing_index = None
                        st.rerun()
                st.write("---")
        else:
            st.info("Belum ada topik yang terdaftar di sistem. Silakan tambahkan topik pertama Anda di atas.")
            
    else:
        # Tampilan jika diakses oleh pengunjung umum
        st.warning("⚠️ Akses Dibatasi!")
        st.info("Menu manajemen data (tambah, edit, dan hapus topik) hanya dapat diakses oleh Admin. Silakan masukkan password **Admin** terlebih dahulu pada kolom di sidebar sebelah kiri.")
