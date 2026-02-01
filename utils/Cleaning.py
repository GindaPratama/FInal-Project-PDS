import pandas as pd
import re
import numpy as np
import unicodedata
import math



def cleaning_pipeline(df):
    df = pd.read_csv("Cleaning/DataMasterAll.csv")
    # Drop Duplicate
    df["Nama Tempat_clean"] = (
        df["Nama Tempat"]
        .str.lower()
        .str.strip()
    )

    df["Alamat_clean"] = (
        df["Alamat"]
        .str.lower()
        .str.strip()
    )

    df = df.drop_duplicates(
        subset=["Nama Tempat_clean", "Alamat_clean"]
    )

    df = df.drop(columns=["Nama Tempat_clean", "Alamat_clean"])

    sebelum = pd.read_csv("Cleaning/DataMasterAll.csv").shape[0]
    sesudah = df.shape[0]

    print("Record sebelum:", sebelum)
    print("Record sesudah :", sesudah)
    print("Duplikat dihapus:", sebelum - sesudah)

    # Normalisasi Tipe Tempat
    katolik_keywords = [
        "katolik", "katedral", "keuskupan"
    ]

    protestan_keywords = [
        "kristen", "protestan", "hkbp", "gki", "gpib",
        "gkj", "gkps", "gkp", "gbi", "gbit", "ifgf",
        "bethany", "gsja", "gbis", "gkkd"
    ]

    def normalize_type(row):
        tp = str(row["Jenis Tempat uc"]).lower()
        name = str(row["Nama Tempat"]).lower()

        if "masjid" in tp:
            return "Masjid"

        if "vihara" in tp:
            return "Vihara"

        if "pura" in tp:
            return "Pura"

        if "gereja" in tp:
            if any(k in name for k in katolik_keywords):
                return "Gereja Katolik"
            elif any(k in name for k in protestan_keywords):
                return "Gereja Protestan"
            else:
                return "Gereja Umum"

        return "Lainnya"

    df["Jenis Tempat"] = df.apply(normalize_type, axis=1)
    print("Drop lainnya:", df["Jenis Tempat"].value_counts().get('Lainnya',0))

    # drop yang Lainnya
    df = df[df["Jenis Tempat"] != "Lainnya"]
    df["Jenis Tempat"].value_counts()
    df[["Nama Tempat", "Jenis Tempat uc", "Jenis Tempat"]].head(10)

    # Cleaning Nama
    master = pd.read_csv("Cleaning/master_wilayah_jabar.csv")

    # Normalisasi master
    master["alias"] = master["alias"].str.lower()

    def extract_kota_kab_from_master(Alamat):
        if pd.isna(Alamat):
            return "Tidak diketahui"

        Alamat = Alamat.lower()
    

        for _, row in master.iterrows():
            # alias dipisah |
            patterns = row["alias"].split("|")

            for p in patterns:
                p = p.strip()
                if p and re.search(rf"\b{re.escape(p)}\b", Alamat):
                    return row["resmi"]

        return "Tidak diketahui"



    df["Kota/Kabupaten"] = df["Alamat"].apply(extract_kota_kab_from_master)
    df["Kota/Kabupaten"].value_counts()
    df[df["Kota/Kabupaten"] == "Tidak diketahui"][["Alamat"]].head(20)

    print("Unknown Place:", df["Kota/Kabupaten"].value_counts().get('Tidak diketahui',0))

    sebelum = len(df)
    df = df[df["Kota/Kabupaten"].str.strip().str.lower() != "tidak diketahui"]
    sesudah = len(df)

    print("Baris After Clean Kota:", sesudah)

    # Cleaning Jam Operasional

    def clean_jam_operasional(text):
        if pd.isna(text):
            return pd.Series([False, None, None, "Tidak diketahui"])

        text = str(text).lower().strip()

        # 24 jam
        if "24 jam" in text or "buka 24" in text:
            return pd.Series([True, "00:00", "23:59", "24 Jam"])

        # format jam umum: 05.00-22.00 / 05:00–22:00
        match = re.search(
            r'(\d{1,2})[.:](\d{2}).*?(\d{1,2})[.:](\d{2})',
            text
        )

        if match:
            open_time = f"{match.group(1).zfill(2)}:{match.group(2)}"
            close_time = f"{match.group(3).zfill(2)}:{match.group(4)}"

            # validasi logis jam
            if open_time < close_time:
                return pd.Series([False, open_time, close_time, "Normal"])
            else:
                return pd.Series([False, open_time, close_time, "Tidak konsisten"])

        return pd.Series([False, None, None, "Tidak konsisten"])

    df[[
        "24 Jam",
        "Jam Buka",
        "Jam Tutup",
        "Status Operasional"
    ]] = df["Jam Operasional"].apply(clean_jam_operasional)

    # Distribusi status jam operasional
    df["Status Operasional"].value_counts()

    # Contoh data bermasalah
    df[df["Status Operasional"] != "Normal"][[
        "Nama Tempat", "Jam Operasional", "Status Operasional"
    ]].head(10)

    df['Nama Tempat'] = df['Nama Tempat'].replace(
        to_replace=r'(?i)\bmesjid\b',
        value='Masjid',
        regex=True
    )

    df['Jam Buka'] = pd.to_datetime(df['Jam Buka'], format='%H:%M', errors='coerce')
    df['Jam Tutup'] = pd.to_datetime(df['Jam Tutup'], format='%H:%M', errors='coerce')

    mask_masjid = df['Nama Tempat'].str.contains(r'\bMasjid\b', na=False)

    df.loc[mask_masjid, 'Jam Buka'] = (
        df.loc[mask_masjid, 'Jam Buka']
        .fillna(pd.to_datetime('04:00', format='%H:%M'))
    )

    df.loc[mask_masjid, 'Jam Tutup'] = (
        df.loc[mask_masjid, 'Jam Tutup']
        .fillna(pd.to_datetime('22:00', format='%H:%M'))
    )

    mask_non_masjid = ~mask_masjid

    mean_open_time = df.loc[mask_non_masjid, 'Jam Buka'].mean()
    mean_close_time = df.loc[mask_non_masjid, 'Jam Tutup'].mean()

    df.loc[mask_non_masjid, 'Jam Buka'] = (
        df.loc[mask_non_masjid, 'Jam Buka']
        .fillna(mean_open_time)
    )
    df.loc[mask_non_masjid, 'Jam Tutup'] = (
        df.loc[mask_non_masjid, 'Jam Tutup']
        .fillna(mean_close_time)
    )
    df['Jam Buka'] = df['Jam Buka'].dt.strftime('%H:%M')
    df['Jam Tutup'] = df['Jam Tutup'].dt.strftime('%H:%M')

    df['Jam Buka'] = pd.to_datetime(df['Jam Buka'], format='%H:%M', errors='coerce')
    df['Jam Tutup'] = pd.to_datetime(df['Jam Tutup'], format='%H:%M', errors='coerce')

    df['Status Operasional'] = (
        df['Status Operasional']
        .astype(str)
        .str.lower()
        .str.strip()
    )

    mask_normal = (
        df['Jam Buka'].notna() &
        df['Jam Tutup'].notna() &
        (df['Jam Buka'] < df['Jam Tutup']) &
        (
            df['Status Operasional'].isin([
                'tidak diketahui',
                'unknown',
                '-',
                'nan',
                ''
            ])
        )
    )

    df.loc[mask_normal, 'Status Operasional'] = 'Normal'

    df.loc[
        (df['Jam Buka'] >= df['Jam Tutup']) &
        df['Jam Buka'].notna() &
        df['Jam Tutup'].notna(),
        'Status Operasional'
    ] = 'Tidak Konsisten'

    df['Jam Buka'] = df['Jam Buka'].dt.strftime('%H:%M')
    df['Jam Tutup'] = df['Jam Tutup'].dt.strftime('%H:%M')

    df['Status Operasional'] = (
        df['Status Operasional']
        .astype(str)
        .str.strip()
        .str.lower()
        .replace({
            'normal': 'Normal',
            'tidak diketahui': 'Tidak Diketahui',
            'tidak konsisten': 'Tidak Konsisten'
        })
    )



    #Cleaning Review
    df["Jumlah Review"] = (
        df["Jumlah Review"]
        .astype(str)
        .str.replace(".", "", regex=False)  # hapus pemisah ribuan
    )
    df["Jumlah Review"] = pd.to_numeric(df["Jumlah Review"], errors="coerce")
    print(len(df))

    # jumlah data sebelum
    sebelum = df.shape[0]
    # drop review < 50
    df = df[df["Jumlah Review"] >= 20]
    # jumlah data sesudah
    sesudah = df.shape[0]

    print("Record sebelum:", sebelum)
    print("Record sesudah :", sesudah)
    print("Record di-drop :", sebelum - sesudah)

    # Cleaning no tlp

    def extract_digits_only(val):
        if pd.isna(val):
            return np.nan

        # ambil semua digit, termasuk yang terpisah simbol aneh
        digits = re.findall(r"\d+", str(val))

        if not digits:
            return np.nan

        return "".join(digits)


    df["telepon_digits"] = df["telepon"].apply(extract_digits_only)


    # Normalisasi 0
    def normalize_phone_strict0(number):
        if pd.isna(number):
            return np.nan

        number = str(number)

        # 62xxxxxxxx → 0xxxxxxxx
        if number.startswith("62"):
            return "0" + number[2:]

        # valid jika sudah diawali 0
        if number.startswith("0"):
            return number

        # selain itu → kosongkan
        return np.nan


    df["Telepon"] = df["telepon_digits"].apply(normalize_phone_strict0)


    df = df.drop(columns=["telepon_digits"])

    df[["telepon", "Telepon"]].head(15)
    df["Telepon"].isna().mean()


    # Update Availability Telepon
    df["Ketersediaan Telepon"] = df["Telepon"].apply(
        lambda x: "Ada" if pd.notna(x) else "Tidak Ada"
    )

    df["Ketersediaan Telepon"].value_counts()
    df[df["Ketersediaan Telepon"] == "Ada"][["telepon", "Telepon"]].head(10)
    df[df["Ketersediaan Telepon"] == "Tidak Ada"][["telepon", "Telepon"]].head(10)

    # ==============================================================================
    # 2. LOGIC Aksesibilitas Difabel (USING NUMPY & PANDAS VECTORIZATION)
    # ==============================================================================

    # Cek keberadaan 3 fitur positif secara massal
    has_pintu = df['Aksesibilitas Difabel'].str.contains('Memiliki pintu masuk khusus pengguna kursi roda', case=False, na=False).astype(int)
    has_parkir = df['Aksesibilitas Difabel'].str.contains('Memiliki tempat parkir khusus pengguna kursi roda', case=False, na=False).astype(int)
    has_toilet = df['Aksesibilitas Difabel'].str.contains('Ada toilet khusus pengguna kursi roda', case=False, na=False).astype(int)
    has_tempatduduk = df['Aksesibilitas Difabel'].str.contains('Ada kursi khusus pengguna kursi roda', case=False, na=False).astype(int)

    # Hitung skor total
    df['skor_aksesibilitas_temp'] = has_pintu + has_parkir + has_toilet + has_tempatduduk

    # Cek fitur negatif (Jika ada 'Tidak memiliki...', skor paksa jadi 0)
    has_negative = df['Aksesibilitas Difabel'].str.contains('Tidak memiliki', case=False, na=False)
    has_negative2 = df['Aksesibilitas Difabel'].str.contains('Tidak ada', case=False, na=False)

    # Tentukan skor final menggunakan NumPy
    df['Skor Aksesibilitas'] = np.where(
        has_negative | has_negative2,
        0,
        df['skor_aksesibilitas_temp']
    )

    # Tentukan Label menggunakan np.select (Gaya Data Science banget)
    conditions = [
        df['Skor Aksesibilitas'] == 0,
        df['Skor Aksesibilitas'].between(1, 2),
        df['Skor Aksesibilitas'] == 3,
        df['Skor Aksesibilitas'] >= 4
    ]

    choices = [
        "Tidak Tersedia",
        "Aksesibilitas Difabel Terbatas",
        "Aksesibilitas Difabel Cukup Lengkap",
        "Aksesibilitas Difabel Sangat Lengkap"
    ]

    df['Status Aksesibilitas'] = np.select(
        conditions,
        choices,
        default="Tidak Tersedia"
    )

    # Hapus kolom temp
    df.drop(columns=['skor_aksesibilitas_temp'], inplace=True)


    # ==============================================================================
    # 3. LOGIC Alamat (USING PANDAS STR EXTRACT & REGEX)
    # ==============================================================================
    # Hapus Plus Code (e.g. 3JRQ+QC2) dan Kode Pos (5 digit) pake Regex massal
    # \b[A-Z0-9]{4}\+[A-Z0-9]{2,}\b -> pola Plus Code Google Maps
    # \b\d{5}\b -> pola Kode Pos Indonesia
    df['Alamat'] = df['Alamat'].str.replace(r'\b[A-Z0-9]{4}\+[A-Z0-9]{2,}\b', '', regex=True)
    df['Alamat'] = df['Alamat'].str.replace(r'\b\d{5}\b', '', regex=True)

    # Final touch: bersihkan sisa koma berlebih atau spasi ganda
    df['Alamat'] = df['Alamat'].str.replace(r',\s*,', ',', regex=True).str.strip(', ')

    provinsi_pattern = r"(?i)(?:,\s*)?\b(jawa\s+barat|west\s+java)\b"
    df["Alamat"] = df["Alamat"].astype(str)
    df["Alamat"] = df["Alamat"].str.replace(provinsi_pattern, "", regex=True)

    # Drop Kolom 
    df = df.drop(columns=[
        "Jenis Tempat uc",
        "Jam Operasional",
        "telepon",
        "Ketersediaan Akses"
    ])

    df["Aksesibilitas Difabel"] = df["Aksesibilitas Difabel"].replace("[]", "")

    df["Aksesibilitas Difabel"] = df["Aksesibilitas Difabel"].replace("", np.nan)

    df.info()
    df.head()

    # Jumlah data awal
    before = len(df)

    # Drop nama_tempat yang NaN atau kosong/spasi
    df = df[
        df["Nama Tempat"].notna() &
        (df["Nama Tempat"].str.strip() != "")
    ]

    # Jumlah data akhir
    after = len(df)

    # Log
    print(f"Jumlah data awal  : {before}")
    print(f"Jumlah data akhir : {after}")
    print(f"Data nama terhapus     : {before - after}")

    # Jumlah data awal
    before = len(df)

    # Drop Alamat yang NaN atau kosong/spasi
    df = df[
        df["Alamat"].notna() &
        (df["Alamat"].str.strip() != "")
    ]

    # Jumlah data akhir
    after = len(df)

    # Log
    print(f"Jumlah data awal  : {before}")
    print(f"Jumlah data akhir : {after}")
    print(f"Data Alamat terhapus     : {before - after}")

    # Jumlah data awal
    before = len(df)

    # Drop rating yang NaN atau kosong/spasi
    df = df[
        df["Rating"].notna() &
        (df["Rating"].str.strip() != "")
    ]

    # Jumlah data akhir
    after = len(df)

    # Log
    print(f"Jumlah data awal  : {before}")
    print(f"Jumlah data akhir : {after}")
    print(f"Data Rating terhapus     : {before - after}")

    # Jumlah data awal
    before = len(df)

    df = df[
        df["Jumlah Review"].notna() &
        (df["Jumlah Review"].astype(str).str.strip() != "")
    ]

    # Jumlah data akhir
    after = len(df)

    print(f"Jumlah data awal  : {before}")
    print(f"Jumlah data akhir : {after}")
    print(f"Data Review terhapus     : {before - after}")

    return df



