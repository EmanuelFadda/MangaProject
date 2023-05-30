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

#recupero di tutti i generi presente nel database
def get_all_genres():
    try:
        cur = mysql.connection.cursor()

        #query
        query = "SELECT * FROM categoria;"

        #return dei dati
        cur.execute(query)
        genres = cur.fetchall()
        cur.close()
        return genres
    
    except Exception as e:
        print(f"Errore durante l'esecuzione della query: {str(e)}")
        return []

#recupero dei capitolo di un certo manga
def get_chapters_by_manga_id(id):
    cur = mysql.connection.cursor()

    #query
    query = """
            SELECT capitolo.*
            FROM capitolo
            WHERE ID_Manga=%s
            ORDER BY numeroVolume,numeroCapitolo ASC
            """
    
    #return dei dati
    cur.execute(query, (id,))
    chapters = cur.fetchall()
    return chapters

#recupero di tutti gli artisti o autori
def get_all_person():
    try:
        cur = mysql.connection.cursor()

        #query
        query = "SELECT * FROM persona ORDER BY persona.nome ASC"

        #return dei dati
        cur.execute(query)
        person = cur.fetchall()
        cur.close()
        return person
    except Exception as e:
        print(f"Errore durante l'esecuzione della query: {str(e)}")
        return []

#recupero di tutti i commenti sotto a un certo manga
def get_comments_by_manga_id(id):
    cur = mysql.connection.cursor()

    #query
    query = """
            SELECT commento.*, utente.ID, utente.nickname
            FROM commento
            JOIN utente ON commento.ID_Utente=utente.ID
            WHERE ID_Manga=%s
            ORDER BY commento.ID DESC
            """
    
    #return dei dati
    cur.execute(query, (id,))
    chapters = cur.fetchall()
    return chapters

#recupero degli id di un numero di manga (18 di base)
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

    #return degli id
    ids = []
    for manga in cur.fetchall():
        ids.append(manga[0])
    return tuple(ids)


def get_manga_by_list_id(ids):
    try:
        cur = mysql.connection.cursor()

        # palcehoder per evitare l'sql injection
        placeholders = "("+(','.join(['%s'] * len(ids)))+")"

        #query
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
        
        #return dei dati
        cur.execute(query, ids)
        result = cur.fetchall()
        cur.close()
        return result
    except Exception as e:
        print(f"Errore durante l'esecuzione della query: {str(e)}")
        return None


#recupero delle informazioni di un utente
def get_user_informations(id):
    cur = mysql.connection.cursor()

    #query
    query = """
            SELECT *
            FROM utente
            WHERE ID=%s
            """

    #return dei dati
    cur.execute(query,(id,))
    user = cur.fetchall()
    return user

#recupero delle informazioni di un utente
def get_follow(id):
    cur = mysql.connection.cursor()

    #query
    query = """
            SELECT utente.ID,utente.nickname
            FROM segue
            JOIN utente ON segue.seguito=utente.ID 
            WHERE segue.ID_Utente=%s
            """

    #return dei dati
    cur.execute(query,(id,))
    user = cur.fetchall()
    return user

#recupero dei manga letti da un utente
def get_viewed_manga(id):
    cur = mysql.connection.cursor()

    #query
    query = """
            SELECT manga.*
            FROM manga 
            join letto on manga.ID=letto.ID_manga
            join utente on letto.ID_utente=utente.ID
            WHERE utente.ID=%s
            """
    
    #return dei dati
    cur.execute(query, (id,))
    manga = cur.fetchall()
    return manga

#recupero dei manga preferiti da un utente
def get_favorite_manga(id):
    cur = mysql.connection.cursor()

    #query
    query = """
            SELECT manga.*
            FROM manga 
            join preferiti on manga.ID=preferiti.ID_manga
            join utente on preferiti.ID_utente=utente.ID
            WHERE utente.ID=%s
            """

    #return dei dati
    cur.execute(query,(id,))
    manga = cur.fetchall()
    return manga


#controllo informazioni inserite nel login con quelle presenti nel database
def control_login(email, password):
    cur = mysql.connection.cursor()

    where = ""

    #query
    query = """
            SELECT utente.ID, utente.nickname,utente.admin
            FROM utente
            WHERE utente.email=%s AND utente.password=%s
            """

    #return dei dati
    cur.execute(query,(email,password))
    result = cur.fetchone()
    return result


#controllo informazioni inserite nel login con quelle presenti nel database
def control_register(email):
    cur = mysql.connection.cursor()

    #query
    query = """
            SELECT utente.ID
            FROM utente
            WHERE utente.email=%s
            """


    cur.execute(query,(email,))
    result = cur.fetchall()

    #nessun account con quella mail 
    if len(result) == 0:
        return True
    
    return False


# inserimento nuovo account nel database
def create_account(email, password, nome, cognome, nickname, data_Nascita, admin=0):
    cur = mysql.connection.cursor()

    # query
    query = """
            INSERT INTO utente
            ( nome, cognome, data_Nascita, nickname, email, password, admin)
            VALUES ( %s, %s, %s, %s, %s, %s, %s)
            """
    cur.execute(query,(nome, cognome, data_Nascita, nickname, email, password, admin))
    mysql.connection.commit()

# inserimento nuovo commento 
def add_comment(contenuto,idutente,idmanga):
    cur = mysql.connection.cursor()

    #query
    query = """
            INSERT INTO commento(contenuto,ID_Utente,ID_Manga) VALUES (%s ,%s,%s)
            """
    cur.execute(query,(contenuto,idutente,idmanga))
    mysql.connection.commit()

#rimozione di un commento
def delete_comment(idcommento):
    cur = mysql.connection.cursor()

    #query
    query = """
            DELETE FROM commento WHERE ID=%s
            """
    cur.execute(query,(idcommento,))
    mysql.connection.commit()

#controllo se un manga è tra i preferiti di un certo account
def is_favorite(idutente,idmanga):
    cur = mysql.connection.cursor()

    #query
    query = """
            SELECT * FROM preferiti WHERE ID_Utente=%s AND ID_Manga=%s
            """
    cur.execute(query,(idutente,idmanga))
    result=cur.fetchone()

    if result is None:
        return False
    else:
        return True


#aggiunge un manga ai preferiti di un utente   
def add_favorite(idutente,idmanga):
    cur = mysql.connection.cursor()

    #query
    query = """
            INSERT INTO preferiti(ID_Utente,ID_Manga) VALUES (%s ,%s)
            """
    cur.execute(query,(idutente,idmanga))
    mysql.connection.commit()

#rimuovere un manga dai preferiti di un utente  
def delete_favorite(idutente,idmanga):
    cur = mysql.connection.cursor()

    #query
    query = """
            DELETE FROM preferiti WHERE ID_Utente=%s AND ID_Manga=%s
            """
    cur.execute(query,(idutente,idmanga))
    mysql.connection.commit()



#controllo se un manga è tra i letti di un certo account
def is_read(idutente,idmanga):
    cur = mysql.connection.cursor()

    #query
    query = """
            SELECT * FROM letto WHERE ID_Utente=%s AND ID_Manga=%s
            """
    cur.execute(query,(idutente,idmanga))
    result=cur.fetchone()
    if result is None:
        return False
    else:
        return True
    
#aggiunge un manga ai letti di un utente 
def add_read(idutente,idmanga):
    cur = mysql.connection.cursor()

    #query
    query = """
            INSERT INTO letto(ID_Utente,ID_Manga) VALUES (%s ,%s)
            """
    cur.execute(query,(idutente,idmanga))
    mysql.connection.commit()


#controllo se un account è tra i seguiti di un certo account
def is_follower(idutente,idutente2):
    cur = mysql.connection.cursor()

    #query
    query = """
            SELECT * FROM segue WHERE ID_Utente=%s AND seguito=%s
            """
    cur.execute(query,(idutente,idutente2))
    result=cur.fetchone()

    if result is None:
        return False
    else:
        return True


#aggiunge un account ai seguiti di un utente   
def add_follower(idutente,idutente2):
    cur = mysql.connection.cursor()

    #query
    query = """
            INSERT INTO segue(ID_Utente,seguito) VALUES (%s ,%s)
            """
    cur.execute(query,(idutente,idutente2))
    mysql.connection.commit()

#rimuovere un account dai seguiti di un utente  
def delete_follower(idutente,idutente2):
    cur = mysql.connection.cursor()

    #query
    query = """
            DELETE FROM segue WHERE ID_Utente=%s AND seguito=%s
            """
    cur.execute(query,(idutente,idutente2))
    mysql.connection.commit()
