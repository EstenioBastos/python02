from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import sqlite3
import os
import plotly.graph_objs as go
from dash import Dash, html, dcc
import dash
import numpy as np

import config

app = Flask(__name__)
DB_PATH = config.DB_PATH

# Função para inicializar o banco
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inadimplencia (
             mes TEXT PRIMARY KEY,
             inadiplencia REAL                    
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS selic (
            mes TEXT PRIMARY KEY,         
            selic_diaria REAL         
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    return render_template_string('''
        <h1> Upload de dados Econômicos </h1>
        <form action="/upload" method="post" enctype="multipart/Form-data">
            <label> Arquivo de inadimplencia (CSV)  :</label>
            <input type="file" name="campo_inadimplencia" required><br><br>
                                  
            <label> Arquivo da Taxa SELIC (CSV):  </label>
            <input type="file" name="campo_selic" required><br><br>
            
            <input type="submit" value="Fazer Upload">                     
        <form>
        <br><br>
        <a href="/consultar"> Consultar dados Armazenados </a><br>
        <a href="/graficos"> Visualizar Graficos </a><br>
        <a href="/editar_inadimplencia"> Editar Inadimplencias </a><br>
        <a href="/correlacao"> Analisar Correlação </a><br>

''')

@app.route('/upload', methods=["POST"])
def upload_dados():
    inad_file = request.files.get('campo_inadimplencia')
    selic_file = request.files.get('campo_selic')

# Verifica se os arquivos foram enviados
    if not inad_file or not selic_file:
        return jsonify({"Erro":"Ambos os arquivos devem ser enviados"})
    
    inad_df = pd.read_csv(inad_file, sep=';', names=['data','inadimplencia'], header=0)
    selic_df = pd.read_csv(selic_file, sep=';', names=['data', 'selic_diaria'], header=0)

    inad_df['data'] = pd.to_datetime(inad_df['data'], format="%d/%m/%Y")
    selic_df['data'] = pd.to_datetime(selic_df['data'], format="%d/%m/%Y")


    inad_df['mes'] = inad_df['data'].dt.to_period('M').astype(str)
    selic_df['mes'] = selic_df['data'].dt.to_period('M').astype(str)

    inad_mensal = inad_df[["mes", "inadimplencia"]].drop_duplicates()
    selic_mensal = selic_df.groupby('mes')['selic_diaria'].mean().reset_index()

    with sqlite3.connect(DB_PATH) as conn: 
        inad_mensal.to_sql('inadimplencia', conn, if_exists='replace', index=False)
        selic_mensal.to_sql('selic', conn, if_exists='replace', index=False)

    return jsonify({"mensagem":"Dados armazenados com sucesso!"})

@app.route('/consultar', methods=['GET', 'POST'])
def consultar_dados():
    # Resultado se essa pagina for carregada recebendo o POST
    if request.method == 'POST':
        tabela = request.form.get('campo_tabela')
        if tabela not in ['inadimplencia','selic']:
            return jsonify({"erro":"Tabela Inválida."}),400
        
        with sqlite3.connect(DB_PATH) as conn: 
            df = pd.read_sql_query(f"SELECT * FROM {tabela}", conn)
        return df.to_html(index=False)

    # Resultado da pagina sendo carregada a primeira vez, sem receber o post
    return render_template_string('''
        <h1> Consulta de Tabela </h1>
        <form method= "post">
            <label for="tabela"> Escola a tabela: </label>
            <select name="campo_tabela">
                <option value="inadimplencia"> Inadimplência </option>
                <option value="selic"> Selic </option>
            </select>
            <input type ="submit" value="Consultar">                   
        </form>
        <br><a href="/"> Voltar </a>

    ''')

@app.route('/graficos')
def graficos():
    with sqlite3.connect(DB_PATH) as conn:
        inad_df = pd.read_sql_query("SELECT * FROM inadimplencia", conn)
        selic_df = pd.read_sql_query("SELECT * FROM selic", conn)
    
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=inad_df['mes'], y=inad_df['inadimplencia'], mode='lines+markers', name='Inadimplência'))
    fig1.update_layout(title="Evolução da Inadimplência", xaxis_title='Mês',yaxis_title='%', template='plotly_dark')

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=selic_df['mes'], y=selic_df['selic_diaria'], mode='lines+markers', name='SELIC'))
    fig2.update_layout(title="Média Mensal da SELIC", xaxis_title='Mês',yaxis_title='Taxa', template='plotly_dark')

    graph_html1 = fig1.to_html(full_html=False, include_plotlyjs='cdn')
    graph_html2 = fig2.to_html(full_html=False, include_plotlyjs=False)
    
    return render_template_string('''
          <html>
            <head>
                <title>Gráficos Econômicos</title>
                <style>
                    .container{
                        display:flex;
                        justify-content:space-around;
                    }
                    .graph{
                        width: 48%;     
                    }
                </style>
            </head>
            <body>
                <h1 style="text-align: center"> Gráficos Econômicos </h1>
                <div class="container">
                    <div class="graph">  {{ grafico1|safe }} </div>  
                    <div class="graph">  {{ grafico2|safe }} </div> 
                </div>
                <br><br>
                <div style="text-align: center"><a href="/"Voltar</a></div>
            </body>
        </html> 
        
''', grafico1=graph_html1, grafico2=graph_html2)  

@app.route('/editar_inadimplencia', methods=['GET','POST'])
def editar_inadimplencia():
    if request.method == "POST":
        mes = request.form.get('campo_mes')
        novo_valor = request.form.get('campo_valor')
        try:
            novo_valor = float(novo_valor)
        except:
            return jsonify({'mensagem':'Valor inválido.'})
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE inadimplencia SET inadimplencia = ? WHERE mes=?", (novo_valor, mes))
            conn.commit()
        return jsonify({f"mensagem": "Valor atualizado para o mês {mes}"})

    return render_template_string('''
    <h1>Editar Inadimplencia </h1>
        <form method='post'>
            <label for='campo_mes'> Mês (AAAA-MM): </label>
            <input type='text' name='campo_mes' required><br>
                                  
            <label for='campo_valor'> Novo valor de inadimplência </label>                     
            <input type='text' name='campo_valor' required><br>
            
            <input type='submit' value='Atualizar'>
                                                          
        </form>
        <br>
        <a href='/'>Voltar<a>
''')

@app.route('/correlacao')
def correlacao():
    with sqlite3.connect(DB_PATH) as conn:
        inad_df = pd.read_sql_query("SELECT * FROM inadimplencia", conn)
        selic_df = pd.read_sql_query("SELECT * FROM selic", conn)
    merged = pd.merge(inad_df,selic_df, on='mes')
    correl = merged['inadimplencia'].corr(merged['selic_diaria'])

    # Regressão Linear
    y = merged['inadimplencia']
    x = merged['selic_diaria']
    m, b = np.polyfit(x, y, 1) # m: coeficiente angular e b: coeficiente linear

    
    fig = go.Figure()
    # Etapa A
    fig.add_trace(go.Scatter(
        x = x,
        y = y,
        mode = 'markers',
        name = 'Inadimplência x SELIC',
        marker = dict(
            color = 'rgba(0, 123, 2, 0.8)',
            size = 12, 
            line = dict(width=2, color='white'),
            symbol = 'circle'
        ), 
        hovertemplate = 'SELIC: %{x:.2f}%<br>Inadimplência:%{y:.2f}%<extra></extra>'
    ))
    # Etapa B
    fig.add_trace(go.Scatter(
        x = x,
        y = m * y + b,
        mode='lines', 
        name='Linhas de Tendência',
        line=dict(
            color = 'rgba(220,3,69,1)',
            width = 4, 
            dash = 'dot'
        )
    ))
    fig.update_layout(
        title = {
            'text':',br>Correlação entre SELIC e Inadimplência</br><br><span style="font-size:16px"> Coeficiente de Correlação: {correl:2.f} </span>',
            'y':0.95,
            'x':0.5,
            'xanchor':'center',
            'yanchor':'top'
        },
        xaxis_title = dict(
            text = 'SELIC Média Mensal (%)',
            font=dict(size = 18, family = 'Arial', color = 'gray')
        ),
        yaxis_title = dict(
            text = 'Inadimplência (%)',
            font=dict(size = 18, family = 'Arial', color = 'gray')
        ),
        xaxis = dict(
            tickfont = dict(size = 14, family = 'Arial', color = 'black'),
            gridcolor = 'lightgray'
        ),
        yaxis = dict(
            tickfont = dict(size = 14, family = 'Arial', color = 'black'),
            gridcolor = 'lightgray'
        ),
        plot_bgcolor = '#f8f9fa',
        paper_bgcolor = 'white',
        font = dict(size = 14, family = 'Arial', color = 'black'),
        legend = dict(
            orientation ='h',
            yanchor = 'bottom',
            y=1.05,
            xanchor = 'bottom',
            x=0.5,
            bgcolor='rgba(0,0,0,0)',
            borderwidth = 0
        ),
        margin = dict(l=60, r=60, t=120, b=60)
    )

    graph_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return render_template_string('''
        <html>
            <head>
                <title> Correlação SELIC vs Inadimplência </title>
                <style>
                    body{
                        font-family: Arial, sans-serif;
                        background-color: #ffffff;
                        color: #333;
                        font-weight:bold;          
                    }
                    .container{
                        width: 90%;
                        margin:auto;
                        text-align:center;    
                    }
                    h1{
                        margin-top:40px;            
                    }
                    a{
                        text-decoration:nome;
                        color:00ff00;           
                    }
                    a:hover{
                        text-decoration:underline;            
                    }
                </style>
            </head>
            <body>
                <div class= 'container'>
                    <h1> Correlação SELIC vs Inadimplência </h1>
                    <div>{{ grafico|safe}}</div>
                    <br><a href='/'>Voltar</a>
                </div>
            </body>                 
        </html>

    ''', grafico=graph_html)

# iniciar o servidor local flask da aplicação
if __name__ == '__main__':
    init_db()
    app.run(debug=True)


