import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils.scoring import calculate_score

st.set_page_config(
    page_title="Insight & Analisis",
    layout="wide"
)

st.title(" Insight & Analisis Kualitas Tempat Ibadah")

# ===============================
# LOAD & PREPARE DATA
# ===============================
df = pd.read_csv("dataset/AfterCleaned.csv")
df.columns = df.columns.str.strip()

df = calculate_score(df)

# pastikan numerik
num_cols = ["Rating", "Jumlah Review", "Skor Total", "Skor Aksesibilitas"]
for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# ===============================
# SIDEBAR FILTER
# ===============================
st.sidebar.header(" Filter Analisis")

daerah_list = ["Semua"] + sorted(df["Kota/Kabupaten"].dropna().unique())
jenis_list = ["Semua"] + sorted(df["Jenis Tempat"].dropna().unique())

selected_daerah = st.sidebar.selectbox("Kota / Kabupaten", daerah_list)
selected_jenis = st.sidebar.selectbox("Jenis Tempat Ibadah", jenis_list)

# ===============================
# FILTER DATA
# ===============================
df_filtered = df.copy()

if selected_daerah != "Semua":
    df_filtered = df_filtered[df_filtered["Kota/Kabupaten"] == selected_daerah]

if selected_jenis != "Semua":
    df_filtered = df_filtered[df_filtered["Jenis Tempat"] == selected_jenis]

# ===============================
# HEADER DINAMIS
# ===============================
st.markdown(
    f"""
     **Cakupan Analisis:**  
    - **Daerah:** {selected_daerah}  
    - **Jenis Tempat Ibadah:** {selected_jenis}
    """
)

# ===============================
# KPI RINGKASAN
# ===============================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Jumlah Tempat Ibadah", len(df_filtered))

with col2:
    st.metric("Rata-rata Skor Total", round(df_filtered["Skor Total"].mean(), 2))

with col3:
    st.metric(
        "Persentase Akses Difabel (%)",
        round((df_filtered["Skor Aksesibilitas"] > 0).mean() * 100, 1)
    )

with col4:
    st.metric(
        "Rata-rata Rating",
        round(df_filtered["Rating"].mean(), 2)
    )

st.divider()

# ===============================
# 1. KETIMPANGAN AKSESIBILITAS
# ===============================
st.subheader(" Ketimpangan Aksesibilitas Difabel")

akses_daerah = (
    df_filtered
    .groupby("Kota/Kabupaten")["Skor Aksesibilitas"]
    .mean()
    .reset_index()
    .sort_values("Skor Aksesibilitas")
)

fig1 = px.bar(
    akses_daerah,
    x="Skor Aksesibilitas",
    y="Kota/Kabupaten",
    orientation="h",
    title="Rata-rata Skor Aksesibilitas per Daerah",
    color="Skor Aksesibilitas",
    color_continuous_scale="Blues"
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("""
**Insight:**  
Terlihat adanya ketimpangan fasilitas aksesibilitas difabel antar daerah.  
Wilayah dengan skor rendah memerlukan perhatian khusus dalam pemerataan fasilitas publik.
""")

st.divider()

# ===============================
# 2. KORELASI RATING vs SKOR TOTAL
# ===============================
st.subheader(" Korelasi Rating dan Skor Total")

fig2 = px.scatter(
    df_filtered,
    x="Rating",
    y="Skor Total",
    color="Skor Aksesibilitas",
    size="Jumlah Review",
    title="Rating vs Skor Total",
    labels={
        "Rating": "Rating Pengguna",
        "Skor Total": "Skor Total Kualitas"
    }
)

st.plotly_chart(fig2, use_container_width=True)

corr = df_filtered["Rating"].corr(df_filtered["Skor Total"])

st.markdown(f"""
**Insight:**  
Nilai korelasi antara rating dan skor total adalah **{corr:.2f}**.  
Hal ini menunjukkan bahwa **rating yang tinggi tidak selalu diikuti oleh kualitas aksesibilitas dan informasi yang baik**.
""")

st.divider()

# ===============================
# 3. INFORMASI PUBLIK
# ===============================
st.subheader(" Ketersediaan Informasi Publik")

info_df = pd.DataFrame({
    "Kategori": ["Website", "Telepon"],
    "Persentase (%)": [
        df_filtered["Website"].mean() * 100,
        df_filtered["Telepon"].mean() * 100
    ]
})

fig3 = px.bar(
    info_df,
    x="Kategori",
    y="Persentase (%)",
    text="Persentase (%)",
    title="Ketersediaan Informasi Publik"
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("""
**Insight:**  
Ketersediaan informasi publik masih belum merata.  
Tempat ibadah dengan informasi yang lengkap cenderung memiliki skor total yang lebih tinggi.
""")

st.divider()

# ===============================
# 4. PRIORITAS PERBAIKAN
# ===============================
st.subheader(" Prioritas Perbaikan Fasilitas")

prioritas = df_filtered[
    (df_filtered["Skor Total"] <= 3) &
    (df_filtered["Rating"] >= 4)
].sort_values("Skor Total")

st.dataframe(
    prioritas[[
        "Nama Tempat",
        "Jenis Tempat",
        "Kota/Kabupaten",
        "Rating",
        "Skor Total"
    ]].head(10),
    use_container_width=True
)

st.markdown("""
**Insight:**  
Tempat ibadah pada daftar ini memiliki tingkat kepuasan pengguna yang baik,
namun belum didukung oleh fasilitas aksesibilitas dan informasi yang memadai.
""")

st.divider()

# ===============================
# KESIMPULAN AKHIR
# ===============================
st.subheader(" Kesimpulan Umum")

st.markdown("""
- Sistem berhasil mengidentifikasi **ketimpangan kualitas fasilitas** secara spasial
- **Rating bukan indikator tunggal** kualitas tempat ibadah
- Skor komposit memberikan dasar yang lebih objektif untuk evaluasi
- Analisis dinamis memungkinkan pengambilan keputusan berbasis wilayah
""")

st.success("✔ Analisis selesai. Silakan ubah filter untuk melihat insight per daerah.")
