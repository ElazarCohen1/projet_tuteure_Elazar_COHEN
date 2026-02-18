DROP TABLE IF EXISTS recipe ON DELETE CASCADE ;
DROP TABLE IF EXISTS ingredient ON DELETE CASCADE ;
DROP TABLE IF EXISTS recipe_ingredient ON DELETE CASCADE ;
DROP TABLE IF EXISTS category ON DELETE CASCADE ;
DROP TABLE IF EXISTS recipe_category ON DELETE CASCADE ;
DROP TABLE IF EXISTS diet ON DELETE CASCADE ;
DROP TABLE IF EXISTS recipe_diet ON DELETE CASCADE ;
DROP TABLE IF EXISTS  step ON DELETE CASCADE ;
DROP TABLE IF EXISTS regime ON DELETE CASCADE ;


CREATE TABLE recipe (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    instructions TEXT,
    preparation_time INT,
    cooking_time INT,
    servings INT, 
    difficulty VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ingredient (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);


CREATE TABLE recipe_ingredient (
    recipe_id INT REFERENCES recipe(id) ON DELETE CASCADE,
    ingredient_id INT REFERENCES ingredient(id),
    quantity NUMERIC,
    unit VARCHAR(50),
    PRIMARY KEY (recipe_id, ingredient_id)
);

CREATE TABLE category (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE recipe_category (
    recipe_id INT REFERENCES recipe(id) ON DELETE CASCADE,
    category_id INT REFERENCES category(id),
    PRIMARY KEY (recipe_id, category_id)
);

CREATE TABLE diet (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE recipe_diet (
    recipe_id INT REFERENCES recipe(id) ON DELETE CASCADE,
    diet_id INT REFERENCES diet(id),
    PRIMARY KEY (recipe_id, diet_id)
);

CREATE TABLE step (
    id SERIAL PRIMARY KEY,
    recipe_id INT REFERENCES recipe(id) ON DELETE CASCADE,
    step_number INT NOT NULL,
    instruction TEXT NOT NULL
);