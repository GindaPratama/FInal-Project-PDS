import pandas as pd
import streamlit as st
from utils.Cleaning import cleaning_pipeline

st.set_page_config(
    page_title="Data Cleaning",
    layout="wide"
)

st.title("Data Cleaning & Validasi")
st.caption("Halaman ini menampilkan proses pembersihan dan normalisasi data sebelum digunakan dalam sistem analisis.")

# ===============================
# LOAD DATA
# ===============================
df_raw = pd.read_csv("Cleaning/DataMasterAll.csv")
df_cleaned = cleaning_pipeline(df_raw.copy())

# ===============================
# SECTION 1: OVERVIEW
# ===============================
st.subheader("Ringkasan Dataset")

col1, col2, col3 = st.columns(3)
col1.metric("Jumlah Baris (Raw)", df_raw.shape[0])
col2.metric("Jumlah Kolom (Raw)", df_raw.shape[1])
col3.metric("Jumlah Kolom (Setelah Cleaning)", df_cleaned.shape[1])

st.divider()

# ===============================
# SECTION 2: PREVIEW DATA
# ===============================
st.subheader("Preview Data")

tab1, tab2 = st.tabs(["Data Mentah", "Data Setelah Cleaning"])

with tab1:
    st.dataframe(df_raw.head(10), use_container_width=True)

with tab2:
    st.dataframe(df_cleaned.head(10), use_container_width=True)

# ===============================
# SECTION 3: STRUKTUR KOLOM
# ===============================
st.subheader("Struktur Kolom Dataset")

col_raw, col_clean = st.columns(2)

with col_raw:
    st.markdown("### Sebelum Cleaning")
    schema_raw = pd.DataFrame({
        "Nama Kolom": df_raw.columns,
        "Tipe Data": df_raw.dtypes.astype(str)
    })
    st.dataframe(schema_raw, use_container_width=True)

with col_clean:
    st.markdown("### Setelah Cleaning")
    schema_clean = pd.DataFrame({
        "Nama Kolom": df_cleaned.columns,
        "Tipe Data": df_cleaned.dtypes.astype(str)
    })
    st.dataframe(schema_clean, use_container_width=True)

# ===============================
# SECTION 4: PERUBAHAN KOLOM
# ===============================
st.subheader("Perubahan Setelah Cleaning")

added_cols = set(df_cleaned.columns) - set(df_raw.columns)
removed_cols = set(df_raw.columns) - set(df_cleaned.columns)
common_cols = set(df_raw.columns).intersection(set(df_cleaned.columns))

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("####  Kolom Ditambahkan")
    if added_cols:
        st.write(list(added_cols))
    else:
        st.write("Tidak ada")

with col_b:
    st.markdown("####  Kolom Dihapus")
    if removed_cols:
        st.write(list(removed_cols))
    else:
        st.write("Tidak ada")

with col_c:
    st.markdown("####  Kolom Dinormalisasi")
    st.write(sorted(list(common_cols)))

# ===============================
# SECTION 5: DAMPAK CLEANING
# ===============================
st.subheader(" Dampak Cleaning (Ringkas)")

impact = pd.DataFrame({
    "Kolom": df_cleaned.columns,
    "Jumlah Null (Sebelum)": df_raw.reindex(columns=df_cleaned.columns).isna().sum().values,
    "Jumlah Null (Sesudah)": df_cleaned.isna().sum().values
})

st.dataframe(impact, use_container_width=True)

st.info(
    "Cleaning difokuskan pada normalisasi nilai kategorikal, penanganan nilai kosong, "
    "serta penyesuaian format data agar siap digunakan pada proses analisis dan visualisasi."
)

# ===============================
# SECTION 6: DOWNLOAD
# ===============================
st.subheader("⬇ Unduh Data Bersih")

st.download_button(
    label="Download AfterCleaned.csv",
    data=df_cleaned.to_csv(index=False),
    file_name="AfterCleaned.csv",
    mime="text/csv"
)
