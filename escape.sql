DROP SCHEMA IF EXISTS library CASCADE;
CREATE SCHEMA library;
SET SCHEMA 'library';

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

-- Table Book
CREATE TABLE Book (
                      book_id SERIAL PRIMARY KEY,
                      title VARCHAR(255) NOT NULL,
                      publibrarycation_date DATE,
                      original_title VARCHAR(255),
                      number_of_pages INTEGER,
                      isbn VARCHAR(10),
                      isbn13 VARCHAR(13),
                      description TEXT,
                      publisher_id INTEGER REFERENCES Publisher(publisher_id)
);

CREATE INDEX idx_book_title_fulltext ON Book USING GIN (to_tsvector('french', title));
CREATE INDEX idx_book_description_fulltext ON Book USING GIN (to_tsvector('french', description));
CREATE INDEX idx_book_fulltext ON Book USING GIN (
                                                  to_tsvector('french', title || ' ' || description)
    );

-- Table Author
CREATE TABLE Author (
                        author_id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        gender VARCHAR(255) CHECK (gender IN ('male', 'female', 'other')),
                        birthplace VARCHAR(255)
);

CREATE INDEX idx_author_name_fulltext ON Author USING GIN (to_tsvector('simple', lower(name)));


-- Table User
CREATE TABLE "user" (
                        user_id SERIAL PRIMARY KEY,
                        name VARCHAR(255),
                        birth_date DATE,
                        gender VARCHAR(255) CHECK (gender IN ('male', 'female', 'other')),
                        favorite_book_id INTEGER REFERENCES Book(book_id),
                        favorite_author_id INTEGER REFERENCES Author(author_id)
);

-- Table Questionary
CREATE TABLE Questionary (
                             questionary_id SERIAL PRIMARY KEY,
                             age INTEGER,
                             child BOOLEAN,
                             familial_situation varchar,
                             gender VARCHAR(255) CHECK (gender IN ('male', 'female', 'other')),
                             socio_pro_cat varchar,
                             habitation varchar,
                             frequency varchar,
                             book_size varchar
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

-- Table User_Book_Interaction
CREATE TABLE User_Book_Interaction (
                                       interaction_id SERIAL PRIMARY KEY,
                                       user_id INTEGER REFERENCES "user"(user_id),
                                       book_id INTEGER REFERENCES Book(book_id),
                                       interaction_type VARCHAR(255),
                                       interaction_date TIMESTAMP
);

-- Table User_Book_Preference
CREATE TABLE User_Book_Preference (
                                      preference_id SERIAL PRIMARY KEY,
                                      user_id INTEGER REFERENCES "user"(user_id),
                                      genre_id INTEGER REFERENCES Genre(genre_id),
                                      preference_name VARCHAR(255),
                                      preference_date TIMESTAMP,
                                      preference_rating INTEGER
);

-- Table User_Book_History
CREATE TABLE User_Book_History (
                                   history_id SERIAL PRIMARY KEY,
                                   user_id INTEGER REFERENCES "user"(user_id),
                                   book_id INTEGER REFERENCES Book(book_id),
                                   reading_date TIMESTAMP
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
                         user_id1 INTEGER REFERENCES "user"(user_id),
                         user_id2 INTEGER REFERENCES "user"(user_id),
                         friendship_date DATE,
                         PRIMARY KEY (user_id1, user_id2)
);

-- Table Liked (User's liked genres)
CREATE TABLE Liked (
                       user_id INTEGER REFERENCES "user"(user_id),
                       genre_id INTEGER REFERENCES Genre(genre_id),
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

-- Table Setting_of_book
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

-- Table Liked_author (User's liked author)
CREATE TABLE Liked_author (
                              user_id INTEGER REFERENCES "user"(user_id),
                              author_id INTEGER REFERENCES Author(author_id),
                              PRIMARY KEY (user_id, author_id)
);

-- Table Preferred_format_of_reading (User's preferred format of reading)
CREATE TABLE Preferred_format_of_reading (
                                             user_id INTEGER REFERENCES "user"(user_id),
                                             format_id INTEGER REFERENCES Format_of_reading(format_reading_id),
                                             PRIMARY KEY (user_id, format_id)
);

-- Table User_field_of_reading (User's field of reading)
CREATE TABLE User_field_of_reading (
                                       user_id INTEGER REFERENCES "user"(user_id),
                                       field_id INTEGER REFERENCES Field_of_reading(field_id),
                                       PRIMARY KEY (user_id, field_id)
);


--Questionary relation

-- Table Favorite_book (favorite book of questionary)
CREATE TABLE Favorite_book (
                               questionary_id INTEGER REFERENCES Questionary(questionary_id),
                               book_id INTEGER REFERENCES Book(book_id),
                               PRIMARY KEY (questionary_id, book_id)
);

-- Table Likes_genre
CREATE TABLE Likes_genre (
                             questionary_id INTEGER REFERENCES Questionary(questionary_id),
                             genre_id INTEGER REFERENCES Genre(genre_id),
                             PRIMARY KEY (questionary_id, genre_id)
);

-- Table Favorite_author
CREATE TABLE Favorite_author (
                                 questionary_id INTEGER REFERENCES Questionary(questionary_id),
                                 author_id INTEGER REFERENCES Author(author_id),
                                 PRIMARY KEY (questionary_id, author_id)
);

-- Table Preferred_type_of_book
CREATE TABLE Preferred_type_of_book (
                                        questionary_id INTEGER REFERENCES Questionary(questionary_id),
                                        type_id INTEGER REFERENCES Type_book(type_id),
                                        PRIMARY KEY (questionary_id, type_id)
);

-- Table Preferred_interest
CREATE TABLE Preferred_interest (
                                    questionary_id INTEGER REFERENCES Questionary(questionary_id),
                                    interest_id INTEGER REFERENCES Interest(interest_id),
                                    PRIMARY KEY (questionary_id, interest_id)
);

-- Table Preferred_format_of_reading (questionary's preferred format of reading)
CREATE TABLE Preferred_format_of_reading_questionary (
                                                         questionary_id INTEGER REFERENCES Questionary(questionary_id),
                                                         format_id INTEGER REFERENCES Format_of_reading(format_reading_id),
                                                         PRIMARY KEY (questionary_id, format_id)
);

-- Table User_field_of_reading (questionary's field of reading)
CREATE TABLE User_field_of_reading_questionary (
                                                   questionary_id INTEGER REFERENCES Questionary(questionary_id),
                                                   field_id INTEGER REFERENCES Field_of_reading(field_id),
                                                   PRIMARY KEY (questionary_id, field_id)
);

--End questionary relations

--TRIGGERS

--triggers book rating

--to calculate book average rating
CREATE OR REPLACE FUNCTION calculate_book_average_rating() RETURNS TRIGGER AS $$
BEGIN
    NEW.rating_count := NEW.five_star_rating + NEW.four_star_rating + NEW.three_star_rating + NEW.two_star_rating + NEW.one_star_rating;

    IF NEW.rating_count > 0 THEN
        NEW.average_rating := (
            5 * NEW.five_star_rating +
            4 * NEW.four_star_rating +
            3 * NEW.three_star_rating +
            2 * NEW.two_star_rating +
            1 * NEW.one_star_rating
        ) / NEW.rating_count;
    ELSE
        NEW.average_rating := 0;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_book_average_rating
BEFORE INSERT OR UPDATE ON Rating_book
FOR EACH ROW
EXECUTE FUNCTION calculate_book_average_rating();


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


--update book rating count
CREATE OR REPLACE FUNCTION update_book_rating_count() RETURNS TRIGGER AS $$
BEGIN
    NEW.rating_count := NEW.five_star_rating + NEW.four_star_rating + NEW.three_star_rating + NEW.two_star_rating + NEW.one_star_rating;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_book_rating_count
BEFORE INSERT OR UPDATE ON Rating_book
FOR EACH ROW
EXECUTE FUNCTION update_book_rating_count();

--update book review count
CREATE OR REPLACE FUNCTION update_book_review_count() RETURNS TRIGGER AS $$
BEGIN
    NEW.book_review_count := (SELECT COUNT(*) FROM Reviews WHERE book_id = NEW.book_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_book_review_count
AFTER INSERT OR DELETE ON Rating_book
FOR EACH ROW
EXECUTE FUNCTION update_book_review_count();








--triggers author rating

--to calculate average rating
CREATE OR REPLACE FUNCTION calculate_author_average_rating() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.author_rating_count > 0 THEN
        NEW.average_author_rating := NEW.average_author_rating / NEW.author_rating_count;
    ELSE
        NEW.average_author_rating := 0;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_author_average_rating
BEFORE INSERT OR UPDATE ON Rating_author
FOR EACH ROW
EXECUTE FUNCTION calculate_author_average_rating();

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

--update author rating count
CREATE OR REPLACE FUNCTION update_author_rating_count() RETURNS TRIGGER AS $$
BEGIN
    NEW.author_rating_count := (SELECT COUNT(*) FROM Rating_author WHERE author_id = NEW.author_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER increment_author_rating_count
AFTER INSERT OR DELETE ON Rating_author
FOR EACH ROW
EXECUTE FUNCTION update_author_rating_count();



--update author review count
CREATE OR REPLACE FUNCTION update_author_review_count() RETURNS TRIGGER AS $$
BEGIN
    NEW.author_review_count := (SELECT COUNT(*) FROM Reviews WHERE author_id = NEW.author_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_author_review_count
AFTER INSERT OR DELETE ON Rating_author
FOR EACH ROW
EXECUTE FUNCTION update_author_review_count();
