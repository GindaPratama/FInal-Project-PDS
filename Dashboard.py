import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Aksesibilitas Tempat Ibadah Jawa Barat",
    layout="wide"
)

# CSS dark
st.markdown("""
<style>
.stApp { background-color: #0e1117; color: #eaeaea; }
</style>
""", unsafe_allow_html=True)

# ===== LOAD DATA =====
df = pd.read_csv("dataset/AfterCleaned.csv")
df["Rating"] = (
    df["Rating"].astype(str)
    .str.replace(",", ".", regex=False)
    .astype(float)
)

# ===== DASHBOARD CONTENT =====
st.title("Ketersediaan Informasi dan Aksesibilitas Difabel Tempat Ibadah Jawa Barat")

# (lanjutkan KPI, chart, insight, kesimpulan — sama persis seperti sebelumnya)
import streamlit as st
import pandas as pd
import plotly.express as px

# ================= LOAD DATA =================
df = pd.read_csv("dataset/AfterCleaned.csv")

df["Rating"] = (
    df["Rating"]
    .astype(str)
    .str.replace(",", ".", regex=False)
    .astype(float)
)

# ================= HEADER =================
st.title("Dashboard")
st.caption(
    "Dashboard ini menyajikan analisis aksesibilitas difabel dan kualitas informasi "
    "tempat ibadah di Provinsi Jawa Barat berdasarkan data Google Maps."
)

st.divider()

# ================= KPI =================
total = df.shape[0]
ramah = df[df["Skor Aksesibilitas"] > 0].shape[0]
info_lengkap = df[
    (df["Website"] == "Ada") &
    (df["Ketersediaan Telepon"] == "Ada")
].shape[0]
daerah = df["Kota/Kabupaten"].nunique()

c1, c2, c3, c4 = st.columns(4)

def card(col, title, value):
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

card(c1, "Total Tempat Ibadah", total)
card(c2, "Ramah Difabel", ramah)
card(c3, "Informasi Lengkap", info_lengkap)
card(c4, "Kab/Kota", daerah)

st.divider()

# ================= CHART 1 =================
st.subheader("Distribusi Skor Aksesibilitas Difabel")

# pastikan semua skor 0–4 muncul, walaupun jumlahnya 0
skor_count = (
    df["Skor Aksesibilitas"]
    .value_counts()
    .reindex([0, 1, 2, 3, 4], fill_value=0)
    .reset_index()
)

skor_count.columns = ["Skor", "Jumlah"]

fig1 = px.bar(
    skor_count,
    x="Skor",
    y="Jumlah",
    text="Jumlah",
    title="Sebaran Skor Aksesibilitas (0–4)",
    template="plotly_dark"
)

fig1.update_traces(
    marker_color="#4C78A8",
    textposition="outside"
)

fig1.update_layout(
    xaxis=dict(
        tickmode="array",
        tickvals=[0, 1, 2, 3, 4]
    ),
    yaxis_title="Jumlah Tempat Ibadah",
    xaxis_title="Skor Aksesibilitas",
    title_x=0.5
)

st.plotly_chart(fig1, use_container_width=True)


# ===== KESIMPULAN & REKOMENDASI CHART 1 =====
total_tempat = df.shape[0]
skor_0 = (df["Skor Aksesibilitas"] == 0).sum()
skor_rendah = (df["Skor Aksesibilitas"] <= 1).sum()

st.markdown("###  Kesimpulan")
st.markdown(
    f"""
    Mayoritas tempat ibadah di Jawa Barat masih berada pada tingkat aksesibilitas rendah.
    Sebanyak **{skor_rendah} dari {total_tempat} tempat ibadah**
    memiliki skor aksesibilitas **0–1**, yang menunjukkan minimnya fasilitas pendukung
    bagi penyandang disabilitas.
    """
)

st.markdown("###  Rekomendasi")
st.markdown(
    """
    - Fokuskan program peningkatan aksesibilitas pada tempat ibadah dengan skor 0 dan 1.
    - Prioritaskan penyediaan fasilitas dasar seperti jalur landai (ramp) dan akses masuk yang aman.
    - Jadikan skor aksesibilitas sebagai indikator evaluasi layanan publik keagamaan.
    """
)


# ================= CHART 2 =================
st.subheader("Perbandingan Aksesibilitas Antar Daerah")

akses_daerah = (
    df.assign(ramah=df["Skor Aksesibilitas"] > 0)
    .groupby("Kota/Kabupaten")["ramah"]
    .mean()
    .sort_values(ascending=False)
)

top5 = akses_daerah.head(5).reset_index()
bottom5 = akses_daerah.tail(5).reset_index()

compare = pd.concat([top5, bottom5])

fig3 = px.bar(
    compare,
    x="ramah",
    y="Kota/Kabupaten",
    orientation="h",
    text=compare["ramah"].apply(lambda x: f"{x:.0%}"),
    title="Top 5 vs Bottom 5 Aksesibilitas Difabel",
    template="plotly_dark"
)

fig3.update_traces(marker_color="#59A14F")
fig3.update_layout(
    xaxis_title="Persentase Tempat Ibadah Ramah Difabel",
    yaxis_title="",
    title_x=0.5
)

st.plotly_chart(fig3, use_container_width=True)

# ===== KESIMPULAN & REKOMENDASI CHART 3 =====
best_daerah = top5.iloc[0]
worst_daerah = bottom5.iloc[-1]

st.markdown("### Kesimpulan")
st.markdown(
    f"""
    Terdapat kesenjangan yang signifikan dalam tingkat aksesibilitas antar daerah di Jawa Barat.
    **{best_daerah['Kota/Kabupaten']}** menjadi daerah dengan tingkat aksesibilitas tertinggi
    (**{best_daerah['ramah']:.0%}**), sementara **{worst_daerah['Kota/Kabupaten']}**
    memiliki tingkat aksesibilitas terendah.
    """
)

st.markdown("### Rekomendasi")
st.markdown(
    """
    - Jadikan daerah dengan performa terbaik sebagai model praktik baik (best practice).
    - Prioritaskan alokasi anggaran dan program peningkatan aksesibilitas pada daerah tertinggal.
    - Lakukan monitoring berkala untuk memastikan pemerataan fasilitas aksesibilitas.
    """
)



# ================= INSIGHT =================
st.info(
    f"Daerah dengan aksesibilitas tertinggi: **{top5.iloc[0]['Kota/Kabupaten']}** "
    f"({top5.iloc[0]['ramah']:.0%}). "
    f"Sebaliknya, daerah dengan aksesibilitas terendah adalah "
    f"**{bottom5.iloc[-1]['Kota/Kabupaten']}**."
)

# ================= CHART 3 =================
st.subheader("Perbandingan Ketersediaan Informasi Website dan Telepon")

# ===============================
# DATA PREPARATION (AMAN)
# ===============================
df["Website"] = df["Website"].astype(str).str.strip().str.lower()

total_data = len(df)

# ===============================
# AGREGASI DATA (LOGIKA VALID CSV)
# ===============================
# Website berdasarkan STRING
website_tersedia = (df["Website"] == "tersedia").sum()
website_tidak = total_data - website_tersedia

# Telepon berdasarkan NOT NULL (NUMERIC)
telepon_tersedia = df["Telepon"].notna().sum()
telepon_tidak = total_data - telepon_tersedia

kontak_df = pd.DataFrame({
    "Jenis Informasi": ["Website", "Telepon"],
    "Tersedia": [website_tersedia, telepon_tersedia],
    "Tidak Tersedia": [website_tidak, telepon_tidak]
})

kontak_long = kontak_df.melt(
    id_vars="Jenis Informasi",
    var_name="Status",
    value_name="Jumlah"
)

# ===============================
# VISUALISASI
# ===============================
fig2 = px.bar(
    kontak_long,
    x="Jenis Informasi",
    y="Jumlah",
    color="Status",
    barmode="group",
    text="Jumlah",
    template="plotly_dark",
    title="Perbandingan Ketersediaan Informasi Website dan Telepon",
    color_discrete_map={
        "Tersedia": "#00E676",
        "Tidak Tersedia": "#FF5252"
    }
)

fig2.update_traces(textposition="outside")

fig2.update_layout(
    title_x=0.5,
    xaxis_title="",
    yaxis_title="Jumlah Tempat Ibadah",
    bargap=0.35,
    font=dict(size=13)
)

st.plotly_chart(fig2, use_container_width=True)

# ===============================
# KESIMPULAN
# ===============================
st.markdown("### Kesimpulan")
st.markdown("""
Ketersediaan informasi melalui **telepon jauh lebih tinggi dibandingkan website**.
Hal ini menunjukkan bahwa mayoritas tempat ibadah di Jawa Barat masih mengandalkan
komunikasi langsung, sementara pemanfaatan media digital belum optimal.
""")

# ===============================
# REKOMENDASI
# ===============================
st.markdown("### Rekomendasi")
st.markdown("""
- Perlu peningkatan penyediaan **website resmi** sebagai sumber informasi utama
- Website dapat digunakan untuk:
  - Menyediakan informasi fasilitas aksesibilitas difabel
  - Memberikan akses informasi selama 24 jam
  - Mendukung teknologi bantu (screen reader, peta interaktif)
- Digitalisasi informasi menjadi kunci pemerataan layanan publik yang inklusif
""")

