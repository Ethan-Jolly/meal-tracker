import streamlit as st

def get_pages():
    pages = [
        st.Page('streamlit_pages/add_meals.py',title='Add Meals',icon=':material/add_shopping_cart:'),
        st.Page('streamlit_pages/week_picker.py',title='Week Picker',icon=':material/event:')
    ]
    return pages