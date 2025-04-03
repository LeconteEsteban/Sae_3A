async function fetchBooksByCategory() {
    try {
        const response = await fetch("/statistique/count_by_genre"); 
        if (!response.ok) {
            throw new Error("Erreur lors de la récupération des données");
        }
        const data = await response.json();

        const labels = data.map(item => item.genre_name);
        const values = data.map(item => item.book_count);

        const ctx1 = document.getElementById('booksByCategoryA').getContext('2d');
        const chart = new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Nombre de livres',
                    data: values,
                    backgroundColor: 'rgba(255, 99, 132, 0.6)',
                }]
            },
        });

    } catch (error) {
        console.error("Erreur:", error);
    }
}

// Appelle la fonction au chargement de la page
fetchBooksByCategory();
