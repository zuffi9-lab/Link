import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash

DB_PATH = os.environ.get("DB_PATH", "/data/links.db")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "change_me")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")
SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret")
PROFILE_TITLE = os.environ.get("PROFILE_TITLE", "Мои ссылки")
PROFILE_SUBTITLE = os.environ.get("PROFILE_SUBTITLE", "Мини-LINKTREE для личного использования")

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                description TEXT,
                sort_order INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1
            )
            """
        )
        conn.commit()


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return view_func(*args, **kwargs)

    return wrapped


def verify_admin_password(password: str) -> bool:
    if ADMIN_PASSWORD_HASH:
        return check_password_hash(ADMIN_PASSWORD_HASH, password)
    return password == ADMIN_PASSWORD


@app.route("/")
def public_profile():
    with get_db() as conn:
        links = conn.execute(
            "SELECT * FROM links WHERE is_active=1 ORDER BY sort_order ASC, id DESC"
        ).fetchall()
    return render_template(
        "public.html",
        links=links,
        profile_title=PROFILE_TITLE,
        profile_subtitle=PROFILE_SUBTITLE,
    )


@app.get("/health")
def healthcheck():
    return jsonify({"status": "ok"}), 200


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == ADMIN_USERNAME and verify_admin_password(password):
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Неверный логин или пароль", "error")
    return render_template("login.html")


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("public_profile"))


@app.route("/admin")
@login_required
def admin_dashboard():
    with get_db() as conn:
        links = conn.execute("SELECT * FROM links ORDER BY sort_order ASC, id DESC").fetchall()
    return render_template("admin.html", links=links)


@app.route("/admin/links", methods=["POST"])
@login_required
def add_link():
    title = request.form.get("title", "").strip()
    url = request.form.get("url", "").strip()
    description = request.form.get("description", "").strip()
    sort_order = int(request.form.get("sort_order", 0) or 0)
    is_active = 1 if request.form.get("is_active") == "on" else 0

    if not title or not url:
        flash("Поля title и url обязательны", "error")
        return redirect(url_for("admin_dashboard"))

    with get_db() as conn:
        conn.execute(
            "INSERT INTO links (title, url, description, sort_order, is_active) VALUES (?, ?, ?, ?, ?)",
            (title, url, description, sort_order, is_active),
        )
        conn.commit()

    flash("Ссылка добавлена", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/links/<int:link_id>/update", methods=["POST"])
@login_required
def update_link(link_id: int):
    title = request.form.get("title", "").strip()
    url = request.form.get("url", "").strip()
    description = request.form.get("description", "").strip()
    sort_order = int(request.form.get("sort_order", 0) or 0)

    if not title or not url:
        flash("Поля title и url обязательны", "error")
        return redirect(url_for("admin_dashboard"))

    with get_db() as conn:
        conn.execute(
            "UPDATE links SET title = ?, url = ?, description = ?, sort_order = ? WHERE id = ?",
            (title, url, description, sort_order, link_id),
        )
        conn.commit()

    flash("Ссылка обновлена", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/links/<int:link_id>/toggle", methods=["POST"])
@login_required
def toggle_link(link_id: int):
    with get_db() as conn:
        conn.execute(
            "UPDATE links SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?",
            (link_id,),
        )
        conn.commit()
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/links/<int:link_id>/delete", methods=["POST"])
@login_required
def delete_link(link_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM links WHERE id = ?", (link_id,))
        conn.commit()
    flash("Ссылка удалена", "success")
    return redirect(url_for("admin_dashboard"))


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
