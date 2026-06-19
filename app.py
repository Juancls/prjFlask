# app.py ou main.py
import os
from flask import Flask
from flask import request, jsonify
from datetime import datetime
from flask_cors import CORS
import models
from database import db

app = Flask(__name__)
CORS(app)

# Define o caminho absoluto para o arquivo do banco de dados
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'vivi_cleaning.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# cria a tabela com os serviços caso ela inicio vazia
with app.app_context():
    db.create_all()

    # verifica se a tabela de serviços já tem registros para não duplicar
    if models.Servico.query.first() is None:
        servicos_iniciais = [
            models.Servico(idServico=1, tipo_servico="Lavanderia", descricao="Lavar Roupa", valor=50.00),
            models.Servico(idServico=2, tipo_servico="Lavanderia", descricao="Passar Roupa", valor=60.00),
            models.Servico(idServico=3, tipo_servico="Cozinha", descricao="Lavar Louça", valor=30.00),
            models.Servico(idServico=4, tipo_servico="Limpeza", descricao="Limpeza Geral (Fácil/Manutenção)", valor=150.00),
            models.Servico(idServico=5, tipo_servico="Limpeza", descricao="Limpeza Pesada (Festa/Pós-obra)", valor=300.00),
            models.Servico(idServico=6, tipo_servico="Organização", descricao="Organização de Armários e Closets", valor=120.00),
            models.Servico(idServico=7, tipo_servico="Limpeza", descricao="Limpeza de Vidros e Janelas", valor=80.00),
            models.Servico(idServico=8, tipo_servico="Cozinha", descricao="Limpeza Interna de Geladeira e Forno", valor=70.00),
            models.Servico(idServico=9, tipo_servico="Cozinha", descricao="Preparo de Refeições (Cozinhar)", valor=100.00),
            models.Servico(idServico=10, tipo_servico="Quarto", descricao="Troca de Roupas de Cama e Banho", valor=40.00),
            models.Servico(idServico=11, tipo_servico="Limpeza", descricao="Limpeza de Área Externa/Quintal", valor=130.00),
            models.Servico(idServico=12, tipo_servico="Jardinagem", descricao="Cuidado e Rega de Plantas", valor=35.00),
        ]

        try:
            db.session.bulk_save_objects(servicos_iniciais)
            db.session.commit()
            print("Serviços padrões inseridos com sucesso no SQLite!")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao inserir serviços iniciais: {e}")


@app.route('/servicos', methods=['GET'])
def listar_servicos():
    # Busca todos os serviços ordenados pelo ID
    servicos = models.Servico.query.order_by(models.Servico.idServico).all()

    # Cria a lista formatada em JSON
    lista_servicos = []
    for s in servicos:
        lista_servicos.append({
            "idServico": s.idServico,
            "tipo_servico": s.tipo_servico,
            "descricao": s.descricao,
            "valor": float(s.valor) if s.valor else 0.0  # Converte Decimal para float para não dar erro no JSON
        })

    return jsonify(lista_servicos), 200


@app.route('/cadastrar', methods=['POST'])
def cadastrar_cliente():
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')
    cpf = dados.get('cpf')
    telefone = dados.get('telefone')

    # Validação básica de campos obrigatórios do banco
    if not all([nome, email, senha, cpf, telefone]):
        return jsonify({"mensagem": "Todos os campos (Nome, E-mail, Senha, CPF e Telefone) são obrigatórios!"}), 400

    # Verifica se o e-mail já existe no banco
    email_existente = models.Cliente.query.filter_by(email=email).first()
    if email_existente:
        return jsonify({"mensagem": "Este e-mail já está cadastrado!"}), 400

    # Cria o novo cliente (endereco inicia vazio/None conforme o seu SQL)
    novo_cliente = models.Cliente(
        nome=nome,
        email=email,
        senha=senha,
        cpf=cpf,
        telefone=telefone,
        endereco=None
    )

    try:
        db.session.add(novo_cliente)
        db.session.commit()
        return jsonify({"mensagem": "Conta criada com sucesso! Faça seu login."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"mensagem": f"Erro ao criar conta: {str(e)}"}), 500

@app.route('/login', methods=['POST'])
def login_cliente():
    dados = request.get_json()
    email = dados.get('email')
    senha = dados.get('senha')

    if not email or not senha:
        return jsonify({"erro": "E-mail e senha são obrigatórios."}), 400

    cliente = models.Cliente.query.filter_by(email=email).first()

    if not cliente or cliente.senha != senha:
        # Retorna a estrutura vazia para o front cair no bloco de erro se necessário
        return jsonify({"userInfo": None, "mensagem": "E-mail ou senha incorretos."}), 401

    # Retorna exatamente o formato que o seu Front-end estruturou
    return jsonify({
        "mensagem": "Login efetuado com sucesso!",
        "userInfo": {
            "id": cliente.idCliente,  # Guardamos o ID aqui para usar depois no agendamento
            "user": cliente.nome,  # dados.userInfo.user
            "Email": cliente.email  # dados.userInfo.Email
        }
    }), 200


@app.route('/clientes/<int:id_cliente>', methods=['GET'])
def buscar_cliente_por_id(id_cliente):
    # Busca o cliente no banco SQLite pelo ID
    cliente = models.Cliente.query.get(id_cliente)

    if not cliente:
        return jsonify({"erro": "Cliente não encontrado"}), 404

    # Devolve o JSON limpo que o React está esperando
    return jsonify({
        "cpf": cliente.cpf if hasattr(cliente, 'cpf') else "",
        "telefone": cliente.telefone if cliente.telefone else "",
        "endereco": cliente.endereco if cliente.endereco else ""
    }), 200


@app.route('/agendamentos', methods=['POST'])
def criar_agendamento():
    dados = request.get_json()

    # 1. Captura os dados vindos do Front-end
    data_str = dados.get('data_reservada')  # Recebe 'YYYY-MM-DD'
    horario_str = dados.get('horario_reservado')  # Recebe 'HH:MM'
    endereco = dados.get('endereco')
    lista_servicos = dados.get('servicos')  # Lista de IDs ex: [1, 4, 7]
    id_cliente = dados.get('idCliente', 1)  # Padrão 1 caso não venha logado

    # Validação básica
    if not data_str or not horario_str or not lista_servicos:
        return jsonify({"erro": "Data, horário e pelo menos um serviço são obrigatórios."}), 400

    try:
        # 2. Converte as strings do React para formatos que o SQLAlchemy entende
        data_objeto = datetime.strptime(data_str, '%Y-%m-%d').date()
        horario_objeto = datetime.strptime(horario_str, '%H:%M').time()

        # 3. Opcional: Se quiser atualizar o endereço no cadastro do Cliente
        cliente = models.Cliente.query.get(id_cliente)
        if cliente:
            cliente.endereco = endereco
            db.session.add(cliente)

        # 4. Cria um registro na tabela agendamento para CADA serviço selecionado
        for id_servico in lista_servicos:
            novo_agendamento = models.Agendamento(
                data_reservada=data_objeto,
                horario_reservado=horario_objeto,
                status_da_reserva="Pendente",
                idCliente=id_cliente,
                idServico=id_servico,
                idFuncionario=None  # Fica nulo até a Vivi Cleaning atribuir um funcionário no dashboard
            )
            db.session.add(novo_agendamento)

        # Salva todas as inserções de uma vez só no SQLite
        db.session.commit()
        return jsonify({"mensagem": "Agendamento(s) criado(s) com sucesso!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": f"Erro interno ao salvar agendamento: {str(e)}"}), 500


@app.route('/clientes/<int:id_cliente>/agendamentos', methods=['GET'])
def obter_agendamentos_cliente(id_cliente):
    try:
        # Busca todos os agendamentos do cliente específico no SQLite
        agendamentos = models.Agendamento.query.filter_by(idCliente=id_cliente).all()

        lista_agendamentos = []
        for a in agendamentos:
            lista_agendamentos.append({
                "idAgendamento": a.idAgendamento,
                # Converte os objetos de data/hora do SQLite para texto legível
                "data": a.data_reservada.strftime('%d/%m/%Y') if a.data_reservada else "Sem data",
                "horario": a.horario_reservado.strftime('%H:%M') if a.horario_reservado else "Sem hora",
                "status": a.status_da_reserva if a.status_da_reserva else "Pendente",
                # Pega a descrição direto do relacionamento com a tabela servico
                "servico": a.servico.descricao if a.servico else "Serviço Geral",
                "valor": float(a.servico.valor) if a.servico and a.servico.valor else 0.0
            })

        return jsonify(lista_agendamentos), 200

    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar histórico: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)