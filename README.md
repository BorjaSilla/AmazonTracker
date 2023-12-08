# Amazon Tracker

![Amazon Tracker](https://i.imgur.com/nhyHXzi.png)

Track and analyze Amazon product data with ease! Explore the live demo [here](https://amazontracker.streamlit.app/). 🚀

## Table of Contents

- [Introduction](#introduction)
- [Scraping](#scraping)
- [Features](#features)
- [Acknowledgments](#acknowledgments)

## Introduction

Amazon Tracker is a comprehensive tool designed for scraping and tracking Amazon product data. The project includes scripts for scraping Amazon product details, storing the data in a MongoDB database, and a [Streamlit](https://amazontracker.streamlit.app/) web app for visualizing and analyzing the collected data.

## Scraping

The scraping process involves the following steps:

1. **Multithreaded Scraping:** Utilizes multiprocessing to scrape multiple Amazon product categories simultaneously.
2. **Data Extraction:** Extracts product details such as title, price, rating, and number of reviews from Amazon.
3. **Data Storage:** Stores scraped data in MongoDB for efficient data retrieval and analysis.

## Features

- **Streamlit Web App:** A user-friendly web app for exploring and visualizing Amazon product data.
- **Dynamic Filtering:** Allows users to filter data based on categories, dates, prices, and more.
- **Visualization:** Generates insightful plots and charts to help users understand trends and patterns.

## Streamlit

### Filters

- **Category:** Select a specific category or choose "All records" to view data across all categories.
- **Day:** Filter data by selecting a specific day or choose "All" to view aggregated data.
- **Price Range:** Use a slider to set a price range for filtering products.
- **Date Range:** Choose a date range to focus your analysis on specific time intervals.

### Metrics

- **Average Price:** Showcase the average price based on the applied filters, along with the percentage change in the last 24 hours. 💰
- **Average Rating:** Visualize the average rating based on the applied filters, along with the percentage change in the last 24 hours. ⭐
- **Average Number of Reviews:** Explore the average number of reviews considering the applied filters, along with the percentage change in the last 24 hours. 📝

### Plots

- **Price Distribution:** Interactive histogram showcasing the distribution of product prices within the selected category and date.
- **Average Price per Category:** Bar chart illustrating the average price for each category based on the applied filters.
- **Rating Distribution:** Histogram displaying the distribution of product ratings within the selected category and date.
- **Price vs. Rating Scatter Plot:** Scatter plot showcasing the relationship between product prices and ratings.
- **Reviews Over Time:** Line chart depicting the progression of reviews over time.

### Interactive Timeline

- **Average Category Metrics:** Animated timeline chart showing the average price, rating, and number of reviews for each category over time.

## Acknowledgments

This project serves as the final project for the Data Analytics Bootcamp at Ironhack. Special thanks to our dedicated professors and supportive teammates for their invaluable guidance and collaboration throughout this learning journey!




