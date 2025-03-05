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
