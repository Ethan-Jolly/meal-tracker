from collections import defaultdict
from pathlib import Path
import sqlite3

import streamlit as st
import altair as alt
import pandas as pd

import db_access as dba
import dialogs
import uuid
from datetime import datetime

st.title('Add Ingredients')

if st.session_state['ingredient_added']:
    st.session_state['ingredient_added'] = False
    st.toast('Ingredient added successfully', icon=':material/check:')

df_meals = dba.run_sql_query('''SELECT meal_id, meal_name, MAX(updated_at) FROM meals
                                    GROUP BY meal_name;''')

chosen_meal = st.selectbox('Choose a meal to add ingredients to: ', df_meals['meal_name'].unique())

meal_id = df_meals[df_meals['meal_name']==chosen_meal]['meal_id'].reset_index(drop=True)[0]

df_ingredients = dba.run_sql_query(f'''SELECT ingredient_id, ingredient_name, quantity, unit, MAX(updated_at) FROM ingredients
                                    WHERE meal_id == '{meal_id}'
                                    GROUP BY ingredient_name;''')

st.markdown('**Current Ingredients**')
if not df_ingredients.empty:
    df_ingredients = df_ingredients[['ingredient_name','quantity','unit']].rename(columns={'ingredient_name':'Ingredient','quantity':'Amount','unit':'Unit'})
    st.dataframe(df_ingredients, hide_index=True, use_container_width=True)
else:
    st.info('No ingredients added yet', icon=':material/info:')

with st.form('Add ingredient'):
    ingredient = st.text_input('Ingredient', key='ingredient')
    cols = st.columns(2)
    amount = cols[0].number_input('Amount')
    unit = cols[1].text_input('Unit', key='unit')

    submit = st.form_submit_button('Submit')
    if submit:
        st.session_state['ingredient_added'] = True

        df = pd.concat([pd.DataFrame([{'ingredient_id':str(uuid.uuid4()),
                                        'meal_id':meal_id,
                                        'ingredient_name':ingredient,
                                        'quantity':amount,
                                        'unit':unit,
                                        'updated_by':'user',
                                        'updated_at':datetime.now()}])], ignore_index=True)
        
        dba.insert_ingredients(df)
        st.rerun()