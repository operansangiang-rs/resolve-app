import streamlit as st
import json
import os
import requests
import base64

# =========================================================================
# 🔐 KONFIGURASI
# =========================================================================
try:
    GITHUB_TOKEN = st.secrets["github"]["token"]
    REPO_NAME = st.secrets["github"]["repo"]
except Exception:
    GITHUB_TOKEN = ""
    REPO_NAME = ""

DB_FILE = "data_store.json"

st.set_page_config(
    page_title="Resolve App",
    page_icon="🛠️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# =========================================================================
# FUNGSI DATA PERSISTENCE (GitHub Sync)
# =========================================================================
def push_to_github(data):
    if GITHUB_TOKEN.startswith("ghp_") and "/" in REPO_NAME:
        try:
            url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            res = requests.get(url, headers=headers)
            sha = res.json().get("sha") if res.status_code == 200 else None
            
            json_string = json.dumps(data, indent=4)
            content_base64 = base64.b64encode(json_string.encode("utf-8")).decode("utf-8")
            
            payload = {
                "message": "Sistem: Update data_store.json",
                "content": content_base64
            }
            if sha:
                payload["sha"] = sha
            requests.put(url, headers=headers, json=payload)
        except Exception as e:
            st.error(f"Gagal push ke GitHub: {e}")

def load_shared_data():
    """Mengambil data dari GitHub agar selalu terupdate."""
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            content = base64.b64decode(res.json().get("content")).decode("utf-8")
            data = json.loads(content)
            # Simpan lokal agar cepat
            with open(DB_FILE, "w") as f:
                json.dump(data, f, indent=4)
            return data
    except:
        pass
    
    # Fallback ke lokal jika gagal ambil dari GitHub
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
            
    return {"database": [], "categories": ["Support", "Smartplus", "Smarthis"]}

def save_shared_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)
    push_to_github(data)

# Load data
shared_data = load_shared_data()
db_list = shared_data["database"]
categories_list = shared_data["categories"]

# State management
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "editing_index" not in st.session_state: st.session_state.editing_index = None

# UI
st.sidebar.title("🔐 Akses Admin")
if not st.session_state.is_admin:
    admin_password = st.sidebar.text_input("Password Admin", type="password")
    if st.sidebar.button("Masuk"):
        if admin_password == "123":
            st.session_state.is_admin = True
            st.rerun()
else:
    if st.sidebar.button("Keluar"):
        st.session_state.is_admin = False
        st.rerun()

st.title("🛠️ Resolve App")
tab_cari, tab_admin = st.tabs(["🔍 Cari Solusi", "⚙️ Panel Admin"])

with tab_cari:
    search_query = st.text_input("Cari topik...")
    filter_kategori = st.selectbox("Filter Kategori:", ["Semua Kategori"] + categories_list)
    
    for item in db_list:
        if (search_query.lower() in item["topik"].lower()) and (filter_kategori == "Semua Kategori" or item["kategori"] == filter_kategori):
            with st.expander(f"📌 {item['topik']} ({item['kategori']})"):
                st.info(item["solusi"])

with tab_admin:
    if st.session_state.is_admin:
        # Form Tambah
        input_topik = st.text_input("Topik Baru:")
        input_kategori = st.selectbox("Kategori:", categories_list)
        input_solusi = st.text_area("Solusi:")
        if st.button("Simpan Solusi Baru"):
            db_list.append({"topik": input_topik, "solusi": input_solusi, "kategori": input_kategori})
            save_shared_data({"database": db_list, "categories": categories_list})
            st.success("Tersimpan!")
            st.rerun()
        
        # Daftar Edit/Hapus
        st.write("---")
        for i, item in enumerate(db_list):
            col1, col2 = st.columns([8, 2])
            col1.write(f"{item['topik']}")
            if col2.button("🗑️", key=f"del_{i}"):
                db_list.pop(i)
                save_shared_data({"database": db_list, "categories": categories_list})
                st.rerun()
    else:
        st.warning("Harap login sebagai Admin.")
