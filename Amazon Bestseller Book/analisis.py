import streamlit as st
st.set_page_config(page_title="Analisis Buku Bestseller", layout="wide")

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("bestsellers book.csv", delimiter=';', encoding='latin1')

df = load_data()

# Halaman utama
st.title("📚 Analisis Data Buku Bestseller Amazon")
st.markdown("Aplikasi ini menampilkan analisis eksploratif dari data buku terlaris berdasarkan rating, ulasan, harga, dan genre.")

# Tampilkan data mentah
with st.expander("🔍 Lihat Data Mentah"):
    st.dataframe(df.reset_index(drop=True))

# Sidebar filter
st.sidebar.header("🔎 Filter Data")
years = sorted(df['Year'].unique())
genres = df['Genre'].unique()

# Default-nya semua tahun dan genre terpilih
selected_year = st.sidebar.multiselect("Pilih Tahun", years, default=years)
selected_genre = st.sidebar.multiselect("Pilih Genre", genres, default=genres)

# Validasi jika user sengaja mengosongkan filter
if not selected_year:
    st.warning("⚠️ Silakan pilih minimal satu **tahun** di sidebar.")
elif not selected_genre:
    st.warning("⚠️ Silakan pilih minimal satu **genre** di sidebar.")
else:
    filtered_df = df[(df['Year'].isin(selected_year)) & (df['Genre'].isin(selected_genre))]


    # 📚 Distribusi Genre
    st.subheader("📚 Distribusi Buku per Genre")
    genre_count = filtered_df['Genre'].value_counts()
    st.plotly_chart(px.bar(
        genre_count, 
        x=genre_count.index, 
        y=genre_count.values,
        labels={'x': 'Genre', 'y': 'Jumlah Buku'}, 
        title="Jumlah Buku per Genre"))

    # ⭐ Distribusi Rating
    st.subheader("⭐ Distribusi User Rating")
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.histplot(filtered_df['User Rating'], bins=10, kde=True, ax=ax, color='skyblue')
    ax.set_xlabel("Rating")
    ax.set_ylabel("Jumlah Buku")
    st.pyplot(fig)

    # 💰 Rata-rata Harga per Genre
    st.subheader("💰 Rata-rata Harga per Genre")
    avg_price = filtered_df.groupby("Genre")['Price'].mean().reset_index()
    fig = px.bar(avg_price, x='Genre', y='Price', text='Price', title="Rata-Rata Harga Buku per Genre")
    fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
    fig.update_layout(yaxis_title='Harga (USD)')
    st.plotly_chart(fig)

    # 📦 Distribusi Harga Buku per Genre - violin plot
    st.subheader("📦 Distribusi Harga Buku per Genre (Violin Plot)")
    fig_violin, ax_violin = plt.subplots(figsize=(8, 5))
    sns.violinplot(data=filtered_df, x="Genre", y="Price", palette="Set2", ax=ax_violin)
    ax_violin.set_title("Distribusi Harga Buku Berdasarkan Genre")
    ax_violin.set_ylabel("Harga Buku (USD)")
    st.pyplot(fig_violin)

    # 🏆 Buku dengan Rating Tertinggi
    st.subheader("🏆 Buku dengan Rating Tertinggi")
    top_rating = filtered_df.sort_values(by="User Rating", ascending=False).drop_duplicates(subset=["Name"]).head(5)
    top_rating = top_rating.reset_index(drop=True)
    top_rating.index += 1
    st.dataframe(top_rating[["Name", "Author", "User Rating", "Reviews", "Price"]])

    # 🔥 Buku dengan Review Terbanyak
    st.subheader("🔥 Buku dengan Review Terbanyak")
    top_reviews = filtered_df.sort_values(by="Reviews", ascending=False).drop_duplicates(subset=["Name"]).head(5)
    top_reviews = top_reviews.reset_index(drop=True)
    top_reviews.index += 1
    st.dataframe(top_reviews[["Name", "Author", "Reviews", "User Rating", "Price"]])

    # 📈 Tren Jumlah Buku Terbit per Tahun
    st.subheader("📈 Tren Jumlah Buku Terbit per Tahun")
    book_year_trend = filtered_df['Year'].value_counts().sort_index().reset_index()
    book_year_trend.columns = ['Year', 'Jumlah Buku']
    st.plotly_chart(px.bar(book_year_trend, x='Year', y='Jumlah Buku', text='Jumlah Buku',
                        title="Jumlah Buku Terbit per Tahun"))

    # ✍️ Penulis dengan Buku Terbanyak
    st.subheader("✍️ Penulis dengan Buku Terbanyak")
    top_authors = filtered_df['Author'].value_counts().head(10).reset_index()
    top_authors.columns = ['Author', 'Jumlah Buku']
    st.plotly_chart(px.bar(top_authors, x='Author', y='Jumlah Buku', text='Jumlah Buku',
                        title='10 Penulis dengan Jumlah Buku Terbanyak di Bestseller'))

    # Korelasi Rating vs. Review (interaktif dan kesimpulan dinamis)
    st.subheader("📊 Hubungan antara Rating, Review, dan Harga Buku")

    korelasi_df = filtered_df.copy()
    korelasi_df['Harga Buku'] = korelasi_df['Price']
    korelasi_df['Jumlah Review'] = korelasi_df['Reviews']

    # Scatter Plot
    fig = px.scatter(
        korelasi_df, 
        x='User Rating', 
        y='Jumlah Review', 
        color='Harga Buku', 
        size='Harga Buku', 
        hover_data=['Name', 'Author', 'Price'],
        title="Korelasi antara Rating, Jumlah Review, dan Harga Buku",
        labels={"User Rating": "Rating", "Jumlah Review": "Review"}
    )
    fig.update_layout(coloraxis_colorbar=dict(title="Harga Buku (USD)"))
    st.plotly_chart(fig)

    # 💬 Analisis Dinamis Berdasarkan Filter
    avg_rating = korelasi_df['User Rating'].mean()
    avg_review = korelasi_df['Jumlah Review'].mean()
    avg_price = korelasi_df['Harga Buku'].mean()

    top_book = korelasi_df.sort_values(by=["User Rating", "Jumlah Review"], ascending=False).iloc[0]

    st.markdown("### 📌 Interpretasi Berdasarkan Data Terfilter")
    st.markdown(f"""
    - Rata-rata rating buku: **{avg_rating:.2f}**
    - Rata-rata jumlah review: **{avg_review:,.0f}**
    - Rata-rata harga buku: **${avg_price:.2f}**
    - Buku terpopuler saat ini:
        - **{top_book['Name']}** oleh **{top_book['Author']}**
        - Rating: **{top_book['User Rating']}**, Review: **{top_book['Jumlah Review']:,}**, Harga: **${top_book['Harga Buku']:.2f}**
    
    **Kesimpulan:** Buku dengan **rating tinggi** dan **jumlah review banyak** cenderung populer, terlepas dari harga buku yang bisa bervariasi.
    """)

    # 🧠 Kesimpulan Akhir
    st.subheader("🧠 Kesimpulan Analisis Data")
    st.markdown("""
    - Genre **Non Fiction** lebih banyak dibanding Fiction.
    - Harga buku mayoritas antara **$5 – $20**.
    - Buku dengan rating tinggi (>4.8) seringkali juga mendapat banyak review.
    - Penulis seperti **Jeff Kinney** dan **Suzanne Collins** sangat produktif.
    - Tidak selalu ada korelasi antara harga dan rating — buku murah bisa sangat populer.

    📌 Buku bestseller lebih dipengaruhi **kualitas isi dan popularitas**, bukan sekadar harga.
    """)

# Footer
st.markdown("---")
st.markdown("Dibuat oleh: **Irgi Ahmad Alfarizi** | Dataset: *Amazon Bestseller Books*")
