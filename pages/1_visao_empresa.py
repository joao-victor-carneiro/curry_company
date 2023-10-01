#Instalers
#!pip install haversine
#!pip install plotly

#Libaries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

#Biblioteca necessárias
import folium
from streamlit_folium import folium_static
from datetime import datetime
import pandas as pd
import re

st.set_page_config( page_title='Visão Empresa', page_icon='📊', layout='wide')
#===============================================================================================#
# Funções
#===============================================================================================#

#--------------------------------------#
#Order metrics - gráfico de linhas
#--------------------------------------#
def order_metrics(df1):
    cols = ['ID','Order_Date']
    df_aux = df1.loc[:,cols].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux, x='Order_Date',y='ID')
            
    return fig
#--------------------------------------#
#traffic order share - gráfico de pizza
#--------------------------------------#
def traffic_order_share (df1):
    cols = ['ID','Road_traffic_density']
    df_aux = df1.loc[:,cols].groupby('Road_traffic_density').count().reset_index()
    df_aux ['entregas_perc'] = df_aux['ID']/df_aux['ID'].sum()    
    fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')

    return fig
#--------------------------------------#
#traffic order city - gráfico de bolhas
#--------------------------------------#    
def traffic_order_city (df1):
    cols = ['ID','City','Road_traffic_density']
    df_aux = df1.loc[:,cols].groupby(['City','Road_traffic_density']).count().reset_index()
    df_aux['perc_ID'] = 100*(df_aux['ID']/df_aux['ID'].sum())            
    fig = px.scatter(df_aux, x='City',y='ID',size='ID', color='Road_traffic_density')
    
    return fig
#--------------------------------------#
#order by week - gráfico de linhas
#--------------------------------------# 
def order_by_week (df1):          
    df1['Week_of_Year'] = df1['Order_Date'].dt.strftime("%U")
    cols = ['Week_of_Year', 'ID']
    df_aux = df1.loc[:,cols].groupby('Week_of_Year').count().reset_index()    
    fig = px.line(df_aux, x='Week_of_Year',y='ID')
        
    return fig
#--------------------------------------#
#order shares by week - gráfico de linhas
#--------------------------------------# 
def order_share_by_week (df1):
    df1['Week_of_Year'] = df1['Order_Date'].dt.strftime("%U") #Criando a coluna 'Week_of_Year' no dataframe principal
    df_aux1 = df1.loc[:,['ID','Week_of_Year']].groupby('Week_of_Year').count().reset_index() #Pedidos por semana
    df_aux2 = df1.loc[:,['Delivery_person_ID','Week_of_Year']].groupby('Week_of_Year').nunique().reset_index() #Pedidos por entregadores únicos
    df_aux = pd.merge(df_aux1, df_aux2, how = 'inner') #Juntar o resultado dos dois dataframes
    df_aux['Order_by_Delivery'] = df_aux['ID']/df_aux['Delivery_person_ID'] #Criar a coluna 'Order_by_Delivery' com a operação em questão para o agrupamento
    fig = px.line(df_aux, x='Week_of_Year', y='Order_by_Delivery') #Gráfico de linhas

    return fig
#--------------------------------------#
#country map - mapa
#--------------------------------------# 
def country_map (df1):
    df_aux = ( df1.loc[:,['Delivery_location_latitude','Delivery_location_longitude','Road_traffic_density','City']]
                  .groupby(['City','Road_traffic_density'])
                  .median()
                  .reset_index())
    map = folium.Map()
    for index, location_info in df_aux.iterrows():

        folium.Marker([location_info['Delivery_location_latitude'],location_info['Delivery_location_longitude']],
                            popup=location_info[['City','Road_traffic_density']]).add_to(map)
    folium_static( map, width=1024, height=600)

#--------------------------------------#
#Limpando os dados
#--------------------------------------#    
def clean_code(df1):

    """ Esta função tem a responsabilidade de limpar o dataframe

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
    
#=================================== Início da Estrutura Lógica do Código ========================================#

#--------------------------------------#
#Import dataset
#--------------------------------------#
df = pd.read_csv('dataset/train.csv')
#--------------------------------------#
#Limpando os dados
#--------------------------------------#
df1 = clean_code(df)

#=========================================================================#
# streamlit: streamlit run visao_empresa.py
#=========================================================================#
# SIDEBAR
#=========================================================================#

st.header('Marketplace - visão cliente', divider='blue') #Criar Títulos

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

## Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin (traffic_option)
df1 = df1.loc[linhas_selecionadas , :]

#=========================================================================================================#
# Comando do streamlit: lAYOUT
#=========================================================================================================#

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', ' Visão Tática', 'Visão Geográfica'])
#VISÃO - EMPRESA

#-------------------------------------------TAB 1---------------------------------------------------------#
with tab1:
    #==================== Container 1 ==================#
    with st.container():
        fig = order_metrics(df1)
        st.markdown('# Orders by day')
        st.plotly_chart (fig, use_container_width=True) #Importar gráfico para o plotly o 'use_container_width=True' é para o gráfico caber na tela.

    #==================== Container 2 ==================#
    with st.container(): #Criar colunas dentro de um container
        col1, col2 = st.columns(2)

        with col1: #Gráfico de pizza            
            fig = traffic_order_share (df1)
            st.header ('Traffic Order Share')
            st.plotly_chart (fig, use_container_width=True)            
            
            
        with col2: #Gráfico de bolhas
            fig = traffic_order_city (df1)
            st.header ('Traffic Order City')
            st.plotly_chart (fig, use_container_width=True)
            
#-------------------------------------------TAB 2---------------------------------------------------------#
with tab2:
    #==================== Container 1 ==================#
    with st.container():

        fig = order_by_week (df1)
        st.markdown('# Order by Week')
        st.plotly_chart (fig, use_container_width=True)    
        
    #==================== Container 2 ==================#
    with st.container():

        fig = order_share_by_week (df1)
        st.markdown('# Order share by Week')
        st.plotly_chart (fig, use_container_width=True)       
                
#-------------------------------------------TAB 3---------------------------------------------------------#
with tab3:  #Criação de mapas
    st.markdown('# Country Map')
    country_map (df1)
























