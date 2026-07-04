from pathlib import Path
import json

import pandas as pd
from flask import Flask, render_template_string, request


app = Flask(__name__)

BASE_PATH = Path(__file__).resolve().parents[1]
GOLD_PATH = BASE_PATH / "data" / "gold"
GEOJSON_PATH = BASE_PATH / "app" / "brasil_estados.geojson"
TABELA_UF = "indicador_meta_uf"

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


def filtrar_dados(df: pd.DataFrame, ano: str, rede: str) -> pd.DataFrame:
    dados = df.copy()

    if ano != "todos":
        dados = dados[dados["ano"].astype(str) == ano]

    if rede != "todas":
        dados = dados[dados["rede"] == rede]

    return dados.sort_values(["sigla_uf", "rede"]).drop_duplicates("sigla_uf")


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
            cursor: default;
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
                            <path class="uf"
                                  d="{{ estado.path }}"
                                  fill="{{ estado.cor }}">
                                <title>{{ estado.sigla }} - {{ estado.nome }} | Taxa: {{ estado.taxa }} | Meta: {{ estado.meta }} | {{ estado.status }}</title>
                            </path>
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


if __name__ == "__main__":
    app.run(debug=False, port=5004, use_reloader=False)
