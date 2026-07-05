from pathlib import Path
from html import escape

import pandas as pd
from flask import Flask, render_template_string, request


app = Flask(__name__)

BASE_PATH = Path(__file__).resolve().parents[1]
GOLD_PATH = BASE_PATH / "data" / "gold"
TABELA_SIMULACAO = "simulacao_alfabetizacao_2030"
NIVEIS_ANALISE = {
    "municipio": "Municipio",
    "uf": "UF",
    "brasil": "Brasil",
}
CLASSES_RISCO = [
    "Meta atingida",
    "Baixo risco",
    "Risco moderado",
    "Risco alto",
    "Risco critico",
    "Sem informacao",
]
DESCRICOES_COLUNAS = {
    "UF": "Sigla da Unidade Federativa analisada.",
    "Codigo": "Codigo IBGE do municipio.",
    "Municipio": "Nome do municipio analisado.",
    "Nivel": "Nivel agregado da analise exibida na linha.",
    "Municipios agregados": "Quantidade de municipios considerados no agrupamento.",
    "Taxa atual": "Taxa de alfabetizacao observada no ano base da simulacao.",
    "Conservador": "Taxa simulada em um cenario de crescimento mais lento.",
    "Base": "Taxa simulada no cenario principal, considerando gap ate a meta e participacao na avaliacao.",
    "Acelerado": "Taxa simulada em um cenario otimista, com maior avanco por intervencoes.",
    "Gap base": "Diferenca entre a meta do ano selecionado e a taxa simulada no cenario base.",
    "Prob. meta": "Probabilidade indicativa de atingir a meta no cenario base.",
}


def carregar_gold_particionado(nome_tabela: str) -> pd.DataFrame:
    caminho_tabela = GOLD_PATH / nome_tabela
    arquivos = sorted(caminho_tabela.rglob("*.parquet"))

    if not arquivos:
        raise FileNotFoundError(f"Nenhum parquet encontrado para gold.{nome_tabela}")

    frames = []
    for arquivo in arquivos:
        df_particao = pd.read_parquet(arquivo)
        if "ano" not in df_particao.columns and arquivo.parent.name.startswith("ano="):
            df_particao.insert(0, "ano", int(arquivo.parent.name.split("=", 1)[1]))
        frames.append(df_particao)

    return pd.concat(frames, ignore_index=True)


def formatar_percentual(valor) -> str:
    if pd.isna(valor):
        return "-"
    return f"{float(valor):.2f}%"


def formatar_numero(valor) -> str:
    if pd.isna(valor):
        return "-"
    return f"{int(valor):,}".replace(",", ".")


def descricao_coluna(coluna: str) -> str:
    if coluna.startswith("Meta "):
        ano = coluna.replace("Meta ", "", 1)
        return f"Meta oficial de alfabetizacao para o ano {ano}."

    if coluna.startswith("Risco "):
        ano = coluna.replace("Risco ", "", 1)
        return f"Classe de risco no ano {ano}, calculada pela distancia ate a meta no cenario base."

    return DESCRICOES_COLUNAS.get(coluna, f"Coluna {coluna}.")


def adicionar_tooltips_cabecalho(html_tabela: str, colunas: list[str]) -> str:
    html_com_tooltips = html_tabela

    for coluna in colunas:
        descricao = escape(descricao_coluna(coluna), quote=True)
        texto = escape(coluna)
        cabecalho_original = f"<th>{texto}</th>"
        cabecalho_com_tooltip = f'<th title="{descricao}">{texto}</th>'
        html_com_tooltips = html_com_tooltips.replace(
            cabecalho_original,
            cabecalho_com_tooltip,
            1,
        )

    return html_com_tooltips


def classificar_risco_agregado(gap: float, probabilidade: float) -> str:
    if pd.isna(gap):
        return "Sem informacao"
    if gap <= 0:
        return "Meta atingida"
    if probabilidade >= 80:
        return "Baixo risco"
    if gap <= 5:
        return "Risco moderado"
    if gap <= 15:
        return "Risco alto"
    return "Risco critico"


def preparar_nivel_analise(df: pd.DataFrame, nivel: str) -> pd.DataFrame:
    if nivel == "municipio":
        df_nivel = df.copy()
        df_nivel["unidade_analise"] = df_nivel["id_municipio_nome"].fillna(df_nivel["id_municipio"])
        return df_nivel

    if nivel == "uf":
        chaves = ["ano", "sigla_uf"]
    else:
        chaves = ["ano"]

    agregacoes = {
        "id_municipio": "nunique",
        "taxa_atual": "mean",
        "meta_alfabetizacao": "mean",
        "taxa_simulada_conservador": "mean",
        "taxa_simulada_base": "mean",
        "taxa_simulada_acelerado": "mean",
        "gap_base": "mean",
        "probabilidade_atingir_meta_base": "mean",
    }
    df_nivel = df.groupby(chaves, dropna=False).agg(agregacoes).reset_index()
    df_nivel = df_nivel.rename(columns={"id_municipio": "total_municipios"})
    df_nivel["status_cenario_base"] = "Abaixo da meta"
    df_nivel.loc[df_nivel["gap_base"] <= 0, "status_cenario_base"] = "Meta atingida"
    df_nivel["classe_risco_2030"] = [
        classificar_risco_agregado(gap, prob)
        for gap, prob in zip(
            df_nivel["gap_base"],
            df_nivel["probabilidade_atingir_meta_base"],
        )
    ]

    if nivel == "uf":
        df_nivel["unidade_analise"] = df_nivel["sigla_uf"]
    else:
        df_nivel["sigla_uf"] = "BR"
        df_nivel["unidade_analise"] = "Brasil"

    return df_nivel


def filtrar_dados(df: pd.DataFrame, ano: str, uf: str, risco: str, busca: str, nivel: str) -> pd.DataFrame:
    if ano != "todos":
        df = df[df["ano"].astype(str) == ano]
    if uf != "todas":
        df = df[df["sigla_uf"] == uf]
    if busca and nivel == "municipio":
        termo = busca.strip().casefold()
        nome = df["id_municipio_nome"].fillna("").astype(str).str.casefold()
        codigo = df["id_municipio"].fillna("").astype(str).str.casefold()
        df = df[nome.str.contains(termo, regex=False) | codigo.str.contains(termo, regex=False)]

    df_nivel = preparar_nivel_analise(df, nivel)

    if risco != "todos":
        df_nivel = df_nivel[df_nivel["classe_risco_2030"] == risco]

    return df_nivel.copy()


def selecionar_ano_analise(df: pd.DataFrame, ano_filtro: str) -> pd.DataFrame:
    if ano_filtro != "todos":
        return df.copy()

    ano_final = df[df["ano"] == 2030]
    if not ano_final.empty:
        return ano_final.copy()

    return df.copy()


def rotulo_ano_analise(ano_filtro: str) -> str:
    if ano_filtro == "todos":
        return "2030"

    return ano_filtro


def montar_metricas(df: pd.DataFrame, ano_filtro: str, nivel_label: str) -> dict[str, str]:
    base = selecionar_ano_analise(df, ano_filtro)
    coluna_total = "id_municipio" if "id_municipio" in base.columns else "unidade_analise"
    label_total = "Municipios" if nivel_label == "Municipio" else nivel_label

    return {
        "label_total": label_total,
        "total": formatar_numero(base[coluna_total].nunique()),
        "media_base": formatar_percentual(base["taxa_simulada_base"].mean()),
        "media_meta": formatar_percentual(base["meta_alfabetizacao"].mean()),
        "atingem": formatar_numero((base["status_cenario_base"] == "Meta atingida").sum()),
        "risco_critico": formatar_numero((base["classe_risco_2030"] == "Risco critico").sum()),
    }


def resumo_por_uf(df_base_municipal: pd.DataFrame, ano_filtro: str) -> pd.DataFrame:
    df = preparar_nivel_analise(df_base_municipal, "municipio")
    base = selecionar_ano_analise(df, ano_filtro)

    resumo = (
        base.groupby("sigla_uf", dropna=False)
        .agg(
            municipios=("id_municipio", "nunique"),
            taxa_base_media=("taxa_simulada_base", "mean"),
            meta_media=("meta_alfabetizacao", "mean"),
            gap_medio=("gap_base", "mean"),
            risco_critico=("classe_risco_2030", lambda s: (s == "Risco critico").sum()),
            meta_atingida=("status_cenario_base", lambda s: (s == "Meta atingida").sum()),
        )
        .reset_index()
    )
    resumo["percentual_meta_atingida"] = (
        resumo["meta_atingida"] / resumo["municipios"] * 100
    ).round(2)
    return resumo.sort_values(["gap_medio", "risco_critico"], ascending=[False, False])


def serie_nacional(df: pd.DataFrame) -> list[dict[str, float]]:
    serie = (
        df.groupby("ano")
        .agg(
            conservador=("taxa_simulada_conservador", "mean"),
            base=("taxa_simulada_base", "mean"),
            acelerado=("taxa_simulada_acelerado", "mean"),
            meta=("meta_alfabetizacao", "mean"),
        )
        .reset_index()
        .sort_values("ano")
    )
    return serie.round(2).to_dict("records")


def barras_risco(df: pd.DataFrame, ano_filtro: str) -> list[dict[str, str]]:
    base = selecionar_ano_analise(df, ano_filtro)

    total = max(len(base), 1)
    contagem = base["classe_risco_2030"].value_counts().to_dict()
    return [
        {
            "classe": classe,
            "quantidade": formatar_numero(contagem.get(classe, 0)),
            "largura": f"{(contagem.get(classe, 0) / total * 100):.2f}%",
        }
        for classe in CLASSES_RISCO
        if contagem.get(classe, 0) > 0
    ]


def montar_listagem(df: pd.DataFrame, ano_filtro: str, ano_label: str, nivel: str) -> pd.DataFrame:
    base = selecionar_ano_analise(df, ano_filtro)

    if nivel == "municipio":
        colunas = ["sigla_uf", "id_municipio", "id_municipio_nome"]
    elif nivel == "uf":
        colunas = ["sigla_uf", "total_municipios"]
    else:
        colunas = ["unidade_analise", "total_municipios"]

    colunas += [
        "taxa_atual",
        "meta_alfabetizacao",
        "taxa_simulada_conservador",
        "taxa_simulada_base",
        "taxa_simulada_acelerado",
        "gap_base",
        "probabilidade_atingir_meta_base",
        "classe_risco_2030",
    ]
    tabela = base[colunas].sort_values(["gap_base", "taxa_simulada_base"], ascending=[False, True]).head(80)
    tabela = tabela.rename(
        columns={
            "sigla_uf": "UF",
            "id_municipio": "Codigo",
            "id_municipio_nome": "Municipio",
            "unidade_analise": "Nivel",
            "total_municipios": "Municipios agregados",
            "taxa_atual": "Taxa atual",
            "meta_alfabetizacao": f"Meta {ano_label}",
            "taxa_simulada_conservador": "Conservador",
            "taxa_simulada_base": "Base",
            "taxa_simulada_acelerado": "Acelerado",
            "gap_base": "Gap base",
            "probabilidade_atingir_meta_base": "Prob. meta",
            "classe_risco_2030": f"Risco {ano_label}",
        }
    )
    for coluna in ["Taxa atual", f"Meta {ano_label}", "Conservador", "Base", "Acelerado", "Gap base", "Prob. meta"]:
        tabela[coluna] = tabela[coluna].apply(formatar_percentual)
    return tabela


HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulacao Alfabetizacao 2030</title>
    <style>
        :root {
            --bg: #f4f6f8;
            --panel: #ffffff;
            --text: #1f2933;
            --muted: #647180;
            --line: #d9e0e8;
            --accent: #176b87;
            --accent-soft: #e4f1f5;
            --good: #2f7d4f;
            --warn: #b56b16;
            --bad: #b63d3d;
            --critical: #7a2531;
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            background: var(--bg);
            color: var(--text);
            font-family: Arial, Helvetica, sans-serif;
        }

        .shell {
            width: min(1440px, calc(100% - 32px));
            margin: 0 auto;
            padding: 24px 0 36px;
        }

        header {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: flex-end;
            margin-bottom: 18px;
        }

        h1 {
            margin: 0 0 6px;
            font-size: 28px;
            line-height: 1.15;
        }

        .subtitle {
            margin: 0;
            color: var(--muted);
            font-size: 14px;
        }

        .badge {
            border: 1px solid var(--line);
            background: var(--panel);
            border-radius: 6px;
            padding: 8px 10px;
            color: var(--muted);
            font-size: 12px;
            white-space: nowrap;
        }

        .filters {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 16px;
            display: grid;
            grid-template-columns: 150px 140px 140px 190px minmax(220px, 1fr) 120px;
            gap: 12px;
            align-items: end;
        }

        label {
            display: block;
            color: var(--muted);
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 6px;
        }

        select, input {
            width: 100%;
            border: 1px solid var(--line);
            border-radius: 6px;
            padding: 9px 10px;
            font-size: 14px;
            background: #ffffff;
            color: var(--text);
        }

        button {
            border: 0;
            border-radius: 6px;
            padding: 10px 14px;
            background: var(--accent);
            color: #ffffff;
            font-weight: 700;
            cursor: pointer;
        }

        .metrics {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 12px;
            margin: 16px 0;
        }

        .explanation {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 16px;
            margin-top: 16px;
        }

        .explanation h2 {
            margin: 0 0 8px;
            font-size: 17px;
        }

        .explanation p {
            margin: 0 0 10px;
            color: var(--muted);
            font-size: 14px;
            line-height: 1.45;
        }

        .explanation ul {
            margin: 0;
            padding-left: 18px;
            color: var(--muted);
            font-size: 14px;
            line-height: 1.55;
        }

        .metric {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 14px;
            min-height: 86px;
        }

        .metric span {
            display: block;
            color: var(--muted);
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .metric strong {
            font-size: 25px;
            line-height: 1.1;
        }

        .grid {
            display: grid;
            grid-template-columns: 1.5fr 1fr;
            gap: 16px;
            align-items: start;
        }

        .panel {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
        }

        .panel h2 {
            margin: 0;
            padding: 14px 16px;
            border-bottom: 1px solid var(--line);
            font-size: 17px;
        }

        .panel-body {
            padding: 16px;
        }

        .line-chart {
            height: 300px;
            display: grid;
            grid-template-columns: 56px 1fr;
            gap: 12px;
            align-items: stretch;
        }

        .axis {
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            color: var(--muted);
            font-size: 12px;
            text-align: right;
        }

        .plot {
            position: relative;
            border-left: 1px solid var(--line);
            border-bottom: 1px solid var(--line);
            background: linear-gradient(to bottom, #eef3f7 1px, transparent 1px);
            background-size: 100% 25%;
            min-width: 0;
        }

        .point {
            position: absolute;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            transform: translate(-50%, 50%);
        }

        .point.conservador { background: var(--warn); }
        .point.base { background: var(--accent); }
        .point.acelerado { background: var(--good); }
        .point.meta { background: var(--bad); }

        .legend {
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
            margin-top: 14px;
            color: var(--muted);
            font-size: 13px;
        }

        .legend span::before {
            content: "";
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 6px;
        }

        .legend .conservador::before { background: var(--warn); }
        .legend .base::before { background: var(--accent); }
        .legend .acelerado::before { background: var(--good); }
        .legend .meta::before { background: var(--bad); }

        .risk-row {
            display: grid;
            grid-template-columns: 128px 1fr 72px;
            gap: 10px;
            align-items: center;
            margin-bottom: 12px;
            font-size: 13px;
        }

        .bar-track {
            height: 14px;
            background: #edf1f5;
            border-radius: 4px;
            overflow: hidden;
        }

        .bar {
            height: 100%;
            background: var(--accent);
        }

        .risk-row:nth-child(1) .bar { background: var(--good); }
        .risk-row:nth-child(2) .bar { background: #65a36f; }
        .risk-row:nth-child(3) .bar { background: var(--warn); }
        .risk-row:nth-child(4) .bar { background: var(--bad); }
        .risk-row:nth-child(5) .bar { background: var(--critical); }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        th, td {
            padding: 10px 9px;
            border-bottom: 1px solid var(--line);
            text-align: left;
            white-space: nowrap;
        }

        th {
            background: #f8fafc;
            color: var(--muted);
            font-size: 12px;
            cursor: help;
        }

        .table-wrap {
            overflow-x: auto;
        }

        .uf-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
            gap: 10px;
        }

        .uf-card {
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 11px;
            background: #fbfcfd;
        }

        .uf-card strong {
            display: block;
            font-size: 18px;
            margin-bottom: 6px;
        }

        .uf-card span {
            display: block;
            color: var(--muted);
            font-size: 12px;
            line-height: 1.55;
        }

        @media (max-width: 980px) {
            header { display: block; }
            .badge { display: inline-block; margin-top: 12px; }
            .filters, .metrics, .grid { grid-template-columns: 1fr; }
            .line-chart { grid-template-columns: 42px 1fr; }
        }
    </style>
</head>
<body>
    <div class="shell">
        <header>
            <div>
                <h1>Simulacao de Alfabetizacao ate 2030</h1>
                <p class="subtitle">Cenarios municipais baseados no resultado observado mais recente e nas metas oficiais anuais.</p>
            </div>
            <div class="badge">gold.simulacao_alfabetizacao_2030</div>
        </header>

        <form class="filters" method="get">
            <div>
                <label for="nivel">Nivel de analise</label>
                <select id="nivel" name="nivel" onchange="this.form.submit()">
                    {% for valor, rotulo in opcoes.niveis.items() %}
                    <option value="{{ valor }}" {% if filtros.nivel == valor %}selected{% endif %}>{{ rotulo }}</option>
                    {% endfor %}
                </select>
            </div>
            <div>
                <label for="ano">Ano simulado</label>
                <select id="ano" name="ano" onchange="this.form.submit()">
                    <option value="todos" {% if filtros.ano == 'todos' %}selected{% endif %}>Todos</option>
                    {% for item in opcoes.anos %}
                    <option value="{{ item }}" {% if filtros.ano == item %}selected{% endif %}>{{ item }}</option>
                    {% endfor %}
                </select>
            </div>
            <div>
                <label for="uf">UF</label>
                <select id="uf" name="uf" onchange="this.form.submit()">
                    <option value="todas" {% if filtros.uf == 'todas' %}selected{% endif %}>Todas</option>
                    {% for item in opcoes.ufs %}
                    <option value="{{ item }}" {% if filtros.uf == item %}selected{% endif %}>{{ item }}</option>
                    {% endfor %}
                </select>
            </div>
            <div>
                <label for="risco">Risco {{ ano_label }}</label>
                <select id="risco" name="risco" onchange="this.form.submit()">
                    <option value="todos" {% if filtros.risco == 'todos' %}selected{% endif %}>Todos</option>
                    {% for item in opcoes.riscos %}
                    <option value="{{ item }}" {% if filtros.risco == item %}selected{% endif %}>{{ item }}</option>
                    {% endfor %}
                </select>
            </div>
            <div>
                <label for="busca">Municipio ou codigo</label>
                <input id="busca" name="busca" value="{{ filtros.busca }}" placeholder="Buscar municipio" {% if filtros.nivel != 'municipio' %}disabled{% endif %}>
            </div>
            <button type="submit">Filtrar</button>
        </form>

        <section class="explanation">
            <h2>Como interpretar esta simulacao</h2>
            <p>Este dashboard usa o resultado municipal observado mais recente como ponto de partida e compara a evolucao simulada com as metas oficiais anuais ate 2030. A simulacao e gerada no nivel Municipio; ao selecionar UF ou Brasil, o painel agrega os municipios simulados para permitir leitura estadual ou nacional.</p>
            <ul>
                <li><strong>Conservador:</strong> crescimento mais lento da taxa de alfabetizacao.</li>
                <li><strong>Base:</strong> crescimento esperado considerando o gap ate a meta e a participacao na avaliacao.</li>
                <li><strong>Acelerado:</strong> cenario otimista, simulando maior avanco por intervencoes e politicas publicas.</li>
                <li><strong>Risco:</strong> classifica a unidade selecionada conforme a distancia ate a meta no cenario base.</li>
            </ul>
        </section>

        <section class="metrics">
            <div class="metric"><span>{{ metricas.label_total }} em {{ ano_label }}</span><strong>{{ metricas.total }}</strong></div>
            <div class="metric"><span>Media simulada base</span><strong>{{ metricas.media_base }}</strong></div>
            <div class="metric"><span>Meta media {{ ano_label }}</span><strong>{{ metricas.media_meta }}</strong></div>
            <div class="metric"><span>Meta atingida</span><strong>{{ metricas.atingem }}</strong></div>
            <div class="metric"><span>Risco critico</span><strong>{{ metricas.risco_critico }}</strong></div>
        </section>

        <section class="grid">
            <div class="panel">
                <h2>Evolucao media por cenario</h2>
                <div class="panel-body">
                    <div class="line-chart">
                        <div class="axis"><span>100%</span><span>75%</span><span>50%</span><span>25%</span><span>0%</span></div>
                        <div class="plot">
                            {% for ponto in serie %}
                                {% set x = loop.index0 * 100 / ((serie|length) - 1 if (serie|length) > 1 else 1) %}
                                <span class="point conservador" style="left: {{ x }}%; bottom: {{ ponto.conservador }}%;" title="{{ ponto.ano }} conservador: {{ ponto.conservador }}%"></span>
                                <span class="point base" style="left: {{ x }}%; bottom: {{ ponto.base }}%;" title="{{ ponto.ano }} base: {{ ponto.base }}%"></span>
                                <span class="point acelerado" style="left: {{ x }}%; bottom: {{ ponto.acelerado }}%;" title="{{ ponto.ano }} acelerado: {{ ponto.acelerado }}%"></span>
                                <span class="point meta" style="left: {{ x }}%; bottom: {{ ponto.meta }}%;" title="{{ ponto.ano }} meta: {{ ponto.meta }}%"></span>
                            {% endfor %}
                        </div>
                    </div>
                    <div class="legend">
                        <span class="conservador">Conservador</span>
                        <span class="base">Base</span>
                        <span class="acelerado">Acelerado</span>
                        <span class="meta">Meta</span>
                    </div>
                </div>
            </div>

            <div class="panel">
                <h2>Distribuicao de risco em {{ ano_label }}</h2>
                <div class="panel-body">
                    {% for item in riscos %}
                    <div class="risk-row">
                        <strong>{{ item.classe }}</strong>
                        <div class="bar-track"><div class="bar" style="width: {{ item.largura }}"></div></div>
                        <span>{{ item.quantidade }}</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </section>

        {% if filtros.nivel == 'municipio' %}
        <section class="panel" style="margin-top: 16px;">
            <h2>Resumo por UF em {{ ano_label }}</h2>
            <div class="panel-body">
                <div class="uf-grid">
                    {% for item in resumo_uf %}
                    <div class="uf-card">
                        <strong>{{ item.sigla_uf }}</strong>
                        <span>Media base: {{ "%.2f"|format(item.taxa_base_media) }}%</span>
                        <span>Meta media: {{ "%.2f"|format(item.meta_media) }}%</span>
                        <span>Gap medio: {{ "%.2f"|format(item.gap_medio) }} p.p.</span>
                        <span>Criticos: {{ item.risco_critico }}</span>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </section>
        {% endif %}

        <section class="panel" style="margin-top: 16px;">
            <h2>{{ nivel_label }} prioritarios no cenario base</h2>
            <div class="table-wrap">
                {{ tabela|safe }}
            </div>
        </section>
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    df = carregar_gold_particionado(TABELA_SIMULACAO)
    opcoes = {
        "anos": sorted(df["ano"].dropna().astype(int).astype(str).unique()),
        "ufs": sorted(df["sigla_uf"].dropna().astype(str).unique()),
        "riscos": CLASSES_RISCO,
        "niveis": NIVEIS_ANALISE,
    }
    filtros = {
        "nivel": request.args.get("nivel", "municipio"),
        "ano": request.args.get("ano", "todos"),
        "uf": request.args.get("uf", "todas"),
        "risco": request.args.get("risco", "todos"),
        "busca": request.args.get("busca", "").strip(),
    }
    if filtros["nivel"] not in NIVEIS_ANALISE:
        filtros["nivel"] = "municipio"

    df_filtrado = filtrar_dados(df, **filtros)
    ano_label = rotulo_ano_analise(filtros["ano"])
    nivel_label = NIVEIS_ANALISE[filtros["nivel"]]
    tabela = montar_listagem(
        df_filtrado,
        filtros["ano"],
        ano_label,
        filtros["nivel"],
    )
    html_tabela = tabela.to_html(
        index=False,
        classes="data-table",
    )
    html_tabela = adicionar_tooltips_cabecalho(html_tabela, list(tabela.columns))

    return render_template_string(
        HTML,
        filtros=filtros,
        opcoes=opcoes,
        ano_label=ano_label,
        nivel_label=nivel_label,
        metricas=montar_metricas(df_filtrado, filtros["ano"], nivel_label),
        serie=serie_nacional(df_filtrado),
        riscos=barras_risco(df_filtrado, filtros["ano"]),
        resumo_uf=resumo_por_uf(df, filtros["ano"]).head(12).to_dict("records"),
        tabela=html_tabela,
    )


if __name__ == "__main__":
    app.run(debug=False, port=5005, use_reloader=False)
