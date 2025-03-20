//avoir l'id avec l'url, les cookies ne marche pas
function getIdAccount() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('userId');
}


async function getReadBooks(userId) {
    try {
        const response = await fetch(`/read/${userId}`);
        if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);
        const data = await response.json();
        console.log('Livres lus récupérés:', data);
        return data;
    } catch (error) {
        console.error("Erreur lors de la récupération des livres lus:", error);
        return [];
    }
}


async function getReadBooksLike(userId) {
    try {
        const response = await fetch(`/reviews/${userId}/noted-books`);
        console.log(response)
        if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);
        console.log(response)
        return await response.json();
    } catch (error) {
        console.error("Erreur lors de la récupération des livres lus:", error);
        return [];
    }
}



async function getBookDetails(bookId) {
    try {
        const response = await fetch(`/books/${bookId}`);
        if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error(`Erreur lors de la récupération du livre ${bookId}:`, error);
        return null;
    }
}

async function loadBooks() {
    const userId = getIdAccount();
    if (!userId) {
        console.error('Aucun userId trouvé dans l\'URL.');
        return;
    }

    // Suppose que chaque élément est un objet avec une propriété book_id
    const readData = await getReadBooks(userId);
    const readDataLike = await getReadBooksLike(userId);
    
    // Si readData et readDataLike contiennent des objets, extrais l'ID avec .book_id
    const bookIds = readData.map(item => item.book_id || item); // Si déjà un ID, garde-le
    const bookIdsLike = readDataLike.map(item => item.book_id || item);
    
    const books = await Promise.all(bookIds.map(id => getBookDetails(id)));
    const booksLike = await Promise.all(bookIdsLike.map(id => getBookDetails(id)));
    
    renderBooks(books.filter(book => book !== null)); 
    renderBooksLike(booksLike.filter(book => book !== null));
}


function renderBooks(books) {
    const container = document.getElementById("livrelu");
    container.innerHTML = ""; 

    if (books.length === 0) {
        container.innerHTML = "<p>Aucun livre trouvé.</p>";
        return;
    }

    books.forEach(book => {
        const bookDiv = document.createElement("div");
        
        bookDiv.classList.add("book-card");
        bookDiv.innerHTML = `
            <img src="${book.url !== "-1" ? book.url : "/static/notfound.jpg"}" 
                 alt="Couverture de ${book.title}" 
                 style="width:100px; height:150px;">
            <h3>${book.title}</h3>
        `;


        container.appendChild(bookDiv);
    });
}

function renderBooksLike(books){
    const container = document.getElementById("livrelike");
    container.innerHTML = ""; 

    if (books.length === 0) {
        container.innerHTML = "<p>Aucun livre liké.</p>";
        return;
    }

    books.forEach(book => {
        const bookDiv = document.createElement("div");
        
        bookDiv.classList.add("book-card");
        bookDiv.innerHTML = `
            <img src="${book.url !== "-1" ? book.url : "/static/notfound.jpg"}" 
                 alt="Couverture de ${book.title}" 
                 style="width:100px; height:150px;">
            <h3>${book.title}</h3>
        `;


        container.appendChild(bookDiv);
    });
}

document.addEventListener("DOMContentLoaded", loadBooks);

