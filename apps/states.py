import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import pandas as pd
import locale

from app import app
from apps.covid_data import data

locale.setlocale(locale.LC_NUMERIC, '')


def show_states_page():
    data.refresh_data()

    df_conf, df_recov, df_dec, df_act = data.compute_states_cumulative()
    states = df_conf.index.values.tolist()

    layout_page = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Nav(
                                [
                                    dbc.NavLink('Covid-19 India Dashboard', href='/', className='text-white'),
                                ], horizontal='start', className='bg-dark'
                            )
                        ], lg=3
                    ),
                    dbc.Col(
                        [
                            dbc.Nav(
                                [
                                    dbc.NavLink('Home', href='/', className='text-white'),
                                    dbc.NavLink('State Wise', href='/state-wise', disabled=True, className='text-grey'),
                                ], horizontal='end', className='bg-dark'
                            )
                        ], lg=9
                    )
                ], no_gutters=True
            ),

            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Graph(
                                id="statewise",
                                figure={'data': [
                                    {'x': states, 'y': df_act.tolist(), 'type': 'bar', 'name': 'Active',
                                     'marker': {'color': '#b86b23'}},
                                    {'x': states, 'y': df_recov.tolist(), 'type': 'bar', 'name': 'Recovered',
                                     'marker': {'color': '#55704a'}},
                                    {'x': states, 'y': df_dec.tolist(), 'type': 'bar', 'name': 'Deceased',
                                     'marker': {'color': '#b00909'}},
                                ],
                                    'layout': {'height': '400', 'barmode': 'stack',
                                               'title': 'State Wise Cumulative Numbers',
                                               'paper_bgcolor': '#f8f9fa', 'plot_bgcolor': '#f8f9fa',
                                               'yaxis': {'title': 'Patient Count'}}}
                            )
                        ]
                    )
                ]
            ),

            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("", id='state_name', style={'text-align': 'center'})
                        ], style={'background-color': '#f8f9fa'}
                    )
                ]
            ),

            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Graph(
                                id='state_cumulative',
                                figure={
                                    'layout': {'height': '480'}}
                            )
                        ], lg=6
                    ),

                    dbc.Col(
                        [
                            dcc.Graph(
                                id='state_daily',
                                figure={
                                    'layout': {'height': '480'}}
                            )
                        ], lg=6
                    )
                ], no_gutters=True
            ),

            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Graph(
                                id='districts_current',
                                figure={
                                    'layout': {'height': '520'}}
                            )
                        ]
                    )
                ]
            ),

            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3("Test Data", style={'margin-top': '6%', 'text-align': 'center'}),
                            html.Div(id="test_table", style={'width': '100px', 'margin-left': '20%', 'margin-top': '10%'})
                        ], lg=3, style={'height': '520px', 'background-color': '#f8f9fa',
                                        'justify-content': 'center'}
                    ),

                    dbc.Col(
                        [
                            html.H3("Key Metrics", style={'margin-top': '6%', 'text-align': 'center'}),
                            html.Div(id="data cards", style={'margin-top': '4%'})
                        ], lg=3, style={'height': '520px', 'background-color': '#f8f9fa'}
                    ),

                    dbc.Col(
                        [
                            html.H3("District-wise Breakup", style={'text-align': 'center'}),
                            html.Div(id="district_data_table", style={'margin-left': '4%', 'margin-right': '3%'})
                        ], lg=6, style={'height': '520px', 'background-color': '#f8f9fa'}
                    ),
                ], no_gutters=True
            ),

            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Graph(
                                id='state_daily_percent',
                                figure={
                                    'layout': {'height': '520'}}
                            )
                        ], lg=6
                    ),

                    dbc.Col(
                        [
                            dcc.Graph(
                                id='state_recov_dec_spread',
                                figure={
                                    'layout': {'height': '520'}}
                            )
                        ], lg=6
                    ),
                ], no_gutters=True
            ),
        ], fluid=True
    )

    return layout_page


@app.callback(
    Output("state_cumulative", "figure"),
    [Input("statewise", "clickData")])
def display_state_cumulative(click_data):
    if click_data is None:
        state = 'KA'
    else:
        state = click_data['points'][0]['label']

    df = pd.DataFrame()
    df['date'] = data.df_sts_dec['date']
    df['Deceased'] = data.df_sts_dec[state].expanding().sum()
    df['Recovered'] = data.df_sts_recov[state].expanding().sum()
    df['Active_Daily'] = data.df_sts_conf[state] - data.df_sts_recov[state] - data.df_sts_dec[state]
    df['Active'] = df['Active_Daily'].expanding().sum()

    trace = [dict(type="scatter", x=df['date'], y=df['Deceased'], name='Deceased', mode='lines',
                  line={'width': '0', "color": "#b00909"}, fill='tonexty', stackgroup='one'),
             dict(type="scatter", x=df['date'], y=df['Recovered'], name='Recovered', mode='lines',
                  line={'width': '0', "color": "#1c6300"}, fill='tonexty', stackgroup='one'),
             dict(type="scatter", x=df['date'], y=df['Active'], name='Active', mode='lines',
                  line={'width': '0', "color": "#0317fc"}, fill='tonexty', stackgroup='one')]

    layout = dict(title=f'Cumulative Count', plot_bgcolor='#f8f9fa', paper_bgcolor='#f8f9fa', height=480,
                  yaxis={"title": "Patient Count"}, legend=dict(x=.3, y=1.13, orientation='h'))

    return {"data": trace, "layout": layout}


@app.callback(
    Output("state_daily", "figure"),
    [Input("statewise", "clickData")])
def display_state_daily(click_data):
    if click_data is None:
        state = 'KA'
    else:
        state = click_data['points'][0]['label']

    trace = [dict(type="scatter", x=data.df_sts_conf['date'], y=data.df_sts_conf[state], name='Confirmed',
                  marker=dict(color='#fa7900')),
             dict(type="scatter", x=data.df_sts_recov['date'], y=data.df_sts_recov[state], name='Recovered',
                  marker=dict(color='#1c6300')),
             dict(type="scatter", x=data.df_sts_dec['date'], y=data.df_sts_dec[state], name='Deceased',
                  marker=dict(color='#b00909'))]

    layout = dict(title=f'Daily Snapshot', plot_bgcolor='#f8f9fa', paper_bgcolor='#f8f9fa', height=480,
                  yaxis={"title": "Patient Count"}, legend=dict(x=.3, y=1.13, orientation='h'))

    return {"data": trace, "layout": layout}


@app.callback(
    Output("districts_current", "figure"),
    [Input("statewise", "clickData")])
def display_districts_current(click_data):
    if click_data is None:
        state = 'KA'
    else:
        state = click_data['points'][0]['label']

    df = data.df_districts.loc[data.df_districts['State_Code'] == state]

    trace = [dict(type="scatter", x=df['District'], y=df['Active'], name='Active', mode='markers',
                  marker=dict(color='#0317fc', size=df['Active'], sizemode='area', opacity=0.5)),
             dict(type="scatter", x=df['District'], y=df['Recovered'], name='Recovered', mode='markers',
                  marker=dict(color='#1c6300', size=df['Recovered'], sizemode='area', opacity=0.5)),
             dict(type="scatter", x=df['District'], y=df['Deceased'], name='Deceased', mode='markers',
                  marker=dict(color='#b00909', size=df['Deceased'], sizemode='area', opacity=0.5))]

    layout = dict(title=f'Current District Snapshot', plot_bgcolor='#f8f9fa', paper_bgcolor='#f8f9fa', height=520,
                  yaxis={"title": "Patient Count"}, legend=dict(x=.41, y=1.13, orientation='h', itemsizing='constant'))

    return {"data": trace, "layout": layout}


state_code_mapping = {'AN': 'Andaman & Nicobar Island', 'AP': 'Andhra Pradesh', 'AR': 'Arunanchal Pradesh',
                      'AS': 'Assam', 'BR': 'Bihar', 'CH': 'Chandigarh', 'CT': 'Chhattisgarh', 'DD': 'Daman & Diu',
                      'DL': 'NCT of Delhi', 'DN': 'Dadara & Nagar Havelli', 'GA': 'Goa', 'GJ': 'Gujarat',
                      'HP': 'Himachal Pradesh', 'HR': 'Haryana', 'JH': 'Jharkhand', 'JK': 'Jammu & Kashmir',
                      'KA': 'Karnataka', 'KL': 'Kerala', 'LA': 'Ladakh', 'LD': 'Lakshadweep', 'MH': 'Maharashtra',
                      'ML': 'Meghalaya', 'MN': 'Manipur', 'MP': 'Madhya Pradesh', 'MZ': 'Mizoram', 'NL': 'Nagaland',
                      'OR': 'Odisha', 'PB': 'Punjab', 'PY': 'Puducherry', 'RJ': 'Rajasthan', 'SK': 'Sikkim',
                      'TG': 'Telangana', 'TN': 'Tamil Nadu', 'TR': 'Tripura', 'UN': 'Unknown', 'UP': 'Uttar Pradesh',
                      'UT': 'Uttarakhand', 'WB': 'West Bengal'}


@app.callback(
    Output("state_name", "children"),
    [Input("statewise", "clickData")])
def display_state_name(click_data):
    if click_data is None:
        state = 'KA'
    else:
        state = click_data['points'][0]['label']

    return state_code_mapping[state]


@app.callback(
    Output("state_daily_percent", "figure"),
    [Input("statewise", "clickData")])
def display_state_percent(click_data):
    if click_data is None:
        state = 'KA'
    else:
        state = click_data['points'][0]['label']

    df = data.df_sts_conf.loc[:, ['date', 'TT', state]]
    df['percent'] = (df[state]/df['TT'])*100

    trace = [dict(type="scatter", x=df['date'], y=df['percent'], name='Percentage', marker=dict(color='#fa7900'))]

    layout = dict(title=f'% Daily Contribution to National Count (Confirmed Cases)', plot_bgcolor='#f8f9fa',
                  paper_bgcolor='#f8f9fa', height=520, yaxis={"title": "Percentage"},
                  legend=dict(x=.3, y=1.13, orientation='h'))

    return {"data": trace, "layout": layout}


@app.callback(
    Output("test_table", "children"),
    [Input("statewise", "clickData")])
def display_state_test_table(click_data):
    if click_data is None:
        state = 'KA'
    else:
        state = click_data['points'][0]['label']

    df_test = data.df_sts_test
    df_test = df_test.loc[df_test['State'] == state_code_mapping[state]]
    df_test = df_test.dropna(axis=0)

    if df_test.empty:
        return f'No Test Data Available for {state_code_mapping[state]}'

    df_test = df_test.iloc[-1]

    positive_perc = round(df_test['Positive'] / df_test['Total Tested'] * 100, 2)
    negative_perc = round(df_test['Negative'] / df_test['Total Tested'] * 100, 2)
    pos_data = f'{df_test["Positive"]} ({positive_perc}%)'
    neg_data = f'{df_test["Negative"]} ({negative_perc}%)'
    df_test['Positive'] = pos_data
    df_test['Negative'] = neg_data

    parameters = df_test.index.values.tolist()
    values = df_test.values.tolist()
    test_list_dict_params = [{'Parameter': k, 'Value': v} for k, v in zip(parameters, values)]

    dash_test_table = dash_table.DataTable(
                                           data=test_list_dict_params,
                                           columns=[{'id': 'Parameter', 'name': 'Parameter'},
                                                    {'id': 'Value', 'name': 'Value'}],
                                           style_data_conditional=[
                                               {
                                                   'if': {'row_index': 'odd'},
                                                   'backgroundColor': 'rgb(248, 248, 248)'
                                               }
                                           ],
                                           style_header={
                                                            'backgroundColor': 'rgb(230, 230, 230)',
                                                            'fontWeight': 'bold', 'textAlign': 'center'
                                                        },
                                           style_cell={'textAlign': 'left'},
                                           )

    return dash_test_table


@app.callback(
    Output("state_recov_dec_spread", "figure"),
    [Input("statewise", "clickData")])
def display_state_recov_dec_spread(click_data):
    if click_data is None:
        state = 'KA'
    else:
        state = click_data['points'][0]['label']

    df_recov = data.df_recovery.loc[data.df_recovery['State code'] == state]
    df_dec = data.df_deceased.loc[data.df_deceased['State code'] == state]

    trace = [dict(type="violin", x=df_recov['Duration'], name='Recovery', orientation='h',
                  marker=dict(color='#1c6300')),
             dict(type="violin", x=df_dec['Duration'], name='Deceased', orientation='h',
                  marker=dict(color='#b00909')),
             ]

    layout = dict(title='Recovery / Deceased Duration Spread', plot_bgcolor='#f8f9fa',
                  paper_bgcolor='#f8f9fa', height=520, xaxis={"title": "Days"})

    return {"data": trace, "layout": layout}


@app.callback(
    Output("data cards", "children"),
    [Input("statewise", "clickData")])
def display_data_cards(click_data):
    if click_data is None:
        state = 'KA'
    else:
        state = click_data['points'][0]['label']

    df_conf, df_recov, df_dec, df_act = data.compute_states_cumulative()
    tot_conf = df_conf[state]
    tot_recov = df_recov[state]
    tot_dec = df_dec[state]
    tot_act = df_act[state]
    perc_act = round(tot_act/tot_conf * 100, 2)
    perc_recov = round(tot_recov/tot_conf * 100, 2)
    perc_dec = round(tot_dec/tot_conf * 100, 2)
    act_str = f'{locale.format_string("%d", tot_act, grouping=True, monetary=False)} ({perc_act}%)'
    recov_str = f'{locale.format_string("%d", tot_recov, grouping=True, monetary=False)} ({perc_recov}%)'
    dec_str = f'{locale.format_string("%d", tot_dec, grouping=True, monetary=False)} ({perc_dec}%)'

    row_1 = dbc.Row(
        [
            dbc.Col(dbc.Card([dbc.CardHeader("Confirmed", className='font-weight-bold'),
                              dbc.CardBody(locale.format_string('%d', tot_conf, grouping=True, monetary=False))],
                             color="dark", outline=True), width=4),
            dbc.Col(dbc.Card([dbc.CardHeader("Active", className='font-weight-bold'),
                              dbc.CardBody(act_str)],
                             color="dark", outline=True), width=8),
        ], className="mb-4", style={'text-align': 'center'}
    )

    row_2 = dbc.Row(
        [
            dbc.Col(dbc.Card([dbc.CardHeader("Positive", className='font-weight-bold'),
                              dbc.CardBody("somedata4")], color="dark", outline=True), width=4),
            dbc.Col(dbc.Card([dbc.CardHeader("Recovered", className='font-weight-bold'),
                              dbc.CardBody(recov_str)],
                             color="dark", outline=True), width=8),
        ], className="mb-4", style={'text-align': 'center'}
    )

    row_3 = dbc.Row(
        [
            dbc.Col(dbc.Card([dbc.CardHeader("Negative", className='font-weight-bold'),
                              dbc.CardBody("somedata7")], color="dark", outline=True), width=4),
            dbc.Col(dbc.Card([dbc.CardHeader("Deceased", className='font-weight-bold'),
                              dbc.CardBody(dec_str)],
                             color="dark", outline=True), width=8),
        ], className="mb-4", style={'text-align': 'center'}
    )

    return [row_1, row_2, row_3]


@app.callback(
    Output("district_data_table", "children"),
    [Input("statewise", "clickData")])
def display_state_test_table(click_data):
    if click_data is None:
        state = 'KA'
    else:
        state = click_data['points'][0]['label']

    column_list = ['District', 'Confirmed', 'Active', 'Recovered', 'Deceased', 'Delta_Confirmed', 'Delta_Recovered',
                   'Delta_Deceased']

    df = data.df_districts.loc[data.df_districts['State_Code'] == state, column_list].copy()
    df.rename(columns={'Delta_Confirmed': 'Delta Confirmed', 'Delta_Recovered': 'Delta Recovered',
                       'Delta_Deceased': 'Delta Deceased'}, inplace=True)

    district_table = dash_table.DataTable(data=df.to_dict('records'),
                                          columns=[{'id': col, 'name': col} for col in df.columns.values.tolist()],
                                          style_table={'maxHeight': '450px', 'overflowY': 'auto'},
                                          style_header={'whiteSpace': 'normal', 'height': 'auto', 'fontWeight': 'bold',
                                                        'textAlign': 'center', 'backgroundColor': 'rgb(230, 230, 230)'},
                                          style_data_conditional=[
                                              {
                                                  'if': {'row_index': 'odd'},
                                                  'backgroundColor': 'rgb(248, 248, 248)'
                                              },
                                              {
                                                  'if': {'column_id': ['Confirmed', 'Delta Confirmed']},
                                                  'color': '#fa7900'
                                              },
                                              {
                                                  'if': {'column_id': ['Recovered', 'Delta Recovered']},
                                                  'color': '#1c6300'
                                              },
                                              {
                                                  'if': {'column_id': ['Deceased', 'Delta Deceased']},
                                                  'color': '#b00909'
                                              },
                                              {
                                                  'if': {'column_id': 'Active'}, 'color': '#0317fc'
                                              }
                                          ],
                                          style_cell={'textAlign': 'center'},
                                          style_cell_conditional=[
                                              {
                                                  'if': {'column_id': 'District'}, 'textAlign': 'right'
                                              }
                                          ]
                                          )

    return district_table
