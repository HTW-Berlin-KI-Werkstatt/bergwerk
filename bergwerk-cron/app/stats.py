import pandas as pd
from tools import tools
from matplotlib import pyplot as plt
import seaborn as sns   
from datetime import datetime

print("Running stats cron!")

page = """
= All Time Statistics =

This page is updated every day with the latest statistics for this assistant.

== Unique Users per Day== 

[[File:upd_all_time.png|1000px|Number of Unique Users per Day]]

== Unique Users per Week ==

[[File:upw_all_time.png|1000px|Number of Unique Users per Week]]

== Messages per Hour ==

[[File:mph_all_time.png|1000px|Number of Messages per Hour]]

== Messages per Day of Week ==

[[File:mpdow_all_time.png|1000px|Number of Messages per Day of Week]]
"""

df = tools.sql2pd("tracker_db", "tracker")

df['datetime'] = pd.to_datetime(df['ts'], unit='s')
df['year'] =  df['datetime'].dt.year
df['month'] =  df['datetime'].dt.month
df['day'] =  df['datetime'].dt.day
df['dow'] = df['datetime'].dt.dayofweek
df['hour'] =  df['datetime'].dt.hour
df['date'] = df['datetime'].dt.date
unique_users_per_day = df.groupby('date')['id'].nunique()


plt.figure(figsize=(12, 6))
plt.plot(unique_users_per_day.index, unique_users_per_day.values)
plt.title('Number of Unique Users per Day')
plt.xlabel('Date')
plt.ylabel('Number of unique users')
plt.savefig("/usr/src/app/upd_all_time.png")

df['year_week'] = df['datetime'].dt.strftime('%Y-%U')
unique_users_per_week = df.groupby('year_week')['id'].nunique()
unique_users_per_week = unique_users_per_week.sort_index()

unique_users_per_week.plot(kind='bar', figsize=(12, 6), title='Number of Unique Users per Week')
plt.xlabel('Year and Week')
plt.ylabel('Number of Unique Users')
plt.xticks(rotation=45)
plt.savefig("/usr/src/app/upw_all_time.png")

# Compute the number of messages per hour
messages_per_hour = df.groupby('hour').size()
messages_per_dow = df.groupby('dow').size()
plt.figure(figsize=(12, 6))
messages_per_hour.plot(kind='bar', title='Number of Messages per Hour')
plt.xlabel('Hour of the Day')
plt.ylabel('Number of Messages')
plt.savefig("/usr/src/app/mph_all_time.png")

# Plot the number of messages per day of the week
plt.figure(figsize=(12, 6))
messages_per_dow.plot(kind='bar', title='Number of Messages per Day of the Week')
plt.xlabel('Day of the Week')
plt.ylabel('Number of Messages')
plt.xticks(ticks=range(7), labels=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], rotation=45)
plt.savefig("/usr/src/app/mpdow_all_time.png")

tools.create_or_update_page("Stats", page, ["/usr/src/app/upd_all_time.png", 
                                            "/usr/src/app/upw_all_time.png",
                                            "/usr/src/app/mph_all_time.png",
                                            "/usr/src/app/mpdow_all_time.png"])