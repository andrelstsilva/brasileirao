# Importar bibliotecas
import requests
import numpy as np
import pandas as pd
import plotly.express as px 
import plotly.io as pio
import streamlit as st
from plotly.subplots import make_subplots

def buscar_dados_brasileirao():

    # Endpoint público
    url = "https://api.cartola.globo.com/atletas/mercado"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    resposta = requests.get(url, headers=headers, timeout=30)
    resposta.raise_for_status()

    dados = resposta.json()

    # Mapeia id da posição -> nome da posição
    mapa_posicoes = {
        str(id_pos): info["nome"]
        for id_pos, info in dados["posicoes"].items()
    }

    # Mapeia id do clube -> nome do clube
    mapa_clubes = {
        int(id_clube): info['nome']
        for id_clube, info in dados['clubes'].items()
    }

    jogadores = []

    # A chave correta é 'atletas'
    for atleta in dados["atletas"]:

        scout = atleta.get("scout", {})
        jogos = atleta.get("jogos_num", 0)

        # Ignora jogadores sem jogos
        if jogos == 0:
            continue

        jogador_dict = {
            "Atleta": atleta.get("apelido"),
            "Time": mapa_clubes.get(atleta.get('clube_id'), 'Desconhecido'),
            "Posição": mapa_posicoes.get(
                str(atleta.get("posicao_id")),
                "Desconhecida"
            ),
            "Jogos": jogos,
            "Gols": scout.get("G", 0),
            "Cartões Amarelos": scout.get("CA", 0),
            "Cartões Vermelhos": scout.get("CV", 0),
            "Desarmes": scout.get("DS", 0),
            "Passes Incompletos": scout.get("PI", 0)
        }

        jogadores.append(jogador_dict)

    return pd.DataFrame(jogadores)
    
    
    
    return df

#Executa a função
df_estatisticas = buscar_dados_brasileirao()

#Mostra as 5 primeiras linhas no console
print(df_estatisticas.head())

#Salva o resultado em um arquivo Excel e CSV
#df_estatisticas.to_excel('C:/Users/lecan/OneDrive/Área de Trabalho/estudos_python/jogador/dados_brasileirao.xlsx', index=False)
#df_estatisticas.to_csv('C:/Users/lecan/OneDrive/Área de Trabalho/estudos_python/jogador/dados_brasileirao.csv', index=False, encoding='utf-8')    
    

#criar coluna
df_estatisticas['gol_jogo'] = (
    df_estatisticas['Gols']
    .div(df_estatisticas['Jogos'].replace(0, np.nan))
    .fillna(0)
)
# Metricas descritivas
gol_time = (
    df_estatisticas.groupby('Time')['Gols']
    .sum()
    .reset_index(name='Total de Gols')
)
cartao_time_amarelo = df_estatisticas.groupby('Time')['Cartões Amarelos'].sum()  
cartao_time_vermelho = df_estatisticas.groupby('Time')['Cartões Vermelhos'].sum()
cartao_time = (cartao_time_amarelo + cartao_time_vermelho).reset_index(name='Total de Cartões')


# Os 10 principais artilheiros
top_10_gols = df_estatisticas.nlargest(10,'Gols')
top_10_amarelos = df_estatisticas.nlargest(10,'Cartões Amarelos')
top_10_vermelhos = df_estatisticas.nlargest(10,'Cartões Vermelhos')
top_10_gols_time = gol_time.nlargest(10, 'Total de Gols')
top_10_cartao = cartao_time.nlargest(10, 'Total de Cartões')
top_10_aproveitamento = df_estatisticas.nlargest(10, 'gol_jogo')

# No Plotly, para  o maior ficar no topo visualmento, precisamos inverter a ordem
top_10_gols = top_10_gols.sort_values(by='Gols', ascending=True)
top_10_amarelos = top_10_amarelos.sort_values(by='Cartões Amarelos', ascending=True)
top_10_vermelhos = top_10_vermelhos.sort_values(by='Cartões Vermelhos', ascending=True)
top_10_gols_time = top_10_gols_time.sort_values(by='Total de Gols', ascending=True)
top_10_cartao = top_10_cartao.sort_values(by = 'Total de Cartões', ascending= True)
top_10_aproveitamento = top_10_aproveitamento.sort_values(by='gol_jogo', ascending=True)
st.title("Estatísticas do Brasileirão")

# Criar o gráfico de barras horizontais
fig_artilheiros = px.bar(
    top_10_gols,
    x='Gols',
    y='Atleta',
    text='Atleta',
    orientation='h', #Define a barra horizontal
    title= '10 Maiores Goleadores do Brasileirão',
    hover_name= 'Atleta', #titulo da caixa de interação 
    hover_data= ['Atleta','Time', 'Jogos','Posição'] # Informação extras ao passar o mouse!   
)

fig_aproveitamento = px.bar(
    top_10_aproveitamento,
    x='gol_jogo',
    y='Atleta',
    text='Atleta',
    orientation='h', #Define a barra horizontal
    title= '10 Maiores Goleadores do Brasileirão',
    hover_name= 'Atleta', #titulo da caixa de interação 
    hover_data= ['Atleta', 'Jogos','Posição'] # Informação extras ao passar o mouse!   
)

fig_gols_time = px.bar(
    top_10_gols_time,
    x='Total de Gols',
    y='Time',
    text='Time',
    orientation='h', #Define a barra horizontal
    title= '10 Maiores Aproveitamentos em Gols ',
    hover_name= 'Time', #titulo da caixa de interação 
    hover_data= ['Time', 'Total de Gols'] # Informação extras ao passar o mouse!   
)

# Criar o gráfico de barras horizontais cartões amarelos
fig_amarelos = px.bar(
    top_10_amarelos,
    x='Cartões Amarelos',
    y='Atleta',
    text='Atleta',
    orientation='h', #Define a barra horizontal
    title= '10 Maiores cartões amarelos',
    hover_name= 'Atleta', #titulo da caixa de interação 
    hover_data= ['Atleta','Time', 'Jogos','Posição'] # Informação extras ao passar o mouse!   
)

# Criar o gráfico de barras horizontais cartões amarelos
fig_vermelhos = px.bar(
    top_10_vermelhos,
    x='Cartões Vermelhos',
    y='Atleta',
    text='Atleta',
    orientation='h', #Define a barra horizontal
    title= '10 Maiores cartões vermelhos',
    hover_name= 'Atleta', #titulo da caixa de interação 
    hover_data= ['Atleta','Time', 'Jogos','Posição'] # Informação extras ao passar o mouse!   
)

# Criar o gráfico de barras horizontais cartões por time
fig_cartao = px.bar(
    top_10_cartao,
    x='Total de Cartões',
    y='Time',
    text='Time',
    orientation='h', #Define a barra horizontal
    title= '10 Times com mais cartões',
   # hover_name= 'Atleta', #titulo da caixa de interação 
    #hover_data= ['Atleta','Time', 'Jogos','Posição'] # Informação extras ao passar o mouse!   
)

# Exibir o gráfico no navegador
pio.renderers.default = "browser"
#fig_artilheiros.show() 
#fig_amarelos.show()       
# Cria uma página com 2 gráficos lado a lado
fig = make_subplots(
    rows=2,
    cols=3,
    subplot_titles=(
        "10 Times com mais gols",
        "Top 10 Goleadores",
        "10+ Aproveitamentos de Gols",
        "Top 10 Amarelados",
        "Top 10 Vermelhos",
        "Top 10 Times com mais cartões",
        
    )
)

# Adiciona o primeiro gráfico
for trace in fig_gols_time.data:
    fig.add_trace(trace, row=1, col=1)
    
for trace in fig_aproveitamento.data:
    fig.add_trace(trace, row=1, col=3)

for trace in fig_artilheiros.data:
    fig.add_trace(trace, row=1, col=2)

# Adiciona o segundo gráfico
for trace in fig_amarelos.data:
    fig.add_trace(trace, row=2, col=1)

for trace in fig_vermelhos.data:
    fig.add_trace(trace, row=2, col=2)
    
for trace in fig_cartao.data:
    fig.add_trace(trace, row=2, col=3)


# Ajusta o layout
fig.update_layout(
    #title="Estatísticas do Brasileirão",
    height=1100,
    uniformtext_minsize=8,
    uniformtext_mode='show',
    #width=1400,
    showlegend=False
)

fig.update_traces(
    textposition='inside',
    insidetextanchor='middle',
    textfont=dict(color='white', size=11)
)

fig.update_yaxes(
    tickmode='array',
    tickvals=[],
    showticklabels=False,
    showline=False,
    showgrid=False,
    zeroline=False,
    title_text=None
)

# Exibe no Edge (ou navegador padrão)

st.plotly_chart(fig, width="stretch")
