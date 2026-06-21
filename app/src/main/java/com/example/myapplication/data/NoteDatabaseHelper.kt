package com.example.myapplication.data

import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper

/**
 * SQLite 数据库帮助类 —— 处理数据库创建、升级和所有 CRUD 操作
 */
class NoteDatabaseHelper(context: Context) : SQLiteOpenHelper(
    context,
    DATABASE_NAME,
    null,
    DATABASE_VERSION
) {
    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL(
            """
            CREATE TABLE $TABLE_NOTES (
                $COL_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                $COL_TITLE TEXT NOT NULL DEFAULT '',
                $COL_CONTENT TEXT NOT NULL DEFAULT '',
                $COL_TIMESTAMP INTEGER NOT NULL
            )
            """.trimIndent()
        )
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        db.execSQL("DROP TABLE IF EXISTS $TABLE_NOTES")
        onCreate(db)
    }

    /** 插入一条笔记 */
    fun insertNote(note: Note): Long {
        val db = writableDatabase
        val values = android.content.ContentValues().apply {
            put(COL_TITLE, note.title)
            put(COL_CONTENT, note.content)
            put(COL_TIMESTAMP, note.timestamp)
        }
        return db.insert(TABLE_NOTES, null, values)
    }

    /** 更新一条笔记 */
    fun updateNote(note: Note): Int {
        val db = writableDatabase
        val values = android.content.ContentValues().apply {
            put(COL_TITLE, note.title)
            put(COL_CONTENT, note.content)
            put(COL_TIMESTAMP, note.timestamp)
        }
        return db.update(TABLE_NOTES, values, "$COL_ID = ?", arrayOf(note.id.toString()))
    }

    /** 删除一条笔记 */
    fun deleteNote(noteId: Int): Int {
        val db = writableDatabase
        return db.delete(TABLE_NOTES, "$COL_ID = ?", arrayOf(noteId.toString()))
    }

    /** 查询所有笔记，按时间倒序 */
    fun getAllNotes(): List<Note> {
        val db = readableDatabase
        val cursor = db.query(
            TABLE_NOTES, null, null, null, null, null,
            "$COL_TIMESTAMP DESC"
        )
        val notes = mutableListOf<Note>()
        cursor.use {
            while (it.moveToNext()) {
                notes.add(
                    Note(
                        id = it.getInt(it.getColumnIndexOrThrow(COL_ID)),
                        title = it.getString(it.getColumnIndexOrThrow(COL_TITLE)),
                        content = it.getString(it.getColumnIndexOrThrow(COL_CONTENT)),
                        timestamp = it.getLong(it.getColumnIndexOrThrow(COL_TIMESTAMP))
                    )
                )
            }
        }
        return notes
    }

    /** 检查标题是否已存在 */
    fun titleExists(title: String, excludeId: Int? = null): Boolean {
        val db = readableDatabase
        val selection = if (excludeId != null) {
            "$COL_TITLE = ? AND $COL_ID != ?"
        } else {
            "$COL_TITLE = ?"
        }
        val args = if (excludeId != null) {
            arrayOf(title, excludeId.toString())
        } else {
            arrayOf(title)
        }
        val cursor = db.query(TABLE_NOTES, arrayOf(COL_ID), selection, args, null, null, "1")
        return cursor.use { it.count > 0 }
    }

    companion object {
        private const val DATABASE_NAME = "notes.db"
        private const val DATABASE_VERSION = 1
        private const val TABLE_NOTES = "notes"
        private const val COL_ID = "id"
        private const val COL_TITLE = "title"
        private const val COL_CONTENT = "content"
        private const val COL_TIMESTAMP = "timestamp"
    }
}
