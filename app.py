import streamlit as st

# Pengaturan halaman awal
st.set_page_config(page_title="Resolve App", page_icon="🛠️", layout="centered")

# Header Utama
st.title("🛠️ Resolve App")
st.subheader("Solusi Cerdas untuk Problem Aplikasi Anda")

st.markdown("---")

# Konten selamat datang
st.success("Repository berhasil terkoneksi!")
st.write("Selamat datang, Mas Lian! Mari kita mulai bangun fitur troubleshooting di sini.")

# Contoh input interaktif sederhana
user_problem = st.text_input("Masukkan kendala atau error aplikasi yang Anda alami:")
if user_problem:
    st.info(f"Kendala yang Anda masukkan: *{user_problem}*")
    st.write("Fitur analisis solusi akan segera siap di sini!")
