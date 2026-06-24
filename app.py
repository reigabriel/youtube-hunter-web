import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import os
import requests
import random
import time
from datetime import datetime

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Outlier Hunter Pro",
    layout="wide",
    page_icon="🎯"
)

ARQUIVO_SALVOS = "canais_salvos.csv"


# ============================================================
# CSS CUSTOMIZADO - VISUAL MODERNO / SAAS
# ============================================================

def aplicar_estilo_saas():
    st.markdown("""
    <style>
        /* Esconder marcações padrão do Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Fundo geral */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #f7f8fb;
        }

        /* Área principal */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
            max-width: 1280px;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f1f4f9 0%, #ffffff 100%);
            border-right: 1px solid #e5e7eb;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #111827;
        }

        /* Título principal */
        .main-title {
            font-size: 2.5rem;
            font-weight: 850;
            letter-spacing: -0.04em;
            color: #111827;
            margin-bottom: 0.2rem;
        }

        .subtitle {
            color: #6b7280;
            font-size: 1rem;
            margin-bottom: 2rem;
        }

        /* Cards de métricas */
        .metric-card {
            background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
            border: 1px solid #e5e7eb;
            border-radius: 22px;
            padding: 24px;
            box-shadow: 0 14px 35px rgba(15, 23, 42, 0.06);
            min-height: 130px;
        }

        .metric-label {
            color: #6b7280;
            font-size: 0.92rem;
            font-weight: 650;
            margin-bottom: 8px;
        }

        .metric-value {
            color: #111827;
            font-size: 2.15rem;
            line-height: 1.1;
            font-weight: 850;
            letter-spacing: -0.04em;
        }

        .metric-helper {
            margin-top: 10px;
            color: #9ca3af;
            font-size: 0.82rem;
        }

        /* Caixa principal de busca */
        .search-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 24px;
            padding: 26px;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
            margin-bottom: 1rem;
        }

        .section-title {
            font-size: 1.2rem;
            font-weight: 800;
            color: #111827;
            margin-bottom: 0.35rem;
        }

        .section-caption {
            color: #6b7280;
            font-size: 0.95rem;
            margin-bottom: 1.2rem;
        }

        /* Botões */
        .stButton > button {
            border-radius: 12px !important;
            font-weight: 700 !important;
            min-height: 44px;
            transition: all 0.22s ease-in-out;
            border: 1px solid #e5e7eb;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.12) !important;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #ff4b4b 0%, #ef4444 100%) !important;
            border: none !important;
            color: white !important;
        }

        /* Inputs */
        .stTextInput input,
        .stNumberInput input,
        .stSelectbox div[data-baseweb="select"] > div {
            border-radius: 12px !important;
        }

        /* Tabs modernas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            border-bottom: none;
            margin-bottom: 1rem;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: #eef1f6;
            border-radius: 999px;
            padding: 10px 18px;
            color: #374151;
            font-weight: 700;
        }

        .stTabs [aria-selected="true"] {
            background: #111827 !important;
            color: #ffffff !important;
        }

        .stTabs [data-baseweb="tab-highlight"] {
            display: none;
        }

        /* Containers com borda do Streamlit */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {
            border-radius: 22px !important;
            border: 1px solid #e5e7eb !important;
            background-color: #ffffff !important;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05) !important;
            padding: 1.1rem !important;
        }

        /* Expander */
        details {
            border-radius: 14px !important;
            border: 1px solid #e5e7eb !important;
            background-color: #f9fafb !important;
        }

        /* Dataframe / Data editor */
        [data-testid="stDataFrame"] {
            border-radius: 18px;
            overflow: hidden;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
        }

        /* Cards de resultado */
        .result-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 22px;
            padding: 18px;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
            margin-bottom: 14px;
        }

        .channel-title {
            font-size: 1.05rem;
            font-weight: 800;
            margin-bottom: 0.15rem;
        }

        .muted-text {
            color: #6b7280;
            font-size: 0.88rem;
        }

        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 750;
            background-color: #eef2ff;
            color: #3730a3;
            margin-top: 6px;
        }

        .badge-green {
            background-color: #ecfdf5;
            color: #047857;
        }

        .badge-red {
            background-color: #fef2f2;
            color: #b91c1c;
        }

        /* Separador */
        hr {
            border: none;
            border-top: 1px solid #e5e7eb;
            margin: 1.5rem 0;
        }
    </style>
    """, unsafe_allow_html=True)


aplicar_estilo_saas()


# ============================================================
# FUNÇÕES DE BANCO DE DADOS CSV
# ============================================================

def carregar_salvos():
    colunas = [
        'Nome',
        'Inscritos',
        'Vídeos',
        'Média Views',
        'País',
        'Criação',
        'Dias Vida',
        'Link',
        'Data Descoberta'
    ]

    if not os.path.exists(ARQUIVO_SALVOS):
        return pd.DataFrame(columns=colunas)

    return pd.read_csv(ARQUIVO_SALVOS)


def salvar_canal(dados_canal):
    df = carregar_salvos()

    if dados_canal['Link'] not in df['Link'].values:
        linha_limpa = {
            k: v for k, v in dados_canal.items()
            if k in df.columns
        }

        novo_df = pd.DataFrame([linha_limpa])
        df = pd.concat([df, novo_df], ignore_index=True)
        df.to_csv(ARQUIVO_SALVOS, index=False)

        return True

    return False


# ============================================================
# FUNÇÃO DE INTELIGÊNCIA DE NICHO
# ============================================================

def get_google_suggestions(termo_raiz):
    url = "http://suggestqueries.google.com/complete/search"
    sugestoes = set()
    alfabeto = "abcdefghijklmnopqrstuvwxyz"

    if not termo_raiz:
        return []

    try:
        r = requests.get(
            url,
            params={
                'client': 'firefox',
                'ds': 'yt',
                'q': termo_raiz
            },
            timeout=10
        )

        if r.status_code == 200:
            for item in r.json()[1]:
                sugestoes.add(item)

    except Exception:
        pass

    for letra in random.sample(alfabeto, 3):
        try:
            r = requests.get(
                url,
                params={
                    'client': 'firefox',
                    'ds': 'yt',
                    'q': f"{termo_raiz} {letra}"
                },
                timeout=10
            )

            if r.status_code == 200:
                for item in r.json()[1]:
                    sugestoes.add(item)

            time.sleep(0.1)

        except Exception:
            pass

    return list(sugestoes)


# ============================================================
# MOTOR DE BUSCA YOUTUBE
# ============================================================

def executar_busca(
    api_key,
    query,
    max_results,
    duration,
    min_subs,
    max_subs,
    min_videos,
    max_videos,
    region_code,
    usar_proxima_pagina=False
):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)

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

        if region_code:
            search_params['regionCode'] = region_code

        if duration:
            search_params['videoDuration'] = duration

        request = youtube.search().list(**search_params)
        response = request.execute()

        st.session_state['next_page_token'] = response.get('nextPageToken')
        st.session_state['termo_atual'] = query

        channel_ids = {
            item['snippet']['channelId']
            for item in response.get('items', [])
        }

        if not channel_ids:
            return []

        st.session_state['quota_usada'] += 1

        request_channels = youtube.channels().list(
            id=','.join(list(channel_ids)),
            part='snippet,statistics'
        )

        channels_response = request_channels.execute()

        novos = []

        for channel in channels_response.get('items', []):
            stats = channel.get('statistics', {})
            snippet = channel.get('snippet', {})

            subs = int(stats.get('subscriberCount', 0)) if not stats.get('hiddenSubscriberCount') else 0
            vids = int(stats.get('videoCount', 0))
            views_total = int(stats.get('viewCount', 0))
            pais = snippet.get('country', 'N/A')

            try:
                raw_date = snippet['publishedAt']
                data_criacao_obj = datetime.strptime(raw_date[:10], "%Y-%m-%d")
                data_formatada = data_criacao_obj.strftime("%d/%m/%Y")
                dias_de_vida = (datetime.now() - data_criacao_obj).days

            except Exception:
                data_formatada = "Desconhecida"
                dias_de_vida = 9999

            if min_subs <= subs <= max_subs and min_videos <= vids <= max_videos:
                media_views = int(views_total / vids) if vids > 0 else 0

                novos.append({
                    'Nome': snippet.get('title', 'Canal sem nome'),
                    'Inscritos': subs,
                    'Vídeos': vids,
                    'Total Views': views_total,
                    'Média Views': media_views,
                    'País': pais,
                    'Criação': data_formatada,
                    'Dias Vida': dias_de_vida,
                    'Link': f"https://www.youtube.com/channel/{channel['id']}",
                    'Data Descoberta': datetime.now().strftime("%Y-%m-%d"),
                    'Thumb': snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
                    'Desc': snippet.get('description', '')[:100] + "..."
                })

        return novos

    except Exception as e:
        st.error(f"Erro na API: {e}")
        return []


# ============================================================
# HELPERS DE INTERFACE
# ============================================================

def formatar_numero(valor):
    try:
        valor = int(valor)

        if valor >= 1_000_000:
            return f"{valor / 1_000_000:.1f}M"

        if valor >= 1_000:
            return f"{valor / 1_000:.1f}K"

        return str(valor)

    except Exception:
        return str(valor)


def metric_card(label, value, helper="", emoji=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{emoji} {label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-helper">{helper}</div>
    </div>
    """, unsafe_allow_html=True)


def section_header(title, caption):
    st.markdown(f"""
    <div class="section-title">{title}</div>
    <div class="section-caption">{caption}</div>
    """, unsafe_allow_html=True)


# ============================================================
# ESTADO DA SESSÃO
# ============================================================

valores_iniciais = {
    'quota_usada': 0,
    'resultados_busca': [],
    'next_page_token': None,
    'termo_atual': "",
    'sugestoes_cache': []
}

for chave, valor in valores_iniciais.items():
    if chave not in st.session_state:
        st.session_state[chave] = valor


# ============================================================
# HEADER DO DASHBOARD
# ============================================================

st.markdown("""
<div class="main-title">🎯 Outlier Hunter Pro</div>
<div class="subtitle">
    Descubra canais pequenos com performance fora da curva no YouTube.
</div>
""", unsafe_allow_html=True)

df_atual = carregar_salvos()
total_salvos = len(df_atual)

if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    status_sistema = "Online"
    status_helper = "API configurada"
    status_emoji = "🟢"
else:
    api_key = None
    status_sistema = "Configurar"
    status_helper = "Adicione sua API Key"
    status_emoji = "🔴"

col_m1, col_m2, col_m3 = st.columns(3)

with col_m1:
    metric_card(
        label="Canais na Biblioteca",
        value=total_salvos,
        helper="Leads salvos no banco local",
        emoji="📁"
    )

with col_m2:
    metric_card(
        label="Custo da Sessão API",
        value=st.session_state['quota_usada'],
        helper="Estimativa de unidades usadas",
        emoji="⚡"
    )

with col_m3:
    metric_card(
        label="Status do Sistema",
        value=f"{status_sistema} {status_emoji}",
        helper=status_helper,
        emoji="🧩"
    )

st.markdown("<hr>", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.caption("Configure a API e os filtros globais da busca.")

    st.markdown("---")

    if "GOOGLE_API_KEY" not in st.secrets:
        api_key_digitada = st.text_input(
            "YouTube API Key",
            type="password",
            placeholder="Cole sua chave aqui"
        )

        if api_key_digitada:
            api_key = api_key_digitada

    region = st.selectbox(
        "Região Alvo",
        ["Qualquer", "BR", "US", "PT"],
        index=0
    )

    region_param = None if region == "Qualquer" else region

    st.caption("Use a região para priorizar canais de um país específico.")

    st.markdown("---")

    st.info(
        "Dica: filtros muito restritos podem retornar poucos canais. "
        "Comece amplo e depois refine."
    )


# ============================================================
# ABAS PRINCIPAIS
# ============================================================

tab_busca, tab_discovery, tab_salvos = st.tabs([
    "🔍 Motor de Busca",
    "🧠 Inteligência de Nicho",
    "💾 Biblioteca de Leads"
])


# ============================================================
# ABA 1 - MOTOR DE BUSCA
# ============================================================

with tab_busca:
    section_header(
        "Motor de Busca",
        "Encontre canais recentes e filtre por tamanho, formato e potencial de outlier."
    )

    with st.container(border=True):
        c1, c2 = st.columns([3, 1])

        query = c1.text_input(
            "Palavra-chave ou Nicho",
            "Marketing Digital",
            placeholder="Ex: Finanças, Roblox, Receitas..."
        )

        duracao = c2.selectbox(
            "Formato",
            ["Qualquer", "Vídeo Médio (4-20m)", "Vídeo Longo (>20m)"],
            index=1
        )

        with st.expander("🛠️ Filtros Avançados de Tamanho"):
            col_sub1, col_sub2, col_vid1, col_vid2 = st.columns(4)

            min_subs = col_sub1.number_input(
                "Mín. Inscritos",
                value=1000,
                step=100
            )

            max_subs = col_sub2.number_input(
                "Máx. Inscritos",
                value=10000000,
                step=1000
            )

            min_videos = col_vid1.number_input(
                "Mín. Vídeos",
                value=1,
                step=1
            )

            max_videos = col_vid2.number_input(
                "Máx. Vídeos",
                value=50,
                step=1
            )

            max_results = st.slider(
                "Velocidade da Busca",
                10,
                50,
                50,
                help="Quantidade de vídeos analisados por varredura."
            )

        mapa_dur = {
            "Qualquer": None,
            "Vídeo Médio (4-20m)": "medium",
            "Vídeo Longo (>20m)": "long"
        }

        col_btn1, col_btn2 = st.columns([1, 2])

        if col_btn1.button(
            "🔍 Iniciar Varredura",
            type="primary",
            use_container_width=True
        ):
            if api_key:
                with st.spinner("Analisando o YouTube..."):
                    st.session_state['resultados_busca'] = []
                    st.session_state['next_page_token'] = None

                    res = executar_busca(
                        api_key=api_key,
                        query=query,
                        max_results=max_results,
                        duration=mapa_dur[duracao],
                        min_subs=min_subs,
                        max_subs=max_subs,
                        min_videos=min_videos,
                        max_videos=max_videos,
                        region_code=region_param,
                        usar_proxima_pagina=False
                    )

                    st.session_state['resultados_busca'] = res

                    if not res:
                        st.warning("Nenhum canal atendeu aos filtros atuais.")

            else:
                st.error("Configure sua API Key nas Settings da barra lateral.")

        if st.session_state['termo_atual']:
            if st.session_state['next_page_token']:
                if col_btn2.button(
                    f"🔄 Aprofundar busca para '{st.session_state['termo_atual']}'",
                    use_container_width=True
                ):
                    if api_key:
                        with st.spinner("Cavando mais fundo..."):
                            res = executar_busca(
                                api_key=api_key,
                                query=st.session_state['termo_atual'],
                                max_results=max_results,
                                duration=mapa_dur[duracao],
                                min_subs=min_subs,
                                max_subs=max_subs,
                                min_videos=min_videos,
                                max_videos=max_videos,
                                region_code=region_param,
                                usar_proxima_pagina=True
                            )

                            links_existentes = {
                                c['Link']
                                for c in st.session_state['resultados_busca']
                            }

                            novos = [
                                c for c in res
                                if c['Link'] not in links_existentes
                            ]

                            st.session_state['resultados_busca'].extend(novos)

                            if novos:
                                st.toast(f"✅ {len(novos)} novos canais adicionados!")
                            else:
                                st.toast("Nenhum canal novo nesta página.")

                    else:
                        st.error("Configure sua API Key nas Settings da barra lateral.")

            else:
                col_btn2.info("🏁 Varredura completa para este termo.")

    # Resultados
    if st.session_state['resultados_busca']:
        st.markdown(
            f"### 📋 Resultados Encontrados ({len(st.session_state['resultados_busca'])})"
        )

        for i, canal in enumerate(st.session_state['resultados_busca']):
            is_viral = canal['Média Views'] > canal['Inscritos']
            canal_novo = canal['Dias Vida'] < 90

            with st.container(border=True):
                col_img, col_info, col_metrics, col_btn = st.columns(
                    [1, 4, 2, 1],
                    gap="medium"
                )

                with col_img:
                    if canal.get('Thumb'):
                        st.image(canal['Thumb'], width=82)
                    else:
                        st.markdown("🎬")

                with col_info:
                    st.markdown(
                        f"""
                        <div class="channel-title">
                            <a href="{canal['Link']}" target="_blank">
                                {canal['Nome']}
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    if canal_novo:
                        st.markdown(
                            f"""
                            <span class="badge badge-green">
                                🚀 Promessa: {canal['Dias Vida']} dias de vida
                            </span>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"""
                            <span class="badge">
                                📅 Ativo há {canal['Dias Vida']} dias
                            </span>
                            """,
                            unsafe_allow_html=True
                        )

                    st.caption(f"📍 Região: {canal['País']} · Criado em {canal['Criação']}")

                with col_metrics:
                    st.markdown(f"👤 **{formatar_numero(canal['Inscritos'])}** inscritos")
                    st.markdown(f"🎥 **{formatar_numero(canal['Vídeos'])}** vídeos")

                    if is_viral:
                        st.markdown(
                            f"📈 Média: :green[**{formatar_numero(canal['Média Views'])}**] 🔥"
                        )
                    else:
                        st.markdown(
                            f"📈 Média: **{formatar_numero(canal['Média Views'])}**"
                        )

                with col_btn:
                    st.markdown("<br>", unsafe_allow_html=True)

                    if st.button(
                        "Salvar",
                        key=f"s_{i}_{canal['Link']}",
                        use_container_width=True
                    ):
                        if salvar_canal(canal):
                            st.toast("Canal salvo na Biblioteca!")
                        else:
                            st.toast("Canal já estava salvo.")


# ============================================================
# ABA 2 - INTELIGÊNCIA DE NICHO
# ============================================================

with tab_discovery:
    section_header(
        "Inteligência de Nicho",
        "Descubra variações e subnichos sugeridos pelo comportamento de busca do YouTube."
    )

    with st.container(border=True):
        st.markdown("#### ⛏️ Descobridor de Sub-Nichos")

        st.write(
            "Digite um nicho amplo e o app encontrará sugestões relacionadas "
            "que podem revelar oportunidades de conteúdo."
        )

        termo = st.text_input(
            "Tema Raiz",
            placeholder="Ex: Emagrecimento, Python, Investimentos..."
        )

        if st.button("Gerar Mapa de Nichos", type="primary"):
            if termo:
                with st.spinner("Analisando tendências de busca..."):
                    st.session_state['sugestoes_cache'] = get_google_suggestions(termo)
            else:
                st.warning("Digite um tema raiz para gerar sugestões.")

        if st.session_state.get('sugestoes_cache'):
            st.markdown("<hr>", unsafe_allow_html=True)
            st.write("**Oportunidades encontradas:**")

            cols = st.columns(3)

            for i, sug in enumerate(st.session_state['sugestoes_cache']):
                if cols[i % 3].button(
                    f"🔍 {sug}",
                    key=f"nicho_{i}",
                    use_container_width=True
                ):
                    if api_key:
                        with st.spinner(f"Investigando '{sug}'..."):
                            st.session_state['resultados_busca'] = []
                            st.session_state['next_page_token'] = None

                            res = executar_busca(
                                api_key=api_key,
                                query=sug,
                                max_results=50,
                                duration="medium",
                                min_subs=min_subs,
                                max_subs=max_subs,
                                min_videos=min_videos,
                                max_videos=max_videos,
                                region_code=region_param,
                                usar_proxima_pagina=False
                            )

                            st.session_state['resultados_busca'] = res

                            st.success(
                                "Busca concluída! Volte para a aba "
                                "'Motor de Busca' para ver os resultados."
                            )

                    else:
                        st.error("Configure sua API Key nas Settings da barra lateral.")


# ============================================================
# ABA 3 - BIBLIOTECA DE LEADS
# ============================================================

with tab_salvos:
    section_header(
        "Biblioteca de Leads",
        "Gerencie os canais salvos e exporte sua base para análise externa."
    )

    df = carregar_salvos()

    if not df.empty:
        st.markdown("#### 📁 Sua Base de Leads")

        st.data_editor(
            df,
            column_config={
                "Link": st.column_config.LinkColumn("Canal")
            },
            hide_index=True,
            use_container_width=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        c1.download_button(
            "📥 Exportar para CSV",
            df.to_csv(index=False).encode('utf-8'),
            "outliers_leads.csv",
            "text/csv",
            use_container_width=True
        )

        if c2.button(
            "🗑️ Limpar Banco de Dados",
            use_container_width=True
        ):
            os.remove(ARQUIVO_SALVOS)
            st.rerun()

    else:
        st.info(
            "Sua biblioteca está vazia. Comece salvando canais na aba de Busca."
        )
