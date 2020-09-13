import pandas as pd     #(version 1.0.0)
import plotly           #(version 4.5.4) pip install plotly==4.5.4
import plotly.express as px
import json

import dash             #(version 1.9.1) pip install dash==1.9.1
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State

app = dash.Dash(__name__)

df_data = pd.read_csv("newimn.csv")
df1=pd.read_csv("in_avg_mal.csv")
dff = df_data.groupby('State/UT', as_index=False)[['Underweight','Stunting ','Wasting ']].sum()
print (dff[:5])
df2 = pd.read_csv('All_Ymalnutri.csv')

print("Geographical Information\n")
with open('states_new_1.json') as f:
    data_map = json.load(f)

app.layout = html.Div([
    html.Div([

    html.H1("Malnutrition in India", style={'text-align': 'center'}),

    dcc.Dropdown(id="slct_year",
                 options=[
                     {"label": "1992", "value": 1992},
                     {"label": "2005", "value": 2005},
                     {"label": "2015", "value": 2015}],
                 multi=False,
                 value=2015,
                 style={'width': "40%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my_bee_map', figure={})

    ],),
    html.Div([
        dash_table.DataTable(
            id='datatable_id',
            data=dff.to_dict('records'),
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": False} for i in dff.columns
            ],
            editable=False,
          #  filter_action="native",
            sort_action="native",
            sort_mode="multi",
            row_selectable="multi",
            column_selectable="single",
            selected_columns=[],
            row_deletable=False,
            selected_rows=[],
            page_action="native",
            page_current= 0,
            page_size= 6,
            # page_action='none',
            # style_cell={
            # 'whiteSpace': 'normal'
            # },
            # fixed_rows={ 'headers': True, 'data': 0 },
            # virtualization=False,
            style_cell_conditional=[
                {'if': {'column_id': 'State/UT'},
                 'width': '100%', 'textAlign': 'left'},
                {'if': {'column_id': 'Underweight'},
                 'width': '25%', 'textAlign': 'left','display':'none'},
                {'if': {'column_id': 'Stunting '},
                 'width': '23%', 'textAlign': 'left','display':'none'},
                {'if': {'column_id': 'Wasting '},
                 'width': '22%', 'textAlign': 'left','display':'none'},
            ],
        ),
    ],className='row'),

    html.Div([
        html.Div([
            dcc.Dropdown(id='linedropdown',
                options=[
                         {'label': 'Underweight', 'value': 'Underweight'},
                         {'label': 'Stunting', 'value': 'Stunting '},
                         {'label': 'Wasting', 'value': 'Wasting '}
                ],
                value='Underweight',
                multi=False,
                clearable=False
            ),
        ],style={'width': '45%', 'margin-top':'50px', 'display': 'inline-block'}),

        html.Div([
        dcc.Dropdown(id='piedropdown',
            options=[
                     {'label': 'Underweight', 'value': 'Underweight'},
                     {'label': 'Stunting', 'value': 'Stunting '},
                     {'label': 'Wasting', 'value': 'Wasting '}
            ],
            value='Underweight',
            multi=False,
            clearable=False
        ),
        ],style={'width': '45%', 'margin-top':'-41px','float': 'right', 'display': 'block'})

    ],'''style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'}'''),

    html.Div([
        html.Div([
            dcc.Graph(id='linechart'),
        ],style={'width': '49%', 'margin-top':'0px', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='piechart'),
        ],style={'width': '49%','margin-top':'15px','float': 'right', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='barchart'),
        ],style={'width': '49%', 'margin-top':'0px', 'display': 'inline-block'})

    ],className='row'),


])


@app.callback(
    [Output('piechart', 'figure'),
     Output('linechart', 'figure'),
     Output('barchart', 'figure'),
     Output(component_id='output_container', component_property='children'),
     Output(component_id='my_bee_map', component_property='figure')],
    [Input('datatable_id', 'selected_rows'),
     Input('piedropdown', 'value'),
     Input('linedropdown', 'value'),
     Input(component_id='slct_year', component_property='value')]
)
def update_data(chosen_rows,piedropval,linedropval,option_slctd):
    if len(chosen_rows)==0:
        df_filterd = dff[dff['State/UT'].isin(['Andhra Pradesh','Kerala','Tamil Nadu','Telangana'])]
    else:
        print(chosen_rows)
        df_filterd = dff[dff.index.isin(chosen_rows)]

    pie_chart=px.pie(
            data_frame=df_filterd,
            names='State/UT',
            values=piedropval,
            hole=.3,
            labels={'State/UT':'States'},
            )
   
    #extract list of chosen countries
    list_chosen_countries=df_filterd['State/UT'].tolist()
    #filter original df according to chosen countries
    #because original df has all the complete dates
    df_line = df_data[df_data['State/UT'].isin(list_chosen_countries)]

    line_chart = px.line(
            data_frame=df_line,
            x='Year',
            y=linedropval,
            color='State/UT',
            labels={'State/UT':'States', 'Year':'Year'},
            )
    line_chart.update_layout(uirevision='foo')

    
    bar_chart = px.bar(
    data_frame=df1,
    x="Income level",
    y="Averaged Malnutrition(%)",
    color="Income level",               # differentiate color of marks
    opacity=0.9,                  # set opacity of markers (from 0 to 1)
    orientation="v",              # 'v','h': orientation of the marks
    barmode='relative',
     labels={"Averaged Malnutrition(%)":"Malnutrition Averaged",
    "Income level":"Income level"},           # map the labels of the figure
    title='Malnutrition based on Income level', # figure title
    width=700,                   # figure width in pixels
    height=600,                   # figure height in pixels
    template='gridon',
    )
    container = "The year chosen by user is: {}".format(option_slctd)

    dff1 = df2.copy()
    dff1 = dff1[dff1["Year"] == option_slctd]
    

    # Plotly Express
    colour = plotly.colors.sequential.deep
    colour_final = colour[1:100]
    fig = px.choropleth_mapbox(dff1, geojson=data_map, locations='id',
                           color='Malnutrition',
                           color_continuous_scale=colour_final,
                           zoom=3, 
                           opacity=0.5,
                           mapbox_style='white-bg',
                          # width=1000,                   # figure width in pixels
                           height=700,       
                           labels={'demand':'demand of crop'},
                           template='plotly_white',
                           center={'lat':21,'lon':79}
                          )
    pie_chart.update_layout(
            title={
            'text': "Percentage of {}".format(piedropval)+" among States",
            'y':0.98,
            'x':0.47,
            'xanchor': 'center',
            'yanchor': 'top'})
    line_chart.update_layout(
            title={
            'text': "Year wise Trends of {}".format(piedropval),
            'y':0.95,
            'x':0.47,
            'xanchor': 'center',
            'yanchor': 'top'})
    return (pie_chart,line_chart, bar_chart,container, fig)

#------------------------------------------------------------------


'''@app.callback(
    Output('datatable_id', 'style_data_conditional'),
    [Input('datatable_id', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': {'column_id': i},
        'background_color': '#D2F3FF'
    } for i in selected_columns]'''


#------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=False)
