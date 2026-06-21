"""
database.py — SQLite 数据库操作层（后端数据持久化）

仅使用 Python 标准库 sqlite3，零外部依赖。
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "notes.db")


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """初始化数据库表结构"""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL DEFAULT '',
                content TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMP DEFAULT (datetime('now', 'localtime'))
            )
        """)
        conn.commit()


def get_all_notes():
    """查询所有笔记，按创建时间倒序"""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, title, content, created_at FROM notes ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def title_exists(title, exclude_id=None):
    """
    检查标题是否已存在。
    exclude_id: 排除指定 id（更新时使用，不检查自身）
    返回 True/False
    """
    with get_connection() as conn:
        if exclude_id is not None:
            row = conn.execute(
                "SELECT 1 FROM notes WHERE title = ? AND id != ? LIMIT 1",
                (title, exclude_id),
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT 1 FROM notes WHERE title = ? LIMIT 1",
                (title,),
            ).fetchone()
        return row is not None


def create_note(title, content):
    """创建新笔记，返回新记录的 id"""
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO notes (title, content) VALUES (?, ?)",
            (title, content),
        )
        conn.commit()
        return cursor.lastrowid


def update_note(note_id, title, content):
    """更新笔记，返回受影响行数"""
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE notes SET title = ?, content = ? WHERE id = ?",
            (title, content, note_id),
        )
        conn.commit()
        return cursor.rowcount


def delete_note(note_id):
    """删除笔记，返回受影响行数"""
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        return cursor.rowcount
