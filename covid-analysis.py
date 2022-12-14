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


# Predições #####################################################################################################################################
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pylab as plt

confirmados = brasil.confirmed
confirmados.index = brasil.observationdate

print(confirmados)

res = seasonal_decompose(confirmados)

fig5, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(10, 8))
ax1.plot(res.observed)
ax2.plot(res.trend)
ax3.plot(res.seasonal)
ax4.plot(confirmados.index, res.resid)
ax4.axhline(0, linestyle='dashed', c='black')
plt.show()


# ARIMA ########################################################################################################
from pmdarima.arima import auto_arima

modelo = auto_arima(confirmados)

fig6 = go.Figure( go.Scatter(
    x= confirmados.index, y= confirmados, name= 'Observados'
))

fig6.add_trace(go.Scatter(
    x= confirmados.index, y= modelo.predict_in_sample(), name= 'Preditos'
))

fig6.add_trace(go.Scatter(
    x= pd.date_range('2020-05-20', '2020-06-20'), y= modelo.predict(31), name= 'Forecast'
))

fig6.update_layout(title='Previsão de casos confirmados no Brasil para os próximos 30 dias')
fig6.show()

# MODELO DE CRESCIMENTO ##########################################################################################
from fbprophet import Prophet

# Preprocessamentos
train = confirmados.reset_index()[:-5]
test = confirmados.reset_index()[-5:]

# Renomeando colunas
train.rename(columns={'observationdate':'ds', 'confirmed': 'y'}, inplace=True)
test.rename(columns={'observationdate':'ds', 'confirmed': 'y'}, inplace=True)

# Definir o modelo de crescimento
profeta = Prophet(growth='logistic', changepoints['2020-03-21', '2020-03-30', '2020-04-25','2020-05-03', '2020-05-10'])

# pop = 211463256
pop = 1000000
train['cap'] = pop

# Treina o modelo
profeta.fit(train)

# Construir previsões para o futuro
future_dates = profeta.make_future_dataframe(periods=200)
forecast = profeta.prefict(future_dates)


# Mostrar gráfico

fig7 = go.Figure()

fig7.add_trace(go.Scatter(x=forecast.ds, y= forecast.yhat, name='Predição'))
fig7.add_trace(go.Scatter(x=test.index, y=test, name='Observados - Teste'))
fig7.add_trace(go.Scatter(x=train.ds, y=train.y, name='Observados - Treino'))
fig7.update_layout(title='Predições de casos confirmados no Brasil')
fig7.show()


