# MangaProject

## Descrizione progetto

Il progetto consiste nello sviluppo di una webapp Flask collegato a un database MySQL. Per l'uso di alcune funzionalità la webapp verrà affiancata a un'API di intelligenza artificiale (GPT-4) .

La webapp permetterà la visualizzazione di una lista di manga, sopra di essa ci sarà una navbar che permetterà la registrazione e il login. Cliccando su uno dei manga nella lista si potrà visualizzare le informazioni inerenti a quel manga, come per esempio la descrizione, i volumi e i capitoli . Si avrà accesso alla visualizzazione delle tavole di ogni singolo volume del manga cliccando al relativo volume interessato e specificandone il capitolo (chiunque potrà visualizzare le tavole, anche gli utenti non registrati).

C'è la possibilità di registrarsi al sito , sbloccando nuove funzionalità:
- cronologia dei manga visti
- lista dei manga piaciuti (nella pagina di visualizzazione del manga si potrà mettere il "mi piace" nell'icona apposita
- la possibilità di utilizzare un IA per farsi consigliare ulteriori manga da leggere  (uso dell'api GPT-4) 

Gli utenti registrati potranno interagire tra di loro, ricercare gli utenti, seguirli e visualizzare il loro profilo con le relative informazioni dell'utente

Nella pagina del profilo saranno presenti 
- nickname
- codice identificativo (ID)
- cronologia manga visti
- manga piaciuti
- immagine profilo
- nome e cognome 

Per la registrazione di un utente si necessitano delle seguenti informazioni da inserire nel form:
- nickname
- immagine profilo (si potrà aggiungere un immagine successivamente)
- nome e cognome 
- email
- password
- data di nascita

L'id verrà creato automaticamente dal database , e sarà univoco. Non esisteranno utenti con lo stesso nickname. 

## ANALISI DEI RISCHI

- Caricare sul database in modo efficiente i dati riguardanti ogni manga (PROBABILITA : 2 , DANNO : 3)

- Gestire la visualizzazione corretta delle immagini (not out of bound)  (PROBABILITA : 2 , DANNO : 1)

- Le immagini del capitolo impiegheranno tempo a visualizzarsi a causa di conessione scarsa (PROBABILITA : 3 , DANNO : 1)

- Recuperare  i dati forniti da chatGPT in formato JSON (PROBABILITA : 2, DANNO : 2)

- Creare un template NON originale e creativo (PROBABILITA : 1 , DANNO : 1)


## DATE E REALESE

Ecco le varie realese del progetto:

- 12 maggio : Pagina home in cui vengono visualizzati una dozzina di fumetti con anteprima la copertina e la trama del fumetto

- 17 maggio : Possibilita di visualizzare una pagina riguardante il fumetto con aggiunta i generi, gli autori, gli artisti e la lista dei capitoli

- 19 maggio : Sarà possibile visualizzare ogni capitolo di ogni manga, in modalita lettura e con passaggio al capitolo successivo

- 24 maggio : Aggiunta una sezione di ricerca in cui è possibile ricercare un fumetto in base al nome, artista, autore, genere...

- 26 maggio : Verrà aggiunta una sezione registra e login, in cui un utente potrà registrarsi e visualizzare i manga preferiti e lasciare un commento sotto ogni manga

- 31 maggio : Tramite l'api di chatGPT sarà possibile ogni utente potra farsi consigliare un manga da leggere in base alle sue richieste
