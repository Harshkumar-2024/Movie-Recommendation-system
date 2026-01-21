import streamlit as st
import pickle
import os
import requests

# 1. Configuration
FILE_ID = "1rxCY3Kj2pllx3Zz9q2bn0jeLFBiJoOz8"
FILENAME = "similarity.pkl"


def download_from_drive():
    # This direct link works better for bypassing the basic Google Drive blocks
    url = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

    with st.spinner("🚀 Downloading model from Google Drive... Please wait."):
        response = requests.get(url, stream=True)
        # Check if we actually got the file or an error
        if response.status_code == 200:
            with open(FILENAME, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        else:
            st.error(f"Download failed! Status code: {response.status_code}")
            st.stop()


# 2. Execution (Run every time)
if not os.path.exists(FILENAME):
    download_from_drive()

# Check if file is valid before loading
if os.path.getsize(FILENAME) < 1000:  # If file is tiny, it's an error page
    st.error("The downloaded file is too small. Check if your Google Drive link is 'Anyone with the link can view'.")
    os.remove(FILENAME)  # Remove bad file so we can retry
    st.stop()

# 3. Load the data
try:
    with open(FILENAME, 'rb') as f:
        similarity = pickle.load(f)
except Exception as e:
    st.error(f"Error loading the pickle file: {e}")
    os.remove(FILENAME)  # Delete corrupted file
    st.stop()

# The rest of your code (movies.pkl, fetch_poster, recommend) stays the same
# Load data
movies = pickle.load(open('movies.pkl', 'rb'))   # KEEP AS DATAFRAME

# Movie titles for dropdown
movies_list = movies['title'].values

def fetch_poster(movie_id):
    api_key = "199156c7bd68d0091856aaa4f52eee85"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('poster_path'):
            return "https://image.tmdb.org/t/p/w500" + data['poster_path']
        else:
            return "https://via.placeholder.com/300x450?text=No+Poster"

    except requests.exceptions.RequestException as e:
        print(e)
        return "https://via.placeholder.com/300x450?text=Error"

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]

    distances = similarity[index]
    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_movies = []
    recommended_movies_posters = []
    for i in movie_list[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters

# Streamlit UI
st.title('🎬Movie Recommendation System')

selected_movie_name = st.selectbox(
    'Search or scroll to select a movie',
    movies_list
)

if st.button('Recommend'):
    names,posters = recommend(selected_movie_name)

    cols = st.columns(5)

    for col,name,poster in zip(cols,names,posters):
        with col:
            st.image(poster)
            st.markdown(f"**{name}**")


