import streamlit as st
import uuid
import pandas as pd
import db_access as dba
from datetime import datetime

@st.dialog("Add a new meals")
def new_meal_dialog():
    meal_name = st.text_input("What is the name of the meal?")
    description = st.text_input("Description")
    added_by = st.text_input("Added By")


    if not meal_name or not added_by:
        st.info('Please enter a meal name before adding to list')
    else:
        add = st.button("Add New Meal")
        if add:
            id = str(uuid.uuid4())
            df = pd.concat([st.session_state['meal_df'], pd.DataFrame([{'meal_id':id, 
                                            'meal_name':meal_name,
                                            'description':description,
                                            'updated_by':added_by,
                                            'updated_at':datetime.now()}])], ignore_index=True)
            st.session_state['meal_df'] = df
            st.markdown('**Current List**')
            st.dataframe(st.session_state['meal_df'][['meal_name','description']].rename({'meal_name':'Meal Name','description':'Description'}), hide_index=True,use_container_width=True)
    
    upload = st.button("Upload",
                disabled=st.session_state['meal_df'].empty,
                on_click=dba.insert_meals,
                args=(st.session_state['meal_df'],))

    if upload:
        st.rerun()
    

    # if st.button("Submit"):
        
    #     id = str(uuid.uuid4())
    #     data = {'meal_id':id, 
    #             'meal_name':meal_name,
    #             'decription':description}

    #     df = pd.Dataframe(data)



    #     st.rerun()