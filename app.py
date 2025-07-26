from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from datetime import datetime
import os
from weasyprint import HTML
import logging

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui_123'

# Configuração de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_RELATORIOS = os.path.join(BASE_DIR, 'relatorios')
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
    salario_input = ''

    if request.method == 'POST':
        try:
            # Processa salário
            salario_str = request.form.get('salario', '0').replace(',', '.')
            salario = float(salario_str) if salario_str else 0.0
            salario_input = request.form.get('salario', '')
            
            # Processa despesas fixas
            for nome in DESPESAS_FIXAS:
                valor_str = request.form.get(nome, '0').replace(',', '.')
                try:
                    valor = float(valor_str)
                    if valor > 0:
                        despesas.append((nome, valor))
                except ValueError:
                    continue

            # Processa despesas extras (SOLUÇÃO DEFINITIVA)
            i = 0
            while True:
                nome = request.form.get(f'extra_nome_{i}')
                valor = request.form.get(f'extra_valor_{i}')
                
                if not nome and not valor:
                    break
                    
                if nome and nome.strip():
                    try:
                        # Converte formato brasileiro para float
                        valor_float = float(valor.replace('.', '').replace(',', '.'))
                        if valor_float > 0:
                            despesas.append((nome.strip(), valor_float))
                            logger.debug(f"Despesa extra {i}: {nome.strip()} - R$ {valor_float:.2f}")
                    except (ValueError, AttributeError):
                        continue
                i += 1

            # Cálculos
            total = sum(valor for _, valor in despesas) if despesas else 0
            resultado = salario - total if salario else 0
            tipo = 'Crédito' if resultado >= 0 else 'Déficit'

            # Salvar relatório se solicitado
            if 'salvar' in request.form:
                if not despesas:
                    flash("Preencha pelo menos uma despesa válida", "warning")
                elif salario <= 0:
                    flash("Informe um salário válido", "danger")
                else:
                    try:
                        agora = datetime.now()
                        nome_arquivo = f"relatorio_{agora.strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
                        caminho_arquivo = os.path.join(PASTA_RELATORIOS, nome_arquivo)

                        html = render_template("relatorio_pdf.html",
                                            data=agora.strftime('%d/%m/%Y %H:%M'),
                                            despesas=despesas,
                                            total=total,
                                            resultado=abs(resultado),
                                            tipo=tipo,
                                            salario=salario)

                        HTML(string=html).write_pdf(
                            caminho_arquivo,
                            presentational_hints=True
                        )

                        flash(f"Relatório salvo: {nome_arquivo}", "success")

                    except Exception as e:
                        flash(f"Erro ao gerar PDF: {str(e)}", "danger")
                        logger.error(f"Erro PDF: {str(e)}")

        except Exception as e:
            flash(f"Erro ao processar: {str(e)}", "danger")
            logger.error(f"Erro processamento: {str(e)}")

    return render_template("index.html",
                        despesas_nomes=DESPESAS_FIXAS,
                        despesas=despesas,
                        total=total,
                        resultado=resultado,
                        tipo=tipo,
                        salario=salario_input)

@app.route('/relatorios')
def relatorios():
    try:
        arquivos = sorted([f for f in os.listdir(PASTA_RELATORIOS) if f.endswith('.pdf')])
        return render_template("relatorios.html", arquivos=arquivos)
    except Exception as e:
        flash(f"Erro ao listar relatórios: {str(e)}", "danger")
        return render_template("relatorios.html", arquivos=[])

@app.route('/relatorio/<nome_arquivo>')
def abrir_relatorio(nome_arquivo):
    try:
        return send_from_directory(PASTA_RELATORIOS, nome_arquivo)
    except Exception as e:
        flash(f"Erro ao abrir relatório: {str(e)}", "danger")
        return redirect(url_for('relatorios'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)