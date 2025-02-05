CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    created INTEGER NOT NULL -- UNIX timestamp
    );

CREATE TABLE plays (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    userid INTEGER NOT NULL,
    time INTEGER NOT NULL, -- Time the user played
    timer NUMERIC NOT NULL, -- How long it took
    year INTEGER NOT NULL, -- Random year
    month INTEGER NOT NULL, -- Random month
    day INTEGER NOT NULL, -- Random day
    dayofweek INTEGER NOT NULL, -- Day of week 0 to 6
    answer INTEGER NOT NULL, -- Answer user gave 0 to 6
    correct INTEGER NOT NULL, -- 0 for False (incorrect) 1 for True (correct)

    FOREIGN KEY (userid) REFERENCES users(id)
    );