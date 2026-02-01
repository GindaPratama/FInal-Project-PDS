import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

from utils.scoring import calculate_score

st.set_page_config(page_title="GIS Tempat Ibadah", layout="wide")
st.title("GIS – 5 Tempat Ibadah Prioritas Jawa Barat")

# ===============================
# LOAD DATA
# ===============================
df = pd.read_csv("dataset\AfterCleaned.csv")
df.columns = df.columns.str.strip()   # WAJIB

df = calculate_score(df)

# ===============================
# NORMALISASI
# ===============================
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
df["Skor Total"] = pd.to_numeric(df["Skor Total"], errors="coerce").fillna(0)
df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce").fillna(0)

df = df.dropna(subset=["Latitude", "Longitude"])

# ===============================
# KATEGORI KONDISI
# ===============================
df["Kategori Kondisi"] = pd.cut(
    df["Skor Total"],
    bins=[-1, 3, 6, 100],
    labels=["Sangat Memerlukan Perbaikan", "Cukup", "Terbaik"]
)

# ===============================
# SIDEBAR FILTER
# ===============================
st.sidebar.header(" Filter")

selected_daerah = st.sidebar.selectbox(
    "Kota / Kabupaten",
    ["Semua"] + sorted(df["Kota/Kabupaten"].dropna().unique())
)

selected_jenis = st.sidebar.selectbox(
    "Jenis Tempat Ibadah",
    ["Semua"] + sorted(df["Jenis Tempat"].dropna().unique())
)

selected_kondisi = st.sidebar.radio(
    "Kategori",
    ["Terbaik", "Sangat Memerlukan Perbaikan"]
)

# ===============================
# FILTER DATA
# ===============================
filtered = df.copy()

if selected_daerah != "Semua":
    filtered = filtered[filtered["Kota/Kabupaten"] == selected_daerah]

if selected_jenis != "Semua":
    filtered = filtered[filtered["Jenis Tempat"] == selected_jenis]

filtered = filtered[filtered["Kategori Kondisi"] == selected_kondisi]

# ===============================
# SORT & TOP 5
# ===============================
if selected_kondisi == "Terbaik":
    top5 = filtered.sort_values("Skor Total", ascending=False).head(5)
else:
    top5 = filtered.sort_values("Skor Total", ascending=True).head(5)

# ===============================
# MAP (SELALU DIBUAT)
# ===============================
m = folium.Map(
    location=[-6.914744, 107.609810],
    zoom_start=8,
    tiles="CartoDB dark_matter"
)

# ===============================
# ADD MARKER (KALAU ADA DATA)
# ===============================
if not top5.empty:

    m.location = [
        top5["Latitude"].mean(),
        top5["Longitude"].mean()
    ]
    m.zoom_start = 11 if selected_daerah != "Semua" else 9

    for rank, (_, row) in enumerate(top5.iterrows(), start=1):

        color = "green" if selected_kondisi == "Terbaik" else "red"
        icon = "star" if selected_kondisi == "Terbaik" else "exclamation-sign"

        popup = f"""
        <b>#{rank} {row['Nama Tempat']}</b><br>
        Jenis: {row['Jenis Tempat']}<br>
        Daerah: {row['Kota/Kabupaten']}<br>
        Rating: {row['Rating']} <br>
        Skor Total: <b>{row['Skor Total']}</b><br>
        Aksesibilitas: {row['Status Aksesibilitas']}
        """

        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=popup,
            tooltip=f"#{rank} {row['Nama Tempat']}",
            icon=folium.Icon(color=color, icon=icon)
        ).add_to(m)

else:
    st.warning("⚠️ Tidak ada data sesuai filter yang dipilih.")

# ===============================
# RENDER MAP
# ===============================
st_folium(m, width=1200, height=550)

# ===============================
# TABLE
# ===============================
st.subheader(" 5 Tempat Ibadah Prioritas")

if not top5.empty:
    st.dataframe(
        top5[[
            "Nama Tempat",
            "Jenis Tempat",
            "Kota/Kabupaten",
            "Rating",
            "Skor Total",
            "Kategori Kondisi"
        ]],
        use_container_width=True
    )

# ===============================
# INSIGHT
# ===============================
st.subheader(" Insight")

st.markdown("""
 **Hasil visualisasi GIS menunjukkan bahwa:**

- Tempat ibadah dengan **rating tinggi belum tentu memiliki skor total tinggi**
- **Aksesibilitas difabel dan kelengkapan informasi** menjadi faktor pembeda utama
- Masih terdapat wilayah dengan fasilitas publik yang **memerlukan intervensi prioritas**

 **Rekomendasi:**
- Fokus peningkatan fasilitas difabel
- Standarisasi informasi publik (website & kontak)
- Gunakan pendekatan spasial dalam pemerataan kualitas
""")
