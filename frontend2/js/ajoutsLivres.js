let allPublishers = [];
let allAwards = [];
let allAuthors = [];
let allGenres = [];

async function loadData() {
    try {
        const [publishersRes, awardsRes, authorsRes, genresRes] = await Promise.all([
            fetch("/publishers/all"),
            fetch("/awards/all"),
            fetch("/authors/all"),
            fetch("/genres/all")
        ]);

        allPublishers = await publishersRes.json();
        allAwards = await awardsRes.json();
        allAuthors = await authorsRes.json();
        allGenres = await genresRes.json();
    } catch (error) {
        console.error("Erreur lors du chargement des données :", error);
    }
}

document.addEventListener("DOMContentLoaded", async function() {
    await loadData();
});
function searchItems(inputId, resultsId, dataList, selectedContainerId) {
    const inputField = document.getElementById(inputId);
    const resultsContainer = document.getElementById(resultsId);
    const selectedContainer = document.getElementById(selectedContainerId);

    const query = inputField.value.toLowerCase();
    resultsContainer.innerHTML = "";

    if (query.length < 2) {
        resultsContainer.classList.add("hidden");
        return;
    }

    const filteredResults = dataList.filter(item => item.name.toLowerCase().includes(query));

    if (filteredResults.length > 0) {
        resultsContainer.classList.remove("hidden");
        filteredResults.forEach(item => {
            const li = document.createElement("li");
            li.textContent = item.name;
            li.classList.add("px-4", "py-2", "cursor-pointer", "hover:bg-gray-200");

            li.onclick = () => {
                addSelectedTag(item, inputField, selectedContainer);
                resultsContainer.classList.add("hidden");
            };

            resultsContainer.appendChild(li);
        });
    } else {
        resultsContainer.classList.add("hidden");
    }
}

// Fonction générique pour ajouter un élément à un conteneur de tags
function addSelectedTag(item, inputField, container) {
    // Vérifie si l'élément est déjà sélectionné
    if (Array.from(container.children).some(tag => tag.dataset.id == item.id)) return;

    const tag = document.createElement("span");
    tag.textContent = item.name;
    tag.classList.add("bg-blue-200", "px-2", "py-1", "rounded", "mr-2", "cursor-pointer");
    tag.dataset.id = item.id;

    // Enlève le tag au clic
    tag.onclick = () => {
        tag.remove();
    };

    container.appendChild(tag);

    // Réinitialiser l'input
    inputField.value = "";
}

function getSelectedTags(selectedContainerId) {
    const selectedContainer = document.getElementById(selectedContainerId);
    return Array.from(selectedContainer.children).map(tag => tag.dataset.id);
}




// 🔥 Expose les fonctions pour qu'elles soient accessibles dans le HTML
window.searchPublishers = () => searchItems("publisherSearch", "publisherResults", allPublishers, "selectedPublishers");
window.searchAwards = () => searchItems("awardSearch", "awardResults", allAwards, "selectedAwards");
window.searchAuthors = () => searchItems("bookAuthor", "authorsList", allAuthors, "selectedAuthors");
window.searchGenres = () => searchItems("bookGenres", "genresList", allGenres, "selectedGenres");



// 🔥 Gestion modale
document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("addBookModal");
    const openModalButton = document.getElementById("openModalButton");
    const closeModalButton = document.getElementById("closeModalButton");

    if (openModalButton && closeModalButton && modal) {
        openModalButton.addEventListener("click", () => modal.classList.remove("hidden"));
        closeModalButton.addEventListener("click", () => modal.classList.add("hidden"));
    }


    
    

    // Formulaire d'ajout de livre
    const bookForm = document.getElementById("bookForm");
    if (bookForm) {
        bookForm.addEventListener("submit", function(event) {
            event.preventDefault();

            const bookTitle = document.getElementById("bookTitle").value;
            const bookIsbn = document.getElementById("bookIsbn").value;
            const bookIsbn13 = document.getElementById("bookIsbn13").value;
            const bookDescription = document.getElementById("bookDescription").value;
            const bookNumberOfPages = document.getElementById("bookNumberOfPages").value;

            // Utilise dataset.selectedId pour obtenir l'ID du publisher
            const bookPublisherIds = getSelectedTags("selectedPublishers");
            const bookAwardIds = getSelectedTags("selectedAwards");
            const bookAuthorIds = getSelectedTags("selectedAuthors");
            const bookGenres = getSelectedTags("selectedGenres");




            // NOTE: On envoie ici les IDs des awards et publishers
            const bookData = {
                title: bookTitle,
                isbn: bookIsbn,
                isbn13: bookIsbn13,
                description: bookDescription,
                number_of_pages: parseInt(bookNumberOfPages),
                publisher_ids: bookPublisherIds.map(id => parseInt(id)), // IDs des éditeurs
                author_ids: bookAuthorIds.map(id => parseInt(id)), // IDs des auteurs
                genre_ids: bookGenres.map(id => parseInt(id)), // IDs des genres
                award_ids: bookAwardIds.map(id => parseInt(id)) // IDs des prix
            };
            
            

            console.log("bookData avant l'envoi:", bookData);

            fetch("/books/add", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(bookData)
            })
            .then(response => {
                if (!response.ok) {
                    return response.text().then(text => { throw new Error(text); });
                }
                return response.json();
            })
            .then(data => {
                console.log("Réponse de l'API :", data); 
                alert(`Livre ajouté avec succès ! ID du livre: ${data.book_id}`);
                bookForm.reset();

                document.getElementById("selectedPublishers").innerHTML = '';
                document.getElementById("selectedAwards").innerHTML = '';
                document.getElementById("selectedAuthors").innerHTML = '';
                document.getElementById("selectedGenres").innerHTML = '';
                modal.classList.add('hidden');
            })
            .catch(error => {
                console.error("Erreur lors de l'ajout du livre :", error);
                alert("Erreur lors de l'ajout du livre.");
            });
        });
    }
});

document.getElementById("openAddAuthorModal").addEventListener("click", function() {
    document.getElementById("addAuthorModal").classList.remove("hidden");
});
document.getElementById("closeAuthorModalButton").addEventListener("click", function() {
    document.getElementById("addAuthorModal").classList.add("hidden");
});

// Gestion du formulaire d'ajout d'auteur
document.getElementById("authorForm").addEventListener("submit", async function(event) {
    event.preventDefault();
    const name = document.getElementById("authorName").value;
    const birthplace = document.getElementById("authorBirthplace").value;
    
    try {
        const response = await fetch("/authors/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, birthplace })
        });
        
        if (!response.ok) {
            throw new Error("Erreur lors de l'ajout de l'auteur");
        }
        
        const newAuthor = await response.json();
        alert("Auteur ajouté avec succès !");
        
        // Ajouter l'auteur à la liste des auteurs
        const authorsList = document.getElementById("authorsList");
        const li = document.createElement("li");
        li.textContent = `${newAuthor.name} (${newAuthor.birthplace})`;
        li.classList.add("p-2", "cursor-pointer", "hover:bg-gray-200");
        authorsList.appendChild(li);
        
        document.getElementById("addAuthorModal").classList.add("hidden");
    } catch (error) {
        alert(error.message);
    }
});