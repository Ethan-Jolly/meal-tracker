import streamlit as st

def get_pages():
    pages = [
        st.Page('streamlit_pages/add_meals.py',title='Add Meals',icon='🛒'),
        st.Page('streamlit_pages/add_ingredients.py',title='Add Ingredients',icon='🍲'),
        st.Page('streamlit_pages/week_picker.py',title='Week Picker',icon='📆')
    ]
    return pages