# IA.py - LogicStart AI Enterprise Ultra
from openai import OpenAI
from pymongo import MongoClient
from datetime import datetime
import hashlib

class IA:
    def __init__(self, api_key=None, mongo_uri="mongodb://localhost:27017/"):
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.mongo = MongoClient(mongo_uri)
        self.db = self.mongo["logicstart"]
        self.chat_col = self.db["chat"]
        self.code_col = self.db["code"]
        self.embed_col = self.db["embeddings"]

    # ---------------- HASH ----------------
    def _hash(self, text):
        return hashlib.md5(text.encode()).hexdigest()

    # ---------------- EMBEDDINGS ----------------
    def gerar_embedding(self, texto):
        if not self.client:
            return []
        emb = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texto
        )
        return emb.data[0].embedding

    # ---------------- ARQUIVOS ----------------
    def salvar_codigo(self, user_id, nome, codigo):
        emb = self.gerar_embedding(codigo)
        self.code_col.update_one(
            {"user_id": user_id, "nome": nome},
            {"$set": {"codigo": codigo, "embedding": emb, "updated_at": datetime.utcnow()}},
            upsert=True
        )

    def buscar_codigo_relevante(self, user_id, pergunta, top_k=3):
        emb_query = self.gerar_embedding(pergunta)
        docs = list(self.code_col.find({"user_id": user_id}))
        def similaridade(a,b):
            return sum(x*y for x,y in zip(a,b)) if a and b else 0
        docs.sort(key=lambda d: similaridade(emb_query, d.get("embedding", [])), reverse=True)
        return docs[:top_k]

    # ---------------- HISTÓRICO ----------------
    def montar_contexto(self, user_id, pergunta):
        historico = list(self.chat_col.find({"user_id": user_id}).sort("timestamp",-1).limit(5))
        contexto = ""
        for h in reversed(historico):
            contexto += f"Usuário: {h['msg']}\nIA: {h['resposta']}\n"
        arquivos = self.buscar_codigo_relevante(user_id, pergunta)
        for arq in arquivos:
            contexto += f"\nArquivo ({arq['nome']}):\n{arq['codigo']}\n"
        return contexto

    # ---------------- CHAT PRINCIPAL ----------------
    def perguntar(self, user_id, mensagem):
        if not self.client:
            return "⚠ IA não configurada."

        contexto = self.montar_contexto(user_id, mensagem)
        prompt = f"""
Você é uma IA especialista em LogicStart (Python em português).
Objetivo:
- Responda de forma clara, útil e direta.
- Nunca repita literalmente a pergunta do usuário.
- Use o contexto do histórico e dos arquivos relevantes do usuário.
- Explique o raciocínio se gerar código.
- Sempre entregue código funcional quando solicitado.
- Se não souber a resposta, diga claramente e ofereça solução aproximada.

Contexto do usuário:
{contexto}

Nova pergunta do usuário:
{mensagem}

Resposta da IA:
"""
        resposta = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system", "content":"Você é uma IA especialista em LogicStart."},
                {"role":"user", "content": prompt}
            ],
            temperature=0.7
        ).choices[0].message.content

        # Salva histórico
        self.chat_col.insert_one({
            "user_id": user_id,
            "msg": mensagem,
            "resposta": resposta,
            "timestamp": datetime.utcnow()
        })

        return resposta

    # ---------------- FUNÇÕES AVANÇADAS ----------------
    def gerar(self, user_id, pedido):
        return self.perguntar(user_id, f"Gere código LogicStart: {pedido}")

    def corrigir(self, user_id, codigo):
        self.salvar_codigo(user_id, "temp_corrigir", codigo)
        return self.perguntar(user_id, "Corrija este código sem repetir o que está escrito e explique as mudanças:")

    def explicar(self, user_id, codigo):
        self.salvar_codigo(user_id, "temp_explicar", codigo)
        return self.perguntar(user_id, "Explique este código detalhadamente e de forma didática:")

    def melhorar(self, user_id, codigo):
        self.salvar_codigo(user_id, "temp_melhorar", codigo)
        return self.perguntar(user_id, "Melhore este código tornando-o mais limpo, eficiente e comentado:")

    # ---------------- AUTOCOMPLETE ----------------
    def sugerir(self, codigo):
        comandos = ["variavel","imprimir","se","senao","fim_se","repetir",
                    "fim_repetir","funcao","fim_funcao","retorna","enquanto","fim_enquanto"]
        ultima = codigo.split("\n")[-1].strip()
        return [c for c in comandos if c.startswith(ultima)]

    # ---------------- ANÁLISE ----------------
    def analisar(self, codigo):
        erros = []
        linhas = codigo.split("\n")
        for i,l in enumerate(linhas):
            if "imprimir" in l and "(" not in l:
                erros.append(f"Linha {i+1}: função 'imprimir' possivelmente sem parênteses")
            if "variavel" in l and "=" not in l:
                erros.append(f"Linha {i+1}: declaração 'variavel' possivelmente sem valor")
        return erros
