import sqlite3
from contextlib import closing

from config import DATABASE_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS plants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    care TEXT,
    water_every_days INTEGER DEFAULT 7,
    UNIQUE(user_id, name)
);

CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plant_name TEXT NOT NULL,
    days_interval INTEGER NOT NULL,
    UNIQUE(user_id, plant_name)
);
"""

class PlantRepository:

    def __init__(self, path=DATABASE_PATH):
        self.path = path
        self._ensure_schema()

    def _conn(self):
        return sqlite3.connect(self.path, check_same_thread=False)

    def _ensure_schema(self):
        with closing(sqlite3.connect(DATABASE_PATH)) as conn:
            conn.executescript(SCHEMA)   # <-- CREA LAS TABLAS SI NO EXISTEN
            conn.commit()

    # ---------- PLANTAS ----------
    def add_or_update_plant(self, user_id, name, care=None, water_every_days=7):
        with closing(self._conn()) as conn:
            conn.execute(
                """
                INSERT INTO plants (user_id, name, care, water_every_days)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, name) DO UPDATE SET
                    care = excluded.care,
                    water_every_days = excluded.water_every_days
                """,
                (user_id, name, care, water_every_days)
            )
            conn.commit()

    def get_plants(self, user_id):
        with closing(self._conn()) as conn:
            rows = conn.execute(
                "SELECT name, care, water_every_days FROM plants WHERE user_id=?",
                (user_id,)
            ).fetchall()
            return [
                {"name": r[0], "care": r[1], "water_every_days": r[2]}
                for r in rows
            ]

    def get_plant(self, user_id, name):
        with closing(self._conn()) as conn:
            row = conn.execute(
                "SELECT name, care, water_every_days FROM plants WHERE user_id=? AND LOWER(name)=?",
                (user_id, name)
            ).fetchone()
            if not row:
                return None
            return {"name": row[0], "care": row[1], "water_every_days": row[2]}
        
    def remove_plant(self, user_id, name):
        with closing(self._conn()) as conn:
            conn.execute(
                "DELETE FROM plants WHERE user_id=? AND LOWER(name)=?",
                (user_id, name.lower())
            )
            conn.commit()


    # ---------- RECORDATORIOS ----------
    def set_reminder(self, user_id, plant_name, interval):
        with closing(self._conn()) as conn:
            conn.execute(
                """
                INSERT INTO reminders (user_id, plant_name, days_interval)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, plant_name) 
                DO UPDATE SET days_interval = excluded.days_interval;
                """,
                (user_id, plant_name, interval)
            )
            conn.commit()

    def get_reminders(self, user_id):
        with closing(self._conn()) as conn:
            rows = conn.execute(
                "SELECT plant_name, days_interval FROM reminders WHERE user_id=?",
                (user_id,)
            ).fetchall()
            return [{"plant_name": r[0], "days_interval": r[1]} for r in rows]
        

        
    def get_all_reminders(self):
        """Devuelve todos los recordatorios de todos los usuarios."""
        with closing(self._conn()) as conn:
            rows = conn.execute(
                "SELECT user_id, plant_name, days_interval FROM reminders"
            ).fetchall()

            return [
                {
                    "user_id": r[0],
                    "plant_name": r[1],
                    "days_interval": r[2]
                }
                for r in rows
            ]

    def remove_reminder(self, user_id, plant_name):
        """Elimina un reminder específico de la BD."""
        with closing(self._conn()) as conn:
            conn.execute(
                "DELETE FROM reminders WHERE user_id=? AND plant_name=?",
                (user_id, plant_name)
            )
            conn.commit()
