// Choper les infos du sessionStorage
document.addEventListener("DOMContentLoaded", async () => {
    const userId = localStorage.getItem("user_id");

    if (!userId) {
        console.log("Aucun utilisateur connecté.");
        return;
    }

    try {
        const response = await fetch(`/api/user/${userId}`);
        if (!response.ok) {
            throw new Error("Erreur lors de la récupération des infos utilisateur");
        }

        const userData = await response.json();
        console.log("Utilisateur récupéré :", userData);

        localStorage.setItem("user_data", JSON.stringify(userData));

        document.querySelectorAll(".user-name").forEach(el => el.textContent = userData.name);

    } catch (error) {
        console.error("Erreur lors du chargement de l'utilisateur :", error);
    }
});

// Affiche les infos de l'utilisateurs depuis une modale
async function showUserInfo() {
    const userId = localStorage.getItem("user_id");
    if (!userId) {
        console.error("Aucun utilisateur connecté.");
        return;
    }

    try {
        const response = await fetch(`/api/user/${userId}`);
        if (!response.ok) {
            throw new Error("Erreur lors de la récupération des infos utilisateur");
        }

        const userData = await response.json();
        console.log("Utilisateur récupéré :", userData);

        localStorage.setItem("user_data", JSON.stringify(userData));

        console.log("Données passées à updateUserModal :", userData);

        document.body.style.overflow = "hidden"
        updateUserModal(userData);
        const modal = document.getElementById("userInfoModal");
        modal.addEventListener("click", (e) => {
            if(e.target === modal ) hideUserInfo();
        })
        
        modal.classList.remove("hidden");

    } catch (error) {
        console.error("Erreur lors du chargement de l'utilisateur :", error);
    }
}




function updateUserModal(userData) {
    const fields = {
        userName: userData.name.trim() || "Non renseigné",
        userAge: userData.age || "N/A",
        userChild: userData.child ? "Oui" : "Non",
        userFamily: userData.familial_situation || "N/A",
        userGender: userData.gender || "N/A",
        userSocioPro: userData.cat_socio_pro || "N/A",
        userLocation: userData.lieu_habitation || "N/A",
        userFrequency: userData.frequency || "N/A",
        userBookSize: userData.book_size || "N/A",
        userBirthDate: formatBirthDate(userData.birth_date),
    };

    // Update la modale avec les infos récupérées
    Object.keys(fields).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = fields[id];
        }
    });
}

// Gérer le format de la date
function formatBirthDate(dateStr) {
    if (!dateStr) return "N/A";
    const date = new Date(dateStr);
    return date.toLocaleDateString("fr-FR", {
        day: "numeric",
        month: "long",
        year: "numeric"
    });
}

// Fermer la modale

function hideUserInfo() {
    document.getElementById("userInfoModal").classList.add("hidden");
    document.body.style.overflow = "auto"
}

window.showUserInfo = showUserInfo;
window.hideUserInfo = hideUserInfo;
