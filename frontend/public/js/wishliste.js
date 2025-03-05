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


function wishListe() {
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
      // Initialisation du carrousel avec les données récupérées
      initializeCarousel(data, 'wishlistCarousel'); // 'wishlistCarousel' est l'ID de ton carousel
    })
    .catch(error => console.error("Erreur lors de la récupération de la wishlist", error));
}
