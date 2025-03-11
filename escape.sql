DROP SCHEMA IF EXISTS library CASCADE;
CREATE SCHEMA IF NOT EXISTS library;
SET search_path TO library;


-- Table Genre
CREATE TABLE Genre (
                       genre_id SERIAL PRIMARY KEY,
                       name VARCHAR(255) NOT NULL
);

CREATE INDEX idx_genre_name_fulltext ON Genre USING GIN (to_tsvector('simple', lower(name)));

-- Book
-- Table Publisher
CREATE TABLE Publisher (
                           publisher_id SERIAL PRIMARY KEY,
                           name VARCHAR(200) NOT NULL
);

-- Table Serie
CREATE TABLE Serie (
                       serie_id SERIAL PRIMARY KEY,
                       name VARCHAR(150)
);

-- Table Award
CREATE TABLE Award (
                       award_id SERIAL PRIMARY KEY,
                       name TEXT NOT NULL
);

-- Table Settings
CREATE TABLE Settings (
                          settings_id SERIAL PRIMARY KEY,
                          description TEXT
);

-- Table Characters
CREATE TABLE Characters (
                            characters_id SERIAL PRIMARY KEY,
                            name varchar(150)
);

---End book
--- Questionnary

-- Table Type_book
CREATE TABLE Type_book (
                           type_id SERIAL PRIMARY KEY,
                           type_name VARCHAR(255)
);

-- Table Format_of_reading
CREATE TABLE Format_of_reading (
                                   format_reading_id SERIAL PRIMARY KEY,
                                   format_name VARCHAR(255)
);

-- Table Field_of_reading
CREATE TABLE Field_of_reading (
                                  field_id SERIAL PRIMARY KEY,
                                  field_name VARCHAR(255)
);

-- Table Interest
CREATE TABLE Interest (
                          interest_id SERIAL PRIMARY KEY,
                          description VARCHAR(255)
);

-- End questionnary

-- Table Book
CREATE TABLE Book (
                      book_id SERIAL PRIMARY KEY,
                      title VARCHAR(255) NOT NULL,
                      publication_date DATE,
                      original_title TEXT,
                      number_of_pages INTEGER,
                      isbn VARCHAR(255),
                      isbn13 VARCHAR(255),
                      description TEXT,
                      publisher_id INTEGER REFERENCES Publisher(publisher_id)
);

CREATE INDEX idx_book_title_fulltext ON Book USING GIN (to_tsvector('french', title));
CREATE INDEX idx_book_description_fulltext ON Book USING GIN (to_tsvector('french', description));
CREATE INDEX idx_book_fulltext ON Book USING GIN (
                                                  to_tsvector('french', title || ' ' || description)
    );
CREATE INDEX idx_book_publication_date ON Book (publication_date);

CREATE EXTENSION IF NOT EXISTS vector;
-- SET search_path to library, public;
-- peut être bugger en fonction des environnements, contacter angely! mais grosso modo, l'extension pgvector est activé dans public, et pas dans library
CREATE TABLE Book_vector (
    id INT PRIMARY KEY,
    title TEXT,
    vector public.VECTOR(384)
);


-- Table Author
CREATE TABLE Author (
                        author_id SERIAL PRIMARY KEY,
                        name VARCHAR(70) NOT NULL,
                        gender VARCHAR(20),
                        birthplace VARCHAR(70)
);

CREATE INDEX idx_author_name_fulltext ON Author USING GIN (to_tsvector('simple', lower(name)));

-- Table wrote
CREATE TABLE Wrote (
                                 book_id INTEGER REFERENCES Book(book_id),
                                 author_id INTEGER REFERENCES Author(author_id),
                                 PRIMARY KEY (book_id, author_id)
);

-- Table User
CREATE TABLE _Users (
                        user_id SERIAL PRIMARY KEY,
                        name VARCHAR(50),
                        age VARCHAR(30),
                        passwords VARCHAR(100),
                        child boolean,
                        familial_situation varchar(70),
                        gender VARCHAR(20),
                        cat_socio_pro varchar(50),
                        lieu_habitation varchar(50),
                        frequency varchar(40),
                        book_size varchar(32),
                        birth_date DATE
);


-- Table User_vector
CREATE TABLE User_vector(
    id INT PRIMARY KEY,
    vector public.VECTOR(1536)
);

-- Table Rating_book
CREATE TABLE Rating_book (
                             rating_id SERIAL PRIMARY KEY,
                             book_id INTEGER REFERENCES Book(book_id),
                             rating_count INTEGER,
                             review_count INTEGER,
                             average_rating FLOAT,
                             five_star_rating INTEGER,
                             four_star_rating INTEGER,
                             three_star_rating INTEGER,
                             two_star_rating INTEGER,
                             one_star_rating INTEGER
);

CREATE MATERIALIZED VIEW library.top_books
(
  book_id,
  title,
  average_rating,
  rating_count,
  review_count,
  score
)
AS 
SELECT DISTINCT ON (b.book_id)
    b.book_id,
    b.title,
    rb.average_rating,
    rb.rating_count,
    rb.review_count,
    rb.average_rating * 20000::double precision + rb.rating_count::double precision + (rb.review_count::numeric * 0.1)::double precision AS score
FROM 
    library.book b
JOIN 
    library.rating_book rb ON b.book_id = rb.book_id
ORDER BY 
    b.book_id, rb.average_rating DESC, rb.rating_count DESC;

CREATE UNIQUE INDEX top_books_book_id_idx ON library.top_books USING btree (book_id);



-- Table Rating_author
CREATE TABLE Rating_author (
                               rating_id SERIAL PRIMARY KEY,
                               author_id INTEGER REFERENCES Author(author_id),
                               average_author_rating FLOAT,
                               author_rating_count INTEGER,
                               author_review_count INTEGER
);

-- Table Book_similarity
CREATE TABLE Book_similarity (
                                 book_id1 INTEGER REFERENCES Book(book_id),
                                 book_id2 INTEGER REFERENCES Book(book_id),
                                 similarity_score NUMERIC,
                                 PRIMARY KEY (book_id1, book_id2)
);
CREATE INDEX idx_book_similarity_book_id1 ON Book_similarity (book_id1);

-- Créer la table User_Book_Review sans clé étrangère
CREATE TABLE User_Book_Review (
    review_id SERIAL PRIMARY KEY, 
    review VARCHAR(500),      
    notation_id INT NOT NULL
);

-- Créer la table User_Book_Notation sans clé étrangère
CREATE TABLE User_Book_Notation (
    notation_id SERIAL PRIMARY KEY, 
    note SMALLINT,                   
    review_id INT,  
    read_id INT NOT NULL
);

-- Table User_Book_Preference user liked those book
CREATE TABLE User_Book_Read (
    read_id SERIAL PRIMARY KEY,
    user_id INTEGER ,
    book_id INTEGER ,
    is_read boolean,
    is_liked boolean, 
    is_favorite boolean,
    reading_date date,
    notation_id INT
);


-- Table User_Book_Notation
CREATE TABLE User_Liked_Genre (
    user_liked_genre_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    genre_id INTEGER
);

-- Table Genre_and_vote
CREATE TABLE Genre_and_vote (
        book_id INTEGER ,
        genre_id INTEGER,
        vote_count INTEGER,
        PRIMARY KEY (book_id, genre_id)
);

CREATE INDEX idx_genre_and_vote_genre_id ON Genre_and_vote (genre_id);
CREATE INDEX idx_genre_and_vote_book_id ON Genre_and_vote (book_id);

-- Table Friends
CREATE TABLE Friends (
                         user_id1 INTEGER REFERENCES _Users(user_id),
                         user_id2 INTEGER REFERENCES _Users(user_id),
                         friendship_date DATE,
                         PRIMARY KEY (user_id1, user_id2)
);

-- Table WishListe
CREATE TABLE WishListe (
                         wish_id SERIAL PRIMARY KEY,
                         user_id INTEGER REFERENCES _Users(user_id),
                         book_id INTEGER REFERENCES Book(book_id),
                         add_date DATE
);

-- Table genre affinity (User's liked genres)
CREATE TABLE Genre_affinity (
                       user_id INTEGER REFERENCES _Users(user_id),
                       genre_id INTEGER REFERENCES Genre(genre_id),
                       count int,
                       PRIMARY KEY (user_id, genre_id)
);

-- Table Serie_of_book
CREATE TABLE Serie_of_book (
                               book_id INTEGER REFERENCES Book(book_id),
                               serie_id INTEGER REFERENCES Serie(serie_id),
                               PRIMARY KEY (book_id, serie_id)
);

-- Table Award_of_book
CREATE TABLE Award_of_book (
                               book_id INTEGER REFERENCES Book(book_id),
                               award_id INTEGER REFERENCES Award(award_id),
                               PRIMARY KEY (book_id, award_id)
);

-- Table settings_of_book
CREATE TABLE Settings_of_book (
                                 book_id INTEGER REFERENCES Book(book_id),
                                 settings_id INTEGER REFERENCES Settings(settings_id),
                                 PRIMARY KEY (book_id, settings_id)
);

-- Table Characters_of_book
CREATE TABLE Characters_of_book (
                                    book_id INTEGER REFERENCES Book(book_id),
                                    characters_id INTEGER REFERENCES characters(characters_id),
                                    PRIMARY KEY (book_id, characters_id)
);

-- Table Liked_author (User's liked author)
CREATE TABLE Liked_author (
                              user_id INTEGER REFERENCES _Users(user_id),
                              author_id INTEGER REFERENCES Author(author_id),
                              PRIMARY KEY (user_id, author_id)
);

-- Table Preferred_format_of_reading (User's preferred format of reading)
CREATE TABLE Preferred_format_of_reading (
                                             format_id SERIAL PRIMARY KEY,
                                             user_id INTEGER REFERENCES _Users(user_id),
                                             format VARCHAR(100)
);

-- Create the User_field_of_reading table
CREATE TABLE User_field_of_reading (
    field_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES _Users(user_id),
    field VARCHAR(100)
);

-- Table Book_Cover
CREATE TABLE Book_Cover (
                               book_id INTEGER REFERENCES Book(book_id),
                               isbn13 VARCHAR(255),
                               cover_url VARCHAR(255),
                               PRIMARY KEY (book_id)
);


--Questionary relation

-- Table Preferred_format_of_reading (questionary's preferred format of reading)
CREATE TABLE Preferred_format_of_reading_user (
                                                         user_id INTEGER REFERENCES _Users(user_id),
                                                         format_id INTEGER REFERENCES Format_of_reading(format_reading_id),
                                                         PRIMARY KEY (user_id, format_id)
);

-- Table User_field_of_reading (questionary's field of reading)
CREATE TABLE User_field_of_reading_user (
                                                   user_id INTEGER REFERENCES _Users(user_id),
                                                   field_id INTEGER REFERENCES Field_of_reading(field_id),
                                                   PRIMARY KEY (user_id, field_id)
);



--TRIGGERS

--triggers book rating

--validate book rating values
CREATE OR REPLACE FUNCTION validate_book_rating_values() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.five_star_rating < 0 OR
       NEW.four_star_rating < 0 OR
       NEW.three_star_rating < 0 OR
       NEW.two_star_rating < 0 OR
       NEW.one_star_rating < 0 THEN
        RAISE EXCEPTION 'Rating values cannot be negative';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_book_rating_values
BEFORE INSERT OR UPDATE ON Rating_book
FOR EACH ROW
EXECUTE FUNCTION validate_book_rating_values();


--triggers author rating

--validate author rating values
CREATE OR REPLACE FUNCTION check_author_rating_count() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.author_rating_count < 0 THEN
        RAISE EXCEPTION 'Author rating count cannot be negative';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER validate_author_rating_count
BEFORE INSERT OR UPDATE ON Rating_author
FOR EACH ROW
EXECUTE FUNCTION check_author_rating_count();


--End Triggers

---Views

--Author
create view author_view as
select a.author_id,
       a.name,
       a.gender,
       a.birthplace,
       ra.average_author_rating,
       ra.author_rating_count,
       ra.author_review_count
from author a
left join rating_author ra on a.author_id = ra.author_id;


--View book
create view book_view as
select b.book_id, b.title, b.publication_date, b.original_title,
       b.number_of_pages, b.isbn, b.isbn13, b.description,
       p.name as publisher_name,
       g.name as genre_name,
       a.name as award_name,
       s.name as serie_name,
       sett.description as settings_description,
       c.name as characters_name,
       rb.rating_count ,
       rb.average_rating,
       rb.five_star_rating ,
       rb.four_star_rating,
       rb.three_star_rating,
       rb.two_star_rating,
       rb.one_star_rating,
       av.name as author_name
from book b
left join Genre_and_vote Gav on b.book_id = Gav.book_id
left join Genre g on g.genre_id = Gav.genre_id
left join Publisher p on b.publisher_id = p.publisher_id
left join Serie_of_book Sob on b.book_id = Sob.book_id
left join Serie s on s.serie_id = Sob.serie_id
left join Award_of_book Aob on b.book_id = Aob.book_id
left join Award a on a.award_id = Aob.award_id
left join Settings_of_book Setob on b.book_id = Setob.book_id
left join Settings sett on sett.settings_id = Setob.settings_id
left join Characters_of_book Cob on b.book_id = Cob.book_id
left join Characters c on c.characters_id = Cob.characters_id
left join rating_book rb on b.book_id = rb.book_id
left join Wrote wr on b.book_id = wr.book_id
left join author_view av on wr.author_id = av.author_id;


