import plotly
import plotly.express as px
import plotly.graph_objects as go

import dash
import dash_table
import dash_core_components as dcc  
import dash_html_components as html
from dash.dependencies import Input,Output,State
from dash.exceptions import PreventUpdate

import os
import json

import urllib
import requests
import pandas as pd
import numpy as np
from flask import Flask, request, json, jsonify, make_response
from watson_machine_learning_client import WatsonMachineLearningAPIClient

import encodingdata

total_cropyield=[]
total_demand=[]
iyear_org=0

# app creation
app = dash.Dash(__name__,suppress_callback_exceptions=True)
server = app.server

# data for Map
with open('states_new.json') as f:
    data_map = json.load(f)

# data for malnutrition
df_data = pd.read_csv("newimn.csv")
df1=pd.read_csv("in_avg_mal.csv")
dff = df_data.groupby('State/UT', as_index=False)[['Underweight','Stunting ','Wasting ']].sum()
print (dff[:5])
df2 = pd.read_csv('All_Ymalnutri.csv')

fig1 = go.Figure()



app.layout = html.Div([
    html.Div(id='page-content',children=[
    html.Div([html.H1("Demand and Supply Predictor", style={'text-align':'center'})]),

    html.Div([
        dcc.Location(id='url',refresh=False),
        html.Br(),
        dcc.Link('Go to Malnutrition',href='/page2'),
]),
html.Div([
    dcc.Dropdown(id='istate',
    options=[
        {'label':'Andhra Pradesh','value':'Andhra Pradesh'},
        {'label':'Arunachal Pradesh','value':'Arunachal Pradesh'},
        {'label':'Assam','value':'Assam'},
        {'label':'Bihar','value':'Bihar'},
        {'label':'Chhattisgarh','value':'Chhattisgarh'},
        {'label':'Goa','value':'Goa'},
        {'label':'Gujarat','value':'Gujarat'},
        {'label':'Haryana','value':'Haryana'},
        {'label':'Himachal Pradesh','value':'Himachal Pradesh'},
        {'label':'Jharkhand','value':'Jharkhand'},
        {'label':'Karnataka','value':'Karnataka'},
        {'label':'Kerala','value':'Kerala'},
        {'label':'Madhya Pradesh','value':'Madhya Pradesh'},
        {'label':'Maharastra','value':'Maharastra'},
        {'label':'Manipur','value':'Manipur'},
        {'label':'Meghalaya','value':'Meghalaya'},
        {'label':'Mizoram','value':'Mizoram'},
        {'label':'Nagaland','value':'Nagaland'},
        {'label':'Odisha','value':'Odisha'},
        {'label':'Punjab','value':'Punjab'},
        {'label':'Rajasthan','value':'Rajasthan'},
        {'label':'Sikkim','value':'Sikkim'},
        {'label':'Tamil Nadu','value':'Tamil Nadu'},
        {'label':'Tripura','value':'Tripura'},
        {'label':'Uttar Pradesh','value':'Uttar Pradesh'},
        {'label':'Uttarakhand','value':'Uttarakhand'},
        {'label':'West Bengal','value':'West Bengal'},
        {'label':'Jammu and Kashmir','value':'Jammu and Kashmir'},
        {'label':'Chandigarh','value':'Chandigarh'},
        {'label':'Delhi','value':'Delhi'},
        {'label':'Dadra and Nagra Haveli','value':'Dadra and Nagra Haveli'},
        {'label':'Puducherry','value':'Puducherry'},
        {'label':'Andaman and Nicobar Islands','value':'Andaman and Nicobar Islands'}
    ],
    multi=False,
    placeholder='Select a State',
    style={'width':'40%'}
),
html.Br(),
dcc.Dropdown(id='icrop',
    options=[
        {'label':'Rice','value':'Rice'},
        {'label':'Wheat','value':'Wheat'},
        {'label':'Jowar','value':'Jowar'},
        {'label':'Bajra','value':'Bajra'},
        {'label':'Potato','value':'Potato'},
        {'label':'Tomato','value':'Tomato'},
        {'label':'Onion','value':'Onion'}
    ],
    multi=False,
    placeholder='Select a Crop',
    style={'width':'40%'}
),
html.Br(),
dcc.Input(id="iyear",
    placeholder='Enter the Year',
    type='number',
    inputMode='numeric',
    value='',
    required=True
),
html.Br(),
dcc.Input(
    id='iarea',
    type='number',
    placeholder='Enter the expected yield area',
),
html.Br(),
html.Button(id='predict',n_clicks=0,children='Predict'),
]),
html.Br(),
html.Br(),
html.Div([
html.H2('Demand-Supply India Map'),
dcc.Graph(id='country_map'),
],style={'float':'left','height':'100%','width':'50%'}),

html.Div([
    html.H2('Demand-Supply Gap'),
    dcc.Graph(id='demandsupply')
],style={'float':'right','height':'100%','width':'50%'}),
html.Br(),
html.Br(),
html.Div([
    dcc.Graph(id='foodinsecurity')
],style={'float':'left','height':'100%','width':'50%'}),
html.Div([
    html.H2('Model Suggestion'),
    html.Div([
        html.Div(id='riskoutput')
    ])
],style={'float':'right','height':'100%','width':'50%'}),

])])

# Malnutrition layout
mal_nutrition = html.Div([
    html.Div(id='page-content-back',children=[
    html.Div([

    html.H1("Malnutrition in India", style={'text-align': 'center'}),

    html.Div([
        dcc.Location(id='url_back',refresh=False),
        html.Br(),
        dcc.Link('Go to Home',href='/page1'),
]),

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


])])



# METHODS

def demand_model_access(access_token,n_clicks,istate_val,iyear_val,icrop_val,state_boundary):
    boundary_demand = []
    demand_predictions = []
    model_url = "https://eu-gb.ml.cloud.ibm.com/v3/wml_instances/0ca61b2e-96dc-4749-9cce-9d719e87e7f2/deployments/afc09fac-32dd-4ec5-972a-e28ec48c19e8/online"
    instance_id = "0ca61b2e-96dc-4749-9cce-9d719e87e7f2"
    call_headers = {'Content-Type': 'application/json',"Authorization":"Bearer "+access_token,"ML-Instance-ID":instance_id}
    for state in state_boundary:
        encoded_demand_data = encodingdata.encode_demand_data(n_clicks,state,iyear_val,icrop_val)
        print(encoded_demand_data)
        dstate = float(encoded_demand_data[0][0])
        dyear = float(encoded_demand_data[0][1])
        dcrop = float(encoded_demand_data[0][2])

        demand_payload = {"fields":["State","Year","Crop"],"values":[[dstate,dyear,dcrop]]}

        result = requests.post(url=model_url,json=demand_payload,headers=call_headers)

        result_json = json.loads(result.text)

        boundary_demand.append(result_json['values'][0][0][0])

    for i in range(0,3):
        encoded_demand_data = encodingdata.encode_demand_data(n_clicks,istate_val,iyear_val,icrop_val)
        print(encoded_demand_data)
        dstate = float(encoded_demand_data[0][0])
        dyear = float(encoded_demand_data[0][1])
        dcrop = float(encoded_demand_data[0][2])

        demand_payload = {"fields":["State","Year","Crop"],"values":[[dstate,dyear,dcrop]]}

        result = requests.post(url=model_url,json=demand_payload,headers=call_headers)

        result_json = json.loads(result.text)

        demand_predictions.append(result_json['values'][0][0][0])

        iyear_val = iyear_val+1
    
    return demand_predictions,boundary_demand



def demand_access_token_generator():
    api_key = "X6Ynj6iHphsCxGSI3khvWWDSt5g5gOcCe92ckMzlFXV4"
    header = {"content-type":"application/x-www-form-urlencoded"}
    post_param = urllib.parse.urlencode({
        "apikey":api_key,
        "grant_type":"urn:ibm:params:oauth:grant-type:apikey"
    }).encode("UTF-8")
    url = "https://iam.cloud.ibm.com/identity/token"
    response = requests.post(url,post_param,header)
    #print(response.text)
    return json.loads(response.text)

def crop_model_access(access_token,n_clicks,istate_val,iyear_val,icrop_val,iarea_val,state_boundary):
    crop_predictions = []
    boundary_supply = []
    model_url = "https://us-south.ml.cloud.ibm.com/v3/wml_instances/1e6bd516-623a-4e64-bdb6-1ea860a312ca/deployments/96111954-7717-4086-968d-5e26ddaf9854/online"
    instance_id = "1e6bd516-623a-4e64-bdb6-1ea860a312ca"
    call_headers = {'Content-Type': 'application/json',"Authorization":"Bearer "+access_token,"ML-Instance-ID":instance_id}
    for state in state_boundary:
        encoded_crop_data = encodingdata.encode_crop_data(n_clicks,state,iyear_val,icrop_val,iarea_val)
        cstate = float(encoded_crop_data[0][0])
        cyear = float(encoded_crop_data[0][1])
        ccrop = float(encoded_crop_data[0][2])
        carea = float(encoded_crop_data[0][3])

        crop_payload = {"fields":["State","Year","Crop","Area"],"values":[[cstate,cyear,ccrop,carea]]}

        result = requests.post(model_url,json=crop_payload,headers=call_headers)

        result_json = json.loads(result.text)

        boundary_supply.append(result_json['values'][0][0][0])

    for i in range(0,3):
        encoded_crop_data = encodingdata.encode_crop_data(n_clicks,istate_val,iyear_val,icrop_val,iarea_val)
        cstate = float(encoded_crop_data[0][0])
        cyear = float(encoded_crop_data[0][1])
        ccrop = float(encoded_crop_data[0][2])
        carea = float(encoded_crop_data[0][3])

        crop_payload = {"fields":["State","Year","Crop","Area"],"values":[[cstate,cyear,ccrop,carea]]}

        result = requests.post(model_url,json=crop_payload,headers=call_headers)

        result_json = json.loads(result.text)

        crop_predictions.append(result_json['values'][0][0][0])

        iyear_val = iyear_val + 1

    return crop_predictions,boundary_supply


def crop_access_token_generator():
    api_key = "wVZbrwyrMjgglhJWpGclhfKBfroTRfChiwenP8frQX2e"
    header = {"content-type":"application/x-www-form-urlencoded"}
    post_param = urllib.parse.urlencode({
        "apikey":api_key,
        "grant_type":"urn:ibm:params:oauth:grant-type:apikey"
    }).encode("UTF-8")
    url = "https://iam.cloud.ibm.com/identity/token"
    response = requests.post(url,post_param,header)
    #print(response.text)
    return json.loads(response.text)

def defining_stateboundaries():
        indian_states = ['Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharastra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Jammu and Kashmir', 'Chandigarh', 'Delhi', 'Dadra and Nagar Haveli', 'Puducherry', 'Andaman and Nicobar Islands']
        state_boundaries = dict.fromkeys(indian_states)

        state_boundaries['Kerala'] = ['Tamil Nadu','Karnataka','Andhra Pradesh','Goa','Maharastra']
        state_boundaries['Tamil Nadu'] = ['Kerala','Karnataka','Andhra Pradesh','Goa','Maharastra']
        state_boundaries['Karnataka'] = ['Tamil Nadu','Kerala','Goa','Andhra Pradesh','Maharastra']
        state_boundaries['Maharastra'] = ['Karnataka','Madhya Pradesh','Goa','Andhra Pradesh','Chhattisgarh','Gujarat']
        state_boundaries['Goa'] = ['Karnataka','Maharastra','Kerala','Andhra Pradesh','Tamil Nadu']
        state_boundaries['Andhra Pradesh'] = ['Karnataka','Maharastra','Tamil Nadu','Odisha','Chhattisgarh']
        state_boundaries['Gujarat'] = ['Rajasthan','Madhya Pradesh','Maharastra','Uttar Pradesh','Haryana']
        state_boundaries['Madhya Pradesh'] = ['Maharastra','Rajasthan','Uttar Pradesh','Chhattisgarh','Gujarat']
        state_boundaries['Chhattisgarh'] = ['Odisha','Jharkhand','Madhya Pradesh','Maharastra','Uttar Pradesh']
        state_boundaries['Odisha'] = ['Chhattisgarh','Jharkhand','West Bengal','Andhra Pradesh','Maharastra']
        state_boundaries['Rajasthan'] = ['Gujarat','Madhya Pradesh','Uttar Pradesh','Haryana','Punjab']
        state_boundaries['Uttar Pradesh'] = ['Madhya Pradesh','Rajasthan','Bihar','Haryana','Uttarakhand','Chhattisgarh']
        state_boundaries['Bihar'] = ['Uttar Pradesh','Jharkhand','Sikkim','Madhya Pradesh','West Bengal','Chhattisgarh']
        state_boundaries['Jharkhand'] = ['Bihar','West Bengal','Odisha','Chhattisgarh','Uttar Pradesh']
        state_boundaries['West Bengal'] = ['Jharkhand','Odisha','Bihar','Sikkim','Assam']
        state_boundaries['Haryana'] = ['Punjab','Rajasthan','Uttar Pradesh','Uttarakhand','Himachal Pradesh']
        state_boundaries['Punjab'] = ['Haryana','Rajasthan','Himachal Pradesh','Jammu and Kashmir','Uttarakhand','Uttar Pradesh']
        state_boundaries['Himachal Pradesh'] = ['Punjab','Uttarakhand','Jammu and Kashmir','Haryana','Uttar Pradesh']
        state_boundaries['Jammu and Kashmir'] = ['Himachal Pradesh','Punjab','Uttarakhand','Haryana','Uttar Pradesh','Rajasthan']
        state_boundaries['Uttarakhand'] = ['Uttar Pradesh','Himachal Pradesh','Haryana','Punjab','Rajasthan','Jammu and Kashmir']
        state_boundaries['Sikkim'] = ['West Bengal','Assam','Bihar','Meghalaya','Jharkhand']
        state_boundaries['Assam'] = ['Meghalaya','Nagaland','Arunachal Pradesh','West Bengal','Manipur','Mizoram']
        state_boundaries['Arunachal Pradesh'] = ['Assam','Nagaland','Manipur','Meghalaya','Mizoram','Tripura']
        state_boundaries['Meghalaya'] = ['Assam','West Bengal','Tripura','Mizoram','Manipur','Nagaland']
        state_boundaries['Nagaland'] = ['Assam','Manipur','Arunachal Pradesh','Meghalaya','Mizoram']
        state_boundaries['Manipur'] = ['Assam','Nagaland','Mizoram','Meghalaya','Tripura']
        state_boundaries['Mizoram'] = ['Manipur','Tripura','Assam','Meghalaya','Nagaland']
        state_boundaries['Tripura'] = ['Mizoram','Assam','Manipur','Meghalaya','Nagaland']
        state_boundaries['Delhi'] = ['Uttar Pradesh','Haryana','Rajasthan','Madhya Pradesh','Punjab']
        state_boundaries['Dadra and Nagar Haveli'] = ['Gujarat','Maharastra','Madhya Pradesh','Rajasthan','Goa']
        state_boundaries['Puducherry'] = ['Tamil Nadu','Andhra Pradesh','Kerala','Karnataka','Odisha']
        state_boundaries['Andaman and Nicobar Islands'] = ['Andhra Pradesh','Tamil Nadu','Odisha','Kerala','West Bengal']
        state_boundaries['Chandigarh'] = ['Punjab','Haryana','Himachal Pradesh','Uttarakhand','Uttar Pradesh']

        return indian_states,state_boundaries


#page 1 - Home page
@app.callback(
    
    [Output(component_id='country_map',component_property='figure'),
    Output('demandsupply','figure'),
    Output(component_id='foodinsecurity',component_property='figure'),
    Output('riskoutput','children')],
    [Input(component_id='predict',component_property='n_clicks')],
    [State(component_id='istate',component_property='value'),
     State(component_id='icrop',component_property='value'),
     State(component_id='iyear',component_property='value'),
     State(component_id='iarea',component_property='value')]
)

def update_output(n_clicks,istate_val,icrop_val,iyear_val,iarea_val):
    global total_cropyield,total_demand,iyear_org
    if (istate_val is None) or (icrop_val is None) or (iyear_val is None):
        raise PreventUpdate
    else:
        print(istate_val)
        print(type(istate_val))
        print(icrop_val)
        print(type(icrop_val))
        print(iyear_val)
        print(type(iyear_val))
        print(iarea_val)
        print(type(iarea_val))

        iyear_org  = iyear_val

        

        # boundaries
        states,state_boundaries = defining_stateboundaries()
        state_list = state_boundaries[istate_val]


        # Demand Model
        print("In Demand Model")
        access_token_result = demand_access_token_generator()
        access_token = access_token_result['access_token']
        model_output,boundary_output = demand_model_access(access_token,n_clicks,istate_val,iyear_val,icrop_val,state_list)
        #demand_prediction = model_output['values'][0][0]
        total_boundary_demand = []
        total_demand = []
        for i in range(0,3):
            val = np.array(model_output[i])
            temp = encodingdata.decode_demand_data(val)
            demand = temp[0][0]
            total_demand.append(demand)
            print("Demand Prediction for Year {} is {}".format(i,demand))
        for i in range(0,len(boundary_output)):
            val = np.array(boundary_output[i])
            temp = encodingdata.decode_demand_data(val)
            demand = temp[0][0]
            total_boundary_demand.append(demand)
            print("{} Demand Prediction for Year {} is {}".format(state_list[i],i,demand))

    
        #Crop Model
        print("In Crop Model")
        iyear_val = iyear_org
        access_token_result = crop_access_token_generator()
        access_token = access_token_result['access_token']
        model_output1,boundary_output1 = crop_model_access(access_token,n_clicks,istate_val,iyear_val,icrop_val,iarea_val,state_list)
        total_cropyield = []
        total_boundary_supply = []
        for i in range(0,3):
            val = np.array(model_output1[i])
            temp = encodingdata.decode_crop_data(val)
            cropyield = temp[0][0]
            total_cropyield.append(cropyield)
            print("Crop Yield Prediction for Year {} is {}".format(i,cropyield))
        for i in range(0,len(boundary_output1)):
            val = np.array(boundary_output1[i])
            temp = encodingdata.decode_crop_data(val)
            cropyield = temp[0][0]
            total_boundary_supply.append(cropyield)
            print("{} Crop Yield Prediction for Year {} is {}".format(state_list[i],i,cropyield))
        
        colour = plotly.colors.qualitative.Set1
        red = colour[0]
        green = colour[2]
        yellow = colour[5]
        gauge_value = 0
        suggestion = 5

        diff = total_cropyield[0] - total_demand[0]

        if (diff > 1000):
            colour_final = yellow
            gauge_value = 0
            suggestion = 1
        elif (diff < 0):
            colour_final = red
            gauge_value = 100
            suggestion = -1
        elif(0<diff<1000):
            colour_final = green
            gauge_value = 50
            suggestion = 0
        colour_final = [[1,green],[1,yellow],[1,red]]

        boundary_gap = [0] * len(total_boundary_demand)
        # calculating the boundary states Demand and Supply Gaps
        for i in range(0,len(total_boundary_demand)):
            boundary_gap[i] = total_boundary_supply[i] - total_boundary_demand[i]

        # classifying states into the import/export category for the commodity
        export_import_condition  = []
        for i in range(0,len(boundary_gap)):
            if boundary_gap[i]>1000:
                export_import_condition.append(1) 
            elif (boundary_gap[i]<0):
                export_import_condition.append(-1)
            else:
                export_import_condition.append(0)

        #states_map = states
        import_to = []
        import_from = []
        demand_list = [0] * len(states)

        if suggestion == 1:
            print("enters the I and E part")
            for i in range(0,len(export_import_condition)):
                if export_import_condition[i] == -1:
                    import_to.append(i)

            value_to_state = []
            for i in range(0,len(import_to)):
                value_to_state.append(state_list[import_to[i]])
            print("STSTAE NAMES")
            print(value_to_state)

            index_of_boundary_states =[]
            index_of_input_state = states.index(istate_val)
            for state in value_to_state:
                index_of_boundary_states.append(states.index(state))

        
            demand_list[index_of_input_state] = suggestion
            for i in range(0,len(index_of_boundary_states)):
                demand_list[index_of_boundary_states[i]] = -1
            print("\n\n DEMAND LIST")
            print(demand_list)
        elif suggestion== -1:
            print("entered the suggestion negative value")
            for i in range(0,len(export_import_condition)):
                if export_import_condition[i] == 1:
                    import_from.append(i)

            value_to_state = []
            for i in range(0,len(import_from)):
                value_to_state.append(state_list[import_from[i]])
            print("STSTAE NAMES")
            print(value_to_state)

            index_of_boundary_states =[]
            index_of_input_state = states.index(istate_val)
            for state in value_to_state:
                index_of_boundary_states.append(states.index(state))

        
            demand_list[index_of_input_state] = suggestion
            for i in range(0,len(index_of_boundary_states)):
    
                demand_list[index_of_boundary_states[i]] = 1
            print("\n\n DEMAND LIST")
            print(demand_list)


        df = pd.DataFrame({'id':states,'Demand':demand_list})


        #Map Creation
        fig = px.choropleth_mapbox(df, geojson=data_map, locations='id',
                           color='Demand',
                           color_continuous_scale=colour_final,
                           zoom=3, 
                           opacity=0.5,
                           mapbox_style='white-bg',
                           #labels={'demand':'demand of crop'},
                           template='plotly_white',
                           center={'lat':21,'lon':79}
                          )

        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

        # Graph Creation
        data1 = pd.DataFrame({'Year':[iyear_org,iyear_org+1,iyear_org+2],'Demand':[total_demand[0],total_demand[1],total_demand[2]],
                    'Supply':[total_cropyield[0],total_cropyield[1],total_cropyield[2]]})
        
        fig1 = go.Figure()

        fig1.add_trace(go.Scatter(x=data1['Year'],y=data1['Demand'],
                         mode='lines+text',name='Demand',
                         text='Demand',textposition='top center',
                         line=dict(color='firebrick')))

        fig1.add_trace(go.Scatter(x=data1['Year'],y=data1['Supply'],
                         mode='lines+text',name='Supply',
                         text='Supply',textposition='bottom center',
                         line=dict(color='royalblue')))
        for i in range(0,2):
            x_p = []
            y_p = []
            gap = []
            x_p.append(data1['Year'][i])
            x_p.append(data1['Year'][i])
            y_p.append(data1['Demand'][i])
            y_p.append(data1['Supply'][i])
            gap.append(data1['Demand'][i] - data1['Supply'][i])
            fig1.add_trace(go.Scatter(x=x_p,y=y_p,
                             mode='lines+text',name='Demand and Supply gap',
                             #text='Gap is {}'.format(gap[0]),
                             #textposition='bottom right',
                             line=dict(color='firebrick',dash='dash')))
        print('executed - 1')
        fig1.update_xaxes(type='category')
        #fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        fig1.update_layout(uirevision='foo')

        # Gauge Creation
        fig2 = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = gauge_value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Risk of Food Insecurity"},
            gauge = {'axis': {'range':[None,100]},
                            'steps' : [
                                {'range':[0,50],'color':"lightgray"},
                                {'range':[50,100],'color':"gray"}]
                                }
                            ))
        fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

        #Model Suggestion
        model_suggestion = ""
        if suggestion == 0:
            model_suggestion = "The {} Demand({}) for {} in {} is equal to Supply({}) generated within that state".format(iyear_org,total_demand[0],icrop_val,istate_val,total_cropyield[0])
        elif suggestion == -1:
            model_suggestion = "The {} Demand({}) for {} in {} is not equal to Supply({}) generated within that state.\nSo, {} needs to import {} from other states ".format(iyear_org,total_demand[0],icrop_val,istate_val,total_cropyield[0],istate_val,icrop_val)
        else:
            model_suggestion = "The {} Supply({}) for {} in {} is more than required Demand ({}) within that state.\nSo, {} can export {} to other states".format(iyear_org,total_cropyield[0],icrop_val,istate_val,total_demand[0],istate_val,icrop_val)

        # if pathname == '/page2':
        #     return [mal_nutrition]

        print("Executed")
        
        return  fig,fig1,fig2,model_suggestion

#page -1 navigate call back
@app.callback(
    [Output(component_id='page-content',component_property='children'),
    ],
    [Input(component_id='url',component_property='pathname')])
def display_page(pathname):
    if pathname == '/page2':
        return [mal_nutrition]

# page -2 Malnutrition call backs
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
    fig4 = px.choropleth_mapbox(dff1, geojson=data_map, locations='id',
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
            'text': "Year wise Trends of {}".format(linedropval),
            'y':0.95,
            'x':0.47,
            'xanchor': 'center',
            'yanchor': 'top'})
    return [pie_chart,line_chart, bar_chart,container, fig4]

# page -2 navigate to home call back
@app.callback(
    [Output(component_id='page-content-back',component_property='children')],
    [Input(component_id='url_back',component_property='pathname')]
)
def display_page_home(pathname):
    if pathname == '/page1':
        return [app.layout]




if __name__=='__main__':
    app.run_server(debug=True)