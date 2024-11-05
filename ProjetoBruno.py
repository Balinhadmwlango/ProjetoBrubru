from pymongo import MongoClient
from cryptography.fernet import Fernet
import bcrypt
import tkinter as tk
from tkinter import messagebox
from bson import ObjectId

dados_user = None
dados_recordacao = None
key = None
idencrypted = [] 
x = 0 
t = 0

def connection_to_mongo():
    global dados_user, dados_recordacao, key, t
    try:
        client = MongoClient("mongodb+srv://root:12345@cluster0.0sf91.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client['Cluster0']
        dados_user = db['Usuarios']
        dados_recordacao = db['Medico']
        
        colecao_documento = dados_recordacao.count_documents({})
        messagebox.showinfo("Sucesso!!", f"Conexão estabelecida! Documentos na coleção: {colecao_documento}")
        
        key = generate_key()
        
        user_choice()

    except Exception as e:
        print(f"Erro! Não foi possível conectar ao MongoDB: {str(e)}")

def user_choice():
    global t
    while True:
        choice = input("Digite 1 para acessar um registro médico, 2 para criar um registro médico ou 3 para sair: ")
    
        if choice == '1':
            if len(idencrypted) == 0:
                print("Nenhum registro médico disponível.")
            else:
                for x in range(t):
                    print(f'{x} = {idencrypted[x]}')

                try:
                    n = int(input("Você quer acessar qual deles? "))
                    if 0 <= n < t:
                        recordacao = acessar_recor_med(idencrypted[n])
                        if recordacao:
                            print(f"Nome do Paciente: {recordacao['nomepaciente']}")
                            print(f"Histórico Médico: {recordacao['historicomed']}")
                            print(f"Tratamentos: {recordacao['tratamentos']}")
                        else:
                            print("Registro não encontrado.")
                    else:
                        print("Opção inválida.")
                except ValueError:
                    print("Por favor, insira um número válido.")

        elif choice == '2':
            id = input("Digite um ID para o registro médico: ")
            username = input("Digite o nome de usuário: ")
            password = input("Digite a senha: ")
            registrar_user(id, username, password)

        elif choice == '3':
            break

def generate_key():
    return Fernet.generate_key()

def encrypt_data(data, key):
    global idencrypted, x
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    idencrypted.append(encrypted_data)
    x += 1
    return encrypted_data

def decrypt_data(encrypted_data, key):
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data).decode()
    return decrypted_data

def senha_hash(senha):
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt())

def checar_senha(hashed, senha):
    return bcrypt.checkpw(senha.encode(), hashed)

def registrar_user(id, usuario, senha):
    hashed_senha = senha_hash(senha)
    dados_user.insert_one({'id': id, 'usuario': usuario, 'senha': hashed_senha})
    print(f"Usuário '{usuario}' registrado com sucesso!")

def criar_recor_medica(nomepaciente, historicomed, tratamentos, key):
    global t
    recordacao = {
        'nomepaciente': encrypt_data(nomepaciente, key),
        'historicomed': encrypt_data(historicomed, key),
        'tratamentos': encrypt_data(tratamentos, key)
    }
    dados_recordacao.insert_one(recordacao)
    print(f"Registro médico criado para {nomepaciente} com sucesso!")
    t += 1

def acessar_recor_med(encrypted_id):
    try:
        recordacao = dados_recordacao.find_one({'_id': ObjectId(encrypted_id)})
        if recordacao:
            nomepaciente = decrypt_data(recordacao['nomepaciente'], key)
            historicomed = decrypt_data(recordacao['historicomed'], key)
            tratamentos = decrypt_data(recordacao['tratamentos'], key)
            return {
                'nomepaciente': nomepaciente,
                'historicomed': historicomed,
                'tratamentos': tratamentos
            }
    except Exception as e:
        print(f"Erro ao acessar o registro médico: {e}")
    return None


root = tk.Tk()
root.title("Conectar ao MongoDB Atlas")

label = tk.Label(root, text="Clique no botão para conectar ao MongoDB Atlas")
label.pack(pady=10)

connect_button = tk.Button(root, text="Conectar", command=connection_to_mongo)
connect_button.pack(pady=10)

root.mainloop()