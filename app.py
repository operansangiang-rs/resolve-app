import streamlit as st
import json
import requests
import base64

# =========================================================================
# KONFIGURASI
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
# FUNGSI DATA
# =========================================================================
def push_to_github(data):
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    
    res = requests.get(url, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None
    
    raw_json = json.dumps(data)
    content_b64 = base64.b64encode(raw_json.encode()).decode()
    
    payload = {"message": "Update data", "content": content_b64}
    if sha: payload["sha"] = sha
    
    put_res = requests.put(url, headers=headers, json=payload)
    return put_res.status_code in [200, 201]

def load_shared_data_fresh():
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{DB_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Cache-Control": "no-cache"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            content = res.json().get("content")
            decoded = base64.b64decode(content.encode()).decode()
            return json.loads(decoded)
    except: pass
    return {"database": [], "categories": ["Support", "Smartplus", "Smarthis", "Server", "Browser"]}

# =========================================================================
# UI & LOGIKA
# =========================================================================
shared_data = load_shared_data_fresh()
db_list = shared_data.get("database", [])
categories_list = shared_data.get("categories", ["Support"])

if "is_admin" not in st.session_state: st.session_state.is_admin = False

st.sidebar.title("🔐 Akses Admin")
if not st.session_state.is_admin:
    pwd = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if pwd == "123": st.session_state.is_admin = True; st.rerun()
        else: st.error("Password Salah!")
else:
    if st.sidebar.button("Keluar"): st.session_state.is_admin = False; st.rerun()

# Tombol Penyegaran Global
if st.button("🔄 Segarkan Data (Refresh)"):
    st.rerun()

st.title("🛠️ Resolve App")
tab1, tab2 = st.tabs(["🔍 Cari Solusi", "⚙️ Panel Admin"])

with tab1:
    search = st.text_input("Cari topik masalah...")
    for item in db_list:
        if search.lower() in item["topik"].lower():
            with st.expander(f"📌 {item['topik']} ({item['kategori']})"):
                st.info(item["solusi"])

with tab2:
    if st.session_state.is_admin:
        st.subheader("➕ Tambah Solusi Baru")
        t = st.text_input("Judul:")
        s = st.text_area("Solusi:")
        k = st.selectbox("Kategori:", categories_list)
        if st.button("Simpan Solusi"):
            db_list.append({"topik": t, "solusi": s, "kategori": k})
            if push_to_github({"database": db_list, "categories": categories_list}):
                st.success("Tersimpan!")
                st.rerun()
        
        st.write("---")
        st.subheader("🗑️ Daftar Kelola Data")
        for i, item in enumerate(db_list):
            col1, col2 = st.columns([0.7, 0.3])
            col1.write(f"**{i+1}. {item['topik']}**")
            with col2:
                if st.button("Hapus Data", key=f"del_{i}", type="primary"):
                    db_list.pop(i)
                    if push_to_github({"database": db_list, "categories": categories_list}):
                        st.rerun()
    else:
        st.warning("⚠️ Silakan login di sidebar untuk akses admin.")
