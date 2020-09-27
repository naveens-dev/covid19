import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from apps.covid_data import data

cpt_state_ordered_list = ['Andaman & Nicobar Island', 'Andhra Pradesh', 'Arunanchal Pradesh', 'Assam', 'Bihar',
                          'Chandigarh', 'Chhattisgarh', 'Dadara & Nagar Havelli', 'Daman & Diu', 'Goa', 'Gujarat',
                          'Haryana', 'Himachal Pradesh', 'Jammu & Kashmir', 'Jharkhand', 'Karnataka', 'Kerala',
                          'Lakshadweep', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland',
                          'NCT of Delhi', 'Puducherry', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana',
                          'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Odisha']

df_india_map = data.df_states.copy()

# px.choropleth expects the rows in the data frame to be in the same order as the states_list that is passed to
# locations parameter. Below two lines sorts the df_new in that order
# refer https://stackoverflow.com/questions/13838405/custom-sorting-in-pandas-dataframe
df_india_map['state_names'] = pd.Categorical(df_india_map['state_names'], cpt_state_ordered_list)
df_india_map.sort_values('state_names', inplace=True)

#with open('f:/naveen/pythonprojects/maps-master/maps-master/Survey-of-India-Index-Maps/Boundaries/India'
#          '/India-States.json') as content:
#    states_json = json.load(content)

with open('india-states.json') as content:
    states_json = json.load(content)

india_fig = px.choropleth(df_india_map, geojson=states_json, color='Active', # title="Test",
                          hover_data=['Confirmed', 'Active', 'Recovered', 'Deceased'],
                          color_continuous_scale=px.colors.sequential.Reds,
                          locations=cpt_state_ordered_list, featureidkey="properties.ST_NM", projection="mercator")
# india_fig.update_layout(title={'text': 'Test Title'})
india_fig.update_geos(fitbounds="locations", visible=False)
india_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=750)
india_fig.update_layout(paper_bgcolor='#f8f9fa')
india_fig.update_layout(geo={'bgcolor': '#f8f9fa'})

india_fig_go = go.Figure(india_fig)
# india_fig_go.update_layout(title_text='Covid-19 Confirmed cases Heat map')

# -------------------------------------------------------------------------------------------------------------------
#                                         State Maps
# -------------------------------------------------------------------------------------------------------------------

kar_cen_cd=['556', '583', '572', '555', '565', '558', '557', '578', '582', '570', '566', '575', '567', '562', '561', '579',
 '574', '564', '576', '581', '560', '573', '577', '559', '584', '568', '571', '569', '563', '580']
guj_cen_cd=['474', '480', '482', '469', '488', '481', '485', '473', '477', '479', '468', '483', '471', '487', '490', '484',
 '470', '478', '476', '472', '492', '475', '489', '486', '491', '493']

#with open(
#        'f:/naveen/pythonprojects/maps-master/maps-master/Survey-of-India-Index-Maps/Boundaries/India/India'
#        '-Districts-2011Census.json') as content:
#    districts = json.load(content)

with open('india-districts-2011census.json') as content:
    districts = json.load(content)

states_fig = px.choropleth(geojson=districts,
                    locations=kar_cen_cd, featureidkey="properties.censuscode",
                    projection="mercator")
states_fig.update_geos(fitbounds="locations", visible=False)
states_fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=580)
states_fig.update_layout(paper_bgcolor='#f8f9fa')
states_fig.update_layout(geo={'bgcolor': '#f8f9fa'})
