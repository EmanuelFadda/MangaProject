from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mangarealm'

mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        # Utente già loggato
        username = session['username']
        return f'Benvenuto, {username}! <a href="/logout">Logout</a>'

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
            return render_template('index.html', manga_data=result)
        else:
            return render_template('index.html', manga_data=None)
    else:
        return render_template('index.html', manga_data=None)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        # Utente già loggato
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        # Esegui la query per verificare le credenziali dell'utente
        query = "SELECT * FROM utente WHERE nickname = %s AND password = %s"
        cur.execute(query, (username, password))
        user = cur.fetchone()
        print(user)
        cur.close()

        if user:
            session['username'] = user[4]
            return redirect('/')
        else:
            error_message = 'Username o password errati. Riprova.'
            return render_template('login.html', error_message=error_message)
    else:
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        # Utente già loggato
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        # Check if the username is already taken
        query = "SELECT * FROM utente WHERE nickname = %s"
        cur.execute(query, (username,))
        existing_user = cur.fetchone()

        if existing_user:
            error_message = 'Username already exists. Please choose a different username.'
            return render_template('register.html', error_message=error_message)
        else:
            # Insert the new user into the database
            query = "INSERT INTO utente (nickname, password) VALUES (%s, %s)"
            cur.execute(query, (username, password))
            mysql.connection.commit()
            cur.close()

            session['username'] = username
            return redirect('/')
    else:
        return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


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
