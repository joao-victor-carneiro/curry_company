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

st.set_page_config( page_title='Visão Entregadores', page_icon='📌', layout='wide')

#===============================================================================================#
# Funções
#===============================================================================================#

#--------------------------------------#
#Top entregadores -> Mais lento ou mais rápido
#Utilizamos uma função para executar tanto a operação de ver os melhores entregadores
#quanto os piores entregadores através da variável criada "top_asc".
#--------------------------------------# 
def top_delivers (df1, top_asc):
    df2 = (df1.loc[:,['Delivery_person_ID','Time_taken(min)','City']]
                 .groupby(['City','Delivery_person_ID'])
                 .max()
                 .sort_values(['City','Time_taken(min)'],ascending = top_asc)
                 .reset_index())   
    
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', : ].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', : ].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', : ].head(10)
    df3 = pd.concat( [df_aux01,df_aux02,df_aux03 ]).reset_index( drop = True)
    
    return df3
    
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
    
#==================================================== Início da Estrutura Lógica do Código =================================================#

#--------------------------------------#
#Import dataset
#--------------------------------------#
df = pd.read_csv('dataset/train.csv')
#--------------------------------------#
#Limpando os dados
#--------------------------------------#
df1 = clean_code(df)


#=========================================================================#
# streamlit: streamlit run visao_entregadores.py
#=========================================================================#
# SIDEBAR
#=========================================================================#

st.header('Marketplace - visão entregadores') #Criar Títulos

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

weather_option = st.sidebar.multiselect(
    'Quais as condições de climáticas :sparkles:',
    ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
       'conditions Cloudy', 'conditions Fog', 'conditions Windy'],
    default= ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
       'conditions Cloudy', 'conditions Fog', 'conditions Windy']) #Tem que ser um valor existente dentro da lista a cima

st.sidebar.markdown("""___""")
st.sidebar.markdown ('### Powered by Carneiro :sunglasses:')

## Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas , :]

## Filtro de condições climáticas
linhas_selecionadas = df1['Weatherconditions'].isin (weather_option)
df1 = df1.loc[linhas_selecionadas , :]

#=========================================================================#
# LAYOUT NO STREAMLIT
#=========================================================================#

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

#-------------------------------- Tab1 -----------------------------------#
with tab1:
    #==================== Container 1 ==================#
    with st.container():
        st.title(':blue[Overall Metrics]')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        with col1:
            
            idade = df1.loc[:,'Delivery_person_Age']
            idade_max = max(idade)
            col1.metric('Older Age', idade_max)

        with col2:
            
            idade_min = min(idade)
            col2.metric('Younger Age', idade_min)
            
        with col3:
            
            vehicle_conditions = df1.loc[:,'Vehicle_condition']
            melhor = max(vehicle_conditions)
            col3.metric('better condition of vehicles',melhor)

        with col4:
            
            pior = min(vehicle_conditions)
            col4.metric('worst condition of vehicles', pior)
            
    #==================== Container 2 ==================#
    with st.container():
        st.markdown("""___""")
        st.title (' :blue[Avaliações]')
        col1,col2 = st.columns (2, gap="small")
        
        with col1:
            st.markdown ('##### Avaliação média dos entregadores')
            mean_delivery_rating = ( df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings'] ]
                                    .groupby('Delivery_person_ID')
                                    .mean()
                                    .reset_index())
            st.dataframe (mean_delivery_rating)

        with col2:
            st.markdown (' ##### Avaliação média e desvio padrão por tráfego')
            df_avg_rating_by_traffic =( (df1.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                                            .groupby('Road_traffic_density')
                                            .agg({'Delivery_person_Ratings':['mean','std']}))) 
            df_avg_rating_by_traffic.columns = ['delivery_mean','delivery_std']                
            st.dataframe (df_avg_rating_by_traffic.reset_index())
            
            st.markdown ('##### Avaliação média e desvio padrão por clíma')
            df_avg_rating_by_Weatherconditions = ((df1.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                                                      .groupby('Weatherconditions')
                                                      .agg({'Delivery_person_Ratings' : ['mean','std']})))                
            df_avg_rating_by_Weatherconditions.columns = ['delivery_mean','delivery_std']                
            st.dataframe (df_avg_rating_by_Weatherconditions.reset_index())
                                                  
    #==================== Container 3 ==================#
    with st.container():
        st.markdown("""___""")
        st.title(' :blue[Velocidade de Entrega]')
        col1,col2 = st.columns(2, gap='large')

        with col1:
            st.markdown ('##### Top entregadores mais rápidos')
            df3 = top_delivers (df1, top_asc=True) #-> Utilização do "top_asc" para crescente
            st.dataframe(df3)          
                    
        with col2:
            st.markdown ('##### Top entregadores mais lentos')
            df3 = top_delivers (df1, top_asc=False)  #-> Utilização do "top_asc" para decrescente
            st.dataframe(df3)
            
            













