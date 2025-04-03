# configurações do nosso sistema!

caminho_banco = "C:/Users/noturno/Desktop/estenio/Sistema/consumo_alcool.db"
caminho_drinks_csv = "C:/Users/noturno/Desktop/estenio/Sistema/drinks.csv"

#Configurações do Flask
server_config = {
    "DEBUG": True,
    "PORT":5000,
    "HOST": "0.0.0.0" # pode ser localhost se desejar
}
# no debug podemos usar as seguintes configs:
# Debug como True ou False para ligar ou desligar o modo,
# ou como DEV e PROD
# DEV é a mesma coisa que Debug True, ou seja, ambiente de desenvolvimento
# PROD é a mesma coisa que False, ou seja, debug desligado e ambiente de produção

# Outras configurações gerais
semente_aleatoria = 42