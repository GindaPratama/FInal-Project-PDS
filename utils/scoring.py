import numpy as np
import pandas as pd

def calculate_score(df):
    df = df.copy()

    # ===============================
    # NORMALISASI DATA
    # ===============================

    # Skor aksesibilitas (0–4) langsung
    df["Skor Aksesibilitas"] = df["Skor Aksesibilitas"].fillna(0)

    # 24 Jam → 1 / 0
    df["24 Jam"] = df["24 Jam"].astype(str).str.lower().isin(["ya", "1", "true"]).astype(int)

    # Website → string "tersedia"
    df["Website"] = df["Website"].astype(str).str.strip().str.lower()
    df["Website"] = (df["Website"] == "tersedia").astype(int)

    # Telepon → NOT NULL (numeric)
    df["Telepon"] = df["Telepon"].notna().astype(int)

    # Review & Rating
    df["Jumlah Review"] = df["Jumlah Review"].fillna(0)
    df["Rating"] = (
        df["Rating"]
        .astype(str)
        .str.replace(",", ".", regex=False)   # 4,6 → 4.6
        .str.extract(r"(\d+\.?\d*)")[0]        # ambil angka saja
    )

    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce").fillna(0)

    # ===============================
    # HITUNG SKOR TOTAL
    # ===============================
    df["Skor Total"] = (
        df["Skor Aksesibilitas"] +
        df["24 Jam"] * 1 +
        df["Website"] * 1 +
        df["Telepon"] * 1 +
        np.where(df["Jumlah Review"] >= 500, 2, 0) +
        np.where(df["Rating"] > 4.5, 1, 0)
    )

    return df
