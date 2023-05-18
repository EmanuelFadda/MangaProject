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
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_query = request.form['search']
        cur = mysql.connection.cursor()
        # Esegui la query di ricerca dei manga
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
            WHERE m.titolo LIKE %s
            GROUP BY m.titolo;
            """
        cur.execute(query, ('%' + search_query + '%',))
        result = cur.fetchall()
        cur.close()
        if result:
            return render_template('index.html', manga_data=result, genres=get_all_genres())
        else:
            return render_template('index.html', manga_data=None, genres=get_all_genres())
    else:
        return render_template('index.html', manga_data=None, genres=get_all_genres())




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


if __name__ == '__main__':
    app.run()
