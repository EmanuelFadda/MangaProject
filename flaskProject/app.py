from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mangarealm'

mysql = MySQL(app)


def get_all_genres():
    try:
        cur = mysql.connection.cursor()
        query = "SELECT titolo FROM categoria;"
        cur.execute(query)
        genres = [row[0] for row in cur.fetchall()]
        cur.close()
        return genres
    except Exception as e:
        print(f"Errore durante l'esecuzione della query: {str(e)}")
        return []


def get_all_authors():
    try:
        cur = mysql.connection.cursor()
        query = """SELECT persona.nome FROM `scrive`
                    LEFT JOIN persona ON scrive.ID_Autore=persona.ID
                    GROUP BY persona.nome;"""
        cur.execute(query)
        authors = [row[0] for row in cur.fetchall()]
        cur.close()
        return authors
    except Exception as e:
        print(f"Errore durante l'esecuzione della query: {str(e)}")
        return []

def get_all_years():
    try:
        cur = mysql.connection.cursor()
        query = """SELECT manga.anno FROM `manga`
                    GROUP BY manga.anno;"""
        cur.execute(query)
        authors = [row[0] for row in cur.fetchall()]
        cur.close()
        return authors
    except Exception as e:
        print(f"Errore durante l'esecuzione della query: {str(e)}")
        return []


def get_all_artist():
    try:
        cur = mysql.connection.cursor()
        query = """SELECT persona.nome FROM disegna
                    LEFT JOIN persona ON disegna.ID_Artista=persona.ID
                    GROUP BY persona.nome;"""
        cur.execute(query)
        authors = [row[0] for row in cur.fetchall()]
        cur.close()
        return authors
    except Exception as e:
        print(f"Errore durante l'esecuzione della query: {str(e)}")
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_query = request.form['search']
        genres = request.form.getlist('genres[]')

        cur = mysql.connection.cursor()
        query = """
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
            WHERE (m.titolo LIKE %s OR c.titolo IN (%s))
            GROUP BY m.titolo;
            """

        cur.execute(query, ('%' + search_query + '%', ', '.join(genres)))
        result = cur.fetchall()
        cur.close()

        if result:
            return render_template('index.html', manga_data=result, genres=get_all_genres(),authors=get_all_authors(),artists=get_all_artist(),years=get_all_years())
        else:
            return render_template('index.html', manga_data=None, genres=get_all_genres(),authors=get_all_authors(),artists=get_all_artist(),years=get_all_years())
    else:
        return render_template('index.html', manga_data=None, genres=get_all_genres(),authors=get_all_authors(),artists=get_all_artist(),years=get_all_years())




def get_manga_by_title(title):
    try:
        cur = mysql.connection.cursor()
        query = """
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
            WHERE m.titolo = %s
            GROUP BY m.titolo;
            """
        cur.execute(query, (title,))
        result = cur.fetchone()
        cur.close()
        return result
    except Exception as e:
        print(f"Errore durante l'esecuzione della query: {str(e)}")
        return None


@app.route('/manga/<title>')
def manga_details(title):
    manga = get_manga_by_title(title)
    if manga:
        return render_template('manga.html', manga=manga)
    else:
        return render_template('error.html', message='Manga not found')


@app.route('/account/<nome_account>')
def profile(nome_account):
    x = nome_account
    return render_template('profile.html', nome_account=x)


if __name__ == '__main__':
    app.run(debug=True)
