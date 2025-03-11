import { showPopup } from './popup.js';
import { getCookie } from './auth.js';

function getIdAccount() {
  const userCookie = getCookie('user');
  if (userCookie) {
      const user = JSON.parse(userCookie);
      return user;
  }
}

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

document.addEventListener('click', async (event) => {
  if (event.target.closest('.like-button')) {
    //console.log("like");
    const slideDiv = event.target.closest('[data-book-id]');
    const bookId = slideDiv.dataset.bookId;
    const userId = getIdAccount();
    //console.log("userId", userId);
    //console.log("bookId", bookId);
    if (!userId) {
      const plusButtons = document.querySelectorAll(".like-button");
      plusButtons.forEach(button => {
        button.classList.add("cursor-not-allowed", "disabled");
        button.setAttribute("title", "Veuillez vous connecter pour liker un livre");
      });
      return;
    }else{
      try {
        const response = await fetch(`/reviews/${userId}/${bookId}`, {
          method: 'POST'
        });
        event.target.classList.toggle('text-red-500');
        showPopupReview(bookId);

        if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);
      } catch (error) {
        console.error("Erreur lors de la requête de like:", error);
        alert("Impossible de liker le livre");
      }
    }
  }
});


async function showPopupReview(bookId) {
  try {
    // Récupération des données du livre
    const bookResponse = await fetch(`books/${bookId}`);
    if (!bookResponse.ok) throw new Error(`Erreur HTTP! statut: ${bookResponse.status}`);
    const book = await bookResponse.json();

    // Récupération de la note existante
    let existingRating = null;
    const userId = getIdAccount();
    try {
      const reviewResponse = await fetch(`/reviews/user/${userId}/${bookId}`);
      if (reviewResponse.ok) {
        const reviewData = await reviewResponse.json();
        existingRating = reviewData.note;
      }
    } catch (error) {
      console.error("Erreur lors de la récupération de la note:", error);
    }
    // Création du popup
    const popup = document.createElement("div");
    popup.classList.add("popup-review", "fixed", "inset-0", "bg-black/50", "flex", "items-center", "justify-center", "z-[999]");
    popup.innerHTML = `
      <div class="popup-content bg-white rounded-lg p-4 shadow-lg max-w-lg mx-auto flex gap-4 max-h-[400px] relative">
      
        
        <button
              id="close-icon"
              class="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
            >
              <i class="fas fa-times"></i>
            </button>

        <img src="${book.url !== "-1" ? book.url : "/static/notfound.jpg"}" 
             alt="Couverture de ${book.title}" 
             class="w-32 h-44 object-cover rounded transition-transform duration-300">
        <div class="flex flex-col items-start gap-2 flex-1">
          <h2 class="text-lg font-bold text-gray-800">${book.title}</h2>
          <div class="stars flex space-x-1 mb-2">
            ${[1, 2, 3, 4, 5].map(i => `
              <i class="fas fa-star cursor-pointer text-xl ${existingRating && i <= existingRating ? 'text-yellow-400' : 'text-gray-300'}" 
                 data-value="${i}"></i>
            `).join('')}
          </div>
          <div class="flex gap-2 mt-auto w-full">
            <button id="validate-review" class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded transition-colors text-sm flex-1">
              ${existingRating ? 'Modifier' : 'Valider'}
            </button>
            ${existingRating ? `
              <button id="delete-review" class="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded transition-colors text-sm flex-1">
                <i class="fas fa-trash mr-1"></i> Supprimer
              </button>
            ` : ''}
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(popup);

    // Gestion des étoiles
    const stars = popup.querySelectorAll('.fa-star');
    let selectedRating = existingRating || 0;

    // Interactions avec les étoiles
    stars.forEach(star => {
      star.addEventListener('mouseover', (e) => {
        if (selectedRating > 0) return;
        const hoverValue = parseInt(e.target.dataset.value);
        stars.forEach(s => s.classList.toggle('text-yellow-400', parseInt(s.dataset.value) <= hoverValue));
      });

      star.addEventListener('mouseleave', () => {
        if (selectedRating === 0) {
          stars.forEach(s => s.classList.remove('text-yellow-400'));
        }
      });

      star.addEventListener('click', (e) => {
        selectedRating = parseInt(e.target.dataset.value);
        stars.forEach(s => s.classList.toggle('text-yellow-400', parseInt(s.dataset.value) <= selectedRating));
      });
    });

    // Validation/modification
    popup.querySelector('#validate-review').addEventListener('click', async () => {
      try {
        const response = await fetch(`/reviews/${userId}/${book.id}/${selectedRating}`, {
          method: existingRating ? 'PUT' : 'POST' // Supposition d'une API RESTful
        });
        
        if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);
        popup.remove();
        alert(`Note ${existingRating ? 'modifiée' : 'ajoutée'} avec succès !`);
      } catch (error) {
        console.error("Erreur lors de la requête:", error);
        alert("Erreur lors de la mise à jour de la note");
      }
    });

    // Suppression
    if (existingRating) {
      popup.querySelector('#delete-review').addEventListener('click', async () => {
        if (confirm("Supprimer définitivement cet avis ?")) {
          try {
            const response = await fetch(`/reviews/${userId}/${book.id}`, { method: 'DELETE' });
            if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);
            popup.remove();
            alert('Avis supprimé !');
          } catch (error) {
            console.error("Erreur:", error);
            alert("Erreur lors de la suppression");
          }
        }
      });
    }

    // Fermeture
    popup.querySelector('#close-icon').addEventListener('click', () => popup.remove());

  } catch (error) {
    console.error("Erreur:", error);
    alert("Erreur lors du chargement");
  }
}

document.addEventListener("click", async (event) => {
  const target = event.target;
  if (target.classList.contains("bookmark")) {
    const slideDiv = target.closest("[data-book-id]");
    const bookId = slideDiv.dataset.bookId;
    const userId = getIdAccount();
    if (!userId) return;

    const isMarked = target.classList.contains("text-blue-500");
    try {
      const response = await fetch(`/read/${userId}/${bookId}`, {
        method: isMarked ? "DELETE" : "POST",
        headers: { "Content-Type": "application/json" }
      });
      if (response.ok) {
        target.classList.toggle("text-gray-500");
        target.classList.toggle("text-blue-500");
      } else {
        console.error("Erreur lors de la mise à jour du statut du livre.");
      }
    } catch (error) {
      console.error("Erreur réseau :", error);
    }
  }
});
