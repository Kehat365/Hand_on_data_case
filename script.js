function searchMovie() {
    const title = document.getElementById('movieTitle').value;
    const loadingIndicator = document.getElementById('loadingIndicator');

    // Show loading indicator
    loadingIndicator.style.display = 'block';

    fetch(`http://localhost:8080/search?title=${encodeURIComponent(title)}`)
        .then(response => response.json())
        .then(data => {
            // Hide loading indicator
            loadingIndicator.style.display = 'none';
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            // Hide loading indicator
            loadingIndicator.style.display = 'none';
        });
}

function displayResults(movies) {
    const results = document.getElementById('results');
    results.innerHTML = '';  // Clear previous results
    movies.forEach(movie => {
        const div = document.createElement('div');
        div.className = 'movie-card clearfix';
        div.innerHTML = `
            <h2><a href="${movie.movie_link}" target="_blank">${movie.title}</a></h2>
            <img src="${movie.poster_url}" alt="${movie.title}" class="movie-poster">
            <p>Director: ${movie.director}</p>
            <p>Story: ${movie.story}</p>
            <p>Rating: ${movie.total_rating}</p>
            <p>Additional Info: ${movie.additional_infos}</p>`;
        results.appendChild(div);
    });
}

