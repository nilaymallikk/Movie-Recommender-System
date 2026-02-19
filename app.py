import streamlit as st
import pickle
import pandas as pd
import requests

# ─── Page Configuration ───
st.set_page_config(
    page_title="🎬 Netflix Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# ─── Custom CSS for Netflix-style dark theme & animated carousel ───
st.markdown("""
<style>
    /* Dark background */
    .stApp {
        background-color: #141414;
        color: #ffffff;
    }
    
    /* Title styling */
    h1 {
        color: #E50914 !important;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #b3b3b3;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Movie card styling */
    .movie-card {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 10px;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid #2a2a4a;
    }
    .movie-card:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(229, 9, 20, 0.3);
    }
    .movie-card img {
        border-radius: 8px;
        width: 100%;
    }
    .movie-title {
        color: #ffffff;
        font-size: 0.95rem;
        font-weight: 600;
        margin-top: 8px;
        min-height: 45px;
    }
    
    /* Carousel animation */
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-card {
        animation: slideIn 0.6s ease forwards;
    }
    .animate-card:nth-child(2) { animation-delay: 0.1s; }
    .animate-card:nth-child(3) { animation-delay: 0.2s; }
    .animate-card:nth-child(4) { animation-delay: 0.3s; }
    .animate-card:nth-child(5) { animation-delay: 0.4s; }
    
    /* Button styling */
    .stButton > button {
        background-color: #E50914 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background-color: #f40612 !important;
        box-shadow: 0 4px 15px rgba(229, 9, 20, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Selectbox styling */
    .stSelectbox label {
        color: #b3b3b3 !important;
        font-size: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── Load Data ───
@st.cache_data
def load_data():
    movies = pickle.load(open('movies.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity

movies, similarity = load_data()

# ─── TMDB API Configuration ───
TMDB_API_KEY = "aae8076738f53ac73410f5c1b284de1e"
PLACEHOLDER_POSTER = "https://via.placeholder.com/500x750.png?text=No+Poster+Available"

def fetch_poster(movie_id):
    """Fetch movie poster from TMDB API with retry logic."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                poster_path = data.get('poster_path')
                if poster_path:
                    return f"https://image.tmdb.org/t/p/w500{poster_path}"
            break
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt == 2:
                break
            continue
        except Exception:
            break
    return PLACEHOLDER_POSTER

def recommend(movie_title):
    """Get top 5 similar movie recommendations."""
    movie_index = movies[movies['title'] == movie_title].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_titles = []
    recommended_posters = []
    
    for i in movie_list:
        movie_id = movies.iloc[i[0]].id
        recommended_titles.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
    
    return recommended_titles, recommended_posters

# ─── App Header ───
st.markdown("<h1>🎬 Netflix-Style Movie Recommender</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Discover movies you\'ll love — powered by Machine Learning</p>', unsafe_allow_html=True)

# ─── Divider ───
st.markdown("---")

# ─── Movie Selection ───
col_select, col_btn = st.columns([3, 1])

with col_select:
    selected_movie = st.selectbox(
        "🔍 Choose a movie you like:",
        movies['title'].values,
        index=0
    )

with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    show_btn = st.button("🎯 Show Recommendations")

# ─── Display Recommendations ───
if show_btn:
    with st.spinner("🔄 Finding similar movies..."):
        titles, posters = recommend(selected_movie)
    
    st.markdown("---")
    st.markdown(f"### 🍿 Movies similar to **{selected_movie}**:")
    st.markdown("")
    
    # Create 5 columns for movie cards
    cols = st.columns(5)
    
    for idx, col in enumerate(cols):
        with col:
            st.image(posters[idx], use_container_width=True)
            st.markdown(f"""
            <div class="movie-title" style="text-align:center; color:#ffffff;
                font-size:0.95rem; font-weight:600; margin-top:4px;">
                {titles[idx]}
            </div>
            """, unsafe_allow_html=True)

# ─── Footer ───
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#666; font-size:0.85rem;">'
    'Built with ❤️ by Nilay Mallik | Content-Based Recommendation Engine'
    '</p>',
    unsafe_allow_html=True
)
