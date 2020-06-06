import dash_core_components as dcc
import dash_bootstrap_components as dbc
import locale
from apps.cpth import india_fig, india_fig_go
from apps.covid_data import data

locale.setlocale(locale.LC_NUMERIC, '')


def show_home_page():
    data.refresh_data()

    df = data.df_cts

    patient_state = ['Active', 'Recovered', 'Deceased']
    patient_value = [data.total_active, data.total_recovered, data.total_deceased]
    patient_test_result = ['Positive', 'Negative']
    patient_test_value = [data.total_confirmed, int(data.total_individuals_tested) - int(data.total_confirmed)]

    date = data.latest_top_5_date
    df_conf_top5 = data.df_conf_top5

    df_conf_dt = data.df_conf_dt

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
                                    dbc.NavLink('Home', href='/', disabled=True, className='text-grey'),
                                    dbc.NavLink('State Wise', href='/state-wise', className='text-white'),
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
                            dbc.CardDeck(
                                [
                                    dbc.Card([dbc.CardHeader("Tested"),
                                              dbc.CardBody(
                                                  locale.format_string('%d', int(data.total_individuals_tested),
                                                                       grouping=True, monetary=False))],
                                             color="dark", className='text-light'),
                                    dbc.Card([dbc.CardHeader("Confirmed"),
                                              dbc.CardBody(locale.format_string('%d', locale.atoi(data.total_confirmed),
                                                                                grouping=True, monetary=False))],
                                             color="dark", className='text-light'),
                                    dbc.Card([dbc.CardHeader("Active"),
                                              dbc.CardBody(locale.format_string('%d', data.total_active, grouping=True,
                                                                                monetary=False))],
                                             color="dark", className='text-light'),
                                    dbc.Card([dbc.CardHeader("Recovered"),
                                              dbc.CardBody(locale.format_string('%d', locale.atoi(data.total_recovered),
                                                                                grouping=True, monetary=False))],
                                             color="dark", className='text-light'),
                                    dbc.Card([dbc.CardHeader("Deceased"),
                                              dbc.CardBody(locale.format_string('%d', locale.atoi(data.total_deceased),
                                                                                grouping=True, monetary=False))],
                                             color="dark", className='text-light'),
                                ], style={'margin': '1% 5%', 'textAlign': 'center'}
                            ),
                        ]
                    )
                ]
            ),

            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Graph(
                                id="india_states_map",
                                config={'displayModeBar': False},
                                figure=india_fig_go
                            ),
                        ], lg=4
                    ),

                    dbc.Col(
                        [
                            dcc.Graph(id='covid-cummulative', config={'displayModeBar': False}, figure={'data': [
                                {'x': df['date'], 'y': df['totaldeceased'], 'type': 'scatter', 'name': 'Deceased',
                                 'mode': 'lines', 'line': {'width': '0', 'color': '#b00909'}, 'fill': 'tonexty',
                                 'stackgroup': 'one'},
                                {'x': df['date'], 'y': df['totalrecovered'], 'type': 'scatter', 'name': 'Recovered',
                                 'mode': 'lines', 'line': {'width': '0', 'color': '#1c6300'}, 'fill': 'tonexty',
                                 'stackgroup': 'one'},
                                {'x': df['date'], 'y': df['totalactive'], 'type': 'scatter', 'name': 'Active',
                                 'mode': 'lines', 'line': {'width': '0', 'color': '#0317fc'}, 'fill': 'tonexty',
                                 'stackgroup': 'one'}],
                                'layout': {'title': 'Cumulative Numbers', 'height': '375', 'paper_bgcolor': '#f8f9fa',
                                           'plot_bgcolor': '#f8f9fa', 'yaxis': {'title': 'Patient Count'},
                                           'legend': {'x': 0.37, 'y': 1.13, 'orientation': 'h'}}
                            }),

                            dcc.Graph(id='covid-daily', config={'displayModeBar': False}, figure={'data': [
                                {'x': df['date'], 'y': df['dailyconfirmed'], 'type': 'scatter', 'name': 'Confirmed',
                                 'marker': {'color': '#fa7900'}},
                                {'x': df['date'], 'y': df['dailyrecovered'], 'type': 'scatter', 'name': 'Recovered',
                                 'marker': {'color': '#1c6300'}},
                                {'x': df['date'], 'y': df['dailydeceased'], 'type': 'scatter', 'name': 'Deceased',
                                 'marker': {'color': '#b00909'}}],
                                'layout': {'title': 'Daily Snapshot', 'height': '375', 'paper_bgcolor': '#f8f9fa',
                                           'plot_bgcolor': '#f8f9fa', 'yaxis': {'title': 'Patient Count'},
                                           'legend': {'x': 0.37, 'y': 1.13, 'orientation': 'h'}}
                            })
                        ], lg=8
                    )
                ], no_gutters=True
            ),

            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Graph(
                                id="pt_state_pie", config={'displayModeBar': False},
                                figure={'data': [{'type': 'pie', 'labels': patient_state, 'values': patient_value,
                                                  'textinfo': 'label+percent', 'insidetextorientation': 'radial',
                                                  'marker': {'colors': ['#b86b23', '#55704a', '#b00909']}}],
                                        'layout': {'height': '375',
                                                   'title': 'Active v/s Recovered v/s Deceased (cumulative)',
                                                   'paper_bgcolor': '#f8f9fa', 'plot_bgcolor': '#f8f9fa'}}
                            )
                        ], lg=3
                    ),
                    dbc.Col(
                        [
                            dcc.Graph(id="zones_bar", config={'displayModeBar': False},
                                      figure={'data': [{'type': 'bar', 'text': data.zone_count,
                                                        'textposition': 'inside', 'hoverinfo': 'none',
                                                        'x': data.zone_categories, 'y': data.zone_count,
                                                        'marker':
                                                            {'color': ['#f28100', '#437a2b', '#750000', '#3b3a3a']}}],
                                              'layout': {'height': '375', 'title': 'Zone Counts',
                                                         'paper_bgcolor': '#f8f9fa', 'plot_bgcolor': '#f8f9fa'}}
                                      )
                        ], lg=3
                    ),
                    dbc.Col(
                        [
                            dcc.Graph(
                                id="pt_test_result_pie", config={'displayModeBar': False},
                                figure={'data': [{'type': 'pie', 'labels': patient_test_result,
                                                  'values': patient_test_value, 'textinfo': 'label+percent',
                                                  'insidetextorientation': 'radial',
                                                  'marker': {'colors': ['#b86b23', '#55704a']}}],
                                        'layout': {'height': '375',
                                                   'title': 'Tests: Positive v/s Negative (cumulative)',
                                                   'paper_bgcolor': '#f8f9fa', 'plot_bgcolor': '#f8f9fa'}}
                            )
                        ], lg=3
                    ),
                    dbc.Col(
                        [
                            dcc.Graph(id="top5_bar", config={'displayModeBar': False},
                                      figure={'data': [{'type': 'bar', 'text': df_conf_top5.values,
                                                        'textposition': 'inside', 'hoverinfo': 'none',
                                                        'x': df_conf_top5.index.values, 'y': df_conf_top5.values,
                                                        'marker': {'color': df_conf_top5.values,
                                                                   'colorscale': 'Reds'}}],
                                              'layout': {'height': '375', 'title': f'Top 5 states on {date} '
                                                                                   f'(Confirmed Cases)',
                                                         'paper_bgcolor': '#f8f9fa', 'plot_bgcolor': '#f8f9fa'}}
                                      )
                        ], lg=3
                    ),
                ]
            ),

            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Graph(id='doubling-time', config={'displayModeBar': False}, figure={'data': [
                                {'x': df_conf_dt['date'], 'y': df_conf_dt['DT'], 'type': 'scatter', 'name': 'Confirmed',
                                 'marker': {'color': '#ab13a6'}}],
                                'layout': {'title': 'Doubling Time', 'height': '375', 'paper_bgcolor': '#f8f9fa',
                                           'plot_bgcolor': '#f8f9fa', 'yaxis': {'title': 'Days'}}
                            })
                        ], lg=6
                    ),

                    dbc.Col(
                        [
                            dcc.Graph(id='recov-dec-spread', config={'displayModeBar': False}, figure={'data': [
                                {'x': data.df_recovery['Duration'], 'type': 'violin', 'name': 'Recovery',
                                 'orientation': 'h', 'marker': {'color': '#1c6300'}},
                                {'x': data.df_deceased['Duration'], 'type': 'violin', 'name': 'Deceased',
                                 'orientation': 'h', 'marker': {'color': '#b00909'}}],
                                'layout': {'title': 'Recovery / Deceased Duration Spread', 'height': '375',
                                           'paper_bgcolor': '#f8f9fa',
                                           'plot_bgcolor': '#f8f9fa', 'xaxis': {'title': 'Days'}}
                            })
                        ], lg=6
                    )
                ]
            )
        ], className='bg-light', fluid=True
    )

    return layout_page
