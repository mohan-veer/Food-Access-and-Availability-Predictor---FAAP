import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler

y_scale_crop=None 
y_scale=None

def encode_demand_data(n_clicks,state_val,year_val,crop_val):
    global y_scale

    print(state_val)
    print(year_val)
    print(crop_val)
    data = pd.read_csv("Demand.csv")
    original_data = data.copy()
    le = LabelEncoder()

    data.State = le.fit_transform(data.State)
    data.Crop = le.fit_transform(data.Crop)

    states=[]
    index_state={}
    index_crop={}

    states=original_data["State"].unique()   

    index_state = dict.fromkeys(states, None) 
     
    for state in index_state.keys():
        location = original_data[original_data['State']==state].index.values
        index_state[state] = location[0]


    # state ='Tamil Nadu'  
    # s = data.State[index_state[state]]
    # print("value of tamil nadu")
    # print(s)
    
    crops=original_data["Crop"].unique()
    
    index_crop = dict.fromkeys(crops, None)

    for crop in index_crop.keys():
        location = original_data[original_data['Crop']==crop].index.values
        index_crop[crop] = location[0]

    # print("TESTING THE ENCODING -2")
    # crop='Jowar'
    # cr= data.Crop[index_crop[crop]]
    # print("testing the value of jowar")
    # print(cr)

    x_scale = MinMaxScaler(feature_range=(0,1))
    y_scale = MinMaxScaler(feature_range=(0,1))

    y = data['Demand'].values

    data = data.drop(['Demand'],axis=1)
    X = data.values

    X_scaled = x_scale.fit_transform(X)
    y_scaled = y_scale.fit_transform(y.reshape(-1,1))
    #print("Scaled data\n")
    # print(X_scaled)
    # print(y_scaled)

    state_label = data.State[index_state[state_val]]
    crop_label = data.Crop[index_crop[crop_val]]
    print("Printing labels")
    print(state_label)
    print(crop_label)
    values = np.array([state_label,year_val,crop_label])
    input_values = x_scale.transform([values])

    return input_values


def encode_crop_data(n_clicks,state,year,crop,area):
    global y_scale_crop    
    data1 = pd.read_csv("Crop.csv")

    original_data1 = data1.copy()
    le_crop = LabelEncoder()

    data1.State = le_crop.fit_transform(data1.State)
    data1.Crop = le_crop.fit_transform(data1.Crop)

    states1=[]
    index_state1={}
    index_crop1={}

    states1=original_data1["State"].unique()   

    index_state1 = dict.fromkeys(states1, None) 
     
    for state in index_state1.keys():
        location = original_data1[original_data1['State']==state].index.values
        index_state1[state] = location[0]
    
    crops1=original_data1["Crop"].unique()
    
    index_crop1 = dict.fromkeys(crops1, None)

    for crop in index_crop1.keys():
        location = original_data1[original_data1['Crop']==crop].index.values
        index_crop1[crop] = location[0]

    y = data1['Production'].values

    data1 = data1.drop(['Production'],axis=1)
    X = data1.values

    x_scale_crop = MinMaxScaler(feature_range=(0,1))
    y_scale_crop = MinMaxScaler(feature_range=(0,1))

    X_scaled_crop = x_scale_crop.fit_transform(X)
    y_scaled_crop = y_scale_crop.fit_transform(y.reshape(-1,1))

    state_label_crop = data1.State[index_state1[state]]
    crop_label_crop = data1.Crop[index_crop1[crop]]
    values_crop = np.array([state_label_crop,year,crop_label_crop,area])
    input_values_crop = x_scale_crop.transform([values_crop])
        
    
    return input_values_crop



def decode_demand_data(demand_prediction):
    global y_scale
    result = y_scale.inverse_transform(demand_prediction.reshape(-1,1))

    return result

def decode_crop_data(crop_prediction):
    global y_scale_crop
    result1 = y_scale_crop.inverse_transform(crop_prediction.reshape(-1,1))
    
    return result1    

    