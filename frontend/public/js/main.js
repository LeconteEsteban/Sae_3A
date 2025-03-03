import { initializeCarousel } from './carousel.js';

export let booksData = [];

async function fetchBooks(url) {  
  try {
    const response = await fetch(url);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`Erreur lors de la récupération des données depuis ${url}:`, error);
    return [];
  }
}

async function init() {
  const [topBooks] = await Promise.all([
    fetchBooks("/books/topbook/30"),
  ]);

  initializeCarousel(topBooks, "Topcarousel");
  initializeCarousel(topBooks, "Newcarousel");
  initializeCarousel(topBooks, "Newcarousel1");
}

init();

document.addEventListener("DOMContentLoaded", function () {
  const toggleButton = document.getElementById("toggleDarkMode");
  const body = document.body;

  // Vérifier si l'utilisateur a déjà activé le mode sombre
  if (localStorage.getItem("dark-mode") === "enabled") {
      body.classList.add("dark-mode");
  }

  toggleButton.addEventListener("click", function () {
      console.log("x");
      body.classList.toggle("dark-mode");

      // Sauvegarde l'état dans le stockage local
      if (body.classList.contains("dark-mode")) {
          localStorage.setItem("dark-mode", "enabled");
      } else {
          localStorage.setItem("dark-mode", "disabled");
      }
  });
});
