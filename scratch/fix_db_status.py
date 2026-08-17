import sqlite3

def fix_db():
    conn = sqlite3.connect("knowledge_assistant.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE documents SET status = 'SUCCESS', num_chunks = 3")
    conn.commit()
    print("Updated rows:", cursor.rowcount)
    conn.close()

if __name__ == "__main__":
    fix_db()
