from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_swagger_ui import get_swaggerui_blueprint
import os

# Configurações do app e do banco de dados
app = Flask(__name__)
POSTGRES_URL = "ep-round-boat-a55avo7a.us-east-2.aws.neon.tech"
POSTGRES_USER = "MeninosDoCristo_owner"
POSTGRES_PW = "7ZaGK4Aorzlt"
POSTGRES_DB = "MeninosDoCristo"
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{POSTGRES_USER}:{POSTGRES_PW}@{POSTGRES_URL}/{POSTGRES_DB}?sslmode=require"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Swagger setup
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Cadastro de Atletas"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Definindo o modelo Atleta
class Atleta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    sub = db.Column(db.String(20), nullable=False)
    nome_responsavel = db.Column(db.String(100), nullable=False)
    posicao = db.Column(db.String(50), nullable=True)  # Posição em campo
    data_registro = db.Column(db.DateTime, server_default=db.func.now())

# Schema do Marshmallow para serialização/deserialização
class AtletaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Atleta
        fields = ('id', 'nome', 'idade', 'sub', 'nome_responsavel', 'posicao', 'data_registro')

atleta_schema = AtletaSchema()
atletas_schema = AtletaSchema(many=True)

# Rota para criar um novo atleta
@app.route('/atletas', methods=['POST'])
def add_atleta():
    nome = request.json['nome']
    idade = request.json['idade']
    sub = request.json['sub']
    nome_responsavel = request.json['nome_responsavel']
    posicao = request.json.get('posicao', None)

    novo_atleta = Atleta(nome=nome, idade=idade, sub=sub, nome_responsavel=nome_responsavel, posicao=posicao)
    db.session.add(novo_atleta)
    db.session.commit()

    return atleta_schema.jsonify(novo_atleta)

# Rota para obter todos os atletas
@app.route('/atletas', methods=['GET'])
def get_atletas():
    todos_atletas = Atleta.query.all()
    result = atletas_schema.dump(todos_atletas)
    return jsonify(result)

# Rota para obter um atleta específico por ID
@app.route('/atletas/<id>', methods=['GET'])
def get_atleta(id):
    atleta = Atleta.query.get(id)
    if not atleta:
        return jsonify({'message': 'Atleta não encontrado'}), 404
    return atleta_schema.jsonify(atleta)

# Rota para atualizar dados de um atleta
@app.route('/atletas/<id>', methods=['PUT'])
def update_atleta(id):
    atleta = Atleta.query.get(id)
    if not atleta:
        return jsonify({'message': 'Atleta não encontrado'}), 404

    atleta.nome = request.json['nome']
    atleta.idade = request.json['idade']
    atleta.sub = request.json['sub']
    atleta.nome_responsavel = request.json['nome_responsavel']
    atleta.posicao = request.json.get('posicao', atleta.posicao)

    db.session.commit()
    return atleta_schema.jsonify(atleta)

# Rota para deletar um atleta
@app.route('/atletas/<id>', methods=['DELETE'])
def delete_atleta(id):
    atleta = Atleta.query.get(id)
    if not atleta:
        return jsonify({'message': 'Atleta não encontrado'}), 404

    db.session.delete(atleta)
    db.session.commit()
    return jsonify({'message': 'Atleta deletado com sucesso'})

# Rota para a página inicial que exibe todos os atletas
@app.route('/')
def index():
    atletas = Atleta.query.all()
    return render_template('index.html', atletas=atletas)

# Rota para o formulário de adicionar atleta
@app.route('/add', methods=['GET', 'POST'])
def add_atleta_form():
    if request.method == 'POST':
        nome = request.form['nome']
        idade = request.form['idade']
        sub = request.form['sub']
        nome_responsavel = request.form['nome_responsavel']
        posicao = request.form.get('posicao', None)

        novo_atleta = Atleta(nome=nome, idade=idade, sub=sub,
                             nome_responsavel=nome_responsavel, posicao=posicao)
        db.session.add(novo_atleta)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_atleta.html')

# Rota para visualizar detalhes de um atleta
@app.route('/atleta/<int:id>')
def atleta_detail(id):
    atleta = Atleta.query.get_or_404(id)
    return render_template('atleta_detail.html', atleta=atleta)

# Inicialização do banco de dados e execução da aplicação
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
