from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

import script
app = Flask(__name__)
app.secret_key = 'key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mangarealm'


user_session = {}
mysql = MySQL(app)

MANGA_FOR_PAGE = 18

filter = {
    "search": "",
    "genre": "",
    "author": "",
    "artist": "",
    "year": "",
            "page": 1
}


@app.route('/', methods=['GET', 'POST'])
def index():

    filter = {
        "search": "",
        "genre": "",
        "author": "",
        "artist": "",
        "year": "",
        "page": 1
    }
    if session.get("user_id") != None:
        user_session["user_id"] = session["user_id"]
        user_session["nickname"] = session["nickname"]
        user_session["admin"] = session["admin"]
    if request.method == 'POST':
        result = None
        filter['search'] = request.form['search']
        filter['genre'] = request.form['genre']
        filter['author'] = request.form['author']
        filter['artist'] = request.form['artist']
        filter['year'] = request.form['year']
        filter['page'] = int(request.form['page'])
        ids = script.get_ids_for_page(filter['search'], filter['genre'], filter['author'], filter['artist'], filter['year'], filter['page'])
        result = script.get_manga_by_list_id(tuple(ids))
        if result:
            return render_template('index.html', manga_data=result, genres=script.get_all_genres(), people=script.get_all_person(), filter=filter, user=user_session)
        else:
            return render_template('index.html', manga_data=None, genres=script.get_all_genres(), people=script.get_all_person(), filter=filter, user=user_session)
    else:
        return render_template('index.html', manga_data=None, genres=script.get_all_genres(), people=script.get_all_person(), filter=filter, user=user_session)


@app.route('/manga/<int:id>')
def manga_details(id):
    esiste=False
    if session.get("user_id") != None:
        esiste=script.is_favorite(session['user_id'],id)
    manga = script.get_manga_by_list_id((id,))[0]
    id_manga = manga[0]

    # recupero capitoli del manga
    chapters = script.get_chapters_by_manga_id(id)

    # recupero commenti del manga
    comments = script.get_comments_by_manga_id(id)

    if manga:
        return render_template('manga.html', genres=script.get_all_genres(), people=script.get_all_person(), manga=manga, chapters=chapters, comments=comments, user=user_session,preferito=esiste)
    else:
        return render_template('error.html', genres=script.get_all_genres(), people=script.get_all_person(), message='Manga not found', user=user_session,preferito=esiste)


@app.route('/account/<id_account>')
def profile(id_account):
    # aggiungere controllo se non esiste l'account

    manga_visti = script.get_viewed_manga(id_account)
    manga_piaciuti = script.get_favorite_manga(id_account)

    # funzione per controllare l'esistenza dell'account
    # funzione per trovare tutti i manga visti
    # funzione per trovare tutti i manga piaciuti

    user = script.get_user_informations(id_account)[0]
    utente = {
        "ID": user[0],
        "nome": user[1],
        "cognome": user[2],
        "data_Nascita": user[3],
        "nickname": user[4],
        "email": user[5],
        "manga_visti": manga_visti,
        "manga_piaciuti": manga_piaciuti,
    }

    return render_template('profile.html', utente=utente, user=user_session)


@app.route('/manga/<int:idm>/capitolo/<int:nc>')
def capitolo(idm, nc):
    if session.get("user_id") != None:
        idu=session["user_id"]
        letto=script.is_read(idu,idm)
        if letto==False:
            script.add_read(idu,idm)
    # richiesta capitoli dal database

    chapters = script.get_chapters_by_manga_id(idm)

    # ricerca del capitolo
    chap = chapters[0]
    for c in chapters:

        if c[1] == nc:
            chap = c
            break

    # url delle immagini
    url = chap[3]
    extension = url[-3:]
    start_url = url[:-5]
    pages = 1

    # calcolo numero di immagini
    imgs = []
    # controllo tipo dell'immagini
    while script.exists(start_url+str(pages)+"."+extension):
        imgs.append(start_url+str(pages)+"."+extension)
        pages += 1

    if extension == "jpg":
        extension = "png"
    else:
        extension = "jpg"

    while script.exists(start_url+str(pages)+"."+extension):
        imgs.append(start_url+str(pages)+"."+extension)
        pages += 1
    return render_template('capitolo.html', genres=script.get_all_genres(), people=script.get_all_person(), imgs=imgs, chapters=chapters, chp=nc, idm=idm, user=user_session)


@app.route('/login')
def login():
    return render_template('login.html', user=None)


@app.route('/register')
def register():
    return render_template('register.html', error_message="", user=None)


@app.route('/complete_login', methods=['POST'])
def complete_login():
    email = request.form.get("email")
    password = request.form.get("password")
    result = script.control_login(email, password)
    if result is None:
        return render_template('login.html', error_message="Login errato, riprova", user=None)
    user_id = str(result[0])
    nickname = str(result[1])
    admin = result[2]
    session["user_id"] = user_id
    session["nickname"] = nickname
    session["admin"] = admin
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    user_session.clear()
    return redirect(url_for("index"))


@app.route("/complete_register", methods=['POST'])
def complete_register():

    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    if (password == confirm_password):

        email = request.form.get("email")
        if (script.control_register(email)):

            nickname = request.form.get("nickname")
            data_Nascita = request.form.get("data_Nascita")
            cognome = request.form.get("cognome")
            nome = request.form.get("nome")
            script.create_account(email, password, nome,
                                  cognome, nickname, data_Nascita)

            return redirect(url_for("index"))

        return render_template('register.html', error_message="Esiste già un utente che usa l'email inserita, riprova", user=None)

    return render_template('register.html', error_message='Verificare che sia inserita la stessa password nei campi "Password" e "Conferma password, riprova"', user=None)

@app.route('/addcomment/<int:idm>',methods=['GET', 'POST'])
def aggiungi_commento(idm):
    if request.method=="POST":
        idu=request.form['idutente']
        commento=request.form['contenuto']
        script.add_comment(commento,idu,idm)

    return redirect(url_for('manga_details', id=idm))

@app.route('/deletecomment/<int:idm>',methods=['GET', 'POST'])
def elimina_commento(idm):
    if request.method=="POST":
        
        idc=int(request.form['idcommento'])
        
        script.delete_comment(idc)

    return redirect(url_for('manga_details', id=idm))

@app.route('/actionfavorite/<int:idm>',methods=['GET', 'POST'])
def azione_preferiti(idm):
    if request.method=="POST":
        idu=session["user_id"]
        esiste=script.is_favorite(idu,idm)
        if esiste:
            script.delete_favorite(idu,idm)  
        else:
            script.add_favorite(idu,idm)   
    return redirect(url_for('manga_details', id=idm))


if __name__ == '__main__':
    app.run(debug=True)
