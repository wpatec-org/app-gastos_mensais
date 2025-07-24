from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from datetime import datetime
import os
from weasyprint import HTML

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

PASTA_RELATORIOS = os.path.join(os.getcwd(), 'relatorios')
os.makedirs(PASTA_RELATORIOS, exist_ok=True)

DESPESAS_FIXAS = [
    "ItauCard", "NUBANK", "WillBank", "INTER", "MELIUZ",
    "PAN", "PIC PAY", "AGUA", "LUZ", "IINTERNET",
    "IPVA", "IPTU", "Pres Casa", "Pensão", "LICENCIAMENTOS"
]

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = total = salario = None
    tipo = ''
    despesas = []

    if request.method == 'POST':
        nomes = request.form.getlist('nomes[]')
        valores = request.form.getlist('valores[]')
        extra_nomes = request.form.getlist('extra_nome[]')
        extra_valores = request.form.getlist('extra_valor[]')
        salario_str = request.form.get('salario', '0').replace(',', '.')
        salario = float(salario_str) if salario_str else 0.0

        for nome, val in zip(nomes, valores):
            if val.strip():
                try:
                    despesas.append((nome, float(val)))
                except ValueError:
                    pass

        for nome, val in zip(extra_nomes, extra_valores):
            if nome.strip() and val.strip():
                try:
                    despesas.append((nome.strip(), float(val)))
                except ValueError:
                    pass

        total = sum(valor for _, valor in despesas)
        resultado = salario - total
        tipo = 'Crédito' if resultado >= 0 else 'Déficit'

        # Salvar relatório
        if 'salvar' in request.form:
            if salario == 0:
                flash("Informe o salário antes de salvar o relatório.", "danger")
            else:
                agora = datetime.now()
                nome_arquivo = f"relatorio_{agora.strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
                caminho_arquivo = os.path.join(PASTA_RELATORIOS, nome_arquivo)

                html = render_template("relatorio_pdf.html",
                                       data=agora.strftime('%d/%m/%Y'),
                                       despesas=despesas,
                                       total=total,
                                       resultado=resultado,
                                       tipo=tipo,
                                       salario=salario)
                HTML(string=html).write_pdf(caminho_arquivo)
                flash(f"Relatório salvo como {nome_arquivo}", "success")

        return render_template("index.html",
                               despesas_nomes=DESPESAS_FIXAS,
                               despesas=despesas,
                               total=total,
                               resultado=resultado,
                               tipo=tipo,
                               salario=salario)

    # GET
    return render_template("index.html",
                           despesas_nomes=DESPESAS_FIXAS,
                           despesas=[],
                           total=None,
                           resultado=None,
                           tipo='',
                           salario=None)

@app.route('/relatorios')
def relatorios():
    arquivos = sorted([f for f in os.listdir(PASTA_RELATORIOS) if f.endswith('.pdf')])
    return render_template("relatorios.html", arquivos=arquivos)

@app.route('/relatorio/<nome_arquivo>')
def abrir_relatorio(nome_arquivo):
    return send_from_directory(PASTA_RELATORIOS, nome_arquivo)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
