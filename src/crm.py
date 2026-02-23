#!/usr/bin/env python3
"""CRM System"""
import sqlite3, secrets, json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

DB_PATH = Path.home() / ".blackroad" / "crm.db"

class CRM:
    DEAL_STAGES = ["prospecting", "qualification", "proposal", "negotiation", "closed_won", "closed_lost"]
    
    def __init__(self):
        self.db_path = DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY, name TEXT, email TEXT, company TEXT, phone TEXT,
                title TEXT, tags TEXT, notes TEXT, created_at TEXT, last_contact TEXT)""")
            conn.execute("""CREATE TABLE IF NOT EXISTS deals (
                id TEXT PRIMARY KEY, name TEXT, contact_id TEXT, stage TEXT DEFAULT 'prospecting',
                value_usd REAL, probability REAL DEFAULT 0.5, close_date TEXT, owner TEXT,
                notes TEXT, created_at TEXT, FOREIGN KEY(contact_id) REFERENCES contacts(id))""")
            conn.commit()

    def add_contact(self, name: str, email: str, company: str = "") -> str:
        contact_id = secrets.token_hex(8)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""INSERT INTO contacts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (contact_id, name, email, company, "", "", json.dumps([]), "",
                 datetime.utcnow().isoformat(), None))
            conn.commit()
        return contact_id

    def get_pipeline(self, owner: Optional[str] = None) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""SELECT stage, COUNT(*), SUM(value_usd) FROM deals GROUP BY stage""").fetchall()
        return {stage: {"count": count, "value_usd": total or 0} for stage, count, total in rows}

if __name__ == '__main__':
    crm = CRM()
    print("CRM initialized")
