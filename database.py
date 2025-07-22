import sqlite3

conn = sqlite3.connect("conversations.db", check_same_thread=False)
c = conn.cursor()

# Create Users Table
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    phone TEXT,
    address TEXT,
    password TEXT
)
""")

# Create Conversations Table
c.execute("""
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message TEXT,
    sender TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

# USER FUNCTIONS
def create_user(name, email, phone, address, password):
    c.execute("INSERT INTO users (name, email, phone, address, password) VALUES (?, ?, ?, ?, ?)",
              (name, email, phone, address, password))
    conn.commit()
    return {"message": "User created"}

def get_user_by_email(email):
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    return c.fetchone()

# CONVERSATION FUNCTION
def save_conversation(user_id, message, sender):
    c.execute("INSERT INTO conversations (user_id, message, sender) VALUES (?, ?, ?)",
              (user_id, message, sender))
    conn.commit()
