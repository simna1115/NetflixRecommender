import pandas as pd
import numpy as np
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle



# Load datasets
movies_raw = pd.read_csv("data/tmdb_5000_movies.csv")
credits_raw = pd.read_csv("data/tmdb_5000_credits.csv")
movies = movies_raw.merge(credits_raw, on="title")

# Merge on title, drop duplicates
movies = movies[["movie_id", "title", "overview", "genres", "keywords", "cast", "crew"]]
movies.dropna(inplace=True)
movies.drop_duplicates(inplace=True)


# Functions to clean and extract relevant info
def extract_names(obj):
    if isinstance(obj, list):
        return obj
    try:
        parsed = ast.literal_eval(obj)
        return [item['name'] for item in parsed]
    except Exception:
        return []



def extract_top3_cast(obj):
    List = []
    count = 0
    for item in ast.literal_eval(obj):
        if count < 3:
            List.append(item["name"])
            count += 1
        else:
            break
    return List


def extract_director(obj):
    List = []
    for item in ast.literal_eval(obj):
        if item["job"] == "director":
            List.append(item["name"])
            break
    return List


# Apply functions
movies["genres"] = movies["genres"].apply(extract_names)
movies["genres"] = movies["genres"].apply(extract_names)
movies["cast"] = movies["cast"].apply(extract_top3_cast)
movies["crew"] = movies["crew"].apply(extract_director)


# Convert overview to list of words
movies["overview"] = movies["overview"].apply(lambda x: x.split())


# Remove spaces in multi-word names
for col in ["genres", "keywords", "cast", "crew"]:
    movies[col] = movies[col].apply(lambda x: [i.replace(" ", "") for i in x])


# Combine all into tags
movies["tags"] = (
    movies["overview"]
    + movies["genres"]
    + movies["keywords"]
    + movies["cast"]
    + movies["crew"]
)
movies["tags"] = movies["tags"].apply(lambda x: " ".join(x))
movies["tags"] = movies["tags"].apply(lambda x: x.lower())


# Final dataframe
final_df = movies[["movie_id", "title", "tags"]]


# Text vectorization
cv = CountVectorizer(max_features=5000, stop_words="english")
vectors = cv.fit_transform(final_df["tags"]).toarray()

# Similarity matrix
similarity = cosine_similarity(vectors)

# Save the model so we don’t compute again
pickle.dump(similarity, open("model/similarity.pkl", "wb"))


# Recommendation function
import difflib  # This allows fuzzy matching

def recommend(movie):
    # Convert the input movie name to lowercase for comparison
    movie = movie.lower()

    # Get all movie titles from the dataframe in lowercase
    all_titles = final_df['title'].str.lower().tolist()

    # Try to find the closest matching movie title from the list
    close_matches = difflib.get_close_matches(movie, all_titles, n=1, cutoff=0.6)

    # If no close match is found, return None
    if not close_matches:
        return None

    # Otherwise, use the best matching title
    matched_title = close_matches[0]

    # Get the index of that movie from the dataframe
    movie_index = final_df[final_df['title'].str.lower() == matched_title].index[0]

    # Find similarity scores with all other movies
    similarity_scores = similarity[movie_index]

    # Sort the similarity scores and get top 5 movies excluding the original one
    movie_list = sorted(list(enumerate(similarity_scores)), reverse=True, key=lambda x: x[1])[1:6]

    # Create a list of recommended movie titles
    recommended_movies = []
    for i in movie_list:
        recommended_movies.append(final_df.iloc[i[0]].title)

    return recommended_movies



