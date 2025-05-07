from flask import Flask, render_template, request
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

import matplotlib.ticker as ticker
import pandas as pd
import tradingeconomics as te
import os

app = Flask(__name__)
te.login('guest:guest')  # modo invitado

# Lista permitida de países
PAISES_VALIDOS = ['Mexico',  'Sweden']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pais1 = request.form['pais1']
        pais2 = request.form['pais2']

        if pais1 not in PAISES_VALIDOS or pais2 not in PAISES_VALIDOS:
            return "País no válido"

        indicador=["gdp","population"]
        poblacion1 = te.getHistoricalData(country=[pais1], indicator=["gdp","population"], initDate='2015-01-01')
        poblacion2 = te.getHistoricalData(country=[pais2], indicator=["gdp","population"], initDate='2015-01-01')

        # Convertir a DataFrames
        df_pob1 = pd.DataFrame(poblacion1)
        df_pob2 = pd.DataFrame(poblacion2)

        # Filtrar por categoría 'Population' para obtener una poblacion, datos restringidos en guest
        pob1 = df_pob1[df_pob1['Category'] == 'Population']
        pob2 = df_pob2[df_pob2['Category'] == 'Population']
        pob1=pob1['Value'][0]
        pob2=pob2['Value'][0]
        # Indicador
        indicador = "GDP"
        # Obtener datos históricos desde 2015
        data1 = te.getHistoricalData(country=[pais1], indicator=[indicador], initDate='2015-01-01')
        data2 = te.getHistoricalData(country=[pais2], indicator=[indicador], initDate='2015-01-01')

        # Convertir a DataFrames
        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)

        df1['DateTime'] = pd.to_datetime(df1['DateTime'])
        df2['DateTime'] = pd.to_datetime(df2['DateTime'])

        df1.sort_values('DateTime', inplace=True)
        df2.sort_values('DateTime', inplace=True)

        valores1 = (df1['Value'] / pob1) * 1000
        valores2 = (df2['Value'] / pob2) * 1000

        # Crear gráfico
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df1['DateTime'], valores1, label=pais1, linewidth=2.5, marker='o')
        ax.plot(df2['DateTime'], valores2, label=pais2, linewidth=2.5, marker='s')
        ax.set_title(f"PIB per cápita ({pais1} vs {pais2})", fontsize=14)
        ax.set_xlabel("Año")
        ax.set_ylabel("PIB per cápita (por mil)")
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend()
        plt.tight_layout()

        # Guardar imagen
        ruta = os.path.join('static', 'grafico.png')
        plt.savefig(ruta, dpi=300)
        plt.close()

        # Mostrar el gráfico en el mismo index.html
        return render_template('index.html', paises=PAISES_VALIDOS, grafico_generado=True, pais1=pais1, pais2=pais2)

    return render_template('index.html', paises=PAISES_VALIDOS, grafico_generado=False)

if __name__ == '__main__':
    app.run(debug=True)
