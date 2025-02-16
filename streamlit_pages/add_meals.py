from collections import defaultdict
from pathlib import Path
import sqlite3

import streamlit as st
import altair as alt
import pandas as pd

import db_access as dba
import dialogs

# -----------------------------------------------------------------------------


# Load data from database
df = dba.load_table('meals')

st.header('Meal Tracker')

if df.empty:
    st.info('Start by adding a meal below', icon=':material/info:')
else:
    for index, meal in df.iterrows():
        meal_name = f'''<div style="text-align: center; font-size: 24px; font-weight: bold; margin-top: 20px; margin-bottom: 20px;">
                        {meal['meal_name']}
                        </div>'''
        with st.popover(meal['meal_name'], use_container_width=True):

            if meal['description']:
                st.write(meal['description'])

            with st.expander('View Ingredients'):
                df_ingredients = dba.run_sql_query(f'''SELECT ingredient_id, ingredient_name, quantity, unit, MAX(updated_at) FROM ingredients
                                                    WHERE meal_id == '{meal['meal_id']}'
                                                    GROUP BY ingredient_name;''')
                if not df_ingredients.empty:
                    df_ingredients = df_ingredients[['ingredient_name','quantity','unit']].rename(columns={'ingredient_name':'Ingredient','quantity':'Amount','unit':'Unit'})
                    st.dataframe(df_ingredients, hide_index=True, use_container_width=True)
                else:
                    pass

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