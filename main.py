import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

# Conexão com o banco
conn = sqlite3.connect("condominios.db")
cursor = conn.cursor()

# Criação das tabelas
cursor.execute("""
    CREATE TABLE IF NOT EXISTS condominio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        endereco TEXT NOT NULL,
        apartamentos INTEGER NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS observacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        condominio_id INTEGER,
        data TEXT,
        descricao TEXT,
        FOREIGN KEY (condominio_id) REFERENCES condominio(id)
    )
""")
conn.commit()



# Função para cadastrar condomínio
def cadastrar_condominio():
    nome = entry_nome.get().strip().upper()  # Convertendo para MAIÚSCULO
    endereco = entry_endereco.get().strip()
    try:
        apartamentos = int(entry_apartamentos.get())
    except ValueError:
        messagebox.showerror("Erro", "Número de apartamentos inválido.")
        return

    if not nome or not endereco:
        messagebox.showwarning("Aviso", "Preencha todos os campos.")
        return

    # Verificar se já existe condomínio com esse nome
    cursor.execute("SELECT * FROM condominio WHERE nome = ?", (nome,))
    if cursor.fetchone():
        messagebox.showerror("Erro", "Já existe um condomínio com esse nome.")
        return

    cursor.execute("INSERT INTO condominio (nome, endereco, apartamentos) VALUES (?, ?, ?)",
                   (nome, endereco, apartamentos))
    conn.commit()
    messagebox.showinfo("Sucesso", "Condomínio cadastrado com sucesso.")
    limpar_campos()
    listar_condominios()


# Função para limpar campos
def limpar_campos():
    entry_nome.delete(0, tk.END)
    entry_endereco.delete(0, tk.END)
    entry_apartamentos.delete(0, tk.END)

# Função para listar os condomínios
def listar_condominios(filtro=""):
    for row in tree.get_children():
        tree.delete(row)

    if filtro:
        cursor.execute("SELECT * FROM condominio WHERE nome LIKE ?", ('%' + filtro + '%',))
    else:
        cursor.execute("SELECT * FROM condominio")
    
    for cond in cursor.fetchall():
        tree.insert("", "end", values=cond)

# Função chamada ao clicar na lista
def ao_selecionar(event):
    item = tree.focus()
    if item:
        condominio = tree.item(item)['values']
        entry_nome.delete(0, tk.END)
        entry_nome.insert(0, condominio[1])
        entry_endereco.delete(0, tk.END)
        entry_endereco.insert(0, condominio[2])
        entry_apartamentos.delete(0, tk.END)
        entry_apartamentos.insert(0, condominio[3])
        exibir_historico(condominio[0])

# Função para adicionar observação
def adicionar_observacao():
    item = tree.focus()
    if not item:
        messagebox.showwarning("Aviso", "Selecione um condomínio.")
        return

    condominio_id = tree.item(item)['values'][0]
    texto = txt_obs.get("1.0", tk.END).strip()
    if not texto:
        messagebox.showwarning("Aviso", "Digite uma observação.")
        return

    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO observacoes (condominio_id, data, descricao) VALUES (?, ?, ?)",
                   (condominio_id, data, texto))
    conn.commit()
    txt_obs.delete("1.0", tk.END)
    exibir_historico(condominio_id)
    messagebox.showinfo("Sucesso", "Observação registrada.")

# Função para exibir histórico de observações
def exibir_historico(condominio_id):
    txt_historico.config(state=tk.NORMAL)
    txt_historico.delete("1.0", tk.END)
    cursor.execute("SELECT data, descricao FROM observacoes WHERE condominio_id = ? ORDER BY data DESC", (condominio_id,))
    historico = cursor.fetchall()
    if not historico:
        txt_historico.insert(tk.END, "Sem observações registradas.")
    else:
        for data, desc in historico:
            txt_historico.insert(tk.END, f"[{data}]\n{desc}\n\n")
    txt_historico.config(state=tk.DISABLED)

# Função de busca
def buscar():
    termo = entry_busca.get()
    listar_condominios(termo)

# Interface principal
root = tk.Tk()
root.title("Sistema de Cadastro de Condomínios")
root.geometry("900x600")

# Formulário
frame_top = tk.Frame(root)
frame_top.pack(pady=10)

tk.Label(frame_top, text="Nome:").grid(row=0, column=0)
entry_nome = tk.Entry(frame_top, width=30)
entry_nome.grid(row=0, column=1, padx=5)

tk.Label(frame_top, text="Endereço:").grid(row=1, column=0)
entry_endereco = tk.Entry(frame_top, width=30)
entry_endereco.grid(row=1, column=1, padx=5)

tk.Label(frame_top, text="Apartamentos:").grid(row=2, column=0)
entry_apartamentos = tk.Entry(frame_top, width=10)
entry_apartamentos.grid(row=2, column=1, sticky="w", padx=5)

tk.Button(frame_top, text="Cadastrar", command=cadastrar_condominio, width=20).grid(row=3, column=1, pady=5)

# Busca
frame_busca = tk.Frame(root)
frame_busca.pack()
tk.Label(frame_busca, text="Buscar:").pack(side="left")
entry_busca = tk.Entry(frame_busca)
entry_busca.pack(side="left", padx=5)
tk.Button(frame_busca, text="Pesquisar", command=buscar).pack(side="left")

# Tabela de condomínios
tree = ttk.Treeview(root, columns=("ID", "Nome", "Endereço", "Aptos"), show="headings", height=7)
for col in ("ID", "Nome", "Endereço", "Aptos"):
    tree.heading(col, text=col)
    tree.column(col, width=150)
tree.pack(pady=10)
tree.bind("<<TreeviewSelect>>", ao_selecionar)

# Observações
frame_obs = tk.LabelFrame(root, text="Nova Observação", padx=10, pady=10)
frame_obs.pack(fill="x", padx=10)

txt_obs = tk.Text(frame_obs, height=4)
txt_obs.pack(fill="x")

tk.Button(frame_obs, text="Adicionar Observação", command=adicionar_observacao).pack(pady=5)

# Histórico
frame_hist = tk.LabelFrame(root, text="Histórico de Observações", padx=10, pady=10)
frame_hist.pack(fill="both", expand=True, padx=10)

txt_historico = tk.Text(frame_hist, state=tk.DISABLED)
txt_historico.pack(fill="both", expand=True)

listar_condominios()

root.mainloop()

conn.close()
