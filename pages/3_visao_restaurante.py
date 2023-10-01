#Instalers
#!pip install haversine
#!pip install plotly

#Libaries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import numpy as np

#Biblioteca necessárias
import folium
from streamlit_folium import folium_static
from datetime import datetime
import pandas as pd
import re

st.set_page_config( page_title='Visão Restaurantes', page_icon='🍽️', layout='wide')

#===============================================================================================#
# Funções
#===============================================================================================#

#----------------------------------------------#
#Average Distance
#----------------------------------------------# 

def distance(df1):
    cols = ['Restaurant_latitude', 'Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
    df1['Distance'] = df1.loc[:,cols].apply( lambda x:
                                haversine( (x['Restaurant_latitude'],x['Restaurant_longitude']),
                                           (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis = 1)
    avg_distance = np.round(df1['Distance'].mean(),2)
    return avg_distance

#----------------------------------------------#
#average e standard deviation
#----------------------------------------------# 

def avg_std_time_delivery (df1, festival, op):
    """
        Esta função calcula o tempo médio e o desvio padrão do tempo de entrega com o festival.
        Parâmetros:
            Input:
                -df: Dataframe com os dados necessários para cálculo
                -op: Tipo de operação que precisa ser calculado
                    'avg_time': Calcula o tempo médio.
                    'std_time': Calcula o desvio padrão do tempo.
            output:
                -df: Dataframe com 2 colunas e 1 linha.
    """ 
           
    df_aux = (df1.loc[:, ['Time_taken(min)','Festival']]
                 .groupby('Festival')
                 .agg({'Time_taken(min)' : ['mean','std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op],2)
    
    return df_aux

#----------------------------------------------#
#Tempo médio de entrega por cidade - pie graph
#----------------------------------------------# 

def avg_time_delivery_city_graph (df1):
    cols = ['Restaurant_latitude', 'Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
    df1['Distance'] = df1.loc[:,cols].apply( lambda x:
                                    haversine( (x['Restaurant_latitude'],x['Restaurant_longitude']),
                                               (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis = 1)
    avg_distance = df1.loc[:, ['City','Distance']].groupby('City').mean().reset_index()
    
    fig = go.Figure ( data = [go.Pie (labels = avg_distance['City'], #O "P" de Pie é maiúsculo
                              values=avg_distance['Distance'],
                              pull=[0, 0.1, 0])]) # Esse "0.1" é pra dar destaque em um elemento da pizza
    return fig

#--------------------------------------------#
#Tempo de entrega por cidade - columns graph
#--------------------------------------------# 

def deliverty_time_city (df1):
    df_aux = df1.loc[:,['Time_taken(min)','City']].groupby(['City']).agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    
    fig=go.Figure() #Atenção: O "F" de Figure é maiúsculo
    fig.add_trace(go.Bar(name = 'Control', #Atenção: O "B" de Bar é maiúsculo
             x=df_aux['City'],
             y=df_aux['avg_time'],
             error_y=dict( type = 'data', array=df_aux['std_time'])))
    
    fig.update_layout(barmode='group')
    
    return fig

#---------------------------------------------#
#Tempo médio por tippo de entrega - dataframe
#---------------------------------------------# 

def avg_time_delivery_type (df1):
    df_aux = (df1.loc[:,['Time_taken(min)','City','Type_of_order']]
                 .groupby(['City','Type_of_order'])
                 .agg({'Time_taken(min)':['mean','std']}))
    df_aux.columns = ['Time_taken_mean','Time_taken_std']
    df_aux.reset_index()
    
    return df_aux

#---------------------------------------------#
#Distribuição da distânci - sunbrust graph
#---------------------------------------------#

def distance_distribuction (df1):
    df_aux = (df1.loc[:,['Time_taken(min)','City','Road_traffic_density']]
                 .groupby(['City','Road_traffic_density'])
                 .agg({'Time_taken(min)':['mean','std']}))
    df_aux.columns = ['avg_time','std_time']
    df_aux=df_aux.reset_index()
    
    fig=px.sunburst (df_aux, path=['City','Road_traffic_density'], values='avg_time', color='std_time',
                     color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig

#----------------------------------------------#
#Limpando os dados
#----------------------------------------------#    
def clean_code(df1):

    """ 
        Esta função tem a responsabilidade de limpar o dataframe

        Tipos de limpeza:
        1 -> Remoção dos dados NaN
        2 -> Mudança do tipo da coluna de dados
        3 -> Remoção dos espaços das variáveis de texto
        4 -> Formatação da coluna de datas
        5 -> Limpeza da coluna de tempo (remoção do texto da variável numérica)

        Imput: Dataframe
        Output: Dataframe    
    """
    #Limpeza 
    # Fazendo uma cópia do DataFrame lido -> transformar df para df1
    df1 = df.copy()
    # 1.0 - Converter uma coluna de texto (string ou object- str) para número inteiro (int)
        #Apagar as linhas vazias - NaN
    linhas_vazias = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :].copy()
    
    linhas_vazias = df1['Weatherconditions'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :].copy()
    
    linhas_vazias = df1['Road_traffic_density'] !='NaN '
    df1 = df1.loc[linhas_vazias, :].copy()
    
    linhas_vazias = df1['ID'] !='NaN '
    df1 = df1.loc[linhas_vazias, :].copy()
    
    linhas_vazias = df1['City'] !='NaN '
    df1 = df1.loc[linhas_vazias, :].copy()
    
    linhas_vazias = df1['Time_taken(min)'] !='NaN '
    df1 = df1.loc[linhas_vazias, :].copy()
    
        # 1.1 - Delivery_person_Age
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )
    
        #1.2 - multiple_deliveries
            # OBS - Vai precisar apagar as linhas vazias também
    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )
    
    # 2.0 - Converter uma coluna de texto (string ou object- str) para número quebrado (float) - Delivery_person_Ratings
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )
    
    # 3.0 - Converter uma coluna de texto (string ou object- str) para uma data - Order_Date
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y')
    
    #4.0 - Removendo espaços dos textos/string/object
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()
    
    #5.0 - Removendo o texto de números
    #df = df.reset_index( drop=True )
    #for i in range (len(df)):
    #  df.loc[i, 'Time_taken(min)'] = re.findall(r'\d+',df.loc[i,'Time_taken(min)'])
    
    #6.0 - Removendo o '(min) ' do 'Time_taken(min)'
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split(' ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1
    
#=============================== Início da Estrutura Lógica do Código ===============================#

#----------------------------------------------#
#Import dataset
#----------------------------------------------#

df = pd.read_csv('dataset/train.csv')

#----------------------------------------------#
#Limpando os dados
#----------------------------------------------#

df1 = clean_code(df)

#=========================================================================#
# streamlit: streamlit run visao_restaurante.py
#=========================================================================#
# SIDEBAR
#=========================================================================#

st.header('Marketplace - visão restaurantes', divider='blue') #Criar Títulos

#image_path = 'Banco-do-Brasil-logo.png'
image = Image.open ('Banco-do-Brasil-logo.png')
st.sidebar.image (image, width = 120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 3, 9),
    min_value=datetime(2022,2,11),
    max_value=datetime(2022,4,6),
    format='DD-MM-YYYY')


st.sidebar.markdown("""___""")

traffic_option = st.sidebar.multiselect(
    'Quais as condições de trânsito :sparkles:',
    ['Low','Medium','High','Jam'],
    default= ['Low','Medium','High','Jam']) #Tem que ser um valor existente dentro da lista a cima

st.sidebar.markdown("""___""")
st.sidebar.markdown ('### Powered by Carneiro :sunglasses:')

## Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas , :]

## Filtro de condições climáticas
linhas_selecionadas = df1['Road_traffic_density'].isin (traffic_option)
df1 = df1.loc[linhas_selecionadas , :]

#=========================================================================#
# LAYOUT NO STREAMLIT
#=========================================================================#

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

#-------------------------------- Tab1 -----------------------------------#
with tab1:
    #==================== Container 1 ==================#  
    with st.container():
        st.title(':blue[Overall Metrics] :sunglasses:')
        col1, col2, col3= st.columns(3,)

        with col1:
            
            entregadores = df1.loc[:,'Delivery_person_ID'].nunique()
            col1.metric('Delivery Men', entregadores)

        with col2:

            avg_distance = distance (df1)
            col2.metric('Average Distance', avg_distance)          
                                      
        with col3:
            
            df_aux = avg_std_time_delivery (df1, 'Yes', 'avg_time')
            col3.metric('AVG in', df_aux)         
                                            
    #==================== Container 2 ==================#
    with st.container():
        col1, col2, col3 = st.columns(3,)
            
        with col1:

            df_aux = avg_std_time_delivery (df1, 'Yes', 'std_time')
            col1.metric('STD in', df_aux)
                        
        with col2:

            df_aux = avg_std_time_delivery (df1, 'No', 'avg_time')
            col2.metric('AVG out', df_aux)         
                                   
        with col3:

            df_aux = avg_std_time_delivery (df1, 'No', 'std_time')
            col3.metric('STD out', df_aux)

    #==================== Container 3 ==================# 
    with st.container():
        st.markdown("""___""")
        st.title (' :blue[Tempo médio de entrega por cidade]')
        fig = avg_time_delivery_city_graph (df1)
        st.plotly_chart (fig, use_container_width=True)      

    #==================== Container 4 ==================#                                               
    with st.container():
        st.markdown("""___""")
        st.title(' :blue[Distribuição do tempo]')
        col1,col2 = st.columns(2, gap='large')

        with col1:
            st.markdown('##### Tempo de entrega por cidade')
            fig = deliverty_time_city (df1)
            st.plotly_chart (fig, use_container_width=True)          
            
        with col2:
            st.markdown('##### Tempo médio por tipo de entrega')
            df_aux = avg_time_delivery_type (df1)
            st.dataframe(df_aux)                

    #==================== Container 5 ==================#
    with st.container():
        st.markdown("""___""")
        st.title(' :blue[Distribuição da distância]')
        fig = distance_distribuction (df1)
        st.plotly_chart (fig, use_container_width=True)    
