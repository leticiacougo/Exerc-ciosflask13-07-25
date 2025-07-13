from flask import Flask, render_template, request, redirect, url_for, session, make_response
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Troque por uma chave secreta real
app.permanent_session_lifetime = timedelta(minutes=30)

USUARIO_FIXO = 'admin'
SENHA_FIXA = '1234'

NOTICIAS = {
    'Esportes': [
        {'id': 1, 'titulo': 'Time X vence campeonato', 'conteudo': 'Detalhes do jogo...'},
        {'id': 2, 'titulo': 'Jogador Y sofre lesão', 'conteudo': 'Informações médicas...'},
        {'id': 3, 'titulo': 'Novo estádio será inaugurado', 'conteudo': 'Inauguração marcada...'}
    ],
    'Entretenimento': [
        {'id': 4, 'titulo': 'Filme Z é lançado', 'conteudo': 'Sinopse do filme...'},
        {'id': 5, 'titulo': 'Festival de música começa amanhã', 'conteudo': 'Lineup completo...'},
        {'id': 6, 'titulo': 'Cantor A lança novo álbum', 'conteudo': 'Detalhes do álbum...'}
    ],
    'Lazer': [
        {'id': 7, 'titulo': 'Parque B reabre após reforma', 'conteudo': 'Novas atrações...'},
        {'id': 8, 'titulo': 'Dicas para viagens econômicas', 'conteudo': 'Orçamento e destinos...'},
        {'id': 9, 'titulo': 'Receitas fáceis para o fim de semana', 'conteudo': 'Passo a passo...'}
    ]
}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        if usuario == USUARIO_FIXO and senha == SENHA_FIXA:
            session.permanent = True
            session['usuario'] = usuario
            session['contador'] = 0
            session['categoria'] = 'Esportes'
            return redirect(url_for('portal'))
        else:
            return render_template('login.html', erro='Usuário ou senha inválidos.')
    else:
        if 'usuario' in session:
            return redirect(url_for('portal'))
        return render_template('login.html')

@app.route('/portal', methods=['GET', 'POST'])
def portal():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    session['contador'] = session.get('contador', 0) + 1
    tema = request.cookies.get('tema', 'claro')

    if request.method == 'POST':
        categoria_escolhida = request.form.get('categoria')
        if categoria_escolhida in NOTICIAS.keys():
            session['categoria'] = categoria_escolhida

        tema_escolhido = request.form.get('tema')
        if tema_escolhido in ['claro', 'escuro']:
            tema = tema_escolhido

    categoria = session.get('categoria', 'Esportes')
    noticias = NOTICIAS[categoria]

    resp = make_response(render_template('portal.html',
                                         usuario=session['usuario'],
                                         contador=session['contador'],
                                         categoria=categoria,
                                         noticias=noticias,
                                         tema=tema))
    resp.set_cookie('tema', tema, max_age=30*60)
    return resp

@app.route('/noticia/<int:noticia_id>')
def noticia(noticia_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    noticia_encontrada = None
    for lista in NOTICIAS.values():
        for n in lista:
            if n['id'] == noticia_id:
                noticia_encontrada = n
                break
        if noticia_encontrada:
            break

    if not noticia_encontrada:
        return 'Notícia não encontrada', 404

    tema = request.cookies.get('tema', 'claro')

    return render_template('noticia.html', noticia=noticia_encontrada, usuario=session['usuario'], tema=tema)

@app.route('/logout')
def logout():
    session.clear()
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('tema', '', expires=0)
    return resp

if __name__ == '__main__':
    app.run(debug=True)
