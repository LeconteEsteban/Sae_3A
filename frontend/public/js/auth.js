import { initializeCarousel } from './carousel.js';

// Gestion des comptes
export function openModal() {
    document.getElementById('loginModal').classList.remove('hidden');
}

export function closeModal() {
    document.getElementById('loginModal').classList.add('hidden');
}

async function fetchBooks(url) {  
    try {
      const response = await fetch(url);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`Erreur lors de la récupération des données depuis ${url}:`, error);
      return [];
    }
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
            var swiperWrapper = document.querySelector(`#Newcarousel`);
            swiperWrapper.innerHTML = "";
            swiperWrapper = document.querySelector(`#Newcarousel1`);
            swiperWrapper.innerHTML = "";
            fetchBooks(`/recommandations/hybrid/${data.user.user_id}/30`).then(topBooks1 => 
                initializeCarousel(topBooks1, "Newcarousel")
              ).catch(error => console.error("Error fetching Newcarousel:", error));
            fetchBooks(`/recommandations/item/${data.user.user_id}/30`).then(topBooks2 => 
                initializeCarousel(topBooks2, "Newcarousel1")
              ).catch(error => console.error("Error fetching Newcarousel1:", error));
        } else {
            alert('Identifiants incorrects');
        }
    } catch (error) {
        console.error(error);
        alert('Erreur lors de la connexion');
    }
});

export async function reload_hybrid() {
    var swiperWrapper = document.querySelector(`#Newcarousel`);
    swiperWrapper.innerHTML = "";
    if (getIdAccount() != -1) {
        const [topBooks1] = await Promise.all([
            fetchBooks(`/recommandations/hybrid/${getIdAccount()}/30`)
        ]);
        initializeCarousel(topBooks1, "Newcarousel");
    }else{
    const [topBooks1] = await Promise.all([
        fetchBooks("/books/topbook/30")
      ]);
      initializeCarousel(topBooks1, "Newcarousel");
    }
    
}
export async function reload_item() {
    var swiperWrapper = document.querySelector(`#Newcarousel1`);
    swiperWrapper.innerHTML = "";
    if (getIdAccount() != -1) {
        const [topBooks2] = await Promise.all([
            fetchBooks(`/recommandations/item/${getIdAccount()}/30`)
          ]);
        initializeCarousel(topBooks2, "Newcarousel1");
    } else {
        const [topBooks1] = await Promise.all([
            fetchBooks("/books/topbook/30")
          ]);
          initializeCarousel(topBooks1, "Newcarousel1");
    }
    
}// Switcher entre Login/Register
export function switchToRegister() {
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('registerForm').classList.remove('hidden');
    showStep(1);
}

export function switchToLogin() {
    document.getElementById('registerForm').classList.add('hidden');
    document.getElementById('loginForm').classList.remove('hidden');
}

// Afficher une étape et cacher les autres
export function showStep(step) {
    document.querySelectorAll('.register-step').forEach((el) => el.classList.add('hidden'));
    document.getElementById(`registerStep${step}`).classList.remove('hidden');
}



// Revenir à l'étape précédente
export function prevStep(currentStep) {
    showStep(currentStep - 1);
}

// Fonction pour afficher un message d'erreur sous un champ
function showError(inputId, message) {
    const errorElement = document.getElementById(`${inputId}-error`);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.remove('hidden');
    }
}

// Fonction pour enlever l'erreur d'un champ
function clearError(inputId) {
    const errorElement = document.getElementById(`${inputId}-error`);
    if (errorElement) {
        errorElement.textContent = "";
        errorElement.classList.add('hidden');
    }
}

let hasTriedToSubmit = false; // Empêcher l'affichage des messages d'erreurs si l'utilisateur n'a pas cliqué sur "suivant".

function validateStep(step) {
    if (!hasTriedToSubmit){ 
        return true;
     } 

    let isValid = true;

    if (step === 1) {
        const username = document.getElementById('newUsername').value.trim();
        const password = document.getElementById('newPassword').value;

        const usernameRegex = /^[a-zA-Z0-9_-]{3,20}$/; 
        if (!usernameRegex.test(username)) {
            showError('newUsername', "⚠️ L'identifiant doit contenir entre 3 et 20 caractères avec uniquement des lettres, chiffres, _ ou -.");
            isValid = false;
        } else {
            clearError('newUsername');
        }

        const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$/; 
        if (!passwordRegex.test(password)) {
            showError('newPassword', "⚠️ Le mot de passe doit contenir au moins 8 caractères avec au moins une lettre et un chiffre.");
            isValid = false;
        } else {
            clearError('newPassword');
        }
    }

    // Vérification de la date de naissance à l'étape 5 (étape de validation du formulaire)
    if (step === 5) { 
        const birthDateInput = document.getElementById('birth_date').value;
        const birthDateObj = new Date(birthDateInput);
        const today = new Date();
    
        if (!birthDateInput || isNaN(birthDateObj.getTime()) || birthDateObj > today) {
            showError('birth_date', "⚠️ La date de naissance ne peut pas être vide ou dans le futur.");
            isValid = false;
        } else {
            clearError('birth_date');
        }
    }
    

    return isValid;
}


function nextStep(currentStep) {
    hasTriedToSubmit = true; // L'utilisateur a cliqué sur le bouton "suivant"
    if (validateStep(currentStep)) {
        showStep(currentStep + 1);
    }
}

// Ajout des écouteurs pour masquer l'erreur dès que l'utilisateur modifie le champ
document.getElementById('newUsername').addEventListener('input', () => {
    if (hasTriedToSubmit) validateStep(1);
});
document.getElementById('newPassword').addEventListener('input', () => {
    if (hasTriedToSubmit) validateStep(1);
});

// Gestion de la soumission du formulaire d'inscription
document.getElementById('registerFormElement').addEventListener('submit', async (e) => {
    e.preventDefault();

    const userData = {
        username: document.getElementById('newUsername').value.trim(),
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

    // Vérification par rapport à la date actuelle
    const today = new Date();
    const birthDateObj = new Date(userData.birth_date);

    // Test si la date saisie est dans le futur
    if (userData.birth_date && (isNaN(birthDateObj.getTime()) || birthDateObj > today)) {
        showError('birth_date', "⚠️ La date de naissance ne peut pas être dans le futur.");
        return; // Bloquer si la date n'est pas renseignée
    } else {
        clearError('birth_date');
    }

    // Vérifications pour la création du compte au moment de la finalisation de l'inscription
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
            // Test si le nom d'utilisateur est déjà pris
            if (errorData.detail === "Nom d'utilisateur déjà pris.") {
                showError('newUsername', "⚠️ Ce nom d'utilisateur est déjà pris.");
                showStep(1); 
            }
            
            alert(errorData.detail || 'Erreur lors de la création du compte');
        }
    } catch (error) {
        console.error(error);
        alert('Erreur de serveur');
    }
});

// Gestion du menu burger
export function openBurgerHeader() {
    if (document.getElementById('menuBurger').classList.contains('hidden')) {
        document.getElementById('menuBurger').classList.remove('hidden');
    } else {
        document.getElementById('menuBurger').classList.add('hidden');
    }
}

// Gestion de la déconnexion
export async function handleLogout() {
    clearAllCookies(); // Supprime tous les cookies
    document.getElementById('loginButton').classList.remove('hidden');
    document.getElementById('usernameHeader').classList.add('hidden');
    document.getElementById('menuBurger').classList.add('hidden');
    var swiperWrapper = document.querySelector(`#Newcarousel`);
    swiperWrapper.innerHTML = "";
    swiperWrapper = document.querySelector(`#Newcarousel1`);
    swiperWrapper.innerHTML = "";
    fetchBooks("/books/topbook/30").then(topBooks1 => 
        initializeCarousel(topBooks1, "Newcarousel")
      ).catch(error => console.error("Error fetching Newcarousel:", error));
    fetchBooks("/books/topbook/30").then(topBooks2 => 
        initializeCarousel(topBooks2, "Newcarousel1")
      ).catch(error => console.error("Error fetching Newcarousel1:", error));
}

// Fonctions utilitaires pour les cookies
export function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        return decodeURIComponent(parts.pop().split(';').shift());
    }
    return null;
}

export function getIdAccount() {
    const userCookie = getCookie('user');
    if (userCookie) {
        const user = JSON.parse(userCookie);
        return user;
    }else{
        return -1;
    }
}

export function getNameAccount() {
    const userCookie = getCookie('username');
    if (userCookie) {
        const user = JSON.parse(userCookie);
        return user;
    }
}

export function deleteCookie(name) {
    document.cookie = `${name}=; path=/; max-age=0;`;
}

export function clearAllCookies() {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
        const name = cookie.split('=')[0].trim();
        deleteCookie(name);
    }
}


// Rendre les fonctions accessible globalement
window.openModal = openModal;
window.closeModal = closeModal;
window.handleLogout = handleLogout;
window.openBurgerHeader = openBurgerHeader;
window.prevStep = prevStep;
window.nextStep = nextStep;
window.showStep = showStep;
window.switchToLogin = switchToLogin;
window.switchToRegister = switchToRegister;
window.clearAllCookies = clearAllCookies;
window.deleteCookie = deleteCookie;
window.getNameAccount = getNameAccount;
window.getIdAccount = getIdAccount;
window.getCookie = getCookie;
window.reload_hybrid = reload_hybrid;
window.reload_item = reload_item;
