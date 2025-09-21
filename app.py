import json
import os
import pathlib
import time
from typing import Dict, List, Optional
from uuid import uuid4

from flask import Flask, redirect, render_template, request, url_for, abort, jsonify

BASE_DIR = pathlib.Path(__file__).parent
STATE_DIR = BASE_DIR / "state"
STATE_FILE = STATE_DIR / "todos.json"

app = Flask(__name__)


def _load_todos() -> List[Dict]:
    if not STATE_FILE.exists():
        return []
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        return []


def _save_todos(todos: List[Dict]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


def _find_index_by_id(todos: List[Dict], todo_id: str) -> Optional[int]:
    for i, t in enumerate(todos):
        if t.get("id") == todo_id:
            return i
    return None


@app.get("/")
def index():
    todos = _load_todos()
    # sort by created_at ascending, then not done first
    todos.sort(key=lambda t: (t.get("done", False), t.get("created_at", 0)))
    return render_template("index.html", todos=todos)


@app.post("/add")
def add():
    title = request.form.get("title", "").strip()
    if not title:
        return redirect(url_for("index"))
    todos = _load_todos()
    todo = {
        "id": uuid4().hex,
        "title": title,
        "done": False,
        "created_at": int(time.time()),
    }
    todos.append(todo)
    _save_todos(todos)
    return redirect(url_for("index"))


@app.post("/toggle/<todo_id>")
def toggle(todo_id: str):
    todos = _load_todos()
    idx = _find_index_by_id(todos, todo_id)
    if idx is None:
        abort(404)
    todos[idx]["done"] = not todos[idx].get("done", False)
    _save_todos(todos)
    return redirect(url_for("index"))


@app.post("/delete/<todo_id>")
def delete(todo_id: str):
    todos = _load_todos()
    before = len(todos)
    todos = [t for t in todos if t.get("id") != todo_id]
    if len(todos) == before:
        abort(404)
    _save_todos(todos)
    return redirect(url_for("index"))


@app.post("/edit/<todo_id>")
def edit(todo_id: str):
    new_title = request.form.get("title", "").strip()
    if not new_title:
        return redirect(url_for("index"))
    todos = _load_todos()
    idx = _find_index_by_id(todos, todo_id)
    if idx is None:
        abort(404)
    todos[idx]["title"] = new_title
    _save_todos(todos)
    return redirect(url_for("index"))


# Minimal JSON API for potential frontend use
@app.get("/api/todos")
def api_list():
    return jsonify(_load_todos())


@app.post("/api/todos")
def api_add():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    if not title:
        return jsonify({"error": "title is required"}), 400
    todos = _load_todos()
    todo = {
        "id": uuid4().hex,
        "title": title,
        "done": False,
        "created_at": int(time.time()),
    }
    todos.append(todo)
    _save_todos(todos)
    return jsonify(todo), 201


@app.post("/api/todos/<todo_id>/toggle")
def api_toggle(todo_id: str):
    todos = _load_todos()
    idx = _find_index_by_id(todos, todo_id)
    if idx is None:
        return jsonify({"error": "not found"}), 404
    todos[idx]["done"] = not todos[idx].get("done", False)
    _save_todos(todos)
    return jsonify(todos[idx])


@app.delete("/api/todos/<todo_id>")
def api_delete(todo_id: str):
    todos = _load_todos()
    before = len(todos)
    todos = [t for t in todos if t.get("id") != todo_id]
    if len(todos) == before:
        return jsonify({"error": "not found"}), 404
    _save_todos(todos)
    return "", 204


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True)