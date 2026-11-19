"""Olist Intelligent Reviews — auditable lexical triage prototype."""
import re, unicodedata
import pandas as pd
TAXONOMY = {
 "Entrega e logística":[r"\bentreg",r"\batras",r"\bdemor",r"\bprazo",r"\btransport",r"\brastre",r"\bnao recebi",r"\bnao chegou",r"\bextravi",r"\bchegou depois"],
 "Qualidade / defeito do produto":[r"\bdefeit",r"\bquebrad",r"\bnao funciona",r"\bparou de funcionar",r"\bdanificad",r"\bavariad",r"\bqualidade",r"\bdescostur",r"\bmanchad"],
 "Pedido incompleto / item ausente":[r"\bfaltou",r"\bfaltando",r"\bnao veio",r"\bnao vieram",r"\bpedido incompleto",r"\bitem ausente",r"\bquantidade menor"],
 "Produto divergente do anúncio":[r"\bproduto errado",r"\bveio errado",r"\bdiferente do anunciado",r"\bnao corresponde",r"\bmodelo diferente",r"\bnao era o que"],
 "Pagamento / estorno":[r"\bcobranc",r"\bcobrado",r"\bpagamento",r"\bestorno",r"\breembolso",r"\bcartao",r"\bduplicad"],
 "Embalagem":[r"\bembalagem",r"\bamassad",r"\bmal embal",r"\bcaixa aberta",r"\bpacote rasgado",r"\bsem protecao"],
 "Atendimento / comunicação":[r"\batendimento",r"\bsuporte",r"\bnao responderam",r"\bnao responde",r"\bsem retorno",r"\bvendedor nao respondeu"]
}
RECOMMENDATIONS = {
 "Entrega e logística":"Auditar prazo prometido versus rastreamento; segmentar por transportadora, rota e região.",
 "Qualidade / defeito do produto":"Investigar SKU, lote e fornecedor; verificar recorrência e reforçar inspeção.",
 "Pedido incompleto / item ausente":"Conferir picking, packing e expedição; cruzar itens e recorrência por operação/seller.",
 "Produto divergente do anúncio":"Comparar SKU recebido com anúncio, descrição e imagens.",
 "Pagamento / estorno":"Conciliar cobrança e estorno; encaminhar divergências ao Financeiro.",
 "Embalagem":"Inspecionar acondicionamento e integridade no transporte.",
 "Atendimento / comunicação":"Revisar histórico de contato, tempo de resposta e SLA."
}
def normalize(text):
    if pd.isna(text): return ""
    s=unicodedata.normalize("NFKD",str(text).lower())
    return "".join(c for c in s if not unicodedata.combining(c))
def analyze_review(row):
    title=row.get("review_comment_title",""); comment=row.get("review_comment_message",row.get("review_text",""))
    raw=(" ".join(str(x) for x in [title,comment] if pd.notna(x))).strip(); txt=normalize(raw)
    score=pd.to_numeric(row.get("review_score",None),errors="coerce"); hits=[]
    for label,patterns in TAXONOMY.items():
        found=[p for p in patterns if re.search(p,txt)]
        if found: hits.append((label,found))
    if not raw: sentiment="Não determinado"; severity="Indeterminada"
    elif score<=2: sentiment="Negativo"; severity="Alta"
    elif score>=4: sentiment="Positivo"; severity="Baixa"
    else: sentiment="Neutro"; severity="Média"
    labels=[x[0] for x in hits]
    if sentiment=="Negativo" and not labels: severity="Média"
    return {"review_id":row.get("review_id",""),"order_id":row.get("order_id",""),"review_score":None if pd.isna(score) else int(score),
      "sentiment":sentiment,"themes":"; ".join(labels) if labels else ("Sem comentário textual" if not raw else "Não classificado lexicalmente"),
      "matched_terms":"; ".join(p for _,ps in hits for p in ps),"severity":severity,"evidence":raw,
      "recommendations":" | ".join(RECOMMENDATIONS[x] for x in labels),
      "human_review_recommended":bool(score<=2 and (not raw or not labels))}
def analyze_dataframe(df): return pd.DataFrame([analyze_review(x) for x in df.to_dict("records")])
def answer_manager_question(df, question=""):
    out=analyze_dataframe(df); neg=out[out.review_score.fillna(9).le(2)]; counts={}
    for labels in neg.themes.fillna(""):
        for label in labels.split("; "):
            if label in TAXONOMY: counts[label]=counts.get(label,0)+1
    top=sorted(counts.items(),key=lambda x:x[1],reverse=True)[:3]
    return {"total_rows":len(df),"negative_reviews":len(neg),"top_lexical_causes":[{"theme":k,"mentions":v,"recommendation":RECOMMENDATIONS[k]} for k,v in top],
      "note":"Triagem lexical multi-rótulo; uma avaliação pode mencionar mais de uma causa. Não equivale a interpretação semântica validada."}
