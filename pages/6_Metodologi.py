import streamlit as st
import pandas as pd

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Metodologi Penilaian",
    layout="centered"
)

st.header("Metodologi Penilaian")

# ===============================
# LOAD DATA (DATA BERSIH)
# ===============================
df = pd.read_csv("dataset/AfterCleaned.csv")

# Normalisasi Rating
df["Rating"] = (
    df["Rating"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .str.extract(r"(\d+\.?\d*)")[0]
)
df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")

# Normalisasi Jumlah Review
df["Jumlah Review"] = (
    df["Jumlah Review"]
    .astype(str)
    .str.replace(".", "", regex=False)
)
df["Jumlah Review"] = pd.to_numeric(df["Jumlah Review"], errors="coerce")
# ===============================
# NORMALISASI DATA NUMERIK
# ===============================
df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
df["Jumlah Review"] = pd.to_numeric(df["Jumlah Review"], errors="coerce")

# Drop NA & sort (eksplisit, biar clear)
ratings = df["Rating"].dropna().sort_values()
reviews = df["Jumlah Review"].dropna().sort_values()

# ===============================
# HITUNG NILAI TENGAH (MEDIAN)
# ===============================
median_rating = round(ratings.median(), 2)
median_review = int(reviews.median())

# ===============================
# TAMPILAN METODOLOGI
# ===============================
st.markdown(
f"""
###  Skema Skor

- **Aksesibilitas difabel**: 0–4  
- **Buka 24 jam**: +1  
- **Website resmi tersedia**: +1  
- **Nomor telepon tersedia**: +1  
- **Jumlah review ≥ {median_review}**: +2  
- **Rating ≥ {median_rating}**: +1  

---

###  Skor Maksimal
**10 poin**

---

###  Dasar Penentuan Ambang Batas
Ambang batas pada **rating** dan **jumlah review** ditentukan menggunakan  
**nilai tengah (median)** dari seluruh dataset tempat ibadah di Jawa Barat.

Data terlebih dahulu:
- dikonversi ke numerik
- nilai kosong diabaikan
- diurutkan untuk transparansi analisis

Pendekatan median dipilih karena:
- lebih stabil terhadap data ekstrem
- mencerminkan kondisi mayoritas
- meningkatkan objektivitas penilaian

---

###  Tujuan Metodologi
Metodologi ini digunakan sebagai dasar untuk:
- pemeringkatan tempat ibadah
- analisis pemerataan antar wilayah
- penyusunan rekomendasi peningkatan aksesibilitas dan kualitas informasi
"""
)

# ===============================
# INFO TAMBAHAN (OPSIONAL)
# ===============================
st.info(
    f" Median dataset saat ini → Rating: {median_rating}, Jumlah Review: {median_review}"
)
