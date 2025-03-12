import { truncateDescription } from './utils.js';


function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
      return decodeURIComponent(parts.pop().split(';').shift());
  }
  return null;
}

function getIdAccount() {
  const userCookie = getCookie('user');
  if (userCookie) {
      const user = JSON.parse(userCookie);
      return user;
  }
}

async function fetchSimilarBooks(bookId, nBooks = 5) {
  try {
    const recResponse = await fetch(`/recommandations/similar/${bookId}/${nBooks}`);
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

async function fetchWishlist() {
  try {
    const response = await fetch(`/wishlist/${getIdAccount()}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    const wishlistBooks = await response.json();
    //console.log("Wishlist récupérée:", wishlistBooks);
    return wishlistBooks;
  } catch (error) {
    console.error("Erreur lors de la récupération de la wishlist:", error);
    return [];
  }
}

async function fetchRecommendations(wishlist) {
  let allRecommendations = [];
  const wishlistIds = new Set(wishlist.map(book => book.id));
  const addedIds = new Set();

  for (const book of wishlist) {
    const recommendations = await fetchSimilarBooks(book.id, 3);
    const filteredRecommendations = recommendations.filter(rec => 
      !wishlistIds.has(rec.id) && !addedIds.has(rec.id)
    );

    filteredRecommendations.forEach(rec => addedIds.add(rec.id));
    allRecommendations = [...allRecommendations, ...filteredRecommendations];
  }

  return allRecommendations;
}

function createPopupStructure() {
  let popup = document.getElementById("wishlist-popup");
  let overlay = document.getElementById("popup-overlay-wishlist");

  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "popup-overlay-wishlist";
    overlay.style.zIndex = "997";
    overlay.classList.add("popup-overlay-wishlist", "hidden");
    document.body.appendChild(overlay);
  }

  if (!popup) {
    popup = document.createElement("div");
    popup.id = "wishlist-popup";
    popup.classList.add("fixed", "flex", "items-center", "justify-center", "z-[998]","inset-0", "hidden", "bg-white", "mt-10");
    
    popup.innerHTML = `
      <div class="popup-content">
        <button
            id="close-wishlist-popup"
            class="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
          >
            <i class="fas fa-times"></i>
        </button>
        <h2 class="text-gray-800">Ma Wishlist</h2>
        <div id="wishlist-container">Chargement...</div>
        <h2 class="text-gray-800"l>Recommandations</h2>
        <div id="recommendations-container">Chargement...</div>
      </div>
    `;
    
    document.body.appendChild(popup);
    document.getElementById('close-wishlist-popup')?.addEventListener('click', closeWishlistPopup);
  }
}

async function showWishlistPopup() {
  createPopupStructure();
  const popup = document.getElementById("wishlist-popup");
  const overlay = document.getElementById("popup-overlay-wishlist");

  if (popup) {
    popup.style.display = "flex";
  }

  if (overlay) {
    overlay.style.display = "flex"; 
  }
  
  overlay.classList.add("show");
  popup.classList.add("show");
  overlay.classList.remove("hidden");
  popup.classList.remove("hidden");

  const wishlistContainer = document.getElementById("wishlist-container");

  wishlistContainer.innerHTML = "Chargement...";

  const wishlist = await fetchWishlist();
  wishlistContainer.innerHTML = wishlist.length ? wishlist.map(book => `
    <div data-book-id="${book.id}" class="book group relative mr-4 mb-10">
      <img src="${book.url !== "-1" ? book.url : "/static/notfound.jpg"}" 
           alt="Couverture de ${book.title}" 
           class="w-full h-64 object-cover rounded-lg shadow-md transition-transform duration-300">
      
      <div class="absolute inset-0 bg-white bg-opacity-95 flex flex-col opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-lg p-4">
        <h3 class="text-lg font-bold text-gray-800 mb-1 line-clamp-2">${book.title}</h3>
        <p class="text-sm text-gray-600 mb-1">${book.author_name || "Auteur inconnu"}</p>
        <p class="text-xs text-gray-700 mb-2">${book.description ? book.description.slice(0, 100) + "..." : "Pas de description disponible."}</p>
        
        <ul class="flex flex-wrap gap-2 mb-3">
          ${(book.genre_names?.slice(0, 2) || []).map(genre =>
            `<li class="bg-gray-100 text-gray-700 px-2 py-1 text-xs rounded-full border border-gray-300">${genre}</li>`
          ).join("")}
        </ul>
        
         <div class="flex gap-2 mt-auto justify-between w-full">
            <i class="fas fa-bookmark text-gray-500 text-2xl cursor-pointer switch-button"></i>
            <i class="fas fa-minus text-gray-500 text-2xl hover:text-blue-600 cursor-pointer moins-button"></i>
            <i class="fas fa-eye text-gray-500 text-2xl hover:text-green-600 cursor-pointer eye-button"></i>
          </div>
      </div>
    </div>
  `).join("") : "<p class='text-gray-500 text-center py-8'>Votre wishlist est vide.</p>";

  const recommendations = await fetchRecommendations(wishlist);
  addSimilarBooks(recommendations);
}

function addSimilarBooks(books) {
  const similarBooksContainer = document.getElementById("recommendations-container");
  similarBooksContainer.innerHTML = "";
  
  books.forEach((book) => {
    const bookCard = document.createElement("div");
    bookCard.classList.add("similar-book-card", "reco-wishlist", "bg-white", "rounded-lg", "relative", "group", "transition-transform", "duration-300", "zoom-hover", "mr-4", "mb-4");
    
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
            <i class="fas fa-bookmark text-gray-500 text-2xl cursor-pointer bookmark"></i>
            <i class="fas fa-heart text-gray-500 text-2xl cursor-pointer like-button hidden"></i>
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
    const slideDiv = event.target.closest('[data-book-id]');
    const bookId = slideDiv.dataset.bookId;

    if (event.target.classList.contains("disabled")) return;
    
    event.target.classList.add("disabled", "cursor-not-allowed");
    
    try {
      const response = await fetch(`/wishlist/remove/${bookId}/${getIdAccount()}`, {
        method: "DELETE"
      });

      if (response.ok) {
        slideDiv.remove();
        const wishlist = await fetchWishlist();
        const newRecommendations = await fetchRecommendations(wishlist);
        addSimilarBooks(newRecommendations);
      } else {
        console.error("Erreur lors de la suppression de la wishlist");
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
    const slideDiv = event.target.closest('[data-book-id]');
    const bookId = slideDiv.dataset.bookId;


    if (event.target.classList.contains("disabled")) return;
    
    event.target.classList.add("disabled", "cursor-not-allowed");
    
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

document.addEventListener("click", async (event) => {
  if (event.target.classList.contains("switch-button")) {
    const slideDiv = event.target.closest('[data-book-id]');
    const bookId = slideDiv.dataset.bookId;

    if (event.target.classList.contains("disabled")) return;
    
    event.target.classList.add("disabled", "cursor-not-allowed");

    try {
      const response = await fetch(`read/${getIdAccount()}/${bookId}`,{
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        }
      });

      if (response.ok) {
        slideDiv.remove();
        const wishlist = await fetchWishlist();
        const newRecommendations = await fetchRecommendations(wishlist);
        addSimilarBooks(newRecommendations);
      } else {
        console.error("Erreur lors de la switch de la wishlist");
        event.target.classList.remove("disabled", "cursor-not-allowed");
      }
    } catch (error) {
      console.error("Erreur réseau :", error);
      event.target.classList.remove("disabled", "cursor-not-allowed");
    }
    
    try {
      const response = await fetch(`/wishlist/remove/${bookId}/${getIdAccount()}`, {
        method: "DELETE"
      });

      if (response.ok) {
        slideDiv.remove();
        const wishlist = await fetchWishlist();
        const newRecommendations = await fetchRecommendations(wishlist);
        addSimilarBooks(newRecommendations);
      } else {
        console.error("Erreur lors de la suppression de la wishlist");
        event.target.classList.remove("disabled", "cursor-not-allowed");
      }
    } catch (error) {
      console.error("Erreur réseau :", error);
      event.target.classList.remove("disabled", "cursor-not-allowed");
    }
  }
});

function closeWishlistPopup() {
  const popup = document.getElementById("wishlist-popup");
  const overlay = document.getElementById("popup-overlay-wishlist");

  if (popup) {
      popup.classList.add("hidden");
      popup.style.display = "none"; 
  }

  if (overlay) {
      overlay.classList.add("hidden");
      overlay.style.display = "none";
  }
}

document.addEventListener("click", (event) => {
  const overlay = document.getElementById("popup-overlay-wishlist");

  if (event.target === overlay) {
    closeWishlistPopup();
  }
});

window.showWishlistPopup = showWishlistPopup