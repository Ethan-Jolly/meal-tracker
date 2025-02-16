import streamlit as st
from datetime import datetime, timedelta, date
import db_access as dba
import pandas as pd
import utils

st.title('Week Picker')


today = datetime.now()

# Determine the ISO week number
week_number = today.isocalendar().week
year_number = today.isocalendar().year

week_id = str(year_number)+str(week_number)

weekday = today.weekday()

# Calculate the start of the week (Monday)
start_of_week = (today - timedelta(days=weekday)).date()

df_weeks = dba.run_sql_query('''select * from weeks 
            where meal_id in (select distinct meal_id from meals);''')



weeks = utils.get_weeks_list(df_weeks)

chosen_week = st.selectbox('Select a week', weeks)


start_of_week = chosen_week

current_df = df_weeks[df_weeks['start_date'] == start_of_week]

df_meals = dba.load_table('meals')

df_meals = df_meals[df_meals['meal_id'].isin(current_df['meal_id'].unique())]

for index, meal in df_meals.iterrows():
    with st.container(border=True):
        st.markdown(f'''<div style="text-align: center; font-size: 24px; font-weight: bold; margin-top: 20px; margin-bottom: 20px;">
                    {meal['meal_name']}
                    </div>''', unsafe_allow_html=True)
        cols = st.columns([6,2])
        with cols[0].expander('View Ingredients'):
            df_ingredients = dba.run_sql_query(f'''select * from ingredients 
                                                where meal_id == '{meal['meal_id']}' ''')
            df_ingredients = df_ingredients[['ingredient_name', 'quantity', 'unit']].rename(columns={'ingredient_name': 'Ingredient', 'quantity': 'Quantity', 'unit': 'Unit'})
            if df_ingredients.empty:
                st.info('No ingredients found for this meal', icon=':material/info:')
            else:
                st.dataframe(df_ingredients)
        remove = cols[1].button(':material/delete:', use_container_width=True)
        if remove:
            dba.delete_week(start_of_week, meal['meal_id'])
            st.rerun()





if current_df.empty:
    st.info('No meals have been selected for the current week')

st.markdown('**Please choose a meal to add to the current week below:**')

query = '''SELECT t.meal_id, t.meal_name
        FROM meals t
        WHERE t.updated_at = (
            SELECT MAX(updated_at)
            FROM meals
            WHERE t.meal_name = meal_name
        );'''
meals = dba.run_sql_query(query)
meals_lst = meals['meal_name'].unique()
if meals.empty:
    st.info('No Meals Found. Please add a meal in the page below', icon=':material/info:')
    st.page_link('streamlit_pages/add_meals.py',label='Add Meals', icon=':material/add_shopping_cart:', use_container_width=True)
else:
    chosen_meal = st.selectbox('Select a meal', meals_lst)

    chosen_meal_id = meals[meals['meal_name']==chosen_meal]['meal_id'].reset_index(drop=True)[0]

    if not current_df[current_df['meal_id']==chosen_meal_id].empty:
        st.warning('This Meal has already been added this week')
    else:
        if st.button('Add', use_container_width=True):
            dba.insert_week(week_id, start_of_week, chosen_meal_id)
            st.rerun()
