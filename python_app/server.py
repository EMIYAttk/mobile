"""
server.py — HTTP API 服务器（后端）

使用 Python 标准库 http.server 提供 RESTful API。
零外部依赖，启动即可访问 http://localhost:8000
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from database import init_db, get_all_notes, create_note, update_note, delete_note, title_exists

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
PORT = 8000


class NoteAPIHandler(BaseHTTPRequestHandler):
    """处理 HTTP 请求的路由分发"""

    def _send_json(self, data, status=200):
        """发送 JSON 响应"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _send_html(self, content, status=200):
        """发送 HTML 响应"""
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def _send_error(self, message, status=400):
        """发送错误响应"""
        self._send_json({"error": message}, status)

    def _read_body(self):
        """读取请求体中的 JSON 数据"""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def _parse_path(self):
        """解析 URL 路径"""
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        return path, parse_qs(parsed.query)

    # ---- 路由分发 ----

    def do_GET(self):
        path, _ = self._parse_path()
        if path == "/api/notes":
            self._handle_list_notes()
        elif path == "/" or path == "":
            self._serve_static("index.html")
        else:
            # 尝试提供静态文件
            self._serve_static(path.lstrip("/"))

    def do_POST(self):
        path, _ = self._parse_path()
        if path == "/api/notes":
            self._handle_create_note()
        else:
            self._send_error("Not Found", 404)

    def do_PUT(self):
        path, _ = self._parse_path()
        parts = path.split("/")
        if len(parts) == 4 and parts[1] == "api" and parts[2] == "notes":
            try:
                note_id = int(parts[3])
                self._handle_update_note(note_id)
            except ValueError:
                self._send_error("Invalid note ID")
        else:
            self._send_error("Not Found", 404)

    def do_DELETE(self):
        path, _ = self._parse_path()
        parts = path.split("/")
        if len(parts) == 4 and parts[1] == "api" and parts[2] == "notes":
            try:
                note_id = int(parts[3])
                self._handle_delete_note(note_id)
            except ValueError:
                self._send_error("Invalid note ID")
        else:
            self._send_error("Not Found", 404)

    def do_OPTIONS(self):
        """处理 CORS 预检请求"""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ---- 业务处理 ----

    def _handle_list_notes(self):
        notes = get_all_notes()
        self._send_json(notes)

    def _handle_create_note(self):
        body = self._read_body()
        title = body.get("title", "").strip()
        content = body.get("content", "").strip()
        if not title and not content:
            self._send_error("标题和内容不能同时为空")
            return
        if title and title_exists(title):
            self._send_error(f"标题「{title}」已存在，请使用其他标题")
            return
        note_id = create_note(title, content)
        self._send_json({"id": note_id, "message": "创建成功"}, 201)

    def _handle_update_note(self, note_id):
        body = self._read_body()
        title = body.get("title", "").strip()
        content = body.get("content", "").strip()
        if title and title_exists(title, exclude_id=note_id):
            self._send_error(f"标题「{title}」已被其他笔记使用，请使用其他标题")
            return
        rows = update_note(note_id, title, content)
        if rows == 0:
            self._send_error("笔记不存在", 404)
        else:
            self._send_json({"message": "更新成功"})

    def _handle_delete_note(self, note_id):
        rows = delete_note(note_id)
        if rows == 0:
            self._send_error("笔记不存在", 404)
        else:
            self._send_json({"message": "删除成功"})

    def _serve_static(self, filename):
        """提供静态文件服务"""
        # 将 index.html 从 static 目录移动到根目录
        filepath = os.path.join(os.path.dirname(__file__), filename)
        if not os.path.exists(filepath):
            self._send_error("File Not Found", 404)
            return
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        self._send_html(content)

    def log_message(self, format, *args):
        """自定义日志输出"""
        sys.stderr.write(f"[API] {args[0]} {args[1]} {args[2]}\n")


def main():
    init_db()
    server = HTTPServer(("0.0.0.0", PORT), NoteAPIHandler)
    print(f"✓ 笔记应用已启动！")
    print(f"  访问地址: http://localhost:{PORT}")
    print(f"  按 Ctrl+C 停止服务器")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        server.server_close()


if __name__ == "__main__":
    main()
