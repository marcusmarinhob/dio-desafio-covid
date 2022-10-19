#####################################################################################################
#                                     Projeto COVID-19                                              #
#                                  Digital Innovation One                                           #
#####################################################################################################

# Primeiro vamos importar algumas das bibliotecas necessárias para o projeto ########################
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go 

# print(pio.renderers.default)

# Importando informações do CSV  ####################################################################
file_path = './Suporte/covid_19_data.csv'
df = pd.read_csv(file_path, parse_dates=['ObservationDate', 'Last Update'])
print(df)

# Conferir os tipos de cada coluna ##################################################################
print(df.dtypes)

# Formatando as informações importadas ##############################################################
#   Nomes de colunas não devem ter letras maiúsculas e nem caracteres especiais. 
#   Vamos implementar uma função para fazer a limpeza dos nomes dessas colunas.

import re

def corrige_colunas(col_name):
    return re.sub(r"[/| ]", "", col_name).lower()

# testando a função corrige_colunas(col_name)
print( "\n" + corrige_colunas("Adge/P ou") + "\n") 

# Vamos corrigir todas as colunas do df 
df.columns = [corrige_colunas(col) for col in df.columns]
print(df.dtypes)

# Pegando a lista dos países na base de dados ######################################################
print( df.countryregion.unique() )

# Vamos selecionar apenas os dados do Brasil para investigar #######################################
print( df.loc[df.countryregion == 'Brazil'] )

brasil = df.loc[
    (df.countryregion == 'Brazil') &
    (df.confirmed > 0)
]
print(brasil)

# Casos Confirmados ################################################################################

# Gráfico da evolução de casos confirmados
fig = px.line(brasil, 'observationdate', 'confirmed', title='Casos confirmados no Brasil')
fig.show()


# Novos casos por dia #############################################################################

#  Técnica de programação funcional
brasil['novoscasos'] = list( map(
    lambda x: 0 if (x==0) else brasil['confirmed'].iloc[x] - brasil['confirmed'].iloc[x-1], np.arange(brasil.shape[0])
) )

print(brasil)

# Visualizando novos casos
fig2 = px.line(brasil, x='observationdate', y='novoscasos', title='Novos casos por dia no Brasil')
fig2.show()

# Visualizando mortes
fig3 = go.Figure()

fig3.add_trace(
    go.Scatter(x=brasil.observationdate, y=brasil.deaths, name="Mortes", mode="lines+markers", line={'color':'red'})
)

fig3.update_layout(title='Mortes por COVID-19 no Brasil')
fig3.show()

# Taxa de crescimento ######################################################################################################
# taxa_crescimento = (presente/passado)**(1/n)-1

def taxa_crescimento(data, variable, data_inicio=None, data_fim=None):
    # Se data inicio for None, define como a primeira data disponível
    if data_inicio == None:
        data_inicio = data.observationdate.loc[data[variable] > 0].min()
    else:
        data_inicio = pd.to_datetime(data_inicio)

    if data_fim == None:
        data_fim = data.observationdate.iloc[-1]
    else:
        data_fim = pd.to_datetime(data_fim)

    # Define os valores do presente e passado
    passado = data.loc[data.observationdate == data_inicio, variable].values[0]
    presente = data.loc[data.observationdate == data_fim, variable].values[0]

    # Define o número de pontos no tempo que vamos avaliar
    n = (data_fim - data_inicio).days

    # Calcular a taxa
    taxa = (presente/passado)**(1/n) - 1

    return taxa*100

# Taxa de crescimento médio do COVID no Brasil em todo o período
print(taxa_crescimento(brasil, 'confirmed'))


def taxa_crescimento_diaria(data, variable, data_inicio=None):
    # Se data inicio for None, define como a primeira data disponível
    if data_inicio == None:
        data_inicio = data.observationdate.loc[data[variable] > 0].min()
    else:
        data_inicio = pd.to_datetime(data_inicio)

    data_fim = data.observationdate.max()

    # Define o número de pontos no tempo que vamos avaliar
    n = (data_fim - data_inicio).days

    # Taxa calculada de um dia para o outro
    taxas = list( map(
        lambda x: (data[variable].iloc[x] - data[variable].iloc[x-1]) / data[variable].iloc[x-1], range(1, n+1)
    ))

    return np.array(taxas) * 100

tx_dia = taxa_crescimento_diaria(brasil, 'confirmed')

primeiro_dia = brasil.observationdate.loc[brasil.confirmed >0].min()

fig4 = px.line(x=pd.date_range(primeiro_dia, brasil.observationdate.max())[1:], y=tx_dia, title="Taxa de crescimento de casos confirmados no Brasil")
fig4.show()
