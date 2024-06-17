
# app.py
import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, State, callback_context, dash_table, no_update
import dash_table
import dash_ag_grid as dag
import dash_html_components as html
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

import pandas as pd
import numpy as np
import os

import base64
import tempfile
import logging

import base64

cc = 'rgba(0, 0, 0, 0)' #'#000000'
def read_image(image_path):
    with open(image_path, 'rb') as f:
        encoded_image = base64.b64encode(f.read()).decode('ascii')
    # return "data:image/jpeg;base64,{}".format(encoded_image)
    img1 = "data:image/jpeg;base64,{}".format(encoded_image)
    fig = go.Figure()
    fig.add_layout_image(dict(source=img1, xref="x", yref="y", x=0, y=1, sizex=1, sizey=1, xanchor="left", yanchor="top", layer="below"))
    fig.add_trace(go.Scatter(x=[0, 1], y=[0,1], mode='markers'))
    fig.update_xaxes(range=[0, 1], visible=False)
    fig.update_yaxes(range=[0, 1], visible=False)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=200, plot_bgcolor=cc)
    # plot_bgcolor='rgb(255, 255, 255)',   paper_bgcolor='rgb(255, 255, 255)' # Цвет фона графика
   
    return dcc.Graph(figure=fig)

image_path = 'data/2.jpg'
img_plot = read_image(image_path)


#  cd UI/     mkvirtualenv der           workon der          python dbc.py       http://127.0.0.1:8080/
#   http://127.0.0.

csv = 'data/test.csv'
columns = ['CLAIM_ID', 'CUSTOMER_ID', 'CLAIM_DATE', 'CLAIM_TYPE','CLAIM_DESCRIPTION', 'DOC_NUM', 'MATNR', 'QUANTITY', 'UOM',
            'CLAIM_AMOUNT', 'CLAIM_STATUS', 'CREATION_DATE', 'LAST_UPDATE_DATE','DOC_REF']
df = pd.read_csv(csv)

status_counts = df['CLAIM_STATUS'].value_counts()
N = sum(status_counts)
Ni = [status_counts['OPEN'], status_counts['IN_PROGRESS'], status_counts['CLOSED']]

def df_i(df,i):
    return pd.DataFrame({'Parameters':df.columns,'Values':df.iloc[i].to_list()})
df1 = df_i(df,0)

# print(df.columns)
print(Ni, N, df1['Values'][10])

mask_names = {1:'mask=1 - flush', 2:'mask=2 - camel', 3:'mask=3 - filling', 4:'mask=4 - urination'}
mask_options  = [{'label': v, 'value': k} for k, v in mask_names.items()]

mask_colors =  {0: '#BDBDBD', 1: 'cyan', 2: '#00FF00',  3: 'magenta',   4:'yellow'}
# print(mask_options[0]['label'])


c_gray_all = ['#FFFFFF', '#FAFAFA', '#F2F2F2', '#E6E6E6', '#D8D8D8', '#BDBDBD', '#A4A4A4', '#848484', '#6E6E6E', '#585858', '#424242', '#2E2E2E', '#1C1C1C', '#151515', '#000000']
c_gray   = ['#FFFFFF','#F2F2F2','#D8D8D8','#A4A4A4','#6E6E6E','#2E2E2E','#000000','#000000']
c_green  = ['#FFFFFF','#EEF8E3','#B0DC7A','#7FBD32','#496D1D','#29410B','#1B2513','#000000']
c_red    = ['#FFFFFF','#FFE2DC','#FFB09F','#E57E66','#CC4B2E','#581B0E','#240B05','#000000']
c_yellow = ['#FFFFFF','#F3D792','#EDC35A','#C89516','#654C0B','#271F0B','#000000','#000000']
c = c_red;      # 0(wh) 1 2 3 4 5 6(bl) 
cb1, cb2, cb3, bw =c[2], c[4], c[7], '1px' #c[5], c[0]
c_status = ['#F5A9A9','#F2F5A9','#A9F5A9']
tabs_style = {'backgroundColor':c[2], 'color':c[4], 'height':'40px',  'borderBottom':'2px solid white', 'padding': '2px', 'fontSize': '22px', 'fontSize': '18px'}
tab_selected_style = {'backgroundColor':c[4], 'color':c[2], 'height':'40px', 'padding': '1px', 'fontSize': '22px', 'fontWeight': 'bold'}




# =========================== Dash ==========================================

table = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'),
    page_size=20,
    style_table={'height': '400px', 'overflowY': 'auto'},
    style_header={'backgroundColor': c[2], 'fontWeight': 'bold'},
    style_cell={'textAlign': 'left'},
)


progress_status = dbc.Progress([
        dbc.Progress(value=100*Ni[0]/N, color=c_status[0], bar=True, style={"color": "black"}, label=f'OPEN = {Ni[0]}'),
        dbc.Progress(value=100*Ni[1]/N, color=c_status[1], bar=True, style={"color": "black"}, label=f'IN_PROGRESS = {Ni[1]}'),
        dbc.Progress(value=100*Ni[2]/N, color=c_status[2], bar=True, style={"color": "black"}, label=f'CLOSED = {Ni[2]}')], className="mb-3", style={"height": "30px"})

H_tbl = '85vh'
tbl_div = html.Div(
    dash_table.DataTable(
        id="tbl_data",
        columns=[{"name": col, "id": col} for col in df.columns],
        data=df.to_dict("records"),
        editable=True,
        row_selectable="single",
        selected_rows=[0],
        style_cell={'textAlign': 'left'},
        fixed_rows={'headers': True},
        # fixed_rows={'headers': True},
        style_table={'height': '80vh', 'overflowY': 'auto'},
        fill_width=True,
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        # style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': c[2]}], IN_PROGRESS
        style_data_conditional=[{ 'if': {'filter_query': '{CLAIM_STATUS} = "OPEN"'}, 'backgroundColor': c_status[0]},
                                { 'if': {'filter_query': '{CLAIM_STATUS} = "IN_PROGRESS"'}, 'backgroundColor': c_status[1]},
                                { 'if': {'filter_query': '{CLAIM_STATUS} = "CLOSED"'}, 'backgroundColor': c_status[2]}],

    ), style={'overflowY': 'scroll', 'height': H_tbl })



table1 = dbc.Table.from_dataframe(df1, id="tbl_1", striped=True, bordered=True, hover=True, size='sm', color='danger')
# df, id="id_tbl" striped=True, bordered=True,  hover=True, responsive=True, dark=True, borderless=False, size="sm", className="my-custom-class", 
                    #  чередов. границы.        курсора     прокрутка        тем.стиль  границы           md (sm/lg)


buttons = html.Div([
    dbc.Button("Cansel", size="sm", outline=True, color="danger", className="me-1"),
    dbc.Button("Edit", size="sm", outline=True, color="warning", className="me-1"),
    dbc.Button("Aprove", size="sm", outline=True, color="success")], className="d-grid gap-2 d-md-flex justify-content-md-end")

# image1 = dbc.Card(dbc.CardImg(src='1.jpg', top=True), style={"height": "80px"})


form2 = html.Div(
        [table1, img_plot, buttons],
        style={
            "width": "100%", "height": H_tbl, 
            "overflowY": "scroll", "overflowX": "auto",  # Enable vertical horizontal scrolling
            "border": "1px solid #ccc",                  # Optional border for better visualization
        },
    )

list_2 = [html.H1("Claims Data"),
        dbc.Row([dbc.Col([progress_status, tbl_div], style={'width': '70%'}), dbc.Col(form2, style={'width': '30%'}) ])]


# ======================== list_1 ============================================
s_form = {'width':'20%'}
input_groups = html.Div([
    dbc.InputGroup(
        [dbc.InputGroupText("Name", style=s_form),   dbc.Input(id='Customer_Name', placeholder="Name")],
        className="mb-3"),
    dbc.InputGroup(
        [dbc.InputGroupText("Contact", style=s_form),   dbc.Input(id='Customer_Contact', placeholder="Contact")],
        className="mb-3"),
    dbc.InputGroup([
        dbc.InputGroupText("Claim type", style=s_form),   
        dbc.Select(id='CLAIM_TYPE', options=[{"label": "RETURN", "value": 'RETURN'}, {"label": "COMPLAINT", "value":'COMPLAINT'}, {"label": "DISPUTE", "value":'DISPUTE'}], value="RETURN")
        ],className="mb-3"),

    dbc.InputGroup([
        dbc.InputGroupText("QUANTITY", style=s_form),   dbc.Input(id='QUANTITY', value=1, placeholder="QUANTITY", type="number"),
        dbc.InputGroupText("UOM", style=s_form), 
        dbc.Select(id='UOM', options=[{"label": "Piece", "value": 'Piece'}, {"label": "Bottle", "value":'Bottle'}, {"label": "Box", "value":'Box'}], value="Piece"),
        dbc.InputGroupText("AMOUNT", style=s_form),   dbc.Input(id='CLAIM_AMOUNT', value=1, placeholder="CLAIM_AMOUNT", type="number"),
        ], className="mb-3"),

    dbc.InputGroup([dbc.InputGroupText("CLAIM_DESCRIPTION", style=s_form),  dbc.Textarea(id='CLAIM_DESCRIPTION')],  className="mb-3"),
    
    dbc.Label("Document file"),
    dbc.InputGroup([ 
        html.Div( dcc.Upload( id='upload_doc', children= dbc.Button("Upload doc", id='btn_upload_doc', color="light", style={'width':'100%'})), style=s_form),
        dbc.Input(id='Document_file', placeholder="Document file") ],  className="mb-3"),

    dbc.Label("Claim photo"),
    dbc.InputGroup([
        html.Div( dcc.Upload(  id='upload_img', children=dbc.Button("Upload photo", id='btn_upload_img', color="light", style={'width':'100%'})), style=s_form),
        dbc.Input(id='Claim_photo', placeholder="Claim_photo") ],  className="mb-3"),

    dbc.Button("Create claim", id='btn_create_claim', className="me-1", color='info', style=s_form)
    ], style={'backgroundColor':'gray', 'width': '50%', 'padding':20})

df1c = pd.DataFrame({"col1": []})
df2c = pd.DataFrame({"col1": []})
tbl1_claim = dbc.Table.from_dataframe(df1c, id="tbl_claim_1", striped=True, bordered=True, hover=True, size='sm', color='danger')
tbl2_claim = dbc.Table.from_dataframe(df2c, id="tbl_claim_2", striped=True, bordered=True, hover=True, size='sm', color='danger')


form1 = html.Div(
        [html.H1("Claims"), input_groups, tbl1_claim, tbl2_claim, img_plot],
        style={
            "width": "100%", "height": H_tbl, 
            "overflowY": "scroll", "overflowX": "auto",  # Enable vertical horizontal scrolling
            "border": "1px solid #ccc",                  # Optional border for better visualization
        },
    )           


list_1 = [form1,
          html.Br()]


# ======================== layout ============================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, "assets/styles.css"]) 
app.layout = dbc.Container(
    [
        dbc.Tabs([
            dbc.Tab(list_1, label="Tab 1: Claims"),
            dbc.Tab(list_2, label="Tab 2: Claims Data"),
        ]),
  
    ],
    fluid=True,
)

# ======================== app ============================================


def save_file(name, content):
    """Сохранение загруженного файла."""
    UPLOAD_DIRECTORY = "data"
    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.b64decode(data))

@app.callback(
    Output('Document_file', 'value'),    Input('upload_doc', 'contents'),    State('upload_doc', 'filename'))
def update_output(contents, filename):
    if contents is not None:
        save_file(filename, contents)
        return filename
    return ""

@app.callback(
    Output('Claim_photo', 'value'),    Input('upload_img', 'contents'),    State('upload_img', 'filename'))
def update_output(contents, filename):
    if contents is not None:
        save_file(filename, contents)
        return filename
    return ""



@app.callback(
    Output('tbl_claim_1', 'children'), Output('tbl_claim_2', 'children'),
    Input('btn_create_claim', 'n_clicks'),
    State('Customer_Name', 'value'), State('Customer_Contact', 'value'), State('CLAIM_TYPE', 'value'), State('QUANTITY', 'value'),
    State('UOM', 'value'), State('CLAIM_AMOUNT', 'value'), State('CLAIM_DESCRIPTION', 'value'), State('Document_file', 'value'), State('Claim_photo', 'value'))
def create_claim(n_clicks, name, contact, claim_type, quantity, uom, amount, description, doc_file, claim_photo):
    if n_clicks is None:
        return "", ""
    # 'CLAIM_ID', 'CUSTOMER_ID', 'CLAIM_DATE', 'DOC_NUM', 'MATNR', 'CLAIM_STATUS', 'CREATION_DATE', 'LAST_UPDATE_DATE'
    # 'CLAIM_TYPE' 'CLAIM_DESCRIPTION', 'QUANTITY', 'UOM', 'CLAIM_AMOUNT', "DOC_REF", "IMG_REF"

    data = {
        "CUSTUMER_NAME": [name],            "CUSTUMER_CONTACT": [contact],      "CLAIM_TYPE": [claim_type],    
        "QUANTITY": [quantity],             "UOM": [uom],                       "CLAIM_AMOUNT": [amount],
        "CLAIM_DESCRIPTION": [description], "DOC_REF": [doc_file],              "IMG_REF": [claim_photo] }
    df_1 = pd.DataFrame(data)
    tbl_01 = dbc.Table.from_dataframe(df_1, id="tbl_claim_1", striped=True, bordered=True, hover=True, size='sm', color='danger')

    def create_info(ind):
        ind = f'{ind:05}'
        res = [f'clime{ind}', f'custumer{ind}', '01.01.2024', f'doc{ind}', f'mat{ind}', 'OPEN', '01.01.2024', '01.01.2024']
        return res
    res = create_info(n_clicks)

    add_data = {'CLAIM_ID':[res[0]], 'CUSTOMER_ID':[res[1]], 'CLAIM_DATE':[res[2]], 'DOC_NUM':[res[3]], 'MATNR':[res[4]], 'CLAIM_STATUS':[res[5]], 'CREATION_DATE':[res[6]], 'LAST_UPDATE_DATE':[res[7]]}
    df_2 = pd.DataFrame(add_data)
    tbl_02 = dbc.Table.from_dataframe(df_2, id="tbl_claim_2", striped=True, bordered=True, hover=True, size='sm', color='danger')

    return tbl_01, tbl_02


@app.callback(
    Output("tbl_1", "children"),
    [Input('tbl_data', 'selected_cells')],
    [State("tbl_1", "children")])
def display_selected_row(selected_cells, curent_tbl):
    if selected_cells:
        row_number = selected_cells[0]['row']
        df_row = df_i(df,row_number)
        col_t1 = "danger"
        if df_row['Values'][10] == "OPEN": col_t1 = "danger"
        if df_row['Values'][10] == "IN_PROGRESS": col_t1 = "warning"   
        if df_row['Values'][10] == "CLOSED": col_t1 = "success"
        new_table = dbc.Table.from_dataframe(df_row, striped=True, bordered=True, hover=True, size='sm', color=col_t1)
        return new_table

    else:
        return curent_tbl

# @app.callback(Output("output", "children"), [Input("radios", "value")])
# def display_value(value):
#     return f"Selected value: {value}"



# Запуск приложения
if __name__ == '__main__':
    app.run_server(port=8090, debug=True)
