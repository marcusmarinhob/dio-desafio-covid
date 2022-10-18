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

# Visualizando
fig2 = px.line(brasil, x='observationdate', y='novoscasos', title='Novos casos confirmados no Brasil')
fig2.show()
