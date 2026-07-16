import streamlit as st
import json
import os
import requests
import base64

# =========================================================================
# 🔐 KONFIGURASI & AUTH
# =========================================================================
try:
    GITHUB_TOKEN = st.secrets["github"]["token"]
    REPO_NAME = st.secrets["github"]["repo"]
except Exception:
    GITHUB_TOKEN = ""
    REPO_NAME = ""

DB_FILE = "data_store.json"

st.set_page_config(page_title="Resolve App", page_icon="🛠️", layout="centered", initial_sidebar_state="expanded")

# =========================================================================
# FUNGSI SYNC GITHUB (DENGAN ERROR REPORTING)
# =========================================================================
def push_to_github(data):
    if not GITHUB_TOKEN or not REPO_NAME:
        st.error("Konfigurasi Secrets (Token/Repo) belum diatur!")
        return False
        
    try:
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        
        # Ambil SHA lama
        res = requests.get(url, headers=headers)
        sha = res.json().get("sha") if res.status_code == 200 else None
        
        # Siapkan payload
        json_string = json.dumps(data, indent=4)
        content_base64 = base64.b64encode(json_string.encode("utf-8")).decode("utf-8")
        payload = {"message": "Update data_store.json", "content": content_base64}
        if sha: payload["sha"] = sha
        
        # Push
        put_res = requests.put(url, headers=headers, json=payload)
        if put_res.status_code in [200, 201]:
            st.success("Data berhasil tersimpan ke GitHub!")
            return True
        else:
            st.error(f"Gagal Simpan ke GitHub! Status: {put_res.status_code} - {put_res.text}")
            return False
    except Exception as e:
        st.error(f"Terjadi error sistem: {e}")
        return False

def load_shared_data():
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            content = base64.b64decode(res.json().get("content")).decode("utf-8")
            data = json.loads(content)
            return data
    except: pass
    
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {"database": [], "categories": ["Support", "Smartplus", "Smarthis"]}

# Data Management
shared_data = load_shared_data()
db_list = shared_data.get("database", [])
categories_list = shared_data.get("categories", ["Support"])

# UI Login
if "is_admin" not in st.session_state: st.session_state.is_admin = False
st.sidebar.title("🔐 Akses Admin")
if not st.session_state.is_admin:
    pwd = st.sidebar.text_input("Password Admin", type="password")
    if st.sidebar.button("Masuk"):
        if pwd == "123":
            st.session_state.is_admin = True
            st.rerun()
        else: st.sidebar.error("Password Salah!")
else:
    if st.sidebar.button("Keluar"):
        st.session_state.is_admin = False
        st.rerun()

# Main UI
st.title("🛠️ Resolve App")
tab1, tab2 = st.tabs(["🔍 Cari Solusi", "⚙️ Panel Admin"])

with tab1:
    search = st.text_input("Cari topik...")
    for item in db_list:
        if search.lower() in item["topik"].lower():
            with st.expander(f"📌 {item['topik']}"):
                st.info(item["solusi"])

with tab2:
    if st.session_state.is_admin:
        st.subheader("Tambah Solusi")
        t = st.text_input("Judul:")
        s = st.text_area("Solusi:")
        k = st.selectbox("Kategori:", categories_list)
        if st.button("Simpan"):
            db_list.append({"topik": t, "solusi": s, "kategori": k})
            if push_to_github({"database": db_list, "categories": categories_list}):
                st.rerun()
        
        st.write("---")
        for i, item in enumerate(db_list):
            if st.button(f"Hapus {item['topik']}", key=i):
                db_list.pop(i)
                push_to_github({"database": db_list, "categories": categories_list})
                st.rerun()
    else:
        st.warning("Admin diperlukan.")
