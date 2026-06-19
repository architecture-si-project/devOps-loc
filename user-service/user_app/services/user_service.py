from .auth_service import get_connection


def get_all_users():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name, email FROM users")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [{"id": r[0], "name": r[1], "email": r[2]} for r in rows]


def get_user_by_id(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return None

    return {"id": row[0], "name": row[1], "email": row[2]}


def update_user(user_id, name, email):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET name = %s, email = %s WHERE id = %s RETURNING id, name, email",
        (name, email, user_id),
    )

    row = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()

    if not row:
        return None

    return {"id": row[0], "name": row[1], "email": row[2]}


def delete_user(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM users WHERE id = %s RETURNING id", (user_id,))
    row = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()

    return row is not None


def update_user_role(user_id, role):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE users SET role = %s WHERE id = %s RETURNING id, name, email, role",
        (role, user_id),
    )

    row = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()

    if not row:
        return None

    return {"id": row[0], "name": row[1], "email": row[2], "role": row[3]}
