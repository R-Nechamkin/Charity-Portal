--
-- File generated with SQLiteStudio v3.4.4 on Tue Apr 16 14:51:16 2024
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: Application
CREATE TABLE IF NOT EXISTS Application (application_id INTEGER PRIMARY KEY, paid boolean DEFAULT (FALSE), money_granted REAL, row_number INTEGER NOT NULL, sheet_id INTEGER REFERENCES Spreadsheet (sheet_id) NOT NULL);

-- Table: Spreadsheet
CREATE TABLE IF NOT EXISTS Spreadsheet(
    sheet_id INTEGER PRIMARY KEY ,
    url text NOT NULL
);
INSERT INTO Spreadsheet (sheet_id, url) VALUES (1, 'https://docs.google.com/spreadsheets/d/18szop7TqllS9pBAyCXZn7LRIvJbPRaw9-MDVcogLh1E');

-- Table: User
CREATE TABLE IF NOT EXISTS User (user_id INTEGER PRIMARY KEY, username TEXT NOT NULL, password text NOT NULL, sheet_id INTEGER REFERENCES Spreadsheet NOT NULL);
INSERT INTO User (user_id, username, password, sheet_id) VALUES (1, 'John Doe', 'secret', 1);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
