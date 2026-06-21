package com.example.myapplication.data

/**
 * 笔记仓库 —— 作为数据层（后端）的入口
 * 上层（ViewModel）通过此类访问数据库，不直接操作 SQLite
 */
class NoteRepository(private val dbHelper: NoteDatabaseHelper) {

    /** 获取所有笔记 */
    fun getAllNotes(): List<Note> = dbHelper.getAllNotes()

    /** 检查标题是否已存在 */
    fun titleExists(title: String, excludeId: Int? = null): Boolean =
        dbHelper.titleExists(title, excludeId)

    /** 插入笔记 */
    fun insert(note: Note): Long = dbHelper.insertNote(note)

    /** 更新笔记 */
    fun update(note: Note): Int = dbHelper.updateNote(note)

    /** 删除笔记 */
    fun delete(noteId: Int): Int = dbHelper.deleteNote(noteId)
}
