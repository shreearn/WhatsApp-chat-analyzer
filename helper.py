from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
import re
from collections import Counter
import emoji
import numpy as np
import matplotlib.pyplot as plt
import nltk
nltk.download('vader_lexicon')
from datetime import datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer

extract = URLExtract()

def clean_non_ascii_words(text):
    words_list = []
    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7f]', r'', text)
    words_list.append(text)
    text = ' '.join(words_list)
    return text

def clean_non_english_words(text):
    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7f]', r' ', text)
    # Remove non-English characters
    english_chars = re.compile(r'[A-Za-z]+')
    text = ' '.join(english_chars.findall(text))
    return text

def fetch_stats(selected_user,df):

    if selected_user!='Overall':
        df = df[df['user'] == selected_user]

    # Fetching number of messages
    pd.set_option('display.max_rows', None)
    num_messages = df.shape[0]

    # Fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))  # To get URL links
        links.extend(re.findall(r'https?://(?:www\.)?(?:drive|docs)\.google\.(?:com|co\.[a-z]{2,3})/\S+', message))  # To get drive links
    len_links = len(links)
    # Fetch Total number of words
    def clean_links(text):
        # Remove other URLs from chat message
        regex_pattern = r'(http|https)://[^\s]*'
        urls = re.findall(regex_pattern, text)
        for url in urls:
            text = text.replace(url, '')
        return text

    def clean_drive_links(text):
        # Remove Google Drive links
        text = re.sub(r'https?://drive.google.com/\S+', '', text)
        return text

    def clean_punctuations_and_numbers(text):
        # use regular expression to exclude punctuations and also numbers
        text = re.sub(r'[^\w\s]|[\d]', '', text)
        return text

    words = []
    temp = df['message']
    temp = temp.apply(clean_drive_links)  # To exclude any drive links
    temp = temp.apply(clean_links)  # To exclude any links
    temp = temp.apply(clean_punctuations_and_numbers)

    # Creating a function to remove emoji from the words
    for message in temp.apply(clean_non_ascii_words):
        words.extend(message.split())

    # Fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    return num_messages, len(words),num_media_messages,len_links

def most_busy_user(df):
    x = df['user'].value_counts().head()
    df = df[df['user'] != 'group_notification']
    df = round((df['user'].value_counts()/df.shape[0])*100,2).reset_index().rename(columns={
        'index':'Name','user':'Percent'})
    # Rearranging Index
    df.index = np.arange(1, len(df) + 1)
    return x,df

def create_word_cloud(selected_user, df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Filtering the data
    temp = df[df['user'] != 'group_notification']  # Excluding the group notifications
    temp = temp[temp['message'] != '<Media omitted>\n']  # Excluding the media files which were omitted
    temp = temp.loc[~temp['message'].str.contains('Missed voice call')]  # Excluding voice call notification
    temp = temp.loc[~temp['message'].str.contains('Missed video call')]  # Excluding video call notification
    temp = temp.loc[
        ~temp['message'].str.contains('This message was deleted')]  # Excluding the messages deleted by the user itself
    temp = temp.loc[~temp['message'].str.contains(
        'deleted this message')]  # Excluding the messages deleted by other members in the group

    def clean_links(text):
        # Remove other URLs from chat message
        regex_pattern = r'(http|https)://[^\s]*'
        urls = re.findall(regex_pattern, text)
        for url in urls:
            text = text.replace(url, '')
        return text

    def clean_drive_links(text):
        # Remove Google Drive links
        text = re.sub(r'https?://drive.google.com/\S+', '', text)
        return text

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    # Clean links and stop words from messages and leave the message empty(while in whole row other data is present)
    temp['message'] = temp['message'].apply(clean_drive_links)
    temp['message'] = temp['message'].apply(clean_links)
    temp['message'] = temp['message'].apply(remove_stop_words)
    temp['message'] = temp['message'].apply(clean_non_ascii_words)
    temp['message'] = temp['message'].apply(clean_non_english_words)

    # Exclude empty messages
    temp = temp[temp['message'].str.len() > 0]

    if temp.empty or temp.size==0:
        return None
    else:
        wc = WordCloud(width=500, height=400, min_font_size=10, background_color='white')
        df_wc = wc.generate(temp['message'].str.cat(sep=" "))
        return df_wc

def most_common_words(selected_user,df):

    def clean_punctuations_and_numbers(text):
        # use regular expression to exclude punctuations and also numbers
        text = re.sub(r'[^\w\s]|[\d]', '', text)
        return text

    f = open('stop_hinglish.txt','r')
    stop_words = f.read()

    if selected_user!='Overall':
        df = df[df['user'] == selected_user]

    def clean_links(text):
        # Remove other URLs from chat message
        regex_pattern = r'(http|https)://[^\s]*'
        urls = re.findall(regex_pattern, text)
        for url in urls:
            text = text.replace(url, '')
        return text

    def clean_drive_links(text):
        # Remove Google Drive links
        text = re.sub(r'https?://drive.google.com/\S+', '', text)
        return text

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    temp = temp.loc[~temp['message'].str.contains('This message was deleted')]  # Excluding the messages deleted by the user itslef
    temp = temp.loc[~temp['message'].str.contains('deleted this message')]  # Excluding the messages deleted by other members in the group
    temp = temp.loc[~temp['message'].str.contains('Missed voice call')]  # Excluding voice call notification
    temp = temp.loc[~temp['message'].str.contains('Missed video call')]  # Excluding video call notification
    temp['message'] = temp['message'].apply(clean_drive_links)  # To exclude drive links
    temp['message'] = temp['message'].apply(clean_links)  # To exclude url links
    temp['message'] = temp['message'].apply(clean_punctuations_and_numbers)  # To exclude punctuations

    words = []
    for message in temp['message'].apply(clean_non_ascii_words):
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
    if len(words)==0:
        most_common_df = pd.DataFrame()
        return most_common_df
    else:
        most_common_df = pd.DataFrame(Counter(words).most_common(5))
        return most_common_df

def emoji_helper(selected_user,df):

    if selected_user!='Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.UNICODE_EMOJI['en']])

    # If there are no emojis used
    if len(emojis) == 0:
        emoji_df = pd.DataFrame() # create empty DataFrame
        return emoji_df
    else:
        emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

        # Rearranging index
        emoji_df.index = np.arange(1, len(emoji_df) + 1)
        # Renaming Columns
        emoji_df.rename(columns={0: 'Emojis', 1: 'Count'}, inplace=True)

        # Demojizing the emoji
        emoji_list = []
        for i in emoji_df['Emojis']:
            a = emoji.demojize(i)
            emoji_list.append(a)
        emoji_df['sentiments'] = emoji_list

        # Replacing the [:,_] from the sentiments
        chars_to_remove = [':', '_']
        for char in chars_to_remove:
            emoji_df['sentiments'] = emoji_df['sentiments'].str.replace(char, ' ')

        return emoji_df

def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby(['only_date']).count()['message'].reset_index()

    time = []
    for i in range(daily_timeline.shape[0]):
        time.append(datetime.strftime(daily_timeline['only_date'][i], '%b-%d-%Y'))

    daily_timeline['time'] = time

    return daily_timeline

def week_activity_map(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    # Sorting the columns
    sorted_columns = ['00-1', '1-2', '2-3', '3-4', '4-5', '5-6', '6-7', '7-8', '8-9', '9-10', '10-11',
                      '11-12','12-13', '13-14', '14-15', '15-16', '16-17', '17-18', '18-19',
                      '19-20', '20-21', '21-22', '22-23','23-00']
    user_heatmap = user_heatmap.reindex(columns=sorted_columns,fill_value=0)
    # As many users would not have chat in some time periods so the value will be NA for them so replacing it with 0
    return user_heatmap


def addlabels(x, y):
    for i in range(len(x)):
        plt.text(i, y[i] // 2, y[i], ha='center',bbox=dict(facecolor='white', alpha=.5))

def night_owl(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    night_owl = df[(df['hour'] >= 0) & (df['hour'] < 5)].groupby('user').size().idxmax()
    return night_owl

def early_bird(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

def nlp_sentiment_analysis(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    sentiment = []
    sid = SentimentIntensityAnalyzer()
    for message in df['message']:
        score = sid.polarity_scores(message)['compound']
        if score >= 0.9:
            sentiment.append('very positive')
        elif score >= 0.1 and score < 0.9:
            sentiment.append('positive')
        elif score > -0.1 and score < 0.1:
            sentiment.append('neutral')
        elif score > -0.9 and score <= -0.1:
            sentiment.append('negative')
        else:
            sentiment.append('very negative')
    df['sentiment'] = sentiment
    return df['sentiment'].value_counts()
