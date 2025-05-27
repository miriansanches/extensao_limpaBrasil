import streamlit as sl
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

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
        'Alto da Lapa - ZO','Alto de Pinheiros - ZO','Jardim Paulista','Vila Romana','Vila Madalena'
    ],
    'Bairros mais sujos e perigosos': [
        'Capão Redondo - ZS','Santa Cecilia - Centro','República - Centro','Sé - Centro','Brasilândia - ZN'
    ]
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
    'Campos Elisios - Centro': 'Campos Elíseos - Centro'
}
for errado, correto in correcoes.items():
    df['Bairro'] = df['Bairro'].replace(errado, correto)
    for key in data:
        if isinstance(data[key], list):
            data[key] = [correcoes.get(b, b) for b in data[key]]

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
    sl.title('Comparação entre bairros de São Paulo')

    # Cards de resumo
    contagem = {
        'Seguros': df_filtrado['Seguro'].sum(),
        'Perigosos': df_filtrado['Perigoso'].sum(),
        'Limpos': df_filtrado['Limpo'].sum(),
        'Sujos': df_filtrado['Sujo'].sum()
    }
    col1, col2, col3, col4 = sl.columns(4)
    col1.metric("Seguros", contagem['Seguros'])
    col2.metric("Perigosos", contagem['Perigosos'])
    col3.metric("Limpos", contagem['Limpos'])
    col4.metric("Sujos", contagem['Sujos'])

    sl.markdown("### Quantidade de bairros por categoria")
    contagem_df = pd.DataFrame(contagem.items(), columns=['Categoria', 'Quantidade'])

    fig = px.bar(contagem_df, x='Categoria', y='Quantidade', color='Categoria',
                 title='Número de bairros selecionados por categoria',
                 color_discrete_map={
                     'Seguros': 'green',
                     'Perigosos': 'red',
                     'Limpos': 'blue',
                     'Sujos': 'orange'
                 })
    sl.plotly_chart(fig, use_container_width=True)

    # Gráfico de pizza adicional
    fig_pizza = px.pie(contagem_df, names='Categoria', values='Quantidade', 
                       title='Distribuição dos bairros por categoria',
                       color='Categoria',
                       color_discrete_map={
                           'Seguros': 'green',
                           'Perigosos': 'red',
                           'Limpos': 'blue',
                           'Sujos': 'orange'
                       })
    sl.plotly_chart(fig_pizza, use_container_width=True)

    # Gráfico de barras para compostos
    comp_counts = {
        'Seguros & Limpos': df_filtrado['Seguro_e_Limpo'].sum(),
        'Sujos & Perigosos': df_filtrado['Sujo_e_Perigoso'].sum()
    }
    comp_df = pd.DataFrame(comp_counts.items(), columns=['Categoria Composta', 'Quantidade'])
    fig_comp = px.bar(comp_df, x='Categoria Composta', y='Quantidade', color='Categoria Composta',
                      color_discrete_map={
                          'Seguros & Limpos': 'green',
                          'Sujos & Perigosos': 'red'
                      },
                      title='Bairros por categorias compostas')
    sl.plotly_chart(fig_comp, use_container_width=True)

    sl.markdown('---')
    sl.markdown('### Bairros filtrados')
    sl.dataframe(df_filtrado[['Bairro', 'Seguro', 'Perigoso', 'Limpo', 'Sujo', 'Seguro_e_Limpo', 'Sujo_e_Perigoso']].reset_index(drop=True))

    # Download dos dados filtrados
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    sl.download_button("Baixar dados filtrados", csv, "bairros_filtrados.csv", "text/csv")

    # Explicação/Insight
    sl.info("Os bairros mais limpos nem sempre são os mais seguros, e vice-versa. Explore as interseções nos gráficos!")

def graficos():
    sl.title('Análise da hipótese: limpeza e segurança')

    # Gráfico de barras para bairros seguros e limpos / sujos e perigosos
    comp_counts = {
        'Seguros & Limpos': df_filtrado['Seguro_e_Limpo'].sum(),
        'Sujos & Perigosos': df_filtrado['Sujo_e_Perigoso'].sum()
    }
    comp_df = pd.DataFrame(comp_counts.items(), columns=['Categoria Composta', 'Quantidade'])
    fig_comp = px.bar(comp_df, x='Categoria Composta', y='Quantidade', color='Categoria Composta',
                      color_discrete_map={
                          'Seguros & Limpos': 'green',
                          'Sujos & Perigosos': 'red'
                      },
                      title='Bairros por categorias compostas')
    sl.plotly_chart(fig_comp, use_container_width=True)

    # Gráfico de barras das combinações (já existente)
    def categoriza(row):
        categorias = []
        if row['Seguro']:
            categorias.append('Seguro')
        if row['Perigoso']:
            categorias.append('Perigoso')
        if row['Limpo']:
            categorias.append('Limpo')
        if row['Sujo']:
            categorias.append('Sujo')
        return ' & '.join(sorted(categorias)) if categorias else 'Nenhuma categoria'

    df_filtrado['Categorias'] = df_filtrado.apply(categoriza, axis=1)

    contagem = df_filtrado['Categorias'].value_counts().reset_index()
    contagem.columns = ['Combinação', 'Quantidade']

    with sl.spinner('Gerando gráfico...'):
        fig = px.bar(contagem, x='Combinação', y='Quantidade',
                     color='Quantidade', color_continuous_scale='Viridis',
                     title='Interseção das categorias dos bairros')
        sl.plotly_chart(fig, use_container_width=True)

    sl.markdown('### Detalhes dos bairros por categoria')
    sl.dataframe(df_filtrado.sort_values('Categorias').reset_index(drop=True))

def graficos():
 sl.title('Análise focada: bairros limpos & seguros vs. sujos & perigosos')

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
    ### Principais conclusões

    - Nem sempre os bairros mais limpos são os mais seguros, o que indica que limpeza e segurança são fatores independentes em muitos casos.
    - A interseção entre bairros seguros e limpos é pequena, destacando áreas que podem servir de referência para políticas públicas.
    - Bairros sujos e perigosos concentram desafios sociais e ambientais que merecem atenção integrada.
    - A análise permite identificar padrões para direcionar investimentos em segurança e limpeza urbana.

    ### Próximos passos

    - Coletar dados reais com coordenadas geográficas para análises espaciais mais precisas.
    - Implementar análises temporais para acompanhar evolução da segurança e limpeza.
    - Integrar feedback dos usuários para melhorar a base de dados e as visualizações.

    ### Feedback recebido
    """)

    if 'feedbacks' in sl.session_state and sl.session_state['feedbacks']:
        for i, fb in enumerate(sl.session_state['feedbacks'], 1):
            sl.markdown(f"**Feedback {i}:** {fb['texto']}  \nAvaliação: {fb['avaliacao']}")
    else:
        sl.info("Nenhum feedback enviado ainda. Use o formulário na barra lateral para contribuir!")

def sobre():
    sl.title("Sobre o Dashboard")
    sl.markdown("""
    Este dashboard foi criado para analisar a relação entre limpeza e segurança em bairros de São Paulo.
    Os dados são fictícios e servem apenas para fins didáticos.
    
    - **Fontes**: Exemplos baseados em listas públicas e reportagens.
    - **Funcionalidades**: Filtros, gráficos interativos, busca, download de dados, análise de interseção de categorias e coleta de feedback.
    - **Desenvolvedor**: [Seu Nome]
    """)

def sidebar():
    with sl.sidebar:
        selecionado = option_menu(
            menu_title='Menu',
            options=['Home', 'Gráficos','Limpos & Seguros vs Sujos & Perigosos', 'Insights', 'Sobre'],
            icons=['house', 'bar-chart', 'lightbulb','shield-shaded', 'info-circle'],
            default_index=0
        )
    if selecionado == 'Home':
        home()
    elif selecionado == 'Gráficos':
        graficos()
    elif selecionado == 'Insights':
        insights()
    elif selecionado == 'Limpos & Seguros vs Sujos & Perigosos':
        graficos()
    else:
        sobre()

sidebar()
