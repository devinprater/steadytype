from sqlalchemy import inspect
from steadytype_server.config import Settings
from steadytype_server.main import create_app


def test_a_fresh_database_gets_every_table(tmp_path):
    app = create_app(Settings(database_url=f"sqlite:///{tmp_path / 'fresh.db'}", secret="t"))
    tables = set(inspect(app.state.engine).get_table_names())
    assert {"users", "classes", "enrollments", "attempts", "devices",
            "audit_log"} <= tables


def test_an_old_database_gains_the_goal_column(tmp_path):
    import sqlite3

    path = tmp_path / "old.db"
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE classes (id INTEGER PRIMARY KEY, name TEXT,"
                       " teacher_id INTEGER, created_at TEXT)")
    connection.commit()
    connection.close()
    app = create_app(Settings(database_url=f"sqlite:///{path}", secret="t"))
    columns = {c["name"] for c in inspect(app.state.engine).get_columns("classes")}
    assert "goal_minutes" in columns
