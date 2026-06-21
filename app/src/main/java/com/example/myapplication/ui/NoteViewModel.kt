package com.example.myapplication.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.myapplication.data.Note
import com.example.myapplication.data.NoteDatabaseHelper
import com.example.myapplication.data.NoteRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * 笔记 ViewModel —— 作为后端层与 UI 层的桥梁
 * 管理笔记数据的状态，供 UI 层观察和操作
 */
class NoteViewModel(application: Application) : AndroidViewModel(application) {

    private val repository: NoteRepository

    private val _notes = MutableStateFlow<List<Note>>(emptyList())
    val notes: StateFlow<List<Note>> = _notes

    init {
        val dbHelper = NoteDatabaseHelper(application)
        repository = NoteRepository(dbHelper)
        refreshNotes()
    }

    /** 刷新笔记列表 */
    fun refreshNotes() {
        viewModelScope.launch {
            val list = withContext(Dispatchers.IO) {
                repository.getAllNotes()
            }
            _notes.value = list
        }
    }

    /** 检查标题是否重复，返回 null 表示可用，否则返回错误信息 */
    suspend fun checkTitleDuplicate(title: String, excludeId: Int? = null): String? {
        if (title.isBlank()) return null
        return withContext(Dispatchers.IO) {
            if (repository.titleExists(title, excludeId)) {
                if (excludeId != null) "标题「${title}」已被其他笔记使用"
                else "标题「${title}」已存在"
            } else null
        }
    }

    /** 添加笔记 */
    fun insert(note: Note) {
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                repository.insert(note)
            }
            refreshNotes()
        }
    }

    /** 更新笔记 */
    fun update(note: Note) {
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                repository.update(note)
            }
            refreshNotes()
        }
    }

    /** 删除笔记 */
    fun delete(noteId: Int) {
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                repository.delete(noteId)
            }
            refreshNotes()
        }
    }
}
