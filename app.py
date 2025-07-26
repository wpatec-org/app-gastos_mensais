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

# --- FUNÇÃO DE CONVERSÃO CORRIGIDA ---
def converter_para_float(valor_str):
    """Converte uma string de moeda (ex: '1.234,56' ou '1234.56') para float."""
    if not isinstance(valor_str, str):
        return float(valor_str or 0.0)
    # Substitui a vírgula por ponto e depois converte para float
    # Isso funciona bem com inputs type="number" que enviam '.' como decimal
    return float(valor_str.replace(',', '.') or 0.0)

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = total = salario = None
    tipo = ''
    despesas = []
    despesas_extras_input = []
    salario_input = ''

    if request.method == 'POST':
        try:
            # Processa salário
            salario_str = request.form.get('salario', '0')
            salario = converter_para_float(salario_str)
            salario_input = request.form.get('salario', '')
            
            # Processa despesas fixas
            for nome in DESPESAS_FIXAS:
                valor_str = request.form.get(nome, '0')
                try:
                    valor = converter_para_float(valor_str)
                    if valor > 0:
                        despesas.append((nome, valor))
                except (ValueError, TypeError):
                    continue

            # Processa despesas extras
            i = 0
            while True:
                nome = request.form.get(f'extra_nome_{i}')
                valor_str = request.form.get(f'extra_valor_{i}')
                
                # Para o loop quando não encontrar mais campos (ex: extra_nome_5 não existe)
                if nome is None and valor_str is None:
                    break
                    
                if nome and nome.strip():
                    try:
                        valor_float = converter_para_float(valor_str)
                        if valor_float > 0:
                            despesa_extra_tupla = (nome.strip(), valor_float)
                            despesas.append(despesa_extra_tupla)
                            despesas_extras_input.append(despesa_extra_tupla)
                            logger.debug(f"Despesa extra {i}: {nome.strip()} - R$ {valor_float:.2f}")
                    except (ValueError, TypeError):
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
                           despesas_extras=despesas_extras_input,
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
    app.run(debug=True, host='0.0.0.0', port=5000)