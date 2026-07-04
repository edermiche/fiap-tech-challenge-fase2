from pathlib import Path

import pandas as pd
from flask import Flask, render_template_string, request, url_for

try:
    from app import mapa_brasil_metas as mapa
except ImportError:
    import mapa_brasil_metas as mapa


app = Flask(__name__)

BASE_PATH = Path(__file__).resolve().parents[1]
GOLD_PATH = BASE_PATH / "data" / "gold"


DESCRICOES_TABELAS = {
    "evolucao_alfabetizacao": {
        "nome": "Evolucao da alfabetizacao",
        "descricao": (
            "Serie temporal consolidada com taxa media de alfabetizacao, "
            "percentual de participacao e variacoes anuais."
        ),
    },
    "indicador_meta_brasil": {
        "nome": "Indicador de meta Brasil",
        "descricao": (
            "Compara resultado observado e meta de alfabetizacao no nivel Brasil, "
            "calculando distancia da meta e status de cumprimento."
        ),
    },
    "indicador_meta_municipio": {
        "nome": "Indicador de meta municipio",
        "descricao": (
            "Compara resultado observado e meta de alfabetizacao por municipio, "
            "calculando distancia da meta e status de cumprimento."
        ),
    },
    "indicador_meta_uf": {
        "nome": "Indicador de meta UF",
        "descricao": (
            "Compara resultado observado e meta de alfabetizacao por UF, "
            "calculando distancia da meta e status de cumprimento."
        ),
    },
    "ranking_municipio_prioritario": {
        "nome": "Ranking de municipios prioritarios",
        "descricao": (
            "Lista municipios abaixo da meta, ordenados pela maior distancia "
            "negativa em relacao ao objetivo."
        ),
    },
    "ranking_uf_prioritaria": {
        "nome": "Ranking de UFs prioritarias",
        "descricao": (
            "Lista UFs abaixo da meta, ordenadas pela maior distancia negativa "
            "em relacao ao objetivo."
        ),
    },
    "resumo_status_meta": {
        "nome": "Resumo de status das metas",
        "descricao": (
            "Agregado por ano, nivel territorial e status da meta, usado para "
            "visao executiva de cumprimento das metas."
        ),
    },
}


DESCRICOES_COLUNAS = {
    "ano": "Ano de referencia do dado observado.",
    "rede": "Rede de ensino ou nivel administrativo.",
    "taxa_alfabetizacao": "Taxa observada de alfabetizacao.",
    "percentual_participacao": "Percentual de participacao no indicador.",
    "variacao_taxa": "Variacao da taxa de alfabetizacao em relacao ao ano anterior.",
    "variacao_percentual": "Variacao do percentual de participacao em relacao ao ano anterior.",
    "flag_taxa_alfabetizacao_valido": "Flag de qualidade da taxa de alfabetizacao.",
    "flag_percentual_participacao_valido": "Flag de qualidade do percentual de participacao.",
    "nivel_agregacao": "Nivel territorial do indicador.",
    "nivel_agregacao_resultado": "Nivel territorial do resultado observado.",
    "nivel_agregacao_meta": "Nivel territorial da meta.",
    "data_processamento_silver_resultado": "Data de processamento Silver do resultado.",
    "data_processamento_silver_meta": "Data de processamento Silver da meta.",
    "ano_meta": "Ano alvo da meta de alfabetizacao.",
    "meta_alfabetizacao": "Meta percentual de alfabetizacao.",
    "flag_meta_alfabetizacao_valido": "Flag de qualidade da meta de alfabetizacao.",
    "distancia_meta": "Diferenca entre taxa observada e meta de alfabetizacao.",
    "flag_meta_atingida": "Indica se a meta foi atingida.",
    "status_meta": "Classificacao do cumprimento da meta.",
    "id_municipio": "Codigo IBGE do municipio.",
    "serie": "Serie escolar analisada.",
    "media_portugues": "Media de proficiencia em Lingua Portuguesa.",
    "sigla_uf": "Sigla da Unidade Federativa.",
    "ranking": "Posicao no ranking de prioridade.",
    "quantidade": "Quantidade de registros agregados no grupo.",
    "nivel": "Nivel territorial do resumo.",
}


def localizar_parquet_mais_recente(caminho_tabela: Path) -> Path | None:
    arquivos = list(caminho_tabela.rglob("*.parquet"))

    if not arquivos:
        return None

    return max(arquivos, key=lambda arquivo: arquivo.stat().st_mtime)


def listar_tabelas_gold() -> list[str]:
    if not GOLD_PATH.exists():
        return []

    tabelas = []
    for caminho in sorted(GOLD_PATH.iterdir()):
        if caminho.is_dir() and localizar_parquet_mais_recente(caminho):
            tabelas.append(caminho.name)

    return tabelas


def carregar_gold(nome_tabela: str) -> tuple[pd.DataFrame, Path]:
    arquivo = localizar_parquet_mais_recente(GOLD_PATH / nome_tabela)

    if arquivo is None:
        raise FileNotFoundError(f"Nenhum parquet encontrado para gold.{nome_tabela}")

    return pd.read_parquet(arquivo), arquivo


def formatar_valor(valor):
    if pd.isna(valor):
        return "-"

    if isinstance(valor, float):
        return round(valor, 4)

    return valor


def montar_dicionario_colunas(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []

    for coluna in df.columns:
        serie = df[coluna]
        exemplo = "-"
        valores_validos = serie.dropna()
        if not valores_validos.empty:
            exemplo = formatar_valor(valores_validos.iloc[0])

        linhas.append(
            {
                "coluna": coluna,
                "tipo": str(serie.dtype),
                "nulos": int(serie.isna().sum()),
                "% nulos": round((serie.isna().mean() * 100), 2),
                "distintos": int(serie.nunique(dropna=True)),
                "exemplo": exemplo,
                "descricao": DESCRICOES_COLUNAS.get(coluna, "Campo analitico da tabela Gold."),
            }
        )

    return pd.DataFrame(linhas)


def preparar_tabela_html(df: pd.DataFrame, limite: int) -> str:
    df_preview = df.head(limite).map(formatar_valor)
    return df_preview.to_html(index=False, classes="data-table")


HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catalogo Gold</title>
    <style>
        :root {
            --bg: #f5f7fa;
            --panel: #ffffff;
            --text: #1f2933;
            --muted: #607080;
            --line: #d8dee6;
            --accent: #176b87;
            --accent-soft: #e7f2f5;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            background: var(--bg);
            color: var(--text);
            font-family: Arial, Helvetica, sans-serif;
        }

        .layout {
            display: grid;
            grid-template-columns: 300px minmax(0, 1fr);
            min-height: 100vh;
        }

        aside {
            border-right: 1px solid var(--line);
            background: var(--panel);
            padding: 20px 16px;
            position: sticky;
            top: 0;
            height: 100vh;
            overflow: auto;
        }

        main {
            padding: 24px;
            min-width: 0;
        }

        h1,
        h2,
        h3 {
            margin: 0;
        }

        .brand {
            margin-bottom: 18px;
        }

        .brand h1 {
            font-size: 22px;
            margin-bottom: 4px;
        }

        .brand p,
        .subtitle,
        .muted {
            color: var(--muted);
            margin: 0;
            line-height: 1.45;
        }

        .menu {
            display: grid;
            gap: 8px;
        }

        .menu-section {
            margin: 18px 0 8px;
            color: var(--muted);
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
        }

        .menu a {
            display: block;
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 10px 12px;
            color: var(--text);
            text-decoration: none;
            background: #fff;
        }

        .menu a.active {
            border-color: var(--accent);
            background: var(--accent-soft);
            font-weight: 700;
        }

        .menu a.dashboard-link {
            border-color: var(--accent);
            background: var(--accent);
            color: #fff;
        }

        .menu a.dashboard-link .table-name {
            color: rgba(255, 255, 255, .82);
        }

        .table-name {
            display: block;
            color: var(--muted);
            font-size: 12px;
            font-weight: 400;
            margin-top: 2px;
            word-break: break-word;
        }

        .header {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: start;
            margin-bottom: 18px;
        }

        .actions {
            display: flex;
            gap: 8px;
            align-items: end;
        }

        label {
            display: grid;
            gap: 6px;
            color: var(--muted);
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
        }

        input,
        button {
            min-height: 38px;
            border-radius: 6px;
            border: 1px solid var(--line);
            background: #fff;
            color: var(--text);
            padding: 8px 10px;
            font-size: 14px;
        }

        button {
            background: var(--accent);
            border-color: var(--accent);
            color: #fff;
            font-weight: 700;
            cursor: pointer;
        }

        .cards {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--panel);
            overflow: hidden;
            margin-bottom: 16px;
        }

        .metric {
            padding: 14px;
            border-right: 1px solid var(--line);
            min-width: 0;
        }

        .metric:last-child {
            border-right: 0;
        }

        .metric span {
            display: block;
            color: var(--muted);
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        .metric strong {
            display: block;
            min-width: 0;
            overflow-wrap: anywhere;
            word-break: break-word;
            font-size: 24px;
            line-height: 1.15;
        }

        .metric .file-name {
            font-size: 18px;
        }

        .section {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            margin-bottom: 16px;
            overflow: hidden;
        }

        .section-head {
            padding: 14px 16px;
            border-bottom: 1px solid var(--line);
        }

        .section-body {
            padding: 16px;
        }

        .table-wrap {
            overflow: auto;
            max-height: 560px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        th,
        td {
            border-bottom: 1px solid var(--line);
            padding: 8px 10px;
            text-align: left;
            white-space: nowrap;
        }

        th {
            background: var(--accent-soft);
            position: sticky;
            top: 0;
            z-index: 1;
        }

        .erro {
            padding: 16px;
            border: 1px solid #efc6bd;
            border-radius: 8px;
            background: #fff4f1;
            color: #8a2d1c;
        }

        @media (max-width: 900px) {
            .layout {
                grid-template-columns: 1fr;
            }

            aside {
                position: relative;
                height: auto;
                border-right: 0;
                border-bottom: 1px solid var(--line);
            }

            .cards,
            .header {
                display: grid;
                grid-template-columns: 1fr;
            }

            .metric {
                border-right: 0;
                border-bottom: 1px solid var(--line);
            }
        }
    </style>
</head>
<body>
<div class="layout">
    <aside>
        <div class="brand">
            <h1>Catalogo Gold</h1>
            <p>{{ total_tabelas }} tabelas disponiveis em data/gold.</p>
        </div>

        <nav class="menu" aria-label="Tabelas Gold">
            <a class="dashboard-link" href="{{ url_for('mapa_index') }}">
                Mapa Brasil Metas
                <span class="table-name">Dashboard geografico</span>
            </a>

            <div class="menu-section">Tabelas Gold</div>

            {% for item in menu %}
                <a href="{{ url_for('index', tabela=item.tabela, limite=limite) }}"
                   class="{% if item.tabela == tabela_selecionada %}active{% endif %}">
                    {{ item.nome }}
                    <span class="table-name">gold.{{ item.tabela }}</span>
                </a>
            {% endfor %}
        </nav>
    </aside>

    <main>
        {% if erro %}
            <section class="erro">{{ erro }}</section>
        {% else %}
            <header class="header">
                <div>
                    <h1>{{ descricao.nome }}</h1>
                    <p class="subtitle">gold.{{ tabela_selecionada }}</p>
                    <p class="subtitle">{{ descricao.descricao }}</p>
                </div>
                <form class="actions" method="get">
                    <input type="hidden" name="tabela" value="{{ tabela_selecionada }}">
                    <label>
                        Linhas
                        <input type="number" name="limite" min="5" max="500" step="5" value="{{ limite }}">
                    </label>
                    <button type="submit">Atualizar</button>
                </form>
            </header>

            <section class="cards" aria-label="Resumo da tabela">
                <div class="metric"><span>Linhas</span><strong>{{ linhas }}</strong></div>
                <div class="metric"><span>Colunas</span><strong>{{ colunas }}</strong></div>
                <div class="metric"><span>Arquivo</span><strong class="file-name">{{ arquivo_nome }}</strong></div>
                <div class="metric"><span>Amostra</span><strong>{{ limite }}</strong></div>
            </section>

            <section class="section">
                <div class="section-head">
                    <h2>Dicionario da tabela</h2>
                </div>
                <div class="section-body table-wrap">
                    {{ dicionario | safe }}
                </div>
            </section>

            <section class="section">
                <div class="section-head">
                    <h2>Listagem</h2>
                    <p class="muted">Exibindo as primeiras {{ limite }} linhas do arquivo mais recente.</p>
                </div>
                <div class="section-body table-wrap">
                    {{ listagem | safe }}
                </div>
            </section>
        {% endif %}
    </main>
</div>
</body>
</html>
"""


@app.route("/")
def index():
    tabelas = listar_tabelas_gold()
    menu = [
        {
            "tabela": tabela,
            "nome": DESCRICOES_TABELAS.get(tabela, {}).get("nome", tabela),
        }
        for tabela in tabelas
    ]

    if not tabelas:
        return render_template_string(
            HTML,
            total_tabelas=0,
            menu=[],
            tabela_selecionada=None,
            limite=50,
            erro="Nenhuma tabela Gold encontrada em data/gold.",
        )

    tabela_selecionada = request.args.get("tabela", tabelas[0])
    if tabela_selecionada not in tabelas:
        tabela_selecionada = tabelas[0]

    try:
        limite = int(request.args.get("limite", "50"))
    except ValueError:
        limite = 50
    limite = min(max(limite, 5), 500)

    try:
        df, arquivo = carregar_gold(tabela_selecionada)
        descricao = DESCRICOES_TABELAS.get(
            tabela_selecionada,
            {
                "nome": tabela_selecionada,
                "descricao": "Tabela analitica da camada Gold.",
            },
        )

        dicionario = montar_dicionario_colunas(df).to_html(index=False, classes="data-table")
        listagem = preparar_tabela_html(df, limite)

        return render_template_string(
            HTML,
            total_tabelas=len(tabelas),
            menu=menu,
            tabela_selecionada=tabela_selecionada,
            limite=limite,
            erro=None,
            descricao=descricao,
            linhas=f"{len(df):,}".replace(",", "."),
            colunas=len(df.columns),
            arquivo_nome=arquivo.name,
            dicionario=dicionario,
            listagem=listagem,
        )
    except Exception as erro:
        return render_template_string(
            HTML,
            total_tabelas=len(tabelas),
            menu=menu,
            tabela_selecionada=tabela_selecionada,
            limite=limite,
            erro=str(erro),
        )


def ajustar_links_mapa(html: str) -> str:
    return (
        html
        .replace('href="/estado/', 'href="/mapa/estado/')
        .replace('href="/cidade/', 'href="/mapa/cidade/')
        .replace('href="/?ano=', 'href="/mapa?ano=')
        .replace('`/cidade/${cidadeSelect.value}', '`/mapa/cidade/${cidadeSelect.value}')
    )


@app.route("/mapa")
def mapa_index():
    try:
        df = mapa.carregar_indicador_uf()
        opcoes = mapa.montar_opcoes(df)
        ano = request.args.get("ano", opcoes["anos"][0] if opcoes["anos"] else "todos")
        rede = request.args.get("rede", "todas")
        dados = mapa.filtrar_dados(df, ano, rede)

        return render_template_string(
            ajustar_links_mapa(mapa.HTML),
            opcoes=opcoes,
            ano=ano,
            rede=rede,
            estados=mapa.montar_estados(dados),
            metricas=mapa.montar_metricas(dados),
            erro=None,
        )
    except Exception as erro:
        return render_template_string(
            ajustar_links_mapa(mapa.HTML),
            opcoes={"anos": [], "redes": []},
            ano="",
            rede="todas",
            estados=[],
            metricas={},
            erro=str(erro),
        )


@app.route("/mapa/estado/<sigla_uf>")
def mapa_estado(sigla_uf: str):
    sigla_uf = sigla_uf.upper()

    if sigla_uf not in mapa.CODIGO_UF_POR_SIGLA:
        return render_template_string(
            ajustar_links_mapa(mapa.HTML_ESTADO),
            sigla_uf=sigla_uf,
            opcoes={"anos": [], "redes": []},
            ano="",
            rede="todas",
            cidades=[],
            municipios=[],
            metricas={},
            erro=f"UF invalida: {sigla_uf}",
        )

    try:
        df = mapa.carregar_indicador_municipio()
        opcoes = mapa.montar_opcoes(df)
        ano = request.args.get("ano", opcoes["anos"][0] if opcoes["anos"] else "todos")
        rede = request.args.get("rede", "todas")
        opcoes = mapa.incluir_opcao_atual(opcoes, ano, rede)
        dados = mapa.filtrar_dados_municipio(df, sigla_uf, ano, rede)

        return render_template_string(
            ajustar_links_mapa(mapa.HTML_ESTADO),
            sigla_uf=sigla_uf,
            opcoes=opcoes,
            ano=ano,
            rede=rede,
            cidades=mapa.montar_opcoes_cidade(df, sigla_uf),
            municipios=mapa.montar_municipios(dados, sigla_uf),
            metricas=mapa.montar_metricas(dados),
            erro=None,
        )
    except Exception as erro:
        return render_template_string(
            ajustar_links_mapa(mapa.HTML_ESTADO),
            sigla_uf=sigla_uf,
            opcoes={"anos": [], "redes": []},
            ano="",
            rede="todas",
            cidades=[],
            municipios=[],
            metricas={},
            erro=str(erro),
        )


@app.route("/mapa/cidade/<id_municipio>")
def mapa_cidade(id_municipio: str):
    ano = request.args.get("ano", "todos")
    rede = request.args.get("rede", "todas")
    sigla_uf = request.args.get("uf", "")

    try:
        df_municipio = mapa.carregar_indicador_municipio()
        registro = df_municipio[
            df_municipio["id_municipio"].astype(str) == str(id_municipio)
        ]

        if registro.empty:
            raise FileNotFoundError(f"Municipio nao encontrado na Gold: {id_municipio}")

        if not sigla_uf:
            sigla_uf = str(registro.iloc[0].get("sigla_uf") or "")

        return render_template_string(
            ajustar_links_mapa(mapa.HTML_CIDADE),
            id_municipio=id_municipio,
            nome_cidade=mapa.obter_nome_cidade(df_municipio, id_municipio),
            sigla_uf=sigla_uf,
            ano=ano,
            rede=rede,
            secoes=mapa.montar_secoes_cidade(id_municipio, sigla_uf, ano, rede),
            erro=None,
        )
    except Exception as erro:
        return render_template_string(
            ajustar_links_mapa(mapa.HTML_CIDADE),
            id_municipio=id_municipio,
            nome_cidade=str(id_municipio),
            sigla_uf=sigla_uf,
            ano=ano,
            rede=rede,
            secoes=[],
            erro=str(erro),
        )


if __name__ == "__main__":
    app.run(debug=False, port=5006, use_reloader=False)
