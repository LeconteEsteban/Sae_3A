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
document.addEventListener('alpine:init', () => {
    Alpine.store('bookList', {
        books: [],
        genres: [],
        selectedGenre: "",
        searchAuthor: "",
        searchTitle: "",

        async loadBooks() {
            const userId = localStorage.getItem("user_id");
            if (!userId) return;

            try {
                const readData = await getReadBooks(userId);
                if (!Array.isArray(readData)) {
                    throw new Error("readData n'est pas un tableau");
                }

                const bookIds = readData.map(item => item.id || Number(item));
                const books = await Promise.all(bookIds.map(getBookDetails));

                this.books = mergeBooksById(books.filter(book => book !== null));
                this.extractGenres(); // Mets à jour les genres après le chargement

            } catch (error) {
                console.error("Erreur lors du chargement des livres :", error);
            }
        },

        async bookread(book) {
            const userId = localStorage.getItem("user_id");
            if (!userId) return;

            try {
                // Supprime le livre de la wishlist
                const response = await fetch(`/wishlist/remove/${book}/${userId}`, {
                    method: "DELETE",
                    headers: { "Content-Type": "application/json" }
                });

                if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);

                // Ajoute aux livres lus
                const responseR = await fetch(`/read/${userId}/${book}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" }
                });

                if (!responseR.ok) throw new Error(`Erreur HTTP! statut: ${responseR.status}`);

                // Mise à jour instantanée
                this.books = this.books.filter(b => b.id !== book);

                // Recharge les livres pour s'assurer de la mise à jour
                await this.loadBooks();

                return await responseR.json();

            } catch (error) {
                console.error("Erreur lors du déplacement du livre en livres lus:", error);
                return [];
            }
        },

        async removeWishlist(book) {
            try {
                const userId = localStorage.getItem("user_id");
                if (!userId) return;

                const response = await fetch(`/wishlist/remove/${book}/${userId}`, {
                    method: 'DELETE',
                    headers: { "Content-Type": "application/json" }
                });

                if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);

                // Mise à jour instantanée
                this.books = this.books.filter(b => b.id !== book);

                await this.loadBooks();

                return await response.json();
            } catch (error) {
                console.error("Erreur lors de la suppression du livre de la wishlist:", error);
                return [];
            }
        },

        extractGenres() {
            let allGenres = this.books.map(book => book.genre_names).flat();
            this.genres = [...new Set(allGenres)];
        },

        get filteredBooks() {
            return this.books.filter(book => {
                const matchesGenre = this.selectedGenre === "" || 
                    (Array.isArray(book.genre_names) && book.genre_names.includes(this.selectedGenre));
                const matchesAuthor = this.searchAuthor === "" || 
                    (book.author_name && book.author_name.toLowerCase().includes(this.searchAuthor.toLowerCase()));
                const matchesTitle = this.searchTitle === "" || 
                    (book.title && book.title.toLowerCase().includes(this.searchTitle.toLowerCase()));

                return matchesGenre && matchesAuthor && matchesTitle;
            });
        }
    });

    // 🔥 On charge les livres dès l'initialisation
    Alpine.store('bookList').loadBooks();
});





// Fonctions pour récupérer les livres depuis l'API
async function getReadBooks(userId) {
    try {
        const response = await fetch(`/wishlist/${userId}`);
        if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error("Erreur lors de la récupération des livres lus:", error);
        return [];
    }
}

async function getBookDetails(bookId) {
    try {
        bookId = parseInt(bookId, 10);
        if (isNaN(bookId)) {
            throw new Error(`ID du livre invalide: ${bookId}`);
        }

        const response = await fetch(`/books/${bookId}`);

        if (!response.ok) {
            throw new Error(`Erreur HTTP! statut: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        return null;
    }
}





