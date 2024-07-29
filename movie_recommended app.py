import streamlit as st
import requests
import pickle
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import logging
import base64

with open("C:\\Users\\singh\\Downloads\\Netflix-Background (1).jpg", "rb") as image_file:  # Replace with your image path
    encoded_string = base64.b64encode(image_file.read()).decode()
st.markdown(
    f"""
      <style>
      .stApp {{
          background-image: url("data:image/jpg;base64,{encoded_string}");
          background-size: cover;
          background-position: center;
      }}
      </style>
      """,
    unsafe_allow_html=True
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(_name_)

# Function to fetch poster with retry and error handling
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=b221b07bda7a38a423b8f7fb73de2bd9&language=en-US".format(
        movie_id)

    retry_strategy = Retry(
        total=5,  # Number of retries
        backoff_factor=1,  # Time between retries: 1s, 2s, 4s, etc.
        status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
        allowed_methods=["GET"]  # Only retry for GET requests
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("http://", adapter)
    http.mount("https://", adapter)

    try:
        logger.info(f"Fetching poster for movie ID: {movie_id} from {url}")
        response = http.get(url, timeout=10)  # 10 seconds timeout
        response.raise_for_status()  # Raise an error for bad HTTP status codes
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
        else:
            return "https://via.placeholder.com/500x750.png?text=No+Image"  # Fallback image
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching poster for movie ID {movie_id}: {e}")
        st.error(f"Error fetching poster for movie ID {movie_id}.")
        return "https://via.placeholder.com/500x750.png?text=No+Image"  # Fallback image

# Function to recommend movies
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:11]:  # Show 10 movies instead of 5
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

# Streamlit app interface
st.header('Movie Recommender System')

# Load movie data and similarity matrix
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    num_cols = 5
    num_rows = 2
    total_movies = num_cols * num_rows

    for i in range(num_rows):
        cols = st.columns(num_cols)
        for j in range(num_cols):
            movie_index = i * num_cols + j
            if movie_index < len(recommended_movie_names):
                with cols[j]:
                    st.text(recommended_movie_names[movie_index])
                    st.image(recommended_movie_posters[movie_index])
