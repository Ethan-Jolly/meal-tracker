from collections import defaultdict
from pathlib import Path
import sqlite3
import uuid
from datetime import datetime, date

import streamlit as st
import altair as alt
import pandas as pd

def connect_db():
    """Connects to the sqlite database."""

    DB_FILENAME = Path(__file__).parent / "meal_tracker.db"
    db_already_exists = DB_FILENAME.exists()

    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists

    return conn, db_was_just_created


def initialize_data(conn):
    """Initializes the inventory table with some data."""
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS meals (
            meal_id TEXT PRIMARY KEY,
            meal_name TEXT NOT NULL,
            description TEXT,
            updated_by TEXT,
            updated_at DATETIME
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ingredients (
            ingredient_id TEXT PRIMARY KEY,
            meal_id TEXT,
            ingredient_name,
            quantity REAL,
            unit TEXT,
            updated_by TEXT,
            updated_At DATETIME
        );
        """
    )


    cursor.execute(
        f"""
        INSERT INTO meals
            (meal_id, meal_name, description, updated_by, updated_at)
        VALUES
            -- Beverages
            ('{str(uuid.uuid4())}','Ethans Hello Fresh', 'Ethans asian spicy beef and rice meal from hello fresh.','{st.session_state["user"]}','{datetime.now()}'),
            ('{str(uuid.uuid4())}','Yukgaejang','','{st.session_state["user"]}','{datetime.now()}'),
            ('{str(uuid.uuid4())}','Steak','Delicious Steak with either potato wedges or rice and asparagus','{st.session_state["user"]}','{datetime.now()}')
        ;
        """
    )

    conn.commit()
    conn.close()


def run_sql_query(query):
    conn, db_was_just_created = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(f"{query}")
        data = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]

        df = pd.DataFrame(data, columns=column_names)
        conn.close()
        return df
    except Exception as e:
        print(f"Error loading meals: {e}")
        return None  

def load_meals(conn):
    """Loads the inventory data from the database."""
    conn, db_was_just_created = connect_db()
    cursor = conn.cursor()

    try:
        # Execute the query
        cursor.execute("SELECT * FROM meals;")
        data = cursor.fetchall()

        # Get column names from cursor.description
        column_names = [description[0] for description in cursor.description]

        # Create DataFrame with data and column names
        df = pd.DataFrame(data, columns=column_names)
        conn.close()
    except Exception as e:
        print(f"Error loading meals: {e}")
        return None

    return df

def insert_meals(df):
    conn, db_was_just_created = connect_db()
    

    cursor = conn.cursor()

    df["updated_at"] = pd.to_datetime(df["updated_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    rows = df.to_dict(orient="records")

    cursor.executemany(
            """
            INSERT INTO meals
                (meal_id, meal_name, description, updated_by, updated_at)
            VALUES
                (:meal_id, :meal_name, :description, :updated_by, :updated_at)
            """,
            rows,
        )
    
    conn.commit()
    conn.close()


def delete_meal(meal_id):
    conn, db_was_just_created = connect_db()

    cursor = conn.cursor()


    cursor.execute(
            f"DELETE FROM meals WHERE meal_id == '{meal_id}'",
        )

    conn.commit()
    conn.close()


def update_data(conn, df, changes):
    """Updates the inventory data in the database."""
    cursor = conn.cursor()

    if changes["edited_rows"]:
        deltas = st.session_state.inventory_table["edited_rows"]
        rows = []

        for i, delta in deltas.items():
            row_dict = df.iloc[i].to_dict()
            row_dict.update(delta)
            rows.append(row_dict)

        cursor.executemany(
            """
            UPDATE inventory
            SET
                item_name = :item_name,
                price = :price,
                units_sold = :units_sold,
                units_left = :units_left,
                cost_price = :cost_price,
                reorder_point = :reorder_point,
                description = :description
            WHERE id = :id
            """,
            rows,
        )

    if changes["added_rows"]:
        cursor.executemany(
            """
            INSERT INTO inventory
                (id, item_name, price, units_sold, units_left, cost_price, reorder_point, description)
            VALUES
                (:id, :item_name, :price, :units_sold, :units_left, :cost_price, :reorder_point, :description)
            """,
            (defaultdict(lambda: None, row) for row in changes["added_rows"]),
        )

    if changes["deleted_rows"]:
        cursor.executemany(
            "DELETE FROM inventory WHERE id = :id",
            ({"id": int(df.loc[i, "id"])} for i in changes["deleted_rows"]),
        )

    conn.commit()