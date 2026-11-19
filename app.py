import gradio as gr
import pandas as pd
from pathlib import Path
from agent import analyze_dataframe, answer_manager_question
DEMO=Path(__file__).parent/"data"/"olist_real_demo_reviews.csv"
def run_demo():
    df=pd.read_csv(DEMO); out=analyze_dataframe(df); s=answer_manager_question(df)
    text=f"DEMONSTRAÇÃO COM {len(df)} AVALIAÇÕES REAIS DA OLIST\nNotas 1–2: {s['negative_reviews']}\n"
    text+="\n".join(f"• {x['theme']}: {x['mentions']} menções" for x in s["top_lexical_causes"])
    text+="\n\nTriagem lexical multi-rótulo; valide amostras manualmente."
    return text,out
def run_csv(file):
    if file is None: return "Envie um CSV.",pd.DataFrame()
    df=pd.read_csv(file.name); out=analyze_dataframe(df); s=answer_manager_question(df)
    text=f"Registros: {len(df)} | Notas 1–2: {s['negative_reviews']}\n"
    text+="\n".join(f"• {x['theme']}: {x['mentions']}" for x in s["top_lexical_causes"])
    return text,out
with gr.Blocks(title="Olist Intelligent Reviews") as demo:
    gr.Markdown("# Olist Intelligent Reviews\nAgente de triagem lexical auditável baseado em avaliações reais.")
    with gr.Tab("Demonstração com avaliações reais"):
        b=gr.Button("Executar demonstração"); summary=gr.Textbox(lines=5,label="Resumo gerencial"); table=gr.Dataframe(label="Reviews classificadas")
        b.click(run_demo,outputs=[summary,table])
    with gr.Tab("Analisar CSV"):
        f=gr.File(file_types=[".csv"]); go=gr.Button("Analisar lote"); report=gr.Textbox(lines=5); result=gr.Dataframe()
        go.click(run_csv,inputs=f,outputs=[report,result])
demo.launch()
