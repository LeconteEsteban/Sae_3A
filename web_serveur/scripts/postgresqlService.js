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
                    bv.author_name,
                    bv.description,
                    bv.number_of_pages,
                    bv.publisher_name,
                    array_agg(DISTINCT bv.genre_name) AS genre_names,
                    array_agg(DISTINCT bv.award_name) AS award_names,
                    bv.rating_count,
                    bv.average_rating
                FROM
                    library.book_view bv
                WHERE
                    bv.book_id = $1
                GROUP BY
                    bv.book_id, bv.title,bv.isbn,
                    bv.author_name,
                    bv.description,
                    bv.number_of_pages, bv.publisher_name, bv.rating_count, bv.average_rating;
            `;
            const values = [bookId];
            const res = await client.query(query, values);
            return res.rows[0]; // Renvoie la première ligne de résultats
        } finally {
            client.release(); // Libérer le client pour le retourner au pool
        }
    }

    // Créer un nouvel utilisateur
    async createUser(user) {
        const client = await this.connect();
        try {
            const query = `
                INSERT INTO library._Users 
                (name, age, passwords, child, familial_situation, gender, cat_socio_pro, lieu_habitation, frequency, book_size, birth_date)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                RETURNING user_id;
            `;
            const values = [
                user.username,
                user.age,
                user.password,
                user.child,
                user.familial_situation,
                user.gender,
                user.cat_socio_pro,
                user.lieu_habitation,
                user.frequency,
                user.book_size,
                user.birth_date,
            ];
            const res = await client.query(query, values);
            return res.rows[0]; // Retourne l'ID du nouvel utilisateur
        } finally {
            client.release();
        }
    }

    // Authentifier un utilisateur
    async authenticateUser(name, passwords) {
        const client = await this.connect();
        try {
            const query = `
                SELECT * FROM library._Users
                WHERE name = $1 AND passwords = $2;
            `;
            const values = [name, passwords];
            const res = await client.query(query, values);
            return res.rows.length > 0 ? res.rows[0] : null; // Renvoie l'utilisateur ou null
        } finally {
            client.release();
        }
    }
    
}

module.exports = new PostgresqlService();
