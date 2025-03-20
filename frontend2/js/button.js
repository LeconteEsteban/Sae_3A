function toggleFill(button, colorClass) {
    const svg = button.querySelector('svg');
    if (svg.classList.contains(colorClass)) {
        svg.classList.remove(colorClass);
        button.classList.remove(colorClass);
    } else {
        svg.classList.add(colorClass);
        button.classList.add(colorClass);
    }
}

function sendRequest(url, button, colorClass) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            toggleFill(button, colorClass);
            console.log("Action effectuée avec succès :", url);
        } else {
            alert("Erreur lors de l'action.");
        }
    })
    .catch(error => {
        console.error("Erreur réseau :", error);
        alert("Erreur de connexion.");
    });
}

function sendRequestPUT(url, button, colorClass) {
    fetch(url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            toggleFill(button, colorClass);
            console.log("Action effectuée avec succès :", url);
        } else {
            alert("Erreur lors de l'action.");
        }
    })
    .catch(error => {
        console.error("Erreur réseau :", error);
        alert("Erreur de connexion.");
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
        star.addEventListener("click", function() {
            let selectedValue = this.getAttribute("data-value");
            const bookId = document.getElementById('book-id-num').textContent;
            const userId = localStorage.getItem('user_id');
            if (!bookId || !userId) {
                alert("Erreur : Impossible d'ajouter aux likes.");
                return;
            }
            sendRequestPUT(`/reviews/${userId}/${bookId}/${selectedValue}`, document.getElementById("like-button"), "text-red-500");
            document.getElementById("rating-stars").classList.add("hidden");
        });
    });
}

function addToRead(button, colorClass) {
    const bookId = document.getElementById('book-id-num').textContent;
    const userId = localStorage.getItem('user_id');
    if (!bookId || !userId) {
        alert("Erreur : Impossible d'ajouter à la liste des lus.");
        return;
    }
    sendRequest(`/read/${userId}/${bookId}`, button, colorClass);
}