# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


from dash import Dash, dcc, html, Input, Output, callback,dash_table, State
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import warnings
import json
from koboextractor import KoboExtractor
import dash_bootstrap_components as dbc
# Suppress FutureWarning messages
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None 

MUN_COD=pd.read_csv('MUN_COD.txt',delimiter='\t')
# df1 = pd.read_csv('05_12_2023_11_26\Actores_05_12_2023_11_26.csv')
# df2 = pd.read_csv('05_12_2023_11_26\Conflicto_05_12_2023_11_26.csv')
# df3 = pd.read_csv('05_12_2023_11_26\Mesas_05_12_2023_11_26.csv')

token = '3d81f96d16fbc8adc419e90fd5e5684bc58445ff'
kobot = KoboExtractor(token, 'https://kf.kobotoolbox.org/api/v2')
form_id = 'aJThss9cZcGfrUrm7rqcYa'
    # nombre = tp_fichas[l]
datt = kobot.get_data(form_id, query=None, start=None, limit=None, submitted_after=None)
df2 = pd.json_normalize(datt['results'])

MUN_dict=MUN_COD[['Identificacion/municipio','Municipio']].set_index('Identificacion/municipio').to_dict()['Municipio']
DEP_dict=MUN_COD[['Identificacion/municipio','Departamento']].set_index('Identificacion/municipio').to_dict()['Departamento']

# df2['Localizacion/municipio']=df2['Localizacion/municipio'].astype('int')

# df2['Municipio']=df2['Localizacion/municipio'].astype('int').map(MUN_dict)
# df2['Departamento']=df2['Localizacion/municipio'].astype('int').map(DEP_dict)
# for i,col in zip([df1,df2,df3],['Identificacion/municipio','Localizacion/municipio','group_ke65b09/Municipio']):
#     i['Municipio']=i[col].map(MUN_dict)
#     i['Departamento']=i[col].map(DEP_dict)

KEY_LOC=[]
VAL_LOC=[]
for i in MUN_COD[['Departamento','Municipio']].values:
    KEY_LOC.append(i[1]+', '+i[0])
    VAL_LOC.append(i)
for i in MUN_COD['Departamento'].unique():
    KEY_LOC.append(i)
    VAL_LOC.append(i)
LOC=dict()
for key,value in zip(KEY_LOC,VAL_LOC):
    LOC[key]=value


dftime=df2[np.isin(df2['Inicio/Tipo_de_Reporte'],['registro_inicio','alerta_temprana','otros_reportes_actividades'])]
dfsegcierr=df2[np.isin(df2['Inicio/Tipo_de_Reporte'],['cierre','seguimiento_conflictividad','seguimiento_AT'])]
dftime['Municipio']=dftime['Localizacion/municipio'].astype('int').map(MUN_dict)
dftime['Departamento']=dftime['Localizacion/municipio'].astype('int').map(DEP_dict)
ls_all=[]
for _id,cocal,coalt,init,zon,dep,mun,munc in zip(dftime['_id'],
                    dftime['Conflicto/Codificaciones/calculation'],
                    dftime['Alerta/calculation_001'],
                    dftime['Inicio/Fecha_de_ocurrencia_del_evento'],
                    dftime['Localizacion/zona'],
                    dftime['Departamento'],
                    dftime['Municipio'],
                    dftime['Localizacion/municipio']
                    ):
    fil=[np.any(coinc) for coinc in np.isin(dfsegcierr[['Seg_Alerta/C_digo_nico_de_Ale_igina_el_seguimiento',
                                            'Cierre/C_digo_nico_de_Regi_e_la_Alerta_Temprana',
                                            'Seg_Conflicto/C_digo_nico_de_Regi_ro_de_Conflictividad',
                                            'Conflicto/Carac/Actuaciones/Diligencie_el_c_digo_n_de_Alerta_temprana',
                                            'Conflicto/Codificaciones/calculation',
                                            'Alerta/calculation_001']],[cocal,_id,coalt])]
    dftime_fil=dfsegcierr[fil]
    dftime_fil['Municipio']=mun
    dftime_fil['Departamento']=dep
    dftime_fil['Localizacion/zona']=zon
    dftime_fil['Localizacion/municipio']=munc
    if len(dftime_fil)>0:
        ls_all.append(dftime_fil)
df_all=pd.concat(ls_all)
df2=pd.concat([df_all,dftime])

df2['Localizacion/municipio']=df2['Localizacion/municipio'].astype('int')

dep=KEY_LOC[-33:-1]
mun=KEY_LOC[0:-33]

mun_loc=pd.read_csv('mun_loc.csv',skiprows=5,delimiter=';',decimal=',')
dict_lat_mun={}
dict_lon_mun={}
cc=0
for i in mun_loc['Código Municipio'].unique():
    a=mun_loc[mun_loc['Código Municipio']==i]
    b=a[a['Tipo Centro Poblado']=='CABECERA MUNICIPAL (CM)']
    if len(b)==1:
        dict_lon_mun[i]=b['Longitud'].values[0]
        dict_lat_mun[i]=b['Latitud'].values[0]
    else:
        b=a[a['Tipo Centro Poblado']=='CABECERA CORREGIMIENTO DEPARTAMENTAL (CD)']
        dict_lon_mun[i]=b['Longitud'].values[0]
        dict_lat_mun[i]=b['Latitud'].values[0]

df2['latitud']=df2['Localizacion/municipio'].map(dict_lat_mun)
df2['longitud']=df2['Localizacion/municipio'].map(dict_lon_mun)

# for i,col in zip([df1,df2,df3],['Identificacion/municipio','Localizacion/municipio','group_ke65b09/Municipio']):
#     i['latitud']=i[col].map(dict_lat_mun)
#     i['longitud']=i[col].map(dict_lon_mun)

df2['lat']=df2['_geolocation'].apply(lambda x : str(x).split(',')[0].replace('[',''))
df2['lon']=df2['_geolocation'].apply(lambda x : str(x).split(',')[1].replace(']',''))
df2['lat'][df2['lat']=='None']=df2['latitud'][df2['lat']=='None']
df2['lon'][df2['lon']=='None']=df2['longitud'][df2['lon']=='None']
df2['FECHA - HORA UTC']=pd.to_datetime(df2['Inicio/Fecha_de_ocurrencia_del_evento'],infer_datetime_format=False)

# Filtso crossfilterig
columns_confc=[
'Conflicto/Nombre_del_Proyecto',
'Inicio/Fecha_de_ocurrencia_del_evento',
#'Conflicto/Segmento_Afectado_Hidrocarburos',
'Conflicto/Subsector',
'Conflicto/Carac/Categor_a_del_conflicto_Dime',
'Conflicto/Carac/Principales_actores_involucrad',
'Conflicto/Carac/Descripci_n_de_los_A_dentes_del_Conflicto',
'Conflicto/Carac/Descripci_n_de_los_H_tuales_del_conflicto',
'Conflicto/Carac/Afectaciones/Tipo_de_Acciones',
'Conflicto/Carac/Actuaciones/Categor_as_de_acciones_realiza',
'Conflicto/Carac/Compromisos/Descripci_n_de_compr_tividades_a_ejecutar',
'Conflicto/Carac/Compromisos/Nombre_de_la_s_enti_s_y_o_actividad_es',]
columns_val_confc=['Proyecto',
'Fecha',
'Subsector',
'Categoria',
'Actores',
'Antecedentes',
'Descripción',
'Acciones',
'Categoria de las acciones',
'Compromisos',
'Entidades'
]
columns_alertas=['Alerta/Nombre_del_Proyecto_001',
'Inicio/Fecha_de_ocurrencia_del_evento',
'Alerta/Tipo_de_Alerta_Temprana',
'Alerta/Subsector_generador_de_la_Aler',
'Alerta/Tema_Clave_o_Princip_a_la_Alerta_Temprana',
'Alerta/Conductas_vulneratorias_y_o_in',
'Alerta/Afectaciones_y_o_impactos_en_o',
'Alerta/Principales_actores_involucrad_001',
'Alerta/Indique_cu_les_son_las_fuentes_002',
]
columns_val_alertas=['Proyecto',
'Fecha',
'Tipo',
'Subsector',
'Tema clave',
'Conductas vulneratorias',
'Afectaciones',
'Actores',
'Fuente',
]
columns_sconfc=[
'Seg_Conflicto/C_digo_nico_de_Regi_ro_de_Conflictividad',
'Inicio/Fecha_de_ocurrencia_del_evento',
'Seg_Conflicto/Descripci_n_de_nuevo_hechos_del_conflicto',
'Seg_Conflicto/Categor_as_de_acciones_realiza_001',
'Seg_Conflicto/Compromisos_seg/Descripci_n_de_compr_tividades_a_ejecutar_001',
'Seg_Conflicto/Compromisos_seg/Nombre_de_la_s_enti_s_y_o_actividad_es_001',
'Seg_Conflicto/Tipo_de_Acciones_001',
'Seg_Conflicto/Indique_cu_les_son_las_fuentes_001',
]
columns_val_sconfc=[
'Código',
'Fecha',
'Descripción',
'Acciones',
'Compromisos',
'Entidades',
'Tipo de acciones',
'Fuentes',
]
columns_cierr=[
'Cierre/C_digo_nico_de_Regi_e_la_Alerta_Temprana',
'Inicio/Fecha_de_ocurrencia_del_evento',
'Cierre/Tipo_de_Cierre',
'Cierre/Describa_informaci_n_ad_o_Alerta_Temprana',
]
columns_val_cierr=[
'Código',
'Fecha',
'Tipo',
'Descripción'
]
columns_salerta=[
'Seg_Alerta/C_digo_nico_de_Ale_igina_el_seguimiento',
'Inicio/Fecha_de_ocurrencia_del_evento',
'Seg_Alerta/Descripci_n_de_Actua_a_la_Alerta_Temprana',
'Seg_Alerta/Actuaciones_realizadas',
'Seg_Alerta/Describa_los_comprom_ME_y_otras_entidades',
'Seg_Alerta/Nombre_las_entidades_as_en_el_seguimiento'
]
columns_val_salerta=[
'Código',
'Fecha',
'Descripción',
'Acciones',
'Compromisos',
'Entidades'
]
columns_otro=[
'Otro/Otros_reportes_actividades',
'Inicio/Fecha_de_ocurrencia_del_evento',
'Otro/Subsector_001',
'Otro/Descripci_n_de_la_actividad',
'Otro/Principales_actores_involucrad_002',
]
columns_val_otro=[
'Tipo',
'Fecha',
'Subsector',
'Descripción',
'Actores',
]
columns_space=[
'Alerta/Conductas_vulneratorias_y_o_in',
'Alerta/Afectaciones_y_o_impactos_en_o',
'Alerta/Principales_actores_involucrad_001',
'Alerta/Indique_cu_les_son_las_fuentes_002',
'Conflicto/Segmento_Afectado_Hidrocarburos',
'Conflicto/Carac/Principales_actores_involucrad',
'Conflicto/Carac/Afectaciones/Tipo_de_Acciones',
'Conflicto/Carac/Afectaciones/Indique_cu_les_son_las_fuentes',
'Conflicto/Carac/Actuaciones/Categor_as_de_acciones_realiza'
]
columns_code_seg=['Seg_Alerta/C_digo_nico_de_Ale_igina_el_seguimiento',
'Cierre/C_digo_nico_de_Regi_e_la_Alerta_Temprana',
'Seg_Conflicto/C_digo_nico_de_Regi_ro_de_Conflictividad',
'Conflicto/Carac/Actuaciones/Diligencie_el_c_digo_n_de_Alerta_temprana',
'Conflicto/Codificaciones/calculation',
'Alerta/calculation_001']

app = Dash(__name__)
server=app.server
# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options


card_main=html.Div([
    html.H5(children='''
        Filtra por las diferentes columnas
    '''),
    html.H5(children='''
        Departamento
    '''),
    dcc.Dropdown(
        dep,
        [],
        multi=True,
        id='dep_id',
        style={'color': 'black'}
    ),
    html.H5(children='''
        Fecha
    '''),
    html.Div(dcc.DatePickerRange(
            id='DATE',
            start_date_placeholder_text="Start Date",
            end_date_placeholder_text="End Date",
            calendar_orientation='horizontal',
            start_date=df2['FECHA - HORA UTC'].min(),
            end_date=df2['FECHA - HORA UTC'].max(),
            day_size=30,
            min_date_allowed=df2['FECHA - HORA UTC'].min(),
            max_date_allowed=df2['FECHA - HORA UTC'].max(),
            # with_portal=True,
            # persistence=True,
            #initial_visible_month=df_sismos['FECHA - HORA UTC'].min(),
            # reopen_calendar_on_clear=False
        ),style={'font-size': '12px'}),
    html.H5(children='''
        Conteo
    ''',id='conteo_'),
    dbc.Tooltip(
    "Filtro de conteo por Departamento, Municipio y Localización/zona. Representado en los graficos de barras en el eje de abcisas.",
    target='conteo_',
    ),
    dcc.Dropdown(
        ['Municipio','Departamento','Localizacion/zona'],
        'Departamento',
        multi=False,
        id='count_id',
        style={'color': 'black'}
    ),
    html.H5(children='''
        Simbolo
    '''),
    dcc.Dropdown(
        ['Departamento','Localizacion/zona','Ninguno'],
        'Ninguno',
        multi=False,
        id='shape_id',
        style={'color': 'black'}
    ),
    html.H5(children='''
        Filtro Linea de Tiempo
    '''),
    dcc.Dropdown(
        ['Tipo de seguimiento','Municipio','Departamento','Localizacion/zona'],
        'Tipo de seguimiento',
        multi=False,
        id='time_id',
        style={'color': 'black'}
    ),
            html.Br(),
            html.Button('¡Actualizar!', id='submit-val', n_clicks=0,style={'background-color': 'white',}),
                    #  dbc.CardImg(src="assets\logos.png", bottom=True, alt='Logos_convenio_tripartito',)    
    dcc.Markdown('''
        * ¡Bienvenido al visor ...!
        * OAAS
        * Citese como: OAAS...
    '''),], 
            
        className="sidebar",
        id='sidebar')


card_graph=dcc.Graph(
        id='geo2',
        figure={},
    ),


tables=html.Div([
    html.H5('Tabla de Geoinformación (oprime un elemento en el mapa)'),
    html.Div([
        html.H5('Conflictos'),
        dash_table.DataTable(style_table={
            # 'maxHeight': 600,
            'overflowY': 'auto',
            'overflowX': 'scroll'
                                           } ,id='tbl_confc',
                             style_cell={
        'textAlign': 'left',
        'backgroundColor': 'rgb(30, 30, 30)',
        'color': 'white',
        'font-family':"Poppins",
        "whiteSpace": "pre-line",
                                        },),
        ],id='confc_block',style= {'display': 'none'},),
    #Alertas -----------------------------------------
    html.Div([
        html.H5('Alertas Tempranas'),
        dash_table.DataTable(style_table={
            # 'maxHeight': 600,
            'overflowY': 'auto',
            'overflowX': 'scroll'
                                           } ,id='tbl_alerta',
                             style_cell={
        'textAlign': 'left',
        'backgroundColor': 'rgb(30, 30, 30)',
        'color': 'white',
        'font-family':"Poppins",
        "whiteSpace": "pre-line",
                                        },),
        ],id='alerta_block',style= {'display': 'none'}),
    #Seguimiento Conflictos -----------------------------------------
    html.Div([
        html.H5('Seguimiento conflictos'),
        dash_table.DataTable(style_table={
            # 'maxHeight': 600,
            'overflowY': 'auto',
            'overflowX': 'scroll'
                                           } ,id='tbl_sconfc',
                             style_cell={
        'textAlign': 'left',
        'backgroundColor': 'rgb(30, 30, 30)',
        'color': 'white',
        'font-family':"Poppins",
        "whiteSpace": "pre-line",
                                        },),
        ],id='sconfc_block',style= {'display': 'none'}),
    #Seguimiento Alertas-----------------------------------------
    html.Div([
        html.H5('Seguimiento Alertas'),
        dash_table.DataTable(style_table={
            # 'maxHeight': 600,
            'overflowY': 'auto',
            'overflowX': 'scroll'
                                           } ,id='tbl_salerta',
                             style_cell={
        'textAlign': 'left',
        'backgroundColor': 'rgb(30, 30, 30)',
        'color': 'white',
        'font-family':"Poppins",
        "whiteSpace": "pre-line",
                                        },),
        ],id='salerta_block',style= {'display': 'none'}),
    #Seguimiento Alertas-----------------------------------------
    html.Div([
        html.H5('Cierres'),
        dash_table.DataTable(style_table={
            # 'maxHeight': 600,
            'overflowY': 'auto',
            'overflowX': 'scroll'
                                           } ,id='tbl_cierr',
                             style_cell={
        'textAlign': 'left',
        'backgroundColor': 'rgb(30, 30, 30)',
        'color': 'white',
        'font-family':"Poppins",
        "whiteSpace": "pre-line",
                                        },),
        ],id='cierr_block',style= {'display': 'none'}),
    #Otros-----------------------------------------
    html.Div([
        html.H5('Otros'),
        dash_table.DataTable(style_table={
            # 'maxHeight': 600,
            'overflowY': 'auto',
            'overflowX': 'scroll'
                                           } ,id='tbl_otro',
                             style_cell={
        'textAlign': 'left',
        'backgroundColor': 'rgb(30, 30, 30)',
        'color': 'white',
        'font-family':"Poppins",
        "whiteSpace": "pre-line",
                                        },),
        ],id='otro_block',style= {'display': 'none'}),
    ]) #style_table={'maxHeight': 600} ,

card_function=dbc.Card(
    dbc.CardBody('Hola'
    ))

card_references=dbc.Card(
    dbc.CardBody('Hola'
    ))

card_explication_sem=dbc.Card(
    dbc.CardBody([
        html.H2("¿Qué es el semáforo sísmico?", className="card-title"),
        html.H6("El semáforo sísmico es un mecanismo desarrollado por el Servicio Geológico Colombiano (SGC) para la toma de decisiones en el desarrollo de las operaciones de las Pruebas Piloto de Investigación Integral (PPII). Para el semáforo se han definido cuatro colores: verde, amarillo, naranja y rojo. Adicionalmente, se presenta enmarcado dentro de dos volúmenes cilíndricos denominados volúmen de monitoreo (correspondiente al cilíndro externo) y volúmen de suspensión (correspondiente al cilindro interno), definidos de acuerdo con la propuesta del semáforo sísmico (Dionicio et al., 2020). Los volumenes cilíndricos cuentan con una profundidad de 16 km,  radio interno de dos veces la profundidad medida del pozo (Dionicio et al., 2020) y externo de dos veces la profundidad medida del pozo más veinte kilómetros (2h + 20km), de acuerdo con la Resolución 40185 de 2020 del Ministerio de Minas y Energía.",
            className="card-text"),
        html.H6("La clasificación en colores del semáforo se realiza para cada uno de los diferentes rangos de magnitud de los eventos sísmicos que entren dentro de los volúmenes cilíndricos. Los rangos de magnitud son m0, m1, m2, m3 y m4, que tendrán diferentes estados del semáforo, son dependientes del número de sismos registrados diarios para cada uno de esos rangos, cuyos valores se comparan con los parámetros definidos en el documento propuesto para el semáforo sísmico, con el fin de obtener el correspondiente color del semáforo (Dionicio et al., 2020).", 
            className="card-text"),
        # html.Div(
        # html.Img(

        #                     src="assets\OAAS_cut.png",

        #                     id="Tabla7a-image",

        #                     style={

        #                         "height": "auto",
        #                         "max-width": "1000px",
        #                         "margin-top": "5px",
        #                         "display":"block",
        #                         "margin-left": "auto",
        #                         "margin-bottom": "5px",

        #                     },

        #                 )),
        # html.Div(html.Img(

        #                     src="assets\OAAS_cut.png",

        #                     id="Tabla7b-image",

        #                     style={
        #                         "height": "auto",
        #                         "max-width": "1000px",
        #                         "margin-top": "5px",
        #                         "display":"block",
        #                         "margin-left": "auto",
        #                         "margin-bottom": "5px",
        #                     },

        #                 )),
        # dbc.CardImg(src="assets\Tabla7a.png", bottom=True, alt='Tabla7a',),
        # dbc.CardImg(src="assets\Tabla7b.png", bottom=True, alt='Tabla7b',),
        html.H6("Adicionalmente, a medida que se desarrolla el monitoreo diario de las actividades, se registra la acumulación de alertas para cada uno de los colores del semáforo sísmico, donde se asigna una puntuación para cada color de 0 para verde, 1 para amarillo y 3 para naranja (Dionicio et al., 2020). A partir de la puntuación acumulada mensual, se definen las acciones propuestas acordes con el esquema de puntuación del seguimiento mensual de sismicidad montoreada de los PPII (Dionicio et al., 2020).", 
            className="card-text"),
        # html.Img(

        #                     src="https://saaeuyncprdblob.blob.core.windows.net/drupal-blob/UNAL/Imagenes/Dash/Modelo3D/assets/Tabla8.png",

        #                     id="Tabla8-image",

        #                     style={
        #                         "height": "auto",
        #                         "max-width": "1000px",
        #                         "margin-top": "5px",
        #                         "display":"block",
        #                         "margin-left": "auto",
        #                         "margin-bottom": "5px",

        #                     },

        #                 ),
        #dbc.CardImg(src="assets\Tabla8.png", bottom=True, alt='Tabla8',),
    ]))

app.layout = html.Div(children=[
     html.Div(

            [    
                html.Img(
                    src="assets\OAAS_cut.png",
                    id="plotly-image",
                    className="logo-CdT"
                ),                   

                html.H3(

                    "BETA Visor de datos conflictos - Observatorio de la Oficina de Asuntos Sociales y Ambientales",
                    className="model-title"

                    # style={"margin-bottom": "0px", 'textAlign': 'center','font-weight':'bold'},
                ), 

            ], className="header", id='header'

            ),
        html.Div(
            [
                html.Div(
            [
                dcc.Loading(
                id="loading-1",
                type="cube",
                fullscreen=True,
                style={'background-color': '#002c35',
                       'background-image': 'assets\OAAS_cut.png',
                       'opacity':'1', 
                       'background-repeat': 'space',
                       'background-size': '200px 200px',},
                children=html.Div(id="loading-output-1"),
                debug=False,
                loading_state={'component_name':'Cargando...',
                            'prop_name':'Cargando...',
                            'is_loading':True}),
                card_main,
            
                

                html.Div(
                    [
                        html.Br(),
                    #  dbc.Button(html.I(), color='primary', id='btn_sidebar', size="lg"),
                    html.Div(card_graph),
                         ],
                    className="model_graph column",
                                id = 'content'
                                ),
            ],
            # justify="start",

            ),html.Div(tables,className="model_table column",style={ "overflow": "scroll"}),


            ], className="row flex-display",
            id = 'div_slider'
        ),
    # card_main,
    # tables,
    html.H2(children='Datos Generales'),
    dcc.Graph(
        id='fig1',
        figure={},
        className='others'
    ),
    # dcc.Graph(
    #     id='geo1',
    #     figure={}
    # ),
    #html.H1(id='click-data'),#, style=styles['pre']),
    #Fin condicional ------------------------------
    html.H2(children='Conflictos'),
    dcc.Graph(
        id='fig2',
        figure={}
    ),
    html.Div([
        html.Div([
        dcc.Graph(
            id='fig9',
            figure={},
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='fig_C_segh',
            figure={},
        )],className='two_fig_2')]
             ,className='row flex-display'),
    html.Div([
        html.Div([
        dcc.Graph(
            id='fig10',
            figure={},
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='fig_C_act',
            figure={},
        )],className='two_fig_2')]
             ,className='row flex-display'),
    # dcc.Graph(
    #     id='fig10',
    #     figure={}
    # ),
    # dcc.Graph(
    #     id='fig_C_act',
    #     figure={}
    # ),
    html.Div([
        html.Div([
        dcc.Graph(
            id='fig11',
            figure={},
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='fig_C_acc',
            figure={},
        )],className='two_fig_2')]
             ,className='row flex-display'),
    # dcc.Graph(
    #     id='fig11',
    #     figure={}
    # ),
    # dcc.Graph(
    #     id='fig_C_acc',
    #     figure={}
    # ),
    html.Div([
        html.Div([
        dcc.Graph(
            id='fig12',
            figure={},
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='fig_C_info',
            figure={},
        )],className='two_fig_2')]
             ,className='row flex-display'),
    # dcc.Graph(
    #     id='fig12',
    #     figure={}
    # ),
    # dcc.Graph(
    #     id='fig_C_info',
    #     figure={}
    # ),
    html.Div([
        html.Div([
        dcc.Graph(
            id='fig13',
            figure={},
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='fig_C_catacc',
            figure={},
        )],className='two_fig_2')]
             ,className='row flex-display'),
    # dcc.Graph(
    #     id='fig13',
    #     figure={}
    # ),
    # dcc.Graph(
    #     id='fig_C_catacc',
    #     figure={}
    # ),
    html.Div([
        html.Div([
        dcc.Graph(
            id='fig15',
            figure={},
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='fig_dimall_ubi',
            figure={},
        )],className='two_fig_2')]
             ,className='row flex-display'),
    # dcc.Graph(
    # id='fig15',
    # figure={}
    # ),
    # dcc.Graph(
    #     id='fig_dimall_ubi',
    #     figure={}
    # ),
    html.Div([
        html.Div([
        dcc.Graph(
            id='fig16',
            figure={},
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='fig_dimsoc_ubi',
            figure={},
        )],className='two_fig_2')]
             ,className='row flex-display'),
    # dcc.Graph(
    #     id='fig16',
    #     figure={}
    # ),
    # dcc.Graph(
    #     id='fig_dimsoc_ubi',
    #     figure={}
    # ),
    html.Div([
        html.Div([
        dcc.Graph(
            id='fig17',
            figure={},
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='fig_dimeco_ubi',
            figure={},
        )],className='two_fig_2')]
             ,className='row flex-display'),
    # dcc.Graph(
    #     id='fig17',
    #     figure={}
    # ),
    # dcc.Graph(
    #     id='fig_dimeco_ubi',
    #     figure={}
    # ),
    html.Div([
        html.Div([
        dcc.Graph(
            id='fig18',
            figure={},
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='fig_dimam_ubi',
            figure={},
        )],className='two_fig_2')]
             ,className='row flex-display'),
    # dcc.Graph(
    #     id='fig18',
    #     figure={}
    # ),
    # dcc.Graph(
    #     id='fig_dimam_ubi',
    #     figure={}
    # ),
    dcc.Graph(
        id='fig14',
        figure={}
    ),
    html.H2(children='Alertas'),
    dcc.Graph(
        id='fig_A_Subsector',
        figure={}
    ),
    dcc.Graph(
        id='fig3',
        figure={}
    ),
    dcc.Graph(
        id='fig4',
        figure={}
    ),
    html.Div([
        html.Div([
        dcc.Graph(
            id='fig5',
            figure={},
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='fig_A_cvul',
            figure={},
        )],className='two_fig_2')]
             ,className='row flex-display'),
    # dcc.Graph(
    #     id='fig5',
    #     figure={}
    # ),
    # dcc.Graph(
    #     id='fig_A_cvul',
    #     figure={}
    # ),
    html.Div([
        html.Div([
        dcc.Graph(
            id='fig6',
            figure={},
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='fig_A_afcim',
            figure={},
        )],className='two_fig_2')]
             ,className='row flex-display'),
    # dcc.Graph(
    #     id='fig6',
    #     figure={}
    # ),
    # dcc.Graph(
    #     id='fig_A_afcim',
    #     figure={}
    # ),
    html.Div([
        html.Div([
        dcc.Graph(
            id='fig7',
            figure={},
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='fig_A_act',
            figure={},
        )],className='two_fig_2')]
             ,className='row flex-display'),
    # dcc.Graph(
    #     id='fig7',
    #     figure={}
    # ),
    # dcc.Graph(
    #     id='fig_A_act',
    #     figure={}
    # ),
    html.Div([
        html.Div([
        dcc.Graph(
            id='fig8',
            figure={},
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='fig_A_info',
            figure={},
        )],className='two_fig_2')]
             ,className='row flex-display'),
    # dcc.Graph(
    #     id='fig8',
    #     figure={}
    # ),
    # dcc.Graph(
    #     id='fig_A_info',
    #     figure={}
    # ),
    # html.Iframe(id='map',
    #             srcDoc=open('mapa_interactivo.html','r').read(), #Modificar previous 
    #             #src='mapa_interactivo.html',
    #             width='100%',
    #             height='600')
    html.Div([
                html.Div(
                    [     
    dbc.Button("¿Qué es el laboratiorio socioabiental de la OAAS?", color="#4cb286",id="function_but_xl",className="me-1", n_clicks=0),
    dbc.Button("¿Como funciona el visor?",color="#4cb286", id="semaforo_but_xl",size="sm", className="me-1", n_clicks=0),
    dbc.Button("Referencias",color="#4cb286", id="references_but_xl",size="sm", className="me-1", n_clicks=0)
    # html.Button("¿Cómo funciona?", id="function_but_xl",  className="footerButtons", n_clicks=0),
    # html.Button("¿Semáforo sísmico?", id="semaforo_but_xl", className="footerButtons", n_clicks=0),
    # html.Button("Referencias", id="references_but_xl", className="footerButtons", n_clicks=0)
    ], className='helpButtons'
    ),
                # html.Hr(),
                # html.Img(
                # src="assets\OAAS_cut.png",
                # id="logos-image"),
        ],id='footer'),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(" ")),
            dbc.ModalBody(card_function),
        ],
        id="function_mod_xl",
        # fullscreen=True,
        is_open=False,
        size="sm",
    ),
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(" ")),
            dbc.ModalBody(card_references),
        ],
        id="references_mod_xl",
        fullscreen=True,
        is_open=False,
        size="sm",
    ),
            dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(" ")),
            dbc.ModalBody(card_explication_sem),
        ],
        id="semaforo_mod_xl",
        fullscreen=True,
        is_open=False,
        size="sm",
    ),
],style={"display": "flex", "flex-direction": "column"},)

def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

# app.callback(
#     dash.dependencies.Output("perf_mod", "is_open"),
#     dash.dependencies.Input("perf_but", "n_clicks"),
#     dash.dependencies.State("perf_mod", "is_open"),
# )(toggle_modal)

# app.callback(
#     dash.dependencies.Output("iny_mod", "is_open"),
#     dash.dependencies.Input("iny_but", "n_clicks"),
#     dash.dependencies.State("iny_mod", "is_open"),
# )(toggle_modal)

app.callback(
    Output("function_mod_xl", "is_open"),
    Input("function_but_xl", "n_clicks"),
    State("function_mod_xl", "is_open"),
)(toggle_modal)

app.callback(
    Output("references_mod_xl", "is_open"),
    Input("references_but_xl", "n_clicks"),
    State("references_mod_xl", "is_open"),
)(toggle_modal)

app.callback(
    Output("semaforo_mod_xl", "is_open"),
    Input("semaforo_but_xl", "n_clicks"),
    State("semaforo_mod_xl", "is_open"),
)(toggle_modal)

@callback(
    [Output(component_id='fig1', component_property='figure'),
     Output(component_id='fig2', component_property='figure'),
     Output(component_id='fig3', component_property='figure'),
     Output(component_id='fig4', component_property='figure'),
     Output(component_id='fig5', component_property='figure'),
     Output(component_id='fig6', component_property='figure'),
     Output(component_id='fig7', component_property='figure'),
     Output(component_id='fig8', component_property='figure'),
     Output(component_id='fig9', component_property='figure'),
     Output(component_id='fig10', component_property='figure'),
     Output(component_id='fig11', component_property='figure'),
     Output(component_id='fig12', component_property='figure'),
     Output(component_id='fig13', component_property='figure'),
     Output(component_id='fig14', component_property='figure'),
     Output(component_id='fig15', component_property='figure'),
     Output(component_id='fig16', component_property='figure'),
     Output(component_id='fig17', component_property='figure'),
     Output(component_id='fig18', component_property='figure'),
    #  Output(component_id='geo1', component_property='figure'),
     Output(component_id='geo2', component_property='figure'),
     Output(component_id='fig_A_Subsector', component_property='figure'),
     #Espacios por ubi
     Output(component_id='fig_C_segh', component_property='figure'),
     Output(component_id='fig_C_act', component_property='figure'),
     Output(component_id='fig_C_acc', component_property='figure'),
     Output(component_id='fig_C_info', component_property='figure'),
     Output(component_id='fig_C_catacc', component_property='figure'),
     Output(component_id='fig_A_cvul', component_property='figure'),
     Output(component_id='fig_A_afcim', component_property='figure'),
     Output(component_id='fig_A_act', component_property='figure'),
     Output(component_id='fig_A_info', component_property='figure'),
     Output(component_id='fig_dimall_ubi', component_property='figure'),
     Output(component_id='fig_dimsoc_ubi', component_property='figure'),
     Output(component_id='fig_dimeco_ubi', component_property='figure'),
     Output(component_id='fig_dimam_ubi', component_property='figure'),
     ],
    [Input('submit-val', 'n_clicks'),
     State(component_id='dep_id', component_property='value'),
     State(component_id='count_id', component_property='value'),
     State(component_id='shape_id', component_property='value'),
     State(component_id='time_id', component_property='value'),
     State(component_id='DATE', component_property='start_date'),
     State(component_id='DATE', component_property='end_date'),]
)
def update_output_div(act,list_dep,filter_ubi,filter_ubi2,strfil,START_DATE,END_DATE):
    
    # list_dep=[dep[0:5]]
    # list_mun=[]
    # list_mun=[]
    #strfil='mun'
    # filter_ubi='Municipio'
    # filter_ubi2='Localizacion/zona'
    if len(list_dep)==0:
        list_dep.append('COLOMBIA')

    if np.any(np.isin(list_dep,'COLOMBIA')):
        #df11=df1.copy()
        df21=df2.copy()
        #df31=df3.copy()
        i='COLOMBIA'
    else:
        if len(list_dep)==0:
            dep_fil=['']
        else:
            dep_fil=[LOC[dpt] for dpt in list_dep]
        #df11=df1[np.isin(df1['Departamento'],dep_fil)]
        df21=df2[np.isin(df2['Departamento'],dep_fil)]
        #df31=df3[np.isin(df3['Departamento'],dep_fil)]
        i='departamentos y municipios de consulta'
    df21=df21[(df2['FECHA - HORA UTC']<=END_DATE)&(df2['FECHA - HORA UTC']>=START_DATE)]
    # if len(df11)!=0:
    #     # #print('Actores')
    #     # #print(df11['_id'].unique())
    #     pass
    if len(df21)!=0:
        # filter_ubi='Departamento'
        #print('Conflictos')
        #print(df21['_id'].unique())
        dfbar=df21[[filter_ubi,'Inicio/Tipo_de_Reporte']].value_counts().reset_index()
        # Datos Generales --------------------------------
        if len(dfbar!=0):
            fig1 = px.bar(dfbar, x=filter_ubi, y="count", color='Inicio/Tipo_de_Reporte', title="Tipos de Reporte de conflictividad en "+i)
        else:
            fig1 = {}
        # Conflictos --------------------------------
        if filter_ubi2=='Ninguno':
            dfbar=df21[[filter_ubi,'Conflicto/Subsector']].value_counts().reset_index()
        else:
            dfbar=df21[[filter_ubi,'Conflicto/Subsector',filter_ubi2]].value_counts().reset_index()
        if len(dfbar!=0):
            if filter_ubi2=='Ninguno':
                fig2 = px.bar(dfbar, x=filter_ubi, y="count", color='Conflicto/Subsector', title="Conflictos en "+i)
            else:
                fig2 = px.bar(dfbar, x=filter_ubi, y="count", color='Conflicto/Subsector', title="Conflictos en "+i,pattern_shape=filter_ubi2)
        else:
            fig2 = {}
        # Alertas --------------------------------
        dfbar=df21[[filter_ubi,'Alerta/Subsector_generador_de_la_Aler']].value_counts().reset_index()
        draft_template = go.layout.Template()
        draft_template.layout.annotations = [
            dict(
                name='Name',
                text="No hay datos",
                textangle=0,
                opacity=0.1,
                font=dict(color="black", size=30),
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
            )
        ]
        if len(dfbar)!=0:
            fig_A_Subsector = px.bar(dfbar, x=filter_ubi, y="count", color='Alerta/Subsector_generador_de_la_Aler', title="Subsector afectado de Alerta Temprana de conflictividad en "+i)
            #fig.show()
        else:
            fig_A_Subsector=px.scatter()
            draft_template.layout.annotations[0].text="No hay datos para "+'Alerta/Subsector_generador_de_la_Aler'
            fig_A_Subsector.update_layout(template=draft_template)
            # fig_A_Subsector={}
        dfbar=df21[[filter_ubi,'Alerta/Tipo_de_Alerta_Temprana']].value_counts().reset_index()
        if len(dfbar)!=0:
            fig3 = px.bar(dfbar, x=filter_ubi, y="count", color='Alerta/Tipo_de_Alerta_Temprana', title="Tipos de Alerta Temprana de conflictividad en "+i)
            #fig.show()
        else:
            fig3=px.scatter()
            draft_template.layout.annotations[0].text="No hay datos para "+'Alerta/Tipo_de_Alerta_Temprana'
            fig3.update_layout(template=draft_template)
        dfbar=df21[[filter_ubi,'Alerta/Segmento_posiblemente_afectado']].value_counts().reset_index()
        if len(dfbar)!=0:
            fig4 = px.bar(dfbar, x=filter_ubi, y="count", color='Alerta/Segmento_posiblemente_afectado', title="Segmento de Alerta posiblemente afectado en "+i)
        else:
            fig4={}
            #fig.show()
        # Espacio ---------------------------
        fig_ls=[]
        for col,name in zip(columns_space,
            ["Conductas vulneratorias de "+i,
            "Afectaciones y_o impacto en "+i,
            "Principales actores involucrados en "+i,
            "Principales fuentes de información en "+i,
            "Segmento de Hidrocarburso Afectado en "+i,
            "Principales Actores Involucrados en "+i,
            "Tipo de Accion de Conflicto en "+i,
            "Fuentes de Información en "+i,
            "Categorias de las Acciones en "+i,]):
            cd_vul=[]
            for ff in df21[col]:
                try:
                    cd_vul.extend(ff.split(' '))
                except:
                    pass
            unique, counts = np.unique(np.array(cd_vul), return_counts=True)
            if len(unique)!=0:
                fignn=px.pie(names=unique,values= counts, title=name)
                fignn.update_traces(hoverinfo='label+percent+name', textinfo='none')
                fignn.update_layout(
                            legend=dict(font=dict(size=10),itemwidth=30)) # Para leyendas largas se puede simplificar con <br>
                fig_ls.append(fignn)
            else:
                fig_ls.append({})
                #fig.show()
        fig_ls1=[]
        for col in columns_space:
            cd_vul=[]
            filter_ubi_ls=[]
            for ff,ubi in zip(df21[col],df21[filter_ubi]):
                try:
                    cd_vul.extend(ff.split(' '))
                    filter_ubi_ls.extend([str(ubi)]*len(ff.split(' ')))
                    #print(len(ff.split(' ')))
                except:
                    fign={}
            hist_df=pd.DataFrame()
            hist_df[filter_ubi]=filter_ubi_ls
            hist_df[col]=cd_vul
            dfbar=hist_df[[filter_ubi,col]].value_counts().reset_index()
            if len(dfbar)!=0:
                fign = px.bar(dfbar, x=filter_ubi, y="count", color=col, title=col)
                fign.update_layout(legend=dict(
                                font=dict(size= 10),
                                title_text=''))
                #fig.show()
            else:
                fign={}
            fig_ls1.append(fign)
    #----------------------------------------------------------
        dftime=df21[np.isin(df21['Inicio/Tipo_de_Reporte'],['registro_inicio','alerta_temprana','otros_reportes_actividades'])]
        dfsegcierr=df21[np.isin(df21['Inicio/Tipo_de_Reporte'],['cierre','seguimiento_conflictividad','seguimiento_AT'])]

        fig14 = go.Figure()
        hoy = datetime.today().strftime('%Y-%m-%d')
        # strfil='dep' #seg,zon,dep,mun
        for _id,cocal,coalt,init,zon,dep,mun in zip(dftime['_id'],
                            dftime['Conflicto/Codificaciones/calculation'],
                            dftime['Alerta/calculation_001'],
                            dftime['Inicio/Fecha_de_ocurrencia_del_evento'],
                            dftime['Localizacion/zona'],
                            dftime['Departamento'],
                            dftime['Municipio'],
                            ):
            fil=[np.any(coinc) for coinc in np.isin(dfsegcierr[columns_code_seg],[cocal,_id,coalt])]
            dftime_fil=dfsegcierr[fil]
            if strfil=='Tipo de seguimiento':
                nc='Reporte'
                sg='En seguimiento'
                cr='Cerrado'
            elif strfil=='Localizacion/zona':
                [nc,sg,cr]=[zon,zon,zon]
            elif strfil=='Departamento':
                [nc,sg,cr]=[dep,dep,dep]
            elif strfil=='Municipio':
                [nc,sg,cr]=[mun,mun,mun]
                
            x=[init]
            y=[_id]
            if len(dftime_fil)!=0:
                if np.any(np.isin(dftime_fil['Inicio/Tipo_de_Reporte'].unique(),['seguimiento_conflictividad','seguimiento_AT'])):
                    for i in dftime_fil[(np.isin(dftime_fil['Inicio/Tipo_de_Reporte'],['seguimiento_conflictividad','seguimiento_AT']))]['Inicio/Fecha_de_ocurrencia_del_evento'].sort_values():
                        x.append(i)
                        y.append(_id)
                if not np.any(np.isin(dftime_fil['Inicio/Tipo_de_Reporte'].unique(),['cierre'])):
                    x.append(hoy)
                    y.append(_id)
                    fig14.add_trace(go.Scatter(x=x, y=y, name=str(_id),
                                            legendgroup=sg,
                                            legendgrouptitle_text=sg,
                                            marker_color='green',
                                            marker_size=4,
                                            line_shape='linear',
                                            line_dash='dash',
                                            line_width=0.75,))
                if np.any(np.isin(dftime_fil['Inicio/Tipo_de_Reporte'].unique(),['cierre'])):
                    x.append(dftime_fil[dftime_fil['Inicio/Tipo_de_Reporte']=='cierre']['Inicio/Fecha_de_ocurrencia_del_evento'].values[0])
                    y.append(_id)
                    fig14.add_trace(go.Scatter(x=x, y=y, name=str(_id),legendgrouptitle_text=cr,legendgroup=cr,marker_color='red',
                                    line_shape='linear'))
            else:
                # x.append(hoy)
                # y.append(_id)
                fig14.add_trace(go.Scatter(x=x, y=y, name=str(_id),
                                        legendgroup=nc,
                                        legendgrouptitle_text=nc,
                                        marker_color=len(nc),
                                        #  marker_colorscale='YlOrRd',
                                        #  marker_cmin=0,
                                        #  marker_cmax=30,
                                        marker_size=4,
                                        line_shape='linear',
                                        line_dash='dot',
                                        line_width=0.75,))
                # #print(len(nc))
        fig14.update_layout(autosize=True,height=500,
                            margin=dict(l=250, r=250, b=0, t=30),
                            font_family="Poppins"
                        )
        fig14.update_yaxes(tickformat="~m") 
        #fig.show()
    #----------------------------------------------------------        
        soc=[]
        eco=[]
        am=[]
        filter_ubi_soc=[]
        filter_ubi_eco=[]
        filter_ubi_am=[]
        for soc1,eco1,am1,ubi in zip(df21['Conflicto/Carac/Categor_a_del_conflicto_Dime'],
                            df21['Conflicto/Carac/Categor_as_del_conflicto_Dim_001'],
                            df21['Conflicto/Carac/Categor_as_del_Conflicto_Dim'],
                            df21[filter_ubi]):
            soc.extend(str(soc1).split(' '))
            eco.extend(str(eco1).split(' '))
            am.extend(str(am1).split(' '))
            filter_ubi_soc.extend([str(ubi)]*len(str(soc1).split(' ')))
            filter_ubi_eco.extend([str(ubi)]*len(str(eco1).split(' ')))
            filter_ubi_am.extend([str(ubi)]*len(str(am1).split(' ')))
        df_soc=pd.DataFrame()
        df_eco=pd.DataFrame()
        df_am=pd.DataFrame()
        for tipo,ubi,dfi,nom in zip([soc,eco,am],
                                [filter_ubi_soc,filter_ubi_eco,filter_ubi_am],
                                [df_soc,df_eco,df_am],
                                ['Social','Economico','Ambiental']):
            dfi['Tipo']=tipo
            dfi['Ubicacion']=ubi
            dfi['Dimension']=nom
        df_soc = df_soc.drop(df_soc[df_soc['Tipo'] == 'nan'].index)
        df_eco = df_eco.drop(df_eco[df_eco['Tipo'] == 'nan'].index)
        df_am = df_am.drop(df_am[df_am['Tipo'] == 'nan'].index)
        df_freq=pd.concat([df_soc,df_eco,df_am])
        fig15 = px.line_polar(df_freq[['Dimension']].value_counts().reset_index(), r="count", theta="Dimension",line_close=True,
                        title="Grafico de cuantificacion dimensional"
                        )
        fig_dimall_ubi=px.bar(df_freq[['Dimension','Ubicacion']].value_counts().reset_index(), x='Ubicacion', y="count", color='Dimension', title='Grafico de cuantificacion dimensional')
        fig16=px.pie(df_soc[['Tipo']].value_counts().reset_index(),names='Tipo',values= 'count', title='Social')
        fig_dimsoc_ubi=px.bar(df_soc[['Tipo','Ubicacion']].value_counts().reset_index(), x='Ubicacion', y="count", color='Tipo', title='Grafico de cuantificacion dimensional social')
        fig17=px.pie(df_eco[['Tipo']].value_counts().reset_index(),names='Tipo',values= 'count', title='Economica')
        fig_dimeco_ubi=px.bar(df_eco[['Tipo','Ubicacion']].value_counts().reset_index(), x='Ubicacion', y="count", color='Tipo', title='Grafico de cuantificacion dimensional economico')
        fig18=px.pie(df_am[['Tipo']].value_counts().reset_index(),names='Tipo',values= 'count', title='Ambiental')
        fig_dimam_ubi=px.bar(df_am[['Tipo','Ubicacion']].value_counts().reset_index(), x='Ubicacion', y="count", color='Tipo', title='Grafico de cuantificacion dimensional ambiental')
    # if len(df31)!=0:
    #     pass
    if len(df21)>0:
        # heat=df21[['latitud','longitud','Municipio','Departamento']].value_counts().reset_index()
        # geo2 = px.density_mapbox(heat, lat='latitud', lon='longitud', z='count', radius=25,hover_data=['Municipio','Departamento'],
        #                 center=dict(lat=4, lon=-72), zoom=3,
        #                 mapbox_style="open-street-map")
        # geo2.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        heat=df21[['latitud','longitud','Municipio','Departamento']].value_counts().reset_index()
        scatt=df21[['lat','lon','Municipio','Departamento']].value_counts().reset_index()
        geo2 = px.density_mapbox(heat, lat='latitud', lon='longitud', z='count', radius=25,
                        center=dict(lat=4, lon=-72), zoom=3,
                        mapbox_style="open-street-map",color_continuous_scale=px.colors.sequential.Jet)
        # geo1 = px.scatter_mapbox(scatt, lat="lat", lon="lon", color="count", 
        #                 #          size="count",
        #                 #   color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10
        #                   )
        # geo_scatter=px.scatter_geo(df2[['lat','lon','Municipio','Departamento']].value_counts().reset_index(), 
        #                      lat="lat",
        #                      lon='lon',
        #                      color="count", # which column to use to set the color of markers
        #                      #hover_name="country", # column added to hover information
        #                      #size="pop", # size of markers
                            
        #                      #projection="natural earth"
        #                     mapbox_style="open-street-map"
        #                      )
        geo2.add_trace(go.Scattermapbox(
                lat=scatt.lat,
                lon=scatt.lon,
                mode='markers',
                name='Registros',
                # hoverinfo='all',
                text=[str(scatt['lat'][i]) + '<br>' + str(scatt['lon'][i]) + '<br>' + scatt['Municipio'][i] + '<br>' + scatt['Departamento'][i] for i in range(scatt.shape[0])],
                marker=go.scattermapbox.Marker(
                    size=6,
                    color='red',
                    opacity=0.7,
                    # colorscale='jet',
                ),
            ))
        geo2.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        
    else:
        geo2=go.Figure()
    geo2.update_layout(
        autosize=False,
        # width=1000,
        height=675,
        # margin=dict(

        #     l=50,
        #     r=50,
        #     b=100,
        #     t=100,
        #     pad=4
        # ),
        # paper_bgcolor="LightSteelBlue",
    )

    fig1.add_layout_image(
    dict(
        source="assets\OAAS_cut.png",
        xref="paper", yref="paper",
        x=1.1, y=-0.1,
        sizex=0.4, sizey=0.4,
        xanchor="right", yanchor="bottom"
    )
)

    #Analisis total & = or y merges np.isin
    return fig1,fig2,fig3,fig4,fig_ls[0],fig_ls[1],fig_ls[2],fig_ls[3],fig_ls[4],fig_ls[5],fig_ls[6],fig_ls[7],fig_ls[8],fig14,fig15,fig16,fig17,fig18,geo2,fig_A_Subsector,fig_ls1[4],fig_ls1[5],fig_ls1[6],fig_ls1[7],fig_ls1[8],fig_ls1[0],fig_ls1[1],fig_ls1[2],fig_ls1[3],fig_dimall_ubi,fig_dimsoc_ubi,fig_dimeco_ubi,fig_dimam_ubi

@callback(
    [Output('tbl_confc', 'data'),
     Output('tbl_confc', 'columns'),
     Output('confc_block', 'style'),
     # Alerta
     Output('tbl_alerta', 'data'),
     Output('tbl_alerta', 'columns'),
     Output('alerta_block', 'style'),
     # Sconfc
     Output('tbl_sconfc', 'data'),
     Output('tbl_sconfc', 'columns'),
     Output('sconfc_block', 'style'),
     #S.Alertas
     Output('tbl_salerta', 'data'),
     Output('tbl_salerta', 'columns'),
     Output('salerta_block', 'style'),
     #S.Cierr
     Output('tbl_cierr', 'data'),
     Output('tbl_cierr', 'columns'),
     Output('cierr_block', 'style'),
     #Otros
     Output('tbl_otro', 'data'),
     Output('tbl_otro', 'columns'),
     Output('otro_block', 'style')],
    [Input('geo2', 'clickData')])
def display_click_data(clc):
    clc=json.dumps(clc, indent=2)
    lon=json.loads(clc)['points'][0]['lon']
    lat=json.loads(clc)['points'][0]['lat']
    print(json.loads(clc)['points'][0]['lon'])
    df_table=df2[((df2['latitud']==lat)&(df2['longitud']==lon))|
                (df2['lat']==lat)&(df2['lon']==lon)]
    #Conflictos -----------------------------------------
    confc=df_table[df_table['Inicio/Tipo_de_Reporte']=='registro_inicio']
    if len(confc)>0:
        confc=confc[columns_confc].sort_values(by='Inicio/Fecha_de_ocurrencia_del_evento')
        columns_renam={}
        for key,val in zip(columns_confc,columns_val_confc):
            columns_renam[key]=val
        confc=confc.rename(columns=columns_renam)
        dtconfc=confc.to_dict('records')
        colconfc=[{"name": i, "id": i} for i in columns_val_confc]
        dconfc={'display': 'block'}
    else:
        dtconfc=df2[columns_otro][0:2].to_dict('records')
        colconfc=[{"name": i, "id": i} for i in columns_otro]
        dconfc={'display': 'none'}
    #Alertas -----------------------------------------
    alertas=df_table[df_table['Inicio/Tipo_de_Reporte']=='alerta_temprana']
    if len(alertas)>0:
        alertas=alertas[columns_alertas].sort_values(by='Inicio/Fecha_de_ocurrencia_del_evento')
        columns_renam={}
        for key,val in zip(columns_alertas,columns_val_alertas):
            columns_renam[key]=val
        alertas=alertas.rename(columns=columns_renam)
        dtalerta=alertas.to_dict('records')
        colalerta=[{"name": i, "id": i} for i in columns_val_alertas]
        dalerta={'display': 'block'}
    else:
        dtalerta=df2[columns_otro][0:2].to_dict('records')
        colalerta=[{"name": i, "id": i} for i in columns_otro]
        dalerta={'display': 'none'}
    #S.Conflictos -----------------------------------------
    sconfc=df_table[df_table['Inicio/Tipo_de_Reporte']=='seguimiento_conflictividad']
    if len(sconfc)>0:
        sconfc=sconfc[columns_sconfc].sort_values(by='Inicio/Fecha_de_ocurrencia_del_evento')
        columns_renam={}
        for key,val in zip(columns_sconfc,columns_val_sconfc):
            columns_renam[key]=val
        sconfc=sconfc.rename(columns=columns_renam)
        dtsconfc=sconfc.to_dict('records')
        colsconfc=[{"name": i, "id": i} for i in columns_val_sconfc]
        dsconfc={'display': 'block'}
    else:
        dtsconfc=df2[columns_otro][0:2].to_dict('records')
        colsconfc=[{"name": i, "id": i} for i in columns_otro]
        dsconfc={'display': 'none'}
    #Cierres -----------------------------------------
    cierr=df_table[df_table['Inicio/Tipo_de_Reporte']=='cierre']
    if len(cierr)>0:    
        cierr=cierr[columns_cierr].sort_values(by='Inicio/Fecha_de_ocurrencia_del_evento')
        columns_renam={}
        for key,val in zip(columns_cierr,columns_val_cierr):
            columns_renam[key]=val
        cierr=cierr.rename(columns=columns_renam)
        dtcierr=cierr.to_dict('records')
        colcierr=[{"name": i, "id": i} for i in columns_val_cierr]
        dcierr={'display': 'block'}
    else:
        dtcierr=df2[columns_otro][0:2].to_dict('records')
        colcierr=[{"name": i, "id": i} for i in columns_otro]
        dcierr={'display': 'none'}
    #S.Alertas -----------------------------------------
    salerta=df_table[df_table['Inicio/Tipo_de_Reporte']=='seguimiento_AT']
    if len(salerta)>0:   
        salerta=salerta[columns_salerta].sort_values(by='Inicio/Fecha_de_ocurrencia_del_evento')
        columns_renam={}
        for key,val in zip(columns_salerta,columns_val_salerta):
            columns_renam[key]=val
        salerta=salerta.rename(columns=columns_renam)
        dtsalerta=alertas.to_dict('records')
        colsalerta=[{"name": i, "id": i} for i in columns_val_salerta]
        dsalerta={'display': 'block'}
    else:
        dtsalerta=df2[columns_otro][0:2].to_dict('records')
        colsalerta=[{"name": i, "id": i} for i in columns_otro]
        dsalerta={'display': 'none'}
    #Otros -----------------------------------------
    otro=df_table[df_table['Inicio/Tipo_de_Reporte']=='otros_reportes_actividades']
    
    if len(otro)>0: 
        print(otro)  
        otro=otro[columns_otro].sort_values(by='Inicio/Fecha_de_ocurrencia_del_evento')
        columns_renam={}
        for key,val in zip(columns_otro,columns_val_otro):
            columns_renam[key]=val
        otro=otro.rename(columns=columns_renam)
        dtotro=otro.to_dict('records')
        colotro=[{"name": i, "id": i} for i in columns_val_otro]
        dotro={'display': 'block'}
    else:
        dtotro=df2[columns_otro][0:2].to_dict('records')
        colotro=[{"name": i, "id": i} for i in columns_otro]
        dotro={'display': 'none'}
    # Fin condicionales
    return dtconfc,colconfc,dconfc,dtalerta,colalerta,dalerta,dtsconfc,colsconfc,dsconfc,dtsalerta,colsalerta,dsalerta,dtcierr,colcierr,dcierr,dtotro,colotro,dotro,

if __name__ == '__main__':
    app.run(debug=True)
