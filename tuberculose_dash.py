import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import base64
import pandas as pd

combined_df = pd.read_csv('tuberculose_010203.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

# Get unique states from the DataFrame (excluding 'Code', 'Description', 'Total', and 'Month' columns)
state_options = [{'label': state, 'value': state} for state in combined_df.columns[3:-1]]  # Adjust index as needed

# App layout
app.layout = html.Div([
    html.H1("Monthly and State Data Dashboard"),
    html.H2("Select the Month"),
    dcc.Dropdown(
        id='month-dropdown',
        options=[
            {'label': 'January', 'value': 'January'},
            {'label': 'February', 'value': 'February'},
            {'label': 'March', 'value': 'March'}
        ],
        value='January'  # Default value
    ),
    html.H2("Total Procedures Chart per Month"),
    dcc.Graph(id='total-procedures-per-state-chart'),
    html.H2("Total Procedures Map per Month"),
    html.Img(id='procedures-map', src=''),
    html.H2("Select the State"),
    dcc.Dropdown(
        id='state-dropdown',
        options=state_options,
        value=state_options[0]['value']  # Default value
    ),
    html.H2("Table of Data of each State"),
    dash_table.DataTable(id='data-table', page_size=10)
    
])

# Callback to update table based on dropdowns
@app.callback(
    Output('data-table', 'data'),
    [Input('month-dropdown', 'value'),
     Input('state-dropdown', 'value')]
)

def update_table(selected_month, selected_state):
    # Filter based on selected month and state
    filtered_df = combined_df[(combined_df['Month'] == selected_month) & (combined_df[selected_state] != 0)]
    
    # Adjusting DataFrame to show only relevant columns for simplicity
    # You may customize this to display different/more columns
    filtered_df = filtered_df[['Code', 'Description', selected_state, 'Month']]

    return filtered_df.to_dict('records')

@app.callback(
    Output('total-procedures-per-state-chart', 'figure'),
    [Input('month-dropdown', 'value')]
)

def update_chart(selected_month):
    # Filter the DataFrame based on the selected month
    filtered_df = combined_df[(combined_df['Month'] == selected_month)]

    # Calculate the total procedures per state for the selected month
    state_totals = filtered_df.iloc[:, 3:-1].sum().reset_index()
    state_totals.columns = ['State', 'Total Procedures']

    # Create a bar chart
    fig = px.bar(state_totals, x='State', y='Total Procedures', title=f'Total Procedures Per State in {selected_month}')
    
    return fig

# Callback to update the image based on the selected month
@app.callback(
    Output('procedures-map', 'src'),
    [Input('month-dropdown', 'value')]
)
def update_image_src(selected_month):
    # Map the selected month to the corresponding image file
    image_files = {'January': 'Total Procedures_012023_map.png',
                   'February': 'Total Procedures_022023_map.png',
                   'March': 'Total Procedures_032023_map.png'
                   }
    
    # Encode the image for embedding
    encoded_image = base64.b64encode(open(image_files[selected_month], 'rb').read()).decode()
    src_data = f'data:image/png;base64,{encoded_image}'
    
    return src_data

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)  # Change 8051 to any available port

from flask_caching import Cache

cache = Cache(app.server, config={
    'CACHE_TYPE': 'null',
    'CACHE_NO_NULL_WARNING': True,
})

app.config.suppress_callback_exceptions = True

@app.server.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response