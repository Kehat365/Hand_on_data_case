This project implements a Movie Recommendation API using Python and Flask. The API provides movie recommendations based on a given movie title. It uses a combination of content-based filtering (via a TF-IDF vectorizer and a K-Nearest Neighbors model) and collaborative filtering (based on user ratings) to suggest similar movies.

# <b> Quick Setup Guide</b>
## 1. Download the Repository

Download the repository from GitHub containing the entire project, including both the Flask API and the web application files.
## 2. Run the Flask API

In a terminal, navigate to the directory of the downloaded repository where the Flask application (app.py) is located and run it with the command : 'python app.py'. This will start the Flask server, which serves as the backend for the web application.
## 3. Run the HTML File

Open the vizht.html file from the downloaded repository in a web browser to access the web application. Use it to search for movies and view recommendations.

# <b>How It Works</b>

## Data Preparation: 
Movie data is loaded from big query and processed. Features are combined into a single string for each movie to prepare for the TF-IDF vectorization.

## TF-IDF Vectorization: 
The combined features are vectorized using TF-IDF to analyze the textual data.

## K-Nearest Neighbors Model: 
A KNN model is used to find movies that are similar to the query movie based on the cosine similarity of their feature vectors.

## User Ratings Analysis: 
For collaborative filtering, user ratings are analyzed to find movies popular among users who liked the query movie.

## Web Scraping: 
Additional details about each recommended movie are scraped from their respective IMDb pages.



More details and some visualizations are given in the notebook.
