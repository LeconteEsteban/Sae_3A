var swiper = new Swiper(".centered-slide-carousel", {
    centeredSlides: true,
    paginationClickable: true,
    loop: true,
    spaceBetween: 30,
    slideToClickedSlide: true,
    pagination: {
      el: ".centered-slide-carousel .swiper-pagination",
      clickable: true,
    },
    breakpoints: {
      1920: {
        slidesPerView: 4,
        spaceBetween: 30
      },
      1028: {
        slidesPerView: 2,
        spaceBetween: 10
      },
      990: {
        slidesPerView: 1,
        spaceBetween: 0
      }
    }
   });