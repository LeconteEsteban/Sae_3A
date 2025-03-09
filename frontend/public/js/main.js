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
function init() {
  console.log("1");
  fetchBooks("/books/topbook/30").then(topBooks => 
    initializeCarousel(topBooks, "Topcarousel")
  ).catch(error => console.error("Error fetching Topcarousel:", error));
  console.log("2");
  fetchBooks("/books/topbook/30").then(topBooks1 => 
    initializeCarousel(topBooks1, "Newcarousel")
  ).catch(error => console.error("Error fetching Newcarousel:", error));
  console.log("3");
  fetchBooks("/books/topbook/30").then(topBooks2 => 
    initializeCarousel(topBooks2, "Newcarousel1")
  ).catch(error => console.error("Error fetching Newcarousel1:", error));
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
