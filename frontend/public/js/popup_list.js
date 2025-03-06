let currentSimilarBooks = [];

async function fetchSimilarBooks(bookId, nBooks = 30) {
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
    popup.classList.add("popup-container", "hidden");
    
    popup.innerHTML = `
      <div class="popup-content">
        <h2>Ma Wishlist</h2>
        <div id="wishlist-container">Chargement...</div>
        <h2>Recommandations</h2>
        <div id="recommendations-container">Chargement...</div>
        <button onclick="closePopup()">Fermer</button>
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

  const wishlistContainer = document.getElementById("wishlist-container");
  const recommendationsContainer = document.getElementById("recommendations-container");

  wishlistContainer.innerHTML = "Chargement...";
  recommendationsContainer.innerHTML = "";

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
          <button class="secondary plus-button"><i class="fas fa-plus"></i></button>
          <button class="secondary eye-button"><i class="fas fa-eye"></i></button>
        </div>
      </div>
    </div>
  `).join("") : "<p>Votre wishlist est vide.</p>";

  const recommendations = await fetchRecommendations(wishlist);
  addSimilarBooks(recommendations, recommendationsContainer);
}

document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("popup-overlay-wishlist");

  if (overlay) {
    overlay.addEventListener("click", closeWishlistPopup);
  }
});

function closePopup() {
  const popup = document.getElementById("wishlist-popup");
  popup.classList.remove("show");
  popup.classList.add("hide");
  setTimeout(() => {
    popup.classList.add("hidden");
    popup.classList.remove("hide");
  }, 300);
}

function addSimilarBooks(books, container) {
  container.innerHTML = books.length ? books.map(book => `
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
          <button class="secondary plus-button"><i class="fas fa-plus"></i></button>
          <button class="secondary eye-button"><i class="fas fa-eye"></i></button>
        </div>
      </div>
    </div>
  `).join("") : "<p>Aucune recommandation disponible.</p>";
}

window.showWishlistPopup = showWishlistPopup