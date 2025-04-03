// Fonction pour éviter les doublons dans le cadre d'un livre multi-genres
function mergeBooksById(books) {
    const bookMap = new Map();

    books.forEach(book => {
        if (!bookMap.has(book.id)) {
            bookMap.set(book.id, { ...book, genre_names: new Set(book.genre_names) });
        } else {
            bookMap.get(book.id).genre_names = new Set([
                ...bookMap.get(book.id).genre_names,
                ...book.genre_names
            ]);
        }
    });

    return Array.from(bookMap.values()).map(book => ({
        ...book,
        genre_names: Array.from(book.genre_names)
    }));
}

async function getBookRating(userId, bookId) {
    try {
        const response = await fetch(`/reviews/user/${userId}/${bookId}`);
        if (!response.ok) return null;

        const data = await response.json();
        return data.note;
    } catch (error) {
        console.error(`Erreur lors de la récupération de la note pour le livre ${bookId}:`, error);
        return null;
    }
}

document.addEventListener('alpine:init', () => {
    Alpine.data('bookList', () => ({
        books: [],
        booksLike: [],
        genres: [],
        selectedGenre: "",
        searchAuthor: "",
        searchTitle: "", 
        minRating: 0,

        async init() {
            await this.loadBooks();
            this.extractGenres();
        },

        async moveToWishlist(book) {
            const userId = localStorage.getItem("user_id");
            if (!userId) return;
        
            // Met à jour l'affichage immédiatement pour un effet instantané
            this.books = this.books.filter(b => b.id !== book.id);
            this.booksLike = this.booksLike.filter(b => b.id !== book.id);
        
            try {
                // Supprime des livres lus
                const deleteResponse = await fetch(`/read/${userId}/${book.id}`, {
                    method: "DELETE",
                    headers: { "Content-Type": "application/json" }
                });
        
                if (!deleteResponse.ok) {
                    console.warn(`Échec de la suppression du livre ${book.id}, statut: ${deleteResponse.status}`);
                }
        
                // Ajoute à la wishlist (avec la bonne route)
                const addResponse = await fetch(`/wishlist/add/${book.id}/${userId}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" }
                });
        
                if (!addResponse.ok) {
                    throw new Error(`Erreur HTTP! statut: ${addResponse.status}`);
                }
        
            } catch (error) {
                console.error(`Erreur lors du déplacement du livre ${book.id} en wishlist:`, error);
            }
        },
        
        

        async loadBooks() {
            const userId = localStorage.getItem("user_id");
            if (!userId) return;
        
            try {
                const [readData, readDataLike] = await Promise.all([
                    getReadBooks(userId),
                    getReadBooksLike(userId)
                ]);
        
                const bookIds = readData.map(item => item.book_id || Number(item)).filter(id => !isNaN(id));
                const bookIdsLike = readDataLike.map(item => Number(item.book_id) || Number(item)).filter(id => !isNaN(id));

        
                const books = await Promise.all(bookIds.map(async (bookId) => {
                    const book = await getBookDetails(bookId);
                    if (book) {
                        book.rating = (await getBookRating(userId, bookId)) || 0;
                    }
                    return book;
                }));
        
                const booksLike = await Promise.all(bookIdsLike.map(async (bookId) => {
                    const book = await getBookDetails(bookId);
                    if (book) {
                        book.rating = (await getBookRating(userId, bookId)) || 0;
                    }
                    return book;
                }));
        
                const allBooks = mergeBooksById([...books, ...booksLike]);
        
                this.books = allBooks;
                this.booksLike = allBooks.filter(book => book.rating > 0);
        
            } catch (error) {
                console.error("Erreur lors du chargement des livres :", error);
            }
        },

        extractGenres() {
            this.genres = [...new Set(this.books.flatMap(book => book.genre_names))];
        },

        async rateBook(book, rating) {
            const userId = localStorage.getItem("user_id");
            if (!userId) return;
        
            try {
                const response = await fetch(`/reviews/${userId}/${book.id}/${rating}`, {
                    method: "POST", 
                    headers: { "Content-Type": "application/json" }
                });
        
                if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);
        
                book.rating = rating;
                if (!this.booksLike.some(b => b.id === book.id)) {
                    this.booksLike.push(book);
                }
        
            } catch (error) {
                console.error(`Erreur lors de la notation du livre ${book.id}:`, error);
            }
        },

        async removeRating(book) {
            const userId = localStorage.getItem("user_id");
            if (!userId) return;
        
            try {
                const response = await fetch(`/reviews/${userId}/${book.id}`, {
                    method: "DELETE",
                    headers: { "Content-Type": "application/json" }
                });
        
                if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);
        
                book.rating = 0;
                this.books = this.books.map(b => (b.id === book.id ? { ...b, rating: 0 } : b));
                this.booksLike = this.booksLike.filter(b => b.id !== book.id);
        
            } catch (error) {
                console.error(`Erreur lors de la suppression de la note du livre ${book.id}:`, error);
            }
        },

        async removeBook(book) {
            const userId = localStorage.getItem("user_id");
            if (!userId) return;
        
            try {
                const response = await fetch(`/read/${userId}/${book.id}`, {
                    method: "DELETE",
                    headers: { "Content-Type": "application/json" }
                });
        
                if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);
        
                // Supprime le livre de la liste
                this.books = this.books.filter(b => b.id !== book.id);
                this.booksLike = this.booksLike.filter(b => b.id !== book.id);
        
            } catch (error) {
                console.error(`Erreur lors de la suppression du livre ${book.id} des livres lus:`, error);
            }
        },

        get filteredBooks() {
            return this.books.filter(book =>
                (!this.selectedGenre || book.genre_names.includes(this.selectedGenre)) &&
                (!this.searchAuthor || book.author_name?.toLowerCase().includes(this.searchAuthor.toLowerCase())) &&
                (!this.searchTitle || book.title?.toLowerCase().includes(this.searchTitle.toLowerCase())) &&
                (book.rating >= this.minRating)
            );
        },

        get filteredBooksLike() {
            return this.booksLike.filter(book =>
                (!this.selectedGenre || book.genre_names.includes(this.selectedGenre)) &&
                (!this.searchAuthor || book.author_name?.toLowerCase().includes(this.searchAuthor.toLowerCase())) &&
                (!this.searchTitle || book.title?.toLowerCase().includes(this.searchTitle.toLowerCase())) &&
                (book.rating >= this.minRating)
            );
        }
    }));
});



// Fonctions pour récupérer les livres depuis l'API
async function getReadBooks(userId) {
    try {
        const response = await fetch(`/read/${userId}`);
        if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error("Erreur lors de la récupération des livres lus:", error);
        return [];
    }
}

async function getReadBooksLike(userId) {
    try {
        const response = await fetch(`/reviews/${userId}/noted-books`);
        if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error("Erreur lors de la récupération des livres likés:", error);
        return [];
    }
}

async function getBookDetails(bookId) {
    try {
        bookId = parseInt(bookId, 10);
        if (isNaN(bookId)) throw new Error(`ID du livre invalide: ${bookId}`);

        const response = await fetch(`/books/${bookId}`);
        if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);

        return await response.json();
    } catch (error) {
        return null;
    }
}
