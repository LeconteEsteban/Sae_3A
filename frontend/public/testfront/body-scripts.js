document.addEventListener("DOMContentLoaded", function () {
    const prevButton = document.querySelector('.prev');
    const nextButton = document.querySelector('.next');
    const slides = document.querySelectorAll('.slide');
    const sliderWrapper = document.querySelector('.slider-wrapper');
    let currentIndex = 0;

    const updateSliderPosition = () => {
        const slideWidth = slides[0].offsetWidth;
        sliderWrapper.style.transform = `translateX(-${currentIndex * slideWidth}px)`;
    };

    nextButton.addEventListener('click', () => {
        if (currentIndex < slides.length - 1) {
            currentIndex++;
        } else {
            currentIndex = 0; // Retour au début
        }
        updateSliderPosition();
    });

    prevButton.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
        } else {
            currentIndex = slides.length - 1; // Retour à la fin
        }
        updateSliderPosition();
    });

    // Initialisation de la position du slider
    updateSliderPosition();
});

document.addEventListener("DOMContentLoaded", function () {
    const prevButton = document.querySelector('.prev-top10');
    const nextButton = document.querySelector('.next-top10');
    const slides = document.querySelectorAll('.slide-top10');
    const sliderWrapper = document.querySelector('.slider-wrapper-top10');
    let currentIndex = 0;

    const updateSliderPosition = () => {
        const slideWidth = slides[0].offsetWidth;
        sliderWrapper.style.transform = `translateX(-${currentIndex * slideWidth}px)`;
    };

    nextButton.addEventListener('click', () => {
        if (currentIndex < slides.length - 1) {
            currentIndex++;
        } else {
            currentIndex = 0; // Retour au début
        }
        updateSliderPosition();
    });

    prevButton.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
        } else {
            currentIndex = slides.length - 1; // Retour à la fin
        }
        updateSliderPosition();
    });

    // Initialisation de la position du slider
    updateSliderPosition();
});