import streamlit as st
import menu

st.set_page_config(
    page_title="Meal Tracker"
)

headers = st.context.headers

pg = st.navigation(menu.get_pages())
pg.run()