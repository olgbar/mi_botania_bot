import sqlite3
from contextlib import contextmanager, closing

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

CREATE TABLE IF NOT EXISTS user_context (
    user_id INTEGER PRIMARY KEY,
    last_plant TEXT
);

"""

class PlantRepository:

    def __init__(self, path=DATABASE_PATH):
        self.path = path
        self._ensure_schema()

    @contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self.path, check_same_thread=False)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _ensure_schema(self):
        with self._get_conn() as conn:
            conn.executescript(SCHEMA)

    # ---------- PLANTAS ----------
 
    def add_or_update_plant(self, user_id, name, care=None, water_every_days=7):
        with self._get_conn() as conn:
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
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT name, care, water_every_days FROM plants WHERE user_id=?",
                (user_id,)
            ).fetchall()
            return [
                {"name": r[0], "care": r[1], "water_every_days": r[2]}
                for r in rows
            ]


    def get_plant(self, user_id, name):
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT name, care, water_every_days FROM plants WHERE user_id=? AND LOWER(name)=?",
                (user_id, name)
            ).fetchone()
            if not row:
                return None
            return {"name": row[0], "care": row[1], "water_every_days": row[2]}
        
    def remove_plant(self, user_id, name):
        with self._get_conn() as conn:
            conn.execute(
                "DELETE FROM plants WHERE user_id=? AND LOWER(name)=?",
                (user_id, name.lower())
            )
            conn.commit()


    # ---------- RECORDATORIOS ----------
    def set_reminder(self, user_id, plant_name, interval):
        with self._get_conn() as conn:
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
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT plant_name, days_interval FROM reminders WHERE user_id=?",
                (user_id,)
            ).fetchall()
            return [{"plant_name": r[0], "days_interval": r[1]} for r in rows]
        

        
    def get_all_reminders(self):
        """Devuelve todos los recordatorios de todos los usuarios."""
        with self._get_conn() as conn:
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
        with self._get_conn() as conn:
            conn.execute(
                "DELETE FROM reminders WHERE user_id=? AND LOWER(plant_name)=?",
                (user_id, plant_name)
            )
            conn.commit()


# --------------------memoria -----------------------


    def set_last_plant(self, user_id, plant_name):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO user_context (user_id, last_plant)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET last_plant=excluded.last_plant;
            """, (user_id, plant_name))
            conn.commit()

    def get_last_plant(self, user_id):
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT last_plant FROM user_context WHERE user_id=?",
                (user_id,)
            ).fetchone()
            return row[0] if row else None

