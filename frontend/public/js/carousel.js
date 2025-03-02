import { truncateDescription } from './utils.js';
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
