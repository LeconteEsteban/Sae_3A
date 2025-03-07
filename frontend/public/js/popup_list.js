import { truncateDescription } from './utils.js';

let currentSimilarBooks = [];

async function fetchSimilarBooks(bookId, nBooks = 3) {
  try {
    const recResponse = await fetch(`/recommandations/book/${bookId}/${nBooks}`);
    if (!recResponse.ok) throw new Error(`HTTP ${recResponse.status}`);
    
    const recommendedBooks = await recResponse.json();
    
 
    const validBooks = recommendedBooks.filter(book => 
      book?.id && book?.title && book?.url
    );
    
    console.log("Livres similaires validés:", validBooks);
    return validBooks;

  } catch (error) {
    console.error("Erreur lors de la récupération des recommandations:", error);
    return [];
  }
}

async function fetchWishlist() {
  try {
    const response = await fetch(`/wishlist/${getIdAccount()}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    const wishlistBooks = await response.json();
    console.log("Wishlist récupérée:", wishlistBooks);
    return wishlistBooks;
  } catch (error) {
    console.error("Erreur lors de la récupération de la wishlist:", error);
    return [];
  }
}

async function fetchRecommendations(wishlist) {
  let allRecommendations = [];
  for (const book of wishlist) {
    const recommendations = await fetchSimilarBooks(book.id, 3); // 3 recommandations par livre
    allRecommendations = [...allRecommendations, ...recommendations];
  }
  return allRecommendations;
}

function createPopupStructure() {
  let popup = document.getElementById("wishlist-popup");
  let overlay = document.getElementById("popup-overlay-wishlist");

  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "popup-overlay-wishlist";
    overlay.classList.add("popup-overlay-wishlist", "hidden");
    document.body.appendChild(overlay);
  }

  if (!popup) {
    popup = document.createElement("div");
    popup.id = "wishlist-popup";
    popup.classList.add("fixed", "flex", "items-center", "justify-center", "z-[999]","inset-0", "hidden");
    
    popup.innerHTML = `
      <div class="popup-content">
        <button
            id="close-popup"
            class="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
          >
            <i class="fas fa-times"></i>
        </button>
        <h2>Ma Wishlist</h2>
        <div id="wishlist-container">Chargement...</div>
        <h2>Recommandations</h2>
        <div id="recommendations-container">Chargement...</div>
      </div>
    `;
    
    document.body.appendChild(popup);
  }
}

async function showWishlistPopup() {
  createPopupStructure();
  const popup = document.getElementById("wishlist-popup");
  const overlay = document.getElementById("popup-overlay-wishlist");
  
  overlay.classList.add("show");
  popup.classList.add("show");
  overlay.classList.remove("hidden");
  popup.classList.remove("hidden");

  const wishlistContainer = document.getElementById("wishlist-container");

  wishlistContainer.innerHTML = "Chargement...";

  const wishlist = await fetchWishlist();
  wishlistContainer.innerHTML = wishlist.length ? wishlist.map(book => `
    <div data-book-id="${book.id}" class="book">
      <img src="${book.url !== "-1" ? book.url : "/static/notfound.jpg"}" 
           alt="Couverture de ${book.title}">
      <div class="book-details">
        <h3>${book.title}</h3>
        <p>${book.author_name || "Auteur inconnu"}</p>
        <p>${book.description ? book.description.slice(0, 100) + "..." : "Pas de description disponible."}</p>
        <div class="tags">
          ${(book.genre_names?.slice(0, 2) || []).map(genre =>
            `<span class="tag">${genre}</span>`
          ).join("")}
        </div>
        <div class="actions">
          <button class="primary like-button"><i class="fas fa-heart"></i></button>
          <button class="secondary moins-button"><i class="fas fa-minus"></i></button>
          <button class="secondary eye-button"><i class="fas fa-eye"></i></button>
        </div>
      </div>
    </div>
  `).join("") : "<p>Votre wishlist est vide.</p>";

  const recommendations = await fetchRecommendations(wishlist);
  addSimilarBooks(recommendations);
}

function addSimilarBooks(books) {
  const similarBooksContainer = document.getElementById("recommendations-container");
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

document.addEventListener("click", async (event) => {
  if (event.target.classList.contains("moins-button")) {
    const bookId = event.target.getAttribute("data-book-id");

    if (event.target.classList.contains("disabled")) return;
    
    event.target.classList.add("disabled", "cursor-not-allowed");
    console.log("idAccount", getIdAccount());
    console.log("Ajout du livre à la wishlist", bookId);
    try {
      const response = await fetch(`/wishlist/remove/${bookId}/${getIdAccount()}`);

      if (response.ok) {
        event.target.classList.replace("text-gray-500", "text-red-500"); 
      } else {
        console.error("Erreur lors de la suppresion à la wishlist");
        event.target.classList.remove("disabled", "cursor-not-allowed");
      }
    } catch (error) {
      console.error("Erreur réseau :", error);
      event.target.classList.remove("disabled", "cursor-not-allowed");
    }
  }
});

document.addEventListener("click", async (event) => {
  if (event.target.classList.contains("plus-button")) {
    const bookId = event.target.getAttribute("data-book-id");

    if (event.target.classList.contains("disabled")) return;
    
    event.target.classList.add("disabled", "cursor-not-allowed");
    console.log("idAccount", getIdAccount());
    console.log("Ajout du livre à la wishlist", bookId);
    try {
      const response = await fetch(`/wishlist/add/${bookId}/${getIdAccount()}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        }
      });

      if (response.ok) {
        event.target.classList.replace("text-gray-500", "text-red-500"); 
      } else {
        console.error("Erreur lors de l'ajout à la wishlist");
        event.target.classList.remove("disabled", "cursor-not-allowed");
      }
    } catch (error) {
      console.error("Erreur réseau :", error);
      event.target.classList.remove("disabled", "cursor-not-allowed");
    }
  }
});

window.showWishlistPopup = showWishlistPopup