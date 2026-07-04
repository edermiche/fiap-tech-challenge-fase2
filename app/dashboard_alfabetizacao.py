from pathlib import Path

import pandas as pd
from flask import Flask, render_template_string, request


app = Flask(__name__)

BASE_PATH = Path(__file__).resolve().parents[1]
GOLD_PATH = BASE_PATH / "data" / "gold"

TABELAS_POR_VISAO = {
    "brasil": "indicador_meta_brasil",
    "regiao": "indicador_meta_regiao",
    "uf": "indicador_meta_uf",
    "municipio": "indicador_meta_municipio",
}

NOMES_VISAO = {
    "brasil": "Brasil",
    "regiao": "Regiao",
    "uf": "UF",
    "municipio": "Municipio",
}


def carregar_gold_particionado(nome_tabela: str) -> pd.DataFrame:
    caminho_tabela = GOLD_PATH / nome_tabela
    arquivos = sorted(caminho_tabela.rglob("*.parquet"))

    if not arquivos:
        raise FileNotFoundError(f"Nenhum parquet encontrado para gold.{nome_tabela}")

    frames = []
    for arquivo in arquivos:
        df_particao = pd.read_parquet(arquivo)

        if "ano" not in df_particao.columns:
            nome_particao = arquivo.parent.name
            if nome_particao.startswith("ano="):
                valor_ano = nome_particao.split("=", 1)[1]
                df_particao.insert(0, "ano", int(valor_ano))

        frames.append(df_particao)

    return pd.concat(frames, ignore_index=True)


def formatar_percentual(valor) -> str:
    if pd.isna(valor):
        return "-"

    return f"{float(valor):.2f}%"


def preparar_dados(visao: str, ano: str, rede: str, uf: str, busca: str) -> pd.DataFrame:
    df = carregar_gold_particionado(TABELAS_POR_VISAO[visao])

    if ano != "todos":
        df = df[df["ano"].astype(str) == ano]

    if rede != "todas" and "rede" in df.columns:
        df = df[df["rede"] == rede]

    if visao == "municipio" and uf != "todas" and "sigla_uf" in df.columns:
        df = df[df["sigla_uf"] == uf]

    if visao == "municipio" and busca:
        termo = busca.strip().casefold()
        nome = df["id_municipio_nome"].fillna("").astype(str).str.casefold()
        codigo = df["id_municipio"].fillna("").astype(str).str.casefold()
        df = df[nome.str.contains(termo, regex=False) | codigo.str.contains(termo, regex=False)]

    return df.copy()


def coluna_taxa(visao: str) -> str:
    if visao == "regiao":
        return "taxa_alfabetizacao_media"

    return "taxa_alfabetizacao"


def coluna_status(visao: str) -> str:
    if visao == "regiao":
        return "status_meta_regiao"

    return "status_meta"


def montar_listagem(df: pd.DataFrame, visao: str) -> pd.DataFrame:
    coluna_percentual = coluna_taxa(visao)
    coluna_situacao = coluna_status(visao)
    colunas_base = ["ano", "rede", coluna_percentual, coluna_situacao]

    if visao == "brasil":
        colunas = colunas_base
        ordenar = ["ano", "rede"]
    elif visao == "regiao":
        colunas = ["ano", "nome_regiao", "rede", coluna_percentual, coluna_situacao]
        ordenar = ["ano", "nome_regiao", "rede"]
    elif visao == "uf":
        colunas = ["ano", "sigla_uf", "sigla_uf_nome", "nome_regiao"] + colunas_base[1:]
        ordenar = ["ano", "sigla_uf", "rede"]
    else:
        colunas = [
            "ano",
            "id_municipio",
            "id_municipio_nome",
            "sigla_uf",
            "nome_regiao",
        ] + colunas_base[1:]
        ordenar = ["ano", "sigla_uf", "id_municipio_nome", "rede"]

    colunas = [coluna for coluna in colunas if coluna in df.columns]
    ordenar = [coluna for coluna in ordenar if coluna in df.columns]

    listagem = df[colunas].sort_values(ordenar).reset_index(drop=True)
    listagem = listagem.rename(
        columns={
            "ano": "Ano",
            "rede": "Rede",
            "sigla_uf": "UF",
            "sigla_uf_nome": "Nome da UF",
            "nome_regiao": "Regiao",
            "id_municipio": "Codigo municipio",
            "id_municipio_nome": "Municipio",
            "taxa_alfabetizacao": "% alfabetizados",
            "taxa_alfabetizacao_media": "% alfabetizados",
            "status_meta": "Status da meta",
            "status_meta_regiao": "Status da meta",
        }
    )

    if "% alfabetizados" in listagem.columns:
        listagem["% alfabetizados"] = listagem["% alfabetizados"].apply(formatar_percentual)

    return listagem


def montar_metricas(df: pd.DataFrame, visao: str) -> dict[str, str]:
    taxa = pd.to_numeric(df.get(coluna_taxa(visao)), errors="coerce")
    status = df.get(coluna_status(visao), pd.Series(dtype="object"))

    return {
        "media": formatar_percentual(taxa.mean()),
        "maior": formatar_percentual(taxa.max()),
        "menor": formatar_percentual(taxa.min()),
        "registros": f"{len(df):,}".replace(",", "."),
        "meta_atingida": f"{int((status == 'Meta atingida').sum()):,}".replace(",", "."),
    }


def opcoes_filtro() -> dict[str, list[str]]:
    frames = []

    for tabela in TABELAS_POR_VISAO.values():
        try:
            frames.append(carregar_gold_particionado(tabela))
        except FileNotFoundError:
            pass

    if not frames:
        return {"anos": [], "redes": [], "ufs": []}

    df = pd.concat(frames, ignore_index=True, sort=False)

    anos = sorted(df["ano"].dropna().astype(int).astype(str).unique(), reverse=True)
    redes = sorted(df["rede"].dropna().astype(str).unique()) if "rede" in df.columns else []
    ufs = sorted(df["sigla_uf"].dropna().astype(str).unique()) if "sigla_uf" in df.columns else []

    return {"anos": anos, "redes": redes, "ufs": ufs}


HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Alfabetizacao</title>
    <style>
        :root {
            --bg: #f5f7fa;
            --panel: #ffffff;
            --text: #1f2933;
            --muted: #5d6875;
            --line: #d8dee6;
            --accent: #176b87;
            --accent-soft: #e7f2f5;
            --good: #2f7d4f;
            --warn: #a45f13;
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

        .shell {
            width: min(1360px, calc(100% - 32px));
            margin: 0 auto;
            padding: 24px 0 32px;
        }

        header {
            margin-bottom: 18px;
        }

        h1 {
            margin: 0 0 6px;
            font-size: 28px;
            font-weight: 700;
        }

        .subtitle {
            margin: 0;
            color: var(--muted);
            font-size: 14px;
        }

        .tabs {
            display: flex;
            gap: 8px;
            margin: 18px 0;
            flex-wrap: wrap;
        }

        .tab {
            border: 1px solid var(--line);
            color: var(--text);
            background: var(--panel);
            border-radius: 6px;
            padding: 10px 16px;
            text-decoration: none;
            font-weight: 700;
            min-width: 112px;
            text-align: center;
        }

        .tab.active {
            background: var(--accent);
            border-color: var(--accent);
            color: #ffffff;
        }

        .filters {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 16px;
            display: grid;
            grid-template-columns: repeat(5, minmax(150px, 1fr));
            gap: 12px;
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

        select,
        input,
        button {
            width: 100%;
            min-height: 38px;
            border-radius: 6px;
            border: 1px solid var(--line);
            background: #ffffff;
            color: var(--text);
            padding: 8px 10px;
            font-size: 14px;
        }

        button {
            background: var(--accent);
            color: #ffffff;
            border-color: var(--accent);
            cursor: pointer;
            font-weight: 700;
        }

        .metrics {
            display: grid;
            grid-template-columns: repeat(5, minmax(150px, 1fr));
            gap: 12px;
            margin: 18px 0;
        }

        .metric {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 14px;
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
            font-size: 24px;
            line-height: 1.1;
        }

        .table-section {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
        }

        .table-head {
            padding: 14px 16px;
            border-bottom: 1px solid var(--line);
            display: flex;
            justify-content: space-between;
            gap: 12px;
            align-items: center;
        }

        .table-head h2 {
            margin: 0;
            font-size: 18px;
        }

        .table-head span {
            color: var(--muted);
            font-size: 13px;
            white-space: nowrap;
        }

        .table-wrap {
            overflow: auto;
            max-height: 68vh;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            font-size: 13px;
        }

        th,
        td {
            border-bottom: 1px solid var(--line);
            padding: 9px 10px;
            text-align: left;
            white-space: nowrap;
        }

        th {
            background: var(--accent-soft);
            position: sticky;
            top: 0;
            z-index: 1;
        }

        tr:hover td {
            background: #fafcfd;
        }

        .erro {
            background: #fff4f1;
            border: 1px solid #efc6bd;
            border-radius: 8px;
            color: #8a2d1c;
            padding: 16px;
        }

        @media (max-width: 980px) {
            .filters,
            .metrics {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        @media (max-width: 620px) {
            .shell {
                width: min(100% - 20px, 1360px);
                padding-top: 16px;
            }

            h1 {
                font-size: 22px;
            }

            .filters,
            .metrics {
                grid-template-columns: 1fr;
            }

            .tab {
                flex: 1 1 100px;
                min-width: 0;
            }
        }
    </style>
</head>
<body>
<main class="shell">
    <header>
        <h1>Dashboard de Alfabetizacao</h1>
        <p class="subtitle">Percentual de estudantes alfabetizados por Brasil, regiao, UF e municipio.</p>
    </header>

    <nav class="tabs" aria-label="Visoes do dashboard">
        {% for chave, nome in nomes_visao.items() %}
            <a class="tab {% if chave == visao %}active{% endif %}"
               href="/?visao={{ chave }}&ano={{ ano }}&rede={{ rede }}&uf={{ uf }}">
                {{ nome }}
            </a>
        {% endfor %}
    </nav>

    <form class="filters" method="get">
        <input type="hidden" name="visao" value="{{ visao }}">

        <label>
            Ano
            <select name="ano">
                <option value="todos" {% if ano == "todos" %}selected{% endif %}>Todos</option>
                {% for item in opcoes.anos %}
                    <option value="{{ item }}" {% if ano == item %}selected{% endif %}>{{ item }}</option>
                {% endfor %}
            </select>
        </label>

        <label>
            Rede
            <select name="rede">
                <option value="todas" {% if rede == "todas" %}selected{% endif %}>Todas</option>
                {% for item in opcoes.redes %}
                    <option value="{{ item }}" {% if rede == item %}selected{% endif %}>{{ item }}</option>
                {% endfor %}
            </select>
        </label>

        <label>
            UF
            <select name="uf" {% if visao != "municipio" %}disabled{% endif %}>
                <option value="todas" {% if uf == "todas" %}selected{% endif %}>Todas</option>
                {% for item in opcoes.ufs %}
                    <option value="{{ item }}" {% if uf == item %}selected{% endif %}>{{ item }}</option>
                {% endfor %}
            </select>
        </label>

        <label>
            Municipio
            <input name="busca" value="{{ busca }}" placeholder="Nome ou codigo" {% if visao != "municipio" %}disabled{% endif %}>
        </label>

        <button type="submit">Filtrar</button>
    </form>

    {% if erro %}
        <section class="erro">{{ erro }}</section>
    {% else %}
        <section class="metrics" aria-label="Resumo">
            <div class="metric"><span>Media</span><strong>{{ metricas.media }}</strong></div>
            <div class="metric"><span>Maior taxa</span><strong>{{ metricas.maior }}</strong></div>
            <div class="metric"><span>Menor taxa</span><strong>{{ metricas.menor }}</strong></div>
            <div class="metric"><span>Registros</span><strong>{{ metricas.registros }}</strong></div>
            <div class="metric"><span>Meta atingida</span><strong>{{ metricas.meta_atingida }}</strong></div>
        </section>

        <section class="table-section">
            <div class="table-head">
                <h2>Listagem - {{ nome_visao }}</h2>
                <span>{{ total_listagem }} linhas</span>
            </div>
            <div class="table-wrap">
                {{ tabela | safe }}
            </div>
        </section>
    {% endif %}
</main>
</body>
</html>
"""


@app.route("/")
def index():
    visao = request.args.get("visao", "brasil")
    if visao not in TABELAS_POR_VISAO:
        visao = "brasil"

    opcoes = opcoes_filtro()
    ano = request.args.get("ano", opcoes["anos"][0] if opcoes["anos"] else "todos")
    rede = request.args.get("rede", "todas")
    uf = request.args.get("uf", "todas")
    busca = request.args.get("busca", "")

    try:
        df = preparar_dados(visao, ano, rede, uf, busca)
        listagem = montar_listagem(df, visao)
        metricas = montar_metricas(df, visao)

        return render_template_string(
            HTML,
            nomes_visao=NOMES_VISAO,
            nome_visao=NOMES_VISAO[visao],
            visao=visao,
            ano=ano,
            rede=rede,
            uf=uf,
            busca=busca,
            opcoes=opcoes,
            metricas=metricas,
            total_listagem=len(listagem),
            tabela=listagem.to_html(index=False, classes="data-table"),
            erro=None,
        )
    except Exception as erro:
        return render_template_string(
            HTML,
            nomes_visao=NOMES_VISAO,
            nome_visao=NOMES_VISAO[visao],
            visao=visao,
            ano=ano,
            rede=rede,
            uf=uf,
            busca=busca,
            opcoes=opcoes,
            metricas={},
            total_listagem=0,
            tabela="",
            erro=str(erro),
        )


if __name__ == "__main__":
    app.run(debug=False, port=5003, use_reloader=False)
