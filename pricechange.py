import pandas as pd
import numpy as np
import plotly.express as px
from openpyxl import Workbook
from openpyxl.drawing.image import Image
import dash
from dash import dcc, Input, Output
import plotly.graph_objs as go
from dash import html
import webbrowser  # Import the webbrowser module

# Load the CSV file into a DataFrame
df = pd.read_csv('pricehistory.csv')

# Convert the "Scraped Date" column to datetime
df['Scraped Date'] = pd.to_datetime(df['Scraped Date'])

# Find the rows with the latest scraped date for each product
latest_prices = df.groupby('Product Name').apply(lambda x: x[x['Scraped Date'] == x['Scraped Date'].max()])

# Create a new DataFrame with the latest prices and stock
price_list = latest_prices[['Product Name', 'Price', 'Stock', 'Brand', 'Category']]

# Initialize the Dash app
app = dash.Dash(__name__)

# Define app layout with external CSS
app.layout = html.Div([
    html.H1("Product Price History", id='app-title'),
    
    # Dropdown menu to select a product
    dcc.Dropdown(
        id='product-dropdown',
        options=[{'label': product, 'value': product} for product in price_list['Product Name']],
        value=price_list['Product Name'].iloc[0],  # Initial selected value
    ),
    
    # Interactive line chart
    dcc.Graph(id='price-history-chart'),
    dcc.Location(id='url', refresh=False)  # Location component to capture browser tab close event
])

# Define callback to update the chart based on product selection
@app.callback(
    Output('price-history-chart', 'figure'),
    [Input('product-dropdown', 'value')]
)
def update_chart(selected_product):
    filtered_df = df[df['Product Name'] == selected_product]
    
    # Convert datetime to Python datetime objects using np.array
    scraped_dates = np.array(filtered_df['Scraped Date'])
    
    # Create the line chart with markers
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=scraped_dates, y=filtered_df['Price'], mode='lines+markers'))
    
    fig.update_layout(
        title=f'Price Change Over Time for {selected_product}',
        xaxis_title='Scraped Date',
        yaxis_title='Price',
    )
    
    return fig

# Define callback to stop the server when the tab is closed
@app.callback(Output('url', 'pathname'), Input('url', 'href'))
def close_tab(href):
    if href is None:
        raise dash.exceptions.PreventUpdate
    return href

if __name__ == '__main__':
    # Open the app in the default web browser
    webbrowser.open('http://127.0.0.1:8050/')
    
    # Run the Dash app
    app.run_server(debug=True)
