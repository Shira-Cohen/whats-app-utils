--in order to run this script please open cmd in postgressqlp bin folder (in windows "C:\Program Files\PostgreSQL\<postgres version>\bin" - please change postgres version) 
--run this command:
--psql -h localhost -p 5432 -U postgres -d postgres -f <script location>
--Remember to replace the placeholders (localhost, 5432, postgres, and the script location) with the appropriate values for your PostgreSQL setup.
--for example:
--psql -h localhost -p 5432 -U postgres -d postgres -f "C:\Users\user1\Documents\projects\AccountManagement\documentation\create_db_test.sql"


-- 1. Create the "whats_app" database
CREATE DATABASE whats_app;

-- 2. Connect to the "whats_app" database
\c whats_app;

-- 3. Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    display_name TEXT,
    email TEXT UNIQUE,
    google_user_id VARCHAR(255),
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Login sessions (for managing login tokens)
CREATE TABLE login_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_token TEXT UNIQUE NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expired_at TIMESTAMP
);

-- 5. Conversations (can be one-on-one or group chat)
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    is_group BOOLEAN DEFAULT FALSE,
    name TEXT, -- group name (if applicable)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Relationship table between conversations and users (many-to-many)
CREATE TABLE conversation_participants (
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (conversation_id, user_id)
);

-- 7. Messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE
);
