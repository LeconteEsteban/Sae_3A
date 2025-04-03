// Fonction stockage pour la page précédant la connexion

function stockagePagePrecedente() {
    const currentPage = window.location.href;
    console.log("Page actuelle avant stockage:", currentPage);

    // Supprime la valeur enregistrée dans le local storage
    localStorage.removeItem('previousPage'); 
    localStorage.setItem('previousPage', currentPage);

    console.log("Page stockée dans localStorage:", localStorage.getItem('previousPage')); 

    // Redirige vers la page de connexion
    setTimeout(() => {
        window.location.href = "/static/connexionPage.html";
    }, 50);
}

window.stockagePagePrecedente = stockagePagePrecedente;


document.addEventListener("DOMContentLoaded", function () {
    const toggleToRegister = document.getElementById("toggle-register");
    const toggleToLogin = document.getElementById("toggle-login");
    const loginForm = document.getElementById("loginFormElement"); 
    const registerForm = document.getElementById("registerForm");

    if (toggleToRegister && toggleToLogin && loginForm && registerForm) {
        toggleToRegister.addEventListener("click", function (event) {
            event.preventDefault();

            loginForm.classList.add("hidden");
            registerForm.classList.remove("hidden");
        });

        toggleToLogin.addEventListener("click", function (event) {
            event.preventDefault(); 
            registerForm.classList.add("hidden");
            loginForm.classList.remove("hidden");
        });
    } 
});





export function openModal() {
    document.getElementById('loginModal').classList.remove('hidden');
}

export function closeModal() {

    const previousPage = localStorage.getItem('previousPage');

    if (previousPage) {
        window.location.href = previousPage;
    }
}

async function adminLogin(username, password) {
    try {
        const response = await fetch('/api/admin/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });

        if (response.ok) {
            const data = await response.json();


            localStorage.setItem("user_id", data.user.user_id);
            localStorage.setItem("username", data.user.name);
            localStorage.setItem("role", data.user.role);

            window.location.href = "/static/adminpage.html";
        } else {
            alert('Accès refusé : Vous devez être administrateur.');
        }
    } catch (error) {
        console.error(error);
        alert('Erreur lors de la connexion admin');
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const userRole = localStorage.getItem('role');
    const userId = localStorage.getItem('user_id');

    const adminPages = [
        "/static/ajoutsLivres.html",
        "/static/adminpage.html"
    ];

    const currentPage = window.location.pathname;

    // Rediriger l'admin si il est pas connecté
    if (adminPages.includes(currentPage) && userRole !== 'admin') {
        localStorage.removeItem('user_id');
        localStorage.removeItem('username');
        localStorage.removeItem('role');
        localStorage.removeItem('user_data');
        window.location.href = "/static/connexionPageAdmin.html";
    }

    // Déconnecter l'admin s'il force la connexion
    if (userRole === 'admin' && (currentPage === "/" || currentPage === "/#")) {
        localStorage.removeItem('user_id');
        localStorage.removeItem('username');
        localStorage.removeItem('role');
        localStorage.removeItem('user_data');
    }
});


const adminLoginForm = document.getElementById('adminLoginForm');

if (adminLoginForm) {
    adminLoginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        await adminLogin(username, password);
    });
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

const loginFormElement = document.getElementById('loginFormElement');

// Vérifier que le formulaire existe avant d'ajouter l'écouteur d'événements
if (loginFormElement) {
    loginFormElement.addEventListener('submit', async (e) => {
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

                localStorage.setItem("user_id", data.user.user_id);
                localStorage.setItem("username", data.user.name);

                const previousPage = localStorage.getItem('previousPage') || "/";
                localStorage.removeItem('previousPage'); 

                window.location.href = previousPage;

            } else {
                alert('Identifiants incorrects');
            }
        } catch (error) {
            console.error(error);
            alert('Erreur lors de la connexion');
        }
    });
}




// Switcher entre Login/Register
function switchToRegister() {
    const loginForm = document.getElementById('loginFormElement');
    const registerForm = document.getElementById('registerForm');

    if (!loginForm || !registerForm) {
        console.error("⚠️ ERREUR : Un des éléments est introuvable !");
        return;
    }

    loginForm.classList.add("hidden");
    registerForm.classList.remove("hidden");
}


const loginForm = document.getElementById('loginFormElement');
if (!loginForm) {
} else {
    switchToLogin();
}


export function switchToLogin() {
    document.getElementById('registerForm').classList.add('hidden');
    document.getElementById('loginFormElement').classList.remove('hidden');
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

let hasTriedToSubmit = false; 

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
    hasTriedToSubmit = true; // L'utilisateur a cliqué sur "Suivant" -> active la validation

    if (validateStep(currentStep)) {
        console.log("Validation OK, passage à l'étape suivante :", currentStep + 1);
        showStep(currentStep + 1); 
    } else {
        console.log("Validation échouée à l'étape :", currentStep);
    }
}

function showStep(step) {
    console.log("Affichage de l'étape :", step);
    
    document.querySelectorAll('.register-step').forEach(el => el.classList.add('hidden'));
    
    const nextStep = document.getElementById(`registerStep${step}`);
    if (nextStep) {
        nextStep.classList.remove('hidden');
    } else {
        console.error("Erreur : étape introuvable", step);
    }
}


// Ajout des écouteurs pour masquer l'erreur dès que l'utilisateur modifie le champ
if (document.getElementById('newUsername')) {
    document.getElementById('newUsername').addEventListener('input', () => {
        if (hasTriedToSubmit) validateStep(1);
    });
}

if (document.getElementById('newPassword')) {
    document.getElementById('newPassword').addEventListener('input', () => {
        if (hasTriedToSubmit) validateStep(1);
    });
}

// Gestion de la soumission du formulaire d'inscription
const registerFormElement = document.getElementById('registerFormElement');

if (registerFormElement) {
    registerFormElement.addEventListener('submit', async (e) => {
        e.preventDefault();

        const userData = {
            username: document.getElementById('newUsername').value.trim(),
            password: document.getElementById('newPassword').value,
            age: document.getElementById('age').value,
            gender: document.getElementById('gender').value,
            cat_socio_pro: document.getElementById('cat_socio_pro').value,
            lieu_habitation: document.getElementById('lieu_habitation').value,
            child: document.querySelector('input[name="child"]:checked').value === "true",  
            familial_situation: document.getElementById('familial_situation') ? document.getElementById('familial_situation').value : null,
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
}




window.openModal = openModal;
window.closeModal = closeModal;
window.prevStep = prevStep;
window.nextStep = nextStep;
window.showStep = showStep;
window.switchToLogin = switchToLogin;
window.switchToRegister = switchToRegister;

