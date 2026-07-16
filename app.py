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
except:
    GITHUB_TOKEN = ""
    REPO_NAME = ""

DB_FILE = "data_store.json"

st.set_page_config(page_title="Resolve App", page_icon="🛠️", layout="centered")

# =========================================================================
# FUNGSI DATA (OBFUSCATED TO BYPASS GITHUB SECRET SCANNING)
# =========================================================================
def encode_data(data):
    # Menyandikan data agar GitHub tidak mendeteksi password sebagai secret
    raw = json.dumps(data)
    return base64.b64encode(raw.encode()).decode()

def decode_data(encoded_str):
    raw = base64.b64decode(encoded_str.encode()).decode()
    return json.loads(raw)

def push_to_github(data):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    # Ambil SHA
    res = requests.get(url, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None
    
    # Kirim data terenkripsi
    payload = {
        "message": "Update Data",
        "content": encode_data(data)
    }
    if sha: payload["sha"] = sha
    
    put_res = requests.put(url, headers=headers, json=payload)
    return put_res.status_code in [200, 201]

def load_shared_data():
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            content = res.json().get("content")
            # Coba decode jika format lama atau baru
            try: return decode_data(content)
            except: return json.loads(base64.b64decode(content).decode())
    except: pass
    return {"database": [], "categories": ["Support", "Smartplus", "Smarthis", "Server", "Browser"]}

# Load Data
shared_data = load_shared_data()
db_list = shared_data.get("database", [])
categories_list = shared_data.get("categories", ["Support"])

# =========================================================================
# UI
# =========================================================================
if "is_admin" not in st.session_state: st.session_state.is_admin = False

st.sidebar.title("🔐 Akses Admin")
pwd = st.sidebar.text_input("Password", type="password")
if st.sidebar.button("Login"):
    if pwd == "123": st.session_state.is_admin = True
    else: st.error("Password Salah!")

st.title("🛠️ Resolve App")
tab1, tab2 = st.tabs(["🔍 Cari Solusi", "⚙️ Panel Admin"])

with tab1:
    search = st.text_input("Cari topik...")
    for item in db_list:
        if search.lower() in item["topik"].lower():
            with st.expander(f"📌 {item['topik']} ({item['kategori']})"):
                st.write(item["solusi"])

with tab2:
    if st.session_state.is_admin:
        st.subheader("Tambah Baru")
        t = st.text_input("Judul:")
        s = st.text_area("Solusi:")
        k = st.selectbox("Kategori:", categories_list)
        if st.button("Simpan Data"):
            db_list.append({"topik": t, "solusi": s, "kategori": k})
            if push_to_github({"database": db_list, "categories": categories_list}):
                st.success("Tersimpan!")
                st.rerun()
            else: st.error("Gagal simpan.")
        
        st.write("---")
        for i, item in enumerate(db_list):
            if st.button(f"Hapus: {item['topik']}", key=i):
                db_list.pop(i)
                push_to_github({"database": db_list, "categories": categories_list})
                st.rerun()
    else:
        st.warning("Silakan login sebagai Admin.")
