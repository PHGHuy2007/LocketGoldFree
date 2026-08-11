import os
import sqlite3
import threading
from datetime import datetime, timezone

import requests


class HistoryStore:
    PLACEHOLDER_VALUES = {
        "xxxx",
        "your_service_role_key",
        "your-project",
        "https://xxxx.supabase.co",
        "https://your-project.supabase.co",
    }

    def __init__(self):
        self.supabase_url = (os.getenv("SUPABASE_URL") or "").rstrip("/")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv(
            "SUPABASE_ANON_KEY"
        )
        default_sqlite_path = "/tmp/history.db" if os.getenv("VERCEL") else "history.db"
        self.sqlite_path = os.getenv("HISTORY_DB_PATH", default_sqlite_path)
        self.lock = threading.Lock()

        if self._use_supabase:
            print("History store initialized with Supabase")
        else:
            self._init_sqlite()
            print(f"History store initialized with SQLite: {self.sqlite_path}")

    @property
    def _use_supabase(self):
        if not (self.supabase_url and self.supabase_key):
            return False

        normalized_url = self.supabase_url.lower()
        normalized_key = self.supabase_key.strip().lower()
        if normalized_url in self.PLACEHOLDER_VALUES:
            return False
        if normalized_key in self.PLACEHOLDER_VALUES:
            return False
        if "xxxx" in normalized_url or "your-project" in normalized_url:
            return False

        return True

    def create_request(self, client_id, username):
        now = self._now()
        row = {
            "client_id": client_id,
            "username": username,
            "status": "waiting",
            "message": "Dang cho xu ly",
            "uid": None,
            "product_id": None,
            "created_at": now,
            "updated_at": now,
            "completed_at": None,
        }
        if self._use_supabase:
            self._supabase_request("POST", "/request_history", json=row)
            return

        with self.lock, sqlite3.connect(self.sqlite_path) as conn:
            conn.execute(
                """
                INSERT INTO request_history (
                    client_id, username, status, message, uid, product_id,
                    created_at, updated_at, completed_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["client_id"],
                    row["username"],
                    row["status"],
                    row["message"],
                    row["uid"],
                    row["product_id"],
                    row["created_at"],
                    row["updated_at"],
                    row["completed_at"],
                ),
            )

    def update_request(self, client_id, status, message=None, uid=None, product_id=None):
        now = self._now()
        completed_at = now if status in ("completed", "error") else None
        payload = {"status": status, "updated_at": now}
        if message is not None:
            payload["message"] = message
        if uid is not None:
            payload["uid"] = uid
        if product_id is not None:
            payload["product_id"] = product_id
        if completed_at is not None:
            payload["completed_at"] = completed_at

        if self._use_supabase:
            self._supabase_request(
                "PATCH",
                f"/request_history?client_id=eq.{client_id}",
                json=payload,
            )
            return

        fields = ["status = ?", "updated_at = ?"]
        values = [status, now]
        if message is not None:
            fields.append("message = ?")
            values.append(message)
        if uid is not None:
            fields.append("uid = ?")
            values.append(uid)
        if product_id is not None:
            fields.append("product_id = ?")
            values.append(product_id)
        if completed_at is not None:
            fields.append("completed_at = ?")
            values.append(completed_at)
        values.append(client_id)

        with self.lock, sqlite3.connect(self.sqlite_path) as conn:
            conn.execute(
                f"UPDATE request_history SET {', '.join(fields)} WHERE client_id = ?",
                values,
            )

    def recent(self, limit=20):
        limit = max(1, min(int(limit or 20), 100))
        if self._use_supabase:
            params = (
                "select=client_id,username,status,message,uid,product_id,"
                f"created_at,updated_at,completed_at&order=created_at.desc&limit={limit}"
            )
            return self._supabase_request("GET", f"/request_history?{params}")

        with self.lock, sqlite3.connect(self.sqlite_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT client_id, username, status, message, uid, product_id,
                       created_at, updated_at, completed_at
                FROM request_history
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]

    def _init_sqlite(self):
        db_dir = os.path.dirname(os.path.abspath(self.sqlite_path))
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        with self.lock, sqlite3.connect(self.sqlite_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS request_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT NOT NULL UNIQUE,
                    username TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT,
                    uid TEXT,
                    product_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_request_history_created_at
                ON request_history (created_at DESC)
                """
            )

    def _supabase_request(self, method, path, json=None):
        url = f"{self.supabase_url}/rest/v1{path}"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
        }
        if method in ("POST", "PATCH"):
            headers["Prefer"] = "return=minimal"

        response = requests.request(method, url, headers=headers, json=json, timeout=10)
        response.raise_for_status()
        if response.content:
            return response.json()
        return []

    @staticmethod
    def _now():
        return datetime.now(timezone.utc).isoformat()
