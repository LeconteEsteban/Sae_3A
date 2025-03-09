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

export function initializeCarousel(data, carouselId) {
  const swiperWrapper = document.querySelector(`#${carouselId}`);

  if (!swiperWrapper) {
    console.error(`Aucun élément trouvé pour l'ID ${carouselId}`);
    return;
  }

  if (!data?.length) {
    console.error(`Aucune donnée récupérée pour ${carouselId}`);
    return;
  }

  swiperWrapper.innerHTML = "";

  data.forEach(book => {
    const slide = document.createElement("div");
    slide.classList.add("swiper-slide", "relative", "group", "transition-transform", "duration-300", "zoom-hover");

    slide.innerHTML = `
      <div data-book-id="${book.id}" class="bg-white shadow-lg rounded-lg p-4 flex flex-col items-center justify-center relative w-50 h-80">
        <img src="${book.url !== "-1" ? book.url : "/static/notfound.jpg"}" 
             alt="Couverture de ${book.title}" 
             class="w-32 h-44 object-cover rounded transition-transform duration-300">
        <h3 class="text-lg font-bold text-gray-800 mt-2 text-center line-clamp-2 overflow-hidden">
  ${book.title}
</h3>
        
        <div class="absolute inset-0 bg-white bg-opacity-95 flex flex-col text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-lg p-4">
          <h3 class="text-lg text-black font-bold mb-1 line-clamp-2">${book.title}</h3>
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

  new Swiper(swiperWrapper.closest(".swiper"), {
    centeredSlides: true,
    loop: true,
    spaceBetween: 10,
    slideToClickedSlide: true,
    navigation: {
      nextEl: swiperWrapper.closest(".swiper").querySelector(".swiper-button-next"),
      prevEl: swiperWrapper.closest(".swiper").querySelector(".swiper-button-prev"),
    },
    breakpoints: {
      1920: { slidesPerView: 8 },
      1028: { slidesPerView: 6 },
      768: { slidesPerView: 4 },
      480: { slidesPerView: 1 }
    }
  });
}

document.addEventListener("DOMContentLoaded", async () => {

  if (!getIdAccount) {
    const plusButtons = document.querySelectorAll(".plus-button");
    plusButtons.forEach(button => {
      button.classList.add("cursor-not-allowed", "disabled");
      button.setAttribute("title", "Veuillez vous connecter pour ajouter des livres à votre wishlist");
    });
  }
});

document.addEventListener("click", async (event) => {
  if (event.target.classList.contains("plus-button")) {
    const slideDiv = event.target.closest('[data-book-id]');
    const bookId = slideDiv.dataset.bookId;

    if (event.target.classList.contains("disabled")) return;
    
    event.target.classList.add("disabled", "cursor-not-allowed");
    //console.log("idAccount", getIdAccount());
    //console.log("Ajout du livre à la wishlist", bookId);
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
