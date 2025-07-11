import os
import gdown

# Create model directory if it doesn't exist
if not os.path.exists("model"):
    os.makedirs("model")

# Download the similarity.pkl file from Google Drive if it's missing
file_path = "model/similarity.pkl"
if not os.path.exists(file_path):
    gdown.download(
        "https://drive.google.com/uc?id=19eihpBmQ1fC-acyxvuvUI3MWuXVXKwiY",
        file_path,
        quiet=False
    )



import streamlit as st
import recommender  # Your Python file with recommend() logic

# Set the title of the web app
st.title("🎬 Movie Recommender System")

# Create a dropdown (select box) with all movie titles
selected_movie_name = st.selectbox(
    "🔍 Type or select a movie:",
    recommender.final_df['title'].values  # List of all movie titles
)

# Button to trigger recommendation
if st.button("Show Recommendations"):
    # Call the recommend function and store the result
    recommendations = recommender.recommend(selected_movie_name)

    # Check if recommendations were found
    if recommendations is None:
        st.error("❌ Movie not found or no similar movies available. Try another title.")
    else:
        st.subheader(f"✅ Top 5 Similar Movies to: {selected_movie_name}")
        for movie in recommendations:
            st.write("🎞️", movie)
