from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import requests
app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mangarealm'

mysql = MySQL(app)

MANGA_FOR_PAGE = 18


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        result = None
        if len(request.form) == 1:
            titolo = request.form['search']
            ids = get_ids_for_page(title=titolo)
            result = get_manga_by_list_id(tuple(ids))

        else:
            genre = request.form['genre']
            author = request.form['author']
            artist = request.form['artist']
            year = request.form['year']
            ids = get_ids_for_page(
                genre=genre, author=author, artist=artist, year=year)
            result = get_manga_by_list_id(tuple(ids))
        if result:
            return render_template('index.html', manga_data=result, genres=get_all_genres(), people=get_all_person())
        else:
            return render_template('index.html', manga_data=None, genres=get_all_genres(), people=get_all_person())
    else:
        return render_template('index.html', manga_data=None, genres=get_all_genres(), people=get_all_person())


@app.route('/manga/<int:id>')
def manga_details(id):
    manga = get_manga_by_list_id((id,))[0]
    id_manga = manga[0]

    # recupero capitoli del manga
    chapters = get_chapters_by_manga_id(id)

    # recupero commenti del manga
    comments = get_comments_by_manga_id(id)

    if manga:
        return render_template('manga.html', genres=get_all_genres(), people=get_all_person(), manga=manga, chapters=chapters, comments=comments)
    else:
        return render_template('error.html', genres=get_all_genres(), people=get_all_person(), message='Manga not found')


@app.route('/account/<nickname_account>')
def profile(nickname_account):
    # aggiungere controllo se non esiste l'account
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
    nickname = nickname_account
    nome = "nome"
    cognome = "cognome"
    email = "email"
    id = 12
    manga_visti = [manga_object, manga_object, manga_object]
    manga_piaciuti = [manga_object, manga_object, manga_object, manga_object]

    utente = {
        "id": id,
        "nickname": nickname,
        "nome": nome,
        "cognome": cognome,
        "email": email,
        "manga_visti": manga_visti,
        "manga_piaciuti": manga_piaciuti,
    }

    return render_template('profile.html', utente=utente)


@app.route('/manga/<int:idm>/capitolo/<int:nc>')
def capitolo(idm, nc):

    # richiesta capitoli dal database

    chapters = get_chapters_by_manga_id(idm)

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
    while exists(start_url+str(pages)+"."+extension):
        imgs.append(start_url+str(pages)+"."+extension)
        pages += 1

    if extension == "jpg":
        extension = "png"
    else:
        extension = "jpg"

    while exists(start_url+str(pages)+"."+extension):
        imgs.append(start_url+str(pages)+"."+extension)
        pages += 1
    return render_template('capitolo.html', genres=get_all_genres(), people=get_all_person(), imgs=imgs, chapters=chapters, chp=nc)


def exists(path):
    r = requests.head(path)
    return r.status_code == requests.codes.ok


def get_all_genres():
    try:
        cur = mysql.connection.cursor()
        query = "SELECT * FROM categoria;"
        cur.execute(query)
        genres = cur.fetchall()
        cur.close()
        return genres
    except Exception as e:
        print(f"Errore durante l'esecuzione della query: {str(e)}")
        return []


def get_all_person():
    try:
        cur = mysql.connection.cursor()
        query = "SELECT * FROM persona ORDER BY persona.nome ASC"
        cur.execute(query)
        person = cur.fetchall()
        cur.close()
        return person
    except Exception as e:
        print(f"Errore durante l'esecuzione della query: {str(e)}")
        return []


def get_chapters_by_manga_id(id):
    cur = mysql.connection.cursor()
    query = """
            SELECT capitolo.*
            FROM capitolo
            WHERE ID_Manga=%s
            ORDER BY numeroVolume,numeroCapitolo ASC
            """
    cur.execute(query, (id,))
    chapters = cur.fetchall()
    return chapters


def get_comments_by_manga_id(id):
    cur = mysql.connection.cursor()
    query = """
            SELECT commento.*, utente.ID, utente.nickname
            FROM commento
            JOIN utente ON commento.ID_Utente=utente.ID
            WHERE ID_Manga=%s
            """
    cur.execute(query, (id,))
    chapters = cur.fetchall()
    return chapters


def get_ids_for_page(title="", genre="", author="", artist="", year="", page=1):
    cur = mysql.connection.cursor()
    first = True
    base_query = """SELECT manga.id
        FROM manga
    """
    join = ""
    where = "WHERE 1=1"
    params = []
    limit = " LIMIT "+str(MANGA_FOR_PAGE)
    skip = " SKIP "+str(MANGA_FOR_PAGE*(page-1))
    # filtra per nome
    if title != "":
        where += " AND titolo LIKE %s"
        params.append('%'+title+'%')

    # filtra per genere
    if genre != "":
        join += "JOIN tipomanga ON manga.id=tipomanga.ID_Manga "
        where += " AND ID_categoria=%s"
        params.append(int(genre))

    # filtra per autore
    if author != "":
        join += " JOIN scrive ON manga.id=scrive.ID_Manga "
        where += " AND ID_Autore=%s"
        params.append(int(author))

    # filtra per artista
    if artist != "":
        join += " JOIN disegna ON manga.id=disegna.ID_Manga "
        where += " AND ID_Artista=%s"
        params.append(int(artist))

    # filtra per anno
    if year != "":
        where += " AND Anno=%s"
        params.append(int(year))
    print(base_query+join+where+limit)
    cur.execute(base_query+join+where+limit, params)
    ids = []
    for manga in cur.fetchall():
        ids.append(manga[0])
    return tuple(ids)


def get_manga_by_list_id(ids):
    try:
        cur = mysql.connection.cursor()

        # palcehoder per evitare l'sql injection
        placeholders = "("+(','.join(['%s'] * len(ids)))+")"

        query = f"""
            SELECT m.*, GROUP_CONCAT(DISTINCT c.titolo SEPARATOR ', ') AS Genres,
                    GROUP_CONCAT(DISTINCT aut.nome SEPARATOR ', ') AS Authors,
                    GROUP_CONCAT(DISTINCT art.nome SEPARATOR ', ') AS Artists
            FROM manga m
            LEFT JOIN tipomanga tm ON m.ID = tm.ID_Manga
            LEFT JOIN categoria c ON tm.ID_Categoria = c.ID
            LEFT JOIN scrive s ON m.ID = s.ID_Manga
            LEFT JOIN persona aut ON s.ID_Autore = aut.ID
            LEFT JOIN disegna d ON m.ID = d.ID_Manga
            LEFT JOIN persona art ON d.ID_Artista = art.ID
            WHERE m.ID IN {placeholders}
            GROUP BY m.ID;
            """
        cur.execute(query, ids)
        result = cur.fetchall()
        cur.close()
        return result
    except Exception as e:
        print(f"Errore durante l'esecuzione della query: {str(e)}")
        return None


if __name__ == '__main__':
    app.run(debug=True)
