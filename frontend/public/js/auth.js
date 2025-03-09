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
            const [topBooks1] = await Promise.all([
                fetchBooks(`/recommandations/user/${data.user.user_id}/30`)
                //fetchBooks(`/recommandations/user/2/30`)
              ]);
            initializeCarousel(topBooks1, "Newcarousel");
            
            const [topBooks2] = await Promise.all([
                fetchBooks(`/recommandations/user/book/${data.user.user_id}/30`)
                //fetchBooks("/recommandations/user/book/2/30")
              ]);
            initializeCarousel(topBooks2, "Newcarousel1");
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
            fetchBooks(`/recommandations/user/${getIdAccount()}/30`)
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
            fetchBooks(`/recommandations/user/book/${getIdAccount()}/30`)
          ]);
        initializeCarousel(topBooks2, "Newcarousel1");
    } else {
        const [topBooks1] = await Promise.all([
            fetchBooks("/books/topbook/30")
          ]);
          initializeCarousel(topBooks1, "Newcarousel1");
    }
    
}
// Switcher entre Login/Register
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

// Passer à l'étape suivante
export function nextStep(currentStep) {
    showStep(currentStep + 1);
}

// Revenir à l'étape précédente
export function prevStep(currentStep) {
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
    const [topBooks1] = await Promise.all([
        fetchBooks("/books/topbook/30")
      ]);
      initializeCarousel(topBooks1, "Newcarousel");
    
      const [topBooks2] = await Promise.all([
        fetchBooks("/books/topbook/30")
      ]);
      initializeCarousel(topBooks2, "Newcarousel1");
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
