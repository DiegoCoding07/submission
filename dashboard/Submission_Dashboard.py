import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Style untuk visualisasi
sns.set(style='dark')

# Header utama dashboard
st.title("E-Commerce Public Data Analysis")
st.write("Dashboard untuk analisis data publik E-Commerce.")

# Mengambil data utama
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
data_url = "https://drive.google.com/uc?id=1hrfe_A9RtTg3_Cin4rZUWpM2xQA7v_hr"
all_data = pd.read_csv(data_url)

# Preprocessing data
def preprocess_data(df):
    for col in datetime_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    df.sort_values(by="order_approved_at", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

all_data = preprocess_data(all_data)

# Menentukan rentang tanggal
min_date = all_data["order_approved_at"].min()
max_date = all_data["order_approved_at"].max()

# Sidebar untuk filter
with st.sidebar:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://github.com/DiegoCoding07/submission/raw/main/dashboard/Dashboard_Logo.png", width=100)
    with col2:
        st.write(' ')
    with col3:
        st.write(' ')
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

filtered_data = all_data[(all_data["order_approved_at"] >= pd.Timestamp(start_date)) & 
                         (all_data["order_approved_at"] <= pd.Timestamp(end_date))]

# Fungsi untuk membuat daily orders dataframe
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    }).reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    return daily_orders_df

daily_orders_df = create_daily_orders_df(filtered_data)

# Fungsi untuk total pendapatan per kategori produk
def revenue_by_category(df):
    category_revenue = df.groupby("product_category_name_english")["payment_value"].sum().reset_index()
    category_revenue = category_revenue.sort_values(by="payment_value", ascending=False)
    return category_revenue

category_revenue_df = revenue_by_category(filtered_data)

# Fungsi untuk distribusi skor ulasan
def review_score_distribution(df):
    review_scores = df['review_score'].value_counts().sort_index()
    return review_scores

review_scores = review_score_distribution(filtered_data)

# Fungsi untuk pesanan mingguan dan bulanan
def create_weekly_monthly_orders_df(df):
    weekly_orders_df = df.resample(rule='W', on='order_approved_at').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    }).reset_index()
    weekly_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    monthly_orders_df = df.resample(rule='M', on='order_approved_at').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    }).reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    return weekly_orders_df, monthly_orders_df

weekly_orders_df, monthly_orders_df = create_weekly_monthly_orders_df(filtered_data)

# Fungsi untuk analisis pesanan per pelanggan
def customer_purchase_analysis(df):
    customer_data = df.groupby("customer_unique_id").agg({
        "order_id": "nunique",
        "payment_value": "sum",
        "order_approved_at": ["min", "max"]
    }).reset_index()
    customer_data.columns = ["customer_unique_id", "order_count", "total_spent", "first_purchase", "last_purchase"]
    return customer_data

customer_data = customer_purchase_analysis(filtered_data)

# Total Pesanan dan Pendapatan
st.subheader("Ikhtisar Statistik")
col1, col2 = st.columns(2)
with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.metric("Total Pesanan", int(total_order))
with col2:
    total_revenue = daily_orders_df["revenue"].sum()
    st.metric("Total Pendapatan", format_currency(total_revenue, 'IDR', locale='id_ID'))

# Grafik pesanan harian
st.subheader("Pesanan Harian")
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(
    x=daily_orders_df["order_approved_at"],
    y=daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.set_title("Total Pesanan Harian", fontsize=16)
ax.set_xlabel("Tanggal", fontsize=12)
ax.set_ylabel("Jumlah Pesanan", fontsize=12)
ax.tick_params(axis="x", rotation=45)
st.pyplot(fig)

# Grafik pesanan mingguan
st.subheader("Pesanan Mingguan")
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(
    x=weekly_orders_df["order_approved_at"],
    y=weekly_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#42A5F5"
)
ax.set_title("Total Pesanan Mingguan", fontsize=16)
ax.set_xlabel("Tanggal", fontsize=12)
ax.set_ylabel("Jumlah Pesanan", fontsize=12)
ax.tick_params(axis="x", rotation=45)
st.pyplot(fig)

# Grafik pesanan bulanan
st.subheader("Pesanan Bulanan")
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(
    x=monthly_orders_df["order_approved_at"],
    y=monthly_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#1E88E5"
)
ax.set_title("Total Pesanan Bulanan", fontsize=16)
ax.set_xlabel("Tanggal", fontsize=12)
ax.set_ylabel("Jumlah Pesanan", fontsize=12)
ax.tick_params(axis="x", rotation=45)
st.pyplot(fig)

# Grafik pendapatan per kategori
st.subheader("Pendapatan Berdasarkan Kategori Produk")
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(
    x=category_revenue_df["payment_value"].head(10),
    y=category_revenue_df["product_category_name_english"].head(10),
    palette="Blues_r"
)
ax.set_title("Top 10 Kategori Produk Berdasarkan Pendapatan", fontsize=16)
ax.set_xlabel("Pendapatan", fontsize=12)
ax.set_ylabel("Kategori Produk", fontsize=12)
st.pyplot(fig)

# Grafik distribusi skor ulasan
st.subheader("Distribusi Skor Ulasan")
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(
    x=review_scores.index,
    y=review_scores.values,
    palette="Set2"
)
ax.set_title("Distribusi Skor Ulasan", fontsize=16)
ax.set_xlabel("Skor Ulasan", fontsize=12)
ax.set_ylabel("Jumlah Ulasan", fontsize=12)
st.pyplot(fig)
