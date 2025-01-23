document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const urlParams = new URLSearchParams(window.location.search);
    const bookId = urlParams.get('id');

    if (bookId) {
        // Demander les informations du livre
        socket.emit('get_livre', bookId);
    }

    // Réception des données du livre
    socket.on('data_livre', async (bookData) => {
        if (bookData.error) {
            document.getElementById('loading').innerText = bookData.error;
        } else {
            // Afficher la couverture du livre
            const cover = document.getElementById('book-cover');
            // const imgUrl = `https://covers.openlibrary.org/b/isbn/${bookData.isbn}-L.jpg`;
            // fetchImage(imgUrl).then(img => {
            //     cover.src = imgUrl;
            //     cover.width = img.width;
            //     cover.height = img.height;
            // }).catch(err => {
            //     console.error('Erreur lors du chargement de l\'image :', err);
            // });

            // Afficher la couverture du livre
            const imgUrl = `https://www.googleapis.com/books/v1/volumes?q=isbn:${bookData.isbn13}`;
            try {
                const response = await fetch(imgUrl);
                const data = await response.json();
                if (data.items && data.items.length > 0) {
                    const coverUrl = data.items[0].volumeInfo.imageLinks.thumbnail;
                    cover.src = coverUrl;
                    cover.alt = bookData.title;
                } else {
                    console.error('Aucune couverture trouvée pour ce livre.');
                }
            } catch (error) {
                console.error('Erreur lors du chargement de l\'image :', error);
            }

            console.log(bookData);
            // Afficher les données du livre
            document.getElementById('book-title').innerText = bookData.title;
            document.getElementById('book-author').innerText = bookData.author_name;
            // Afficher les genres
            const genresContainer = document.getElementById('book-genres');
            bookData.genre_names.forEach(genre => {
                const genreElement = document.createElement('span');
                genreElement.innerText = genre;
                genreElement.classList.add(
                    'px-3',      // Padding horizontal
                    'py-1',      // Padding vertical
                    'bg-[#FFB100]', // Couleur de fond bleu
                    'rounded-lg', // Coins arrondis
                    'text-sm',    // Taille de texte petite
                    'text-black', // Couleur du texte en blanc
                    'mr-2',       // Marge à droite pour espacer les badges
                    'mb-2'        // Marge en bas pour les petites tailles d'écran
                );
                genresContainer.appendChild(genreElement);
            });
            document.getElementById('book-description').innerText =  bookData.description.replaceAll("#virgule", ",");
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
    });
});


async function fetchImage(url) {
    const img = new Image();
    return new Promise((res, rej) => {
        img.onload = () => res(img);
        img.onerror = e => rej(e);
        img.src = url;
    });
}
