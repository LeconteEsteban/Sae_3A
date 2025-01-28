const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

//services
const postgresqlService = require('./scripts/postgresqlService');

// Servir les fichiers statiques (HTML/CSS/JS frontend)
app.use(express.static(path.join(__dirname, '../frontend/public')));

// Route pour la page du livre
app.get('/livre', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/public/livre.html'));
});

// Route pour la page du main
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/public/index.html'));
});

// Connexion via Socket.IO
io.on('connection', (socket) => {
    console.log('Nouvelle connexion Socket.IO');

    // Réception d'une demande de livre
    socket.on('get_livre', async (bookId) => {
        console.log('Demande de livre reçue :', bookId);

        try {
            // Récupérer les données du livre depuis la base de données
            const bookData = await postgresqlService.getBookDataBdd(bookId);

            // Envoi des données du livre au client
            socket.emit('data_livre', bookData);
        } catch (error) {
            console.error('Erreur lors de la récupération des données du livre :', error);
            socket.emit('data_livre', { error: 'Erreur lors de la récupération des données du livre' });
        }
    });

    socket.on('disconnect', () => {
        console.log('Utilisateur déconnecté');
    });
});

// Lancer le serveur
const PORT = 3000;
server.listen(PORT, () => {
    console.log(`Serveur lancé sur http://localhost:${PORT}`);
});
