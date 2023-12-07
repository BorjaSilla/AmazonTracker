import streamlit as st
from pymongo import MongoClient
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pyecharts import options as opts
from pyecharts.charts import Line
from pyecharts.options import ComponentTitleOpts
from pyecharts.charts import Bar
from streamlit_echarts import st_pyecharts
from pyecharts.globals import ThemeType
from pyecharts.charts import Pie
from pyecharts.charts import Timeline, Bar
import streamlit.components.v1 as components
from pyecharts.charts import Scatter
from pyecharts.commons.utils import JsCode
import os

# Set page config as the first Streamlit command
st.set_page_config(
    page_title='AmazonTracker',
    page_icon='🔎'
)

# Access secrets
mongo_uri = st.secrets['MONGO_URI']


# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client["amazontracker"]
collection = db["scrape_collection"]
print('CONNECTED')

# Fetch data from MongoDB
data = list(collection.find())

print(len(data))

# Convert data to DataFrame
df = pd.DataFrame(data)

# Convert 'price' column to float, handling non-numeric values
df['price'] = pd.to_numeric(df['price'], errors='coerce')

# Convert 'datetime' column to datetime
df['datetime'] = pd.to_datetime(df['datetime'])

# Calculate the total number of products
total_products = len(df)

# Calculate the daily count of items
daily_count = df.groupby(df['datetime'].dt.date).size().reset_index(name='count')

# Add 'formatted_date' column to daily_count
daily_count['formatted_date'] = pd.to_datetime(daily_count['datetime']).dt.strftime('%Y-%m-%d')

# Calculate the cumulative sum for daily growth
daily_count['cumulative_count'] = daily_count['count'].cumsum()

# Calculate the total number of products
total_products = daily_count['cumulative_count'].iloc[-1]

# Calculate the count from 24 hours ago
count_24h_ago = daily_count['cumulative_count'].iloc[-2] if len(daily_count) > 1 else 0

# Calculate added today
added_today = total_products - count_24h_ago

# Calculate the percentage increase in the last 24 hours
percentage_increase_24h = ((added_today) / count_24h_ago) * 100 if count_24h_ago > 0 else 100

# Title
st.sidebar.title("AmazonTracker `v1.0`")

# Calculate the total number of unique ASINs
total_unique_asins = df['asin'].nunique()

# Display total number of unique ASINs, actual number of records, and percentage increase with green color
st.sidebar.markdown(
    f'<div style="text-align: left; color: #fff; font-size: 18px;">'
    f'<strong>{total_products} Records</strong>'
    f'<br><span style="color: #fff;font-size: 14px"><strong>{total_unique_asins} unique products</strong></span>'
    f'<br><span style="color: #008000;font-size: 14px"><strong>+{added_today} records added ({percentage_increase_24h:.2f}%)↑ today</strong></span>'
    f'<br><span style="color: #fff;font-size: 14px">⌚ Last Update: {df["datetime"].max()}</span>'
    f'</div>',
    unsafe_allow_html=True
)




st.sidebar.header('Filters🔎')

# Fetch unique categories and days from MongoDB
categories = collection.distinct("category")
# Add 'All' category to the list of categories at the beginning
categories.insert(0, 'All records')
categories.insert(1, 'Unique Products')

# Fetch unique days and add 'All' to the list of days
days = sorted(df["datetime"].dt.date.unique(), reverse=True)
days.insert(0, 'All')

# Category filter
selected_category = st.sidebar.selectbox("Select a category", categories)

# Day filter
selected_day = st.sidebar.selectbox("Select a day", days)

# Price slider
price_range = st.sidebar.slider("Select a price range", min_value=df['price'].min(), max_value=df['price'].max(), value=(df['price'].min(), df['price'].max()))


# Date range slider
date_range = st.sidebar.date_input("Select a date range", value=(df['datetime'].min().date(), df['datetime'].max().date()))


# Reset dates button
if st.sidebar.button("Reset Dates"):
    date_range = (df['datetime'].min().date(), df['datetime'].max().date())
    selected_day = 'All'

# Show available dates popup
available_dates = sorted(df['datetime'].dt.date.unique(), reverse=True)
available_date_range = f"{min(available_dates)} to {max(available_dates)}"
st.sidebar.text(f"ℹ️ Available Dates: {available_date_range}")

# Check if there is data for the selected date range
if (date_range[0] not in available_dates) or (date_range[1] not in available_dates):
    st.warning(f"No data available for the selected date range.\n ℹ️ Available Dates: {available_date_range}.")
    st.stop()

# Filter data based on the selected category, date range, and price range
if selected_category == 'All records':
    # If 'All' is selected for category, filter by the selected date range and display all records
    if selected_day == 'All':
        filtered_data = df[(df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1])]
    else:
        # If a specific day is chosen, filter by that day and the selected date range
        filtered_data = df[(df["datetime"].dt.date == selected_day) & (df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1])]
elif selected_category == 'Unique Products':
    # If 'All' is selected for category, display only unique ASINs without date filtering
    if selected_day == 'All':
        filtered_data = df[(df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1])].drop_duplicates(subset='asin')
    else:
        # If 'All' is selected for category but a specific day is chosen, filter by that day and the selected date range
        filtered_data = df[(df["datetime"].dt.date == selected_day) & (df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1])]
else:
    # Display data for the selected category, specific day, and date range, including duplicates
    if selected_day == 'All':
        filtered_data = df[(df["category"] == selected_category) & (df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1])]
    else:
        filtered_data = df[(df["category"] == selected_category) & (df["datetime"].dt.date == selected_day) & (df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1])]





total_records = len(filtered_data)
# Display total records in the sidebar as small blue text
st.sidebar.markdown(f'<div style="color: #33C5FF; font-size: 12px;">Selected Records: {total_records}</div>', unsafe_allow_html=True)

# KPIs
avg_price = filtered_data["price"].mean()
avg_rating = filtered_data["rating"].mean()
avg_reviews = filtered_data["num_reviews"].mean()

# THE TITLE
st.title(f"AmazonTracker")
st.write(f"#### Category: {selected_category.capitalize()}")

# Convert selected_day to pd.Timestamp if it's not 'All Records'
if selected_day != 'All':
    selected_day = pd.to_datetime(selected_day)

# Initialize df_last_24h_selected_date
df_last_24h_selected_date = pd.DataFrame()

# Filter data for all records 24 hours ago, considering the category
if selected_day != 'All':
    df_last_24h_selected_date = df[
        (df['datetime'] >= (selected_day - pd.DateOffset(hours=24))) &
        (df['datetime'] < selected_day) &
        ((df['category'] == selected_category) | (selected_category == 'All records') | (selected_category == 'Unique Products'))
    ]
else:
    # Handle the case when 'All Records' is selected as the category and 'All' is selected as the date
    df_last_24h_all_records = df[df['datetime'] >= (pd.to_datetime(df['datetime'].max()) - pd.DateOffset(hours=24))]
    if selected_category == 'All records':
        avg_price_24h_all_records = df_last_24h_all_records['price'].mean()
    elif selected_category == 'Unique Products':
        avg_price_24h_all_records = df_last_24h_all_records['price'].unique().mean()
    else:
        # Calculate the average price 24 hours ago for all categories
        avg_price_24h_all_records = df_last_24h_all_records['price'].mean()

# Continue with calculating other metrics as needed
avg_price_24h_ago = df_last_24h_selected_date['price'].mean() if selected_day != 'All' else avg_price_24h_all_records
avg_rating_24h_ago = df_last_24h_selected_date['rating'].mean() if selected_day != 'All' else df_last_24h_all_records['rating'].mean()
avg_reviews_24h_ago = df_last_24h_selected_date['num_reviews'].mean() if selected_day != 'All' else df_last_24h_all_records['num_reviews'].mean()

# Calculate the percentage changes for each metric in the last 24 hours leading up to the selected date
delta_avg_price = round(((avg_price - avg_price_24h_ago) / max(avg_price_24h_ago, 1)) * 100, 2) if avg_price_24h_ago > 0 and selected_day != 'All' else None
delta_avg_rating = round(((avg_rating - avg_rating_24h_ago) / max(avg_rating_24h_ago, 1)) * 100, 2) if avg_rating_24h_ago > 0 and selected_day != 'All' else None
delta_avg_reviews = round(((avg_reviews - avg_reviews_24h_ago) / max(avg_reviews_24h_ago, 1)) * 100, 2) if avg_reviews_24h_ago > 0 and selected_day != 'All' else None

# Create three columns for the metrics
metric1, metric2, metric3 = st.columns(3)

# Metric 1: Avg Price
with metric1:
    st.metric(
        label='Average Price 💲',
        value=f"€{avg_price:.2f}",
        delta=f"{delta_avg_price:.2f}% (24h)" if delta_avg_price is not None else None
    )

if selected_day != 'All':
    # Display the line only when 'All' is not selected for datetime
    st.write('Price 24h ago:', round(avg_price_24h_ago, 2), 'Price now:', round(avg_price, 2))

# Metric 2: Avg Rating
with metric2:
    st.metric(
        label='Average Rating ⭐',
        value=f"{avg_rating:.2f}",
        delta=f"{delta_avg_rating:.2f}% (24h)" if delta_avg_rating is not None else None
    )

# Metric 3: Avg Number of Reviews
with metric3:
    st.metric(
        label='Average Number of Reviews 📝',
        value=f"{avg_reviews:.2f}",
        delta=f"{delta_avg_reviews:.2f}% (24h)" if delta_avg_reviews is not None else None
    )

# Calculate the range of prices for the filtered data
filtered_price_range = filtered_data["price"].max() - filtered_data["price"].min()

# Calculate the number of bins such that each bin represents $1 for the filtered data
filtered_num_bins = int(filtered_price_range) + 1

# Apply the price filter to filtered_data
filtered_data = filtered_data[(filtered_data['price'] >= price_range[0]) & (filtered_data['price'] <= price_range[1])]

fig_filtered_price_distribution = px.histogram(
    filtered_data, 
    x="price", 
    nbins=filtered_num_bins,
    title=f"Price Distribution for {selected_category} on {selected_day}",
    range_x=[0, 300]  # Set the x-axis range from 0 to 200
)
# Set the width to 900
fig_filtered_price_distribution.update_layout(width=900, height=600)
st.plotly_chart(fig_filtered_price_distribution)


# Calculate average price per category based on the filtered data
avg_price_per_category = filtered_data.groupby("category")["price"].mean().sort_values(ascending=False).reset_index()

fig_bar = px.bar(
    avg_price_per_category, 
    x="price", 
    y="category", 
    color="category",  # Set color based on the "category" column
    orientation='h', 
    title="Average Price per Category",
    range_x=[0, 300],
    text="price",  # Display the average price as text labels
    height=700
)
fig_bar.update_traces(texttemplate='%{text:.2f}€', textposition='outside')  # Format the text labels
# Set the width to 900
fig_bar.update_layout(width=900)

st.plotly_chart(fig_bar)


# Filter out data points with a rating of 0
filtered_data_scatter = filtered_data[filtered_data['price'] > 0]

# Scatter plot for price vs. rating
fig_scatter = px.scatter(
    filtered_data_scatter,
    x='price',
    y='rating',
    color='category',
    title='Price vs. Rating',
    labels={'price': 'Price', 'rating': 'Rating'},
    hover_data=['title'],  # Display product title on hover
)

# Set y-axis range from 0 to 5
fig_scatter.update_layout(yaxis=dict(range=[0, 5.1]))

# Set the width to 900
fig_scatter.update_layout(width=900, height=700)

# Display the plot in Streamlit app
st.plotly_chart(fig_scatter)

# Calculate the range of ratings for the filtered data
filtered_rating_range = filtered_data["rating"].max() - filtered_data["rating"].min()

# Calculate the number of bins such that each bin represents one rating for the filtered data
filtered_num_bins_rating = int(filtered_rating_range) + 1

# Apply the rating filter to filtered_data
filtered_data = filtered_data[(filtered_data['rating'] > 0)]  # Filter out data points with a rating of 0

# Create a histogram for the rating distribution with bins of size 0.1
fig_filtered_rating_distribution = px.histogram(
    filtered_data, 
    x="rating", 
    nbins=50,  # Set the number of bins to represent 0.1 increments
    title=f"Rating Distribution for {selected_category} on {selected_day}",
    range_x=[0, 5.5]  # Set the x-axis range from 0 to 5
)
# Set the width to 900
fig_filtered_rating_distribution.update_layout(width=900, height=600)
st.plotly_chart(fig_filtered_rating_distribution)




# Reviews Over Time (Line chart)
filtered_reviews_data = df.copy()

# Apply filters to the data
if selected_category != 'All records':
    filtered_reviews_data = filtered_reviews_data[filtered_reviews_data["category"] == selected_category]

filtered_reviews_data = filtered_reviews_data[(filtered_reviews_data['datetime'].dt.date >= date_range[0]) & (filtered_reviews_data['datetime'].dt.date <= date_range[1])]
filtered_reviews_data = filtered_reviews_data[(filtered_reviews_data['price'] >= price_range[0]) & (filtered_reviews_data['price'] <= price_range[1])]

fig_reviews_over_time = px.line(
    filtered_reviews_data.groupby(filtered_reviews_data['datetime'].dt.date)["num_reviews"].sum().reset_index(),
    x="datetime", y="num_reviews",
    title="Reviews Over Time",
    labels={'datetime': 'Date', 'num_reviews': 'Number of Reviews'},
)

# Set the width to 900
fig_reviews_over_time.update_layout(width=900, height=500)
st.plotly_chart(fig_reviews_over_time)  



# Calculate the database size for each hour
database_size_hourly = df.groupby(df['datetime'].dt.floor('H'))['asin'].nunique().cumsum().reset_index()
database_size_hourly.columns = ['datetime', 'database_size']

# Line chart for database size progression
fig_database_size_hourly = px.line(
    database_size_hourly,
    x='datetime',
    y='database_size',
    title='Database Size Progression (Hourly)',
    labels={'datetime': 'Date', 'database_size': 'Database Size'},
)

# Set the width and height in the sidebar
fig_database_size_hourly.update_layout(width=300, height=300)

# Display the database size progression line chart in the sidebar
st.sidebar.plotly_chart(fig_database_size_hourly)

# Filter data for reviews
filtered_reviews_data = df.copy()

# Apply filters to the data
filtered_reviews_data = filtered_reviews_data[(filtered_reviews_data['datetime'].dt.date >= date_range[0]) & (filtered_reviews_data['datetime'].dt.date <= date_range[1])]
filtered_reviews_data = filtered_reviews_data[(filtered_reviews_data['price'] >= price_range[0]) & (filtered_reviews_data['price'] <= price_range[1])]

# Calculate average reviews per category per day
avg_reviews_per_category_per_day = filtered_reviews_data.groupby(['category', filtered_reviews_data['datetime'].dt.date])['num_reviews'].mean().reset_index()

# Bar chart for average reviews animated per day
fig_avg_reviews_per_category = px.bar(
    avg_reviews_per_category_per_day,
    x='category',
    y='num_reviews',
    animation_frame='datetime',
    title='Average Reviews per Category (Animated)',
    labels={'num_reviews': 'Average Reviews'},
    range_y=[0, 80000],
)

# Set the width to 900
fig_avg_reviews_per_category.update_layout(width=900)

# Display the animated bar chart in the main area
st.plotly_chart(fig_avg_reviews_per_category)

# Filter data for ratings
filtered_ratings_data = df.copy()

# Apply filters to the data
filtered_ratings_data = filtered_ratings_data[(filtered_ratings_data['datetime'].dt.date >= date_range[0]) & (filtered_ratings_data['datetime'].dt.date <= date_range[1])]
filtered_ratings_data = filtered_ratings_data[(filtered_ratings_data['price'] >= price_range[0]) & (filtered_ratings_data['price'] <= price_range[1])]

# Calculate average ratings per category per day
avg_ratings_per_category_per_day = filtered_ratings_data.groupby(['category', filtered_ratings_data['datetime'].dt.date])['rating'].mean().reset_index()

# Bar chart for average ratings animated per day
fig_avg_ratings_per_category = px.bar(
    avg_ratings_per_category_per_day,
    x='category',
    y='rating',
    animation_frame='datetime',
    title='Average Ratings per Category (Animated)',
    labels={'rating': 'Average Ratings'},
    range_y=[0, 5.1],
)

# Set the width to 900
fig_avg_ratings_per_category.update_layout(width=900)

# Display the animated bar chart in the main area
st.plotly_chart(fig_avg_ratings_per_category)



# Filter data for prices
filtered_prices_data = df.copy()

# Apply filters to the data
filtered_prices_data = filtered_prices_data[(filtered_prices_data['datetime'].dt.date >= date_range[0]) & (filtered_prices_data['datetime'].dt.date <= date_range[1])]
filtered_prices_data = filtered_prices_data[(filtered_prices_data['price'] >= price_range[0]) & (filtered_prices_data['price'] <= price_range[1])]

# Calculate average prices per category per day
avg_prices_per_category_per_day = filtered_prices_data.groupby(['category', filtered_prices_data['datetime'].dt.date])['price'].mean().reset_index()

# Bar chart for average prices animated per day with fixed Y-axis range
fig_avg_prices_per_category = px.bar(
    avg_prices_per_category_per_day,
    x='category',
    y='price',
    animation_frame='datetime',
    title='Average Prices per Category (Animated)',
    labels={'price': 'Average Prices'},
    range_y=[0, 300],  # Fix Y-axis range to 0-300
)

# Set the width to 900
fig_avg_prices_per_category.update_layout(width=900)

# Display the animated bar chart in the main area
st.plotly_chart(fig_avg_prices_per_category)

# Add a centered text below the chart with smaller size and 50% opacity
st.sidebar.markdown("<h5 style='text-align: center; opacity: 0.5;'>Made by Borja SG</h5>", unsafe_allow_html=True)
