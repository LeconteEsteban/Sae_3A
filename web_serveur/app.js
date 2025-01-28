const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

//services
const postgresqlService = require('./scripts/postgresqlService');

app.use(bodyParser.json());

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

// Route pour créer un nouvel utilisateur
app.post('/api/register', async (req, res) => {
    const user = req.body;
    try {
        const newUser = await postgresqlService.createUser(user);
        res.status(201).json({ message: 'Utilisateur créé avec succès', userId: newUser.user_id });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Erreur lors de la création de l\'utilisateur' });
    }
});

// Route pour se connecter
app.post('/api/login', async (req, res) => {
    try {
        const user = await postgresqlService.authenticateUser(req.body.username, req.body.password);
        if (user) {
            res.status(200).json({ message: 'Connexion réussie', user });
        } else {
            res.status(401).json({ message: 'Nom ou mot de passe incorrect' });
        }
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Erreur lors de la connexion' });
    }
});


// Lancer le serveur
const PORT = 3000;
server.listen(PORT, () => {
    console.log(`Serveur lancé sur http://localhost:${PORT}`);
});
