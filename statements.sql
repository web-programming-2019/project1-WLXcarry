CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    role_id INTEGER NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles (role_id)
);

CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role VARCHAR(16) NOT NULL UNIQUE
)

CREATE TABLE books (
    ISBN_number VARCHAR PRIMARY KEY NOT NULL,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    publication_year INTEGER NOT NULL
);


CREATE TABLE addresses (
    user_id SERIAL PRIMARY KEY,
    address1  VARCHAR(120) NOT NULL,
    address2  VARCHAR(120),
    country VARCHAR NOT NULL,
    state VARCHAR NOT NULL,
    postal_code VARCHAR(16) NOT NULL
);

-- Table --
CREATE TABLE reviews (
    user_id INTEGER UNIQUE NOT NULL,
    ISBN_number VARCHAR NOT NULL, 
    score FLOAT NOT NULL,
    description VARCHAR(280) NOT NULL,
    CHECK (score <= 5),
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (ISBN_number) REFERENCES books (ISBN_number)
);



/*  Use this statement for the api Get reviews */
SELECT title, author, publication_year, reviews.isbn_number, COUNT(reviews.isbn_number),
AVG(score) FROM books INNER JOIN reviews ON books.ISBN_number = reviews.ISBN_number 
WHERE books.isbn_number = '0778313468' GROUP BY reviews.isbn_number, publication_year, title, author;

INSERT INTO reviews (user_id, ISBN_number, score, description) VALUES (4, '0778313468', 2.5, 'Cualquier Vaina')

