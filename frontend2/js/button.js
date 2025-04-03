function toggleFill(button, colorClass) {
    if (!button) return; 
    button.classList.toggle(colorClass);
}


function sendRequest(url, button, colorClass) {
    console.log("Envoi de la requête à :", url);
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        console.log("Réponse reçue :", response.status);
        if (response.ok) {
            console.log("Succès ! Bouton modifié :", button);
            toggleFill(button, colorClass);
        } else {
            response.text().then(text => console.error("Erreur API :", text));
            alert("Erreur lors de l'action.");
        }
    })
    .catch(error => {
        console.error("Erreur réseau :", error);
        alert("Erreur de connexion.");
    });
}


function updateButtonState(buttonId, isActive, activeClass) {
    const button = document.getElementById(buttonId);
    if (button) {
        if (isActive) {
            button.classList.add(activeClass);
        } else {
            button.classList.remove(activeClass);
        }
    }
}



async function getWishlistBooks(userId) {
    try {
        const response = await fetch(`/wishlist/${userId}`);
        if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error("Erreur lors de la récupération des livres dans la wishlist:", error);
        return [];
    }
}
async function getReadBooksLike(userId) {
    try {
        const response = await fetch(`/reviews/${userId}/noted-books`);
        if (!response.ok) throw new Error(`Erreur HTTP! statut: ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error("Erreur lors de la récupération des livres likés:", error);
        return [];
    }
}

// Avoir la note donnée par l'utilisateur au livre
async function getBookRating(userId, bookId) {
    try {
        const response = await fetch(`/reviews/user/${userId}/${bookId}`);
        if (!response.ok) return null;

        const data = await response.json();
        return data.note; 
    } catch (error) {
        console.error(`Erreur lors de la récupération de la note pour le livre ${bookId}:`, error);
        return null;
    }
}

async function onBookChange(bookId) {
    const userId = localStorage.getItem('user_id');
    if (!userId) return;

    const readButton = document.getElementById("read-button");
    const likeButton = document.getElementById("like-button");
    const starsContainer = document.getElementById("rating-stars");
    const wishlistButton = document.getElementById("wishlist-button");

    likeButton.style.display = "none";
    likeButton.style.color = "";
    starsContainer.classList.add("hidden");
    wishlistButton.classList.remove("text-yellow-500");
    
    document.querySelectorAll(".star").forEach(star => {
        star.classList.remove("text-yellow-500");
    });
    

    try {
        const [readBooksResponse, likedBooks, rating, wishlistBooks] = await Promise.all([
            fetch(`/read/${userId}`).then(res => res.ok ? res.json() : Promise.reject(`Erreur API Read: ${res.status}`)),
            getReadBooksLike(userId),
            getBookRating(userId, bookId),
            getWishlistBooks(userId)
        ]);


        const isRead = readBooksResponse.includes(bookId);
        const isLiked = likedBooks.some(item => item[0] === bookId);
        const isWishlisted = wishlistBooks.includes(bookId);

        // Mise à jour des affichages des boutons

        readButton.style.color = isRead ? "green" : "";

        if (isRead) {
            likeButton.style.display = "inline-block";
            likeButton.style.color = isLiked ? "red" : "";
            
            if (isLiked && rating !== null) {
                starsContainer.classList.remove("hidden");
                highlightStars(rating);
            }
        } else {
            likeButton.style.display = "none";
        }

        if (isWishlisted) {
            wishlistButton.classList.add("text-yellow-500");
        } else {
            wishlistButton.classList.remove("text-yellow-500");
        }


    } catch (error) {
        console.error("Erreur lors de la mise à jour des boutons et étoiles :", error);
    }
}





function highlightStars(rating) {
    document.querySelectorAll(".star").forEach(star => {
        star.classList.remove("text-yellow-500");
    });

    document.querySelectorAll(".star").forEach(star => {
        let value = parseInt(star.getAttribute("data-value"), 10);
        if (value <= rating) {
            star.classList.add("text-yellow-500");
        }
    });
}






function addToWishlist(button) {
    const bookId = document.getElementById('book-id-num')?.textContent;
    const userId = localStorage.getItem('user_id');

    if (!userId) {
        alert("Veuillez vous connecter pour ajouter un livre à votre wishlist.");
        return;
    }

    if (!bookId) {
        alert("Erreur : Identifiant du livre introuvable.");
        return;
    }

    button.classList.add("text-yellow-500"); 
    sendRequest(`/wishlist/add/${bookId}/${userId}`, button);
}



function addToLike(button, colorClass) {
    const userId = localStorage.getItem('user_id');

    if (!userId) {
        alert("Veuillez vous connecter pour évaluer un livre.");
        return;
    }

    let ratingStars = document.getElementById("rating-stars");
    if (!ratingStars) {
        alert("Erreur : Section d'évaluation introuvable.");
        return;
    }

    ratingStars.classList.remove("hidden");

    document.querySelectorAll(".star").forEach(star => {
        star.replaceWith(star.cloneNode(true));
    });

    document.querySelectorAll(".star").forEach(star => {
        star.addEventListener("click", async function() {
            const selectedValue = this.getAttribute("data-value");
            const bookId = document.getElementById('book-id-num')?.textContent;

            if (!bookId) {
                alert("Erreur : Identifiant du livre introuvable.");
                return;
            }

            console.log("Envoi de la note :", selectedValue, "pour le livre", bookId);

            try {
                const response = await fetch(`/reviews/${userId}/${bookId}/${selectedValue}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ note: selectedValue })
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error("Erreur API :", errorText);
                    alert("Erreur lors de l'action : " + errorText);
                    return;
                }

                button.style.color = "red";
                ratingStars.classList.add("hidden");
                console.log("Note enregistrée avec succès !");
            } catch (error) {
                console.error("Erreur réseau :", error);
                alert("Erreur de connexion. Veuillez réessayer plus tard.");
            }
        });
    });
}



function addToRead(button) {
    const bookId = document.getElementById('book-id-num')?.textContent;
    const userId = localStorage.getItem('user_id');

    if (!userId) {
        alert("Veuillez vous connecter pour ajouter un livre à votre liste de lecture.");
        return;
    }

    if (!bookId) {
        alert("Erreur : Identifiant du livre introuvable.");
        return;
    }

    button.style.color = "green";
    sendRequest(`/read/${userId}/${bookId}`, button);

    // Afficher immédiatement le bouton "Like"
    const likeButton = document.getElementById("like-button");
    if (likeButton) {
        likeButton.style.display = "inline-block";
    }
}

