from flask import Flask, render_template, request
from flask_mysqldb import MySQL

import script
app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mangarealm'

mysql = MySQL(app)

MANGA_FOR_PAGE = 18

filter={
            "search": "",
            "genre":"",
            "author":"",
            "artist":"",
            "year":"",
            "page": 1
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    filter={
            "search": "",
            "genre":"",
            "author":"",
            "artist":"",
            "year":"",
            "page": 1
    }
    if request.method == 'POST':
        
        result = None
        filter['search'] = request.form['search']
        filter['genre'] = request.form['genre']
        filter['author'] = request.form['author']
        filter['artist'] = request.form['artist']
        filter['year'] = request.form['year']
        filter['page'] = int(request.form['page'])
        ids = script.get_ids_for_page(filter['search'],filter['genre'],filter['author'],filter['artist'],filter['year'],filter['page'])
        result = script.get_manga_by_list_id(tuple(ids))
        if result:
            return render_template('index.html', manga_data=result, genres=script.get_all_genres(), people=script.get_all_person(),filter=filter)
        else:
            return render_template('index.html', manga_data=None, genres=script.get_all_genres(), people=script.get_all_person(),filter=filter)
    else:
        return render_template('index.html', manga_data=None, genres=script.get_all_genres(), people=script.get_all_person(),filter=filter)


@app.route('/manga/<int:id>')
def manga_details(id):
    manga = script.get_manga_by_list_id((id,))[0]
    id_manga = manga[0]

    # recupero capitoli del manga
    chapters = script.get_chapters_by_manga_id(id)

    # recupero commenti del manga
    comments = script.get_comments_by_manga_id(id)

    if manga:
        return render_template('manga.html', genres=script.get_all_genres(), people=script.get_all_person(), manga=manga, chapters=chapters, comments=comments)
    else:
        return render_template('error.html', genres=script.get_all_genres(), people=script.get_all_person(), message='Manga not found')


@app.route('/account/<id_account>')
def profile(id_account):
    # aggiungere controllo se non esiste l'account

    manga_visti = script.get_viewed_manga(id_account)
    manga_piaciuti = script.get_favorite_manga(id_account)
    id_manga = 12
    titolo = "titolo"
    copertina = "url_copertina"
    descrizione = "descrizione"
    anno = 1900

    manga_object = {
        "ID": id_manga,
        "titolo": titolo,
        "copertina": copertina,
        "descrizione": descrizione,
        "anno": anno
    }

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

    return render_template('profile.html', utente=utente)


@app.route('/manga/<int:idm>/capitolo/<int:nc>')
def capitolo(idm, nc):

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
    return render_template('capitolo.html', genres=script.get_all_genres(), people=script.get_all_person(), imgs=imgs, chapters=chapters, chp=nc, idm=idm)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
