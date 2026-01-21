import streamlit as st
import pickle
import os
import requests

FILE_ID = "1rxCY3Kj2pllx3Zz9q2bn0jeLFBiJoOz8"
URL = f"https://drive.google.com/uc?id={FILE_ID}"
FILENAME = "similarity.pkl"


def download_file(url, filename):
    if not os.path.exists(filename):
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)


@st.cache_resource
def load_similarity():
    download_file(URL, FILENAME)
    with open(FILENAME, "rb") as f:
        return pickle.load(f)


# 🔥 Load once, reuse forever
similarity = load_similarity()
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


