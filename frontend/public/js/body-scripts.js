document.addEventListener("DOMContentLoaded", function () {
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
});

document.addEventListener("DOMContentLoaded", function () {
    const prevButton = document.querySelector('.prev-top10');
    const nextButton = document.querySelector('.next-top10');
    const slides = document.querySelectorAll('.slide-top10');
    const sliderWrapper = document.querySelector('.slider-wrapper-top10');
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
});


//Code pour gérer les comptes
function openModal() {
document.getElementById('loginModal').classList.remove('hidden');
}

function closeModal() {
document.getElementById('loginModal').classList.add('hidden');
}

// Gestion du formulaire
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
            //alert('Connexion réussie !');
            //mettre le texte data.user.name dans usernameHeader
            document.getElementById('usernameHeader').textContent = data.user.name;
            document.getElementById('usernameHeader').classList.remove('hidden');
            document.getElementById('loginButton').classList.add('hidden');
            //document.getElementById('logoutButton').classList.remove('hidden');
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
showStep(1);
}

function switchToLogin() {
document.getElementById('registerForm').classList.add('hidden');
document.getElementById('loginForm').classList.remove('hidden');
}

// Afficher une étape et cacher les autres
function showStep(step) {
    document.querySelectorAll('.register-step').forEach((el) => el.classList.add('hidden'));
    document.getElementById(`registerStep${step}`).classList.remove('hidden');
}

// Passer à l'étape suivante
function nextStep(currentStep) {
    showStep(currentStep + 1);
}

// Revenir à l'étape précédente
function prevStep(currentStep) {
    showStep(currentStep - 1);
}

// Fonction qui vérifie si les champs "Identifiant" et "Mot de passe" sont remplis
function checkFieldsStep1() {
    const username = document.getElementById('newUsername').value;
    const password = document.getElementById('newPassword').value;
    const nextButton = document.getElementById('nextButton1');

    // Si les deux champs sont remplis, activer le bouton
    if (username && password) {
        nextButton.disabled = false;
    } else {
        nextButton.disabled = true;
    }
}

// Ajouter des écouteurs d'événements pour les champs "Identifiant" et "Mot de passe"
document.getElementById('newUsername').addEventListener('input', checkFieldsStep1);
document.getElementById('newPassword').addEventListener('input', checkFieldsStep1);

// Appeler la fonction au début pour s'assurer que l'état du bouton est correct
checkFieldsStep1();

// Gestion de la soumission du formulaire d'inscription
document.getElementById('registerFormElement').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const userData = {
        username: document.getElementById('newUsername').value,
        password: document.getElementById('newPassword').value,
        age: document.getElementById('age').value,
        gender: document.getElementById('gender').value,
        cat_socio_pro: document.getElementById('cat_socio_pro').value,
        lieu_habitation: document.getElementById('lieu_habitation').value,
        child: false,
        familial_situation: 'N/A',
        frequency: document.getElementById('frequency').value,
        book_size: document.getElementById('book_size').value,
        birth_date: document.getElementById('birth_date').value,
    };
    const childValue = document.querySelector('input[name="child"]:checked');
    userData.child = childValue ? childValue.value === "true" : false;

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData),
        });

        if (response.ok) {
            alert('Compte créé avec succès !');
            switchToLogin();
        } else {
            const errorData = await response.json();
            if (errorData.detail=="Nom d'utilisateur déjà pris.") {
                showStep(1);
            }
            alert(errorData.detail || 'Erreur lors de la création du compte');
        }
    } catch (error) {
        console.error(error);
        alert('Erreur de serveur');
    }
});

function openBurgerHeader(){
    if (document.getElementById('menuBurger').classList.contains('hidden')) {
        document.getElementById('menuBurger').classList.remove('hidden');
    }else{
        document.getElementById('menuBurger').classList.add('hidden');
    }
    
}

function handleLogout() {
    clearAllCookies(); // Supprime tous les cookies
    document.getElementById('loginButton').classList.remove('hidden');
    document.getElementById('usernameHeader').classList.add('hidden');
    document.getElementById('menuBurger').classList.add('hidden');
    //alert('Déconnexion réussie !');
}

// fin du code pour gérer les comptes

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return decodeURIComponent(parts.pop().split(';').shift());
    }
    return null;
}

function getIdAccount(){
    const userCookie = getCookie('user');
    if (userCookie) {
        const user = JSON.parse(userCookie);
        //console.log('Utilisateur connecté :', user);
        return user;
    }
}
function getNameAccount(){
    const userCookie = getCookie('username');
    if (userCookie) {
        const user = JSON.parse(userCookie);
        //console.log('Utilisateur connecté :', user);
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