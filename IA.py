# IA.py - LogicStart AI Enterprise Ultimate

from openai import OpenAI
from pymongo import MongoClient
from datetime import datetime
import hashlib
import numpy as np

class IA:
    """
    Classe IA para LogicStart IDE
    Funções:
        - Gerar código
        - Corrigir código
        - Explicar código
        - Sugerir autocomplete
        - Analisar código
        - Contexto inteligente com histórico e arquivos relevantes
    """

    def __init__(self, api_key=None, mongo_uri="mongodb://localhost:27017/"):
        # Cliente OpenAI
        self.client = OpenAI(api_key=api_key) if api_key else None

        # MongoDB
        self.mongo = MongoClient(mongo_uri)
        self.db = self.mongo["logicstart"]
        self.chat_col = self.db["chat"]
        self.code_col = self.db["code"]

    # ================= HASH =================
    def _hash(self, text):
        return hashlib.md5(text.encode()).hexdigest()

    # ================= EMBEDDINGS =================
    def gerar_embedding(self, texto):
        """Cria embedding do texto usando OpenAI"""
        if not self.client:
            return []
        emb = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texto
        )
        return emb.data[0].embedding

    # ================= GERENCIAR CÓDIGO =================
    def salvar_codigo(self, user_id, nome, codigo):
        """Salva código no MongoDB com embedding"""
        emb = self.gerar_embedding(codigo)
        self.code_col.update_one(
            {"user_id": user_id, "nome": nome},
            {"$set": {"codigo": codigo, "embedding": emb, "updated_at": datetime.utcnow()}},
            upsert=True
        )

    def buscar_codigo_relevante(self, user_id, pergunta, top=3):
        """Retorna arquivos mais relevantes ao contexto da pergunta"""
        emb_query = self.gerar_embedding(pergunta)
        docs = list(self.code_col.find({"user_id": user_id}))

        def similaridade(a, b):
            if not a or not b: return 0
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        docs.sort(key=lambda d: similaridade(emb_query, d.get("embedding", [])), reverse=True)
        return docs[:top]

    # ================= CONTEXTO INTELIGENTE =================
    def montar_contexto(self, user_id, pergunta):
        """Cria contexto combinando histórico + arquivos relevantes"""
        historico = list(
            self.chat_col.find({"user_id": user_id}).sort("timestamp", -1).limit(5)
        )
        contexto = ""
        for h in reversed(historico):
            contexto += f"Usuário: {h['msg']}\nIA: {h['resposta']}\n"

        arquivos = self.buscar_codigo_relevante(user_id, pergunta)
        for arq in arquivos:
            contexto += f"\nArquivo ({arq['nome']}):\n{arq['codigo']}\n"

        return contexto

    # ================= CHAT =================
    def perguntar(self, user_id, mensagem):
        """Responde pergunta do usuário usando contexto e histórico"""
        if not self.client:
            return "⚠ IA não configurada."

        contexto = self.montar_contexto(user_id, mensagem)
        prompt = f"{contexto}\nNova pergunta:\n{mensagem}"

        resposta = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é uma IA especialista em LogicStart (Python em português). Seja útil, preciso e não repita a pergunta do usuário."},
                {"role": "user", "content": prompt}
            ]
        ).choices[0].message.content

        self.chat_col.insert_one({
            "user_id": user_id,
            "msg": mensagem,
            "resposta": resposta,
            "timestamp": datetime.utcnow()
        })

        return resposta

    # ================= FUNÇÕES DE CÓDIGO =================
    def gerar(self, user_id, pedido):
        return self.perguntar(user_id, f"Gere código LogicStart:\n{pedido}")

    def corrigir(self, user_id, codigo):
        self.salvar_codigo(user_id, "temp", codigo)
        return self.perguntar(user_id, "Corrija este código e explique as alterações.")

    def explicar(self, user_id, codigo):
        self.salvar_codigo(user_id, "temp", codigo)
        return self.perguntar(user_id, "Explique detalhadamente este código.")

    # ================= AUTOCOMPLETE =================
    def sugerir(self, codigo):
        comandos = [
            "variavel","imprimir","se","senao","fim_se",
            "repetir","fim_repetir","funcao","fim_funcao","retorna",
            "enquanto","fim_enquanto","para","fim_para","classe","fim_classe"
        ]
        ultima = codigo.split("\n")[-1].strip()
        return [c for c in comandos if c.startswith(ultima)]

    # ================= ANÁLISE DE CÓDIGO =================
    def analisar(self, codigo):
        """Detecta erros básicos no código"""
        erros = []
        linhas = codigo.split("\n")
        for i, l in enumerate(linhas, start=1):
            if "@" in l:
                erros.append(f"Linha {i}: caractere '@' inválido")
            if "import os" in l or "import sys" in l:
                erros.append(f"Linha {i}: uso de biblioteca proibida")
        return erros

    # ================= UTILIDADES =================
    def listar_historico(self, user_id, limite=20):
        """Retorna histórico recente"""
        historico = list(
            self.chat_col.find({"user_id": user_id}).sort("timestamp", -1).limit(limite)
        )
        return [{"mensagem": h["msg"], "resposta": h["resposta"]} for h in historico]

    def deletar_historico(self, user_id):
        """Deleta histórico do usuário"""
        self.chat_col.delete_many({"user_id": user_id})
