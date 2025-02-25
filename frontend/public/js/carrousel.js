async function fetchBooks() {
  let booksData = [];
  console.log("Debut fetch");

  try {
    const response = await fetch("/books/topbook/30");
    booksData = await response.json();
    console.log("Données récupérées :", booksData); // Affiche les données récupérées
  } catch (error) {
    console.error("Erreur lors de la récupération des données :", error);
  }

  console.log("fin fetch");
  return booksData; // Retourner les données pour les utiliser ailleurs
}

function truncateDescription(description, maxLength) {
  if (description && description.length > maxLength) {
    return description.substring(0, maxLength) + "...";
  }
  return description || "Pas de description";
}

function updatePopup(book) {
  document.getElementById("book-cover").src =
    book.url !== "-1" ? book.url : "/static/notfound.jpg";
  document.getElementById("book-title").textContent = book.title;
  document.getElementById("book-author").textContent = book.author_name;
  document.getElementById("book-description").textContent = book.description
    ? book.description.replaceAll("#virgule", ",")
    : "Pas de description";
  document.getElementById("book-genres").innerHTML = book.genre_names
    ? book.genre_names
        .map(
          (genre) =>
            `<span class="bg-gray-300 text-black px-2 py-1 text-xs rounded">${genre}</span>`
        )
        .join("")
    : "";
  document.getElementById("book-page").textContent =
    book.number_of_pages || "N/A";
  document.getElementById("book-publisher").textContent =
    book.publisher_name || "N/A";
  document.getElementById("book-isbn").textContent = book.isbn13 || "N/A";
}

function addSimilarBooks(books) {
  const similarBooksContainer = document.getElementById(
    "similar-books-container"
  );
  similarBooksContainer.innerHTML = "";
  books.forEach((book) => {
    const bookCard = document.createElement("div");
    bookCard.classList.add(
      "similar-book-card",
      "bg-white",
      "rounded-lg",
      "relative",
      "group",
      "transition-transform",
      "duration-300",
      "zoom-hover"
    );
    const truncatedDescription = truncateDescription(
      book.description
        ? book.description.replaceAll("#virgule", ",")
        : "Pas de description",
      110
    );
    const genres = book.genre_names.slice(0, 2); // Limite à 2 genres

    bookCard.innerHTML = `
      <div id=${book.id} class="bg-white shadow-lg rounded-lg p-4 flex flex-col items-center relative w-50 h-80">
        <img src="${
          book.url !== "-1" ? book.url : "/static/notfound.jpg"
        }" alt="Couverture de ${
      book.title
    }" class="w-32 h-44 object-cover rounded transition-transform duration-300">
        <h3 class="text-lg font-bold text-gray-800 mt-2 text-center">${
          book.title,
          book.id
        }</h3>

        <!-- Infos visibles au hover -->
        <div class="absolute inset-0 bg-white bg-opacity-95 flex flex-col text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-lg p-4">
          <h3 class="text-lg text-black font-bold mb-1">${book.title}</h3>
          <p class="text-xs text-black font-semibold mb-1">${
            book.author_name || "Auteur inconnu"
          }</p>
          <p class="text-xs text-black mb-2">${truncatedDescription}</p>

          <!-- Genres -->
          <ul class="flex gap-2 mb-3">
            ${genres
              .map(
                (genre) =>
                  `<li class="bg-white text-black border border-black px-2 py-1 text-xs rounded">${genre}</li>`
              )
              .join("")}
          </ul>

          <!-- Actions -->
          <div class="flex gap-2 mt-auto justify-between w-full">
            <i class="fas fa-heart text-gray-500 text-2xl cursor-pointer transition-transform duration-200 hover:scale-110 like-button"></i>
            <i class="fas fa-plus text-gray-500 text-2xl cursor-pointer transition-transform duration-200 hover:scale-110 plus-button"></i>
            <i class="fas fa-eye text-gray-500 text-2xl cursor-pointer transition-transform duration-200 hover:scale-110 eye-button"></i>
          </div>
        </div>
      </div>
    `;
    similarBooksContainer.appendChild(bookCard);
  });
}

async function initializeCarousel() {
  const booksData = await fetchBooks();

  if (!booksData || booksData.length === 0) {
    console.error("Aucune donnée récupérée");
    return;
  }

  const swiperWrapper = document.querySelector(".swiper-wrapper");

  booksData.forEach((book) => {
    const slide = document.createElement("div");
    slide.classList.add(
      "swiper-slide",
      "relative",
      "group",
      "transition-transform",
      "duration-300",
      "zoom-hover"
    );

    const genres = book.genre_names.slice(0, 2);
    slide.innerHTML = `
            <div id=${book.id} class="bg-white shadow-lg rounded-lg p-4 flex flex-col items-center justify-center relative w-50 h-80">
                 <img src="${
                   book.url !== "-1" ? book.url : "/static/notfound.jpg"
                 }" alt="Couverture de ${
      book.title
    }" class="w-32 h-44 object-cover rounded transition-transform duration-300">
                <h3 class="text-lg font-bold text-gray-800 mt-2 text-center">${
                  book.title,
                  book.id
                }</h3>
            
                <!-- Infos visibles au hover -->
                <div class="absolute inset-0 bg-white bg-opacity-95 flex flex-col text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-lg p-4">
                    <h3 class="text-lg text-black font-bold mb-1">${
                      book.title
                    }</h3>
                    <p class="text-xs text-black font-semibold mb-1">
  ${book.author_name || "Auteur inconnu"}
</p>

                    <p class="text-xs text-black mb-2">
                    ${
                      book.description
                        ? truncateDescription(
                            book.description.replaceAll("#virgule", ","),
                            250
                          )
                        : "Pas de description"
                    }
                    </p>

                    <ul class="flex gap-2 mb-3">
                        ${genres
                          .map(
                            (genre) =>
                              `<li class="bg-white text-black border border-black px-2 py-1 text-xs rounded">${genre}</li>`
                          )
                          .join("")}
                    </ul>
                    

                    <div class="flex gap-2 mt-auto justify-between w-full">
                        <i class="fas fa-heart text-gray-500 text-2xl cursor-pointer transition-transform duration-200 hover:scale-110 like-button"></i>
                        <i class="fas fa-plus text-gray-500 text-2xl cursor-pointer transition-transform duration-200 hover:scale-110 plus-button"></i>
                        <i class="fas fa-eye text-gray-500 text-2xl cursor-pointer transition-transform duration-200 hover:scale-110 eye-button"></i>
                    </div>
                </div>
            </div>
        `;
    swiperWrapper.appendChild(slide);
  });

  // Initialiser Swiper après avoir ajouté les slides
  var swiper = new Swiper(".centered-slide-carousel", {
    centeredSlides: true,
    loop: true,
    spaceBetween: 10,
    slideToClickedSlide: true,
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
    breakpoints: {
      1920: { slidesPerView: 8, spaceBetween: 10 },
      1028: { slidesPerView: 8, spaceBetween: 10 },
      768: { slidesPerView: 8, spaceBetween: 10 },
      480: { slidesPerView: 1, spaceBetween: 10 },
    },
  });

  // Ajouter les écouteurs d'événements pour les boutons
  const likeButtons = document.querySelectorAll(".like-button");
  const eyeButtons = document.querySelectorAll(".eye-button");
  const popup = document.getElementById("book-popup");
  const closePopupButton = document.getElementById("close-popup");

  likeButtons.forEach((button) => {
    button.addEventListener("click", function () {
      button.classList.toggle("text-red-500");
    });
  });

  eyeButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const slide = button.closest(".swiper-slide");
      const book = booksData.find(
        (book) => book.title === slide.querySelector("h3").textContent
      );
      if (book) {
        updatePopup(book);
        addSimilarBooks(booksData);
        popup.classList.remove("hidden");
        popup.classList.add("show");
      }
    });
  });

  closePopupButton.addEventListener("click", function () {
    popup.classList.remove("show");
    popup.classList.add("hide");
    setTimeout(() => {
      popup.classList.add("hidden");
      popup.classList.remove("hide");
    }, 300);
  });

  popup.addEventListener("click", function (event) {
    if (event.target === popup) {
      popup.classList.remove("show");
      popup.classList.add("hide");
      setTimeout(() => {
        popup.classList.add("hidden");
        popup.classList.remove("hide");
      }, 300);
    }
  });

  // Ajouter un événement de clic pour les livres similaires
  document.addEventListener("click", function (event) {
    if (event.target.closest(".similar-book-card")) {
      const bookCard = event.target.closest(".similar-book-card");
      const bookTitle = bookCard.querySelector("h3").textContent;
      const book = booksData.find((book) => book.title === bookTitle);
      if (book) {
        updatePopup(book);
      }
    }
  });
}

initializeCarousel();
