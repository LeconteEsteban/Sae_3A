let selectedBook = null;

async function fetchBooks() {
    const storageKey = 'booksData';
    const storageKeyG = 'booksDataG';
    const storageTimestampKey = 'booksDataTimestamp';
    const storageTimestampKeyG = 'booksDataTimestampG';

    const userId = localStorage.getItem("user_id");

    const storedData = localStorage.getItem(storageKey);
    const storedTimestamp = localStorage.getItem(storageTimestampKey);
    const storedDataG = localStorage.getItem(storageKeyG);
    const storedTimestampG = localStorage.getItem(storageTimestampKeyG);
    const now = Date.now();

    document.getElementById("loading").style.display = "flex"; 
    document.getElementById("content").style.display = "none";

    let books = [];
    let genreBooks = [];
    let reco = [];

    if (storedData && storedDataG && storedTimestampG && storedTimestamp && now - parseInt(storedTimestamp) < 30000 && now - parseInt(storedTimestampG) < 30000) { 
        console.log('Données chargées depuis localStorage');
        books = JSON.parse(storedData);
        genreBooks = JSON.parse(storedDataG);
    } else {
        try {
            // Récupération des 30 meilleurs livres
            const response = await fetch('/books/topbook/30');
            books = await response.json();

            const response_genre = await fetch('/genres/all');
            const genres = await response_genre.json();

            if (userId) {
                const response_reco = await fetch(`/recommandations/item/${userId}/30`);
                reco = await response_reco.json();
            }

            localStorage.setItem(storageKey, JSON.stringify(books));
            localStorage.setItem(storageTimestampKey, now.toString());

            console.log('Données récupérées depuis l’API');

            if (genres.length > 0) {
                const randomGenres = genres.sort(() => 0.5 - Math.random()).slice(0, 3);
                
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

    processBooks(books, genreBooks, reco);

    document.getElementById("loading").style.display = "none"; 
    document.getElementById("content").style.display = "block";
}
function processBooks(books, genreBooks = [], reco = []) {
    const seenBookIds = new Set(); 

    function filterUniqueBooks(bookList) {
        return bookList.filter(book => {
            if (!seenBookIds.has(book.id)) {
                seenBookIds.add(book.id);
                return true;
            }
            return false;
        });
    }

    const categories = [
        {
            name: 'Meilleurs Livres',
            books: filterUniqueBooks(books.map(book => ({
                title: book.title || 'Titre inconnu',
                image: (book.url === "-1") ? '/static/notfound.jpg' : book.url,  
                description: book.description ? book.description.split('#virgule')[0] : 'Aucune description disponible.',
                pages: book.number_of_pages || 'Non spécifié',
                rating: book.average_rating || 'Non spécifié',
                publisher: book.publisher_name || 'Non spécifié',
                author: book.author_name || 'Auteur inconnu',
                genres: Array.isArray(book.genre_names) ? book.genre_names.join(', ') : 'Non spécifié',
                id: book.id
            })))
        }
    ];

    const recoCategory = {
        name: 'Recommandations',
        books: filterUniqueBooks(reco.map(book => ({
            title: book.title || 'Titre inconnu',
            image: (book.url === "-1") ? '/static/notfound.jpg' : book.url,  
            description: book.description ? book.description.split('#virgule')[0] : 'Aucune description disponible.',
            pages: book.number_of_pages || 'Non spécifié',
            rating: book.average_rating || 'Non spécifié',
            publisher: book.publisher_name || 'Non spécifié',
            author: book.author_name || 'Auteur inconnu',
            genres: Array.isArray(book.genre_names) ? book.genre_names.join(', ') : 'Non spécifié',
            id: book.id
        })))
    };

    const allCategories = [recoCategory, ...categories];

    genreBooks.forEach(genreData => {
        if (genreData && genreData.books.length > 0) {
            allCategories.push({
                name: genreData.genre,
                books: filterUniqueBooks(genreData.books.map(book => ({
                    title: book.title || 'Titre inconnu',
                    image: (book.url === "-1") ? '/static/notfound.jpg' : book.url,  
                    description: book.description ? book.description.split('#virgule')[0] : 'Aucune description disponible.',
                    pages: book.number_of_pages || 'Non spécifié',
                    rating: book.average_rating || 'Non spécifié',
                    publisher: book.publisher_name || 'Non spécifié',
                    id: book.id
                })))
            });
        }
    });

    displayBooks(allCategories);


    const firstNonEmptyCategory = allCategories.find(category => category.books.length > 0);
    if (firstNonEmptyCategory) {
        const randomIndex = Math.floor(Math.random() * firstNonEmptyCategory.books.length);
        const selectedBook = firstNonEmptyCategory.books[randomIndex]; 
        showBookInfo(selectedBook);
    }
}





function displayBooks(categories) {
    const bookContainer = document.getElementById('book-container');
    bookContainer.innerHTML = ''; 
    
    categories.forEach(category => {
        console.log(`Affichage de la catégorie : ${category.name}, Nombre de livres : ${category.books.length}`);
        
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
                scrollTo({ top: 0 });
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
    const bookAuthors = document.getElementById('book-authors-num');
    const bookGenres = document.getElementById('book-genres-num');
    const bookid = document.getElementById('book-id-num');

    if (headerImage && bookTitle && bookDescription && bookPages && bookRating) {
        headerImage.src = book.image;
        bookTitle.textContent = book.title;
        bookDescription.textContent = book.description || 'Aucune description disponible.';
        bookPages.textContent = book.pages || 'Non spécifié';
        bookRating.textContent = book.rating || 'Non spécifié';
        bookPublisher.textContent = book.publisher || 'Non spécifié';
        bookAuthors.textContent = book.author || 'Non spécifié'; 
        bookGenres.textContent = book.genres || 'Non spécifié';   
        bookid.textContent = book.id;
    }

    onBookChange(book.id); 
}

window.onload = fetchBooks;
