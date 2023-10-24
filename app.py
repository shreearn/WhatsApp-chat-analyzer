import streamlit as st
import preprocessor,helper
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns
import plotly.graph_objs as go
import base64
import numpy as np
import pandas as pd
from pathlib import Path
from streamlit_echarts import st_echarts

# --- PATH SETTINGS ---
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
css_file = current_dir / "styles" / "main.css"

# --- GENERAL SETTINGS ---
PAGE_TITLE = "WhatsApp Chat Analyzer"
PAGE_ICON = ":mag_right:"
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)

# --- LOAD CSS---
with open(css_file) as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)


st.sidebar.markdown("<span style='font-size: 26px; font-weight: bold;'><u>WhatsApp Chat Analyzer</u></span>", unsafe_allow_html=True)

def download_file():
    with open('test.txt', 'r', encoding='utf-8') as f:
        contents = f.read()
    b64 = base64.b64encode(contents.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="test.txt">Download file</a>'
    st.sidebar.markdown(href, unsafe_allow_html=True)

# Add a expander
expand_sidebar = st.sidebar.checkbox("Click to know why to download")
if expand_sidebar:
    st.sidebar.caption("Download the test file for analyzing Whatsapp chats (useful if you don't have any chats to upload) or upload your own chats for analysis")
# Add download button to sidebar
if st.sidebar.button('Download File'):
    download_file()



uploaded_file = st.sidebar.file_uploader("Choose a file",type="txt")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    try:
        # Fetching unique user
        user_list = df['user'].unique().tolist()
    except Exception as e:
        st.stop()

    try:
        if 'group_notification' in user_list:
            user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0, "Overall")
        selected_user = st.sidebar.selectbox("Show Analysis wrt", user_list)
    except Exception as e:
        st.stop()

    if st.sidebar.button("Show Analysis"):
        with st.spinner("Running analysis..."): # show spinner while analysis is running
            # Stats Area
            try:
                num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

                st.title("Top Satistics")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.header("Total Messages")
                    st.title(num_messages)
                with col2:
                    st.header("Total Words")
                    st.title(words)
                with col3:
                    st.header("Media Shared")
                    st.title(num_media_messages)
                with col4:
                    st.header("Links Shared")
                    st.title(num_links)

            except Exception as e:
                st.error(f"Error occured is: {e}")  # Display an error message if an exception is raised

            # Monthly Timeline
            try:
                st.title("Monthly Timeline")
                timeline = helper.monthly_timeline(selected_user, df)
                # Plot the line chart using `st_echarts`
                options = {
                    'xAxis': {'type': 'category', 'data': timeline['time'].tolist(), 'axisLabel': {'rotate': 90,'fontSize':9}},
                    'yAxis': {'type': 'value'},
                    'series': [{'type': 'line', 'data': timeline['message'].tolist()}],
                    'tooltip': {'trigger': 'axis'},
                }
                chart_height = 500
                chart = st_echarts(options=options, height=chart_height)

                # Daily Timeline
                st.title("Daily Timeline")
                daily_timeline = helper.daily_timeline(selected_user, df)
                # Convert 'only_date' column to datetime-like data type
                daily_timeline['only_date'] = pd.to_datetime(daily_timeline['only_date'])
                # Drop rows with null or missing values in 'only_date' column
                daily_timeline.dropna(subset=['only_date'], inplace=True)
                # Convert 'date' objects to string representations with a specific format
                daily_timeline['only_date'] = daily_timeline['only_date'].dt.strftime('%Y-%m-%d')

                # Define the chart options
                chart_options = {
                    'xAxis': {'type': 'category', 'data': daily_timeline['only_date'].tolist(),
                              'axisLabel': {'rotate': 90,'fontSize':11}},
                    'yAxis': {'type': 'value'},
                    'series': [{'type': 'line', 'data': daily_timeline['message'].tolist()}],
                    'tooltip': {'trigger': 'axis'}
                }
                # Render the chart using streamlit-echarts
                st_echarts(options=chart_options, height=500)
                
            except Exception as e:
                st.error(f"Error occured is: {e}")  # Display an error message if an exception is raised

            # Activity map
            try:
                st.title("Activity Map")
                col1, col2 = st.columns(2)

                with col1:
                    st.header("Most Busy Day")
                    result_placeholder = st.empty()  # Create a placeholder element to display the result
                    with st.spinner('Running...'):  # Display a spinner
                        # Code of most busy day
                        busy_day = helper.week_activity_map(selected_user, df)
                        fig, ax = plt.subplots()
                        ax.bar(busy_day.index, busy_day.values, color='c')
                        plt.xticks(rotation='vertical')
                        helper.addlabels(busy_day.index, busy_day.values)  # To add data labels on bar graph
                        st.pyplot(fig)
                    result_placeholder.write()  # Update the placeholder element with the result

                with col2:
                    st.header("Most Busy Month")
                    result_placeholder = st.empty()  # Create a placeholder element to display the result
                    with st.spinner('Running...'):  # Display a spinner
                        # Code of most busy month
                        busy_month = helper.month_activity_map(selected_user, df)
                        fig, ax = plt.subplots()
                        ax.bar(busy_month.index, busy_month.values, color='#c20078')
                        plt.xticks(rotation='vertical')
                        helper.addlabels(busy_month.index, busy_month.values)  # To add data labels on bar graph
                        st.pyplot(fig)
                    result_placeholder.write()  # Update the placeholder element with the result

                st.title("Weekly Activity Map")
                result_placeholder = st.empty()  # Create a placeholder element to display the result
                with st.spinner('Running...'):  # Display a spinner
                    # Code of heatmap
                    user_heatmap = helper.activity_heatmap(selected_user, df)
                    fig, ax = plt.subplots()
                    ax = sns.heatmap(user_heatmap)
                    st.pyplot(fig)
                result_placeholder.write()  # Update the placeholder element with the result

            except Exception as e:
                st.error(f"Error occured is: {e}")  # Display an error message if an exception is raised

            # WordCloud
            try:
                st.title("WordCloud")
                result_placeholder = st.empty()  # Create a placeholder element to display the result
                with st.spinner('Running...'):  # Display a spinner to indicate that the function is running
                    # Code of wordcloud
                    df_wc = helper.create_word_cloud(selected_user, df)
                    if df_wc is None:
                        st.write("<span style='font-size: 24px'>🚫 Word Cloud is not possible.</span>",
                                 unsafe_allow_html=True)
                    else:
                        fig, ax = plt.subplots()
                        ax.imshow(df_wc, interpolation='bilinear')
                        st.pyplot(fig)

                result_placeholder.write()  # Update the placeholder element with the result


            except Exception as e:
                st.error(f"Error occured is: {e}")  # Display an error message if an exception is raised

            # Most Busiest User(Group Level)
            try:
                if selected_user == 'Overall':
                    st.title("Most Busiest User")
                    result_placeholder = st.empty()  # Create a placeholder element to display the result
                    with st.spinner('Running...'):  # Display a spinner
                        # Code of Most busiest user
                        x, new_df = helper.most_busy_user(df)
                        fig, ax = plt.subplots()

                        col1, col2 = st.columns(2)

                        with col1:
                            ax.bar(x.index, x.values, color='red')
                            plt.xticks(rotation='vertical')
                            st.pyplot(fig)

                        with col2:
                            st.dataframe(new_df)
                        result_placeholder.write()  # Update the placeholder element with the result

            except Exception as e:
                st.error(f"Error occured is: {e}")  # Display an error message if an exception is raised

            # Most Common Words
            try:
                st.title("Most Common Words")
                result_placeholder = st.empty()  # Create a placeholder element to display the result
                with st.spinner('Running...'):  # Display a spinner
                    # Code of most common words
                    most_common_df = helper.most_common_words(selected_user, df)
                    if most_common_df.empty:
                        st.write(
                            "<span style='font-size: 24px'>🚫 Words are not present or irrelevant words in chat.</span>",
                            unsafe_allow_html=True)

                    else:
                        fig = go.Figure(data=go.Bar(
                            x=most_common_df[1],
                            y=most_common_df[0],
                            orientation='h',  # Set bars to be horizontal
                            text=most_common_df[1],  # Use word counts as data labels
                            textposition='inside',
                            insidetextanchor='middle',
                            marker=dict(color='mediumseagreen')
                        ))
                        fig.update_traces(textfont=dict(size=14, color='white'))
                        # Customize axis labels and tick values
                        fig.update_layout(xaxis_title='Value', yaxis_title='Category',
                                          xaxis=dict(tickmode='auto', tick0=0, dtick=5))

                        st.plotly_chart(fig)
                        result_placeholder.write()  # Update the placeholder element with the result

            except Exception as e:
                st.error(f"Error occured is: {e}")  # Display an error message if an exception is raised

            # Emoji Analysis
            try:
                result_placeholder = st.empty()  # Create a placeholder element to display the result
                with st.spinner('Running...'):  # Display a spinner
                    # Code of emoji analysis
                    emoji_df = helper.emoji_helper(selected_user, df)
                    st.title("Emoji Analysis")
                    if emoji_df.size == 0:
                        # Set the font size to 24px
                        st.write("<span style='font-size: 24px'>🚫 No emojis used in chat.</span>",
                                 unsafe_allow_html=True)
                    else:
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("Count Table")
                            st.dataframe(emoji_df)
                        with col2:
                            fig, ax = plt.subplots()

                            # Create a pie chart
                            trace = go.Pie(labels=emoji_df['Emojis'].head(), values=emoji_df['Count'].head(), hole=0.5)
                            # Create a layout for the plot
                            layout = go.Layout()
                            # Create a figure object and add the trace and layout
                            fig = go.Figure(data=[trace], layout=layout)
                            fig.update_traces(textposition='inside', textinfo='percent+label')
                            fig.update_layout(width=800, height=500)

                            st.write("Donut Chart of Top 5 Emoji")
                            st.plotly_chart(fig)
                            result_placeholder.write()  # Update the placeholder element with the result

            except Exception as e:
                st.error(f"Error occured is: {e}")  # Display an error message if an exception is raised

            # Sentiment Analysis
            try:
                st.title("Sentiment Analysis")
                result_placeholder = st.empty()  # Create a placeholder element to display the result
                with st.spinner('Running...'):  # Display a spinner
                    # Code of sentiment analysis
                    sentiment = helper.nlp_sentiment_analysis(selected_user, df)

                    fig, ax = plt.subplots()
                    plt.figure(figsize=(10, 5))
                    ax.bar(sentiment.index, sentiment.values, color=['yellow', 'green', 'red'])
                    # To add data labels
                    for i, v in enumerate(sentiment.values):
                        ax.text(i, v / 2, str(v), color='white', fontweight='bold', ha='center',
                                bbox=dict(facecolor='black', alpha=0.5))
                    plt.xlabel("Sentiment", fontsize=14)
                    plt.ylabel("Number of Messages", fontsize=14)
                    plt.title("Sentiment Analysis of Messages as Classification", fontsize=18, fontweight='bold')
                    st.pyplot(fig)
                    result_placeholder.write()  # Update the placeholder element with the result

            except Exception as e:
                st.error(f"Error occured is: {e}")  # Display an error message if an exception is raised

            # Early Bird & Night Owl Detection
            try:
                st.title("Fun Facts")

                # Identify the person with the most messages sent during night hours
                night_owl_group = df[(df['hour'] >= 0) & (df['hour'] < 5)].groupby('user').size()

                if night_owl_group.empty:
                    night_owl = "No one"
                else:
                    night_owl = night_owl_group.idxmax()

                # Identify the person with the most messages sent during early morning hours
                early_bird_group = df[(df['hour'] >= 5) & (df['hour'] < 9)].groupby('user').size()

                if early_bird_group.empty:
                    early_bird = "No one"
                else:
                    early_bird = early_bird_group.idxmax()

                # To display message differently in a group and personal chat
                unique_user = df['user'].unique()
                if len(unique_user) > 3:  # For Group Chat
                    st.write(
                        f"<span style='font-size: 28px'><u><b>{early_bird}</u> is the early bird in the group.</b></span>",
                        unsafe_allow_html=True)
                    st.write(
                        f"<span style='font-size: 28px'><u><b>{night_owl}</u> is the night owl in the group.</b></span>",
                        unsafe_allow_html=True)
                else:  # For Personal Chat
                    st.write(f"<span style='font-size: 28px'><u><b>{early_bird}</u> is the early bird.</b></span>",
                             unsafe_allow_html=True)
                    st.write(f"<span style='font-size: 28px'><u><b>{night_owl}</u> is the night owl.</b></span>",
                             unsafe_allow_html=True)


            except Exception as e:
                st.error(f"Error occured is: {e}")  # Display an error message if an exception is raised
