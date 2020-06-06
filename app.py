import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'Covid-19 Dashboard'

server = app.server

app.config.suppress_callback_exceptions = True
