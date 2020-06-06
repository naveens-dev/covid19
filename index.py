import dash_html_components as html
import dash_core_components as dcc
from app import app
from dash.dependencies import Input, Output
from apps import home, states


app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])


@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')],
    prevent_initial_call=True)
def display_page(pathname):
    if pathname == '/':
        return home.show_home_page()
    elif pathname == '/state-wise':
        return states.show_states_page()
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(port=8051, debug=True, host='0.0.0.0')
