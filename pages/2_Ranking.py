import streamlit as st
import pandas as pd

from utils.scoring import calculate_score

st.set_page_config(
    page_title="Ranking Tempat Ibadah",
    layout="wide"
)

st.title("Ranking Tempat Ibadah Jawa Barat")
st.caption("Berbasis Aksesibilitas Difabel & Kualitas Informasi")

# ===============================
# LOAD DATA
# ===============================
@st.cache_data
def load_data():
    return pd.read_csv("dataset/AfterCleaned.csv")

df = load_data()

# ===============================
# HITUNG SKOR (INI KUNCINYA)
# ===============================
df = calculate_score(df)

# ===============================
# FILTER
# ===============================
st.sidebar.header("Filter Ranking")

jenis_filter = st.sidebar.selectbox(
    "Jenis Tempat Ibadah",
    ["Semua"] + sorted(df["Jenis Tempat"].dropna().unique())
)

daerah_filter = st.sidebar.selectbox(
    "Kota/Kabupaten",
    ["Semua"] + sorted(df["Kota/Kabupaten"].dropna().unique())
)

top_n = st.sidebar.slider("Tampilkan Top", 5, 50, 10)

ranking_df = df.copy()

if jenis_filter != "Semua":
    ranking_df = ranking_df[ranking_df["Jenis Tempat"] == jenis_filter]

if daerah_filter != "Semua":
    ranking_df = ranking_df[ranking_df["Kota/Kabupaten"] == daerah_filter]

# ===============================
# RANKING
# ===============================
ranking_df = ranking_df.sort_values(
    by="Skor Total",
    ascending=False
).reset_index(drop=True)

ranking_df["Ranking"] = ranking_df.index + 1

# ===============================
# TAMPILAN
# ===============================
st.subheader("Ranking Tempat Ibadah")

st.dataframe(
    ranking_df[
        [
            "Ranking",
            "Nama Tempat",
            "Jenis Tempat",
            "Kota/Kabupaten",
            "Skor Total"
        ]
    ].head(top_n),
    use_container_width=True
)

# ===============================
# INSIGHT
# ===============================
st.subheader("Insight")

if not ranking_df.empty:
    top = ranking_df.iloc[0]
    st.markdown(f"""
    Tempat ibadah dengan **skor tertinggi** adalah  
    **{top['Nama Tempat']}** di **{top['Kota/Kabupaten']}**,  
    dengan skor **{top['Skor Total']}**.

    Hal ini menunjukkan kombinasi fasilitas aksesibilitas difabel
    dan kualitas informasi yang paling optimal.
    """)
