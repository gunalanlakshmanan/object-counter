-- CREATE SCHEMA
CREATE SCHEMA object_detection;

-- CREATE TABLE
CREATE TABLE IF NOT EXISTS object_detection.object_counter (
   id serial PRIMARY KEY,
   object_class text UNIQUE NOT NULL,
   count integer DEFAULT 1
);