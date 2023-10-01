import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon= "🎲"
    
)

#image_path = 'Banco-do-Brasil-logo.png'
image = Image.open ('Banco-do-Brasil-logo.png')
st.sidebar.image (image, width = 120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.write ("# Curry Company Growth Dashboard")

st.markdown(
    """
    Growth dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão da Empresa:
        - Visão Grencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão do Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão dos Restaurantes:
        - Indicadores semanais de crescimeto dos restaurantes.
    ### Ask for help
    - Time de Data Science no discord
        - @Carneiro
    """)
