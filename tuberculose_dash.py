import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import base64
import pandas as pd

# Color pallet
dark_blue_colors = ['#08306b', '#08519c', '#2171b5', '#4292c6', '#6baed6', '#9ecae1']

# Load the CSV files into pandas dataframes
df_jan = pd.read_csv('csv/tuberculose_012023_cent.csv')
df_feb = pd.read_csv('csv/tuberculose_022023_cent.csv')
df_mar = pd.read_csv('csv/tuberculose_032023_cent.csv')

combined_df = pd.read_csv('csv/tuberculose_010203.csv')
combined_df_cent = pd.read_csv('csv/tuberculose_010203.csv')
piechar_df = pd.read_csv('csv/tuberculose_by_region_df.csv')
piechar_df_region = pd.read_csv('csv/tuberculose_region_010203_cent.csv')

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
        html.H2("Most States with Procedures per 100 k"),
        
        # Container for the first chart and its title
        html.Div([
            dcc.Graph(id='total-procedures-per-state-chart'),
            ]),  # Closing the div for the first chart and title
        
        html.H2("Map of Data of each State (Select Month and State)"),
        # Container for the map
        html.Div([
            html.Div([html.Img(id='procedures-map', src=''),
                      ], id="total_procedures_map"),  # Closing the div for the map
            html.Div(dcc.Graph(id='regionpercent-chart-pie'))
            ], id='table_map'),
        
        html.Div(id='table-map'),
        
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

# TABLE AT THE END
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

# FIRST CHART
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

# MAP
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

# TABLE BY THE MAP
@app.callback(
    Output('table-map', 'children'),
    [Input('month-dropdown', 'value'),
     Input('state-dropdown', 'value')]
)
def update_table_total(selected_month, selected_state):
    if selected_month == 'January':
        df_to_display = df_jan
    elif selected_month == 'February':
        df_to_display = df_feb
    elif selected_month == 'March':
        df_to_display = df_mar

    # Filter DataFrame based on selected state
    if selected_state is not None:
        df_to_display = df_to_display[df_to_display['State'] == selected_state]

    # Select only the desired columns
    df_selected_columns = df_to_display[['State', 'Total Frequency per 100 thousand inhabitants']]
    df_selected_columns = df_selected_columns[['State', 'Total Frequency per 100 thousand inhabitants']].rename(columns={'Total Frequency per 100 thousand inhabitants': 'Frequency 100 k inhabitants'})

    # Convert DataFrame to dictionary
    data = df_selected_columns.to_dict('records')
    
    # Define columns for DataTable
    columns = [{'name': col, 'id': col} for col in df_selected_columns.columns]
    
    # Create DataTable
    table = dash_table.DataTable(data=data, columns=columns)
    
    return table


# PIE CHART BY THE MAP
@app.callback(
    Output('regionpercent-chart-pie', 'figure'),
    [Input('month-dropdown', 'value')]
)
def char_region_(selected_month):
    filtered_df = piechar_df_region
    column_name = f"{selected_month} per 100k"  # This constructs the column name based on the selected month
    
    # Now use this column_name to specify the values for the pie chart
    fig = px.pie(filtered_df, names='Region', 
                 values=column_name,
                 color_discrete_sequence=dark_blue_colors,
                 title=f'Procedures per 100k Habitants by Region for {selected_month}',
                 )
    return fig

# CHARTS
@app.callback(
    Output('procedures-pie-chart', 'figure'),
    [Input('month-dropdown', 'value')]
)
def update_pie_chart(selected_month):
    filtered_df = piechar_df[piechar_df['Month'] == selected_month]
    # Assuming the data aggregation is needed per region for the pie chart
    procedures_per_region = filtered_df.iloc[:, 3:].sum()
    fig = px.pie(procedures_per_region, values=procedures_per_region.values, 
                 color_discrete_sequence=dark_blue_colors,
                 names=procedures_per_region.index, title=f"Total Procedures in {selected_month}")
        
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
    # Create a pie chart with a blue color scale
    pie_fig = px.pie(filtered_data, values='Count', names='State',
                 title=f'Distribution in {selected_region} for {selected_month}',
                 color_discrete_sequence=dark_blue_colors)
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