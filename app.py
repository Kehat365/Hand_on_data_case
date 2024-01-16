from flask import Flask, jsonify, request 
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

movies_info_merg_df = pd.read_csv('movies_info_merg.csv')
ratings_df = pd.read_csv('ratings.csv')

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for this Flask app

# Prepare the data for the KNN model
combined_features = movies_info_merg_df['director_name'] + " " + \
                    movies_info_merg_df['actor_2_name'] + " " + \
                    movies_info_merg_df['genres'] + " " + \
                    movies_info_merg_df['actor_1_name'] + " " + \
                    movies_info_merg_df['actor_3_name'] + " " + \
                    movies_info_merg_df['plot_keywords'] + " " + \
                    movies_info_merg_df['movie_title']
combined_features = combined_features.fillna('')

# Create TF-IDF matrix
vectorizer = TfidfVectorizer(ngram_range=(1, 2))
tfidf_matrix = vectorizer.fit_transform(combined_features)

# Build the KNN model
model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=1)
model_knn.fit(tfidf_matrix)




def clean_title(title):
    """
    Cleans a movie title by removing special characters and trimming spaces.

    Args:
    title (str): The movie title to clean.

    Returns:
    str: A cleaned movie title.
    """
    return title.strip().replace('\xa0', '')

def search_knn(title, movies):
    """
    Search for a movie using KNN based on the given title.

    Args:
        title (str): Title of the movie to search for.
        movies (DataFrame): DataFrame containing movies data.

    Returns:
        int: movieId of the found movie.
    """
    # Combine the title with other features (as done for the dataset)
    title_combined = clean_title(title)  # Add other features if needed
    
    query_vec = vectorizer.transform([title_combined])
    distances, indices = model_knn.kneighbors(query_vec, n_neighbors=1)

    # Get the indices of the nearest neighbors
    nearest_indices = indices.flatten()
    
    # Find corresponding movie titles and other details
    results = movies.iloc[nearest_indices]
    
    return results.iloc[0]['movieId']

def find_similar_movies(movie_id):
    """
    Find similar movies based on user ratings.

    Args:
        movie_id (int): movieId of the movie to find similar movies for.

    Returns:
        DataFrame: DataFrame of top 10 similar movies.
    """
    similar_users = ratings_df[(ratings_df["movieId"] == movie_id) & (ratings_df["rating"] > 4)]["userId"].unique()
    similar_user_recs = ratings_df[(ratings_df["userId"].isin(similar_users)) & (ratings_df["rating"] > 4)]["movieId"]
    similar_user_recs = similar_user_recs.value_counts() / len(similar_users)

    similar_user_recs = similar_user_recs[similar_user_recs > .10]
    all_users = ratings_df[(ratings_df["movieId"].isin(similar_user_recs.index)) & (ratings_df["rating"] > 4)]
    all_user_recs = all_users["movieId"].value_counts() / len(all_users["userId"].unique())
    rec_percentages = pd.concat([similar_user_recs, all_user_recs], axis=1)
    rec_percentages.columns = ["similar", "all"]
    
    rec_percentages["score"] = rec_percentages["similar"] / rec_percentages["all"]
    rec_percentages = rec_percentages.sort_values("score", ascending=False)
    return rec_percentages.head(10).merge(movies_info_merg_df, left_index=True, right_on="movieId")[["score", "title", "genres", "movieId"]]

def movie_poster_fetcher(imdb_link):
    """
    Fetches the URL of a movie's poster from its IMDb page.

    Args:
        imdb_link (str): The URL of the movie's IMDb page.

    Returns:
        str: The URL of the movie's poster image. Returns None if the poster URL is not found.
    """
    hdr = {'User-Agent': 'Mozilla/5.0'}  # Adjust the header as needed
    url_data = requests.get(imdb_link, headers=hdr).text
    s_data = BeautifulSoup(url_data, 'html.parser')
    imdb_dp = s_data.find("meta", property="og:image")
    movie_poster_link = imdb_dp.attrs['content'] if imdb_dp else None
    return movie_poster_link

def get_movie_info(imdb_link):
    """
    Scrapes a movie's detailed information from its IMDb page.

    Args:
        imdb_link (str): The URL of the movie's IMDb page.

    Returns:
        tuple: A tuple containing the director's name, cast, story summary,
               additional information, and movie rating. If certain information
               is not found, 'N/A' is returned in its place.
    """
    hdr = {'User-Agent': 'Mozilla/5.0'}  # Adjust the header as needed
    url_data = requests.get(imdb_link, headers=hdr).text
    s_data = BeautifulSoup(url_data, 'html.parser')
    movie_story = s_data.find('p', class_='sc-466bb6c-3 fOUpWp')
    r_movie_story = movie_story.text if movie_story else 'N/A'
    people = s_data.find_all('div', class_='ipc-metadata-list-item__content-container')
    movie_director = people[0].text if people[0] else 'N/A'
    movie_cast = people[1].text if people[1] else 'N/A'
    movie_desc_ul = s_data.find('ul', class_='ipc-inline-list ipc-inline-list--show-dividers sc-d8941411-2 cdJsTz baseAlt')
    if movie_desc_ul:
        # Extract text from each list item
        movie_desc_list = [li.get_text(strip=True) for li in movie_desc_ul.find_all('li')]
    
        # Join the list items into a single string separated by spaces
        movie_descro = ' '.join(movie_desc_list)
    else:
        movie_descro = "Description not found"
    rating = s_data.find("span", class_="sc-bde20123-1 cMEQkK").text if s_data.find("span", class_="sc-bde20123-1 cMEQkK") else "N/A"  # Update class name as needed
    return movie_director, movie_cast, r_movie_story, movie_descro, rating

@app.route('/search', methods=['GET'])
def search_movies():
    """
    Flask route to handle movie search requests.

    Returns:
        Response: JSON response containing movie information.
    """
    title = request.args.get('title')
    if not title:
        return jsonify({'error': 'No title provided'}), 400

    # Use your search_knn function
    
    searched_movie = search_knn(title, movies_info_merg_df)
    results = find_similar_movies(searched_movie)
    movie_ids = results['movieId'].tolist()

    movie_infos = []
    for movie_id in movie_ids:
        movie = movies_info_merg_df[movies_info_merg_df['movieId'] == movie_id].iloc[0]
        imdb_link = movie['movie_imdb_link']
        director, cast, story, movie_desrr, total_rating = get_movie_info(imdb_link)  # Your scraping function
        poster_url = movie_poster_fetcher(imdb_link)  # Fetch movie poster URL

        movie_infos.append({
            'title': movie['title'],
            'director': director,
            'story': story,
            'additional_infos': movie_desrr,
            'total_rating': total_rating,
            'poster_url': poster_url,
            'movie_link': imdb_link
        })
    
    return jsonify(movie_infos)

if __name__ == '__main__':
    app.run(debug=True, port=8080)