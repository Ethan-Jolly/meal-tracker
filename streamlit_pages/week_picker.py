import streamlit as st
from datetime import datetime, timedelta, date
import db_access as dba
import pandas as pd

st.title('Week Picker')


today = datetime.now()

# Determine the ISO week number
week_number = today.isocalendar().week
year_number = today.isocalendar().year

week_id = str(year_number)+str(week_number)

weekday = today.weekday()

# Calculate the start of the week (Monday)
start_of_week = (today - timedelta(days=weekday)).date()

def get_next_five_weeks():
    # Get today's date
    today = datetime.now()
    
    # Find the next Monday
    days_until_monday = (7 - today.weekday()) % 7
    next_monday = today + timedelta(days=days_until_monday)
    
    # Generate list of 5 Mondays
    monday_dates = [
        (next_monday + timedelta(weeks=i)).strftime('%Y-%m-%d')
        for i in range(5)
    ]
    
    return monday_dates


weeks = get_next_five_weeks()

chosen_week = st.selectbox('Select a week', weeks)

st.subheader(f'Current Week')
st.markdown(f'##### {chosen_week}')
start_of_week = chosen_week

df = dba.load_table('weeks')
df['start_date'] = pd.to_datetime(df['start_date']).dt.date


current_df = df[df['start_date'] == start_of_week]

df_meals = dba.load_table('meals')

df_meals = df_meals[df_meals['meal_id'].isin(current_df['meal_id'].unique())]

for index, meal in df_meals.iterrows():
    with st.container(border=True):
        st.markdown(f'''<div style="text-align: center; font-size: 24px; font-weight: bold; margin-top: 20px; margin-bottom: 20px;">
                    {meal['meal_name']}
                    </div>''', unsafe_allow_html=True)
        with st.expander('View Description'):
            st.write(meal['description'])




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
