# ==========================================importing libaray==================================== #
import os
import warnings

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

# =========================================ignore function================================== #
warnings.filterwarnings('ignore')
os.chdir(os.path.dirname(os.path.realpath('__file__')))


# =====================================Read Data============================================== #
df = pd.read_csv('data/sample_data.csv')

groups = [*df['Person_Groups'].value_counts().index]
groups_options = [{'label': str(x), 'value': str(x)} for x in groups]

# =====================================Card Methods========================================= #
def group_shape(group):
    return df[df['Person_Groups']==group]

def group_users(group):
    data = group_shape(group)
    return format(data.shape[0], ",")+"/"+format(df.shape[0], ",")

def active_precentage(group):
    data = group_shape(group)
    return str(round((data[data['Usage_Active']==1].shape[0]/data.shape[0])*100))+"%"

def Number_of_Click(group):
    data = group_shape(group)
    return format(data['Usage_Number_of_event_buttons_clicks'].sum(), ",")

def Number_of_Meetings(group):
    data = group_shape(group)
    return format(data['Meeting_All'].sum(), ",")

# =================================Chart Method============================================ #


dict_usage = {'000':'Undefine',
              '001':'Android',
              '010':'IOS', 
              '011':'Android&IOS',
              '100':'Web',
              '101':'Web&Android', 
              '110':'Web&IOS',
              '111':'Web&Andorid&IOs'}

def platform_usage(group):
    data = group_shape(group)
    agg_data = data[data['Usage_Active']==1].groupby(['Usage_Web_app',
                                                  'Usage_iOS',
                                                  'Usage_Android']).agg({'Usage_Active':['count'], 
                                                                         'Usage_Number_of_event_buttons_clicks':['sum']})
    agg_data.columns = ['ID_Count', 'Total_Click']
    return agg_data

# =============================Active data split by platform usage=============================== #
def pie_chart(group, col_name):
    data = platform_usage(group)
    data.reset_index(inplace=True)
    data[['Usage_Web_app', 'Usage_iOS', 'Usage_Android']] = data[['Usage_Web_app', 'Usage_iOS', 'Usage_Android']].astype('str')
    data['usage'] = data['Usage_Web_app']+data['Usage_iOS']+""+data['Usage_Android']
    data['platform'] = data['usage'].map(dict_usage)
    my_layout = go.Layout({"showlegend": False})
    
    fig = go.Figure(data=[go.Pie(labels=[*data['platform'].values],
                                 values=[*data[col_name].values],
                                 hole=.4, 
                                 title=col_name)],
                   layout = my_layout)
    
    return fig

# =============================Total bookmark split by Country============================= #

def country_with_bookmarks(group, col_name):
    data = group_shape(group)
    name = col_name.split("_")[-1]
    df_country = data[data['Person_Country'].notna()]
    df_agg_country = df_country.groupby(['Person_Country']).agg({col_name:['sum']})
    df_agg_country.columns = [col_name]
    df_agg_country.reset_index(inplace=True)
    df_agg_country.sort_values(col_name, ascending=True, inplace=True) 
    fig = px.bar(df_agg_country.tail(20), x=col_name, y='Person_Country', text=col_name)
    fig.update_traces(textfont_size=8, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_layout(title=f"Total {name} with Country",
        title_x=0.5, xaxis_title=name, yaxis_title="Country",
        legend_title="", font=dict(size=10, color="black"))
    return fig

# =============================Top 20 Product of interest================================ #

def top_sub_product(group, col_name):
    data = group_shape(group)
    data = data[data[col_name].notna()]
    top_20_categories = data[[col_name]].value_counts().iloc[:20].reset_index()
    top_20_categories.columns = ['product', 'count'] 
    top_20_categories.sort_values('count', ascending=True, inplace=True)
    fig = px.bar(top_20_categories, x='count', y='product', text='count',
            title=f"Top 20 Product of Interest")
    fig.update_traces(textfont_size=8, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_yaxes( showticklabels=False)
    fig.update_layout(title_x=0.5)
    return fig

# ==========================Top 10 job functions split by connection status======================== #

job_function_dict = {'send':['Connection_request_sent_Pending', 
                             'Connection_request_sent_Accepted', 
                             'Connection_request_sent_Declined'],
                     'received': ['Connection_request_received_Pending',
                                 'Connection_request_received_Accepted',
                                 'Connection_request_received_Declined']}

def job_functions(group, status):
    data = group_shape(group)
    df_job_function = data[data['Person_Job_Function'].notna()]
    agg_job_function = df_job_function.groupby('Person_Job_Function').agg({job_function_dict[status][0]:['sum'], 
                                                         job_function_dict[status][1]:['sum'],
                                                         job_function_dict[status][2]:['sum'],})
    
    agg_job_function.columns = ['Pending', 'Accepted', 'Declined']
    agg_job_function.sort_values(['Pending', 'Accepted', 'Declined'], ascending=False, inplace=True)
    agg_job_function.reset_index(inplace=True)
    fig = px.bar(agg_job_function.head(10), y=['Pending', 'Accepted', 'Declined'], x='Person_Job_Function',
            title=f"Top 10 job functions {status} connection")
    fig.update_traces(textfont_size=10, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_xaxes( showticklabels=False)
    fig.update(layout_showlegend=False)
    fig.update_layout(title_x=0.5)
    return fig

# ===========================Total meetings split by Nature of Business======================== #
def nature_meetings(group):
    data = group_shape(group)
    df_meetings_nature = data[data['Person_Nature_of_Business'].notna()]
    agg_meetings_nature = df_meetings_nature.groupby('Person_Nature_of_Business').agg({'Meeting_All':['sum']})
    agg_meetings_nature.columns = ['Total_Meeting']
    agg_meetings_nature.sort_values('Total_Meeting', ascending=True, inplace=True)
    agg_meetings_nature.reset_index(inplace=True)
    
    fig = px.bar(agg_meetings_nature, x='Total_Meeting', y='Person_Nature_of_Business', text='Total_Meeting')
    fig.update_traces(textfont_size=8, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_layout(title="Total meetings VS. Nature of Business",
        title_x=0.5,
        xaxis_title="Total Meeting",
        yaxis_title="Nature of Business",
        legend_title="",
        font=dict(
            size=10,
            color="black"
        )
    )
    return fig


#  =================================Deployment========================================= #

# ==================================Text field========================================== #
def drawText():
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H2("Data Analysis For Organization"),
                ], style={'textAlign': 'center', 'color':'#fff'}) 
            ]), color = 'dark'
        ),
    ])

# ===============================================Design Dash =================================== #
external_stylesheets = [dbc.themes.FLATLY]

app = dash.Dash(__name__, 
                external_stylesheets=external_stylesheets,
                update_title='Loading...',
                title='Informa'
)

server = app.server


app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
#===================================Dashboard Title================================#
            dbc.Row([
                dbc.Col([
                    drawText()
                ], width=12)
            ], justify="center", align='center'),
            
            html.Br(),
            
#==================================options=========================================#
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id='status',
                        options=[
                            {'label': 'Send', 'value': 'send'},
                            {'label': 'Received', 'value': 'received'}
                        ],
                        value='send',
                        clearable=False,
                    ),
                ], width=2),
                
                dbc.Col([
                    dcc.Dropdown(
                        id='product',
                        options=[
                            {'label': 'Product', 'value': 'Person_Product_Categories_of_Interest'},
                            {'label': 'Sub Product', 'value': 'Person_Product_Sub-categories_of_Interest'}
                        ],
                        value='Person_Product_Categories_of_Interest',
                        clearable=False,
                    ),
                ], width=2),
                
                dbc.Col([
                    dcc.Dropdown(
                        id='Groups',
                        options=groups_options,
                        value=groups_options[0]['value'],
                        clearable=False,
                    ),
                ], width=4),
                
                dbc.Col([
                    dcc.Dropdown(
                        id='Pie_Filter',
                        options=[
                            {'label': 'Total Clicks', 'value': 'Total_Click'},
                            {'label': 'Number of ID', 'value': 'ID_Count'}
                        ],
                        value='Total_Click',
                        clearable=False,
                    ),
                ], width=2),
                
                dbc.Col([
                    dcc.Dropdown(
                        id='Bookmarks',
                        options=[
                            {'label': 'Exhibitors', 'value': 'Bookmarks_Exhibitors'},
                            {'label': 'Sessions', 'value': 'Bookmarks_Sessions'},
                            {'label': 'Items', 'value': 'Bookmarks_Items'}
                        ],
                        value='Bookmarks_Exhibitors',
                        clearable=False,
                    ),
                ], width=2),
                
            ], justify="center", align='center'),
            html.Br(),
            
#======================================Card========================================#
            dbc.Row([
                dbc.Col([
                    
                    html.Div([
                        html.H5("Group Users/Total Users"),
                    ], className='card-header', style={'textAlign': 'center', 'max-width': '20rem'}),
                    
                    html.Div([
                        html.H4(id='Group_Users'),
                    ], className='card-body', style={'textAlign': 'center'}) 
                    
                ],className='card text-white bg-primary mb-3', width=3),
                dbc.Col([
                    
                    html.Div([
                        html.H5("Active Precentage"),
                    ], className='card-header', style={'textAlign': 'center','max-width': '20rem'}),
                    
                    html.Div([
                        html.H4(id='Active_Precentage'),
                    ], className='card-body', style={'textAlign': 'center'}) 
                    
                ],className='card text-white bg-success mb-3', width=3),
                dbc.Col([
                    html.Div([
                        html.H5("Total Clicks"),
                    ], className='card-header', style={'textAlign': 'center', 'max-width': '20rem'}),
                    
                    html.Div([
                        html.H4(id='Total_Clicks'),
                    ], className='card-body', style={'textAlign': 'center'}) 
                    
                ],className='card text-white bg-info mb-3', width=3),
                dbc.Col([
                    html.Div([
                        html.H5("Total Meetings"),
                    ], className='card-header', style={'textAlign': 'center', 'max-width': '20rem'}),
                    
                    html.Div([
                        html.H4(id='Total_Meetings'),
                    ], className='card-body', style={'textAlign': 'center'}) 
                    
                ],className='card text-white bg-danger mb-3', width=3),
            ]),
            html.Br(),
            
            
#======================================Charts======================================#
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Loading(
                            id="loading-0",
                            children=[dcc.Graph(id='Business', figure={}),],
                            type="default",
                        ),

                    ]),
                ], width=4, style={'border-bottom': '1px solid #000'}),
                
                dbc.Col([
                    html.Div([
                        dcc.Loading(
                            id="loading-1",
                            children=[dcc.Graph(id='Pie_Chart', figure={}),],
                            type="default",
                        ),

                    ]),
                ], width=4, style={'border-left': '1px solid #000', 'border-bottom': '1px solid #000'}),
                
                dbc.Col([
                    html.Div([
                        dcc.Loading(
                            id="loading-2",
                            children=[dcc.Graph(id='Bar1', figure={}),],
                            type="default",
                        ),

                    ]),
                ], width=4, style={'border-left': '1px solid #000', 'border-bottom': '1px solid #000'})
            ]),
            html.Br(),
#==================================second row of charts=============================#
            dbc.Row([
                dbc.Col([
                    html.Div([
                        dcc.Loading(
                            id="loading-3",
                            children=[dcc.Graph(id='Bar_Product', figure={}),],
                            type="default",
                        ),

                    ]),
                ], width=6),
                
                dbc.Col([
                    html.Div([
                        dcc.Loading(
                            id="loading-4",
                            children=[dcc.Graph(id='Job_Functions', figure={}),],
                            type="default",
                        ),

                    ]),
                ], width=6, style={'border-left': '1px solid #000'})
            ]),
            
        ])
    )
])

#==================================callback=======================================#
@app.callback(
    Output('Business', 'figure'),
    Output('Pie_Chart', 'figure'),
    Output('Bar1', 'figure'),
    Output('Bar_Product', 'figure'),
    Output('Job_Functions', 'figure'),
    Output('Group_Users', 'children'),
    Output('Active_Precentage', 'children'),
    Output('Total_Clicks', 'children'),
    Output('Total_Meetings', 'children'),
    Input('status', 'value'),
    Input('Groups', 'value'),
    Input('product', 'value'),
    Input('Pie_Filter', 'value'),
    Input('Bookmarks', 'value'),
)
def update_output(status, group, product, typeFilter, bookmark):
    group_user = group_users(group)
    active_precent = active_precentage(group)
    total_click = Number_of_Click(group)
    total_meeting = Number_of_Meetings(group)
    fig0 = nature_meetings(group)
    fig = pie_chart(group,typeFilter)
    fig2 = country_with_bookmarks(group, bookmark)
    fig3 = top_sub_product(group, product)
    fig4 = job_functions(group, status)
    return fig3, fig, fig4, fig0, fig2, group_user, active_precent, total_click, total_meeting

#===================================run server====================================#
if __name__ == '__main__':
    app.run_server(debug=True)