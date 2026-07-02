from pathlib import Path

import pandas as pd
from flask import Flask, render_template_string, request


app = Flask(__name__)

BASE_PATH = Path(__file__).resolve().parents[1]

CAMADAS = {
    "bronze": {
        "nome": "Bronze",
        "prefixo": "bronze",
        "caminho": BASE_PATH / "data" / "bronze",
    },
    "silver": {
        "nome": "Silver",
        "prefixo": "silver",
        "caminho": BASE_PATH / "data" / "silver",
    },
    "gold": {
        "nome": "Gold",
        "prefixo": "gold",
        "caminho": BASE_PATH / "data" / "gold",
    },
}


def localizar_parquet_mais_recente(caminho_tabela: Path) -> Path | None:
    arquivos = list(caminho_tabela.rglob("*.parquet"))

    if not arquivos:
        return None

    return max(arquivos, key=lambda arquivo: arquivo.stat().st_mtime)


def listar_tabelas(camada: str) -> list[str]:
    caminho_camada = CAMADAS[camada]["caminho"]

    if not caminho_camada.exists():
        return []

    tabelas = []

    for caminho in sorted(caminho_camada.iterdir()):
        if caminho.is_dir() and localizar_parquet_mais_recente(caminho):
            tabelas.append(caminho.name)

    return tabelas


def carregar_tabela(camada: str, nome_tabela: str) -> pd.DataFrame:
    caminho_camada = CAMADAS[camada]["caminho"]
    prefixo = CAMADAS[camada]["prefixo"]
    arquivo = localizar_parquet_mais_recente(caminho_camada / nome_tabela)

    if arquivo is None:
        raise FileNotFoundError(
            f"Nenhum parquet encontrado para {prefixo}.{nome_tabela}"
        )

    return pd.read_parquet(arquivo)


def montar_tabela_colunas(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "coluna": df.columns,
            "tipo": [str(df[coluna].dtype) for coluna in df.columns],
            "nulos": [int(df[coluna].isna().sum()) for coluna in df.columns],
        }
    )


HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Validador Medalhao</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 30px;
            background: #f6f6f6;
            color: #222;
        }

        .container {
            max-width: 1280px;
            margin: auto;
        }

        .card {
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,.08);
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 16px;
        }

        .metric-box {
            background: #f5f8fb;
            border-left: 5px solid #1f4e79;
            border-radius: 8px;
            padding: 14px;
        }

        .metric-box h3 {
            margin: 0 0 8px 0;
            font-size: 14px;
            color: #555;
        }

        .metric-box p {
            margin: 0;
            font-size: 18px;
            font-weight: bold;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            font-size: 13px;
        }

        th, td {
            border: 1px solid #ddd;
            padding: 6px;
            text-align: left;
            white-space: nowrap;
        }

        th {
            background: #eee;
        }

        .table-wrapper {
            overflow-x: auto;
        }

        label {
            display: block;
            font-weight: bold;
            margin-top: 12px;
        }

        select, button {
            padding: 8px;
            margin-top: 8px;
            width: 100%;
            max-width: 480px;
        }

        button {
            background: #1f4e79;
            border: 0;
            border-radius: 6px;
            color: white;
            cursor: pointer;
            font-weight: bold;
        }

        .erro {
            color: #b00020;
            font-weight: bold;
        }

        @media (max-width: 900px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
<div class="container">

    <div class="card">
        <h1>Validador das Camadas Bronze, Silver e Gold</h1>
        <p>Caminho selecionado: <b>{{ caminho_camada }}</b></p>

        <form method="get">
            <label>Camada</label>
            <select name="camada" onchange="this.form.submit()">
                {% for chave, dados in camadas.items() %}
                    <option value="{{ chave }}" {% if chave == camada_selecionada %}selected{% endif %}>
                        {{ dados.nome }}
                    </option>
                {% endfor %}
            </select>

            <label>Tabela</label>
            <select name="tabela">
                {% for tabela in tabelas %}
                    <option value="{{ tabela }}" {% if tabela == tabela_selecionada %}selected{% endif %}>
                        {{ prefixo }}.{{ tabela }}
                    </option>
                {% endfor %}
            </select>

            <button type="submit">Carregar</button>
        </form>
    </div>

    {% if erro %}
    <div class="card">
        <h2>Erro</h2>
        <p class="erro">{{ erro }}</p>
    </div>
    {% endif %}

    {% if tabela_selecionada and not erro %}
    <div class="grid">
        <div class="metric-box">
            <h3>Camada</h3>
            <p>{{ nome_camada }}</p>
        </div>

        <div class="metric-box">
            <h3>Linhas</h3>
            <p>{{ linhas }}</p>
        </div>

        <div class="metric-box">
            <h3>Colunas</h3>
            <p>{{ colunas }}</p>
        </div>
    </div>

    <br>

    <div class="card">
        <h2>{{ prefixo }}.{{ tabela_selecionada }}</h2>
    </div>

    <div class="card">
        <h2>Colunas</h2>
        <div class="table-wrapper">
            {{ tabela_colunas | safe }}
        </div>
    </div>

    <div class="card">
        <h2>Resumo numerico</h2>
        <div class="table-wrapper">
            {{ resumo | safe }}
        </div>
    </div>

    <div class="card">
        <h2>Amostra dos dados</h2>
        <div class="table-wrapper">
            {{ preview | safe }}
        </div>
    </div>
    {% endif %}

</div>
</body>
</html>
"""


@app.route("/")
def index():
    camada_selecionada = request.args.get("camada", "bronze")

    if camada_selecionada not in CAMADAS:
        camada_selecionada = "bronze"

    dados_camada = CAMADAS[camada_selecionada]
    tabelas = listar_tabelas(camada_selecionada)
    tabela_selecionada = request.args.get("tabela")

    if not tabelas:
        return render_template_string(
            HTML,
            camadas=CAMADAS,
            camada_selecionada=camada_selecionada,
            nome_camada=dados_camada["nome"],
            prefixo=dados_camada["prefixo"],
            caminho_camada=dados_camada["caminho"],
            tabelas=[],
            tabela_selecionada=None,
            erro=f"Nenhuma tabela {dados_camada['nome']} encontrada.",
            linhas=0,
            colunas=0,
            tabela_colunas="",
            resumo="",
            preview="",
        )

    if tabela_selecionada not in tabelas:
        tabela_selecionada = tabelas[0]

    try:
        df = carregar_tabela(camada_selecionada, tabela_selecionada)
        df_colunas = montar_tabela_colunas(df)
        resumo = df.describe(include="all").transpose().reset_index()
        resumo = resumo.rename(columns={"index": "coluna"})

        return render_template_string(
            HTML,
            camadas=CAMADAS,
            camada_selecionada=camada_selecionada,
            nome_camada=dados_camada["nome"],
            prefixo=dados_camada["prefixo"],
            caminho_camada=dados_camada["caminho"],
            tabelas=tabelas,
            tabela_selecionada=tabela_selecionada,
            erro=None,
            linhas=len(df),
            colunas=len(df.columns),
            tabela_colunas=df_colunas.to_html(index=False),
            resumo=resumo.to_html(index=False),
            preview=df.head(50).to_html(index=False),
        )

    except Exception as erro:
        return render_template_string(
            HTML,
            camadas=CAMADAS,
            camada_selecionada=camada_selecionada,
            nome_camada=dados_camada["nome"],
            prefixo=dados_camada["prefixo"],
            caminho_camada=dados_camada["caminho"],
            tabelas=tabelas,
            tabela_selecionada=tabela_selecionada,
            erro=str(erro),
            linhas=0,
            colunas=0,
            tabela_colunas="",
            resumo="",
            preview="",
        )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
