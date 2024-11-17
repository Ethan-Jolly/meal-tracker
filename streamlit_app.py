from collections import defaultdict
from pathlib import Path
import sqlite3

import streamlit as st
import altair as alt
import pandas as pd

import db_access as dba
import dialogs


# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="Meal Tracker",
    layout="wide"
)

headers = st.context.headers
st.markdown(dict(headers))

st.session_state['user'] = 'dev'

# -----------------------------------------------------------------------------


# Connect to database and create table if needed
conn, db_was_just_created = dba.connect_db()

# Initialize data.
if db_was_just_created:
    dba.initialize_data(conn)
    st.toast("Database initialized with some sample data.")

# Load data from database
df = dba.load_meals(conn)

st.header('Meal Tracker')


cols = st.columns(4)
cols[0].markdown('Meal')
cols[1].markdown('Description')
cols[2].markdown('Added By')
cols[3].markdown('Time Added')

for index, row in df.iterrows():
    cols = st.columns(4)
    cols[0].markdown(row['meal_name'])
    cols[1].markdown(row['description'])
    cols[2].markdown(row['updated_by'])
    cols[3].markdown(row['updated_at'])

# st.dataframe(df, hide_index=True, use_container_width=True)

st.markdown('--------')

cols = st.columns(2)

add_meal = cols[0].button('Add Meal', use_container_width=True, type="primary")


if add_meal:
    st.session_state['meal_df'] = pd.DataFrame([], columns=['meal_id','meal_name','description'])

    dialogs.new_meal_dialog()

with cols[1].popover('Delete Meal', use_container_width=True):
    df_meals = dba.run_sql_query('''SELECT meal_id, meal_name, MAX(updated_at) FROM meals
                                    GROUP BY meal_name;''')
    chosen_meal = st.selectbox('Choose a meal',df_meals['meal_name'].unique())
    if not df_meals.empty:
        meal_id = df_meals[df_meals['meal_name']==chosen_meal]['meal_id'].reset_index(drop=True)[0]

        if st.button('Delete Meal', use_container_width=True):
            dba.delete_meal(meal_id)
            st.rerun()
        st.markdown(meal_id)


# Display data with editable table
# edited_df = st.data_editor(
#     df,
#     disabled=["id"],  # Don't allow editing the 'id' column.
#     num_rows="dynamic",  # Allow appending/deleting rows.
#     column_config={
#         # Show dollar sign before price columns.
#         "price": st.column_config.NumberColumn(format="$%.2f"),
#         "cost_price": st.column_config.NumberColumn(format="$%.2f"),
#     },
#     key="inventory_table",
# )

# has_uncommitted_changes = any(len(v) for v in st.session_state.inventory_table.values())

# st.button(
#     "Commit changes",
#     type="primary",
#     disabled=not has_uncommitted_changes,
#     # Update data in database
#     on_click=update_data,
#     args=(conn, df, st.session_state.inventory_table),
# )