import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import base64
import pandas as pd

# Load the CSV files into pandas dataframes
df_jan = pd.read_csv('tuberculose_012023_total_state.csv')
df_feb = pd.read_csv('tuberculose_022023_total_state.csv')
df_mar = pd.read_csv('tuberculose_032023_total_state.csv')

combined_df = pd.read_csv('tuberculose_010203.csv')
piechar_df = pd.read_csv('tuberculose_by_region_df.csv')

# Define the Brazilian states by region
regions = {
    'North': ['Acre', 'Amapá', 'Amazonas', 'Pará', 'Rondônia', 'Roraima', 'Tocantins'],
    'Northeast': ['Alagoas', 'Bahia', 'Ceará', 'Maranhão', 'Paraíba', 'Pernambuco', 'Piauí', 'Rio Grande do Norte', 'Sergipe'],
    'Central-West': ['Distrito Federal', 'Goiás', 'Mato Grosso', 'Mato Grosso do Sul'],
    'Southeast': ['Espírito Santo', 'Minas Gerais', 'Rio de Janeiro', 'São Paulo'],
    'South': ['Paraná', 'Rio Grande do Sul', 'Santa Catarina']
}

# Initialize the Dash app
app = dash.Dash(__name__)

# Get unique states from the DataFrame (excluding 'Code', 'Description', 'Total', and 'Month' columns)
state_options = [{'label': state, 'value': state} for state in combined_df.columns[3:-1]]  # Adjust index as needed
region_options = [{'label': region, 'value': region} for region in ['North', 'Northeast', 'Central-West', 'Southeast', 'South']]

app.layout = html.Div([
    # Main container div with flex display and gray background
    html.Div([
        # Sidebar for dropdowns with light blue background
        html.Div([
            html.H2("Select from Data"),
            html.H3("State"),
            dcc.Dropdown(
                id='state-dropdown',
                options=state_options,
                value=state_options[0]['value']
            ),
            html.H3("Region"),
            dcc.Dropdown(
                id='region-dropdown',
                options=region_options,
                value=region_options[0]['value']
            ),
            html.H3("Month"),
            dcc.Dropdown(
                id='month-dropdown',
                options=[
                    {'label': 'January', 'value': 'January'},
                    {'label': 'February', 'value': 'February'},
                    {'label': 'March', 'value': 'March'}
                ],
                value='January'  # Default value
            ),     
        ])# Closing the sidebar div
    ], className='sidebar'),  # Closing the container div for the sidebar
    
    # Main content area for charts and tables
    html.Div([
        html.H1("Monthly and State Data Dashboard"),
        html.H2("Total Procedures Chart per Month (Select Month)"),
        
        # Container for the first chart and its title
        html.Div([
            dcc.Graph(id='total-procedures-per-state-chart'),
            ]),  # Closing the div for the first chart and title
        
        html.H2("Map of Data of each State (Select Month)"),
        # Container for the map
        html.Div([
            html.Div([html.Img(id='procedures-map', src=''),
                      ], id="total_procedures_map"),  # Closing the div for the map
            html.Div(id='table-container')
            ], id='table_map'),
        
        
        # Container with the three charts
        html.Div([
            html.H2("Total Procedures per Month by Region (Select Month and Region)"),
            html.Div([
                dcc.Graph(id='state-distribution-chart-pie'),
                dcc.Graph(id='state-distribution-chart-bar'),
                dcc.Graph(id='procedures-pie-chart'),
            ], id="state-distribution-chart")
            ]),  # Closing the div for the three charts
        
        # Container with the table of procedures
        html.H2("Table of Data of each State (Select State and Month)"),
        html.Div([    
            html.Div(dash_table.DataTable(id='data-table', page_size=10),
                id="data_table") # Closing for the div for the table
        ], className='data_state'),  # Closing the div for the table 
        
        # footer
        html.H2("Created by @diguitarrista")
        
    ], className='main-content'),  # Closing the main content area div
], className='app-background')  # Closing the app layout div

# Callback to update table based on dropdowns
@app.callback(
    Output('data-table', 'data'),
    [Input('month-dropdown', 'value'),
     Input('state-dropdown', 'value')]
)

def update_table(selected_month, selected_state):
    # Filter based on selected month first
    filtered_df = combined_df[combined_df['Month'] == selected_month]
    
    # Check if, after filtering by month, all values for the selected state are zero
    if filtered_df[selected_state].eq(0).all():
        # Create a DataFrame with the same structure but with placeholder/default values
        placeholder_df = pd.DataFrame([{'Code': 'No Data', 'Description': 'No Data', selected_state: 0, 'Month': selected_month}])
        return placeholder_df.to_dict('records')

    # Further filter to exclude rows where the state's value is 0, if necessary
    filtered_df = filtered_df[filtered_df[selected_state] != 0]

    # Adjust DataFrame to show only relevant columns
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

@app.callback(
    Output('table-container', 'children'),
    [Input('month-dropdown', 'value')]
)
def update_table_total(selected_month):
    if selected_month == 'January':
        df_to_display = df_jan
    elif selected_month == 'February':
        df_to_display = df_feb
    elif selected_month == 'March':
        df_to_display = df_mar

    return dash_table.DataTable(
        data=df_to_display.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df_to_display.columns]
    )

@app.callback(
    Output('procedures-pie-chart', 'figure'),
    [Input('month-dropdown', 'value')]
)
def update_pie_chart(selected_month):
    filtered_df = piechar_df[piechar_df['Month'] == selected_month]
    # Assuming the data aggregation is needed per region for the pie chart
    procedures_per_region = filtered_df.iloc[:, 3:].sum()
    fig = px.pie(procedures_per_region, values=procedures_per_region.values, names=procedures_per_region.index, title=f"Total Procedures in {selected_month}")
        
    return fig

@app.callback(
    [Output('state-distribution-chart-pie', 'figure'),
     Output('state-distribution-chart-bar', 'figure')],
    [Input('region-dropdown', 'value'),
     Input('month-dropdown', 'value')]
)
def update_pie_bar_chart_region(selected_region, selected_month):
    # Filter the data for the selected region and month
    filtered_data = combined_df[combined_df['Month'] == selected_month][regions[selected_region]].sum().reset_index()
    filtered_data.columns = ['State', 'Count']
    # Create a pie chart
    pie_fig = px.pie(filtered_data, values='Count', names='State', title=f'Distribution in {selected_region} for {selected_month}')
    
    # Create a bar chart
    bar_fig = px.bar(filtered_data, x='State', y='Count', title=f'Distribution in {selected_region} for {selected_month}')
    
    return pie_fig, bar_fig

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