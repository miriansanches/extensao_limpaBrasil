import streamlit as sl
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
import re



from PIL import Image

# Configuração da página
sl.set_page_config(page_title='Analise do lixo em SP', page_icon='🏙️', layout='wide')

# Dados fixos
data = {
    'Posicoes': list(range(1, 11)),
    'Bairros mais seguros de SP': [
        'Alto da Lapa - ZO','Alto de Pinheiros - ZO','Higienópolis - Centro','Jardim América - ZO',
        'Jardim Paulista - ZO','Perdizes - ZO','Pinheiros -ZO','Pompéia - ZO','Vila Madalena - ZO','Vila Romana - ZO'
    ],
    'Bairros mais perigosos de SP': [
        'Capão Redondo - ZS','Campo Limpo - ZS','Pinheros - ZO','Campos Elisios - Centro','Sé - Centro',
        'Perdizes - ZO','Consoloção - Centro','Pari - Centro','Santo Amaro - ZS','Parque Santo Antônio - ZS'
    ],
    'Bairros mais sujos de SP': [
        'Santa Cecilia - Centro', 'República - Centro', 'Freguesia - ZN', 'Santana - ZN','Bom Retiro - Centro',
        'Brasilândia - ZN','Lapa - ZO','Belém - ZL','Itaim Bibi - ZO','Pinheiros - ZO'
    ],
    'Bairros mais limpos de SP': [
        'Marsilac - ZS','Anhanguera - ZO','Paralheiros - ZS','Perus - ZO','Cidade Tirandentes - ZL',
        'Parque do Carmo - ZL','Ponte Rasa - ZL','Socorro - ZS','José Bonifácio - ZL', 'São Rafael - ZL'
    ],
    'Bairros mais seguros e limpos': [
        'Alto da Lapa - ZO','Jardim Paulista','Vila Madalena'
    ],
    'Bairros mais sujos e perigosos': [
        'Capão Redondo - ZS','Santa Cecilia - Centro','República - Centro','Sé - Centro','Brasilândia - ZN'
    ]
}

# Dicionário de coordenadas dos bairros (ajustado para os nomes do seu dataset)
coordenadas_bairros = {
    "Alto da Lapa - ZO": (-23.5353, -46.7131),
    "Alto de Pinheiros - ZO": (-23.5586, -46.7267),
    "Higienópolis - Centro": (-23.5489, -46.6581),
    "Jardim América - ZO": (-23.5614, -46.6736),
    "Jardim Paulista - ZO": (-23.5649, -46.6544),
    "Perdizes - ZO": (-23.5332, -46.6781),
    "Pinheiros - ZO": (-23.5671, -46.6936),
    "Pompéia - ZO": (-23.5276, -46.6785),
    "Vila Madalena - ZO": (-23.5615, -46.6922),
    "Vila Romana - ZO": (-23.5237, -46.6872),
    "Capão Redondo - ZS": (-23.6761, -46.7902),
    "Campo Limpo - ZS": (-23.6266, -46.7616),
    "Campos Elíseos - Centro": (-23.5377, -46.6389),
    "Sé - Centro": (-23.5505, -46.6333),
    "Consolação - Centro": (-23.5512, -46.6612),
    "Pari - Centro": (-23.5272, -46.6186),
    "Santo Amaro - ZS": (-23.6485, -46.7133),
    "Parque Santo Antônio - ZS": (-23.6639, -46.7695),
    "Santa Cecilia - Centro": (-23.5426, -46.6462),
    "República - Centro": (-23.5446, -46.6486),
    "Freguesia - ZN": (-23.4922, -46.7013),
    "Santana - ZN": (-23.5015, -46.6253),
    "Bom Retiro - Centro": (-23.5316, -46.6336),
    "Brasilândia - ZN": (-23.4566, -46.7013),
    "Lapa - ZO": (-23.5272, -46.7059),
    "Belém - ZL": (-23.5362, -46.5913),
    "Itaim Bibi - ZO": (-23.5886, -46.6855),
    "Marsilac - ZS": (-23.8456, -46.7983),
    "Anhanguera - ZO": (-23.4205, -46.7696),
    "Paralheiros - ZS": (-23.8467, -46.7357),
    "Perus - ZO": (-23.3968, -46.7361),
    "Cidade Tirandentes - ZL": (-23.5696, -46.3974),
    "Parque do Carmo - ZL": (-23.5644, -46.4842),
    "Ponte Rasa - ZL": (-23.4945, -46.5378),
    "Socorro - ZS": (-23.6625, -46.7033),
    "José Bonifácio - ZL": (-23.5443, -46.4183),
    "São Rafael - ZL": (-23.5734, -46.4347),
}

# Criar DataFrame com bairros únicos
todos_bairros = set()
for lista in data.values():
    if isinstance(lista, list):
        todos_bairros.update(lista)
df = pd.DataFrame({'Bairro': list(todos_bairros)})

# Correções de nomes para garantir correspondência correta
correcoes = {
    'Pinheros - ZO': 'Pinheiros - ZO',
    'Consoloção - Centro': 'Consolação - Centro',
    'Campos Elisios - Centro': 'Campos Elíseos - Centro',
    'Pinheiros -ZO': 'Pinheiros - ZO',
    'Jardim Paulista': 'Jardim Paulista - ZO',
    'Vila Romana': 'Vila Romana - ZO',
    'Vila Madalena': 'Vila Madalena - ZO'
}
df['Bairro'] = df['Bairro'].replace(correcoes)
for key in data:
    if isinstance(data[key], list):
        data[key] = [correcoes.get(b, b) for b in data[key]]

# Adiciona as colunas de latitude e longitude ao DataFrame
df['lat'] = df['Bairro'].map(lambda x: coordenadas_bairros.get(x, (None, None))[0])
df['lon'] = df['Bairro'].map(lambda x: coordenadas_bairros.get(x, (None, None))[1])

df = pd.DataFrame([
    {"Bairro": bairro, "lat": coord[0], "lon": coord[1]}
    for bairro, coord in coordenadas_bairros.items()
])

# Exemplo de categorias para cada bairro (você deve substituir pelos seus dados reais)
# Categorias: 'Perigoso', 'Limpo', 'Seguro', 'Sujo'
categorias = {
    "Alto da Lapa - ZO": "Seguro",
    "Alto de Pinheiros - ZO": "Limpo",
    "Higienópolis - Centro": "Seguro",
    "Jardim América - ZO": "Limpo",
    "Jardim Paulista - ZO": "Seguro",
    "Perdizes - ZO": "Limpo",
    "Pinheiros - ZO": "Limpo",
    "Pompéia - ZO": "Perigoso",
    "Vila Madalena - ZO": "Limpo",
    "Vila Romana - ZO": "Sujo",
    "Capão Redondo - ZS": "Perigoso",
    "Campo Limpo - ZS": "Perigoso",
    "Campos Elíseos - Centro": "Seguro",
    "Sé - Centro": "Perigoso",
    "Consolação - Centro": "Seguro",
    "Pari - Centro": "Perigoso",
    "Santo Amaro - ZS": "Sujo",
    "Parque Santo Antônio - ZS": "Sujo",
    "Santa Cecilia - Centro": "Perigoso",
    "República - Centro": "Perigoso",
    "Freguesia - ZN": "Limpo",
    "Santana - ZN": "Limpo",
    "Bom Retiro - Centro": "Perigoso",
    "Brasilândia - ZN": "Perigoso",
    "Lapa - ZO": "Limpo",
    "Belém - ZL": "Sujo",
    "Itaim Bibi - ZO": "Seguro",
    "Marsilac - ZS": "Perigoso",
    "Anhanguera - ZO": "Sujo",
    "Paralheiros - ZS": "Sujo",
    "Perus - ZO": "Perigoso",
    "Cidade Tirandentes - ZL": "Sujo",
    "Parque do Carmo - ZL": "Sujo",
    "Ponte Rasa - ZL": "Sujo",
    "Socorro - ZS": "Sujo",
    "José Bonifácio - ZL": "Sujo",
    "São Rafael - ZL": "Sujo"
}

# Adicionar coluna de categoria no DataFrame
df['Categoria'] = df['Bairro'].map(categorias)

color_map = {
    'Perigoso': 'red',
    'Limpo': 'lightblue',
    'Seguro': 'darkblue',
    'Sujo': 'salmon'  # vermelho claro
}

# Colunas booleanas para categorias
df['Seguro'] = df['Bairro'].isin(data['Bairros mais seguros de SP'])
df['Perigoso'] = df['Bairro'].isin(data['Bairros mais perigosos de SP'])
df['Limpo'] = df['Bairro'].isin(data['Bairros mais limpos de SP'])
df['Sujo'] = df['Bairro'].isin(data['Bairros mais sujos de SP'])

# Categorias compostas
df['Seguro_e_Limpo'] = df['Bairro'].isin(data['Bairros mais seguros e limpos'])
df['Sujo_e_Perigoso'] = df['Bairro'].isin(data['Bairros mais sujos e perigosos'])

# Filtros sidebar
sl.sidebar.header('Selecione os filtros')

seguros_filter = sl.sidebar.multiselect(
    'Bairros mais seguros de SP',
    options=data['Bairros mais seguros de SP'],
    default=data['Bairros mais seguros de SP'],
    key='seguros'
)

perigosos_filter = sl.sidebar.multiselect(
    'Bairros mais perigosos de SP',
    options=data['Bairros mais perigosos de SP'],
    default=data['Bairros mais perigosos de SP'],
    key='perigosos'
)

limpos_filter = sl.sidebar.multiselect(
    'Bairros mais limpos de SP',
    options=data['Bairros mais limpos de SP'],
    default=data['Bairros mais limpos de SP'],
    key='limpos'
)

sujos_filter = sl.sidebar.multiselect(
    'Bairros mais sujos de SP',
    options=data['Bairros mais sujos de SP'],
    default=data['Bairros mais sujos de SP'],
    key='sujos'
)

# Busca rápida por bairro
busca = sl.sidebar.text_input("Buscar bairro")
sl.sidebar.markdown("---")

# Formulário de feedback na sidebar
with sl.sidebar.form("feedback_form"):
    sl.markdown("### Deixe seu feedback ou sugestão")
    feedback_text = sl.text_area("Comentários", max_chars=500)
    feedback_rating = sl.selectbox("Avaliação geral", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"])
    submitted_feedback = sl.form_submit_button("Enviar feedback")
    if submitted_feedback:
        if 'feedbacks' not in sl.session_state:
            sl.session_state['feedbacks'] = []
        sl.session_state['feedbacks'].append({'texto': feedback_text, 'avaliacao': feedback_rating})
        sl.success("Obrigado pelo seu feedback!")

# Filtrar DataFrame conforme seleção e busca
df_filtrado = df[
    (df['Bairro'].isin(seguros_filter)) |
    (df['Bairro'].isin(perigosos_filter)) |
    (df['Bairro'].isin(limpos_filter)) |
    (df['Bairro'].isin(sujos_filter))
].copy()

if busca:
    df_filtrado = df_filtrado[df_filtrado['Bairro'].str.contains(busca, case=False)]

def home():
    sl.title('Análise do Lixo e Segurança em São Paulo')
    sl.markdown("""
        Este dashboard permite explorar a relação entre limpeza urbana e segurança nos bairros da cidade de São Paulo.
        Utilize os filtros ao lado para selecionar bairros e veja como as categorias se distribuem.
        """)

        # Cards de resumo
    seguros_limpos = df_filtrado[df_filtrado['Seguro_e_Limpo']]
    sujos_perigosos = df_filtrado[df_filtrado['Sujo_e_Perigoso']]

            # Gráfico de barras comparativo
    comp_counts = {
                'Limpos & Seguros': seguros_limpos.shape[0],
                'Sujos & Perigosos': sujos_perigosos.shape[0]
            }
    comp_df = pd.DataFrame(comp_counts.items(), columns=['Grupo', 'Quantidade'])
    fig_bar = px.bar(comp_df, x='Grupo', y='Quantidade', color='Grupo',
                            color_discrete_map={'Limpos & Seguros': 'green', 'Sujos & Perigosos': 'red'},
                            title='Comparativo: Bairros Limpos & Seguros vs. Sujos & Perigosos')
    sl.plotly_chart(fig_bar, use_container_width=True)

    sl.markdown('---')
    sl.markdown('### Bairros filtrados')
    sl.dataframe(df_filtrado[['Bairro', 'Seguro', 'Perigoso', 'Limpo', 'Sujo', 'Seguro_e_Limpo', 'Sujo_e_Perigoso']].reset_index(drop=True))

            # Download dos dados filtrados
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    sl.download_button("Baixar dados filtrados", csv, "bairros_filtrados.csv", "text/csv")

def graficos():
    sl.title('Bairros por Zona de São Paulo')

    def extrair_zona(bairro):
        match = re.search(r'-\s*(ZO|ZS|ZN|ZL|Centro)', bairro)
        if match:
            zona = match.group(1)
            if zona == 'Centro':
                return 'Centro'
            elif zona == 'ZO':
                return 'Zona Oeste'
            elif zona == 'ZS':
                return 'Zona Sul'
            elif zona == 'ZN':
                return 'Zona Norte'
            elif zona == 'ZL':
                return 'Zona Leste'
        return 'Zona Desconhecida'
        # Mapa dos bairros filtrados
    # Adicione a coluna de zona
    df_filtrado['Zona'] = df_filtrado['Bairro'].apply(extrair_zona)

# Mapa customizado com legenda e cores
    df_mapa = df_filtrado.dropna(subset=['lat', 'lon'])
    if not df_mapa.empty:
        fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color="Categoria",
        hover_name="Bairro",
        zoom=10,
        center={"lat": -23.55, "lon": -46.63},  # Centro aproximado de São Paulo
        mapbox_style="carto-darkmatter",
        color_discrete_map=color_map,
        title="Mapa dos bairros classificados por categoria"
    )

    # Exibir o mapa no Streamlit
        sl.plotly_chart(fig, use_container_width=True)
    else:
        print("Nenhum bairro com coordenadas disponíveis para exibir no mapa.")



    # Função para extrair a zona do nome do bairro
    def extrair_zona(bairro):
        match = re.search(r'-\s*(ZO|ZS|ZN|ZL|Centro)', bairro)
        if match:
            zona = match.group(1)
            if zona == 'Centro':
                return 'Centro'
            elif zona == 'ZO':
                return 'Zona Oeste'
            elif zona == 'ZS':
                return 'Zona Sul'
            elif zona == 'ZN':
                return 'Zona Norte'
            elif zona == 'ZL':
                return 'Zona Leste'
        return 'Zona Desconhecida'

    # Cria coluna Zona sem sobrescrever df_filtrado original
    df_zonas = df_filtrado.copy()
    df_zonas['Zona'] = df_zonas['Bairro'].apply(extrair_zona)

    zonas = ['Centro', 'Zona Norte', 'Zona Sul', 'Zona Leste', 'Zona Oeste']

    dados_grafico = []
    for zona in zonas:
        df_zona = df_zonas[df_zonas['Zona'] == zona]
        dados_grafico.append({
            'Zona': zona,
            'Seguros': df_zona['Seguro'].sum(),
            'Perigosos': df_zona['Perigoso'].sum(),
            'Limpos': df_zona['Limpo'].sum(),
            'Sujos': df_zona['Sujo'].sum()
        })

    df_grafico = pd.DataFrame(dados_grafico)
    df_long = df_grafico.melt(id_vars='Zona', 
                              value_vars=['Seguros', 'Perigosos', 'Limpos', 'Sujos'],
                              var_name='Categoria', value_name='Quantidade')

    fig = px.bar(df_long, x='Zona', y='Quantidade', color='Categoria', barmode='group',
                 title='Quantidade de bairros por categoria em cada zona de São Paulo',
                 labels={'Zona': 'Zona de São Paulo', 'Quantidade': 'Número de Bairros', 'Categoria': 'Categoria'})
    sl.plotly_chart(fig, use_container_width=True)

    # Insights abaixo do gráfico
    sl.markdown("### Insights por Zona")

    sl.info("Podemos ver, que a zona que tem bairros mais seguros (Zona Oeste) é considerada uma zona nobre da cidade de SP. **")
    sl.info("Podemos correlacionar a questão de segurança e limpeza com a teoria da janela quebrada")
    sl.info("Em contrapartida, o lugar aonde há bairros menos seguros (Centro), é considerado uam área suja da região de SP")
    sl.info("Em todas as nossas pesquisas, vimos também, que as cidades em que há maior registro de segurança, há maior coleta de limpeza")

def comparativo_limpos_sujos():
    sl.title('🟢 Limpos & Seguros vs 🔴 Sujos & Perigosos')

    # Contagem dos bairros compostos
    seguros_limpos = df_filtrado[df_filtrado['Seguro_e_Limpo']]
    sujos_perigosos = df_filtrado[df_filtrado['Sujo_e_Perigoso']]

    # Gráfico de barras comparativo
    comp_counts = {
        'Limpos & Seguros': seguros_limpos.shape[0],
        'Sujos & Perigosos': sujos_perigosos.shape[0]
    }
    comp_df = pd.DataFrame(comp_counts.items(), columns=['Grupo', 'Quantidade'])
    fig_bar = px.bar(comp_df, x='Grupo', y='Quantidade', color='Grupo',
                     color_discrete_map={'Limpos & Seguros': 'green', 'Sujos & Perigosos': 'red'},
                     title='Comparativo: Bairros Limpos & Seguros vs. Sujos & Perigosos')
    sl.plotly_chart(fig_bar, use_container_width=True)

    # Gráfico de pizza comparativo
    fig_pie = px.pie(comp_df, names='Grupo', values='Quantidade',
                     color='Grupo',
                     color_discrete_map={'Limpos & Seguros': 'green', 'Sujos & Perigosos': 'red'},
                     title='Proporção: Limpos & Seguros vs. Sujos & Perigosos')
    sl.plotly_chart(fig_pie, use_container_width=True)

    # Listas detalhadas
    sl.markdown("### Lista de bairros limpos & seguros")
    sl.write(seguros_limpos['Bairro'].tolist() if not seguros_limpos.empty else "Nenhum bairro encontrado.")

    sl.markdown("### Lista de bairros sujos & perigosos")
    sl.write(sujos_perigosos['Bairro'].tolist() if not sujos_perigosos.empty else "Nenhum bairro encontrado.")

    # Insight automático
    sl.info(f"Total de bairros limpos & seguros: {seguros_limpos.shape[0]}")
    sl.info(f"Total de bairros sujos & perigosos: {sujos_perigosos.shape[0]}")
    if seguros_limpos.shape[0] > sujos_perigosos.shape[0]:
        sl.success("Há mais bairros limpos & seguros do que sujos & perigosos nesta seleção!")
    elif seguros_limpos.shape[0] < sujos_perigosos.shape[0]:
        sl.error("Atenção: há mais bairros sujos & perigosos do que limpos & seguros nesta seleção!")
    else:
        sl.warning("O número de bairros limpos & seguros e sujos & perigosos está igual nesta seleção.")

    # Gráfico de barras mostrando o percentual em relação ao total filtrado
    total = df_filtrado.shape[0]
    if total > 0:
        percent_df = pd.DataFrame({
            'Grupo': ['Limpos & Seguros', 'Sujos & Perigosos'],
            'Percentual': [seguros_limpos.shape[0]/total*100, sujos_perigosos.shape[0]/total*100]
        })
        fig_percent = px.bar(percent_df, x='Grupo', y='Percentual', color='Grupo',
                             color_discrete_map={'Limpos & Seguros': 'green', 'Sujos & Perigosos': 'red'},
                             title='Percentual dos grupos em relação ao total filtrado')
        sl.plotly_chart(fig_percent, use_container_width=True)

def insights():
    sl.title("Insights e Conclusões")
    sl.markdown("""
    ### Detalhes do Projeto

    - O nosso trabalho teve como objetivo estudar a relação entre a sujeira e a falta de segurança dos bairros.
    - O grupo responsável por este trabalho realizou uma ação social na coleta de lixo junto a ONG Limpa Brasil no bairro Heliópolis, uma das cidades classificadas como mais sujas, de acordo com os gráficos e pesquisas. O motivo foi justamente os pontos viciados de lixo, lá presentes.
    - A hipótese desta pesquisa segue o viés da criminologia da Teoria das Janelas Quebradas, que sugere que sinais visíveis de desordem e lixo, como janelas quebradas não consertadas, podem levar ao aumento do crime e da desorganização em uma área.
    - Percebemos que há uma forte ligação entre os bairros que são mais limpos e seguros (considerados bairros nobres) e os bairros mais sujos e com maior taxa de marginalização (bairros inseguros), reforçando a Teoria da Janela Quebrada.

    ### Conclusões e Propostas

    - Por questões sociais, vemos que bairros mais marginalizados são esteriotipados como mais perigosos.
    - Contextualização: Conforme a amostragem das bases de dados e gráficos, alguns bairros aparecem com uma taxa muito discrepante ao tratar de limpeza e sujeira. Onde bairros masi sujos tem cada vez mais tendência de marginalização e bairros mais nobres sofreram um crescimento na taxa de assalto, pois pessoas de classe alta se tornam alvos para assaltos. 
    
    ### Como Resolver
    -Como resolver:
        1. Denúncia e Fiscalização;
        2. Coleta Seletiva;
        3. Educação Ambiental;
        4. Ecopontos e Pontos de Entrega Voluntária (PEV);
        5. Parcerias Público-Privadas (PPPs);
        6. Tecnologias Sustentáveis;
        7. Reciclagem e Reutilização;
        8. Fiscalização e Combate ao Descarte Irregular;
        
                           
                            

    ### Feedback recebido
    """)

    if 'feedbacks' in sl.session_state and sl.session_state['feedbacks']:
        for i, fb in enumerate(sl.session_state['feedbacks'], 1):
            sl.markdown(f"**Feedback {i}:** {fb['texto']}  \nAvaliação: {fb['avaliacao']}")
    else:
        sl.info("Nenhum feedback enviado ainda. Use o formulário na barra lateral para contribuir!")

def sobre():
    sl.title("Sobre o Dashboard")
    image = Image.open('image\WhatsApp Image 2025-05-24 at 11.19.40.jpeg')  # ou use uma URL diretamente em st.image()
    sl.markdown("""
    Este dashboard foi criado para analisar a relação entre limpeza e segurança em bairros de São Paulo.
    Os dados são reais e servem para comparação e dados para a Limpa Brasil.
    
    - **Fontes**: Dados da limpa Brasil e dados de bairros em SP.
    - **Funcionalidades**: Filtros, gráficos interativos, busca, download de dados, análise de interseção de categorias e coleta de feedback.
    - **Desenvolvedores**: Mirian Sanches, Nicoli Felipe, Guilherme Souza, Júlia Garzo, Lorena Gabarão, Vitória Gatutti
    """
    )

    sl.markdown("""
    Aonde você pode nos encontrar:
                
                """)
    sl.markdown("""
- [Mirian Sanches](https://www.linkedin.com/in/miriansanches)
- [Nicoli Felipe](https://www.linkedin.com/in/nicoli-felipe/)
- [Guilherme Souza](https://www.linkedin.com/in/guilherme-henrique-oliveira-de-souza)
- [Júlia Garzo](https://www.linkedin.com/in/juliagarzo)
- [Lorena Gabarão](https://www.linkedin.com/in/lorenagabarao/)
- [Vitória Gatutti](https://www.linkedin.com/in/galuttivitoria)
""")
    image = Image.open('image\WhatsApp Image 2025-05-24 at 11.19.40.jpeg')  # ou use uma URL diretamente em st.image()
    sl.image(image, caption="Foto da equipe", use_column_width=True)

    

def sidebar():
    with sl.sidebar:
        selecionado = option_menu(
            menu_title='Menu',
            options=['Home', 'Gráficos', 'Limpos & Seguros vs Sujos & Perigosos', 'Insights', 'Sobre'],
            icons=['house', 'bar-chart', 'shield-shaded', 'lightbulb', 'info-circle'],
            default_index=0
        )
    if selecionado == 'Home':
        home()
    elif selecionado == 'Gráficos':
        graficos()
    elif selecionado == 'Limpos & Seguros vs Sujos & Perigosos':
        comparativo_limpos_sujos()
    elif selecionado == 'Insights':
        insights()
    else:
        sobre()

sidebar()
