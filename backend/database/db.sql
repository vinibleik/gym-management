CREATE TABLE user_account (
    id INTEGER NOT NULL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    date_of_birth DATE NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('staff', 'personal', 'student'))
);
