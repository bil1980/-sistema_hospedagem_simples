
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import time
from decimal import Decimal

from supabase import create_client
import redis
import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================================
# CONFIGURAÇÃO: SUPABASE + REDIS
# ==========================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
REDIS_URL = os.getenv("REDIS_URL")

# Conexão com Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# Conexão com Redis
redis_client = None

try:
    candidato = redis.from_url(
        REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2
    )

    candidato.ping()
    redis_client = candidato

    print("Redis conectado com sucesso!")

except Exception as erro:
    redis_client = None
    print("Redis não conectado:", erro)
    print("O sistema utilizará diretamente o Supabase.")


# ==========================================================
# FUNÇÕES AUXILIARES
# ==========================================================

def limpar_cache_relatorio():
    """Remove o relatório do Redis depois de alterações nos dados."""

    if redis_client:
        try:
            redis_client.delete("sistema_hospedagem:vw_reservas")
            print("Cache do relatório removido.")

        except Exception as erro:
            print("Erro ao limpar cache:", erro)


def converter_para_json(valor):
    """Converte datas e valores Decimal para JSON."""

    if hasattr(valor, "isoformat"):
        return valor.isoformat()

    if isinstance(valor, Decimal):
        return float(valor)

    return valor


# ==========================================================
# JANELA PRINCIPAL
# ==========================================================

class SistemaHospedagem:

    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Hospedagem")
        self.root.geometry("850x600")
        self.root.resizable(False, False)

        self.criar_interface()

    def limpar_tela(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ======================================================
    # MENU PRINCIPAL
    # ======================================================

    def criar_interface(self):
        self.limpar_tela()

        tk.Label(
            self.root,
            text="SISTEMA DE HOSPEDAGEM",
            font=("Arial", 22, "bold")
        ).pack(pady=30)

        tk.Label(
            self.root,
            text="Gerenciamento de hóspedes e reservas",
            font=("Arial", 12)
        ).pack(pady=5)

        frame = tk.Frame(self.root)
        frame.pack(pady=35)

        tk.Button(
            frame,
            text="Cadastrar Hóspede",
            width=25,
            height=2,
            command=self.tela_hospede
        ).grid(row=0, column=0, padx=10, pady=10)

        tk.Button(
            frame,
            text="Nova Reserva",
            width=25,
            height=2,
            command=self.tela_reserva
        ).grid(row=0, column=1, padx=10, pady=10)

        tk.Button(
            frame,
            text="Calcular Valor",
            width=25,
            height=2,
            command=self.tela_calculo
        ).grid(row=1, column=0, padx=10, pady=10)

        tk.Button(
            frame,
            text="Relatório de Reservas",
            width=25,
            height=2,
            command=self.tela_relatorio
        ).grid(row=1, column=1, padx=10, pady=10)

        tk.Button(
            self.root,
            text="Sair",
            width=20,
            command=self.root.destroy
        ).pack(pady=20)

    # ======================================================
    # CADASTRO DE HÓSPEDE - SUPABASE
    # ======================================================

    def tela_hospede(self):
        self.limpar_tela()

        tk.Label(
            self.root,
            text="CADASTRAR HÓSPEDE",
            font=("Arial", 20, "bold")
        ).pack(pady=25)

        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Label(frame, text="Nome:").grid(
            row=0, column=0, sticky="e", padx=10, pady=10
        )

        nome = tk.Entry(frame, width=35)
        nome.grid(row=0, column=1)

        tk.Label(frame, text="E-mail:").grid(
            row=1, column=0, sticky="e", padx=10, pady=10
        )

        email = tk.Entry(frame, width=35)
        email.grid(row=1, column=1)

        tk.Label(frame, text="Telefone:").grid(
            row=2, column=0, sticky="e", padx=10, pady=10
        )

        telefone = tk.Entry(frame, width=35)
        telefone.grid(row=2, column=1)

        def salvar():
            nome_valor = nome.get().strip()

            if not nome_valor:
                messagebox.showwarning(
                    "Atenção",
                    "Informe o nome."
                )
                return

            try:
                dados = {
                    "nome": nome_valor,
                    "email": email.get().strip() or None,
                    "telefone": telefone.get().strip() or None
                }

                supabase.table("hospede").insert(dados).execute()

                limpar_cache_relatorio()

                messagebox.showinfo(
                    "Sucesso",
                    "Hóspede cadastrado!"
                )

                nome.delete(0, tk.END)
                email.delete(0, tk.END)
                telefone.delete(0, tk.END)

            except Exception as erro:
                messagebox.showerror(
                    "Erro ao cadastrar hóspede",
                    str(erro)
                )

        tk.Button(
            self.root,
            text="Salvar",
            width=20,
            command=salvar
        ).pack(pady=15)

        tk.Button(
            self.root,
            text="Voltar",
            width=20,
            command=self.criar_interface
        ).pack()

    # ======================================================
    # NOVA RESERVA - FUNCTION RPC DO SUPABASE
    # ======================================================

    def tela_reserva(self):
        self.limpar_tela()

        tk.Label(
            self.root,
            text="NOVA RESERVA",
            font=("Arial", 20, "bold")
        ).pack(pady=20)

        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        tk.Label(frame, text="ID do hóspede:").grid(
            row=0, column=0, sticky="e", padx=10, pady=8
        )

        id_hospede = tk.Entry(frame, width=30)
        id_hospede.grid(row=0, column=1)

        tk.Label(frame, text="Check-in (AAAA-MM-DD):").grid(
            row=1, column=0, sticky="e", padx=10, pady=8
        )

        check_in = tk.Entry(frame, width=30)
        check_in.grid(row=1, column=1)

        tk.Label(frame, text="Check-out (AAAA-MM-DD):").grid(
            row=2, column=0, sticky="e", padx=10, pady=8
        )

        check_out = tk.Entry(frame, width=30)
        check_out.grid(row=2, column=1)

        tk.Label(frame, text="Valor da diária:").grid(
            row=3, column=0, sticky="e", padx=10, pady=8
        )

        valor = tk.Entry(frame, width=30)
        valor.grid(row=3, column=1)

        def criar():
            try:
                hid = int(id_hospede.get())

                entrada = datetime.strptime(
                    check_in.get().strip(),
                    "%Y-%m-%d"
                ).date()

                saida = datetime.strptime(
                    check_out.get().strip(),
                    "%Y-%m-%d"
                ).date()

                diaria = float(
                    valor.get().replace(",", ".")
                )

                if saida <= entrada:
                    messagebox.showwarning(
                        "Atenção",
                        "O check-out deve ser depois do check-in."
                    )
                    return

                if diaria < 0:
                    messagebox.showwarning(
                        "Atenção",
                        "O valor da diária não pode ser negativo."
                    )
                    return

                supabase.rpc(
                    "criar_reserva",
                    {
                        "p_id_hospede": hid,
                        "p_check_in": entrada.isoformat(),
                        "p_check_out": saida.isoformat(),
                        "p_valor_diaria": diaria
                    }
                ).execute()

                limpar_cache_relatorio()

                messagebox.showinfo(
                    "Sucesso",
                    "Reserva criada com sucesso!"
                )

                id_hospede.delete(0, tk.END)
                check_in.delete(0, tk.END)
                check_out.delete(0, tk.END)
                valor.delete(0, tk.END)

            except Exception as erro:
                messagebox.showerror(
                    "Erro ao criar reserva",
                    str(erro)
                )

        tk.Button(
            self.root,
            text="Criar Reserva",
            width=25,
            command=criar
        ).pack(pady=15)

        tk.Button(
            self.root,
            text="Voltar",
            width=20,
            command=self.criar_interface
        ).pack()

    # ======================================================
    # CALCULAR VALOR - FUNCTION RPC DO SUPABASE
    # ======================================================

    def tela_calculo(self):
        self.limpar_tela()

        tk.Label(
            self.root,
            text="CALCULAR VALOR DA RESERVA",
            font=("Arial", 20, "bold")
        ).pack(pady=25)

        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Label(frame, text="Quantidade de dias:").grid(
            row=0, column=0, padx=10, pady=10
        )

        dias = tk.Entry(frame, width=25)
        dias.grid(row=0, column=1)

        tk.Label(frame, text="Valor da diária:").grid(
            row=1, column=0, padx=10, pady=10
        )

        diaria = tk.Entry(frame, width=25)
        diaria.grid(row=1, column=1)

        resultado = tk.Label(
            self.root,
            text="Valor total: R$ 0,00",
            font=("Arial", 16, "bold")
        )
        resultado.pack(pady=20)

        def calcular():
            try:
                qtd_dias = int(dias.get())

                valor_diaria = float(
                    diaria.get().replace(",", ".")
                )

                if qtd_dias <= 0 or valor_diaria < 0:
                    messagebox.showwarning(
                        "Atenção",
                        "Informe dias maiores que zero e diária não negativa."
                    )
                    return

                resposta = supabase.rpc(
                    "calcular_valor_reserva",
                    {
                        "p_quantidade_dias": qtd_dias,
                        "p_valor_diaria": valor_diaria
                    }
                ).execute()

                total = resposta.data

                if isinstance(total, list):
                    total = total[0] if total else 0

                if isinstance(total, dict):
                    total = next(iter(total.values()), 0)

                resultado.config(
                    text=f"Valor total: R$ {float(total):.2f}".replace(".", ",")
                )

            except Exception as erro:
                messagebox.showerror(
                    "Erro no cálculo",
                    str(erro)
                )

        tk.Button(
            self.root,
            text="Calcular",
            width=25,
            command=calcular
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Voltar",
            width=20,
            command=self.criar_interface
        ).pack()

    # ======================================================
    # RELATÓRIO - VIEW DO SUPABASE + REDIS
    # ======================================================

    def tela_relatorio(self):
        self.limpar_tela()

        tk.Label(
            self.root,
            text="RELATÓRIO DE RESERVAS",
            font=("Arial", 20, "bold")
        ).pack(pady=20)

        colunas = (
            "id",
            "hospede",
            "check_in",
            "check_out",
            "diaria",
            "status"
        )

        tabela = ttk.Treeview(
            self.root,
            columns=colunas,
            show="headings",
            height=12
        )

        titulos = {
            "id": "ID",
            "hospede": "Hóspede",
            "check_in": "Check-in",
            "check_out": "Check-out",
            "diaria": "Diária",
            "status": "Status"
        }

        for coluna in colunas:
            tabela.heading(
                coluna,
                text=titulos[coluna]
            )

            tabela.column(
                coluna,
                width=120
            )

        tabela.pack(padx=20, pady=10)

        # Informações sobre a consulta

        info_banco = tk.Label(
            self.root,
            text="Banco utilizado: aguardando consulta...",
            font=("Arial", 11)
        )
        info_banco.pack(pady=5)

        info_tempo = tk.Label(
            self.root,
            text="Tempo de consulta: --",
            font=("Arial", 11)
        )
        info_tempo.pack(pady=5)

        # ==================================================
        # BUSCAR RELATÓRIO
        # ==================================================

        def buscar_relatorio():

            cache_key = "sistema_hospedagem:vw_reservas"

            inicio = time.perf_counter()

            # 1. Tenta buscar no Redis

            if redis_client:
                try:
                    cache = redis_client.get(cache_key)

                    if cache:
                        registros = json.loads(cache)

                        tempo = (
                            time.perf_counter() - inicio
                        ) * 1000

                        print("Dados recuperados do Redis!")

                        return registros, "Redis (Cache)", tempo

                except Exception as erro:
                    print("Erro ao consultar Redis:", erro)

            # 2. Consulta o Supabase se não encontrar no Redis

            resposta = (
                supabase.table("vw_reservas")
                .select(
                    "id_reserva,hospede,check_in,check_out,"
                    "valor_diaria,status"
                )
                .order("id_reserva")
                .execute()
            )

            registros = resposta.data or []

            # 3. Armazena os dados no Redis por 60 segundos

            if redis_client:
                try:
                    redis_client.setex(
                        cache_key,
                        60
                        ,
                        json.dumps(
                            registros,
                            default=converter_para_json
                        )
                    )

                    print("Dados armazenados no Redis!")

                except Exception as erro:
                    print("Erro ao armazenar no Redis:", erro)

            tempo = (
                time.perf_counter() - inicio
            ) * 1000

            print("Dados consultados no Supabase!")

            return registros, "Supabase", tempo

        # ==================================================
        # CARREGAR RELATÓRIO NA TABELA
        # ==================================================

        def carregar():

            try:
                registros, banco, tempo = buscar_relatorio()

                # Limpa a tabela antes de atualizar

                for item in tabela.get_children():
                    tabela.delete(item)

                # Insere as reservas

                for registro in registros:
                    tabela.insert(
                        "",
                        tk.END,
                        values=(
                            registro.get("id_reserva"),
                            registro.get("hospede"),
                            registro.get("check_in"),
                            registro.get("check_out"),
                            registro.get("valor_diaria"),
                            registro.get("status")
                        )
                    )

                # Atualiza o banco utilizado

                info_banco.config(
                    text=f"Banco utilizado: {banco}"
                )

                # Atualiza o tempo de consulta

                info_tempo.config(
                    text=f"Tempo de consulta: {tempo:.2f} ms"
                )

            except Exception as erro:
                messagebox.showerror(
                    "Erro ao carregar relatório",
                    str(erro)
                )

        # Botão para atualizar relatório

        tk.Button(
            self.root,
            text="Atualizar relatório",
            width=25,
            command=carregar
        ).pack(pady=8)

        # Botão para voltar

        tk.Button(
            self.root,
            text="Voltar",
            width=20,
            command=self.criar_interface
        ).pack()

        # Carrega o relatório automaticamente

        carregar()


# ==========================================================
# INICIAR SISTEMA
# ==========================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = SistemaHospedagem(root)

    root.mainloop()
