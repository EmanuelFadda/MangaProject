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

#pagina home/principale
@app.route('/', methods=['GET', 'POST'])
def index():

    #clear del filtro per la ricerca
    filter = {
        "search": "",
        "genre": "",
        "author": "",
        "artist": "",
        "year": "",
        "page": 1
    }

    #se l'utente è loggato vengono salvata le sue informazioni
    if session.get("user_id") != None:
        user_session["user_id"] = session["user_id"]
        user_session["nickname"] = session["nickname"]
        user_session["admin"] = session["admin"]

    #sezione di ricerca dei manga tramite il filtro    
    if request.method == 'POST':
        result = None
        filter['search'] = request.form['search']
        filter['genre'] = request.form['genre']
        filter['author'] = request.form['author']
        filter['artist'] = request.form['artist']
        filter['year'] = request.form['year']
        filter['page'] = int(request.form['page'])

        #recupero dal database di 18 ID dei manga con le caratteristiche presenti nel filtro
        ids = script.get_ids_for_page(filter['search'], filter['genre'], filter['author'], filter['artist'], filter['year'], filter['page'])

        #recupero dal database delle informazioni riguardanti i 18 manga prima ottenuti
        result = script.get_manga_by_list_id(tuple(ids))
        if result:
            return render_template('index.html', manga_data=result, genres=script.get_all_genres(), people=script.get_all_person(), filter=filter, user=user_session)
        else:
            return render_template('index.html', manga_data=None, genres=script.get_all_genres(), people=script.get_all_person(), filter=filter, user=user_session)
    else:
        return render_template('index.html', manga_data=None, genres=script.get_all_genres(), people=script.get_all_person(), filter=filter, user=user_session)


#pagina del singolo manga
@app.route('/manga/<int:id>')
def manga_details(id):

    esiste=False
    #controllo, se l'utente è loggato, che il manga sia presente o meno trai suoi preferiti
    if session.get("user_id") != None:
        esiste=script.is_favorite(session['user_id'],id)
    manga = script.get_manga_by_list_id((id,))[0]

    # recupero capitoli del manga
    chapters = script.get_chapters_by_manga_id(id)

    # recupero commenti del manga
    comments = script.get_comments_by_manga_id(id)

    if manga:
        return render_template('manga.html', genres=script.get_all_genres(), people=script.get_all_person(), manga=manga, chapters=chapters, comments=comments, user=user_session,preferito=esiste)
    else:
        return render_template('error.html', genres=script.get_all_genres(), people=script.get_all_person(), message='Manga not found', user=user_session,preferito=esiste)

#pagina profilo di un account
@app.route('/account/<id_account>')
def profile(id_account):

    #recupero dei manga letti dall'utente
    manga_visti = script.get_viewed_manga(id_account)

    #recupero dei manga preferiti dall'utente
    manga_piaciuti = script.get_favorite_manga(id_account)

    #recupero delle informazioni dell'utente
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

#pagina di un capitolo di un manga
@app.route('/manga/<int:idm>/capitolo/<int:nc>')
def capitolo(idm, nc):

    # in caso l'utente sia loggato, si aggiunge il manga tra quelli letti dall'utente
    if session.get("user_id") != None:
        idu=session["user_id"]
        letto=script.is_read(idu,idm)
        if letto==False:
            script.add_read(idu,idm)

    # recupero dei capitoli del manga
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

    # ----calcolo numero di immagini----

    imgs = []

    # count immangini .jpg
    while script.exists(start_url+str(pages)+"."+extension):
        imgs.append(start_url+str(pages)+"."+extension)
        pages += 1

    if extension == "jpg":
        extension = "png"
    else:
        extension = "jpg"

    # count immangini .png
    while script.exists(start_url+str(pages)+"."+extension):
        imgs.append(start_url+str(pages)+"."+extension)
        pages += 1

    return render_template('capitolo.html', genres=script.get_all_genres(), people=script.get_all_person(), imgs=imgs, chapters=chapters, chp=nc, idm=idm, user=user_session)

#pagina di login
@app.route('/login')
def login():
    return render_template('login.html', user=None)

#pagina di registrazione
@app.route('/register')
def register():
    return render_template('register.html', error_message="", user=None)

#route per controllo dei dati inseriti nel login, redirect alla pagina iniziale se i dati sono compilati correttamente
@app.route('/complete_login', methods=['POST'])
def complete_login():

    #recupero email e password dal form
    email = request.form.get("email")
    password = request.form.get("password")

    #recupero delle informazioni dell'account
    result = script.control_login(email, password)

    #redirect alla pagina di login se non viene trovato nessun account
    if result is None:
        return render_template('login.html', error_message="Login errato, riprova", user=None)
    

    #inserimento dati nella sessione
    session["user_id"] = str(result[0])
    session["nickname"] = str(result[1])
    session["admin"] = result[2]

    return redirect(url_for("index"))

#route per sloggare dall'account, si viene reinderizzati alla pagina principale
@app.route("/logout")
def logout():
    session.clear()
    user_session.clear()
    return redirect(url_for("index"))

#route per controllo dei dati inseriti nel register, redirect alla pagina iniziale se i dati sono compilati correttamente
@app.route("/complete_register", methods=['POST'])
def complete_register():
    
    #controllo password di conferma
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    if (password == confirm_password):

        #controllo che l'email non sia gai assegnata a un altro account
        email = request.form.get("email")
        if (script.control_register(email)):

            #recupero dati dal form
            nickname = request.form.get("nickname")
            data_Nascita = request.form.get("data_Nascita")
            cognome = request.form.get("cognome")
            nome = request.form.get("nome")

            #creazione account e redirect alla pagina iniziale
            script.create_account(email, password, nome,cognome, nickname, data_Nascita)
            return redirect(url_for("index"))

        return render_template('register.html', error_message="Esiste già un utente che usa l'email inserita, riprova", user=None)

    return render_template('register.html', error_message='Verificare che sia inserita la stessa password nei campi "Password" e "Conferma password, riprova"', user=None)

#route per l'aggiunta di un commento a un manga
@app.route('/addcomment/<int:idm>',methods=['GET', 'POST'])
def aggiungi_commento(idm):
    if request.method=="POST":

        #recupero dati dal form
        idu=request.form['idutente']
        commento=request.form['contenuto']

        #aggiunta del commento al database
        script.add_comment(commento,idu,idm)

    #redirect alla pagina del manga
    return redirect(url_for('manga_details', id=idm))

#route per l'eliminazione di un commento da un manga (esclusivo admin)
@app.route('/deletecomment/<int:idm>',methods=['GET', 'POST'])
def elimina_commento(idm):
    if request.method=="POST":
        
        #eliminazione del commento
        idc=int(request.form['idcommento'])
        script.delete_comment(idc)

    return redirect(url_for('manga_details', id=idm))

#route per la rimozione o aggiunta di un manga ai preferiti di un utente
@app.route('/actionfavorite/<int:idm>',methods=['GET', 'POST'])
def azione_preferiti(idm):
    if request.method=="POST":
        idu=session["user_id"]

        #controllo presenza tra i preferiti
        presente=script.is_favorite(idu,idm)

        if presente:

            #rimosso dai preferiti
            script.delete_favorite(idu,idm)  
        else:

            #aggiunta ai preferiti
            script.add_favorite(idu,idm)   
            
    return redirect(url_for('manga_details', id=idm))


if __name__ == '__main__':
    app.run(debug=True)
