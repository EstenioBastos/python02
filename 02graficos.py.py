from flask import Flask, jsonify, send_file
import pandas as pd
import io
import base64
import matplotlib.pyplot as plt





app = Flask(__name__)

#carregar os dados do excel
arquivo = 'C:/Users/noturno/Desktop/estenio/01_base_vendas.xlsx'
df1 = pd.read_excel(arquivo, sheet_name='Relatório de Vendas')    
df2 = pd.read_excel(arquivo, sheet_name='Relatório de Vendas1') 

# rota da pagina inicial ex: http://127.0.0.1:5000/
df_consolidado = pd.concat([df1,df2],ignore_index=True)



@app.route('/')
def pagina_inicial():
     conteudo = '''
     <style>
          a {
               display: inline-block;
               padding: 10px 20px;
               margin: 5px 0;
               text-decoration: none;
               color: white;
               border-radius: 5px;
               text-align: center;
               background-color: #4CAF50;
               transition: 0.3s;
               min-width: 200px;
               min-height:20px;
               }
          </style>
          <h1>API de Analise de Dados de Vendas</h1>
          <h2>Use as rotas para obter analises:</h2>
          <a href=''> -- Pagina Inicial -- </a><br/>
          <a href='/clientes_por_cidade'> -- Clientes por Cidade -- </a><br/>
          <a href='/vendas_por_plano'> -- Vendas por Plano -- </a><br/>
          <a href='/top_cidades'> -- Top 3 Cidades -- </a><br/>
          <a href='/download/excel'> -- Download em Excel -- </a><br/>
          <a href='/download/csv'> -- Download em CSV -- </a><br/>
          <a href=''> -- Grafico de Pizza -- </a><br/>
          <a href=''> -- Grafico de Barras -- </a><br/>
          <a href='mailto:esteniob@gmail.com'> Email de contato </a>

           

          '''
     return conteudo

@app.route('/clientes_por_cidade')
def clientes_por_cidade():
     clientes_por_cidade = df_consolidado.groupby('Cidade')['Cliente'].nunique().sort_values(ascending=False)
     return jsonify(clientes_por_cidade.to_dict())

@app.route('/vendas_por_plano')
def vendas_por_plano():
     vendas_por_plano = df_consolidado['Plano Vendido'].value_counts()
     return jsonify(vendas_por_plano.to_dict())


@app.route('/top_cidades')
def top_cidades():
     clientes_por_cidade = df_consolidado.groupby('Cidade')['Cliente'].nunique().sort_values(ascending=False)
     top_cidades = clientes_por_cidade.head(3)
     return jsonify(top_cidades.to_dict())

@app.route('/download/csv')
def download_csv():
     caminho_csv = 'C:/Users/noturno/Desktop/estenio/arquivo_csv.csv'
     df_consolidado.to_csv(caminho_csv, index=False)
     return jsonify({"message":"download do arquivo CSV disponivel!","file_path":caminho_csv,"Autor":"Estenio"})


@app.route('/download/excel')
def download_excel():
     caminho_excel = 'C:/Users/noturno/Desktop/estenio/arquivo_excel.xlsx'
     df_consolidado.to_excel(caminho_excel, index=False)
     return f"<a href='{caminho_excel}'> Inicar Download <a/>"


#grafico de barras! amanhã tem pizza!
@app.roude('/grafico_barras')
def grafico_barras():
     vendas_por_plano = df_consolidado['Plano Vendido'].value_counts()

     #criar o grafico de barras
     fig, ax = plt.subplots()
     vendas_por_plano.plot(kind='bar', ax=ax , color=['#66b3ff','#99ff99'])
     ax.set_title('Grafico de vendas por plano')
     ax.set_xlabel('Plano')
     ax.set_ylabel('Numero de Vendas')


     #salvar o grafico em um objeto de memoria
     img = io.BytesIO()
     plt.savefig(img, format='png')
     img.seek(0)
     
     img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

     #retornando a imagem como resposta
     return send_file(img, mimetype='imagem/png')



if __name__ == '__main__':
    app.run(debug=True)