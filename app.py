import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import os
import requests
import random
import time
import html
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
# CSS CUSTOMIZADO
# Usa o tema nativo do Streamlit: claro/escuro automático
# ============================================================

def aplicar_estilo_saas():
    st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        :root {
            --app-bg: var(--st-background-color, var(--background-color, #ffffff));
            --app-surface: var(--st-secondary-background-color, var(--secondary-background-color, #f6f7fb));
            --app-text: var(--st-text-color, var(--text-color, #111827));
            --app-primary: var(--st-primary-color, var(--primary-color, #ff4b4b));
            --app-border: var(--st-border-color, rgba(128, 128, 128, 0.22));
            --app-radius: 22px;
        }

        html, body, [data-testid="stAppViewContainer"] {
            background-color: var(--app-bg) !important;
            color: var(--app-text) !important;
        }

        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
            max-width: 1180px;
        }

        [data-testid="stSidebar"] {
            background-color: var(--app-surface) !important;
            border-right: 1px solid var(--app-border);
        }

        .main-title {
            font-size: 2.45rem;
            font-weight: 850;
            letter-spacing: -0.04em;
            color: var(--app-text);
            margin-bottom: 0.25rem;
        }

        .subtitle {
            color: var(--app-text);
            opacity: 0.68;
            font-size: 1rem;
            margin-bottom: 1.6rem;
        }

        .section-title {
            font-size: 1.35rem;
            font-weight: 850;
            color: var(--app-text);
            margin-bottom: 0.25rem;
        }

        .section-caption {
            color: var(--app-text);
            opacity: 0.68;
            font-size: 0.95rem;
            margin-bottom: 1.2rem;
        }

        .stButton > button {
            border-radius: 13px !important;
            font-weight: 750 !important;
            min-height: 45px;
            transition: all 0.22s ease-in-out;
            border: 1px solid var(--app-border) !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 22px rgba(0, 0, 0, 0.14) !important;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #ff4b4b 0%, #ef4444 100%) !important;
            border: none !important;
            color: white !important;
        }

        .stTextInput input,
        .stNumberInput input,
        textarea {
            border-radius: 13px !important;
            border: 1px solid var(--app-border) !important;
        }

        .stSelectbox div[data-baseweb="select"] > div {
            border-radius: 13px !important;
            border: 1px solid var(--app-border) !important;
        }

        div[data-testid="stVerticalBlock"] > div[style*="border"] {
            border-radius: var(--app-radius) !important;
            border: 1px solid var(--app-border) !important;
            background-color: var(--app-bg) !important;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.07) !important;
            padding: 1.1rem !important;
        }

        details {
            border-radius: 14px !important;
            border: 1px solid var(--app-border) !important;
            background-color: var(--app-surface) !important;
        }

        .channel-title {
            font-size: 1.05rem;
            font-weight: 850;
            margin-bottom: 0.15rem;
        }

        .channel-title a {
            color: var(--app-text);
            text-decoration: none;
        }

        .channel-title a:hover {
            text-decoration: underline;
        }

        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 0.78rem;
            font-weight: 750;
            background-color: rgba(99, 102, 241, 0.13);
            color: var(--app-text);
            margin-top: 6px;
        }

        .badge-green {
            background-color: rgba(16, 185, 129, 0.15);
            color: var(--app-text);
        }

        .sidebar-tip {
            background-color: rgba(59, 130, 246, 0.13);
            color: var(--app-text) !important;
            padding: 16px;
            border-radius: 16px;
            font-weight: 650;
            line-height: 1.45;
        }

        hr {
            border: none;
            border-top: 1px solid var(--app-border);
            margin: 1.5rem 0;
        }

        [data-testid="stDataFrame"] {
            border-radius: 18px;
            overflow: hidden;
        }

        /* ====================================================
           MOBILE
           ==================================================== */
        @media screen and (max-width: 768px) {
            .block-container {
                padding-top: 1rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                padding-bottom: 2rem !important;
                max-width: 100% !important;
            }

            .main-title {
                font-size: 1.85rem !important;
                line-height: 1.05;
                margin-top: 0.4rem;
            }

            .subtitle {
                font-size: 0.92rem !important;
                margin-bottom: 1.2rem;
            }

            .section-title {
                font-size: 1.15rem !important;
            }

            .section-caption {
                font-size: 0.88rem !important;
            }

            div[data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }

            .stTabs [data-baseweb="tab-list"] {
                overflow-x: auto;
                white-space: nowrap;
                flex-wrap: nowrap;
                padding-bottom: 0.3rem;
            }

            .stTabs [data-baseweb="tab"] {
                padding: 9px 14px;
                font-size: 0.86rem;
            }

            .stButton > button {
                width: 100% !important;
                min-height: 46px;
            }

            div[data-testid="stVerticalBlock"] > div[style*="border"] {
                border-radius: 18px !important;
                padding: 0.95rem !important;
            }

            img {
                max-width: 100% !important;
                height: auto !important;
            }

            [data-testid="stDataFrame"] {
                overflow-x: auto !important;
            }
        }

        @media screen and (max-width: 480px) {
            .main-title {
                font-size: 1.65rem !important;
            }

            .subtitle {
                font-size: 0.86rem !important;
            }

            .stTabs [data-baseweb="tab"] {
                padding: 8px 12px;
                font-size: 0.82rem;
            }
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
            'order': 'date'
        }

        if token:
            search_params['pageToken'] = token

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
# API KEY
# ============================================================

api_key = st.secrets["GOOGLE_API_KEY"] if "GOOGLE_API_KEY" in st.secrets else None


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
    else:
        st.success("API Key configurada")

    region = st.selectbox(
        "Região Alvo",
        ["Qualquer", "BR", "US", "PT"],
        index=0
    )

    region_param = None if region == "Qualquer" else region

    st.caption("Use a região para priorizar canais de um país específico.")

    st.markdown("---")

    st.markdown("""
    <div class="sidebar-tip">
        Dica: filtros muito restritos podem retornar poucos canais.
        Comece amplo e depois refine.
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# HEADER PRINCIPAL
# ============================================================

st.markdown("""
<div class="main-title">🎯 Outlier Hunter Pro</div>
<div class="subtitle">
    Pesquise palavras-chave e encontre canais pequenos com performance fora da curva.
</div>
""", unsafe_allow_html=True)


# ============================================================
# BLOCO PRINCIPAL DE BUSCA
# ============================================================

section_header(
    "Pesquisa de Palavras-chave",
    "Digite um nicho ou termo para encontrar canais promissores no YouTube."
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


# ============================================================
# RESULTADOS DA BUSCA
# ============================================================

if st.session_state['resultados_busca']:
    st.markdown(
        f"### 📋 Resultados Encontrados ({len(st.session_state['resultados_busca'])})"
    )

    for i, canal in enumerate(st.session_state['resultados_busca']):
        is_viral = canal['Média Views'] > canal['Inscritos']
        canal_novo = canal['Dias Vida'] < 90

        nome_seguro = html.escape(str(canal['Nome']))
        link_seguro = html.escape(str(canal['Link']))

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
                        <a href="{link_seguro}" target="_blank">
                            {nome_seguro}
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
# ABAS SECUNDÁRIAS
# ============================================================

st.markdown("<hr>", unsafe_allow_html=True)

tab_discovery, tab_salvos = st.tabs([
    "🧠 Inteligência de Nicho",
    "💾 Biblioteca de Leads"
])


# ============================================================
# ABA - INTELIGÊNCIA DE NICHO
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
                                "Busca concluída! Os resultados aparecerão na área principal de busca."
                            )

                    else:
                        st.error("Configure sua API Key nas Settings da barra lateral.")


# ============================================================
# ABA - BIBLIOTECA DE LEADS
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
            "Sua biblioteca está vazia. Comece salvando canais na busca principal."
        )
