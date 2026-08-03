"""
Conversor para Markdown — SisConnect (Web)
Converte DOCX, PDF, XLSX, PPTX, HTML, CSV e outros formatos para .md
Roda 100% no navegador. Nenhum dado é salvo no servidor.
"""

import os
import tempfile
import streamlit as st
from pathlib import Path
from markitdown import MarkItDown

# Extensões suportadas
EXTENSOES_SUPORTADAS = [
    "docx", "doc", "pdf", "xlsx", "xls", "pptx", "ppt",
    "html", "htm", "csv", "json", "xml", "txt", "epub",
    "msg", "rtf", "odt"
]

# Configuração da página
st.set_page_config(
    page_title="Conversor para Markdown — SisConnect",
    page_icon="📄",
    layout="centered"
)

# ============================================================
# UI
# ============================================================

st.title("📄 Conversor para Markdown — SisConnect")
st.markdown("""
Converte **DOCX, PDF, XLSX, PPTX, HTML, CSV** e outros formatos para **.md**

""")

st.divider()

# ============================================================
# Upload dos arquivos
# ============================================================

arquivos = st.file_uploader(
    "Escolha os arquivos para converter",
    type=EXTENSOES_SUPORTADAS,
    accept_multiple_files=True,
    help="Você pode selecionar vários arquivos de uma vez"
)

# ============================================================
# Opções
# ============================================================

col1, col2 = st.columns(2)

with col1:
    converter = st.button("🔄 CONVERTER", use_container_width=True, type="primary")

with col2:
    limpar = st.button("🗑️ Limpar lista", use_container_width=True)

if limpar:
    st.rerun()

# ============================================================
# Barra de progresso
# ============================================================

progresso = st.progress(0, text="Aguardando...")
status_texto = st.empty()

# ============================================================
# Lógica de conversão
# ============================================================

def converter_arquivo(arquivo, md):
    """Converte um único arquivo e retorna o conteúdo Markdown"""
    try:
        # Salva o arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{arquivo.name.split('.')[-1]}") as tmp:
            tmp.write(arquivo.getbuffer())
            tmp_path = tmp.name
        
        # Converte
        resultado = md.convert(tmp_path)
        
        # Remove o arquivo temporário
        os.unlink(tmp_path)
        
        return True, resultado.text_content, None
    except Exception as e:
        return False, None, str(e)

# ============================================================
# Execução da conversão
# ============================================================

if converter:
    if not arquivos:
        st.error("❌ Selecione pelo menos um arquivo para converter!")
    else:
        # Inicializa o MarkItDown
        md = MarkItDown()
        
        total = len(arquivos)
        sucesso = 0
        falha = 0
        resultados = []
        
        # Atualiza a barra de progresso
        progresso.progress(0, text=f"Iniciando conversão de {total} arquivo(s)...")
        
        for i, arquivo in enumerate(arquivos):
            progresso.progress(
                (i) / total, 
                text=f"Convertendo {arquivo.name}... ({i+1}/{total})"
            )
            
            ok, conteudo, erro = converter_arquivo(arquivo, md)
            
            if ok:
                sucesso += 1
                resultados.append({
                    "nome": arquivo.name,
                    "conteudo": conteudo,
                    "status": "✅ OK"
                })
            else:
                falha += 1
                resultados.append({
                    "nome": arquivo.name,
                    "conteudo": None,
                    "status": f"❌ Erro: {erro[:100]}"
                })
        
        progresso.progress(1.0, text="✅ Conversão finalizada!")
        
        # ============================================================
        # Exibe os resultados
        # ============================================================
        
        st.divider()
        st.subheader(f"📊 Resultado: {sucesso} convertido(s), {falha} com erro")
        
        for res in resultados:
            with st.expander(f"{res['status']} — {res['nome']}"):
                if res["conteudo"]:
                    st.text_area("Conteúdo Markdown:", res["conteudo"], height=200)
                    st.download_button(
                        label=f"📥 Baixar {res['nome']}.md",
                        data=res["conteudo"],
                        file_name=f"{res['nome']}.md",
                        mime="text/markdown",
                        key=f"download_{res['nome']}"
                    )
                else:
                    st.error(res["status"])
        
        # Botão para limpar e recomeçar
        if st.button("🔄 Converter mais arquivos", use_container_width=True):
            st.rerun()

# ============================================================
# Rodapé
# ============================================================

st.divider()
st.caption("SisConnect — Conversor para Markdown • 100% local e gratuito")
