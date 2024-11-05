from pymongo import MongoClient
from cryptography.fernet import Fernet
import bcrypt
import tkinter as tk
from tkinter import messagebox, simpledialog
from bson import ObjectId

dados_user = None
dados_recordacao = None
key = None
record_ids = []

def connection_to_mongo():
    global dados_user, dados_recordacao, key
    try:
        client = MongoClient("mongodb+srv://root:12345@cluster0.0sf91.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
        db = client['Cluster0']
        dados_user = db['Usuarios']
        dados_recordacao = db['Medico']
        
        colecao_documento = dados_recordacao.count_documents({})
        messagebox.showinfo("Sucesso!!", f"Conexão estabelecida! Documentos na coleção: {colecao_documento}")
        
        key = generate_key()
        
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível conectar ao MongoDB: {str(e)}")

def generate_key():
    return Fernet.generate_key()

def encrypt_data(data, key):
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
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
    messagebox.showinfo("Sucesso", f"Usuário '{usuario}' registrado com sucesso!")

def criar_recor_medica(nomepaciente, historicomed, tratamentos):
    recordacao = {
        'nomepaciente': encrypt_data(nomepaciente, key),
        'historicomed': encrypt_data(historicomed, key),
        'tratamentos': encrypt_data(tratamentos, key)
    }
    result = dados_recordacao.insert_one(recordacao)
    record_ids.append(str(result.inserted_id))
    messagebox.showinfo("Sucesso", f"Registro médico criado para {nomepaciente} com sucesso!")

def acessar_recor_med_por_id(object_id):
    recordacao = dados_recordacao.find_one({'_id': object_id})
    if recordacao:
        nomepaciente = decrypt_data(recordacao['nomepaciente'], key)
        historicomed = decrypt_data(recordacao['historicomed'], key)
        tratamentos = decrypt_data(recordacao['tratamentos'], key)
        return {
            'nomepaciente': nomepaciente,
            'historicomed': historicomed,
            'tratamentos': tratamentos
        }
    else:
        messagebox.showwarning("Aviso", "Registro não encontrado.")
        return None

def acessar_registro():
    if not record_ids:
        messagebox.showwarning("Aviso", "Nenhum registro médico disponível.")
        return
    registros_list = "\n".join([f"{i}: {record_id}" for i, record_id in enumerate(record_ids)])
    n = simpledialog.askinteger("Acessar Registro", f"Digite o índice do registro que deseja acessar:\n\n{registros_list}")
    
    if n is not None and 0 <= n < len(record_ids):
        object_id = ObjectId(record_ids[n])
        recordacao = acessar_recor_med_por_id(object_id)
        if recordacao:
            messagebox.showinfo("Registro Médico", f"Nome do Paciente: {recordacao['nomepaciente']}\n"
                                                   f"Histórico Médico: {recordacao['historicomed']}\n"
                                                   f"Tratamentos: {recordacao['tratamentos']}")
    else:
        messagebox.showwarning("Aviso", "Opção inválida.")

def criar_registro():
    nomepaciente = simpledialog.askstring("Criar Registro", "Digite o nome do paciente:")
    historicomed = simpledialog.askstring("Criar Registro", "Digite o histórico médico:")
    tratamentos = simpledialog.askstring("Criar Registro", "Digite os tratamentos:")
    if nomepaciente and historicomed and tratamentos:
        criar_recor_medica(nomepaciente, historicomed, tratamentos)
    else:
        messagebox.showwarning("Aviso", "Todos os campos devem ser preenchidos.")

def registrar_usuario():
    id = simpledialog.askstring("Registrar Usuário", "Digite um ID para o usuário:")
    usuario = simpledialog.askstring("Registrar Usuário", "Digite o nome de usuário:")
    senha = simpledialog.askstring("Registrar Usuário", "Digite a senha:", show='*')
    if id and usuario and senha:
        registrar_user(id, usuario, senha)
    else:
        messagebox.showwarning("Aviso", "Todos os campos devem ser preenchidos.")

root = tk.Tk()
root.title("Gerenciador de Registros Médicos")

connect_button = tk.Button(root, text="Conectar ao MongoDB", command=connection_to_mongo)
connect_button.pack(pady=10)

register_user_button = tk.Button(root, text="Registrar Usuário", command=registrar_usuario)
register_user_button.pack(pady=10)

create_record_button = tk.Button(root, text="Criar Registro Médico", command=criar_registro)
create_record_button.pack(pady=10)

access_record_button = tk.Button(root, text="Acessar Registro Médico", command=acessar_registro)
access_record_button.pack(pady=10)

root.mainloop()