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

