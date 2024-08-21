# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the spacex data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # Dropdown untuk Launch Sites
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                 ],
                 value='ALL',
                 placeholder='Select a Launch Site here',
                 searchable=True
                 ),
    html.Br(),

    # Pie chart untuk menunjukkan total sukses launches
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    
    # Slider untuk memilih payload range
    dcc.RangeSlider(id='payload-slider',
                    min=min_payload, max=max_payload, step=1000,
                    marks={i: f'{i}' for i in range(int(min_payload), int(max_payload)+1000, 1000)},
                    value=[min_payload, max_payload]
                    ),
    html.Br(),
    
    # Scatter chart untuk menunjukkan korelasi antara payload dan sukses launch
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback untuk `site-dropdown` sebagai input, `success-pie-chart` sebagai output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, 
                     values='class', 
                     names='Launch Site', 
                     title='Total Successful Launches by Sites')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(filtered_df, 
                     names='class', 
                     title=f'Total Success Launches for site {entered_site}')
        return fig

# Callback untuk `site-dropdown` dan `payload-slider` sebagai input, `success-payload-scatter-chart` sebagai output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, selected_payload):
    # Filter dataframe berdasarkan nilai payload yang dipilih
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= selected_payload[0]) & 
                            (spacex_df['Payload Mass (kg)'] <= selected_payload[1])]
    if selected_site == 'ALL':
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class', 
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites'
        )
    else:
        # Filter dataframe berdasarkan situs yang dipilih
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class', 
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for site {selected_site}'
        )
    return fig

# Jalankan aplikasi
if __name__ == '__main__':
    app.run_server(port=8051)
