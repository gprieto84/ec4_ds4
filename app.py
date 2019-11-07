import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

df = pd.read_csv('aggr.csv', parse_dates=['Entry time'])
df['period'] = df['Entry time'].values.astype('datetime64[M]')

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/uditagarwal/pen/oNvwKNP.css', 'https://codepen.io/uditagarwal/pen/YzKbqyV.css'])

#Helper function
def filter_df(exchange, margin, start_date, end_date):
    dff = df[(df['Exchange'] == exchange) & (df['Margin'] == margin) & (df['Entry time'] >= start_date) & (df['Entry time'] <= end_date)]
    return dff


# HTML definition
app.layout = html.Div(children=[
    html.Div(
            children=[
                html.H2(children="Bitcoin Leveraged Trading Backtest Analysis", className='h2-title'),
            ],
            className='study-browser-banner row'
    ),
    html.Div(
        className="row app-body",
        children=[
            html.Div(
                className="twelve columns card",
                children=[
                    html.Div(
                        className="padding row",
                        children=[
                            html.Div(
                                className="two columns card",
                                children=[
                                    html.H6("Select Exchange"),
                                    dcc.RadioItems(
                                        id="exchange-select",
                                        options=[
                                            {'label': label, 'value': label} for label in df['Exchange'].unique()
                                        ],
                                        value='Bitmex',
                                        labelStyle={'display': 'inline-block'}
                                    )
                                ]
                            ),
                            # Leverage Definition
                            html.Div(
                                className="two columns card 2",
                                children=[
                                    html.H6("Select Leverage"),
                                    dcc.RadioItems(
                                        id="leverage-select",
                                        options=[
                                            {'label':label, 'value': label} for label in df['Margin'].unique()
                                        ],
                                        value=1,
                                        labelStyle={'display': 'inline-block'}
                                    )
                                ]
                            ),
                            # Datepicker
                            html.Div(
                                className="three column card",
                                children=[
                                    html.H6("Select Dates"),
                                    dcc.DatePickerRange(
                                        id="date-range-select",
                                        start_date=df['Entry time'].min(),
                                        end_date=df['Entry time'].max(),
                                        display_format='MMM YY'
                                    )
                                ]
                            ),
                            #Strategy Returns
                            html.Div(
                                id="strat-returns-div",
                                className="two columns indicator pretty_container",
                                children=[
                                    html.P(id="strat-returns", className="indicator_value"),
                                    html.P('Strategy Returns', className="twelve columns indicator_text"),
                                ]
                            ),
                            #Market Returns
                            html.Div(
                                id="market-returns-div",
                                className="two columns indicator pretty_container",
                                children=[
                                    html.P(id="market-returns", className="indicator_value"),
                                    html.P('Market Returns', className="twelve columns indicator_text"),
                                ]
                            ),
                            #Strategy vs Market 
                            html.Div(
                                id="strat-vs-market-div",
                                className="two columns indicator pretty_container",
                                children=[
                                    html.P(id="strat-vs-market", className="indicator_value"),
                                    html.P('Strategy vs. Market Returns', className="twelve columns indicator_text"),
                                ]
                            ),
                          
                        ]
                )
        ]),
        # Candle Stick
        html.Div(
            className='twelve columns card',
            children=[
                dcc.Graph(
                    id='monthly-chart',
                    figure={
                        'data':[]
                    }
                )
            ]
        )
    ])        
])

#Callbacks
@app.callback(
    [
        dash.dependencies.Output('date-range-select', 'start_date'),
        dash.dependencies.Output('date-range-select', 'end_date')
    ],
    [
        dash.dependencies.Input('exchange-select', 'value')
    ]
)
def update(value):
    dff = df[df['Exchange'] == value]
    return dff['Entry time'].min(), dff['Entry time'].max() 



@app.callback(
    dash.dependencies.Output('monthly-chart', 'figure'),
    [
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range-select', 'start_date'),
        dash.dependencies.Input('date-range-select', 'end_date')
    ]
)
def update_candlestick(value_e, value_m, start_date, end_date):
    dff = filter_df(value_e, value_m,start_date,end_date)
    dff_monthly = dff.groupby('period').agg({'Entry balance':'last','Exit balance':'first'}).reset_index()
    trace = go.Candlestick(x=dff_monthly['period'],open=dff_monthly['Entry balance'],high=dff_monthly['Exit balance'],
                        low=dff_monthly['Entry balance'],close=dff_monthly['Exit balance'],
                        increasing={'line': {'color': '#00CC94'}},decreasing={'line': {'color': '#F50030'}})
    return {
            'data': [trace],
            'layout': go.Layout(title=f"Overview of Monthly Performance",
            xaxis={'rangeslider': {'visible': True}})
        }

if __name__ == "__main__":
    app.run_server(debug=True)