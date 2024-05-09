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
import time

colorlist=[
'#3366CC',
'#DC3912',
'#FF9900',
'#109618',
'#990099',
'#0099C6',
'#DD4477',
'#66AA00',
'#B82E2E',
'#316395',
  '#636EFA',
 '#EF553B',
 '#00CC96',
 '#AB63FA',
 '#FFA15A',
 '#19D3F3',
 '#FF6692',
 '#B6E880',
 '#FF97FF',
 '#FECB52',
 'rgb(251,180,174)',
 'rgb(179,205,227)',
 'rgb(204,235,197)',
 'rgb(222,203,228)',
 'rgb(254,217,166)',
 'rgb(255,255,204)',
 'rgb(229,216,189)',
 'rgb(253,218,236)',
 'rgb(242,242,242)',
 'rgb(179,226,205)',
 'rgb(253,205,172)',
 'rgb(203,213,232)',
 'rgb(244,202,228)',
 'rgb(230,245,201)',
 'rgb(255,242,174)',
 'rgb(241,226,204)',
 'rgb(204,204,204)',
'rgb(141,211,199)',
 'rgb(255,255,179)',
 'rgb(190,186,218)',
 'rgb(251,128,114)',
 'rgb(128,177,211)',
 'rgb(253,180,98)',
 'rgb(179,222,105)',
 'rgb(252,205,229)',
 'rgb(217,217,217)',
 'rgb(188,128,189)',
 'rgb(204,235,197)',
 'rgb(255,237,111)',
'rgb(136, 204, 238)',
 'rgb(204, 102, 119)',
 'rgb(221, 204, 119)',
 'rgb(17, 119, 51)',
 'rgb(51, 34, 136)',
 'rgb(170, 68, 153)',
 'rgb(68, 170, 153)',
 'rgb(153, 153, 51)',
 'rgb(136, 34, 85)',
 'rgb(102, 17, 0)',
 'rgb(136, 136, 136)'
 ]

config_map = {
  'toImageButtonOptions': {
    'format': 'png', # one of png, svg, jpeg, webp
    'filename': 'OAAS_mapa_conflictos',
    'height': 1080,
    'width': 1080,
    'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
  }
}
# config_bar = {
#   'toImageButtonOptions': {
#     'format': 'png', # one of png, svg, jpeg, webp
#     'filename': 'OAAS_hist_conflictos',
#     'height': 480,
#     'width': 1240,
#     'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
#   }
# }
config_pie = {
  'toImageButtonOptions': {
    'format': 'png', # one of png, svg, jpeg, webp
    'filename': 'OAAS_tarta_conflictos',
    'height': 1080,
    'width': 1080,
    'scale': 1 ,# Multiply title/legend/axis/canvas sizes by this factor
  }
}

from datetime import datetime
 
# storing the current time in the variable
c = datetime.now()

#note = 'NYSE Trading Days After Announcement<br>Source:<a href="https://www.nytimes.com/"">The NY TIMES</a> Data: <a href="https://www.yahoofinance.com/">Yahoo! Finance</a>'

# Suppress FutureWarning messages
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None 

MUN_COD=pd.read_csv('aux1/MUN_COD.txt',delimiter='\t')

#KoboT start
token = '3d81f96d16fbc8adc419e90fd5e5684bc58445ff'
kobot = KoboExtractor(token, 'https://kf.kobotoolbox.org/api/v2')
form_id = 'aJThss9cZcGfrUrm7rqcYa'
datt = kobot.get_data(form_id, query=None, start=None, limit=None, submitted_after=None)
#KoboT end

#Replace start
replace=pd.read_excel('aux1/aJThss9cZcGfrUrm7rqcYa.xlsx',sheet_name='choices') #Palabras de reemplazo
replace_1=replace[np.isin(replace['list_name'],replace['list_name'].unique()[0:5])]# Palabras de reemplazo iniciales
values=replace['label'].values
values_1=replace_1['label'].values
replace_dict = dict(zip(replace['name'].values, [values for values in values]))
replace_dict_1 = dict(zip(replace_1['name'].values, [values_1 for values_1 in values_1]))
#Replace end

df2 = pd.json_normalize(datt['results'])
MUN_dict=MUN_COD[['Identificacion/municipio','Municipio']].set_index('Identificacion/municipio').to_dict()['Municipio']
DEP_dict=MUN_COD[['Identificacion/municipio','Departamento']].set_index('Identificacion/municipio').to_dict()['Departamento']

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
for _id,cocal,coalt,init,zon,dep,mun,munc,sub1,sub2,sub3 in zip(dftime['_id'],
                    dftime['Conflicto/Codificaciones/calculation'],
                    dftime['Alerta/calculation_001'],
                    dftime['Inicio/Fecha_de_ocurrencia_del_evento'],
                    dftime['Localizacion/zona'],
                    dftime['Departamento'],
                    dftime['Municipio'],
                    dftime['Localizacion/municipio'],
                    dftime['Conflicto/Subsector'],
                    dftime['Alerta/Subsector_generador_de_la_Aler'],
                    dftime['group_rl63j77/Subsector_generador_de_la_Aler']
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
    dftime_fil['sub1']=sub1
    dftime_fil['sub2']=sub2
    dftime_fil['sub3']=sub3
    if len(dftime_fil)>0:
        ls_all.append(dftime_fil)
df_all=pd.concat(ls_all)
df2=pd.concat([df_all,dftime])
df2['Localizacion/municipio']=df2['Localizacion/municipio'].astype('int')
dep=KEY_LOC[-33::]
mun=KEY_LOC[0:-33]
dict_dep={}
for i in ['Amazonas ','Vaupes ','Guainia ','Guaviare ','Putumayo ','Caqueta ']:
    dict_dep[i]='Zona Amazonia'
for i in ['Choco ','Valle ','Cauca ','Nariño ']:
    dict_dep[i]='Zona Pacifico'
for i in ['Arauca ','Vichada ','Casanare ','Meta ']:
    dict_dep[i]='Zona Orinoquia'
for i in ['La Guajira ','Magdalena ','Cesar ','Atlantico ','Bolivar ','Sucre ','Cordoba ','San Andres ']:
    dict_dep[i]='Zona Caribe'
andina=res = [i for i in dep if i not in list(dict_dep.keys())]

for i in andina:
    dict_dep[i]='Zona Andina'
df2['Localizacion/zona']=dftime['Departamento'].map(dict_dep)
df2=df2.replace(replace_dict_1)

mun_loc=pd.read_csv('aux1/mun_loc.csv',skiprows=5,delimiter=';',decimal=',')
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

'Conflicto/Segmento_Afectado_Miner_a',
'Conflicto/Segmento_Afectado_Energ_a',
'Conflicto/Escala_del_Proyecto',

'Conflicto/Carac/Principales_actores_involucrad',
'Conflicto/Carac/Afectaciones/Tipo_de_Acciones',
'Conflicto/Carac/Afectaciones/Indique_cu_les_son_las_fuentes',
'Conflicto/Carac/Actuaciones/Categor_as_de_acciones_realiza',

'Alerta/Segmento_posiblemente_afectado', #Hidrocarburos
'Alerta/Segmento_posiblemente_afectado_001', #Mineria
'Alerta/Segmento_posiblemente_afectado_energ_a', #Energia
'Alerta/Escala_del_Proyecto_001', #Escala del proyecto
]
columns_code_seg=['Seg_Alerta/C_digo_nico_de_Ale_igina_el_seguimiento',
'Cierre/C_digo_nico_de_Regi_e_la_Alerta_Temprana',
'Seg_Conflicto/C_digo_nico_de_Regi_ro_de_Conflictividad',
'Conflicto/Carac/Actuaciones/Diligencie_el_c_digo_n_de_Alerta_temprana',
'Conflicto/Codificaciones/calculation',
'Alerta/calculation_001']

draft_template = go.layout.Template()
draft_template.layout.annotations = [
    dict(
        name='Name',
        text="No se registran datos para",
        textangle=-15,
        opacity=0.1,
        font=dict(color="black", size=30),
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
    )
]

draft_nodata = go.layout.Template()
draft_nodata.layout.annotations = [
    dict(
        name='Name',
        text="No se registran datos",
        textangle=-15,
        opacity=0.1,
        font=dict(color="black", size=30),
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
    )
]

draft_OAAS = go.layout.Template()
draft_OAAS.layout.annotations = [
    dict(
        name='Name',
        text="Ministerio de Minas y Energía",
        textangle=-15,
        opacity=0.1,
        font=dict(color="black", size=55),
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
    )
]

def bar_all(filter_ubi2,df21,filter_ubi,column,i,namee):
    if filter_ubi2=='Ninguno':
        dfbar=df21[[filter_ubi,column]].value_counts().reset_index()
    else:
        dfbar=df21[[filter_ubi,column,filter_ubi2]].value_counts().reset_index()
    if len(dfbar!=0):
        if filter_ubi2=='Ninguno':
            fig = px.bar(dfbar, x=filter_ubi, y="count", color=column, title=namee+i,labels={"count": "Conteo"})
            fig.update_layout( showlegend=True,legend_title=None)
        else:
            fig = px.bar(dfbar, x=filter_ubi, y="count", color=column, title=namee+i,pattern_shape=filter_ubi2)
        fig.update_layout(template=draft_OAAS)
    else:
        fig=px.scatter()
        draft_template.layout.annotations[0].text="No se registran datos para "+column
        fig.update_layout(template=draft_template)
    return fig
        

app = Dash(__name__)
server = app.server

#app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

dep.insert(0, 'Todos los departamentos')
card_main=html.Div([
    html.H5(children='''
        Filtra por las diferentes columnas
    '''),
    html.H5(children='''
        Departamento
    ''',id='dep__'),
    dbc.Tooltip(
    "Filtro por departamentos",
    target='dep__',
    ),
    dcc.Dropdown(
        dep,
        ['Todos los departamentos'],
        multi=True,
        id='dep_id',
        style={'color': 'black'}
    ),
    html.H5(children='''
        Gerencias
    ''',id='gerencias__'),
    dbc.Tooltip(
    "Filtro por gerencias. Si hay depatamentos activos solo asumira las zonas.",
    target='gerencias__',
    ),
    dcc.Dropdown(
        ['Zona Amazonia','Zona Pacifico','Zona Orinoquia','Zona Caribe','Zona Andina'],
        [],
        multi=True,
        id='ger_id',
        style={'color': 'black'}
    ),
    html.H5(children='''
        Fecha
    ''',id='date__'),
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
    dbc.Tooltip(
    "Filtro de fecha",
    target='date__',
    ),
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
        Subsector
    ''',id='subs__'),
    dbc.Tooltip(
    "Filtro por subsector. General son todos los subsectores.",
    target='subs__',
    ),
    dcc.Dropdown(
        ['General','Hidrocarburos','Energía','Minería'],
        ['General'],
        multi=True,
        id='subsector_id',
        style={'color': 'black'}
    )
    ,
    # html.H5(children='''
    #     Simbolo
    # '''),
    # dcc.Dropdown(
    #     ['Departamento','Localizacion/zona','Ninguno'],
    #     'Ninguno',
    #     multi=False,
    #     id='shape_id',
    #     style={'color': 'black'}
    # )
    # ,
    html.H5(children='''
        Filtro Linea de Tiempo
    ''',id='timedat__'),
    dbc.Tooltip(
    "Desplega la caracteristica en la linea de tiempo",
    target='timedat__',
    ),
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
        * Seleccione los filtros que desea.
    ''',id='estado_filtro',style={'color': 'red', 'background-color': 'orange'}),
    dcc.Markdown(f'''
        * ¡Bienvenido al visor de conflictos mineroenergeticos!
        * Citese como: Observatorio de la Oficina de Asuntos Ambientales y Sociales. Ministerio de Minas y Energía. (s.f.). Visor de conflictos mineroenergeticos. Recuperado {datetime.today().strftime('%Y-%m-%d')}, de https://oaas_confc.com
    '''),], 
            
        className="sidebar",
        id='sidebar')


card_graph=dcc.Graph(
        id='geo2',
        figure={},
        config=config_map
    ),


tables=html.Div([
    html.H5('Tabla de Geoinformación (oprime un elemento en el mapa)',style={'color':'black'}),
    html.Div([
        html.H5('Conflictos',style={'color':'black'}),
        dash_table.DataTable(fixed_rows={'headers': True},
                             style_table={
                                            'overflowY': 'scroll',
                                            'overflowX': 'scroll',
                                            'maxWidth':'95%',
                                        } ,id='tbl_confc',
                            style_cell={              
                                            'textAlign': 'left',
                                            'backgroundColor': 'rgb(30, 30, 30)',
                                            'color': 'white',
                                            'font-family':'Nunito Sans',
                                            'font-size': '13px',
                                            "whiteSpace": "pre-line",
                                            'maxWidth': '280px',
                                            'minWidth': '100px',},
                            style_header={
                                'backgroundColor': '#edb600',
                                'fontWeight': 'bold',
                                'color': 'black',
                            },
                            style_data={
                                'color': 'black',
                                'backgroundColor': '#DDD0B4'
                            }),
        ],id='confc_block',style= {'display': 'none'},),
    #Alertas -----------------------------------------
    html.Div([
        html.H5('Alertas Tempranas',style={'color':'black'}),
        dash_table.DataTable(fixed_rows={'headers': True},
                             style_table={
                                            'overflowY': 'scroll',
                                            'overflowX': 'scroll',
                                            'maxWidth':'95%',
                                        } ,id='tbl_alerta',
                            style_cell={              
                                            'textAlign': 'left',
                                            'backgroundColor': 'rgb(30, 30, 30)',
                                            'color': 'white',
                                            'font-family':'Nunito Sans',
                                            'font-size': '13px',
                                            "whiteSpace": "pre-line",
                                            'maxWidth': '280px',
                                            'minWidth': '100px',},
                            style_header={
                                'backgroundColor': '#edb600',
                                'fontWeight': 'bold',
                                'color': 'black',
                            },
                            style_data={
                                'color': 'black',
                                'backgroundColor': '#DDD0B4'
                            }),
        ],id='alerta_block',style= {'display': 'none'}),
    #Seguimiento Conflictos -----------------------------------------
    html.Div([
        html.H5('Seguimiento conflictos',style={'color':'black'}),
        dash_table.DataTable(fixed_rows={'headers': True},
                             style_table={
                                            'overflowY': 'scroll',
                                            'overflowX': 'scroll',
                                            'maxWidth':'95%',
                                        } ,id='tbl_sconfc',
                            style_cell={              
                                            'textAlign': 'left',
                                            'backgroundColor': 'rgb(30, 30, 30)',
                                            'color': 'white',
                                            'font-family':'Nunito Sans',
                                            'font-size': '13px',
                                            "whiteSpace": "pre-line",
                                            'maxWidth': '280px',
                                            'minWidth': '100px',},
                            style_header={
                                'backgroundColor': '#edb600',
                                'fontWeight': 'bold',
                                'color': 'black',
                            },
                            style_data={
                                'color': 'black',
                                'backgroundColor': '#DDD0B4'
                            }),
        ],id='sconfc_block',style= {'display': 'none'}),
    #Seguimiento Alertas-----------------------------------------
    html.Div([
        html.H5('Seguimiento Alertas',style={'color':'black'}),
        dash_table.DataTable(fixed_rows={'headers': True},
                             style_table={
                                            'overflowY': 'scroll',
                                            'overflowX': 'scroll',
                                            'maxWidth':'95%',
                                        } ,id='tbl_salerta',
                            style_cell={              
                                            'textAlign': 'left',
                                            'backgroundColor': 'rgb(30, 30, 30)',
                                            'color': 'white',
                                            'font-family':'Nunito Sans',
                                            'font-size': '13px',
                                            "whiteSpace": "pre-line",
                                            'maxWidth': '280px',
                                            'minWidth': '100px',},
                            style_header={
                                'backgroundColor': '#edb600',
                                'fontWeight': 'bold',
                                'color': 'black',
                            },
                            style_data={
                                'color': 'black',
                                'backgroundColor': '#DDD0B4'
                            }),
        ],id='salerta_block',style= {'display': 'none'}),
    #Seguimiento Alertas-----------------------------------------
    html.Div([
        html.H5('Cierres',style={'color':'black'}),
        dash_table.DataTable(fixed_rows={'headers': True},
                             style_table={
                                            'overflowY': 'scroll',
                                            'overflowX': 'scroll',
                                            'maxWidth':'95%',
                                        } ,id='tbl_cierr',
                            style_cell={              
                                            'textAlign': 'left',
                                            'backgroundColor': 'rgb(30, 30, 30)',
                                            'color': 'white',
                                            'font-family':'Nunito Sans',
                                            'font-size': '13px',
                                            "whiteSpace": "pre-line",
                                            'maxWidth': '280px',
                                            'minWidth': '100px',},
                            style_header={
                                'backgroundColor': '#edb600',
                                'fontWeight': 'bold',
                                'color': 'black',
                            },
                            style_data={
                                'color': 'black',
                                'backgroundColor': '#DDD0B4'
                            }),
        ],id='cierr_block',style= {'display': 'none'}),
    #Otros-----------------------------------------
    html.Div([
        html.H5('Otros',style={'color':'black'}),
        dash_table.DataTable(fixed_rows={'headers': True},
                             style_table={
                                            'overflowY': 'scroll',
                                            'overflowX': 'scroll',
                                            'maxWidth':'95%',
                                        } ,id='tbl_otro',
                            style_cell={              
                                            'textAlign': 'left',
                                            'backgroundColor': 'rgb(30, 30, 30)',
                                            'color': 'white',
                                            'font-family':'Nunito Sans',
                                            'font-size': '13px',
                                            "whiteSpace": "pre-line",
                                            'maxWidth': '280px',
                                            'minWidth': '100px',},
                            style_header={
                                'backgroundColor': '#edb600',
                                'fontWeight': 'bold',
                                'color': 'black',
                            },
                            style_data={
                                'color': 'black',
                                'backgroundColor': '#DDD0B4'
                            }),
        ],id='otro_block',style= {'display': 'none'}),
    ]) #style_table={'maxHeight': 600} ,

card_function=dbc.Card(
    dbc.CardBody([
        html.H6("La Oficina de Asuntos Ambientales y Sociales busca potenciar de manera significativa el desarrollo sostenible en armonía y respeto de los diferentes territorios del país donde existe presencia del sector minero-energético, de manera que se consolide como un aliado de los territorios.",
            className="card-text"),
        html.H6("Por ello, trabajamos en:", 
            className="card-text"),
        html.H6("   -El fortalecimiento de un buen relacionamiento del sector minero-energético con las autoridades ambientales, locales y las comunidades, promoviendo espacios de diálogo y concertación social.", 
            className="card-text"),
        html.H6("   -La definición de políticas y lineamientos que posicionen los subsectores de minería, energía e hidrocarburos con los más altos estándares, garantizando su sostenibilidad, articulando el sector en las diferentes etapas de planeación de los procesos de Ordenamiento Territorial de las regiones de manera articulada con el sector ambiental del país.", 
            className="card-text"),
        html.H6("   -La construcción de políticas de adaptación, mitigación y gobernanza del cambio climático, derechos humanos y gestión del riesgo de desastres del sector minero energética, así como estrategias de desarrollo y relacionamiento territorial y la articulación de una agenda de relacionamiento interministerial con el Ministerio de Ambiente y Desarrollo Sostenible.", 
            className="card-text"),
        html.Div(
        html.Img(

                            src="assets\OAAS_cut.png",

                            id="Tabla7a-image",

                            style={

                                "height": "auto",
                                #"max-width": "750x",
                                "margin-top": "5px",
                                "display":"block",
                                'textAlign': 'center',
                                "margin-left": "15%",
                                "width": "70%",
                                # "margin-bottom": "5px",

                            },

                        )),
    ]))

card_references=dbc.Card(
    dbc.CardBody([
        html.H6("Oliver H. Lowry, Nira J. Rosenbrough, A. Lewis Farr, Rose J. Randall, “Protein Measurement with the Folin Phenol Reagent,” The Journal of Biological Chemistry (JBC) 193: 265-275, 1951",
            className="card-text"),
    ]))

card_explication_sem=dbc.Card(
    dbc.CardBody([
        html.H6("[Descripción provisional hecha por IA] Este visor de datos es una herramienta poderosa que permite a los usuarios explorar y comprender la dinámica de los conflictos en el sector mineroenergético. Funciona a través de un tablero de control intuitivo que facilita la navegación y el análisis de la información. Aquí tienes una descripción detallada de su funcionamiento:",
            className="card-text"),
        html.H6("Filtrado por múltiples variables: Los usuarios pueden filtrar los datos por departamento, gerencia, fecha y subsector. Esto les permite enfocarse en áreas específicas de interés y obtener información relevante para sus necesidades de análisis.",
            className="card-text"),
        html.H6("Tablero de control interactivo: El tablero de control proporciona una interfaz interactiva donde los usuarios pueden seleccionar fácilmente las variables de interés y ver los resultados de forma dinámica. Pueden explorar diferentes combinaciones de filtros para obtener una visión más completa de los datos.", 
            className="card-text"),
        html.H6("Modelado de resultados en gráficas: Los resultados de los filtros se representan visualmente a través de diversas gráficas y visualizaciones. Estas gráficas pueden incluir histogramas, gráficos de barras, gráficos de líneas, entre otros, dependiendo de la naturaleza de los datos y las preferencias del usuario. Además, el usuario puede ajustar la categorización de fecha y conteo para adaptarse a sus necesidades analíticas específicas.", 
            className="card-text"),
        html.H6("Mapa interactivo: El visor también incluye un mapa interactivo que muestra la ubicación geográfica de los conflictos mineroenergéticos reportados. Al hacer clic en un lugar específico en el mapa, los usuarios pueden acceder a información detallada sobre los informes de conflictos en esa ubicación particular, como la fecha del informe, el tipo de conflicto, las partes involucradas, entre otros detalles relevantes.", 
            className="card-text"),
        html.H6("En resumen, este visor de datos ofrece una experiencia de usuario completa y dinámica para explorar y comprender los conflictos en el sector mineroenergético. Con su capacidad de filtrado, modelado de resultados y visualización interactiva, los usuarios pueden obtener información valiosa para la toma de decisiones y la formulación de políticas.", 
            className="card-text"),
    ]))

app.layout = html.Div(children=[
     html.Div(

            [    
                html.Img(
                    src="assets\gobierno.png",
                    id="plotly-image",
                    className="logo-vida"
                ),                   
                 html.Div([
                html.H4(

                    "Visor de datos de conflictos mineroenergéticos",
                    style={'color':'black'},
                    className="model-title"

                    # style={"margin-bottom": "0px", 'textAlign': 'center','font-weight':'bold'},
                ),
                html.H6(

                    "Observatorio de la Oficina de Asuntos Ambientales y Sociales",
                    style={'color':'black'},
                    

                    # style={"margin-bottom": "0px", 'textAlign': 'center','font-weight':'bold'},
                )
                ],className="model-title"), 
                html.Img(
                    src="assets\OAAS_cut.png",
                    id="plotly-image3",
                    className="logo-oaas"
                ), 
                html.Img(
                    src="assets\ENERGÍA@4x.png",
                    id="plotly-image1",
                    className="logo-energia"
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
                color='#DDD0B4',
                style={'background-color': '#edb600',
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
    html.H2(children='Datos Generales',style={'color':'black'}),
    dcc.Graph(
        id='fig1',
        figure={},
        className='others',
    ),
    # dcc.Graph(
    #     id='geo1',
    #     figure={}
    # ),
    #html.H1(id='click-data'),#, style=styles['pre']),
    #Fin condicional ------------------------------
    html.H2(children='Conflictos',style={'color':'black'}),
    dcc.Graph(
        id='fig2',
        figure={}
    ),
    #Segmento Hidrocarburos
    html.Div([
        html.Div([
        dcc.Graph(
            id='fig9',
            figure={},
            config=config_pie
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='fig_C_segh',
            figure={},
            
        )],className='two_fig_2')]
             ,className='row flex-display'),
#Segmento Mineria
    html.Div([
        html.Div([
        dcc.Graph(
            id='figmin',
            figure={},
            config=config_pie
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='figminbar',
            figure={},
            
        )],className='two_fig_2')]
             ,className='row flex-display'),
#Segmento Energía
    html.Div([
        html.Div([
        dcc.Graph(
            id='figeng',
            figure={},
            config=config_pie
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='figengbar',
            figure={},
            
        )],className='two_fig_2')]
             ,className='row flex-display'),
#Escala de proyecto
    html.Div([
        html.Div([
        dcc.Graph(
            id='figesc',
            figure={},
            config=config_pie
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='figescbar',
            figure={},
            
        )],className='two_fig_2')]
             ,className='row flex-display'),
# Otrossmdoajdnajkd
    html.Div([
        html.Div([
        dcc.Graph(
            id='fig10',
            figure={},
            config=config_pie
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
            config=config_pie
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
            config=config_pie
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
            config=config_pie
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
            config=config_pie
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
            config=config_pie
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
            config=config_pie
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
            config=config_pie,
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
    html.H2(children='Alertas',style={'color':'black'}),
    dcc.Graph(
        id='fig_A_Subsector',
        figure={}
    ),
    dcc.Graph(
        id='fig3',
        figure={}
    ),
    # dcc.Graph(
    #     id='fig4',
    #     figure={}
    # ),
    html.Div([
        html.Div([
        dcc.Graph(
            id='fig5',
            figure={},
            config=config_pie
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
            config=config_pie
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
            config=config_pie
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
            config=config_pie
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='fig_A_info',
            figure={},
        )],className='two_fig_2')]
             ,className='row flex-display'),
    
# Nuevos subsectores
    html.Div([
        html.Div([
        dcc.Graph(
            id='fighidal',
            figure={},
            config=config_pie
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='fighidalbar',
            figure={},
        )],className='two_fig_2')]
             ,className='row flex-display'),
    html.Div([
        html.Div([
        dcc.Graph(
            id='figminal',
            figure={},
            config=config_pie
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='figminalbar',
            figure={},
        )],className='two_fig_2')]
             ,className='row flex-display'),

    html.Div([
        html.Div([
        dcc.Graph(
            id='figengal',
            figure={},
            config=config_pie
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='figengalbar',
            figure={},
        )],className='two_fig_2')]
             ,className='row flex-display'),

    html.Div([
        html.Div([
        dcc.Graph(
            id='figescal',
            figure={},
            config=config_pie
        )],className='two_fig'),
        html.Div([
        dcc.Graph(
            id='figescalbar',
            figure={},
        )],className='two_fig_2')]
             ,className='row flex-display'),
    html.Div([
                html.Div(
                    [     
    dbc.Button("¿Qué es el Observatorio de la Oficina de Asuntos Sociales y Ambientales (OAAS)?", 
               color='#DDD0B4',id="function_but_xl",className="me-1", n_clicks=0),
    dbc.Button("¿Como funciona el visor?",
               color='#DDD0B4', id="semaforo_but_xl",size="sm", className="me-1", n_clicks=0),
    dbc.Button("Referencias",
               color='#DDD0B4', id="references_but_xl",size="sm", className="me-1", n_clicks=0)
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
            dbc.ModalHeader(dbc.ModalTitle(html.H2("¿Qué es el Observatorio de la Oficina de Asuntos Sociales y Ambientales (OAAS)?")), close_button=True),
            dbc.ModalBody(card_function),
        ],
        id="function_mod_xl",
        # fullscreen=True,
        is_open=False,
        size="xl",
    ),
    dbc.Modal(
        [
            dbc.ModalHeader(html.H2(html.H2("Referencias"))),
            dbc.ModalBody(card_references),
        ],
        id="references_mod_xl",
        fullscreen=True,
        is_open=False,
        size="xl",
    ),
            dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(html.H2("¿Como funciona el visor?"))),
            dbc.ModalBody(card_explication_sem),
        ],
        id="semaforo_mod_xl",
        fullscreen=True,
        is_open=False,
        size="xl",
    ),
],
                      
                      style={"display": "flex", "flex-direction": "column"},)


def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

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
     
     Output(component_id='fig5', component_property='figure'),
     Output(component_id='fig6', component_property='figure'),
     Output(component_id='fig7', component_property='figure'),
     Output(component_id='fig8', component_property='figure'),
     Output(component_id='fig9', component_property='figure'),
     Output(component_id='fig10', component_property='figure'),
     
     Output(component_id='figmin', component_property='figure'),
     Output(component_id='figeng', component_property='figure'),
     Output(component_id='figesc', component_property='figure'),
     
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
     
     Output(component_id='figminbar', component_property='figure'),
     Output(component_id='figengbar', component_property='figure'),
     Output(component_id='figescbar', component_property='figure'),
     
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
     
    Output(component_id='fighidal', component_property='figure'),
    Output(component_id='figminal', component_property='figure'),
    Output(component_id='figengal', component_property='figure'),
    Output(component_id='figescal', component_property='figure'),
    Output(component_id='fighidalbar', component_property='figure'),
    Output(component_id='figminalbar', component_property='figure'),
    Output(component_id='figengalbar', component_property='figure'),
    Output(component_id='figescalbar', component_property='figure'),
    Output(component_id="loading-output-1", component_property='children'),
    Output(component_id="estado_filtro", component_property='children'),
    
     ],
    [Input('submit-val', 'n_clicks'),
     State(component_id='dep_id', component_property='value'),
     State(component_id='ger_id', component_property='value'),
     State(component_id='count_id', component_property='value'),
     State(component_id='subsector_id', component_property='value'),
     State(component_id='time_id', component_property='value'),
     State(component_id='DATE', component_property='start_date'),
     State(component_id='DATE', component_property='end_date'),]
)
def update_output_div(act,list_dep,list_ger,filter_ubi,subsector_filt,strfil,START_DATE,END_DATE):
    filter_ubi2='Ninguno'
    # list_dep=[dep[0:5]]
    # list_mun=[]
    # list_mun=[]
    #strfil='mun'
    # filter_ubi='Municipio'
    # filter_ubi2='Localizacion/zona'
    # if len(list_dep)==0:
    #     if len(list_ger)==0:
    #         list_dep.append('COLOMBIA')
    #     else:
    #         pass
    if np.any(np.isin(list_dep,'Todos los departamentos')):
        #df11=df1.copy()
        df21=df2.copy()
        #df31=df3.copy()
        i='Colombia'
    else:
        if len(list_ger)==0:
            if len(list_dep)==0:
                dep_fil=['']
            else:
                dep_fil=[LOC[dpt] for dpt in list_dep]
            df21=df2[np.isin(df2['Departamento'],dep_fil)]
            i='departamentos y municipios de consulta'
        else:
            # dep_fil=[LOC[dpt] for dpt in list_dep]
            df21=df2[np.isin(df2['Localizacion/zona'],list_ger)]
            text_list_ger=''
            for ger in list_ger:
                text_list_ger=text_list_ger+ger+'-'
            i=str(text_list_ger)
    #df21[['Conflicto/Subsector','Alerta/Subsector_generador_de_la_Aler','group_rl63j77/Subsector_generador_de_la_Aler','sub1','sub2','sub']] = df21[['Conflicto/Subsector','Alerta/Subsector_generador_de_la_Aler','group_rl63j77/Subsector_generador_de_la_Aler']].fillna(np.nan)
    #subsector_filt.append(np.nan)
    if np.any(np.isin(subsector_filt,'General')):
        pass
    else:
        df21=df21[(np.isin(df21['Conflicto/Subsector'],subsector_filt))|
                (np.isin(df21['Alerta/Subsector_generador_de_la_Aler'],subsector_filt))|
                (np.isin(df21['sub1'],subsector_filt))|
                (np.isin(df21['sub2'],subsector_filt))|
                (np.isin(df21['sub3'],subsector_filt))
                #(np.isin(df21['Otro/Subsector_00'],subsector_filt))|
                #(np.isin(df21['group_js6nn51/Subsector_001'],subsector_filt))
                ]
    df21=df21[(df21['FECHA - HORA UTC']<=END_DATE)&(df21['FECHA - HORA UTC']>=START_DATE)]
    if len(df21)==0:
        
        last_word='''
        * No se encuentra registros para su selección. Por favor modifique.
    '''
        fig=px.scatter()
        fig.update_layout(template=draft_nodata)
        [fig1,fig2,fig3,fig14,fig15,fig16,fig17,fig18,geo2,fig_A_Subsector,fig_dimall_ubi,fig_dimsoc_ubi,fig_dimeco_ubi,fig_dimam_ubi]=[[fig]*14][0]
        #fig_deter=[fig1,fig2,fig3,fig14,fig15,fig16,fig17,fig18,geo2,fig_A_Subsector,fig_dimall_ubi,fig_dimsoc_ubi,fig_dimeco_ubi,fig_dimam_ubi]
        fig_ls=[]
        fig_ls1=[]

        # for i in fig_deter:
        #     i=fig
        for i in range(16):
            fig_ls.append(fig)
            fig_ls1.append(fig)
    
    else:
        last_word=''
        if len(df21)!=0:
            # Datos Generales --------------------------------
            fig1=bar_all(filter_ubi2,df21,filter_ubi,'Inicio/Tipo_de_Reporte',i,'Tipos de reporte en ')
            # Conflictos --------------------------------
            fig2=bar_all(filter_ubi2,df21,filter_ubi,'Conflicto/Subsector',i,'Subsectores en ')
            # Alertas --------------------------------
            fig_A_Subsector=bar_all(filter_ubi2,df21,filter_ubi,'Alerta/Subsector_generador_de_la_Aler',i,'Subsectores en ')
            fig3=bar_all(filter_ubi2,df21,filter_ubi,'Alerta/Tipo_de_Alerta_Temprana',i,'Tipos de reporte de alerta en ')
            for fig in [fig2,fig_A_Subsector,fig3]:
                fig.update_layout(
                            legend=dict(itemwidth=80)) 
            # fig4=bar_all(filter_ubi2,df21,filter_ubi,'Alerta/Segmento_posiblemente_afectado',i)

            # Espacio ---------------------------
            fig_ls=[]
            col_ls_discrete=[]
            name_columns_space=["Conductas vulneratorias de "+i,
                "Afectaciones y_o impacto en "+i,
                "Principales actores involucrados en "+i,
                "Principales fuentes de información en "+i,
                
                "Segmento de Hidrocarburos Afectado en "+i,
                "Segmento de Minería Afectado en "+i,
                "Segmento de Energía Afectado en "+i,
                "Escala de proyecto (Mineria) "+i,
                
                "Principales Actores Involucrados en "+i,
                "Tipo de Accion de Conflicto en "+i,
                "Fuentes de Información en "+i,
                "Categorias de las Acciones en "+i,
                
                "Segmento de Hidrocarburos Afectado en "+i, #Hidrocarburos
                "Segmento de Minería Afectado en "+i, #Energia
                "Segmento de Energía Afectado en "+i, #Mineria
                "Escala de proyecto (Mineria) "+i
                ]
            for col,name in zip(columns_space,name_columns_space
                ):
                cd_vul=[]
                for ff in df21[col]:
                    try:
                        cd_vul.extend(ff.split(' '))
                    except:
                        pass
                cd_vul_1=[replace_dict[letter] for letter in cd_vul]
                unique, counts = np.unique(np.array(cd_vul_1), return_counts=True)
                count_sort_ind = np.argsort(-counts)
                unique=unique[count_sort_ind]
                counts=counts[count_sort_ind]
                if len(unique)!=0:
                    col_temp={}
                    for key,value in zip(unique,colorlist):
                        col_temp[key]=value
                    fignn=px.pie(names=unique,values= counts, title=name,color=unique,color_discrete_map=col_temp,labels={"count": "Conteo"})
                    fignn.update_traces(hoverinfo='label+percent+name', textposition='inside', textinfo='percent+label')
                    fignn.update(layout_showlegend=False)
                    fignn.update_layout(
                                legend=dict(font=dict(size=10),itemwidth=30)) # Para leyendas largas se puede simplificar con <br>
                    fignn.update_layout(template=draft_OAAS)
                    fig_ls.append(fignn)
                    col_ls_discrete.append(col_temp)
                else:
                    fignn=px.scatter()
                    draft_template.layout.annotations[0].text="No se registran datos para "+col
                    fignn.update_layout(template=draft_template)
                    fig_ls.append(fignn)
                    col_ls_discrete.append('')
                    #fig.show()
            fig_ls1=[]

            for col,name,col_temp in zip(columns_space,name_columns_space,col_ls_discrete
                ):
                cd_vul=[]
                filter_ubi_ls=[]
                for ff,ubi in zip(df21[col],df21[filter_ubi]):
                    try:
                        cd_vul.extend(ff.split(' '))
                        filter_ubi_ls.extend([str(ubi)]*len(ff.split(' ')))
                        #print(len(ff.split(' ')))
                    except:
                        fign={}
                    cd_vul_1=[replace_dict[letter] for letter in cd_vul]
                    #filter_ubi_ls_1=[replace_dict[letter] for letter in filter_ubi_ls]
                hist_df=pd.DataFrame()
                hist_df[filter_ubi]=filter_ubi_ls
                hist_df[col]=cd_vul_1
                if filter_ubi2=='Ninguno':
                    col_ls=[filter_ubi,col]
                    dfbar=hist_df[col_ls].value_counts().reset_index()
                    if len(dfbar)!=0:
                        fign = px.bar(dfbar, x=filter_ubi, y="count", color=col,title=name,color_discrete_map=col_temp,labels={"count": "Conteo"})
                        fign.update_layout(legend=dict(
                                        font=dict(size= 10),
                                        title_text=''))
                        fign.update_layout(template=draft_OAAS)
                        #fig.show()
                    else:
                        fign=px.scatter(title=name)
                        draft_template.layout.annotations[0].text="No se registran datos para "+col
                        fign.update_layout(template=draft_template)
                else:
                    filter_ubi_ls2=[]
                    for ff,ubi in zip(df21[col],df21[filter_ubi2]):
                        try:
                            filter_ubi_ls2.extend([str(ubi)]*len(ff.split(' ')))
                            #print(len(ff.split(' ')))
                        except:
                            fign={}
                    hist_df[filter_ubi2]=filter_ubi_ls2
                    col_ls=[filter_ubi,col,filter_ubi2]
                    dfbar=hist_df[col_ls].value_counts().reset_index()
                    if len(dfbar)!=0:
                        fign = px.bar(dfbar, x=filter_ubi, y="count", color=col, title=name,pattern_shape=filter_ubi2,color_discrete_map=col_temp,labels={"count": "Conteo"})
                        fign.update_layout(legend=dict(
                                        font=dict(size= 10),
                                        orientation="v",
                                        y=1,
                                        x=1,
                                        title_text=''))
                        fign.update_layout(template=draft_OAAS)
                        #fig.show()
                    else:
                        fign=px.scatter(title=name)
                        draft_template.layout.annotations[0].text="No se registran datos para "+col
                        fign.update_layout(template=draft_template)
                fig_ls1.append(fign)
        #----------------------------------------------------------

            dftime=df21[np.isin(df21['Inicio/Tipo_de_Reporte'],['Registro inicial Conflictividad','Registro Alerta Temprana','Otros reportes/actividades'])]
            dfsegcierr=df21[np.isin(df21['Inicio/Tipo_de_Reporte'],['Cierre','Seguimiento Conflictividad','Seguimiento Alerta Temprana'])]

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
                    # print(dftime_fil)
                    if np.any(np.isin(dftime_fil['Inicio/Tipo_de_Reporte'].unique(),['Seguimiento Conflictividad','Seguimiento Alerta Temprana'])):
                        for i in dftime_fil[(np.isin(dftime_fil['Inicio/Tipo_de_Reporte'],['Seguimiento Conflictividad','Seguimiento Alerta Temprana']))]['Inicio/Fecha_de_ocurrencia_del_evento'].sort_values():
                            x.append(i)
                            y.append(_id)
                    if not np.any(np.isin(dftime_fil['Inicio/Tipo_de_Reporte'].unique(),['Cierre'])):
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
                    if np.any(np.isin(dftime_fil['Inicio/Tipo_de_Reporte'].unique(),['Cierre'])):
                        x.append(dftime_fil[dftime_fil['Inicio/Tipo_de_Reporte']=='Cierre']['Inicio/Fecha_de_ocurrencia_del_evento'].values[0])
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
                                font_family='Nunito Sans'
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
            # print(filter_ubi_am)
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
            # if filter_ubi2=='Ninguno':
            df_soc = df_soc.drop(df_soc[df_soc['Tipo'] == 'nan'].index)
            df_eco = df_eco.drop(df_eco[df_eco['Tipo'] == 'nan'].index)
            df_am = df_am.drop(df_am[df_am['Tipo'] == 'nan'].index)
            
            # df_freq=df_freq.replace(replace_dict)
            df_soc=df_soc.replace(replace_dict)
            df_eco=df_eco.replace(replace_dict)
            df_am=df_am.replace(replace_dict)
            
            df_freq=pd.concat([df_soc,df_eco,df_am])
            fig15 = px.line_polar(df_freq[['Dimension']].value_counts().reset_index(), r="count", theta="Dimension",line_close=True,
                            title="Grafico de cuantificacion dimensional"
                            )
            fig15.update_layout(
                        legend=dict(itemwidth=80),template=draft_OAAS) 
            fig_dimall_ubi=px.bar(df_freq[['Dimension','Ubicacion']].value_counts().reset_index(), x='Ubicacion', y="count", color='Dimension', title='Grafico de cuantificacion dimensional',labels={"count": "Conteo"})
            fig_dimall_ubi.update_layout(template=draft_OAAS)
            fig16=px.pie(df_soc[['Tipo']].value_counts().reset_index(),names='Tipo',values= 'count', title='Social',labels={"count": "Conteo"})
            fig16.update_traces(hoverinfo='label+percent+name', textposition='inside', textinfo='percent+label')
            fig16.update(layout_showlegend=False)
            fig16.update_layout(template=draft_OAAS)
            fig_dimsoc_ubi=px.bar(df_soc[['Tipo','Ubicacion']].value_counts().reset_index(), x='Ubicacion', y="count", color='Tipo', title='Grafico de cuantificacion dimensional social',labels={"count": "Conteo"})
            fig_dimsoc_ubi.update_layout(template=draft_OAAS)
            fig17=px.pie(df_eco[['Tipo']].value_counts().reset_index(),names='Tipo',values= 'count', title='Economica',labels={"count": "Conteo"})
            fig17.update_traces(hoverinfo='label+percent+name', textposition='inside', textinfo='percent+label')
            fig17.update(layout_showlegend=False)
            fig17.update_layout(template=draft_OAAS)
            fig_dimeco_ubi=px.bar(df_eco[['Tipo','Ubicacion']].value_counts().reset_index(), x='Ubicacion', y="count", color='Tipo', title='Grafico de cuantificacion dimensional economico',labels={"count": "Conteo"})  
            fig_dimeco_ubi.update_layout(template=draft_OAAS)
            fig18=px.pie(df_am[['Tipo']].value_counts().reset_index(),names='Tipo',values= 'count', title='Ambiental',labels={"count": "Conteo"})
            fig18.update_traces(hoverinfo='label+percent+name', textposition='inside', textinfo='percent+label')
            fig18.update(layout_showlegend=False)
            fig18.update_layout(template=draft_OAAS)
            fig_dimam_ubi=px.bar(df_am[['Tipo','Ubicacion']].value_counts().reset_index(), x='Ubicacion', y="count", color='Tipo', title='Grafico de cuantificacion dimensional ambiental',labels={"count": "Conteo"})
            fig_dimam_ubi.update_layout(template=draft_OAAS)
                # fig16.update_layout(legend=dict(font=dict(size=10),itemwidth=30)) 
                # fig17.update_layout(legend=dict(font=dict(size=10),itemwidth=30)) 
                # fig18.update_layout(legend=dict(font=dict(size=10),itemwidth=30))         
            # else:
            #     filter_ubi_soc2=[]
            #     filter_ubi_eco2=[]
            #     filter_ubi_am2=[]
            #     for soc1,eco1,am1,ubi in zip(df21['Conflicto/Carac/Categor_a_del_conflicto_Dime'],
            #             df21['Conflicto/Carac/Categor_as_del_conflicto_Dim_001'],
            #             df21['Conflicto/Carac/Categor_as_del_Conflicto_Dim'],
            #             df21[filter_ubi2]):
            #                 filter_ubi_soc2.extend([str(ubi)]*len(str(soc1).split(' ')))
            #                 filter_ubi_eco2.extend([str(ubi)]*len(str(eco1).split(' ')))
            #                 filter_ubi_am2.extend([str(ubi)]*len(str(am1).split(' ')))
            #     df_soc[filter_ubi2]=filter_ubi_soc2
            #     df_eco[filter_ubi2]=filter_ubi_eco2
            #     df_am[filter_ubi2]=filter_ubi_am2
            #     df_soc = df_soc.drop(df_soc[df_soc['Tipo'] == 'nan'].index)
            #     df_eco = df_eco.drop(df_eco[df_eco['Tipo'] == 'nan'].index)
            #     df_am = df_am.drop(df_am[df_am['Tipo'] == 'nan'].index)
                
            #     df_freq=pd.concat([df_soc,df_eco,df_am])
            #     fig15 = px.line_polar(df_freq[['Dimension']].value_counts().reset_index(), r="count", theta="Dimension",line_close=True,
            #                     title="Grafico de cuantificacion dimensional"
            #                     )
            #     fig_dimall_ubi=px.bar(df_freq[['Dimension','Ubicacion',filter_ubi2]].value_counts().reset_index(), x='Ubicacion', y="count", color='Dimension', title='Grafico de cuantificacion dimensional',pattern_shape=filter_ubi2)
            #     fig16=px.pie(df_soc[['Tipo']].value_counts().reset_index(),names='Tipo',values= 'count', title='Social')
            #     fig_dimsoc_ubi=px.bar(df_soc[['Tipo','Ubicacion',filter_ubi2]].value_counts().reset_index(), x='Ubicacion', y="count", color='Tipo', title='Grafico de cuantificacion dimensional social',pattern_shape=filter_ubi2)
            #     fig17=px.pie(df_eco[['Tipo']].value_counts().reset_index(),names='Tipo',values= 'count', title='Economica')
            #     fig_dimeco_ubi=px.bar(df_eco[['Tipo','Ubicacion',filter_ubi2]].value_counts().reset_index(), x='Ubicacion', y="count", color='Tipo', title='Grafico de cuantificacion dimensional economico',pattern_shape=filter_ubi2)
            #     fig18=px.pie(df_am[['Tipo']].value_counts().reset_index(),names='Tipo',values= 'count', title='Ambiental')
            #     fig_dimam_ubi=px.bar(df_am[['Tipo','Ubicacion',filter_ubi2]].value_counts().reset_index(), x='Ubicacion', y="count", color='Tipo', title='Grafico de cuantificacion dimensional ambiental',pattern_shape=filter_ubi2)
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
                            mapbox_style="open-street-map",color_continuous_scale=px.colors.sequential.Jet,labels={"count": "Conteo"})
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
                        color='black',
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
            #source="assets\OAAS_cut.png",
            xref="paper", yref="paper",
            x=1.1, y=-0.1,
            sizex=0.4, sizey=0.4,
            xanchor="right", yanchor="bottom"
        )
    )

    #Pie
        for i in fig_ls[0],fig_ls[1],fig_ls[2],fig_ls[3],fig_ls[4],fig_ls[8],fig_ls[5],fig_ls[6],fig_ls[7],fig_ls[9],fig_ls[10],fig_ls[11],fig_ls[12],fig_ls[13],fig_ls[14],fig_ls[15],fig14,fig15,fig16,fig17,fig18:
            i.update_layout(font_family='Nunito Sans')
            i.add_annotation( #¡Personalizarla por tipo de grafica!
                text=f"Observatorio OAAS. <br>Extraido el {c.strftime('%d/%m/%y')}",
                align="left",
                showarrow=False,
                xref="paper",
                yref="paper",
                font=dict(color="black", size=11,family='Nunito Sans'),
                bgcolor="rgba(0,0,0,0)",
                y=0,
                x=0.8,
                xanchor="left",
            )  

    #bar dere
        for i in fig1,fig2,fig3,fig_ls1[4],fig_ls1[5],fig_ls1[6],fig_ls1[7],fig_ls1[8],fig_ls1[9],fig_ls1[10],fig_ls1[11],fig_ls1[0],fig_ls1[1],fig_ls1[2],fig_ls1[3],fig_ls1[12],fig_ls1[13],fig_ls1[14],fig_ls1[15],fig_A_Subsector,fig_dimall_ubi,fig_dimsoc_ubi,fig_dimeco_ubi,fig_dimam_ubi,:
            i.update_layout(font_family='Nunito Sans')
            i.add_annotation( #¡Personalizarla por tipo de grafica!
                text=f"Observatorio OAAS. <br>Extraido el {c.strftime('%d/%m/%y')}",
                align="left",
                showarrow=False,
                xref="paper",
                yref="paper",
                font=dict(color="black", size=11,family='Nunito Sans'),
                bgcolor="rgba(0,0,0,0)",
                y=-0.26,
                x=1.025,
                xanchor="left",
            )  
            
    #mapa y tiempo
        for i in geo2,:
            i.update_layout(font_family='Nunito Sans')
            i.add_annotation( #¡Personalizarla por tipo de grafica!
                text=f"Observatorio OAAS. <br>Extraido el {c.strftime('%d/%m/%y')}",
                align="left",
                showarrow=False,
                xref="paper",
                yref="paper",
                font=dict(color="black", size=11,family='Nunito Sans'),
                bgcolor="rgba(0,0,0,0)",
                y=0,
                x=0,
                xanchor="left",
            )  

        # for i in fig1,fig2,fig3,fig_ls[0],fig_ls[1],fig_ls[2],fig_ls[3],fig_ls[4],fig_ls[5],fig_ls[6],fig_ls[7],fig_ls[8],fig14,fig15,fig16,fig17,fig18,geo2,fig_A_Subsector,fig_ls1[4],fig_ls1[5],fig_ls1[6],fig_ls1[7],fig_ls1[8],fig_ls1[0],fig_ls1[1],fig_ls1[2],fig_ls1[3],fig_dimall_ubi,fig_dimsoc_ubi,fig_dimeco_ubi,fig_dimam_ubi:
        #     i.update_layout(font_family='Nunito Sans')
        #     i.add_annotation( #¡Personalizarla por tipo de grafica!
        #         text="Extraido del visor de conflictos mineroenergteivos del observatorio de la OAAS. fecha (xx/xx/xx)",
        #         align="left",
        #         showarrow=False,
        #         xref="paper",
        #         yref="paper",
        #         font=dict(color="black", size=9),
        #         bgcolor="rgba(0,0,0,0)",
        #         y=0.2,
        #         x=1,
        #         xanchor="left",
        #     )
            # i.add_annotation(
            #     showarrow=False,
            #     text=note,
            #     font=dict(size=10), 
            #     xref='x domain',
            #     x=1.1,
            #     yref='y domain',
            #     y=-0.1
            #     )
        #Analisis total & = or y merges np.isin
    loading=time.sleep(1)
    return fig1,fig2,fig3,fig_ls[0],fig_ls[1],fig_ls[2],fig_ls[3],fig_ls[4],fig_ls[8],fig_ls[5],fig_ls[6],fig_ls[7],fig_ls[9],fig_ls[10],fig_ls[11],fig14,fig15,fig16,fig17,fig18,geo2,fig_A_Subsector,fig_ls1[4],fig_ls1[5],fig_ls1[6],fig_ls1[7],fig_ls1[8],fig_ls1[9],fig_ls1[10],fig_ls1[11],fig_ls1[0],fig_ls1[1],fig_ls1[2],fig_ls1[3],fig_dimall_ubi,fig_dimsoc_ubi,fig_dimeco_ubi,fig_dimam_ubi,fig_ls[12],fig_ls[13],fig_ls[14],fig_ls[15],fig_ls1[12],fig_ls1[13],fig_ls1[14],fig_ls1[15],loading,last_word

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
    # print(json.loads(clc)['points'][0]['lon'])
    df_table=df2[((df2['latitud']==lat)&(df2['longitud']==lon))|
                (df2['lat']==lat)&(df2['lon']==lon)]
    df_table=df_table.replace(replace_dict)
    # df_table=df_table.replace({'<br>':'\n'})
    cols_names=[columns_confc,columns_alertas,columns_sconfc,columns_cierr,columns_salerta,columns_otro]
    def change_names(x):
        try:
            names=str(x).split(' ')
            namesx=[replace_dict[letter] for letter in names]
            namx=''
            for stringss in namesx:
                try:
                    stringss.replace('<br>','')
                except:
                    pass
                namx=namx+'\n'+stringss
            return namx
        except:
            return(str(x))
    for colss in cols_names:
        for col in colss:
            df_table[col]=df_table[col].apply(lambda x:change_names(x))
            # cd_vul=[]
            # for ff in df_table[col]:
            #     try:
            #         cd_vul.extend(ff.split(' '))
            #     except:
            #         pass
            # text_column=''

    #Conflictos -----------------------------------------
    confc=df_table[df_table['Inicio/Tipo_de_Reporte']=='Registro inicial Conflictividad']
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
    alertas=df_table[df_table['Inicio/Tipo_de_Reporte']=='Registro Alerta Temprana']
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
    sconfc=df_table[df_table['Inicio/Tipo_de_Reporte']=='Seguimiento Conflictividad']
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
    cierr=df_table[df_table['Inicio/Tipo_de_Reporte']=='Cierre']
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
    salerta=df_table[df_table['Inicio/Tipo_de_Reporte']=='Seguimiento Alerta Temprana']
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
    otro=df_table[df_table['Inicio/Tipo_de_Reporte']=='Otros reportes/actividades']
    
    if len(otro)>0: 
        # print(otro)  
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
