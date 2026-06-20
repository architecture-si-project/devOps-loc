import os

import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

RESERVATION_NOT_FOUND = "Reservation not found"


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def create_reservation(user_id, housing_name, check_in, check_out):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO reservations (user_id, housing_name, check_in, check_out) VALUES (%s, %s, %s, %s) RETURNING id, user_id, housing_name, check_in, check_out, status",
        (user_id, housing_name, check_in, check_out),
    )

    row = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()

    return _row_to_dict(row)


def get_reservations_by_user(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, user_id, housing_name, check_in, check_out, status FROM reservations WHERE user_id = %s",
        (user_id,),
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [_row_to_dict(r) for r in rows]


def get_reservation_by_id(reservation_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, user_id, housing_name, check_in, check_out, status FROM reservations WHERE id = %s",
        (reservation_id,),
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return None

    return _row_to_dict(row)


def cancel_reservation(reservation_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE reservations SET status = 'cancelled' WHERE id = %s AND status = 'confirmed' RETURNING id",
        (reservation_id,),
    )

    row = cur.fetchone()
    conn.commit()

    cur.close()
    conn.close()

    return row is not None


def _row_to_dict(row):
    return {
        "id": row[0],
        "user_id": row[1],
        "housing_name": row[2],
        "check_in": str(row[3]),
        "check_out": str(row[4]),
        "status": row[5],
    }
