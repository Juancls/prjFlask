# models.py
from database import db


class Cliente(db.Model):
    __tablename__ = 'cliente'

    idCliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(100), nullable=True)
    tipo = db.Column(db.String(100), nullable=True)

    agendamentos = db.relationship('Agendamento', backref='cliente', lazy=True)


class Funcionario(db.Model):
    __tablename__ = 'funcionario'

    idFuncionario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    especialidade = db.Column(db.String(100), nullable=True)
    disponibilidade = db.Column(db.String(100), nullable=True)

    agendamentos = db.relationship('Agendamento', backref='funcionario', lazy=True)


class Servico(db.Model):
    __tablename__ = 'servico'

    idServico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_servico = db.Column(db.String(100), nullable=True)
    descricao = db.Column(db.String(100), nullable=True)
    valor = db.Column(db.Numeric(10, 2), nullable=True)

    agendamentos = db.relationship('Agendamento', backref='servico', lazy=True)


class Agendamento(db.Model):
    __tablename__ = 'agendamento'

    idAgendamento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data_reservada = db.Column(db.Date, nullable=True)
    horario_reservado = db.Column(db.Time, nullable=True)
    status_da_reserva = db.Column(db.String(50), nullable=True)

    # Chaves Estrangeiras
    idCliente = db.Column(db.Integer, db.ForeignKey('cliente.idCliente'), nullable=True)
    idFuncionario = db.Column(db.Integer, db.ForeignKey('funcionario.idFuncionario'), nullable=True)
    idServico = db.Column(db.Integer, db.ForeignKey('servico.idServico'), nullable=True)