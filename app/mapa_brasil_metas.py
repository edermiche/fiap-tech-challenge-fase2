from pathlib import Path
import json

import pandas as pd
from flask import Flask, render_template_string, request


app = Flask(__name__)

BASE_PATH = Path(__file__).resolve().parents[1]
GOLD_PATH = BASE_PATH / "data" / "gold"
SILVER_PATH = BASE_PATH / "data" / "silver"
GEOJSON_PATH = BASE_PATH / "app" / "brasil_estados.geojson"
GEOJSON_MUNICIPIOS_PATH = BASE_PATH / "app" / "brasil_municipios.geojson"
TABELA_UF = "indicador_meta_uf"
TABELA_MUNICIPIO = "indicador_meta_municipio"
TABELAS_CIDADE = [
    "indicador_meta_municipio",
    "indicador_meta_uf",
    "indicador_meta_brasil",
    "ranking_municipio_prioritario",
    "ranking_uf_prioritaria",
    "resumo_status_meta",
    "evolucao_alfabetizacao",
]

CODIGO_UF_POR_SIGLA = {
    "RO": "11",
    "AC": "12",
    "AM": "13",
    "RR": "14",
    "PA": "15",
    "AP": "16",
    "TO": "17",
    "MA": "21",
    "PI": "22",
    "CE": "23",
    "RN": "24",
    "PB": "25",
    "PE": "26",
    "AL": "27",
    "SE": "28",
    "BA": "29",
    "MG": "31",
    "ES": "32",
    "RJ": "33",
    "SP": "35",
    "PR": "41",
    "SC": "42",
    "RS": "43",
    "MS": "50",
    "MT": "51",
    "GO": "52",
    "DF": "53",
}
SIGLA_UF_POR_CODIGO = {
    codigo_uf: sigla_uf
    for sigla_uf, codigo_uf in CODIGO_UF_POR_SIGLA.items()
}

CORES_STATUS = {
    "Meta atingida": "#2f8f5b",
    "Abaixo da meta": "#f3a6a6",
    "Sem informacao": "#d5dbe3",
}

def carregar_indicador_uf() -> pd.DataFrame:
    caminho_tabela = GOLD_PATH / TABELA_UF
    arquivos = sorted(caminho_tabela.rglob("*.parquet"))

    if not arquivos:
        raise FileNotFoundError(f"Nenhum parquet encontrado para gold.{TABELA_UF}")

    frames = []
    for arquivo in arquivos:
        df_particao = pd.read_parquet(arquivo)

        if "ano" not in df_particao.columns and arquivo.parent.name.startswith("ano="):
            df_particao.insert(0, "ano", int(arquivo.parent.name.split("=", 1)[1]))

        frames.append(df_particao)

    return pd.concat(frames, ignore_index=True)


def carregar_indicador_municipio() -> pd.DataFrame:
    caminho_tabela = GOLD_PATH / TABELA_MUNICIPIO
    arquivos = sorted(caminho_tabela.rglob("*.parquet"))

    if not arquivos:
        raise FileNotFoundError(f"Nenhum parquet encontrado para gold.{TABELA_MUNICIPIO}")

    frames = []
    for arquivo in arquivos:
        df_particao = pd.read_parquet(arquivo)

        if "ano" not in df_particao.columns and arquivo.parent.name.startswith("ano="):
            df_particao.insert(0, "ano", int(arquivo.parent.name.split("=", 1)[1]))

        frames.append(df_particao)

    df = pd.concat(frames, ignore_index=True)

    if "sigla_uf" not in df.columns and "id_municipio" in df.columns:
        df["sigla_uf"] = (
            df["id_municipio"]
            .astype(str)
            .str[:2]
            .map(SIGLA_UF_POR_CODIGO)
        )

    if "id_municipio_nome" not in df.columns and "id_municipio" in df.columns:
        df["id_municipio_nome"] = df["id_municipio"].astype(str)

    df = enriquecer_nomes_municipio(df)

    return df


def carregar_dim_municipio() -> pd.DataFrame:
    caminho_tabela = SILVER_PATH / "dim_municipio"
    arquivos = sorted(caminho_tabela.rglob("*.parquet"))

    if not arquivos:
        return pd.DataFrame(columns=["id_municipio", "id_municipio_nome"])

    arquivo = max(arquivos, key=lambda caminho: caminho.stat().st_mtime)
    return pd.read_parquet(arquivo, columns=["id_municipio", "id_municipio_nome"])


def enriquecer_nomes_municipio(df: pd.DataFrame) -> pd.DataFrame:
    if "id_municipio" not in df.columns:
        return df

    dim_municipio = carregar_dim_municipio()
    if dim_municipio.empty:
        return df

    df_enriquecido = df.copy()
    df_enriquecido["id_municipio"] = df_enriquecido["id_municipio"].astype(str)
    dim_municipio = dim_municipio.copy()
    dim_municipio["id_municipio"] = dim_municipio["id_municipio"].astype(str)

    if "id_municipio_nome" in df_enriquecido.columns:
        df_enriquecido = df_enriquecido.drop(columns=["id_municipio_nome"])

    return df_enriquecido.merge(
        dim_municipio.drop_duplicates("id_municipio"),
        on="id_municipio",
        how="left",
    )


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

    df = pd.concat(frames, ignore_index=True)

    if "id_municipio" in df.columns:
        df = enriquecer_nomes_municipio(df)

    if "sigla_uf" not in df.columns and "id_municipio" in df.columns:
        df["sigla_uf"] = (
            df["id_municipio"]
            .astype(str)
            .str[:2]
            .map(SIGLA_UF_POR_CODIGO)
        )

    return df


def status_normalizado(status: str | None) -> str:
    if status == "Meta atingida":
        return "Meta atingida"

    if status == "Abaixo da meta":
        return "Abaixo da meta"

    return "Sem informacao"


def formatar_percentual(valor) -> str:
    if pd.isna(valor):
        return "-"

    return f"{float(valor):.2f}%"


def carregar_geojson() -> dict:
    if not GEOJSON_PATH.exists():
        raise FileNotFoundError(f"GeoJSON do mapa nao encontrado: {GEOJSON_PATH}")

    with GEOJSON_PATH.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def carregar_geojson_municipios() -> dict:
    if not GEOJSON_MUNICIPIOS_PATH.exists():
        raise FileNotFoundError(
            f"GeoJSON dos municipios nao encontrado: {GEOJSON_MUNICIPIOS_PATH}"
        )

    with GEOJSON_MUNICIPIOS_PATH.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)


def iterar_coordenadas(geometry: dict):
    if geometry["type"] == "Polygon":
        for anel in geometry["coordinates"]:
            for lon, lat in anel:
                yield lon, lat

    if geometry["type"] == "MultiPolygon":
        for poligono in geometry["coordinates"]:
            for anel in poligono:
                for lon, lat in anel:
                    yield lon, lat


def criar_projetor(geojson: dict):
    coordenadas = [
        coordenada
        for feature in geojson["features"]
        for coordenada in iterar_coordenadas(feature["geometry"])
    ]
    min_lon = min(lon for lon, _ in coordenadas)
    max_lon = max(lon for lon, _ in coordenadas)
    min_lat = min(lat for _, lat in coordenadas)
    max_lat = max(lat for _, lat in coordenadas)

    largura, altura, margem = 720, 720, 20
    escala = min(
        (largura - margem * 2) / (max_lon - min_lon),
        (altura - margem * 2) / (max_lat - min_lat),
    )
    largura_mapa = (max_lon - min_lon) * escala
    altura_mapa = (max_lat - min_lat) * escala
    deslocamento_x = (largura - largura_mapa) / 2
    deslocamento_y = (altura - altura_mapa) / 2

    def projetar(lon: float, lat: float) -> tuple[float, float]:
        x = deslocamento_x + (lon - min_lon) * escala
        y = deslocamento_y + (max_lat - lat) * escala
        return round(x, 2), round(y, 2)

    return projetar


def anel_para_path(anel: list, projetar) -> str:
    pontos = [projetar(lon, lat) for lon, lat in anel]
    if not pontos:
        return ""

    inicio = pontos[0]
    segmentos = [f"M {inicio[0]} {inicio[1]}"]
    segmentos.extend(f"L {x} {y}" for x, y in pontos[1:])
    segmentos.append("Z")

    return " ".join(segmentos)


def geometria_para_path(geometry: dict, projetar) -> str:
    if geometry["type"] == "Polygon":
        return " ".join(anel_para_path(anel, projetar) for anel in geometry["coordinates"])

    if geometry["type"] == "MultiPolygon":
        return " ".join(
            anel_para_path(anel, projetar)
            for poligono in geometry["coordinates"]
            for anel in poligono
        )

    return ""


def area_anel(anel: list) -> float:
    area = 0.0
    for indice, ponto in enumerate(anel):
        proximo = anel[(indice + 1) % len(anel)]
        area += ponto[0] * proximo[1] - proximo[0] * ponto[1]

    return abs(area) / 2


def maior_anel(geometry: dict) -> list:
    if geometry["type"] == "Polygon":
        return max(geometry["coordinates"], key=area_anel)

    aneis = [anel for poligono in geometry["coordinates"] for anel in poligono]
    return max(aneis, key=area_anel)


def centroide_aproximado(geometry: dict, projetar) -> tuple[float, float]:
    pontos = [projetar(lon, lat) for lon, lat in maior_anel(geometry)]
    min_x = min(x for x, _ in pontos)
    max_x = max(x for x, _ in pontos)
    min_y = min(y for _, y in pontos)
    max_y = max(y for _, y in pontos)

    return round((min_x + max_x) / 2, 2), round((min_y + max_y) / 2, 2)


def montar_estados(df: pd.DataFrame) -> list[dict[str, object]]:
    geojson = carregar_geojson()
    projetar = criar_projetor(geojson)
    estados = []

    for feature in geojson["features"]:
        sigla_uf = feature["properties"]["sigla"]
        registro = df[df["sigla_uf"] == sigla_uf]

        if registro.empty:
            status = "Sem informacao"
            nome = sigla_uf
            taxa = "-"
            meta = "-"
        else:
            linha_registro = registro.iloc[0]
            status = status_normalizado(linha_registro.get("status_meta"))
            nome = linha_registro.get("sigla_uf_nome") or sigla_uf
            taxa = formatar_percentual(linha_registro.get("taxa_alfabetizacao"))
            meta = formatar_percentual(linha_registro.get("meta_alfabetizacao"))

        estados.append(
            {
                "sigla": sigla_uf,
                "nome": nome,
                "path": geometria_para_path(feature["geometry"], projetar),
                "label_x": centroide_aproximado(feature["geometry"], projetar)[0],
                "label_y": centroide_aproximado(feature["geometry"], projetar)[1],
                "cor": CORES_STATUS[status],
                "status": status,
                "taxa": taxa,
                "meta": meta,
            }
        )

    return estados


def montar_municipios(df: pd.DataFrame, sigla_uf: str) -> list[dict[str, object]]:
    geojson = carregar_geojson_municipios()
    codigo_uf = CODIGO_UF_POR_SIGLA[sigla_uf]
    features = [
        feature
        for feature in geojson["features"]
        if str(feature["properties"]["id"]).startswith(codigo_uf)
    ]

    geojson_uf = {"type": "FeatureCollection", "features": features}
    projetar = criar_projetor(geojson_uf)
    municipios = []

    for feature in features:
        id_municipio = str(feature["properties"]["id"])
        registro = df[df["id_municipio"].astype(str) == id_municipio]

        if registro.empty:
            status = "Sem informacao"
            nome = feature["properties"].get("name") or id_municipio
            taxa = "-"
            meta = "-"
        else:
            linha_registro = registro.iloc[0]
            status = status_normalizado(linha_registro.get("status_meta"))
            nome = linha_registro.get("id_municipio_nome") or feature["properties"].get("name")
            taxa = formatar_percentual(linha_registro.get("taxa_alfabetizacao"))
            meta = formatar_percentual(linha_registro.get("meta_alfabetizacao"))

        municipios.append(
            {
                "id": id_municipio,
                "nome": nome,
                "path": geometria_para_path(feature["geometry"], projetar),
                "cor": CORES_STATUS[status],
                "status": status,
                "taxa": taxa,
                "meta": meta,
            }
        )

    return municipios


def filtrar_dados(df: pd.DataFrame, ano: str, rede: str) -> pd.DataFrame:
    dados = df.copy()

    if ano != "todos":
        dados = dados[dados["ano"].astype(str) == ano]

    if rede != "todas":
        dados = dados[dados["rede"] == rede]

    return dados.sort_values(["sigla_uf", "rede"]).drop_duplicates("sigla_uf")


def filtrar_dados_municipio(
    df: pd.DataFrame,
    sigla_uf: str,
    ano: str,
    rede: str,
) -> pd.DataFrame:
    dados = df[df["sigla_uf"] == sigla_uf].copy()

    if ano != "todos" and ano in dados["ano"].astype(str).unique():
        dados = dados[dados["ano"].astype(str) == ano]

    if rede != "todas" and rede in dados["rede"].astype(str).unique():
        dados = dados[dados["rede"] == rede]

    return dados.sort_values(["id_municipio", "rede"]).drop_duplicates("id_municipio")


def montar_opcoes_cidade(df: pd.DataFrame, sigla_uf: str) -> list[dict[str, str]]:
    cidades = (
        df[df["sigla_uf"] == sigla_uf][["id_municipio", "id_municipio_nome"]]
        .dropna(subset=["id_municipio"])
        .drop_duplicates("id_municipio")
        .sort_values("id_municipio_nome")
    )

    return [
        {
            "id": str(linha.id_municipio),
            "nome": str(linha.id_municipio_nome),
        }
        for linha in cidades.itertuples(index=False)
    ]


def obter_nome_cidade(df: pd.DataFrame, id_municipio: str) -> str:
    registro = df[df["id_municipio"].astype(str) == str(id_municipio)]

    if registro.empty:
        return str(id_municipio)

    return str(registro.iloc[0].get("id_municipio_nome") or id_municipio)


def formatar_valor_tabela(valor):
    if pd.isna(valor):
        return "-"

    if isinstance(valor, float):
        return round(valor, 4)

    return valor


def montar_secao_cidade(
    nome_tabela: str,
    id_municipio: str,
    sigla_uf: str,
    ano: str,
    rede: str,
) -> dict[str, str]:
    df = carregar_gold_particionado(nome_tabela)

    if "id_municipio" in df.columns:
        df = df[df["id_municipio"].astype(str) == str(id_municipio)].copy()
    elif "sigla_uf" in df.columns and sigla_uf:
        df = df[df["sigla_uf"].astype(str) == str(sigla_uf)].copy()
    else:
        df = df.copy()

    if ano != "todos" and "ano" in df.columns and ano in df["ano"].astype(str).unique():
        df = df[df["ano"].astype(str) == ano]

    if rede != "todas" and "rede" in df.columns and rede in df["rede"].astype(str).unique():
        df = df[df["rede"] == rede]

    df = df.map(formatar_valor_tabela)

    return {
        "nome": nome_tabela,
        "linhas": str(len(df)),
        "tabela": df.to_html(index=False, classes="data-table") if not df.empty else "",
    }


def montar_secoes_cidade(
    id_municipio: str,
    sigla_uf: str,
    ano: str,
    rede: str,
) -> list[dict[str, str]]:
    secoes = []

    for nome_tabela in TABELAS_CIDADE:
        try:
            secoes.append(
                montar_secao_cidade(
                    nome_tabela,
                    id_municipio,
                    sigla_uf,
                    ano,
                    rede,
                )
            )
        except FileNotFoundError:
            continue

    return secoes


def montar_metricas(df: pd.DataFrame) -> dict[str, str]:
    status = df["status_meta"].map(status_normalizado)

    return {
        "total": str(len(df)),
        "atingiram": str(int((status == "Meta atingida").sum())),
        "abaixo": str(int((status == "Abaixo da meta").sum())),
        "sem_info": str(int((status == "Sem informacao").sum())),
    }


def montar_opcoes(df: pd.DataFrame) -> dict[str, list[str]]:
    return {
        "anos": sorted(df["ano"].dropna().astype(int).astype(str).unique(), reverse=True),
        "redes": sorted(df["rede"].dropna().astype(str).unique()),
    }


def incluir_opcao_atual(opcoes: dict[str, list[str]], ano: str, rede: str) -> dict[str, list[str]]:
    opcoes_atualizadas = {
        "anos": list(opcoes["anos"]),
        "redes": list(opcoes["redes"]),
    }

    if ano and ano != "todos" and ano not in opcoes_atualizadas["anos"]:
        opcoes_atualizadas["anos"].insert(0, ano)

    if rede and rede != "todas" and rede not in opcoes_atualizadas["redes"]:
        opcoes_atualizadas["redes"].insert(0, rede)

    return opcoes_atualizadas


HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa Brasil - Metas de Alfabetizacao</title>
    <style>
        :root {
            --bg: #f5f7fa;
            --panel: #ffffff;
            --text: #1f2933;
            --muted: #607080;
            --line: #d8dee6;
            --accent: #176b87;
            --green: #2f8f5b;
            --red: #f3a6a6;
            --gray: #d5dbe3;
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
            width: min(1180px, calc(100% - 32px));
            margin: 0 auto;
            padding: 24px 0 32px;
        }

        header {
            margin-bottom: 18px;
        }

        h1 {
            margin: 0 0 6px;
            font-size: 28px;
        }

        .subtitle {
            margin: 0;
            color: var(--muted);
            font-size: 14px;
        }

        .filters,
        .metrics,
        .map-panel,
        .legend {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
        }

        .filters {
            display: grid;
            grid-template-columns: repeat(3, minmax(160px, 1fr));
            gap: 12px;
            padding: 16px;
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
            grid-template-columns: repeat(4, minmax(120px, 1fr));
            gap: 0;
            margin: 16px 0;
            overflow: hidden;
        }

        .metric {
            padding: 14px;
            border-right: 1px solid var(--line);
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
            font-size: 28px;
        }

        .content {
            display: grid;
            grid-template-columns: minmax(0, 1fr) 260px;
            gap: 16px;
            align-items: start;
        }

        .map-panel {
            padding: 12px;
            overflow: auto;
        }

        svg {
            display: block;
            width: 100%;
            min-width: 620px;
            height: auto;
        }

        .uf {
            stroke: #ffffff;
            stroke-linejoin: round;
            stroke-width: 1.2;
            cursor: pointer;
            fill-rule: evenodd;
        }

        .uf:hover {
            filter: brightness(0.96);
            stroke: #17202a;
            stroke-width: 1.4;
        }

        .map-outline {
            fill: none;
            stroke: #17202a;
            stroke-linejoin: round;
            stroke-width: 2.4;
            opacity: .85;
            pointer-events: none;
        }

        .uf-label {
            fill: #17202a;
            font-size: 10px;
            font-weight: 700;
            text-anchor: middle;
            dominant-baseline: central;
            pointer-events: none;
        }

        .tooltip {
            position: fixed;
            z-index: 10;
            display: none;
            min-width: 210px;
            max-width: 280px;
            padding: 10px 12px;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: #ffffff;
            box-shadow: 0 10px 30px rgba(23, 32, 42, .18);
            color: var(--text);
            font-size: 13px;
            pointer-events: none;
        }

        .tooltip strong {
            display: block;
            margin-bottom: 6px;
            font-size: 14px;
        }

        .tooltip span {
            display: block;
            color: var(--muted);
            line-height: 1.45;
        }

        .tooltip .approval {
            color: var(--text);
            font-size: 18px;
            font-weight: 700;
            margin: 2px 0 4px;
        }

        .legend {
            padding: 16px;
        }

        .legend h2 {
            margin: 0 0 12px;
            font-size: 18px;
        }

        .legend-item {
            display: grid;
            grid-template-columns: 18px 1fr;
            gap: 8px;
            align-items: center;
            margin-bottom: 10px;
            color: var(--muted);
            font-size: 14px;
        }

        .swatch {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid rgba(0, 0, 0, .08);
        }

        .erro {
            margin-top: 16px;
            background: #fff4f1;
            border: 1px solid #efc6bd;
            border-radius: 8px;
            color: #8a2d1c;
            padding: 16px;
        }

        @media (max-width: 900px) {
            .filters,
            .metrics,
            .content {
                grid-template-columns: 1fr;
            }

            .metric {
                border-right: 0;
                border-bottom: 1px solid var(--line);
            }

            .metric:last-child {
                border-bottom: 0;
            }
        }
    </style>
</head>
<body>
<main class="shell">
    <header>
        <h1>Mapa do Brasil por estado</h1>
        <p class="subtitle">Estados em verde bateram a meta; estados em vermelho claro ficaram abaixo da meta.</p>
    </header>

    <form class="filters" method="get">
        <label>
            Ano
            <select name="ano">
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

        <button type="submit">Atualizar mapa</button>
    </form>

    {% if erro %}
        <section class="erro">{{ erro }}</section>
    {% else %}
        <section class="metrics" aria-label="Resumo dos estados">
            <div class="metric"><span>Estados</span><strong>{{ metricas.total }}</strong></div>
            <div class="metric"><span>Meta atingida</span><strong>{{ metricas.atingiram }}</strong></div>
            <div class="metric"><span>Abaixo da meta</span><strong>{{ metricas.abaixo }}</strong></div>
            <div class="metric"><span>Sem informacao</span><strong>{{ metricas.sem_info }}</strong></div>
        </section>

        <section class="content">
            <div class="map-panel">
                <svg viewBox="0 0 720 720" role="img" aria-label="Mapa do Brasil por estado com contorno real">
                    {% for estado in estados %}
                        <g>
                            <a href="/estado/{{ estado.sigla }}?ano={{ ano }}&rede={{ rede|urlencode }}">
                                <path class="uf"
                                      d="{{ estado.path }}"
                                      fill="{{ estado.cor }}"
                                      data-sigla="{{ estado.sigla }}"
                                      data-nome="{{ estado.nome }}"
                                      data-taxa="{{ estado.taxa }}"
                                      data-meta="{{ estado.meta }}"
                                      data-status="{{ estado.status }}">
                                    <title>{{ estado.sigla }} - {{ estado.nome }} | Taxa: {{ estado.taxa }} | Meta: {{ estado.meta }} | {{ estado.status }}</title>
                                </path>
                            </a>
                            <text class="uf-label" x="{{ estado.label_x }}" y="{{ estado.label_y }}">{{ estado.sigla }}</text>
                        </g>
                    {% endfor %}
                </svg>
            </div>

            <aside class="legend">
                <h2>Legenda</h2>
                <div class="legend-item">
                    <span class="swatch" style="background: var(--green);"></span>
                    <span>Meta atingida</span>
                </div>
                <div class="legend-item">
                    <span class="swatch" style="background: var(--red);"></span>
                    <span>Abaixo da meta</span>
                </div>
                <div class="legend-item">
                    <span class="swatch" style="background: var(--gray);"></span>
                    <span>Sem informacao</span>
                </div>
            </aside>
        </section>
    {% endif %}
</main>
<div class="tooltip" id="map-tooltip" role="status" aria-live="polite"></div>
<script>
    const tooltip = document.getElementById("map-tooltip");
    const estados = document.querySelectorAll(".uf");

    function moverTooltip(event) {
        const margem = 14;
        const largura = tooltip.offsetWidth || 240;
        const altura = tooltip.offsetHeight || 120;
        let x = event.clientX + margem;
        let y = event.clientY + margem;

        if (x + largura > window.innerWidth) {
            x = event.clientX - largura - margem;
        }

        if (y + altura > window.innerHeight) {
            y = event.clientY - altura - margem;
        }

        tooltip.style.left = `${Math.max(margem, x)}px`;
        tooltip.style.top = `${Math.max(margem, y)}px`;
    }

    estados.forEach((estado) => {
        estado.addEventListener("mouseenter", (event) => {
            tooltip.innerHTML = `
                <strong>${estado.dataset.sigla} - ${estado.dataset.nome}</strong>
                <span>% de aprovacao</span>
                <div class="approval">${estado.dataset.taxa}</div>
                <span>Meta: ${estado.dataset.meta}</span>
                <span>Status: ${estado.dataset.status}</span>
            `;
            tooltip.style.display = "block";
            moverTooltip(event);
        });

        estado.addEventListener("mousemove", moverTooltip);

        estado.addEventListener("mouseleave", () => {
            tooltip.style.display = "none";
        });
    });
</script>
</body>
</html>
"""


HTML_ESTADO = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapa de Municipios - {{ sigla_uf }}</title>
    <style>
        :root {
            --bg: #f5f7fa;
            --panel: #ffffff;
            --text: #1f2933;
            --muted: #607080;
            --line: #d8dee6;
            --accent: #176b87;
            --green: #2f8f5b;
            --red: #f3a6a6;
            --gray: #d5dbe3;
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
            width: min(1180px, calc(100% - 32px));
            margin: 0 auto;
            padding: 24px 0 32px;
        }

        header {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: start;
            margin-bottom: 18px;
        }

        h1 {
            margin: 0 0 6px;
            font-size: 28px;
        }

        .subtitle {
            margin: 0;
            color: var(--muted);
            font-size: 14px;
        }

        .back-link {
            display: inline-flex;
            align-items: center;
            min-height: 38px;
            padding: 8px 12px;
            border-radius: 6px;
            background: var(--panel);
            border: 1px solid var(--line);
            color: var(--text);
            font-weight: 700;
            text-decoration: none;
            white-space: nowrap;
        }

        .filters,
        .metrics,
        .map-panel,
        .legend {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
        }

        .filters {
            display: grid;
            grid-template-columns: repeat(4, minmax(160px, 1fr));
            gap: 12px;
            padding: 16px;
            align-items: end;
        }

        .filter-summary {
            margin: 10px 0 0;
            color: var(--muted);
            font-size: 13px;
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
            grid-template-columns: repeat(4, minmax(120px, 1fr));
            gap: 0;
            margin: 16px 0;
            overflow: hidden;
        }

        .metric {
            padding: 14px;
            border-right: 1px solid var(--line);
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
            font-size: 28px;
        }

        .content {
            display: grid;
            grid-template-columns: minmax(0, 1fr) 260px;
            gap: 16px;
            align-items: start;
        }

        .map-panel {
            padding: 12px;
            overflow: auto;
        }

        svg {
            display: block;
            width: 100%;
            min-width: 620px;
            height: auto;
        }

        .municipio {
            stroke: #ffffff;
            stroke-linejoin: round;
            stroke-width: .75;
            cursor: pointer;
            fill-rule: evenodd;
        }

        .municipio:hover {
            filter: brightness(0.96);
            stroke: #17202a;
            stroke-width: 1.2;
        }

        .legend {
            padding: 16px;
        }

        .legend h2 {
            margin: 0 0 12px;
            font-size: 18px;
        }

        .legend-item {
            display: grid;
            grid-template-columns: 18px 1fr;
            gap: 8px;
            align-items: center;
            margin-bottom: 10px;
            color: var(--muted);
            font-size: 14px;
        }

        .swatch {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid rgba(0, 0, 0, .08);
        }

        .tooltip {
            position: fixed;
            z-index: 10;
            display: none;
            min-width: 230px;
            max-width: 300px;
            padding: 10px 12px;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: #ffffff;
            box-shadow: 0 10px 30px rgba(23, 32, 42, .18);
            color: var(--text);
            font-size: 13px;
            pointer-events: none;
        }

        .tooltip strong {
            display: block;
            margin-bottom: 6px;
            font-size: 14px;
        }

        .tooltip span {
            display: block;
            color: var(--muted);
            line-height: 1.45;
        }

        .tooltip .approval {
            color: var(--text);
            font-size: 18px;
            font-weight: 700;
            margin: 2px 0 4px;
        }

        .erro {
            margin-top: 16px;
            background: #fff4f1;
            border: 1px solid #efc6bd;
            border-radius: 8px;
            color: #8a2d1c;
            padding: 16px;
        }

        @media (max-width: 900px) {
            header,
            .filters,
            .metrics,
            .content {
                grid-template-columns: 1fr;
                display: grid;
            }

            .metric {
                border-right: 0;
                border-bottom: 1px solid var(--line);
            }

            .metric:last-child {
                border-bottom: 0;
            }
        }
    </style>
</head>
<body>
<main class="shell">
    <header>
        <div>
            <h1>Mapa de municipios - {{ sigla_uf }}</h1>
            <p class="subtitle">Cidades em verde atingiram a meta; cidades em vermelho claro ficaram abaixo da meta.</p>
        </div>
        <a class="back-link" href="/?ano={{ ano }}&rede={{ rede|urlencode }}">Voltar ao Brasil</a>
    </header>

    <form class="filters" method="get">
        <label>
            Ano
            <select name="ano">
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
            Cidade
            <select id="cidade-select" name="cidade">
                <option value="">Selecione uma cidade</option>
                {% for cidade in cidades %}
                    <option value="{{ cidade.id }}">{{ cidade.nome }}</option>
                {% endfor %}
            </select>
        </label>

        <button type="submit">Atualizar mapa</button>
    </form>
    <p class="filter-summary">Filtro aplicado: ano {{ ano }} | rede {{ rede }}</p>

    {% if erro %}
        <section class="erro">{{ erro }}</section>
    {% else %}
        <section class="metrics" aria-label="Resumo dos municipios">
            <div class="metric"><span>Municipios</span><strong>{{ metricas.total }}</strong></div>
            <div class="metric"><span>Meta atingida</span><strong>{{ metricas.atingiram }}</strong></div>
            <div class="metric"><span>Abaixo da meta</span><strong>{{ metricas.abaixo }}</strong></div>
            <div class="metric"><span>Sem informacao</span><strong>{{ metricas.sem_info }}</strong></div>
        </section>

        <section class="content">
            <div class="map-panel">
                <svg viewBox="0 0 720 720" role="img" aria-label="Mapa dos municipios de {{ sigla_uf }}">
                    {% for municipio in municipios %}
                        <a href="/cidade/{{ municipio.id }}?ano={{ ano }}&rede={{ rede|urlencode }}&uf={{ sigla_uf }}">
                            <path class="municipio"
                                  d="{{ municipio.path }}"
                                  fill="{{ municipio.cor }}"
                                  data-id="{{ municipio.id }}"
                                  data-nome="{{ municipio.nome }}"
                                  data-taxa="{{ municipio.taxa }}"
                                  data-meta="{{ municipio.meta }}"
                                  data-status="{{ municipio.status }}">
                                <title>{{ municipio.nome }} | Taxa: {{ municipio.taxa }} | Meta: {{ municipio.meta }} | {{ municipio.status }}</title>
                            </path>
                        </a>
                    {% endfor %}
                </svg>
            </div>

            <aside class="legend">
                <h2>Legenda</h2>
                <div class="legend-item">
                    <span class="swatch" style="background: var(--green);"></span>
                    <span>Meta atingida</span>
                </div>
                <div class="legend-item">
                    <span class="swatch" style="background: var(--red);"></span>
                    <span>Abaixo da meta</span>
                </div>
                <div class="legend-item">
                    <span class="swatch" style="background: var(--gray);"></span>
                    <span>Sem informacao</span>
                </div>
            </aside>
        </section>
    {% endif %}
</main>
<div class="tooltip" id="city-tooltip" role="status" aria-live="polite"></div>
<script>
    const tooltip = document.getElementById("city-tooltip");
    const municipios = document.querySelectorAll(".municipio");

    function moverTooltip(event) {
        const margem = 14;
        const largura = tooltip.offsetWidth || 250;
        const altura = tooltip.offsetHeight || 120;
        let x = event.clientX + margem;
        let y = event.clientY + margem;

        if (x + largura > window.innerWidth) {
            x = event.clientX - largura - margem;
        }

        if (y + altura > window.innerHeight) {
            y = event.clientY - altura - margem;
        }

        tooltip.style.left = `${Math.max(margem, x)}px`;
        tooltip.style.top = `${Math.max(margem, y)}px`;
    }

    municipios.forEach((municipio) => {
        municipio.addEventListener("mouseenter", (event) => {
            tooltip.innerHTML = `
                <strong>${municipio.dataset.nome}</strong>
                <span>% de aprovacao</span>
                <div class="approval">${municipio.dataset.taxa}</div>
                <span>Meta: ${municipio.dataset.meta}</span>
                <span>Status: ${municipio.dataset.status}</span>
            `;
            tooltip.style.display = "block";
            moverTooltip(event);
        });

        municipio.addEventListener("mousemove", moverTooltip);

        municipio.addEventListener("mouseleave", () => {
            tooltip.style.display = "none";
        });
    });

    const cidadeSelect = document.getElementById("cidade-select");
    if (cidadeSelect) {
        cidadeSelect.addEventListener("change", () => {
            if (!cidadeSelect.value) {
                return;
            }

            const params = new URLSearchParams(window.location.search);
            const ano = params.get("ano") || "{{ ano }}";
            const rede = params.get("rede") || "{{ rede }}";
            window.location.href = `/cidade/${cidadeSelect.value}?ano=${encodeURIComponent(ano)}&rede=${encodeURIComponent(rede)}&uf={{ sigla_uf }}`;
        });
    }
</script>
</body>
</html>
"""


HTML_CIDADE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Detalhe da Cidade - {{ nome_cidade }}</title>
    <style>
        :root {
            --bg: #f5f7fa;
            --panel: #ffffff;
            --text: #1f2933;
            --muted: #607080;
            --line: #d8dee6;
            --accent: #176b87;
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
            width: min(1280px, calc(100% - 32px));
            margin: 0 auto;
            padding: 24px 0 32px;
        }

        header {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: start;
            margin-bottom: 18px;
        }

        h1 {
            margin: 0 0 6px;
            font-size: 28px;
        }

        .subtitle {
            margin: 0;
            color: var(--muted);
            font-size: 14px;
        }

        .back-link {
            display: inline-flex;
            align-items: center;
            min-height: 38px;
            padding: 8px 12px;
            border-radius: 6px;
            background: var(--panel);
            border: 1px solid var(--line);
            color: var(--text);
            font-weight: 700;
            text-decoration: none;
            white-space: nowrap;
        }

        .summary,
        .section {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
        }

        .summary {
            display: grid;
            grid-template-columns: repeat(4, minmax(150px, 1fr));
            margin-bottom: 16px;
            overflow: hidden;
        }

        .summary-item {
            padding: 14px;
            border-right: 1px solid var(--line);
        }

        .summary-item:last-child {
            border-right: 0;
        }

        .summary-item span {
            display: block;
            color: var(--muted);
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 6px;
        }

        .summary-item strong {
            font-size: 18px;
        }

        .section {
            margin-bottom: 16px;
            overflow: hidden;
        }

        .section-head {
            padding: 14px 16px;
            border-bottom: 1px solid var(--line);
            display: flex;
            justify-content: space-between;
            gap: 12px;
            align-items: center;
        }

        .section-head h2 {
            margin: 0;
            font-size: 18px;
        }

        .section-head span {
            color: var(--muted);
            font-size: 13px;
            white-space: nowrap;
        }

        .table-wrap {
            overflow: auto;
            max-height: 460px;
        }

        table {
            border-collapse: collapse;
            width: 100%;
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
            background: #e7f2f5;
            position: sticky;
            top: 0;
            z-index: 1;
        }

        .empty {
            padding: 16px;
            color: var(--muted);
        }

        .erro {
            background: #fff4f1;
            border: 1px solid #efc6bd;
            border-radius: 8px;
            color: #8a2d1c;
            padding: 16px;
        }

        @media (max-width: 900px) {
            header,
            .summary {
                display: grid;
                grid-template-columns: 1fr;
            }

            .summary-item {
                border-right: 0;
                border-bottom: 1px solid var(--line);
            }

            .summary-item:last-child {
                border-bottom: 0;
            }
        }
    </style>
</head>
<body>
<main class="shell">
    <header>
        <div>
            <h1>{{ nome_cidade }}</h1>
            <p class="subtitle">Todas as informacoes disponiveis nas tabelas Gold para esta cidade.</p>
        </div>
        <a class="back-link" href="/estado/{{ sigla_uf }}?ano={{ ano }}&rede={{ rede|urlencode }}">Voltar ao estado</a>
    </header>

    {% if erro %}
        <section class="erro">{{ erro }}</section>
    {% else %}
        <section class="summary">
            <div class="summary-item"><span>Codigo IBGE</span><strong>{{ id_municipio }}</strong></div>
            <div class="summary-item"><span>UF</span><strong>{{ sigla_uf }}</strong></div>
            <div class="summary-item"><span>Ano consultado</span><strong>{{ ano }}</strong></div>
            <div class="summary-item"><span>Rede consultada</span><strong>{{ rede }}</strong></div>
        </section>

        {% for secao in secoes %}
            <section class="section">
                <div class="section-head">
                    <h2>gold.{{ secao.nome }}</h2>
                    <span>{{ secao.linhas }} linhas</span>
                </div>
                {% if secao.tabela %}
                    <div class="table-wrap">{{ secao.tabela | safe }}</div>
                {% else %}
                    <div class="empty">Nenhum registro encontrado para os filtros informados.</div>
                {% endif %}
            </section>
        {% endfor %}
    {% endif %}
</main>
</body>
</html>
"""


@app.route("/")
def index():
    try:
        df = carregar_indicador_uf()
        opcoes = montar_opcoes(df)
        ano = request.args.get("ano", opcoes["anos"][0] if opcoes["anos"] else "todos")
        rede = request.args.get("rede", "todas")
        dados = filtrar_dados(df, ano, rede)

        return render_template_string(
            HTML,
            opcoes=opcoes,
            ano=ano,
            rede=rede,
            estados=montar_estados(dados),
            metricas=montar_metricas(dados),
            erro=None,
        )
    except Exception as erro:
        return render_template_string(
            HTML,
            opcoes={"anos": [], "redes": []},
            ano="",
            rede="todas",
            estados=[],
            metricas={},
            erro=str(erro),
        )


@app.route("/estado/<sigla_uf>")
def estado(sigla_uf: str):
    sigla_uf = sigla_uf.upper()

    if sigla_uf not in CODIGO_UF_POR_SIGLA:
        return render_template_string(
            HTML_ESTADO,
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
        df = carregar_indicador_municipio()
        opcoes = montar_opcoes(df)
        ano = request.args.get("ano", opcoes["anos"][0] if opcoes["anos"] else "todos")
        rede = request.args.get("rede", "todas")
        opcoes = incluir_opcao_atual(opcoes, ano, rede)
        dados = filtrar_dados_municipio(df, sigla_uf, ano, rede)

        return render_template_string(
            HTML_ESTADO,
            sigla_uf=sigla_uf,
            opcoes=opcoes,
            ano=ano,
            rede=rede,
            cidades=montar_opcoes_cidade(df, sigla_uf),
            municipios=montar_municipios(dados, sigla_uf),
            metricas=montar_metricas(dados),
            erro=None,
        )
    except Exception as erro:
        return render_template_string(
            HTML_ESTADO,
            sigla_uf=sigla_uf,
            opcoes={"anos": [], "redes": []},
            ano="",
            rede="todas",
            cidades=[],
            municipios=[],
            metricas={},
            erro=str(erro),
        )


@app.route("/cidade/<id_municipio>")
def cidade(id_municipio: str):
    ano = request.args.get("ano", "todos")
    rede = request.args.get("rede", "todas")
    sigla_uf = request.args.get("uf", "")

    try:
        df_municipio = carregar_indicador_municipio()
        registro = df_municipio[df_municipio["id_municipio"].astype(str) == str(id_municipio)]

        if registro.empty:
            raise FileNotFoundError(f"Municipio nao encontrado na Gold: {id_municipio}")

        if not sigla_uf:
            sigla_uf = str(registro.iloc[0].get("sigla_uf") or "")

        return render_template_string(
            HTML_CIDADE,
            id_municipio=id_municipio,
            nome_cidade=obter_nome_cidade(df_municipio, id_municipio),
            sigla_uf=sigla_uf,
            ano=ano,
            rede=rede,
            secoes=montar_secoes_cidade(id_municipio, sigla_uf, ano, rede),
            erro=None,
        )
    except Exception as erro:
        return render_template_string(
            HTML_CIDADE,
            id_municipio=id_municipio,
            nome_cidade=str(id_municipio),
            sigla_uf=sigla_uf,
            ano=ano,
            rede=rede,
            secoes=[],
            erro=str(erro),
        )


if __name__ == "__main__":
    app.run(debug=False, port=5004, use_reloader=False)
