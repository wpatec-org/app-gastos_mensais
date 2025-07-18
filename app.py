from flask import Flask, render_template, request, flash, session, redirect, url_for
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'segredo'

DESPESAS_FIXAS = [
    "ItauCard", "NUBANK", "WillBank", "INTER", "MELIUZ", "PAN", "PIC PAY",
    "AGUA", "LUZ", "IINTERNET", "IPVA", "IPTU", "Pres Casa", "Pensão", "LICENCIAMENTOS"
]

RELATORIOS_DIR = 'relatorios'
os.makedirs(RELATORIOS_DIR, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    despesas = []
    total_despesas = 0.0
    resultado = None
    tipo_resultado = None
    salario = 0.0

    if request.method == 'POST':
        if 'calcular' in request.form:
            try:
                salario = float(request.form.get('salario', '0').replace(',', '.'))
            except ValueError:
                salario = 0.0

            nomes = request.form.getlist('nomes[]')
            valores = request.form.getlist('valores[]')

            for nome, valor in zip(nomes, valores):
                valor = valor.strip().replace(',', '.')
                if valor:
                    try:
                        valor_float = float(valor)
                    except ValueError:
                        valor_float = 0.0
                    despesas.append((nome, valor_float))
                    total_despesas += valor_float

            extras_nomes = request.form.getlist('extra_nome[]')
            extras_valores = request.form.getlist('extra_valor[]')

            for nome, valor in zip(extras_nomes, extras_valores):
                nome = nome.strip()
                valor = valor.strip().replace(',', '.')
                if nome:
                    try:
                        valor_float = float(valor)
                    except ValueError:
                        valor_float = 0.0
                    despesas.append((nome, valor_float))
                    total_despesas += valor_float

            resultado = round(salario - total_despesas, 2)
            tipo_resultado = "Crédito" if resultado >= 0 else "Déficit"

            # salvar na sessão
            session['despesas'] = despesas
            session['salario'] = salario
            session['total'] = total_despesas
            session['resultado'] = resultado
            session['tipo'] = tipo_resultado

        elif 'salvar' in request.form:
            # recuperar da sessão
            despesas = session.get('despesas', [])
            salario = session.get('salario', 0.0)
            total_despesas = session.get('total', 0.0)
            resultado = session.get('resultado', 0.0)
            tipo_resultado = session.get('tipo', 'Crédito')

            data_nome = datetime.now().strftime("%d-%m-%Y")
            data_texto = datetime.now().strftime("%d/%m/%Y")
            nome_arquivo = f"relatorio_{data_nome}.txt"
            caminho = os.path.join(RELATORIOS_DIR, nome_arquivo)

            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(f"Relatório gerado em: {data_texto}\n")
                f.write("Despesas:\n")
                if despesas:
                    for nome, valor in despesas:
                        f.write(f"  - {nome}: R$ {valor:.2f}\n")
                else:
                    f.write("  Nenhuma despesa registrada.\n")
                f.write(f"\nSalário: R$ {salario:.2f}\n")
                f.write(f"Total de Despesas: R$ {total_despesas:.2f}\n")
                f.write(f"Resultado: {tipo_resultado} de R$ {resultado:.2f}\n")

            flash(f"Relatório salvo como {nome_arquivo}", "success")
            return redirect(url_for('index'))

    else:
        # limpar sessão se for GET
        session.clear()

    return render_template("index.html",
                           despesas_nomes=DESPESAS_FIXAS,
                           despesas=despesas,
                           total=total_despesas,
                           resultado=resultado,
                           tipo=tipo_resultado,
                           salario=salario)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)