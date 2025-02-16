from datetime import datetime, timedelta, date
import pandas as pd

def get_weeks_list(df_weeks):
    # Get existing weeks from df_weeks
    existing_weeks = pd.to_datetime(df_weeks['start_date'].unique()).tolist()
    
    # Get today's date
    today = datetime.now()
    
    # Find the next Monday
    days_until_monday = (7 - today.weekday()) % 7
    next_monday = today + timedelta(days=days_until_monday)
    
    # Generate list of 5 future Mondays
    future_mondays = [
        next_monday + timedelta(weeks=i) 
        for i in range(5)
    ]
    
    # Combine existing and future weeks, remove duplicates, and sort
    all_weeks = sorted(set(existing_weeks + future_mondays))
    
    # Convert to string format
    formatted_weeks = list(sorted(set([d.strftime('%Y-%m-%d') for d in all_weeks])))
    
    return formatted_weeks