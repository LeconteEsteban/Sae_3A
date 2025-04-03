function showNoResultsMessage(searchTerm) {
    const bookContainer = document.getElementById('book-container');
    const header = document.querySelector('header'); 

    bookContainer.innerHTML = ''; 
    bookContainer.classList.add('mt-10'); 

    const messageDiv = document.createElement('div');
    messageDiv.classList.add('text-center', 'mt-10', 'text-gray-500', 'text-xl');
    messageDiv.textContent = `Aucun livre trouvé pour la recherche "${searchTerm}". Essayez un autre terme !`;

    bookContainer.appendChild(messageDiv);


    if (header) {
        header.style.display = 'none';
    }

    document.getElementById("loading").style.display = "none"; 
    document.getElementById("content").style.display = "block";
}


async function fetchBooks() {
    const storageKey = 'booksData';
    const storageKeySearch = 'booksDataSearch';  
    const storageTimestampKey = 'booksDataTimestamp';
    const storageTimestampKeySearch = 'booksDataTimestampSearch';
    const storageLastSearch = 'lastSearchQuery';

    const storedData = localStorage.getItem(storageKey);
    const storedTimestamp = localStorage.getItem(storageTimestampKey);
    const storedDataSearch = localStorage.getItem(storageKeySearch);
    const storedTimestampSearch = localStorage.getItem(storageTimestampKeySearch);
    const lastSearch = localStorage.getItem(storageLastSearch);
    const searchTerm = localStorage.getItem('searchQuery');
    const now = Date.now();

    console.log("Recherche en cours pour le terme:", searchTerm);  

    document.getElementById("loading").style.display = "flex"; 
    document.getElementById("content").style.display = "none";

    let books = [];
    let searchBooks = [];

    // Vérification si on doit ignorer le cache
    const isSearchUpdated = searchTerm && searchTerm.trim() !== "" && searchTerm !== lastSearch;
    const isCacheValid = storedData && storedDataSearch && storedTimestamp && storedTimestampSearch &&
                         now - parseInt(storedTimestamp) < 30000 && now - parseInt(storedTimestampSearch) < 30000;

    if (!isSearchUpdated && isCacheValid) { 
        console.log('Données chargées depuis localStorage');
        books = JSON.parse(storedData);
        searchBooks = JSON.parse(storedDataSearch);
    } else {
        try {
            if (searchTerm && searchTerm.trim() !== "") {
                console.log("Nouvelle recherche détectée, récupération depuis l'API.");
                const response_search = await fetch(`/books/search/${encodeURIComponent(searchTerm)}?limit=30`);

                if (!response_search.ok) {
                    console.error('Erreur lors de la récupération des livres:', response_search.statusText);
                    showNoResultsMessage(searchTerm);
                    return;
                }

                searchBooks = await response_search.json();

                if (searchBooks.length === 0) {
                    console.log("Aucun livre trouvé pour :", searchTerm);
                    showNoResultsMessage(searchTerm);
                    return;
                }

                // Suppression des doublons dans searchBooks, et récupération des livres multi auteurs
                const uniqueBooks = new Map();
                searchBooks.forEach(book => {
                    if (uniqueBooks.has(book.id)) {
                        let existingBook = uniqueBooks.get(book.id);
                        
                        let newAuthors = book.author_names && book.author_names.length > 0
                            ? book.author_names.split(', ') 
                            : [];

                        if (book.author_name) {
                            newAuthors.push(book.author_name);
                        }
                
                        existingBook.author_names = [...new Set([...existingBook.author_names, ...newAuthors])];
                    } else {
                        let newAuthors = book.author_names && book.author_names.length > 0
                            ? book.author_names.split(', ') 
                            : [];
                
                        if (book.author_name) {
                            newAuthors.push(book.author_name);
                        }
                
                        book.author_names = newAuthors;
                        uniqueBooks.set(book.id, book);
                    }
                });
                
                
                searchBooks = Array.from(uniqueBooks.values());


                console.log("Livres trouvés pour la recherche (sans doublons) :", searchBooks);
                localStorage.setItem(storageKeySearch, JSON.stringify(searchBooks));
                localStorage.setItem(storageTimestampKeySearch, now.toString());
                localStorage.setItem(storageLastSearch, searchTerm);
            } else {
                console.log("Pas de terme de recherche, récupération des livres classiques.");
                const response = await fetch('/books/topbook/30');

                if (!response.ok) {
                    console.error('Erreur lors de la récupération des livres topbook:', response.statusText);
                    return;
                }

                books = await response.json();

                // Suppression des doublons dans books
                const uniqueTopBooks = new Map();
                books.forEach(book => {
                    if (!uniqueTopBooks.has(book.id)) {
                        uniqueTopBooks.set(book.id, book);
                    }
                });
                books = Array.from(uniqueTopBooks.values());

                localStorage.setItem(storageKey, JSON.stringify(books));
                localStorage.setItem(storageTimestampKey, now.toString());
            }
        } catch (error) {
            console.error('Erreur lors de la récupération des livres:', error);
            showNoResultsMessage("une erreur inattendue");
            return;
        }
    }

    processBooks(books, searchBooks);
    document.getElementById("loading").style.display = "none"; 
    document.getElementById("content").style.display = "block";
}

function processBooks(books, searchBooks = []) {
    const categories = [{
        name: searchBooks.length > 0 ? 'Résultats de Recherche' : 'Meilleurs Livres',
        books: (searchBooks.length > 0 ? searchBooks : books).map(book => ({
            id: book.id,
            title: book.title || 'Titre inconnu',
            image: (book.url === "-1") ? '/static/notfound.jpg' : book.url,  
            description: book.description ? book.description.split('#virgule')[0] : 'Aucune description disponible.',
            pages: book.number_of_pages || 'Non spécifié',
            rating: book.average_rating || 'Non spécifié',
            publisher: book.publisher_name || 'Non spécifié',
            author: Array.isArray(book.author_names) ? book.author_names.join(', ') : 'Auteur inconnu',
            genres: Array.isArray(book.genre_names) ? book.genre_names.join(', ') : 'Non spécifié',
            awards: Array.isArray(book.award_names) ? book.award_names.filter(a => a).join(', ') : 'Aucun prix'
        }))
    }];

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
                scrollTo({ top: 0 }); 
            });

            bookDiv.appendChild(bookImage);
            booksDiv.appendChild(bookDiv);
        });

        categoryDiv.appendChild(booksDiv);
        bookContainer.appendChild(categoryDiv);
    });
}

// Mise à jour du header
function showBookInfo(book) {
    const headerImage = document.getElementById('header-image');
    const bookTitle = document.getElementById('book-title');
    const bookDescription = document.getElementById('book-description');
    const bookPages = document.getElementById('book-pages-num');
    const bookRating = document.getElementById('book-rating-num');
    const bookPublisher = document.getElementById('book-publisher-num');
    const bookAuthors = document.getElementById('book-authors-num');
    const bookGenres = document.getElementById('book-genres-num');
    const bookAwards = document.getElementById('book-awards-num');
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
        bookAwards.textContent = book.awards || 'Aucun prix';
        bookid.textContent = book.id;

        
    }

    onBookChange(book.id); 
}

window.onload = fetchBooks;
