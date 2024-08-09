#configuração pasica até a linha 13

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd

app = Flask(__name__)
app.config["SECRET_KEY"] = "sua_chave_secreta"  # Substitua por uma chave secreta segura
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///livros.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

#definir modelo de dados ---> criar a classe livros até a linha 35

class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    editora = db.Column(db.String(200), default="Sem Editora")
    ativo = db.Column(db.Boolean, default=False)

    def __init__(self, titulo, autor, categoria, ano, editora="Sem Editora", ativo=False):
        self.titulo = titulo
        self.autor = autor
        self.categoria = categoria
        self.ano = ano
        self.editora = editora
        self.ativo = ativo

    def __repr__(self):
        return f"<Livro {self.titulo}>"
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    #criar tabela e inserir dados iniciais 

with app.app_context():
    db.create_all()

    # Ler o arquivo CSV para um DataFrame
    df = pd.read_csv("tabela - livros.csv")

    # Adicionar cada livro à base de dados, se ainda não estiverem presentes até a linha 57

    for index, row in df.iterrows():
        if not Livro.query.filter_by(titulo=row["Titulo do Livro"]).first():
            livro = Livro(
                titulo=row["Titulo do Livro"],
                autor=row["Autor"],
                categoria=row["Categoria"],
                ano=row["Ano de Publicação"],
                ativo=row["Ativo"] == "TRUE",
            )
            db.session.add(livro)
    db.session.commit()

#### Criar as Rotas para o Site ----> 1. **Rota `/inicio`:** 

@app.route("/inicio")
@login_required
def inicio():
    livros = Livro.query.all()
    return render_template("lista.html", lista_de_livros=livros)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("inicio"))
        else:
            flash("Login ou senha incorretos. Tente novamente.")
    return render_template("login.html")
    

# 2. **Rota `/curriculo`:** -----> Crie uma rota para a página de currículo:   

@app.route("/curriculo")
def curriculo():
    return render_template("curriculo.html")

# 3. **Rota `/novo`:** ---> Crie uma rota para a página de adicionar novos livros:

@app.route("/novo")
@login_required
def novo():
    return render_template("novo.html", titulo="Novo Livro")

# 4. **Rota `/criar`:**-----> Crie uma rota para processar o formulário e salvar o novo livro:

@app.route("/criar", methods=["POST"])
@login_required
def criar():
    titulo = request.form["titulo"]
    autor = request.form["autor"]
    categoria = request.form["categoria"]
    ano = request.form["ano"]
    editora = request.form["editora"]
    livro = Livro(titulo=titulo, autor=autor, categoria=categoria, ano=ano, editora=editora)
    db.session.add(livro)
    db.session.commit()
    return redirect(url_for("inicio"))

# 2. **Adicionar a Rota para Deletar Livros:** -----> Adicione o seguinte código no `app.py` para criar a rota de deleção:

@app.route("/deletar/<int:id>")
@login_required
def deletar(id):
    livro = Livro.query.get(id)
    if livro:
        db.session.delete(livro)
        db.session.commit()
    return redirect(url_for("inicio"))

#  Adicionar uma Rota para Exibir o Formulário de Edição para atualizar livros 

@app.route("/editar/<int:id>")
@login_required
def editar(id):
    livro = Livro.query.get(id)
    if livro:
        return render_template("editar.html", livro=livro)
    return redirect(url_for("inicio"))

### 3. **Adicionar a Rota para Processar a Atualização** 1. **Adicionar a Rota `/atualizar/<int:id>` no `app.py`:**
@app.route("/atualizar/<int:id>", methods=["POST"])
@login_required
def atualizar(id):
    livro = Livro.query.get(id)
    if livro:
        livro.titulo = request.form["titulo"]
        livro.autor = request.form["autor"]
        livro.categoria = request.form["categoria"]
        livro.ano = request.form["ano"]
        livro.editora = request.form["editora"]
        db.session.commit()
    return redirect(url_for("inicio"))

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Verifique se o usuário já existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Nome de usuário já existe. Tente um diferente.")
            return redirect(url_for("cadastro"))

        # Criação de um novo usuário
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Cadastro realizado com sucesso! Você já pode fazer login.")
        return redirect(url_for("login"))
    return render_template("cadastro.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# 1. **Importações Necessárias e Configurações:** ------> No `app.py`, importe as bibliotecas necessárias e configure o Flask-Login.
       # estão nas linhas 8 a 16

#2. **Criação do Modelo de Usuário:**
    # Adicione um modelo de usuário para armazenar informações de login.



# 3. **Carregar Usuário:**
    # Adicione a função para carregar um usuário por ID.

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

### 3. **Criação da Tela de Login**

#### 4.5 Iniciar o Servidor Flask ---> 1. **Adicionar o Código para Rodar o Servidor:**
    # No final do `app.py`, adicione o seguinte código para iniciar o servidor Flask:

if __name__ == "__main__":
    app.run(debug=True)
