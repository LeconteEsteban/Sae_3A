import { initializeCarousel } from './carousel.js';

document.addEventListener("DOMContentLoaded", async () => {
  const userId = 1; // Remplace par l'ID de l'utilisateur connecté
  try {
    const response = await fetch(`/wishlist/${userId}`);
    const books = await response.json();

    if (!response.ok) throw new Error(books.detail || "Erreur inconnue");

    initializeCarousel(books, "wishlist-carousel");
  } catch (error) {
    console.error("Erreur lors du chargement de la wishlist :", error);
  }
});
