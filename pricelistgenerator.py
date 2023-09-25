import os
import pandas as pd
from datetime import timedelta

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set the working directory to the script's directory
os.chdir(script_dir)

# Load the CSV file into a DataFrame
df = pd.read_csv('pricehistory.csv')

# Convert the "Scraped Date" column to datetime
df['Scraped Date'] = pd.to_datetime(df['Scraped Date'])

# Sort the DataFrame by Product Name and Scraped Date
df = df.sort_values(by=['Product Name', 'Scraped Date'])

# Calculate the difference in days between consecutive entries for each product
df['Days Since Last Change'] = df.groupby('Product Name')['Scraped Date'].diff().dt.days

# Calculate the date for 3 months ago from the latest date in the dataset
three_months_ago = df['Scraped Date'].max() - timedelta(days=90)

# Filter the DataFrame to include only rows within the last 3 months
df = df[df['Scraped Date'] >= three_months_ago]

# Calculate a rolling mean of Price changes for all entries within the last 3 months within a product
df['Price Change Avg'] = df.groupby('Product Name')['Price'].transform(lambda x: x.expanding().mean())

# Create a mask to identify rows where the rolling mean is available
mask = df.groupby('Product Name')['Days Since Last Change'].cumcount() < 1

# Use the rolling mean where available, otherwise use the last Price
df['Determined Price'] = df.apply(lambda row: row['Price'] if mask[row.name] else row['Price Change Avg'], axis=1)

# Find the rows with the latest scraped date for each product
latest_prices = df.groupby('Product Name').apply(lambda x: x[x['Scraped Date'] == x['Scraped Date'].max()])

# Create a new DataFrame with the latest prices and stock
price_list = latest_prices[['Product Name', 'Determined Price', 'Stock', 'Brand', 'Category']].copy()

# Rename the 'Determined Price' column to 'Price'
price_list.rename(columns={'Determined Price': 'Price'}, inplace=True)

# Save the latest price list to a new CSV file
price_list.to_csv('latest_prices.csv', index=False)
