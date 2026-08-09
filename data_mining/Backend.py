import string
import json
import sqlite3

class Backend:
    def __init__(self, name: str) -> None:
        self.dbFile = f"{name}.db"
        self.conn = sqlite3.connect(self.dbFile)
        self.cursor = conn.cursor()

    def closeConnection(self) -> None:
        conn.close()




# Below is sample sqlite backend (use for reference), this was from google AI
# 1. Connect to the local file (it will be created automatically if it doesn't exist)
DB_FILE = "local_nested_store.db"
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# 2. Optimize SQLite performance for local disk operations
cursor.execute("PRAGMA journal_mode = WAL;")  # Fast concurrent reads/writes
cursor.execute("PRAGMA synchronous = NORMAL;")  # Balances safety and speed

# 3. Create the row-oriented, nested table layout
cursor.execute("""
    CREATE TABLE IF NOT EXISTS data_store (
        id TEXT PRIMARY KEY,
        nested_data BLOB
    ) WITHOUT ROWID;
""")
conn.commit()

# --- INSERTING DATA ---
# Mock nested data payload
user_payload = {
    "name": "Alice Smith",
    "account": {
        "tier": "premium",
        "tags": ["admin", "developer"]
    },
    "location": {
        "city": "Vancouver",
        "country": "Canada"
    }
}

# Convert Python dict to JSON string
json_string = json.dumps(user_payload)

# Insert using the native engine side jsonb() conversion
cursor.execute("""
    INSERT OR REPLACE INTO data_store (id, nested_data)
    VALUES (?, jsonb(?));
""", ("user_101", json_string))
conn.commit()


# --- RETRIEVING DATA ---

# Strategy A: Retrieve the ENTIRE nested row quickly
cursor.execute("SELECT json(nested_data) FROM data_store WHERE id = ?;", ("user_101",))
row_result = cursor.fetchone()

if row_result:
    # Convert the returned JSON string back into a native Python dict
    full_dict = json.loads(row_result[0])
    print("Full Row Retrieved Successfully:")
    print(f"Name: {full_dict['name']}, Tier: {full_dict['account']['tier']}\n")


# Strategy B: Extract only a SPECIFIC nested value without parsing the whole row
cursor.execute("""
    SELECT json_extract(nested_data, '$.location.city')
    FROM data_store
    WHERE id = ?;
""", ("user_101",))
nested_result = cursor.fetchone()

if nested_result:
    print(f"Extracted Nested Value: {nested_result[0]}")

# Clean up connection
conn.close()
