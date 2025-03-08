import { showPopup } from './popup.js';

document.addEventListener('click', async (event) => {
  if (event.target.closest('.eye-button')) {
    const slideDiv = event.target.closest('[data-book-id]');
    const bookId = slideDiv.dataset.bookId;
    try {
      const response = await fetch(`/books/${bookId}`);
      if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);
      const book = await response.json();
      showPopup(book);
    } catch (error) {
      console.error("Erreur lors de la récupération du livre:", error);
      alert("Impossible de charger les détails du livre");
    }
  }
});

document.addEventListener('click', (event) => {
  if (event.target.closest('.like-button')) {
    event.target.classList.toggle('text-red-500');
  }
});

document.getElementById('close-popup').addEventListener('click', closePopup);
document.getElementById('book-popup').addEventListener('click', (event) => {
  if (event.target === document.getElementById('book-popup')) closePopup();
});

function closePopup() {
  const popup = document.getElementById("book-popup");
  popup.classList.remove("show");
  popup.classList.add("hide");
  setTimeout(() => {
    popup.classList.add("hidden");
    popup.classList.remove("hide");
  }, 300);
}