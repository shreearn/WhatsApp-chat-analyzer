import re
import pandas as pd
import streamlit as st
from dateutil import parser
def preprocess(data):
    try:
        pattern = '\d{1,2}\/\d{2,4}\/\d{2,4},\s\d{1,2}:\d{1,2}\s\w{2}\s-\s'

        message = re.split(pattern, data)[1:]

        dates = re.findall(pattern, data)
        df = pd.DataFrame({'user_message': message, 'message_date': dates})
        df['message_date'] = df['message_date'].str.rstrip(' -').apply(parser.parse)
        df.rename(columns={'message_date': 'date'}, inplace=True)

        # Extract the usernames and messages from the user_message column and store them in separate lists.
        users = []
        messages = []
        for message in df['user_message']:
            entry = re.split('([\w\W]+?):\s', message)
            if entry[1:]:  # user name
                users.append(entry[1])
                messages.append(entry[2])
            else:
                users.append('group_notification')
                messages.append(entry[0])
        # Add the username and message lists to the Pandas dataframe.
        df['user'] = users
        df['message'] = messages
        # Drop the 'user_message' column.
        df.drop(columns=['user_message'], inplace=True)

        # Extract additional date-related features.
        df['only_date'] = df['date'].dt.date
        df['year'] = df['date'].dt.year
        df['month_num'] = df['date'].dt.month
        df['month'] = df['date'].dt.month_name()
        df['day'] = df['date'].dt.day
        df['day_name'] = df['date'].dt.day_name()
        df['hour'] = df['date'].dt.hour
        df['minute'] = df['date'].dt.minute

        # Create a new 'period' column to group messages by hour.
        period = []
        for hour in df[['day_name', 'hour']]['hour']:
            if hour == 23:
                period.append(str(hour) + "-" + str('00'))
            elif hour == 0:
                period.append(str('00') + "-" + str(hour + 1))
            else:
                period.append(str(hour) + "-" + str(hour + 1))

        df['period'] = period

    except Exception as e:
        st.error("You data doesn't contain am and pm format")
    return df
