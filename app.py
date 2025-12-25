import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Araba101 KM-Fiyat Aracı", layout="wide")

st.title("🚗 Araba101 KM-Fiyat Aracı")
st.write("CSV yükle ➜ Marka & model seç ➜ KM / Yıllık KM / Fiyat analiz grafiği gör")

mevcut_yil = datetime.now().year

uploaded_file = st.file_uploader("📂 CSV dosyası yükle (Sütunlar: marka,model,km,fiyat,arac_yili)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    required_cols = {"marka", "model", "km", "fiyat", "arac_yili"}
    if not required_cols.issubset(df.columns):
        st.error(f"CSV dosyan şu sütunları içermeli: {required_cols}")
    else:
        marka_sec = st.selectbox("Marka seç", sorted(df["marka"].unique()))
        model_sec = st.selectbox("Model seç",
                                 sorted(df[df["marka"] == marka_sec]["model"].unique()))

        df_filtre = df[(df["marka"] == marka_sec) & (df["model"] == model_sec)].copy()
        df_filtre["yillik_km"] = df_filtre["km"] / (mevcut_yil - df_filtre["arac_yili"]).clip(lower=1)

        st.write(f"Toplam ilan: **{len(df_filtre)}**")

        max_yillik = int(df_filtre["yillik_km"].quantile(0.95))
        yillik_limit = st.slider("Aykırı yıllık km filtrele", 5000, max_yillik, value=max_yillik)
        df_filtre = df_filtre[df_filtre["yillik_km"] <= yillik_limit]

        if len(df_filtre) > 5:
            ort = df_filtre["fiyat"].mean()
            medyan = df_filtre["fiyat"].median()

            st.metric("Ortalama Fiyat (₺)", f"{ort:,.0f}")
            st.metric("Medyan Fiyat (₺)", f"{medyan:,.0f}")

            fig1 = px.scatter(df_filtre, x="km", y="fiyat",
                              color="yillik_km",
                              title=f"{marka_sec} {model_sec} — KM vs Fiyat",
                              hover_data=["arac_yili","yillik_km"],
                              trendline="ols")
            fig1.update_layout(xaxis_title="Toplam KM", yaxis_title="Fiyat (₺)")
            st.plotly_chart(fig1, use_container_width=True)

            fig2 = px.scatter(df_filtre, x="yillik_km", y="fiyat",
                              title=f"{marka_sec} {model_sec} — Yıllık KM vs Fiyat",
                              hover_data=["arac_yili","km"],
                              trendline="ols")
            fig2.update_layout(xaxis_title="Yıllık KM", yaxis_title="Fiyat (₺)")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("Grafik için en az 6 ilan gerekli.")
else:
    st.info("Başlamak için CSV yükle.")
