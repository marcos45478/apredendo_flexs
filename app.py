from flask import Flask, render_template, request, jsonify, redirect, url_for, flash  # flash para mensagens de feedback
import json
import os
import uuid  # usado para gerar IDs únicos (uuid4)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# chave necessária para utilizar `flash` e sessões
app.secret_key = "chave-super-secreta"

def carregar_usuarios():
    # Verifica se o arquivo 'usuarios.json' existe e carrega os dados
    try:
        if os.path.exists("usuarios.json"):
            with open("usuarios.json", "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        else:
            return []  # Retorna uma lista vazia se o arquivo não existir
    except:
        return []  # Retorna uma lista vazia se ocorrer algum erro ao ler o arquivo
   
def salvar_usuario(usuario):
    # Carrega os usuários existentes
    usuarios = carregar_usuarios()

    try:
        # Adiciona o novo usuário à lista
        usuarios.append(usuario)

        # Salva a lista atualizada de usuários no arquivo 'usuarios.json'
        with open("usuarios.json", "w", encoding="utf-8") as arquivo:
            json.dump(usuarios, arquivo, indent=4)

        return True  # Retorna True se o salvamento for bem-sucedido
    except:
        return False  # Retorna False se ocorrer um erro ao salvar

@app.route("/")
def home():
    # Renderiza a página inicial com o formulário de cadastro
    return render_template("home.html")
   
@app.route("/cadastro-usuario")
def tela_cadastro():
    return render_template("cadastro-usuarios.html")

@app.route("/login")
def tela_login():
     return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        cpf = request.form.get("cpf")
        senha_digitada = request.form.get("senha")

        usuarios = carregar_usuarios()

        for usuario in usuarios:
            if usuario["cpf"] == cpf and check_password_hash(usuario["senha"], senha_digitada):
                flash("Login realizado com sucesso", "sucesso")
                return redirect(url_for("buscar_usuarios"))
            
            flash("CPF ou senha incorretos", "erro")

            return render_template("login.html")

@app.route("/cadastro-usuario", methods=["POST"])
def cadastrar_usuario():
    # Recupera os dados enviados pelo formulário HTML
    nome = request.form.get("nome")
    cpf = request.form.get("cpf")            # CPF do usuário (identificador único)
    email = request.form.get("email")
    idade = request.form.get("idade")
    senha = request.form.get("senha")
    senha_hash = generate_password_hash(senha)

    if not all([nome, cpf, email, idade, senha]):
        flash("Todos os campos são obrigatórios.", "erro")
        return redirect(url_for("cadastrar_usuario"))
    # carrega usuários atuais para checar duplicatas
    usuarios = carregar_usuarios()

    # evita inserir CPF repetido
    if any(u.get("cpf") == cpf for u in usuarios):
        flash("CPF já cadastrado no sistema.", "erro")
        return redirect(url_for("cadastrar_usuario"))
    
    if int(idade) < 18:
        flash("Idade mínima para cadastro é de 18 anos.", "erro")
        return redirect(url_for("cadastrar_usuario"))
    # cria o objeto do usuário, incluindo um id UUID
    usuario = {
        "id": str(uuid.uuid4()),  # identificador global para uso interno
        "nome": nome,
        "cpf": cpf,
        "email": email,
        "idade": idade,
        "senha": senha_hash,
    }

    # tenta salvar usando a função auxiliar
    status = salvar_usuario(usuario)

    if status:
        # após cadastro redireciona para a lista de usuários
        flash("Usuário cadastrado com sucesso.", "sucesso")
        return redirect(url_for('buscar_usuarios'))
    else:
        # caso de erro de escrita
        flash("Não foi possível cadastrar o usuário.", "erro")
        return redirect(url_for('home'))



@app.route("/usuarios/json", methods=["GET"])
def buscar_usuarios_json():
    usuarios = carregar_usuarios()
    return jsonify(usuarios)

@app.route("/usuarios", methods=["GET"])
def buscar_usuarios():
    usuarios = carregar_usuarios()
    total = len(usuarios)
    return render_template("usuarios.html", usuarios = usuarios, total=total)

@app.route("/usuarios/deletar", methods=["POST"])
def deletar_usuario():
    cpf = request.form.get("cpf")
    
    if not cpf:
        flash("CPF necessário para exclusão", "erro")
        return redirect(url_for('buscar_usuarios'))
    
    usuarios = carregar_usuarios()
    novos = [u for u in usuarios if u.get("cpf") != cpf]

    try: 
        with open("usuarios.json", "w", encoding="utf-8") as arquivo:
            json.dump(novos, arquivo, indent=4)
            flash ("usuario removido.",  "sucesso")
    except Exception as e:
        flash(f"Erro ao deleta: {e}", "erro")

    return redirect(url_for('buscar_usuarios'))
if __name__== '__main__':
    app.run(debug=True, port=5001)