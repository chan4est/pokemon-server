CREATE TYPE gender AS ENUM ('male', 'female', 'genderless');

CREATE TYPE region AS ENUM ('kanto', 'johto', 'hoenn', 'sinnoh', 'unova', 'kalos', 'alola', 'galar', 'hisui', 'paldea', 'unknown');


CREATE TABLE pokemon (
  id integer NOT NULL PRIMARY KEY,
  nat_dex_number integer NOT NULL,
  name text NOT NULL,
  form_id integer,
  family_id integer NOT NULL,
  UNIQUE (nat_dex_number, form_id)
);

CREATE TABLE form (
  id integer NOT NULL PRIMARY KEY,
  name text UNIQUE NOT NULL,
  gender gender,
  region region
);

CREATE TABLE line (
  id integer NOT NULL PRIMARY KEY,
  name text UNIQUE NOT NULL,
  has_mega boolean NOT NULL DEFAULT FALSE
);

CREATE TABLE collection (
  id bigint NOT NULL PRIMARY KEY,
  name text NOT NULL
);


CREATE TABLE collection_entries (
  id bigint NOT NULL PRIMARY KEY,
  collection_id bigint NOT NULL REFERENCES collection(id) ON DELETE CASCADE,
  pokemon_id integer NOT NULL,
  preferred_gender gender,
  is_caught boolean NOT NULL DEFAULT FALSE,
  is_mega_hundo_caught boolean NOT NULL DEFAULT FALSE,
  UNIQUE(collection_id, pokemon_id)
);

ALTER TABLE pokemon
ADD CONSTRAINT pokemon_form_id_fk
FOREIGN KEY (form_id) REFERENCES form(id);

ALTER TABLE pokemon
ADD CONSTRAINT pokemon_family_id_fk
FOREIGN KEY (family_id) REFERENCES line (id);

ALTER TABLE collection_entries
ADD CONSTRAINT collection_entries_collection_id_fk
FOREIGN KEY (collection_id) REFERENCES collection (id);

ALTER TABLE collection_entries
ADD CONSTRAINT collection_entries_pokemon_id_fk
FOREIGN KEY (pokemon_id) REFERENCES pokemon (id);