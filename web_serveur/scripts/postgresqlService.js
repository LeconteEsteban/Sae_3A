const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');

// Spécifier le chemin du fichier .env
dotenv.config({ path: path.resolve(__dirname, '../../.env') });

class PostgresqlService {
    constructor() {
        // Créer un pool de connexions PostgreSQL
        this.pool = new Pool({
            user: process.env.DB_USER,
            host: process.env.DB_HOST,
            database: process.env.DB_NAME,
            password: process.env.DB_PASSWORD,
            port: process.env.DB_PORT,
        });
    }

    async connect() {
        const client = await this.pool.connect();
        return client;
    }

    async getBookDataBdd(bookId) {
        const client = await this.connect();
        try {
            const query = `
                SELECT
                    bv.book_id,
                    bv.title,
                    bv.isbn,
                    bv.isbn13,
                    bv.author_name,
                    bv.description,
                    bv.number_of_pages,
                    bv.publisher_name,
                    array_agg(DISTINCT bv.genre_name) AS genre_names,
                    array_agg(DISTINCT bv.award_name) AS award_names,
                    bv.rating_count,
                    bv.average_rating,
                    bc.cover_url
                FROM
                    library.book_view bv
                LEFT JOIN
                    library.Book_Cover bc ON bv.book_id = bc.book_id
                WHERE
                    bv.book_id = $1
                GROUP BY
                    bv.book_id, bv.title,bv.isbn,
                    bv.author_name,
                    bv.description,
                    bv.number_of_pages, bv.publisher_name,  bv.rating_count, bv.average_rating, bv.isbn13, bc.cover_url;
            `;
            const values = [bookId];
            const res = await client.query(query, values);
            return res.rows[0]; // Renvoie la première ligne de résultats
        } finally {
            client.release(); // Libérer le client pour le retourner au pool
        }
    }

    async getBookCoverUrl(bookId, isbn) {
        const client = await this.connect();
        try {
            // Vérifier si une couverture existe
            const coverQuery = `
                SELECT cover_url
                FROM library.Book_Cover
                WHERE book_id = $1;
            `;
            const coverRes = await client.query(coverQuery, [bookId]);
    
            if (coverRes.rowCount > 0) {
                // Si une couverture existe, la renvoyer
                return coverRes.rows[0].cover_url;
            }
    
            // Si aucune couverture n'existe, appeler l'API
            const apiUrl = `https://www.googleapis.com/books/v1/volumes?q=isbn:${isbn}`;
            const response = await fetch(apiUrl);
            const data = await response.json();
            let coverUrl = '-1'; // Valeur par défaut si aucune couverture n'est trouvée
    
            if (data.items && data.items.length > 0) {
                coverUrl = data.items[0].volumeInfo.imageLinks?.thumbnail || '-1';
            }
    
            // Insérer l'URL dans la base de données
            const insertQuery = `
                INSERT INTO library.Book_Cover (book_id, isbn13, cover_url)
                VALUES ($1, $2, $3)
                ON CONFLICT (book_id) DO UPDATE SET cover_url = $3; -- pour gérer les doublons
            `;
            await client.query(insertQuery, [bookId, isbn, coverUrl]);
    
            return coverUrl; // Retourner la couverture
        } catch (error) {
            console.error('Erreur lors de la récupération ou de l\'insertion de la couverture :', error);
            throw error;
        } finally {
            client.release();
        }
    }
    
    
}

module.exports = new PostgresqlService();
