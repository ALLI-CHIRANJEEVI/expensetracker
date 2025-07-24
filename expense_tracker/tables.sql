CREATE DATABASE expense_tracker;

USE expense_tracker;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    food_expenses DECIMAL(10,2) NOT NULL,
    travel_expenses DECIMAL(10,2) NOT NULL,
    accommodation DECIMAL(10,2) NOT NULL,
    other_expenses DECIMAL(10,2) NOT NULL,
    date DATE NOT NULL,
    savings DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

