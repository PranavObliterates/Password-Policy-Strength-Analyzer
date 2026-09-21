import sqlite3
import datetime
import json
import time

DB_FILE = 'audit_logs.db'

def get_connection():
    return sqlite3.connect(DB_FILE, timeout=10.0)

def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                audit_type TEXT,
                result_json TEXT
            )
        ''')
        conn.commit()
    except Exception as e:
        print(f"Database init error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def log_audit(audit_type, result):
    for attempt in range(3):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO audit_logs (timestamp, audit_type, result_json)
                VALUES (?, ?, ?)
            ''', (datetime.datetime.now(), audit_type, json.dumps(result)))
            conn.commit()
            break
        except sqlite3.OperationalError as e:
            if 'locked' in str(e).lower() and attempt < 2:
                time.sleep(0.5)
                continue
            print(f"Database log error: {e}")
            break
        except Exception as e:
            print(f"Database log error: {e}")
            break
        finally:
            if 'conn' in locals() and conn:
                try:
                    conn.close()
                except Exception:
                    pass

def get_all_logs():
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM audit_logs ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Database read error: {e}")
        return []
    finally:
        if 'conn' in locals() and conn:
            conn.close()
