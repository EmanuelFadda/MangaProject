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

MANGA_FOR_PAGE=18

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        result=None
        if len(request.form)==1:
            titolo = request.form['search']
            ids=get_ids_for_page(title=titolo)
            result=get_manga_by_list_id(tuple(ids))
            
        else:
            genre=request.form['genre']
            author=request.form['author']
            artist=request.form['artist']
            year=request.form['year']
            ids=get_ids_for_page(genre=genre,author=author,artist=artist,year=year)
            result=get_manga_by_list_id(tuple(ids))
        if result:
            return render_template('index.html', manga_data=result, genres=get_all_genres(),people=get_all_person())
        else:
            return render_template('index.html', manga_data=None, genres=get_all_genres(),people=get_all_person())
    else:
        return render_template('index.html', manga_data=None, genres=get_all_genres(),people=get_all_person())



def get_ids_for_page(title="",genre="",author="",artist="",year="",page=1):
    cur = mysql.connection.cursor()
    first=True
    base_query="""SELECT manga.id
        FROM manga
    """
    join=""
    where="WHERE 1=1"
    params=[]
    limit=" LIMIT "+str(MANGA_FOR_PAGE)
    skip=" SKIP "+str(MANGA_FOR_PAGE*(page-1))
    #filtra per nome
    if title!= "":
        where+=" AND titolo LIKE %s"
        params.append('%'+title+'%')

    #filtra per genere
    if genre!= "":
        join+= "JOIN tipomanga ON manga.id=tipomanga.ID_Manga "
        where+=" AND ID_categoria=%s"
        params.append(int(genre))

    #filtra per autore
    if author!= "":
        join+=" JOIN scrive ON manga.id=scrive.ID_Manga "
        where+=" AND ID_Autore=%s"
        params.append(int(author))
        
    #filtra per artista
    if artist!= "":
        join+=" JOIN disegna ON manga.id=disegna.ID_Manga "
        where+=" AND ID_Artista=%s"
        params.append(int(artist))

    #filtra per anno
    if year != "":
        where+=" AND Anno=%s"
        params.append(int(year))
    print(base_query+join+where+limit)
    cur.execute(base_query+join+where+limit, params)
    ids=[]
    for manga in cur.fetchall():
        ids.append(manga[0])
    return tuple(ids)

def get_manga_by_list_id(ids):
    try:
        cur = mysql.connection.cursor()

        #palcehoder per evitare l'sql injection
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


@app.route('/manga/<int:id>')
def manga_details(id):
    manga = get_manga_by_list_id((id,))[0]
    id_manga=manga[0]

    #recupero capitoli del manga
    cur = mysql.connection.cursor()
    query="SELECT * FROM capitolo  WHERE capitolo.ID_Manga=%s order by numeroVolume,numeroCapitolo ASC"
    cur.execute(query,(id_manga,))
    capitoli=cur.fetchall()
    
    if manga:
        return render_template('manga.html', manga=manga,capitoli=capitoli)
    else:
        return render_template('error.html', message='Manga not found')




@app.route('/account/<nome_account>')
def profile(nome_account):
    x = nome_account
    return render_template('profile.html', nome_account=x)


@app.route('/manga/<int:idm>/capitolo/<int:nc>')
def capitolo(idm,nc):

    #richiesta capitoli dal database
    cur = mysql.connection.cursor()
    query = """
            SELECT capitolo.*
            FROM capitolo
            WHERE ID_Manga=%s
            ORDER BY numeroVolume,numeroCapitolo ASC
            """
    cur.execute(query, (idm,))
    chaps=cur.fetchall()
    counter=1

    num_chps=len(chaps)
    next_chp=True
    prev_chp=True
    #ricerca del capitolo
    chap=chaps[0]
    for c in chaps:
        
        if c[1]==nc:
            chap=c

            #controllo presenza capitolo precedente
            if counter==1:
                prev_chp=False

            #controllo presenza capitolo successivo
            if counter==num_chps:
                next_chp=False
            break
        counter+=1

    #url delle immagini
    url=chap[3]
    extension=url[-3:]
    start_url=url[:-5]
    pages=1

    #calcolo numero di immagini
    imgs=[]     
    #controllo tipo dell'immagini
    while exists(start_url+str(pages)+"."+extension):
        imgs.append([pages,extension])
        pages+=1

    if extension=="jpg":
        extension="png"
    else:
        extension="jpg"

    while exists(start_url+str(pages)+"."+extension):
        imgs.append([pages,extension])
        pages+=1
    return render_template('capitolo.html',url=start_url, pages=pages, imgs=imgs, chaps=chaps, chp=nc, next_chp=next_chp, prev_chp=prev_chp)


def exists(path):
    r = requests.head(path)
    return r.status_code == requests.codes.ok
  

if __name__ == '__main__':
    app.run(debug=True)
