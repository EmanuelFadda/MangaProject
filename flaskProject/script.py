from flask import Flask
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
    skip = " OFFSET "+str(MANGA_FOR_PAGE*(page-1))
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
    print(title)
    cur.execute(base_query+join+where+limit+skip, params)
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

# def login_search()


def get_user_informations(id):
    cur = mysql.connection.cursor()
    where = "WHERE ID="+id
    query = """
            SELECT *
            FROM utente
            """+where

    cur.execute(query)
    user = cur.fetchall()
    return user


def get_viewed_manga(id):
    cur = mysql.connection.cursor()
    where = "WHERE utente.ID="+id
    query = """
            SELECT manga.*
            FROM manga 
            join letto on manga.ID=letto.ID_manga
            join utente on letto.ID_utente=utente.ID
            """+where

    cur.execute(query)
    manga = cur.fetchall()
    return manga


def get_favorite_manga(id):
    cur = mysql.connection.cursor()
    where = "WHERE utente.ID="+id
    query = """
            SELECT manga.*
            FROM manga 
            join preferiti on manga.ID=preferiti.ID_manga
            join utente on preferiti.ID_utente=utente.ID
            """+where

    cur.execute(query)
    manga = cur.fetchall()

    return manga
