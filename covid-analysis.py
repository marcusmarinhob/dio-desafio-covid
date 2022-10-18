# Projeto COVID-19
## Digital Innovation One

# Primeiro vamos importar algumas das bibliotecas necessárias para o projeto
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go 

file_path = './Suporte/covid_19_data.csv'
df = pd.read_csv(file_path, parse_dates=['ObservationDate', 'Last Update'])
print(df)