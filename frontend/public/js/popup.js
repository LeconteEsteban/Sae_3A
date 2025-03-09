let currentSimilarBooks = [];

async function fetchSimilarBooks(bookId, nBooks = 30) {
  try {
    const recResponse = await fetch(`/recommandations/book/${bookId}/${nBooks}`);
    if (!recResponse.ok) throw new Error(`HTTP ${recResponse.status}`);
    
    const recommendedBooks = await recResponse.json();
    
 
    const validBooks = recommendedBooks.filter(book => 
      book?.id && book?.title && book?.url
    );
    
    //console.log("Livres similaires validés:", validBooks);
    return validBooks;

  } catch (error) {
    console.error("Erreur lors de la récupération des recommandations:", error);
    return [];
  }
}

function truncateDescription(description, maxLength) {
  if (description && description.length > maxLength) {
    return description.substring(0, maxLength) + "...";
  }
  return description || "Pas de description";
}

function updatePopup(book) {
  document.getElementById("similar-books-container").scrollTop = 0;
  document.getElementById("book-cover").src = book.url !== "-1" ? book.url : "/static/notfound.jpg";
  document.getElementById("book-title").textContent = book.title;
  document.getElementById("book-author").textContent = book.author_name;
  document.getElementById("book-description").textContent = book.description ?
    book.description.replaceAll("#virgule", ",") : "Pas de description";
  document.getElementById("book-genres").innerHTML = book.genre_names ?
    book.genre_names.map(genre =>
      `<span class="bg-gray-300 text-black px-2 py-1 text-xs rounded">${genre}</span>`
    ).join("") : "";
  document.getElementById("book-page").textContent = book.number_of_pages || "N/A";
  document.getElementById("book-publisher").textContent = book.publisher_name || "N/A";
  document.getElementById("book-isbn").textContent = book.isbn13 || "N/A";
}

function addSimilarBooks(books) {
  const similarBooksContainer = document.getElementById("similar-books-container");
  similarBooksContainer.innerHTML = "";
  
  books.forEach((book) => {
    const bookCard = document.createElement("div");
    bookCard.classList.add("similar-book-card", "bg-white", "rounded-lg", "relative", "group", "transition-transform", "duration-300", "zoom-hover");
    
    const truncatedDescription = truncateDescription(
      book.description?.replaceAll("#virgule", ",") || "Pas de description",
      110
    );

    bookCard.innerHTML = `
      <div data-book-id="${book.id}" class="bg-white shadow-lg rounded-lg p-4 flex flex-col items-center relative w-50 h-80">
        <img src="${book.url !== "-1" ? book.url : "/static/notfound.jpg"}" 
             alt="Couverture de ${book.title}" 
             class="w-32 h-44 object-cover rounded transition-transform duration-300">
        <h3 class="text-lg font-bold text-gray-800 mt-2 text-center">${book.title}</h3>

        <div class="absolute inset-0 bg-white bg-opacity-95 flex flex-col text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-lg p-4">
          <h3 class="text-lg text-black font-bold mb-1">${book.title}</h3>
          <p class="text-xs text-black font-semibold mb-1">${book.author_name || "Auteur inconnu"}</p>
          
          <p class="text-xs text-black mb-2">${truncatedDescription}</p>
          <ul class="flex gap-2 mb-3">
            ${(book.genre_names?.slice(0, 2) || []).map(genre =>
              `<li class="bg-white text-black border border-black px-2 py-1 text-xs rounded">${genre}</li>`
            ).join("")}
          </ul>
          <div class="flex gap-2 mt-auto justify-between w-full">
            <i class="fas fa-heart text-gray-500 text-2xl cursor-pointer like-button"></i>
            <i class="fas fa-plus text-gray-500 text-2xl cursor-pointer plus-button"></i>
            <i class="fas fa-eye text-gray-500 text-2xl cursor-pointer eye-button"></i>
          </div>
        </div>
      </div>
    `;
    similarBooksContainer.appendChild(bookCard);
  });
}

export function showPopup(book) {
  const popup = document.getElementById("book-popup");
  updatePopup(book);
  
  fetchSimilarBooks(book.id)
    .then(books => {
      currentSimilarBooks = books;
      addSimilarBooks(books);
    });

  popup.classList.remove("hidden");
  popup.classList.add("show");
}



