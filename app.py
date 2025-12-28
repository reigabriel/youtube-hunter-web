import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import os
import requests
import random
import time
from datetime import datetime

# --- Configuração Inicial ---
st.set_page_config(page_title="YouTube Outlier Hunter", layout="wide", page_icon="💎")
ARQUIVO_SALVOS = "canais_salvos.csv"

# --- Funções Auxiliares (CSV e API) ---
def carregar_salvos():
    if not os.path.exists(ARQUIVO_SALVOS):
        return pd.DataFrame(columns=['Nome', 'Inscritos', 'Vídeos', 'Link', 'Data Descoberta'])
    return pd.read_csv(ARQUIVO_SALVOS)

def salvar_canal(dados_canal):
    df = carregar_salvos()
    if dados_canal['Link'] not in df['Link'].values:
        novo_df = pd.DataFrame([dados_canal])
        df = pd.concat([df, novo_df], ignore_index=True)
        df.to_csv(ARQUIVO_SALVOS, index=False)
        return True
    return False

def get_google_suggestions(termo_raiz):
    url = "http://suggestqueries.google.com/complete/search"
    sugestoes = set()
    alfabeto = "abcdefghijklmnopqrstuvwxyz"
    
    # 1. Busca termo puro
    try:
        r = requests.get(url, params={'client': 'firefox', 'ds': 'yt', 'q': termo_raiz})
        if r.status_code == 200:
            [sugestoes.add(item) for item in r.json()[1]]
    except: pass

    # 2. Busca com letras aleatórias (amostragem rápida)
    for letra in random.sample(alfabeto, 3):
        try:
            r = requests.get(url, params={'client': 'firefox', 'ds': 'yt', 'q': f"{termo_raiz} {letra}"})
            if r.status_code == 200:
                [sugestoes.add(item) for item in r.json()[1]]
            time.sleep(0.1)
        except: pass
    return list(sugestoes)

# --- Função Principal de Busca (Com Paginação) ---
def executar_busca(api_key, query, max_results, duration, min_subs, max_videos, usar_proxima_pagina=False):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Lógica de Paginação
        token = st.session_state['next_page_token'] if usar_proxima_pagina else None
        
        st.session_state['quota_usada'] += 100
        
        search_params = {
            'q': query,
            'part': 'snippet',
            'type': 'video',
            'maxResults': max_results,
            'order': 'date',
            'pageToken': token 
        }
        if duration: search_params['videoDuration'] = duration

        request = youtube.search().list(**search_params)
        response = request.execute()
        
        # Atualiza o token para a próxima rodada
        st.session_state['next_page_token'] = response.get('nextPageToken')
        st.session_state['termo_atual'] = query # Lembra o termo atual
        
        channel_ids = {item['snippet']['channelId'] for item in response['items']}
        
        if not channel_ids: return []

        st.session_state['quota_usada'] += 1 
        request_channels = youtube.channels().list(
            id=','.join(list(channel_ids)),
            part='snippet,statistics'
        )
        channels_response = request_channels.execute()
        
        novos = []
        for channel in channels_response['items']:
            stats = channel['statistics']
            subs = int(stats.get('subscriberCount', 0)) if not stats.get('hiddenSubscriberCount') else 0
            vids = int(stats.get('videoCount', 0))
            
            if subs >= min_subs and vids <= max_videos:
                novos.append({
                    'Nome': channel['snippet']['title'],
                    'Inscritos': subs,
                    'Vídeos': vids,
                    'Link': f"https://www.youtube.com/channel/{channel['id']}",
                    'Data Descoberta': datetime.now().strftime("%Y-%m-%d"),
                    'Thumb': channel['snippet']['thumbnails']['default']['url']
                })
        return novos
    except Exception as e:
        st.error(f"Erro na API: {e}")
        return []

# --- Inicialização de Estado ---
keys_padrao = ['quota_usada', 'resultados_busca', 'next_page_token', 'termo_atual', 'sugestoes_cache']
for key in keys_padrao:
    if key not in st.session_state:
        if key == 'resultados_busca': st.session_state[key] = []
        elif key == 'next_page_token': st.session_state[key] = None
        elif key == 'quota_usada': st.session_state[key] = 0
        else: st.session_state[key] = None

# --- Interface ---
st.title("💎 YouTube Outlier Hunter V5")

with st.sidebar:
    st.header("⚙️ Configuração")
    api_key = st.text_input("API Key", type="password")
    st.divider()
    st.metric("Custo Sessão", f"{st.session_state['quota_usada']}")
    st.caption("A busca consome 100 pts. Detalhes consomem 1 pt.")

# Abas
tab_busca, tab_discovery, tab_salvos = st.tabs(["🔍 Busca Manual", "🧠 Descobrir Nichos", "💾 Biblioteca"])

# === ABA 1: BUSCA MANUAL COMPLETA ===
with tab_busca:
    c1, c2 = st.columns([3, 1])
    query = c1.text_input("Palavra-chave", "Marketing Digital")
    duracao = c2.selectbox("Duração", ["Qualquer", "Médio (4-20m)", "Longo (>20m)"], index=1)
    
    # RESTAURADO: Slider e Inputs numéricos
    c3, c4, c5 = st.columns(3)
    min_subs = c3.number_input("Mín. Inscritos", 1000)
    max_videos = c4.number_input("Máx. Vídeos", 30)
    max_results = c5.slider("Vídeos analisados por busca", 10, 50, 50, help="Mais vídeos = mais cota gasta, mas mais chance de achar canais.")

    mapa_dur = {"Qualquer": None, "Médio (4-20m)": "medium", "Longo (>20m)": "long"}
    
    # Botões de Ação
    col_b1, col_b2 = st.columns([1, 4])
    
    # Botão 1: Nova Busca
    if col_b1.button("🔍 Buscar", type="primary"):
        if api_key:
            st.session_state['resultados_busca'] = [] # Limpa anterior
            st.session_state['next_page_token'] = None # Reseta paginação
            res = executar_busca(api_key, query, max_results, mapa_dur[duracao], min_subs, max_videos, usar_proxima_pagina=False)
            st.session_state['resultados_busca'] = res
        else: st.warning("Insira a API Key na barra lateral.")

    # Botão 2: RESTAURADO - Carregar Mais
    if st.session_state['next_page_token'] and st.session_state['termo_atual']:
        if col_b2.button(f"🔄 Carregar mais resultados para '{st.session_state['termo_atual']}'"):
             res = executar_busca(api_key, st.session_state['termo_atual'], max_results, mapa_dur[duracao], min_subs, max_videos, usar_proxima_pagina=True)
             st.session_state['resultados_busca'].extend(res) # Adiciona ao fim da lista
             if not res: st.toast("Nenhum canal novo nesta página.")

    # Exibição de Resultados
    if st.session_state['resultados_busca']:
        st.divider()
        st.subheader(f"Encontrados: {len(st.session_state['resultados_busca'])}")
        
        for i, canal in enumerate(st.session_state['resultados_busca']):
            with st.container(border=True):
                col_img, col_txt, col_btn = st.columns([1, 5, 1])
                col_img.image(canal['Thumb'], width=60)
                col_txt.markdown(f"**[{canal['Nome']}]({canal['Link']})**")
                col_txt.caption(f"Subs: {canal['Inscritos']} | Vídeos: {canal['Vídeos']} | Descoberto: {canal['Data Descoberta']}")
                if col_btn.button("Salvar", key=f"btn_{i}_{canal['Link']}"):
                    if salvar_canal(canal): st.toast("Salvo!")
                    else: st.toast("Já existe.")

# === ABA 2: DESCOBERTA ===
with tab_discovery:
    st.markdown("### ⛏️ Gerador de Ideias")
    root_term = st.text_input("Digite um tema raiz (ex: 'Fitness', 'ASMR')")
    
    if st.button("Minerar Sub-Nichos"):
        with st.spinner("Buscando sugestões..."):
            st.session_state['sugestoes_cache'] = get_google_suggestions(root_term)
    
    if st.session_state.get('sugestoes_cache'):
        st.divider()
        st.write("Clique em um nicho para buscar canais nele:")
        cols = st.columns(3)
        for idx, sugestao in enumerate(st.session_state['sugestoes_cache']):
            if cols[idx % 3].button(f"🔎 {sugestoes}", key=f"sug_{idx}"):
                if api_key:
                    # Inicia uma busca nova na Aba 1 automaticamente
                    st.session_state['resultados_busca'] = []
                    st.session_state['next_page_token'] = None
                    # Usa os parâmetros da Aba 1 (Subs, Videos, Duração)
                    res = executar_busca(api_key, sugestao, 50, "medium", min_subs, max_videos)
                    st.session_state['resultados_busca'] = res
                    st.success(f"Busca por '{sugestao}' realizada! Vá para a aba 'Busca Manual' ver os resultados.")
                else: st.error("Falta a API Key!")

    st.divider()
    if st.button("🎲 Tentar Nicho Aleatório"):
        termo = random.choice(["Como fazer", "Guia completo", "Review honesto", "Vlog de viagem", "Setup gaming"])
        if api_key:
            st.session_state['resultados_busca'] = []
            st.session_state['next_page_token'] = None
            res = executar_busca(api_key, termo, 50, "medium", min_subs, max_videos)
            st.session_state['resultados_busca'] = res
            st.success(f"Busca aleatória ('{termo}') feita! Confira na aba 'Busca Manual'.")

# === ABA 3: SALVOS ===
with tab_salvos:
    df = carregar_salvos()
    if not df.empty:
        st.data_editor(df, column_config={"Link": st.column_config.LinkColumn()}, hide_index=True, use_container_width=True)
        st.download_button("Baixar CSV", df.to_csv(index=False).encode('utf-8'), "outliers.csv", "text/csv")
        if st.button("🗑️ Limpar tudo"):
            os.remove(ARQUIVO_SALVOS)
            st.rerun()
    else: st.info("Sua biblioteca está vazia.")
