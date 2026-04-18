DROP TABLE IF EXISTS recipe_ingredient CASCADE;
DROP TABLE IF EXISTS recipe_category CASCADE;
DROP TABLE IF EXISTS recipe_diet CASCADE;
DROP TABLE IF EXISTS steps CASCADE;
DROP TABLE IF EXISTS ingredients CASCADE;
DROP TABLE IF EXISTS category CASCADE;
DROP TABLE IF EXISTS diet CASCADE;
DROP TABLE IF EXISTS recipe CASCADE;
DROP TABLE IF EXISTS recipe_embeddings;

CREATE TABLE recipe (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    preparation_time INT,
    cooking_time INT,
    servings INT,
    difficulty VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ingredients (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE recipe_ingredient (
    recipe_id INT REFERENCES recipe(id) ON DELETE CASCADE,
    ingredient_id INT REFERENCES ingredients(id) ON DELETE CASCADE,
    quantity NUMERIC,
    unit VARCHAR(50),
    particularity VARCHAR,
    PRIMARY KEY (recipe_id, ingredient_id)
);

CREATE TABLE category (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE recipe_category (
    recipe_id INT REFERENCES recipe(id) ON DELETE CASCADE,
    category_id INT REFERENCES category(id) ON DELETE CASCADE,
    PRIMARY KEY (recipe_id, category_id)
);

CREATE TABLE diet (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE recipe_diet (
    recipe_id INT REFERENCES recipe(id) ON DELETE CASCADE,
    diet_id INT REFERENCES diet(id) ON DELETE CASCADE,
    PRIMARY KEY (recipe_id, diet_id)
);
    
CREATE TABLE steps (
    recipe_id INT REFERENCES recipe(id) ON DELETE CASCADE,
    step_number INT NOT NULL,
    instruction TEXT NOT NULL,
    PRIMARY KEY(recipe_id, step_number)
);


CREATE TABLE recipe_embeddings (
    recipe_id INT REFERENCES recipe(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    chunk_type VARCHAR(50) NOT NULL, 
    embedding vector(384),  
    model_version VARCHAR(50) DEFAULT 'all-MiniLM-L6-v2',
    PRIMARY KEY (recipe_id, chunk_index, chunk_type)
);