import config from '../../js/config.js';

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const bookId = urlParams.get('id');
    console.log('ID du livre :', bookId);
    if (bookId) {
        // Demander les informations du livre
        fetch(`${config.apiUrl}/books/${bookId}`)
            .then(response => response.json())
            .then(bookData => {
                if (bookData.detail) {
                    console.error('Erreur lors de la récupération des données du livre :', bookData.detail);
                    document.getElementById('loading').innerText = bookData.detail;
                } else {
                    console.log('Données du livre :', bookData);
                    // Afficher la couverture du livre
                    const cover = document.getElementById('book-cover');
                    const imgUrl = `https://www.googleapis.com/books/v1/volumes?q=isbn:${bookData.isbn13}`;
                    fetch(imgUrl)
                        .then(response => response.json())
                        .then(data => {
                            if (data.items && data.items.length > 0) {
                                const coverUrl = data.items[0].volumeInfo.imageLinks.thumbnail;
                                cover.src = coverUrl;
                                cover.alt = bookData.title;
                            } else {
                                console.error('Aucune couverture trouvée pour ce livre.');
                            }
                        })
                        .catch(error => {
                            console.error('Erreur lors du chargement de l\'image :', error);
                        });

                    // Afficher les données du livre
                    document.getElementById('book-title').innerText = bookData.title;
                    document.getElementById('book-author').innerText = bookData.author_name;
                    const genresContainer = document.getElementById('book-genres');
                    bookData.genre_names.forEach(genre => {
                        const genreElement = document.createElement('span');
                        genreElement.innerText = genre;
                        genreElement.classList.add(
                            'px-3',
                            'py-1',
                            'bg-[#FFB100]',
                            'rounded-lg',
                            'text-sm',
                            'text-black',
                            'mr-2',
                            'mb-2'
                        );
                        genresContainer.appendChild(genreElement);
                    });
                    document.getElementById('book-description').innerText = bookData.description.replaceAll("#virgule", ",");
                    document.getElementById('book-page').innerText = bookData.number_of_pages;
                    document.getElementById('book-publisher').innerText = bookData.publisher_name;
                    const awardsContainer = document.getElementById('book-awards');
                    bookData.award_names.forEach(award => {
                        const awardElement = document.createElement('span');
                        awardElement.innerText = award;
                        awardsContainer.appendChild(awardElement);
                    });
                    document.getElementById('book-isbn').innerText = bookData.isbn;

                    // Masquer l'écran de chargement et afficher les détails du livre
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('book-details').style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Erreur lors de la récupération des données du livre :', error);
            });
    }
});
