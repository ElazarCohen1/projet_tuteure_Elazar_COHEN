DROP TABLE IF EXISTS recipe_ingredient CASCADE;
DROP TABLE IF EXISTS steps CASCADE;
DROP TABLE IF EXISTS ingredients CASCADE;
DROP TABLE IF EXISTS recipe CASCADE;
DROP TABLE IF EXISTS recipe_embeddings;

CREATE TABLE recipe (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
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


CREATE TABLE steps (
    recipe_id INT REFERENCES recipe(id) ON DELETE CASCADE,
    step_number INT NOT NULL,
    instruction TEXT NOT NULL,
    PRIMARY KEY(recipe_id, step_number)
);


CREATE TABLE recipe_embeddings (
    recipe_id   INT PRIMARY KEY REFERENCES recipe(id) ON DELETE CASCADE,
    chunk_text  TEXT NOT NULL,
    embedding   vector(384),
    model_version VARCHAR(50) DEFAULT 'all-MiniLM-L6-v2'
);