# Projeto COVID-19
## Digital Innovation One

# Primeiro vamos importar algumas das bibliotecas necessárias para o projeto
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go 

# Importando informações do CSV
file_path = './Suporte/covid_19_data.csv'
df = pd.read_csv(file_path, parse_dates=['ObservationDate', 'Last Update'])
print(df)

# Conferir os tipos de cada coluna
print(df.dtypes)

# Formatando as informações importadas
#      - Nomes de colunas não devem ter letras maiúsculas e nem caracteres especiais. 
#        Vamos implementar uma função para fazer a limpeza dos nomes dessas colunas.

import re

def corrige_colunas(col_name):
    return re.sub(r"[/| ]", "", col_name).lower()

# testando a função corrige_colunas(col_name)
print( "\n" + corrige_colunas("Adge/P ou") + "\n") 

# Vamos corrigir todas as colunas do df
df.columns = [corrige_colunas(col) for col in df.columns]
print(df.dtypes)


