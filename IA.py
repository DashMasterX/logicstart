# IA.py - LogicStart AI Enterprise

from openai import OpenAI
from pymongo import MongoClient
from datetime import datetime
import hashlib

class IA:

    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key) if api_key else None

        # MongoDB
        self.mongo = MongoClient("mongodb://localhost:27017/")
        self.db = self.mongo["logicstart"]

        self.chat_col = self.db["chat"]
        self.code_col = self.db["code"]
        self.embed_col = self.db["embeddings"]

    # ================= HASH =================

    def _hash(self, text):
        return hashlib.md5(text.encode()).hexdigest()

    # ================= EMBEDDING =================

    def gerar_embedding(self, texto):
        if not self.client:
            return []

        emb = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texto
        )
        return emb.data[0].embedding

    def salvar_codigo(self, user_id, nome, codigo):
        emb = self.gerar_embedding(codigo)

        self.code_col.update_one(
            {"user_id": user_id, "nome": nome},
            {
                "$set": {
                    "codigo": codigo,
                    "embedding": emb,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    def buscar_codigo_relevante(self, user_id, pergunta):
        emb_query = self.gerar_embedding(pergunta)

        docs = list(self.code_col.find({"user_id": user_id}))

        def similaridade(a, b):
            if not a or not b:
                return 0
            return sum(x*y for x,y in zip(a,b))

        docs.sort(
            key=lambda d: similaridade(emb_query, d.get("embedding", [])),
            reverse=True
        )

        return docs[:3]  # top 3 arquivos relevantes

    # ================= CONTEXTO INTELIGENTE =================

    def montar_contexto(self, user_id, pergunta):
        historico = list(
            self.chat_col.find({"user_id": user_id})
            .sort("timestamp", -1)
            .limit(5)
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
        if not self.client:
            return "IA não configurada."

        contexto = self.montar_contexto(user_id, mensagem)

        prompt = f"""
{contexto}

Nova pergunta:
{mensagem}
"""

        resposta = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é uma IA especialista em LogicStart (Python em português). Use o contexto dos arquivos e histórico."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        ).choices[0].message.content

        self.chat_col.insert_one({
            "user_id": user_id,
            "msg": mensagem,
            "resposta": resposta,
            "timestamp": datetime.utcnow()
        })

        return resposta

    # ================= FUNÇÕES =================

    def gerar(self, user_id, pedido):
        return self.perguntar(user_id, f"Gere código LogicStart: {pedido}")

    def corrigir(self, user_id, codigo):
        self.salvar_codigo(user_id, "temp", codigo)
        return self.perguntar(user_id, "Corrija esse código.")

    def explicar(self, user_id, codigo):
        self.salvar_codigo(user_id, "temp", codigo)
        return self.perguntar(user_id, "Explique esse código.")

    # ================= AUTOCOMPLETE =================

    def sugerir(self, codigo):
        comandos = [
            "variavel","imprimir","se","senao","fim_se",
            "repetir","fim_repetir","funcao","fim_funcao","retorna"
        ]

        ultima = codigo.split("\n")[-1].strip()
        return [c for c in comandos if c.startswith(ultima)]
