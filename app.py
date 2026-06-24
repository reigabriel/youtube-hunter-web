import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import os
import requests
import random
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Outlier Hunter Pro", layout="wide", page_icon="🎯")
ARQUIVO_SALVOS = "canais_salvos.csv"

# --- INJEÇÃO DE CSS CUSTOMIZADO (O "SaaS Look") ---
def aplicar_estilo_saas():
    st.markdown("""
    <style>
        /* Esconder a marca do Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Ajuste do topo para compensar o header escondido */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            max-width: 1200px;
        }

        /* Estilizar os botões (Efeito Hover) */
        .stButton>button {
            border-radius: 8px !important;
            transition: all 0.3s ease;
            font-weight: 500 !important;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        }

        /* Melhorar as métricas */
        [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            color: #1E88E5 !important;
        }

        /* Suavizar bordas das caixas (Containers e Expanders) */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {
            border-radius: 12px !important;
            border: 1px solid #E0E0E0 !important;
            background-color: #FFFFFF !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
            padding: 1rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

aplicar_estilo_saas()

# --- FUNÇÕES DE BANCO DE DADOS (CSV) ---
def carregar_salvos():
    colunas = ['Nome', 'Inscritos', 'Vídeos', 'Média Views', 'País', 'Criação', 'Dias Vida', 'Link', 'Data Descoberta']
    if not os.path.exists(ARQUIVO_SALVOS):
        return pd.DataFrame(columns=colunas)
    return pd.read_csv(ARQUIVO_SALVOS)

def salvar_canal(dados_canal):
    df = carregar_salvos()
    if dados_canal['Link'] not in df['Link'].values:
        linha_limpa = {k: v for k, v in dados_canal.items() if k in df.columns}
        novo_df = pd.DataFrame([linha_limpa])
        df = pd.concat([df, novo_df], ignore_index=True)
        df.to_csv(ARQUIVO_SALVOS, index=False)
        return True
    return False

# --- FUNÇÃO DE INTELIGÊNCIA ---
def get_google_suggestions(termo_raiz):
    url = "http://suggestqueries.google.com/complete/search"
    sugestoes = set()
    alfabeto = "abcdefghijklmnopqrstuvwxyz"
    try:
        r = requests.get(url, params={'client': 'firefox', 'ds': 'yt', 'q': termo_raiz})
        if r.status_code == 200: [sugestoes.add(item) for item in r.json()[1]]
    except: pass
    for letra in random.sample(alfabeto, 3):
        try:
            r = requests.get(url, params={'client': 'firefox', 'ds': 'yt', 'q': f"{termo_raiz} {letra}"})
            if r.status_code == 200: [sugestoes.add(item) for item in r.json()[1]]
            time.sleep(0.1)
        except: pass
    return list(sugestoes)

# --- MOTOR DE BUSCA (CORE) ---
def executar_busca(api_key, query, max_results, duration, min_subs, max_subs, min_videos, max_videos, region_code, usar_proxima_pagina=False):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        token = st.session_state['next_page_token'] if usar_proxima_pagina else None
        
        st.session_state['quota_usada'] += 100
        search_params = {
            'q': query, 'part': 'snippet', 'type': 'video',
            'maxResults': max_results, 'order': 'date', 'pageToken': token,
            'regionCode': region_code
        }
        if duration: search_params['videoDuration'] = duration

        request = youtube.search().list(**search_params)
        response = request.execute()
        
        st.session_state['next_page_token'] = response.get('nextPageToken')
        st.session_state['termo_atual'] = query
        
        channel_ids = {item['snippet']['channelId'] for item in response['items']}
        if not channel_ids: return []

        st.session_state['quota_usada'] += 1 
        request_channels = youtube.channels().list(
            id=','.join(list(channel_ids)), part='snippet,statistics'
        )
        channels_response = request_channels.execute()
        
        novos = []
        for channel in channels_response['items']:
            stats = channel['statistics']
            snippet = channel['snippet']
            
            subs = int(stats.get('subscriberCount', 0)) if not stats.get('hiddenSubscriberCount') else 0
            vids = int(stats.get('videoCount', 0))
            views_total = int(stats.get('viewCount', 0))
            pais = snippet.get('country', 'N/A')
            
            try:
                raw_date = snippet['publishedAt']
                data_criacao_obj = datetime.strptime(raw_date[:10], "%Y-%m-%d")
                data_formatada = data_criacao_obj.strftime("%d/%m/%Y")
                dias_de_vida = (datetime.now() - data_criacao_obj).days
            except:
                data_formatada, dias_de_vida = "Desconhecida", 9999

            if (min_subs <= subs <= max_subs) and (min_videos <= vids <= max_videos):
                media_views = int(views_total / vids) if vids > 0 else 0
                novos.append({
                    'Nome': snippet['title'], 'Inscritos': subs, 'Vídeos': vids,
                    'Total Views': views_total, 'Média Views': media_views, 'País': pais,
                    'Criação': data_formatada, 'Dias Vida': dias_de_vida,
                    'Link': f"https://www.youtube.com/channel/{channel['id']}",
                    'Data Descoberta': datetime.now().strftime("%Y-%m-%d"),
                    'Thumb': snippet['thumbnails']['default']['url'],
                    'Desc': snippet.get('description', '')[:100] + "..."
                })
        return novos
    except Exception as e:
        st.error(f"Erro na API: {e}")
        return []

# --- ESTADO ---
for v in ['quota_usada', 'resultados_busca', 'next_page_token', 'termo_atual', 'sugestoes_cache']:
    if v not in st.session_state:
        st.session_state[v] = [] if v == 'resultados_busca' else (None if v == 'next_page_token' else 0)

# ================= INTERFACE GRÁFICA =================

# --- DASHBOARD HEADER ---
st.markdown("## 🎯 Outlier Hunter Pro")

df_atual = carregar_salvos()
total_salvos = len(df_atual)

# Métricas Top-Level (Design de SaaS)
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("Canais na Biblioteca", total_salvos)
with col_m2:
    st.metric("Custo da Sessão (API)", st.session_state['quota_usada'])
with col_m3:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.metric("Status do Sistema", "Online 🟢")
    else:
        st.metric("Status do Sistema", "Configurar 🔴")

st.divider()

# --- BARRA LATERAL (Apenas Configurações) ---
with st.sidebar:
    st.header("⚙️ Settings")
    if "GOOGLE_API_KEY" not in st.secrets:
        api_key = st.text_input("YouTube API Key", type="password")
    
    region = st.selectbox("Região Alvo", ["Qualquer", "BR", "US", "PT"], index=0)
    region_param = None if region == "Qualquer" else region
    st.caption("Ajuste a região para filtrar canais estrangeiros.")

# --- ABAS PRINCIPAIS ---
tab_busca, tab_discovery, tab_salvos = st.tabs(["🔍 Motor de Busca", "🧠 Inteligência de Nicho", "💾 Biblioteca de Leads"])

# === ABA 1: BUSCA ===
with tab_busca:
    
    # Bloco de Busca (Destacado)
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        query = c1.text_input("Palavra-chave ou Nicho", "Marketing Digital", placeholder="Ex: Finanças, Roblox, Receitas...")
        duracao = c2.selectbox("Formato", ["Qualquer", "Vídeo Médio (4-20m)", "Vídeo Longo (>20m)"], index=1)
        
        # Progressive Disclosure: Filtros complexos escondidos
        with st.expander("🛠️ Filtros Avançados de Tamanho (Opcional)"):
            col_sub1, col_sub2, col_vid1, col_vid2 = st.columns(4)
            min_subs = col_sub1.number_input("Mín. Inscritos", value=1000, step=100)
            max_subs = col_sub2.number_input("Máx. Inscritos", value=10000000, step=1000)
            min_videos = col_vid1.number_input("Mín. Vídeos", value=1, step=1)
            max_videos = col_vid2.number_input("Máx. Vídeos", value=50, step=1)
            max_results = st.slider("Velocidade da Busca (Vídeos por varredura)", 10, 50, 50)
            
        mapa_dur = {"Qualquer": None, "Vídeo Médio (4-20m)": "medium", "Vídeo Longo (>20m)": "long"}
        
        # Botões
        col_btn1, col_btn2 = st.columns([1, 2])
        if col_btn1.button("🔍 Iniciar Varredura", type="primary", use_container_width=True):
            if api_key:
                with st.spinner("Analisando o YouTube..."):
                    st.session_state['resultados_busca'] = []
                    st.session_state['next_page_token'] = None
                    res = executar_busca(api_key, query, max_results, mapa_dur[duracao], min_subs, max_subs, min_videos, max_videos, region_param, False)
                    st.session_state['resultados_busca'] = res
                    if not res: st.warning("Nenhum canal atendeu aos seus filtros super restritos.")
            else: st.error("Configure sua API Key nas Settings (Barra Lateral).")

        if st.session_state['termo_atual']:
            if st.session_state['next_page_token']:
                if col_btn2.button(f"🔄 Aprofundar busca para '{st.session_state['termo_atual']}'", use_container_width=True):
                    with st.spinner("Cavando mais fundo..."):
                        res = executar_busca(api_key, st.session_state['termo_atual'], max_results, mapa_dur[duracao], min_subs, max_subs, min_videos, max_videos, region_param, True)
                        links_existentes = {c['Link'] for c in st.session_state['resultados_busca']}
                        novos = [c for c in res if c['Link'] not in links_existentes]
                        st.session_state['resultados_busca'].extend(novos)
                        if novos: st.toast(f"✅ {len(novos)} novos canais adicionados!")
                        else: st.toast("Nenhum canal novo nesta página.")
            else:
                col_btn2.info("🏁 Varredura completa para este termo.")

    # Exibição dos Resultados (Cards Limpos)
    if st.session_state['resultados_busca']:
        st.markdown(f"### 📋 Resultados Encontrados ({len(st.session_state['resultados_busca'])})")
        
        for i, canal in enumerate(st.session_state['resultados_busca']):
            with st.container(border=True):
                col_img, col_info, col_metrics, col_btn = st.columns([1, 4, 2, 1], gap="medium")
                
                col_img.image(canal['Thumb'], width=80)
                
                with col_info:
                    st.markdown(f"**[{canal['Nome']}]({canal['Link']})**")
                    if canal['Dias Vida'] < 90: st.caption(f"🚀 **Promessa:** {canal['Dias Vida']} dias de vida")
                    else: st.caption(f"📅 Ativo há {canal['Dias Vida']} dias")
                    st.caption(f"📍 Região: {canal['País']}")
                
                with col_metrics:
                    is_viral = canal['Média Views'] > canal['Inscritos']
                    cor = "green" if is_viral else "normal"
                    st.markdown(f"👤 **{canal['Inscritos']}** subs")
                    st.markdown(f"🎥 **{canal['Vídeos']}** vídeos")
                    st.markdown(f"📈 Média: :{cor}[**{canal['Média Views']}**] {'🔥' if is_viral else ''}")
                
                with col_btn:
                    st.markdown("<br>", unsafe_allow_html=True) # Espaçador
                    if st.button("Salvar", key=f"s_{i}_{canal['Link']}", use_container_width=True):
                        if salvar_canal(canal): st.toast("Canal salvo na Biblioteca!")
                        else: st.toast("Canal já estava salvo.")

# === ABA 2: DESCOBERTA ===
with tab_discovery:
    with st.container(border=True):
        st.markdown("#### ⛏️ Descobridor de Sub-Nichos")
        st.write("Digite um nicho amplo e nós encontraremos o que o algoritmo do YouTube está sugerindo agora.")
        termo = st.text_input("Tema Raiz", placeholder="Ex: Emagrecimento, Python, Investimentos...")
        if st.button("Gerar Mapa de Nichos", type="primary"): 
            with st.spinner("Analisando tendências de busca..."):
                st.session_state['sugestoes_cache'] = get_google_suggestions(termo)
        
        if st.session_state.get('sugestoes_cache'):
            st.divider()
            st.write("**Oportunidades encontradas (Clique para investigar):**")
            cols = st.columns(3)
            for i, sug in enumerate(st.session_state['sugestoes_cache']):
                if cols[i%3].button(f"🔍 {sug}", key=f"nicho_{i}", use_container_width=True):
                    if api_key:
                        st.session_state['resultados_busca'] = []
                        st.session_state['next_page_token'] = None
                        res = executar_busca(api_key, sug, 50, "medium", min_subs, max_subs, min_videos, max_videos, region_param, False)
                        st.session_state['resultados_busca'] = res
                        st.success("Busca concluída! Volte para a aba 'Motor de Busca' para ver os resultados.")

# === ABA 3: BIBLIOTECA ===
with tab_salvos:
    df = carregar_salvos()
    if not df.empty:
        st.markdown("#### 📁 Sua Base de Leads (Outliers)")
        st.data_editor(df, column_config={"Link": st.column_config.LinkColumn()}, hide_index=True, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.download_button("📥 Exportar para Excel/CSV", df.to_csv(index=False).encode('utf-8'), "outliers_leads.csv", "text/csv", use_container_width=True)
        if c2.button("🗑️ Limpar Banco de Dados", use_container_width=True):
            os.remove(ARQUIVO_SALVOS)
            st.rerun()
    else: 
        st.info("Sua biblioteca está vazia. Comece a salvar canais na aba de Busca!")
