let selectedBook = null;

async function fetchBooks() {
    const storageKey = 'booksData';
    const storageKeyG = 'booksDataG';
    const storageTimestampKey = 'booksDataTimestamp';
    const storageTimestampKeyG = 'booksDataTimestampG';

    const storedData = localStorage.getItem(storageKey);
    const storedTimestamp = localStorage.getItem(storageTimestampKey);
    const storedDataG = localStorage.getItem(storageKeyG);
    const storedTimestampG = localStorage.getItem(storageTimestampKeyG);
    const now = Date.now();

    document.getElementById("loading").style.display = "flex"; 
    document.getElementById("content").style.display = "none";

    let books = [];
    let genreBooks = [];

    if (storedData && storedDataG && storedTimestampG && storedTimestamp && now - parseInt(storedTimestamp) < 30000 && now - parseInt(storedTimestampG) < 30000) { 
        console.log('Données chargées depuis localStorage');
        books = JSON.parse(storedData);
        genreBooks = JSON.parse(storedDataG);
    } else {
        try {
            // Récupération des livres
            const response = await fetch('/books/topbook/30');
            books = await response.json();

            // Récupération des genres
            const response_genre = await fetch('/genres/all');
            const genres = await response_genre.json();
            console.log("Genres disponibles :", genres);

            // Stockage des données dans localStorage
            localStorage.setItem(storageKey, JSON.stringify(books));
            localStorage.setItem(storageTimestampKey, now.toString());

            console.log('Données récupérées depuis l’API');

            // Sélectionner 5 genres aléatoirement
            if (genres.length > 0) {
                const randomGenres = genres.sort(() => 0.5 - Math.random()).slice(0, 5);
                
                // Effectuer les requêtes pour chaque genre sélectionné
                const genreFetches = randomGenres.map(async (genre) => {
                    try {
                        const response = await fetch(`/books/genre/${encodeURIComponent(genre.name)}?limit=30`);
                        const data = await response.json();
                        console.log(`Données pour le genre ${genre.name}:`, data);
                        return { genre: genre.name, books: data };
                    } catch (error) {
                        console.error(`Erreur lors de la récupération des livres du genre ${genre.name}:`, error);
                        return null;
                    }
                });

                genreBooks = (await Promise.all(genreFetches)).filter(g => g !== null);

                localStorage.setItem(storageKeyG, JSON.stringify(genreBooks));
                localStorage.setItem(storageTimestampKeyG, now.toString());

                console.log("Données des genres récupérées :", genreBooks);
            }

        } catch (error) {
            console.error('Erreur lors de la récupération des livres:', error);
        }
    }

    processBooks(books, genreBooks);

    document.getElementById("loading").style.display = "none"; 
    document.getElementById("content").style.display = "block";
}


function processBooks(books, genreBooks = []) {
    const categories = [
        {
            name: 'Meilleurs Livres',
            books: books.map(book => ({
                title: book.title || 'Titre inconnu',
                image: (book.url === "-1") ? 'static/notfound.jpg' : book.url,  
                description: book.description ? book.description.split('#virgule')[0] : 'Aucune description disponible.',
                pages: book.number_of_pages || 'Non spécifié',
                rating: book.average_rating || 'Non spécifié',
                publisher: book.publisher_name || 'Non spécifié',
                id: book.id
            }))
        }
    ];
    
    genreBooks.forEach(genreData => {
        if (genreData && genreData.books.length > 0) {
            categories.push({
                name: genreData.genre,
                books: genreData.books.map(book => ({
                    title: book.title || 'Titre inconnu',
                    image: (book.url === "-1") ? 'static/notfound.jpg' : book.url,  
                    description: book.description ? book.description.split('#virgule')[0] : 'Aucune description disponible.',
                    pages: book.number_of_pages || 'Non spécifié',
                    rating: book.average_rating || 'Non spécifié',
                    publisher: book.publisher_name || 'Non spécifié'
                }))
            });
        }
    });
    
    displayBooks(categories);

    if (categories.length > 0 && categories[0].books.length > 0) {
        const randomIndex = Math.floor(Math.random() * categories[0].books.length);
        const selectedBook = categories[0].books[randomIndex]; 
        showBookInfo(selectedBook);
    }
}



function displayBooks(categories) {
    const bookContainer = document.getElementById('book-container');
    bookContainer.innerHTML = ''; 
    
    categories.forEach(category => {
        const categoryDiv = document.createElement('div');
        const categoryTitle = document.createElement('h2');
        categoryTitle.textContent = category.name;
        categoryTitle.classList.add('text-2xl', 'font-bold', 'mb-4', "mt-10");
        categoryDiv.appendChild(categoryTitle);

        const booksDiv = document.createElement('div');
        booksDiv.classList.add('flex', 'overflow-x-auto', 'space-x-4','hoverBook');

        category.books.forEach(book => {
            const bookDiv = document.createElement('div');
            bookDiv.classList.add('relative', 'w-40', 'flex-shrink-0', 'group', 'cursor-pointer');
            
            const bookImage = document.createElement('img');
            bookImage.src = book.image;
            bookImage.classList.add('w-full', 'h-56', 'object-cover', 'rounded-lg', 'shadow-lg');
            
            bookDiv.addEventListener('click', () => {
                showBookInfo(book);
                selectedBook = book; 
                scrollTo({ top: 0 })
            });
            
            bookDiv.appendChild(bookImage);
            booksDiv.appendChild(bookDiv);
        });

        categoryDiv.appendChild(booksDiv);
        bookContainer.appendChild(categoryDiv);
    });
}

function showBookInfo(book) {
    const headerImage = document.getElementById('header-image');
    const bookTitle = document.getElementById('book-title');
    const bookDescription = document.getElementById('book-description');
    const bookPages = document.getElementById('book-pages-num');
    const bookRating = document.getElementById('book-rating-num');
    const bookPublisher = document.getElementById('book-publisher-num');
    const bookid = document.getElementById('book-id-num');

    if (headerImage && bookTitle && bookDescription && bookPages && bookRating) {
        headerImage.src = book.image;
        bookTitle.textContent = book.title;
        bookDescription.textContent = book.description;
        bookPages.textContent = book.pages;
        bookRating.textContent = book.rating;
        bookPublisher.textContent = book.publisher;
        bookid.textContent = book.id;
    }
}

window.onload = fetchBooks;
