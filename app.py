from app import create_app

app = create_app()

#Executa a aplicação
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)