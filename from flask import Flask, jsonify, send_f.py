from flask import Flask, jsonify, send_file
import pandas as pd
import io
import base64
import matplotlib.pyplot

app = Flask(__name__)

@app.route('/')
def pagina_inicial():
     return "Hello world"

if __name__ == '__main__':
    app.run(debug=True)