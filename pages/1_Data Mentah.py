import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Raw Data",
    layout="wide"
)

st.title("Raw Data Tempat Ibadah")
st.caption("Data mentah hasil scrapping, belum melalui proses pembersihan atau scoring")

# ===============================
# LOAD RAW DATA
# ===============================
@st.cache_data
def load_raw_data():
    return pd.read_csv("Cleaning/DataMasterAll.csv")

df_raw = load_raw_data()

# ===============================
# INFO DATASET
# ===============================
st.subheader("Informasi Dataset")

col1, col2, col3 = st.columnst = st.columns(3)

with col1:
    st.metric("Jumlah Baris", df_raw.shape[0])

with col2:
    st.metric("Jumlah Kolom", df_raw.shape[1])

with col3:
    st.metric("Ukuran Data", f"{round(df_raw.memory_usage().sum() / 1024, 2)} KB")

st.divider()

# ===============================
# STRUKTUR KOLOM
# ===============================
st.subheader("Struktur Kolom")

struktur = pd.DataFrame({
    "Nama Kolom": df_raw.columns,
    "Tipe Data": df_raw.dtypes.astype(str)
})

st.dataframe(struktur, use_container_width=True)

st.divider()

# ===============================
# FILTER SEDERHANA (EKSPLORASI)
# ===============================
st.subheader("Eksplorasi Data")


selected_jenis = st.multiselect(
        "Filter Jenis Tempat",
        sorted(df_raw["Jenis Tempat uc"].dropna().unique())
    )

df_view = df_raw.copy()


if selected_jenis:
    df_view = df_view[df_view["Jenis Tempat uc"].isin(selected_jenis)]

st.caption(f"Menampilkan {len(df_view)} data")

st.dataframe(df_view, use_container_width=True, height=500)

st.divider()

# ===============================
# DATA KOSONG
# ===============================
st.subheader("⚠️ Data Kosong (Missing Values)")

missing = (
    df_raw.isnull()
    .sum()
    .reset_index()
    .rename(columns={"index": "Kolom", 0: "Jumlah Kosong"})
)

missing = missing[missing["Jumlah Kosong"] > 0]

if missing.empty:
    st.success("Tidak ada data kosong")
else:
    st.dataframe(missing, use_container_width=True)

st.divider()

# ===============================
# DOWNLOAD
# ===============================
st.subheader("⬇Unduh Data Mentah")

st.download_button(
    label="Download Raw Data (CSV)",
    data=df_raw.to_csv(index=False),
    file_name="raw_tempat_ibadah.csv",
    mime="text/csv"
)

st.info(
    "Halaman ini menampilkan data mentah apa adanya. "
    "Data akan diproses lebih lanjut pada tahap pembersihan dan analisis."
)
