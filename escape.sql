DROP SCHEMA IF EXISTS biblio CASCADE;
CREATE SCHEMA biblio;
SET SCHEMA 'biblio';

-- Table User
CREATE TABLE User (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    birth_date DATE,
    gender VARCHAR(255) CHECK (gender IN (male,female, other)), 
    favorite_book_id INTEGER REFERENCES Book(book_id),
    favorite_author_id INTEGER REFERENCES Author(author_id)
);

-- Table Book
CREATE TABLE Book (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    publication_date DATE,
    original_title VARCHAR(255),
    number_of_pages INTEGER,
    isbn VARCHAR(10),
    isbn13 VARCHAR(13),
    description TEXT,
    publisher_id INTEGER REFERENCES Publisher(publisher_id)
    
);

-- Table Author
CREATE TABLE Author (
    author_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    gender VARCHAR(255) CHECK (gender IN (male,female, other)), 
    birthplace VARCHAR(255)
);

-- Table Genre
CREATE TABLE Genre (
    genre_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Table Publisher
CREATE TABLE Publisher (
    publisher_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Table Serie
CREATE TABLE Serie (
    serie_id SERIAL PRIMARY KEY,
    name VARCHAR(255)
);


-- Table Award
CREATE TABLE Award (
    award_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Table Settings
CREATE TABLE Settings (
    setting_id SERIAL PRIMARY KEY,
    description VARCHAR(255)
);

-- Table Characters
CREATE TABLE Characters (
    character_id SERIAL PRIMARY KEY,
    name VARCHAR(255)
);


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

-- Table Questionary
CREATE TABLE Questionary (
    questionary_id SERIAL PRIMARY KEY,
    question TEXT NOT NULL
);

-- Table Rating_book
CREATE TABLE Rating_book (
    rating_id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES Book(book_id),
    rating INTEGER,
    comment TEXT
);

-- Table Rating_author
CREATE TABLE Rating_author (
    rating_id SERIAL PRIMARY KEY,
    author_id INTEGER REFERENCES Author(author_id),
    rating INTEGER,
    comment TEXT
);

-- Table Book_similarity
CREATE TABLE Book_similarity (
    book_id1 INTEGER REFERENCES Book(book_id),
    book_id2 INTEGER REFERENCES Book(book_id),
    similarity_score NUMERIC,
    PRIMARY KEY (book_id1, book_id2)
);

-- Table User_Book_Interaction
CREATE TABLE User_Book_Interaction (
    interaction_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES User(user_id),
    book_id INTEGER REFERENCES Book(book_id),
    interaction_type VARCHAR(255),
    interaction_date TIMESTAMP
);

-- Table User_Book_Preference
CREATE TABLE User_Book_Preference (
    preference_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES User(user_id),
    genre_id INTEGER REFERENCES Genre(genre_id)
);

-- Table User_Book_History
CREATE TABLE User_Book_History (
    history_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES User(user_id),
    book_id INTEGER REFERENCES Book(book_id),
    reading_date DATE
);

-- Table Genre_and_vote
CREATE TABLE Genre_and_vote (
    book_id INTEGER REFERENCES Book(book_id),
    genre_id INTEGER REFERENCES Genre(genre_id),
    vote_count INTEGER,
    PRIMARY KEY (book_id, genre_id)
);

-- Table Friends
CREATE TABLE Friends (
    user_id1 INTEGER REFERENCES User(user_id),
    user_id2 INTEGER REFERENCES User(user_id),
    friendship_date DATE,
    PRIMARY KEY (user_id1, user_id2)
);

-- Table liked (User's liked genres)
CREATE TABLE Liked (
    user_id INTEGER REFERENCES User(user_id),
    genre_id INTEGER REFERENCES Genre(genre_id),
    PRIMARY KEY (user_id, genre_id)
);

-- Table Publisher_of_book
CREATE TABLE Publisher_of_book (
    book_id INTEGER REFERENCES Book(book_id),
    publisher_id INTEGER REFERENCES Publisher(publisher_id),
    PRIMARY KEY (book_id, publisher_id)
);

-- Table Serie_of_book
CREATE TABLE Serie_of_book (
    book_id INTEGER REFERENCES Book(book_id),
    serie_id INTEGER REFERENCES Serie(serie_id),
    PRIMARY KEY (book_id, serie_id)
);

-- Table Format_of_book
CREATE TABLE Format_of_book (
    book_id INTEGER REFERENCES Book(book_id),
    format_id INTEGER REFERENCES Book_format(format_id),
    PRIMARY KEY (book_id, format_id)
);

-- Table Award_of_book
CREATE TABLE Award_of_book (
    book_id INTEGER REFERENCES Book(book_id),
    award_id INTEGER REFERENCES Award(award_id),
    PRIMARY KEY (book_id, award_id)
);

-- Table setting_of_book
CREATE TABLE Setting_of_book (
    book_id INTEGER REFERENCES Book(book_id),
    setting_id INTEGER REFERENCES Settings(setting_id),
    PRIMARY KEY (book_id, setting_id)
);

-- Table Characters_of_book
CREATE TABLE Characters_of_book (
    book_id INTEGER REFERENCES Book(book_id),
    character_id INTEGER REFERENCES Characters(character_id),
    PRIMARY KEY (book_id, character_id)
);

-- Table User's favorite author
CREATE TABLE Favorite_author (
    user_id INTEGER REFERENCES User(user_id),
    author_id INTEGER REFERENCES Author(author_id),
    PRIMARY KEY (user_id, author_id)
);

-- Table User's preferred format of reading
CREATE TABLE Preferred_format_of_reading (
    user_id INTEGER REFERENCES User(user_id),
    format_id INTEGER REFERENCES Format_of_reading(format_reading_id),
    PRIMARY KEY (user_id, format_id)
);

-- Table User's field of reading
CREATE TABLE User_field_of_reading (
    user_id INTEGER REFERENCES User(user_id),
    field_id INTEGER REFERENCES Field_of_reading(field_id),
    PRIMARY KEY (user_id, field_id)
);


