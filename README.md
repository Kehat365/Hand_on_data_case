# Hand_on_data_case
This project implements a Movie Recommendation API using Python and Flask. The API provides movie recommendations based on a given movie title. It uses a combination of content-based filtering (via a TF-IDF vectorizer and a K-Nearest Neighbors model) and collaborative filtering (based on user ratings) to suggest similar movies.

# How It Works

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

More details are given in the notebook.
