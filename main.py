import streamlit as st
import pickle
import pandas as pd
import requests
import os
import base64


# Function to get the Base64 encoded string for the image
def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as image_file:  # Replace with your image path
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string


# Cache filename
cache_file = 'movie_cache.csv'

# Load cached data
if os.path.exists(cache_file):
    cache_df = pd.read_csv(cache_file)
else:
    cache_df = pd.DataFrame(columns=['title', 'imdb_id', 'poster_url'])


def fetch_movie_data(title, api_key):
    global cache_df  # Declare cache_df as global

    # Check if the movie data is already cached
    cached_movie = cache_df[cache_df['title'].str.lower() == title.lower()]

    if not cached_movie.empty:
        return cached_movie['imdb_id'].values[0], cached_movie['poster_url'].values[0]

    # If not cached, fetch from API
    url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()

    if data['Response'] == 'True':
        # Append new data to cache DataFrame
        new_row = pd.DataFrame({'title': [title], 'imdb_id': [data['imdbID']], 'poster_url': [data['Poster']]})
        cache_df = pd.concat([cache_df, new_row], ignore_index=True)
        cache_df.to_csv(cache_file, index=False)  # Save cache to CSV
        return data['imdbID'], data['Poster']  # Return IMDb ID and poster URL
    return None, None  # Return None if not found


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distance = similarity[movie_index]
    movies_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    posters = []

    for i in movies_list:
        title = movies.iloc[i[0]]['title']  # Get movie title
        imdb_id, poster_url = fetch_movie_data(title, api_key)  # Fetch IMDb ID and poster
        recommended_movies.append(title)
        posters.append(poster_url)  # Append the poster URL

    return recommended_movies, posters


# Load movie data and similarity matrix
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Your OMDb API Key
api_key = 'ebcdb41f'  # Replace with your actual API key

# Get the Base64 encoded string of the background image
image_path = "C:/Users/HP/PycharmProjects/movie recommender system/cinema.jpg"  # Update with your image path
encoded_string = get_base64_encoded_image(image_path)

# Set the background image using markdown
st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url("data:image/jpg;base64,{encoded_string}");
        background-size: cover;
        background-position: center;
    }}
    h1 {{
        color: white;
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 20px;
    }}
    .stButton > button {{
        background-color: #FF4B4B;
        color: white;
        font-size: 1.2em;
        border-radius: 10px;
        padding: 10px 20px;
    }}
    .recommended-text {{
        font-size: 1.5em;
        color: white; /* Changed from gold to white */
        font-weight: bold;
    }}
    .stSelectbox > div {{
        background-color: rgba(255, 255, 255, 0.8);
        color: black;
        font-size: 1.2em;
        border-radius: 5px;
    }}
    .stSelectbox label {{
        color: white;
        font-size: 1.5em;
        font-weight: bold;
    }}
    .recommended-title {{
        font-size: 2em;
        color: white;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
    }}
    .recommendation-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
    }}
    .recommended-movies-title {{
        color: white;  /* Changed from gold to white for better contrast */
        font-size: 2em;
        font-weight: bold;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit title
st.markdown("<h1>Movie Recommender System</h1>", unsafe_allow_html=True)

# Select movie
selected_movie_name = st.selectbox(
    'Select a movie:',
    movies['title'].values
)

# Recommend button
if st.button('Recommend'):
    recommendations, posters = recommend(selected_movie_name)

    st.markdown("<div class='recommended-movies-title'>Recommended movies:</div>", unsafe_allow_html=True)

    for movie, poster in zip(recommendations, posters):
        col1, col2 = st.columns([1, 5])  # Create two columns for better layout
        with col1:
            if poster:
                st.image(poster, width=100)
            else:
                st.write("No poster found for this movie.")
        with col2:
            st.markdown(f"<div class='recommended-text'>{movie}</div>", unsafe_allow_html=True)




