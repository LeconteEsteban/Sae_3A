import { showPopup } from './popup.js';

// Gestion de la barre de recherche
document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById('search-input');
    const resultsPopup = document.getElementById('search-results-popup');
    let searchTimeout;
    let errorTimeout;

    // Fonction pour afficher les résultats dans la pop-up
    function displayResults(books) {
        resultsPopup.innerHTML = '';
        if (books.length === 0) {
            resultsPopup.innerHTML = '<div class="p-2 text-gray-500">Aucun résultat trouvé.</div>';
        } else {
            const maxResults = 100;
            books.slice(0, maxResults).forEach(book => {
                const resultElement = document.createElement('div');
                resultElement.classList.add('p-4', 'hover:bg-gray-100', 'cursor-pointer', 'flex', 'items-center', 'gap-4');
                resultElement.id = book.id; 
    
                const rawDescription = book.description || "Aucune description disponible.";
                const description = rawDescription.replace(/#virgule/g, ",");
    
                resultElement.innerHTML = `
                    <img src="${book.url !== "-1" ? book.url : "/static/notfound.jpg"}" alt="Couverture de ${book.title}" class="w-24 h-32 object-cover rounded transition-transform duration-300">
                    <div>
                        <h3 class="font-semibold">${book.title}</h3>
                        <p class="text-sm text-gray-600">${book.author_name || ""}</p>
                        <p class="text-sm text-gray-500 mt-1 overflow-hidden text-ellipsis line-clamp-2 max-h-[3em] leading-[1.5em]">${description}</p>
                    </div>
                `;
    
               
                resultElement.addEventListener("click", () => {
                    showPopup(book);
                });
    
                resultsPopup.appendChild(resultElement);
            });
        }
        resultsPopup.classList.remove('hidden');
    }
    

    function showLoading() {
        resultsPopup.innerHTML = '<div class="p-2 text-gray-500">Chargement en cours...</div>';
        resultsPopup.classList.remove('hidden');
    }

    // Variable globale pour stocker la requête actuelle
    let currentQuery = '';
    // Fonction pour effectuer la recherche via l'API
    async function performSearch() {

        

        const query = searchInput.value.trim();
        currentQuery = query; // Mettre à jour la requête en cours

        if (query.length < 2) {
            resultsPopup.classList.add('hidden');
            return;
        }

        showLoading(); // Afficher l'indicateur de chargement

        try {
            const response = await fetch(`/books/search?query=${encodeURIComponent(query)}&skip=0&limit=20`);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Erreur HTTP:', response.status, response.statusText, errorText);
                throw new Error(`Erreur HTTP: ${response.status} - ${response.statusText}`);
            }

            const books = await response.json();
            console.log('Réponse de l\'API:', books);
            

            // Afficher les résultats dans la pop-up
            if (query === searchInput.value.trim() && query === currentQuery) {
                displayResults(books); // Passer la requête pour le tri
            }
            
        } catch (error) {
            console.error('Erreur lors de la recherche:', error);
            // Ajouter un délai avant d'afficher l'erreur
            errorTimeout = setTimeout(() => {
                resultsPopup.innerHTML = '<div class="p-2 text-gray-500">Erreur lors de la recherche. Veuillez réessayer.</div>';
                resultsPopup.classList.remove('hidden');
            }, 3000); // Délai de 3 secondes avant d'afficher l'erreur
        }
    }

    // Écouteur d'événement pour la saisie dans la barre de recherche avec debouncing
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout); // Annuler le délai précédent
        clearTimeout(errorTimeout); // Annuler le délai d'erreur précédent
        searchTimeout = setTimeout(performSearch, 300); // Délai de 300 ms
    });

    // Réafficher la pop-up des résultats lorsqu'on clique dans la barre de recherche
    searchInput.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query.length >= 2) {
            resultsPopup.classList.remove('hidden'); // Réafficher la pop-up
        }
    });


    // Cacher la pop-up lorsqu'on clique en dehors
    document.addEventListener('click', function (event) {
        if (!searchInput.contains(event.target) && !resultsPopup.contains(event.target)) {
            resultsPopup.classList.add('hidden');
        }
    });
});