document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("search-input");
    const searchButton = document.getElementById("search-button");

    function saveSearch() {
        if (!searchInput) return;

        const query = searchInput.value.trim();
        if (query !== "") {
            localStorage.setItem("searchQuery", query);
            console.log("Requête enregistrée :", query);
            window.location.href = "/static/search.html"; 
        }
    }

    if (searchButton) {
        searchButton.addEventListener("click", saveSearch);
    }

    if (searchInput) {
        searchInput.addEventListener("keypress", function (event) {
            if (event.key === "Enter") {
                saveSearch();
            }
        });
    }
});
