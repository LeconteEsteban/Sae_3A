async function fetchBookWeights() {
    try {
        const storedData = localStorage.getItem('bookWeights');
        if (storedData) {
            const { books, timestamp } = JSON.parse(storedData);
            const storedDate = new Date(timestamp);
            const currentDate = new Date();
            const oneWeekInMillis = 7 * 24 * 60 * 60 * 1000; 

            if (currentDate - storedDate <= oneWeekInMillis) {
                return books;
            }
        }

        const response = await fetch('/statistique/book');
        if (!response.ok) {
            throw new Error('Erreur lors de la récupération des pondérations');
        }

        const data = await response.json();
        const books = data.books || [];

        const storageData = {
            books,
            timestamp: new Date().toISOString()
        };
        localStorage.setItem('bookWeights', JSON.stringify(storageData));

        return books;

    } catch (error) {
        console.error("Erreur lors de la récupération des données :", error);
        return [];
    }
}


async function calculateBookPurchases(totalBooks = 10000) {
    try {
        const books = await fetchBookWeights();
        
        if (books.length === 0) {
            console.warn("Aucun livre trouvé.");
            return [];
        }

        const totalWeight = books.reduce((sum, book) => sum + book.adjusted_weight, 0);

        if (totalWeight === 0) {
            console.warn("La somme des pondérations est de 0.");
            return [];
        }

        let bookPurchases = books
            .map(book => ({
                title: book.title,
                url: book.url,
                genre: book.genres,
                rating: book.rating,
                count: Math.floor((book.adjusted_weight / totalWeight) * totalBooks),
            }))
            .filter(book => book.count > 0);

        let totalCount = bookPurchases.reduce((sum, book) => sum + book.count, 0);

        bookPurchases = bookPurchases.map(book => {
            if (book.count > 500) {
                return {
                    ...book,
                    count: 500,
                };
            }
            return book;
        });

        let newTotalCount = bookPurchases.reduce((sum, book) => sum + book.count, 0);
        let difference = totalBooks - newTotalCount;

        if (difference !== 0) {
            const remainingBooks = bookPurchases.filter(book => book.count < 500);
            let index = 0;

            while (difference !== 0 && remainingBooks.length > 0) {
                const book = remainingBooks[index % remainingBooks.length];
                const availableSpace = 500 - book.count;
                const adjustment = Math.min(difference, availableSpace);
                
                book.count += adjustment;
                difference -= adjustment;
                index++;
            }
        }

        console.log(bookPurchases);
        return bookPurchases;
    } catch (error) {
        console.error("Erreur lors du calcul des achats de livres :", error);
        return [];
    }
}
