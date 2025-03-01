import { showPopup } from './popup.js';
import { getBookById } from './carousel.js';

console.log('events.js loaded');

document.addEventListener('click', async (event) => {
  if (event.target.closest('.eye-button')) {
    const slideDiv = event.target.closest('[data-book-id]');
    const bookId = slideDiv.dataset.bookId;
    const book = getBookById(bookId);
    if (book) showPopup(book);
  }
});



document.addEventListener('click', (event) => {
  if (event.target.closest('.similar-book-card')) {
    const cardDiv = event.target.closest('[data-book-id]');
    const bookId = cardDiv.dataset.bookId;

    if (book) showPopup(book);
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