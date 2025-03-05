import { initializeCarousel } from './carousel.js';

function getUserId() {
  const user = getIdAccount();
  if (user) {
    console.log("Utilisateur authentifié avec ID :", user);
    return user;
  } else {
    console.log("Utilisateur non authentifié !");
    return null;
  }
}

export function wishListe() {
  const userId = getUserId(); // Récupère l'ID de l'utilisateur

  if (!userId) {
    alert("Utilisateur non authentifié !");
    return;
  }

  // Si l'utilisateur est authentifié, récupère la wishlist
  fetch(`/wishlist/${userId}`)
    .then(response => {
      if (!response.ok) {
        throw new Error('Erreur lors de la récupération de la wishlist');
      }
      return response.json();
    })
    .then(data => {
      // Vérifie si la wishlist est vide
      if (data && data.length > 0) {
        // Si la wishlist n'est pas vide, initialiser le carrousel
        initializeCarousel(data, 'wishlistCarousel'); // 'wishlistCarousel' est l'ID de ton carousel
      } else {
        // Si la wishlist est vide, afficher la popup
        const popup = document.getElementById('noBooksPopup');
        if (popup) {
          popup.classList.remove('hidden');
        } else {
          console.error("Popup non trouvée !");
        }
      }
    })
    .catch(error => console.error("Erreur lors de la récupération de la wishlist", error));
}

// Ajout d'un gestionnaire d'événements pour fermer la popup
document.getElementById('closePopup')?.addEventListener('click', () => {
  const popup = document.getElementById('noBooksPopup');
  if (popup) {
    popup.classList.add('hidden'); // Masque la popup
  }
});