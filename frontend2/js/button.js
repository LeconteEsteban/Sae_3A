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


function resetButtonColors() {
    document.getElementById("read-button")?.classList.remove("text-green-500");
    document.getElementById("like-button")?.classList.remove("text-red-500");
    document.getElementById("wishlist-button")?.classList.remove("text-yellow-500");
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

    // **1. Masquer "Like" et les étoiles au début**
    likeButton.style.display = "none";
    starsContainer.classList.add("hidden");

    // **2. Réinitialiser les étoiles avant d'afficher la nouvelle note**
    document.querySelectorAll(".star").forEach(star => {
        star.classList.remove("text-yellow-500");
    });

    try {
        // Récupère les notes des livres lus
        const [readBooksResponse, likedBooks, rating] = await Promise.all([
            fetch(`/read/${userId}`).then(res => res.json()),
            getReadBooksLike(userId),
            getBookRating(userId, bookId)
        ]);

        const isRead = readBooksResponse.some(book => book.includes(bookId));
        const isLiked = likedBooks.map(item => item[0]).includes(bookId);

        console.log("Livre:", bookId, "Est lu ?", isRead, "Est liké ?", isLiked, "Note:", rating);

        // Mise à jour des boutons
        if (isRead) {
            readButton.style.color = "green";
            likeButton.style.display = "inline-block";
            likeButton.style.color = isLiked ? "red" : "";

            if (isLiked && rating !== null) {
                starsContainer.classList.remove("hidden");
                highlightStars(rating);
            }
        } else {
            readButton.style.color = "";
            likeButton.style.display = "none";
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






function addToWishlist(button, colorClass) {
    const bookId = document.getElementById('book-id-num').textContent;
    const userId = localStorage.getItem('user_id');
    if (!bookId || !userId) {
        alert("Erreur : Impossible d'ajouter à la wishlist.");
        return;
    }
    sendRequest(`/wishlist/add/${bookId}/${userId}`, button, colorClass);
}

function addToLike(button, colorClass) {
    let ratingStars = document.getElementById("rating-stars");
    ratingStars.classList.remove("hidden");

    document.querySelectorAll(".star").forEach(star => {
        star.replaceWith(star.cloneNode(true));
    });

    document.querySelectorAll(".star").forEach(star => {
        star.addEventListener("click", async function() {
            let selectedValue = this.getAttribute("data-value");
            const bookId = document.getElementById('book-id-num').textContent;
            const userId = localStorage.getItem('user_id');

            if (!bookId || !userId) {
                alert("Erreur : Impossible d'ajouter aux likes.");
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
                document.getElementById("rating-stars").classList.add("hidden");
                console.log("Note enregistrée avec succès !");
            } catch (error) {
                console.error("Erreur réseau :", error);
                alert("Erreur de connexion.");
            }
        });
    });
}


function addToRead(button) {
    const bookId = document.getElementById('book-id-num').textContent;
    const userId = localStorage.getItem('user_id');
    if (!bookId || !userId) {
        alert("Erreur : Impossible d'ajouter à la liste des lus.");
        return;
    }
    button.style.color = "green"
    sendRequest(`/read/${userId}/${bookId}`, button);
}




