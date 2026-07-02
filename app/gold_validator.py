from pathlib import Path

import pandas as pd
from flask import Flask, request, render_template_string

app = Flask(__name__)

BASE_PATH = Path(__file__).resolve().parents[1]
GOLD_PATH = BASE_PATH / "data" / "gold"


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


def carregar_gold(nome_tabela: str) -> pd.DataFrame:
    arquivo = localizar_parquet_mais_recente(GOLD_PATH / nome_tabela)

    if arquivo is None:
        raise FileNotFoundError(f"Nenhum parquet encontrado para gold.{nome_tabela}")

    return pd.read_parquet(arquivo)


HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Validador Gold</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 30px;
            background: #f6f6f6;
        }

        .card {
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,.08);
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

        select, button {
            padding: 8px;
            margin-top: 8px;
        }
    </style>
</head>
<body>

<div class="card">
    <h1>Validador da Camada Gold</h1>
    <p>Caminho Gold: <b>{{ gold_path }}</b></p>

    <form method="get">
        <label>Selecione a tabela Gold:</label><br>
        <select name="tabela">
            {% for tabela in tabelas %}
                <option value="{{ tabela }}" {% if tabela == tabela_selecionada %}selected{% endif %}>
                    gold.{{ tabela }}
                </option>
            {% endfor %}
        </select>

        <button type="submit">Carregar</button>
    </form>
</div>

{% if erro %}
<div class="card">
    <h2>Erro</h2>
    <p>{{ erro }}</p>
</div>
{% endif %}

{% if tabela_selecionada and not erro %}
<div class="card">
    <h2>gold.{{ tabela_selecionada }}</h2>
    <p><b>Linhas:</b> {{ linhas }}</p>
    <p><b>Colunas:</b> {{ colunas }}</p>
</div>

<div class="card">
    <h2>Colunas</h2>
    <div class="table-wrapper">
        {{ tabela_colunas | safe }}
    </div>
</div>

<div class="card">
    <h2>Resumo numérico</h2>
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

</body>
</html>
"""


@app.route("/")
def index():
    tabelas = listar_tabelas_gold()

    if not tabelas:
        return render_template_string(
            HTML,
            tabelas=[],
            tabela_selecionada=None,
            erro="Nenhuma tabela Gold encontrada em data/gold.",
            gold_path=GOLD_PATH,
            linhas=0,
            colunas=0,
            tabela_colunas="",
            resumo="",
            preview="",
        )

    tabela_selecionada = request.args.get("tabela", tabelas[0])

    if tabela_selecionada not in tabelas:
        tabela_selecionada = tabelas[0]

    try:
        df = carregar_gold(tabela_selecionada)

        df_colunas = pd.DataFrame({
            "coluna": df.columns,
            "tipo": [str(df[coluna].dtype) for coluna in df.columns],
            "nulos": [int(df[coluna].isna().sum()) for coluna in df.columns],
        })

        resumo = df.describe(include="all").transpose().reset_index()
        resumo = resumo.rename(columns={"index": "coluna"})

        return render_template_string(
            HTML,
            tabelas=tabelas,
            tabela_selecionada=tabela_selecionada,
            erro=None,
            gold_path=GOLD_PATH,
            linhas=len(df),
            colunas=len(df.columns),
            tabela_colunas=df_colunas.to_html(index=False),
            resumo=resumo.to_html(index=False),
            preview=df.head(50).to_html(index=False),
        )

    except Exception as erro:
        return render_template_string(
            HTML,
            tabelas=tabelas,
            tabela_selecionada=tabela_selecionada,
            erro=str(erro),
            gold_path=GOLD_PATH,
            linhas=0,
            colunas=0,
            tabela_colunas="",
            resumo="",
            preview="",
        )


if __name__ == "__main__":
    app.run(debug=True)
    