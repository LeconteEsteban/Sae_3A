document.addEventListener("DOMContentLoaded", function () {
    // Slider principal
    const prevButton = document.querySelector('.prev');
    const nextButton = document.querySelector('.next');
    const slides = document.querySelectorAll('.slide');
    const sliderWrapper = document.querySelector('.slider-wrapper');
    let currentIndex = 0;

    const updateSliderPosition = () => {
        const slideWidth = slides[0].offsetWidth;
        sliderWrapper.style.transform = `translateX(-${currentIndex * slideWidth}px)`;
    };

    nextButton.addEventListener('click', () => {
        if (currentIndex < slides.length - 1) {
            currentIndex++;
        } else {
            currentIndex = 0; // Retour au début
        }
        updateSliderPosition();
    });

    prevButton.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
        } else {
            currentIndex = slides.length - 1; // Retour à la fin
        }
        updateSliderPosition();
    });

    // Initialisation de la position du slider
    updateSliderPosition();

    // Slider Top 10
    const prevButtonTop10 = document.querySelector('.prev-top10');
    const nextButtonTop10 = document.querySelector('.next-top10');
    const slidesTop10 = document.querySelectorAll('.slide-top10');
    const sliderWrapperTop10 = document.querySelector('.slider-wrapper-top10');
    let currentIndexTop10 = 0;

    const updateSliderPositionTop10 = () => {
        const slideWidth = slidesTop10[0].offsetWidth;
        sliderWrapperTop10.style.transform = `translateX(-${currentIndexTop10 * slideWidth}px)`;
    };

    nextButtonTop10.addEventListener('click', () => {
        if (currentIndexTop10 < slidesTop10.length - 1) {
            currentIndexTop10++;
        } else {
            currentIndexTop10 = 0; // Retour au début
        }
        updateSliderPositionTop10();
    });

    prevButtonTop10.addEventListener('click', () => {
        if (currentIndexTop10 > 0) {
            currentIndexTop10--;
        } else {
            currentIndexTop10 = slidesTop10.length - 1; // Retour à la fin
        }
        updateSliderPositionTop10();
    });

    // Initialisation de la position du slider Top 10
    updateSliderPositionTop10();
});



// Gestion de la barre de recherche
document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById('search-input');
    const resultsPopup = document.getElementById('search-results-popup');
    let searchTimeout;

    // Fonction pour afficher les résultats dans la pop-up
    function displayResults(books) {
        resultsPopup.innerHTML = ''; // Effacer les résultats précédents

        if (books.length === 0) {
            resultsPopup.innerHTML = '<div class="p-2 text-gray-500">Aucun résultat trouvé.</div>';
        } else {
            const maxResults = 10; // Limite le nombre de résultats affichés
            books.slice(0, maxResults).forEach(book => {
                const resultElement = document.createElement('div');
                resultElement.classList.add('p-2', 'hover:bg-gray-100', 'cursor-pointer', 'flex','items-center', 'gap-4');
                resultElement.innerHTML = `
                    <img src="${
                                book.url !== "-1" ? book.url : "/static/notfound.jpg"
                                }" alt="Couverture de ${
                                book.title
                            }" class="w-24 h-32 object-cover rounded transition-transform duration-300">
                    <div>
                        <h3 class="font-semibold">${book.title}</h3>
                        <p class="text-sm text-gray-600">${book.author_name || "pas auteur"}</p>
                    </div>
                    
                `;
                resultsPopup.appendChild(resultElement);
            });
        }

        // Afficher la pop-up
        resultsPopup.classList.remove('hidden');
    }

    function showLoading() {
        resultsPopup.innerHTML = '<div class="p-2 text-gray-500">Chargement en cours...</div>';
        resultsPopup.classList.remove('hidden');
    }

    // Fonction pour effectuer la recherche via l'API
    async function performSearch() {
        const query = searchInput.value.trim();

        if (query.length < 2) {
            resultsPopup.classList.add('hidden');
            return;
        }

        showLoading(); // Afficher l'indicateur de chargement

        try {
            const response = await fetch(`http://127.0.0.1:8000/books/search?query=${encodeURIComponent(query)}&skip=0&limit=10`);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Erreur HTTP:', response.status, response.statusText, errorText);
                throw new Error(`Erreur HTTP: ${response.status} - ${response.statusText}`);
            }

            const books = await response.json();
            console.log('Réponse de l\'API:', books);
            

            // Afficher les résultats dans la pop-up
            displayResults(books);
        } catch (error) {
            console.error('Erreur lors de la recherche:', error);
            resultsPopup.innerHTML = '<div class="p-2 text-gray-500">Erreur lors de la recherche. Veuillez réessayer.</div>';
            resultsPopup.classList.remove('hidden');
        }
    }

    // Écouteur d'événement pour la saisie dans la barre de recherche avec debouncing
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout); // Annuler le délai précédent
        searchTimeout = setTimeout(performSearch, 100); // Délai de 300 ms
    });

    // Cacher la pop-up lorsqu'on clique en dehors
    document.addEventListener('click', function (event) {
        if (!searchInput.contains(event.target) && !resultsPopup.contains(event.target)) {
            resultsPopup.classList.add('hidden');
        }
    });
});

// Gestion des comptes
function openModal() {
    document.getElementById('loginModal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('loginModal').classList.add('hidden');
}

// Gestion du formulaire de connexion
document.getElementById('loginFormElement').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });

        if (response.ok) {
            const data = await response.json();
            // Stocker l'utilisateur dans un cookie
            document.cookie = `user=${encodeURIComponent(JSON.stringify(data.user.user_id))}; path=/; max-age=43200`; // Expire dans 24h
            document.cookie = `username=${encodeURIComponent(JSON.stringify(data.user.name))}; path=/; max-age=43200`; // Expire dans 24h
            document.getElementById('usernameHeader').textContent = data.user.name;
            document.getElementById('usernameHeader').classList.remove('hidden');
            document.getElementById('loginButton').classList.add('hidden');
            closeModal();
        } else {
            alert('Identifiants incorrects');
        }
    } catch (error) {
        console.error(error);
        alert('Erreur lors de la connexion');
    }
});

// Switcher entre Login/Register
function switchToRegister() {
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('registerForm').classList.remove('hidden');
}

function switchToLogin() {
    document.getElementById('registerForm').classList.add('hidden');
    document.getElementById('loginForm').classList.remove('hidden');
}

// Gestion du formulaire d'inscription
document.getElementById('registerFormElement').addEventListener('submit', async (e) => {
    e.preventDefault();
    const newUsername = document.getElementById('newUsername').value;
    const newPassword = document.getElementById('newPassword').value;

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: newUsername,
                password: newPassword,
                age: 'N/A',
                child: false,
                familial_situation: 'N/A',
                gender: 'N/A',
                cat_socio_pro: 'N/A',
                lieu_habitation: 'N/A',
                frequency: 'N/A',
                book_size: 'N/A',
                birth_date: '2000-01-01'
            }),
        });

        if (response.ok) {
            alert('Compte créé avec succès !');
            switchToLogin();
        } else {
            alert('Erreur lors de la création du compte');
        }
    } catch (error) {
        console.error(error);
        alert('Erreur de serveur');
    }
});

// Gestion du menu burger
function openBurgerHeader() {
    if (document.getElementById('menuBurger').classList.contains('hidden')) {
        document.getElementById('menuBurger').classList.remove('hidden');
    } else {
        document.getElementById('menuBurger').classList.add('hidden');
    }
}

// Gestion de la déconnexion
function handleLogout() {
    clearAllCookies(); // Supprime tous les cookies
    document.getElementById('loginButton').classList.remove('hidden');
    document.getElementById('usernameHeader').classList.add('hidden');
    document.getElementById('menuBurger').classList.add('hidden');
}

// Fonctions utilitaires pour les cookies
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return decodeURIComponent(parts.pop().split(';').shift());
    }
    return null;
}

function getIdAccount() {
    const userCookie = getCookie('user');
    if (userCookie) {
        const user = JSON.parse(userCookie);
        return user;
    }
}

function getNameAccount() {
    const userCookie = getCookie('username');
    if (userCookie) {
        const user = JSON.parse(userCookie);
        return user;
    }
}

function deleteCookie(name) {
    document.cookie = `${name}=; path=/; max-age=0;`;
}

function clearAllCookies() {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
        const name = cookie.split('=')[0].trim();
        deleteCookie(name);
    }
}