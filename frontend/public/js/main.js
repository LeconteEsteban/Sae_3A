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

//à opti ici
async function init() {
  const [topBooks] = await Promise.all([
    fetchBooks("/books/topbook/30")
  ]);

  initializeCarousel(topBooks, "Topcarousel");

  const [topBooks1] = await Promise.all([
    fetchBooks("/books/topbook/30")
  ]);
  initializeCarousel(topBooks1, "Newcarousel");

  const [topBooks2] = await Promise.all([
    fetchBooks("/books/topbook/30")
  ]);
  initializeCarousel(topBooks2, "Newcarousel1");
}

init();

document.addEventListener("DOMContentLoaded", function () {
  const chk = document.getElementById("chk");
  const body = document.body;


  if (localStorage.getItem("dark-mode") === "enabled") {
      body.classList.add("dark-mode");
      chk.checked = true; 
  }

  
  chk.addEventListener("change", function () {
      body.classList.toggle("dark-mode");

      // Sauvegarde de l'état dans le stockage local
      if (body.classList.contains("dark-mode")) {
          localStorage.setItem("dark-mode", "enabled");
      } else {
          localStorage.setItem("dark-mode", "disabled");
      }
  });
});
