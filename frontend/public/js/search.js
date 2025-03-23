import { showPopup } from './popup.js';

// Gestion de la barre de recherche
document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById('search-input');
    const resultsPopup = document.getElementById('search-results-popup');
    const genreDropdownButton = document.getElementById('genreDropdownButton');
    const genreDropdown = document.getElementById('genreDropdown');
    let selectedGenres = new Set();
    let searchTimeout;
    let errorTimeout;

    // Fonction pour afficher les résultats dans la pop-up
    function displayResults(books) {
        resultsPopup.innerHTML = '';
        if (books.length === 0) {
            resultsPopup.innerHTML = '<div class="p-2 text-gray-500">Aucun résultat trouvé.</div>';
        } else {
            const maxResults = 100;
            const query = searchInput.value.trim(); // Récupère la recherche en cours
    
            books.slice(0, maxResults).forEach(book => {
                const resultElement = document.createElement('div');
                resultElement.classList.add('p-4', 'hover:bg-gray-100', 'cursor-pointer', 'flex', 'items-center', 'gap-4');
                resultElement.id = book.id; 
    
                const rawDescription = book.description || "Aucune description disponible.";
                const description = rawDescription.replace(/#virgule/g, ",");
    
                // Fonction pour mettre en évidence le texte correspondant
                const highlightText = (text, query) => {
                    if (!query) return text;
                    const regex = new RegExp(`(${query})`, "gi");
                    return text.replace(regex, '<span class="bg-yellow-200">$1</span>');
                };
    
                // Appliquer la mise en surbrillance au titre et à l'auteur
                const highlightedTitle = highlightText(book.title, query);
                const highlightedAuthor = book.author_name ? highlightText(book.author_name, query) : "";
    
                resultElement.innerHTML = `
                    <img src="${book.url !== "-1" ? book.url : "/static/notfound.jpg"}" alt="Couverture de ${book.title}" class="w-24 h-32 object-cover rounded transition-transform duration-300">
                    <div>
                        <h3 class="font-semibold">${highlightedTitle}</h3>
                        <p class="text-sm text-gray-600">${highlightedAuthor}</p>
                        <p class="text-sm text-gray-500 mt-1 overflow-hidden text-ellipsis line-clamp-2 max-h-[3em] leading-[1.5em]">${description}</p>
                    </div>
                `;
    
                // Ajouter un événement de clic pour afficher plus d'infos
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
            // Récupérer les genres sélectionnés sous forme de tableau
            const selectedGenresArray = Array.from(selectedGenres);

            // Ajouter les genres comme paramètre dans la requête
            const genresParam = selectedGenresArray.length > 0 ? `&genres=${encodeURIComponent(selectedGenresArray.join(','))}` : '';

            // Effectuer la recherche avec la requête et les genres sélectionnés
            const response = await fetch(`/books/search?query=${encodeURIComponent(query)}${genresParam}&skip=0&limit=20`);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Erreur HTTP:', response.status, response.statusText, errorText);
                throw new Error(`Erreur HTTP: ${response.status} - ${response.statusText}`);
            }

            const books = await response.json();
            
            // Afficher les résultats dans la pop-up
            if (query === searchInput.value.trim() && query === currentQuery) {
                displayResults(books); // Passer la requête pour le tri
            }
            console.log(`/books/search?query=${encodeURIComponent(query)}${genresParam}&skip=0&limit=20`)
            
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


    // clic sur le bouton Genre
    genreDropdownButton.addEventListener('click', async function () {
        // Si la liste est déjà visible, la cacher
        if (!genreDropdown.classList.contains('hidden')) {
            genreDropdown.classList.add('hidden');
            return;
        }

        // Récupérer les genres via l'API
        try {
            const response = await fetch('/genres/all');
            if (!response.ok) throw new Error('Erreur lors de la récupération des genres');

            const genres = await response.json();
            genreDropdown.innerHTML = ''; // Vide la liste avant de la remplir

            genres.forEach(genre => {
                const listItem = document.createElement('li');
                listItem.textContent = genre.name;
                listItem.classList.add('px-4', 'py-2', 'hover:bg-gray-100', 'cursor-pointer', 'list-none', 'pl-0', 'ml-2');

                // Appliquer la sélection si ce genre est déjà sélectionné
                if (selectedGenres.has(genre.name)) {
                    listItem.classList.add('bg-gray-300');
                }

                // Gestion de la sélection/désélection
                listItem.addEventListener('click', (event) => {
                    event.stopPropagation(); // Empêche la fermeture instantanée

                    if (selectedGenres.has(genre.name)) {
                        selectedGenres.delete(genre.name);
                        listItem.classList.remove('bg-gray-300');
                    } else {
                        selectedGenres.add(genre.name);
                        listItem.classList.add('bg-gray-300');
                    }

                    console.log("Genres sélectionnés :", Array.from(selectedGenres));
                    
                    // Réactualiser la recherche dès qu'un genre est modifié
                    const query = searchInput.value.trim();
                    if (query.length >= 2) {
                        performSearch(); // Effectuer la recherche à chaque modification des genres
                    }
                });

                genreDropdown.appendChild(listItem);
            });

            genreDropdown.classList.remove('hidden'); // Afficher la liste
            genreDropdown.classList.add('max-h-60', 'overflow-y-auto');

        } catch (error) {
            console.error("Erreur API :", error);
            genreDropdown.innerHTML = '<div class="p-2 text-red-500">Erreur lors du chargement</div>';
            genreDropdown.classList.remove('hidden');
        }
    });

    // Fermer la liste si on clique en dehors
    document.addEventListener('click', function (event) {
        if (!genreDropdownButton.contains(event.target) && !genreDropdown.contains(event.target)) {
            genreDropdown.classList.add('hidden');
        }
    });

});