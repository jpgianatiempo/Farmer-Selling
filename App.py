import dash
import dash_core_components as dcc
import dash_html_components as html
from numpy import isin
import plotly.graph_objects as go
import dash_split_pane
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from datetime import datetime
from dash.exceptions import PreventUpdate

#https://www.statworx.com/at/blog/how-to-build-a-dashboard-in-python-plotly-dash-step-by-step-tutorial/
#https://blog.finxter.com/python-dash-how-to-build-a-dashboard/

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
 
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)
 

df = pd.read_csv('Base.csv', engine="python",encoding="latin-1")
df = df[df["Campaña"]!= "07/08"]

fecha = df["Fecha"].max()
original_date = datetime.strptime(fecha, '%Y-%m-%d')
fecha = original_date.strftime("%d-%m-%Y")

def get_options(granos):
    dict_list = []
    for i in granos:
        dict_list.append({'label': i, 'value': i})

    return dict_list


app.layout = html.Div(children=[
    html.H1(children='Comercialización de granos en Argentina',
    style={'textAlign': 'left','color': 'steelblue'}),
   html.H4(children="Datos semanales desde el 2009 hasta el "+fecha,
    style={'textAlign': 'left'}),  

   dash_split_pane.DashSplitPane(
    children=[
  
      html.Div(children=[
        html.H1(children='Configuración', style={'textAlign': 'center','color': 'steelblue'}),
        html.P('''Seleccione un cultivo'''),
        dcc.Dropdown(id='dropdown-menu',
        options=get_options(df['Grano'].unique()),
                           multi=False,
                           value="Trigo", #[df['Grano'].sort_values()[0]],
                           className='selector_granos'),
        html.P(''' '''), 
        html.P('''Seleccione el sector'''),
        dcc.Dropdown(id='dropdown-menu-sector',
        options=get_options(df['Sector'].unique()),
                           multi=False,
                           value="Total", #[df['Grano'].sort_values()[0]],
                           className='selector_sector'),
        html.P(''' '''),                  
        html.P('''Seleccione todas, una o más campañas'''),
        dcc.RadioItems(
            id="all-checklist",
            options=[{"label": i, "value": i} for i in ["Todas", "Últimas 5" ,"Últimas 3"]],
            value="Todas",
            labelStyle={"display": "inline-block"},
        ),
        html.Div(
        style={'width':'100%', 'height':'100%','float':'left'},
        children=[
        dcc.Checklist(id='checklist-campana',
        options=get_options(df['Campaña'].unique()),
                           value=['08/09','09/10','10/11','11/12','12/13','13/14','14/15','15/16','16/17','17/18','18/19','19/20','20/21', '21/22'],
                           labelStyle={'display': 'inline-block'},
                           className='selector_campana')
                    ])],
          style={'margin-left': '10%','margin-right': '10%', 'verticalAlign': 'middle'}),
      
      html.Div(children=[
        html.H1(children='Gráficos', style={'textAlign': 'center','color': 'steelblue'}),
        html.Button('Total comprado', id='btn-1',style={'margin-left': '15%','textAlign': 'center'}),
        html.Button('Compras sin precio', id='btn-2',style={'textAlign': 'center'}),
        html.Button('Compras con precio', id='btn-3',style={'textAlign': 'center'}),
        html.Button('DJVE', id='btn-4',style={'textAlign': 'center'}),
        html.Div(id='container', children = [
         html.H3('''Compras totales''', style={'textAlign': 'center'}),
         dcc.Graph(id='input-graph',
          config={'displayModeBar': False}
                                    )
        ])                         
            ])
    ],
   id="splitter",
   split="vertical",
   size=1000,
   primary="second"
      )
])


#Cambia los container
@app.callback(
    Output(component_id='container', component_property='children'),
    Input(component_id='btn-1', component_property='n_clicks'),
    Input('btn-2', 'n_clicks'),
    Input('btn-3', 'n_clicks'),
    Input('btn-4', 'n_clicks'),
)
def update_output(btn1_click,btn2_click,btn3_click,btn4_click):
   changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
   if 'btn-1' in changed_id:
      return html.Div([html.H3('''Compras Totales''', style={'textAlign': 'center'}),
            dcc.Graph(id='input-graph',
               config={'displayModeBar': False}
                                    )])
   elif 'btn-2' in changed_id:
      return html.Div([html.H3('''Compras sin Precio''', style={'textAlign': 'center'}),
            dcc.Graph(id='input-graph-sin-precio',
               config={'displayModeBar': False}
                                    )])
   elif 'btn-3' in changed_id:
      return html.Div([html.H3('''Compras con Precio''', style={'textAlign': 'center'}),
            dcc.Graph(id='input-graph-con-precio',
               config={'displayModeBar': False}
                                    )])
   elif 'btn-4' in changed_id:
      return html.Div([html.H3('''DJVE''', style={'textAlign': 'center'}),
            dcc.Graph(id='input-graph-djve',
               config={'displayModeBar': False}
                                    )])
   else:
      raise PreventUpdate


#Generador de gráfico "COMPRAS TOTALES"
@app.callback(
    Output(component_id='input-graph', component_property='figure'),
    Input(component_id='dropdown-menu', component_property='value'),
    Input('dropdown-menu-sector', 'value'),
    Input('checklist-campana', 'value'))
def update_output_div(grano, sector, campana):
   test_sample = df[df['Grano'] == grano]
   test_sample = test_sample[test_sample["Sector"] == sector]
   test_sample = test_sample[test_sample["id"]<=104]
   test_sample = test_sample[test_sample["Campaña"].isin(campana)]
   figure = px.line(test_sample,
                  x='id',
                  y='Total_Comprado',
                  color='Campaña',
                  template='simple_white')
   return figure


#Generador de gráfico "COMPRAS SIN PRECIO"
@app.callback(
    Output(component_id='input-graph-sin-precio', component_property='figure'),
    Input(component_id='dropdown-menu', component_property='value'),
    Input('dropdown-menu-sector', 'value'),
    Input('checklist-campana', 'value'))
def update_output_div(grano, sector, campana):
   test_sample = df[df['Grano'] == grano]
   test_sample = test_sample[test_sample["Sector"] == sector]
   test_sample = test_sample[test_sample["id"]<=104]
   test_sample = test_sample[test_sample["Campaña"].isin(campana)]
   figure = px.line(test_sample,
                  x='id',
                  y='Total_sin_Precio',
                  color='Campaña',
                  template='simple_white')
   return figure

#Generador de gráfico "COMPRAS CON PRECIO"
@app.callback(
    Output(component_id='input-graph-con-precio', component_property='figure'),
    Input(component_id='dropdown-menu', component_property='value'),
    Input('dropdown-menu-sector', 'value'),
    Input('checklist-campana', 'value'))
def update_output_div(grano, sector, campana):
   test_sample = df[df['Grano'] == grano]
   test_sample = test_sample[test_sample["Sector"] == sector]
   test_sample = test_sample[test_sample["id"]<=104]
   test_sample = test_sample[test_sample["Campaña"].isin(campana)]
   figure = px.line(test_sample,
                  x='id',
                  y='Total_con_Precio',
                  color='Campaña',
                  template='simple_white')
   return figure


#Generador de gráfico "DJVE"
@app.callback(
    Output(component_id='input-graph-djve', component_property='figure'),
    Input(component_id='dropdown-menu', component_property='value'),
    Input('dropdown-menu-sector', 'value'),
    Input('checklist-campana', 'value'))
def update_output_div(grano, sector, campana):
   test_sample = df[df['Grano'] == grano]
   test_sample = test_sample[test_sample["Sector"] == "Total"]
   test_sample = test_sample[test_sample["id"]<=104]
   test_sample = test_sample[test_sample["Campaña"].isin(campana)]
   figure = px.line(test_sample,
                  x='id',
                  y='DJVE_Acumuladas',
                  color='Campaña',
                  template='simple_white')
   return figure


#callback de todas o ninguna
@app.callback(
    Output("checklist-campana", "value"),
    Input("all-checklist", "value")
)
def sync_checklists(all_selected):
   if all_selected == "Todas":
      value = ['08/09','09/10','10/11','11/12','12/13','13/14','14/15','15/16','16/17','17/18','18/19','19/20','20/21', '21/22']
      return value
   if all_selected == "Últimas 3":
      value = ['19/20','20/21', '21/22']
      return value
   if all_selected == "Últimas 5":
      value = ['17/18','18/19','19/20','20/21', '21/22']
      return value
   #if all_selected == "Ninguna":
   #   value = []
   #   return value     
   else:
      raise PreventUpdate



#Run and see L€ M@GiC
if __name__ == '__main__':
   app.run_server(debug=True)