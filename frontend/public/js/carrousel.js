async function fetchBooks() {
  let booksData = [];
  console.log("Debut fetch");

  try {
    const response = await fetch("/books/topbook/30");
    booksData = await response.json();
    console.log("Données récupérées :", booksData);
  } catch (error) {
    console.error("Erreur lors de la récupération des données :", error);
  }

  console.log("fin fetch");
  return booksData;
}
async function fetchSimilarBooks(bookId, nBooks = 60) {
  try {
    const recResponse = await fetch(`/recommandations/book/${bookId}/${nBooks}`);
    const recommendedBooks = await recResponse.json();
    
    console.log("Structure des recommandations:", JSON.stringify(recommendedBooks, null, 2));

    const ids = recommendedBooks.map(item => item.id); 
    console.log("IDs extraits:", ids);

    const booksPromises = ids.map(async (id) => {
      try {
        const bookResponse = await fetch(`/books/${id}`);
        if (!bookResponse.ok) throw new Error(`HTTP ${bookResponse.status}`);
        return await bookResponse.json();
      } catch (error) {
        console.error(`Échec sur le livre ${id}:`, error.message);
        return null;
      }
    });

    const booksResults = await Promise.allSettled(booksPromises);
    const successfulBooks = booksResults
      .filter(result => result.status === 'fulfilled' && result.value)
      .map(result => result.value);

    console.log("Livres similaires récupérés:", successfulBooks);
    return successfulBooks;

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

let currentSimilarBooks = []; // Stockage des livres similaires actuels

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

async function initializeCarousel() {
  const booksData = await fetchBooks();
  const popup = document.getElementById("book-popup");
  const closePopupButton = document.getElementById("close-popup");

  if (!booksData?.length) {
    console.error("Aucune donnée récupérée");
    return;
  }

  // Initialisation du carousel
  const swiperWrapper = document.querySelector(".swiper-wrapper");
  swiperWrapper.innerHTML = "";

  booksData.forEach(book => {
    const slide = document.createElement("div");
    slide.classList.add("swiper-slide", "relative", "group", "transition-transform", "duration-300", "zoom-hover");
    
    slide.innerHTML = `
      <div data-book-id="${book.id}" class="bg-white shadow-lg rounded-lg p-4 flex flex-col items-center justify-center relative w-50 h-80">
        <img src="${book.url !== "-1" ? book.url : "/static/notfound.jpg"}" 
             alt="Couverture de ${book.title}" 
             class="w-32 h-44 object-cover rounded transition-transform duration-300">
        <h3 class="text-lg font-bold text-gray-800 mt-2 text-center">${book.title}</h3>
        
        <div class="absolute inset-0 bg-white bg-opacity-95 flex flex-col text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-lg p-4">
          <h3 class="text-lg text-black font-bold mb-1">${book.title}</h3>
          <p class="text-xs text-black font-semibold mb-1">${book.author_name || "Auteur inconnu"}</p>
          <p class="text-xs text-black mb-2">
            ${truncateDescription(book.description?.replaceAll("#virgule", ",") || "Pas de description", 250)}
          </p>
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
    swiperWrapper.appendChild(slide);
  });

  // Initialisation Swiper
  const swiper = new Swiper(".centered-slide-carousel", {
    centeredSlides: true,
    loop: true,
    spaceBetween: 10,
    slideToClickedSlide: true,
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
    breakpoints: {
      1920: { slidesPerView: 8 },
      1028: { slidesPerView: 6 },
      768: { slidesPerView: 4 },
      480: { slidesPerView: 1 }
    }
  });

  // Gestion des événements
  document.addEventListener("click", async (event) => {
    // Gestion du clic sur l'oeil
    if (event.target.closest(".eye-button")) {
      const slideDiv = event.target.closest('[data-book-id]');
      const bookId = slideDiv.dataset.bookId;
      const book = booksData.find(b => b.id == bookId);
      
      if (book) {
        updatePopup(book);
        currentSimilarBooks = await fetchSimilarBooks(bookId);
        addSimilarBooks(currentSimilarBooks);
        popup.classList.remove("hidden");
        popup.classList.add("show");
      }
    }

    // Gestion du clic sur les livres similaires
    if (event.target.closest(".similar-book-card")) {
      const cardDiv = event.target.closest('[data-book-id]');
      const bookId = cardDiv.dataset.bookId;
      const book = currentSimilarBooks.find(b => b.id == bookId);
      
      if (book) {
        updatePopup(book);
        currentSimilarBooks = await fetchSimilarBooks(bookId);
        addSimilarBooks(currentSimilarBooks);
      }
    }
  });

  // Fermeture de la popup
  closePopupButton.addEventListener("click", () => {
    popup.classList.remove("show");
    popup.classList.add("hide");
    setTimeout(() => {
      popup.classList.add("hidden");
      popup.classList.remove("hide");
    }, 300);
  });

  popup.addEventListener("click", (event) => {
    if (event.target === popup) {
      popup.classList.remove("show");
      popup.classList.add("hide");
      setTimeout(() => {
        popup.classList.add("hidden");
        popup.classList.remove("hide");
      }, 300);
    }
  });
}

initializeCarousel();