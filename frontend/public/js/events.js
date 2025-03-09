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
    const response = await fetch(`books/${bookId}`);
    if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);
    
    const book = await response.json();
    
    // Créer le popup
    const popup = document.createElement("div");
    popup.classList.add("popup-review", "fixed", "inset-0", "bg-black/50", "flex", "items-center", "justify-center", "z-[999]", "h-42");
    popup.innerHTML = `
    <div class="popup-content bg-white rounded-lg p-4 shadow-lg max-w-lg mx-auto flex gap-4 max-h-[400px]">

      <img src="${book.url !== "-1" ? book.url : "/static/notfound.jpg"}" 
             alt="Couverture de ${book.title}" 
             class="w-32 h-44 object-cover rounded transition-transform duration-300">
      <div class="flex flex-col items-start gap-2 flex-1 overflow-y-auto">
        <h2 class="text-lg font-bold text-gray-800">${book.title}</h2>
        <div class="stars flex space-x-1 mb-2">
          ${[1, 2, 3, 4, 5].map(i => `
            <i class="fas fa-star cursor-pointer text-xl text-gray-300 transition-colors hover:text-yellow-400"
              data-value="${i}"></i>
          `).join('')}
        </div>
        <div class="flex gap-2 mt-auto w-full">
          <button id="validate-review" class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded transition-colors text-sm flex-1">
            Valider
          </button>
          <button id="close-popup" class="bg-gray-400 hover:bg-gray-500 text-white px-3 py-1 rounded transition-colors text-sm flex-1">
            Fermer
          </button>
        </div>
      </div>
    </div>
`;
    document.body.appendChild(popup);


    // Gestion des étoiles
    const starsContainer = popup.querySelector('.stars');
    const stars = popup.querySelectorAll('.fa-star');
    let selectedRating = 0;

    // Survol des étoiles
    starsContainer.addEventListener('mouseover', (e) => {
      if (!e.target.classList.contains('fa-star') || selectedRating > 0) return;
      
      const hoverValue = parseInt(e.target.dataset.value);
      stars.forEach(star => {
        const value = parseInt(star.dataset.value);
        star.classList.toggle('text-yellow-400', value <= hoverValue);
        star.classList.toggle('text-gray-300', value > hoverValue);
      });
    });

    // Fin du survol
    starsContainer.addEventListener('mouseleave', () => {
      if (selectedRating === 0) {
        stars.forEach(star => {
          star.classList.remove('text-yellow-400');
          star.classList.add('text-gray-300');
        });
      }
    });

    // Clic sur une étoile
    stars.forEach(star => {
      star.addEventListener('click', (e) => {
        selectedRating = parseInt(e.target.dataset.value);
        stars.forEach(s => {
          const value = parseInt(s.dataset.value);
          s.classList.toggle('text-yellow-400', value <= selectedRating);
          s.classList.toggle('text-gray-300', value > selectedRating);
        });
      });
    });

    // Valider la note
    popup.querySelector('#validate-review').addEventListener('click', async () => {
      try {
        const response = await fetch(`/reviews/${getIdAccount()}/${book.id}/${selectedRating}`, {
          method: 'POST'
        });
        popup.remove();

        if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);
      } catch (error) {
        console.error("Erreur lors de la requête de like:", error);
        alert("Impossible de liker le livre");
      }

    });
      

    // Fermer le popup
    popup.querySelector('#close-popup').addEventListener('click', () => {
      popup.remove();
    });

  } catch (error) {
    console.error("Erreur lors de la récupération du livre:", error);
    alert("Impossible de récupérer les informations du livre");
  }
}

