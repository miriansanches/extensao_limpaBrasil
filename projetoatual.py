import streamlit as sl
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
import re

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
    zona_top_limpos = df_grafico.loc[df_grafico['Limpos'].idxmax()]['Zona'] if df_grafico['Limpos'].sum() > 0 else "Nenhuma"
    zona_top_sujos = df_grafico.loc[df_grafico['Sujos'].idxmax()]['Zona'] if df_grafico['Sujos'].sum() > 0 else "Nenhuma"
    zona_top_seguros = df_grafico.loc[df_grafico['Seguros'].idxmax()]['Zona'] if df_grafico['Seguros'].sum() > 0 else "Nenhuma"
    zona_top_perigosos = df_grafico.loc[df_grafico['Perigosos'].idxmax()]['Zona'] if df_grafico['Perigosos'].sum() > 0 else "Nenhuma"

    sl.info(f"Zona com mais bairros limpos: **{zona_top_limpos}**")
    sl.info(f"Zona com mais bairros sujos: **{zona_top_sujos}**")
    sl.info(f"Zona com mais bairros seguros: **{zona_top_seguros}**")
    sl.info(f"Zona com mais bairros perigosos: **{zona_top_perigosos}**")

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