# progetto_django
Questo progetto è un'applicazione web sviluppata in Django per la gestione di ristoranti, con funzionalità di registrazione utenti, prenotazioni, recensioni, gestione delle strutture. Gli utenti possono esplorare i ristoranti, fare prenotazioni, lasciare recensioni, e i proprietari possono visualizzare grafici sull'andamento delle strutture. Gli amministratori hanno pieno controllo sul sistema, incluso l'aggiunta, la modifica e la cancellazione delle strutture e degli utenti.
Caratteristiche principali:

    Gestione utenti: Registrazione, login, e gestione degli account.
    Gestione ristoranti: Aggiunta, visualizzazione e gestione dei ristoranti.
    Prenotazioni: Sistema per prenotare in un ristorante e gestire le prenotazioni.
    Recensioni: Gli utenti possono lasciare recensioni sui ristoranti.
    Grafici: Visualizzazione dei dati sugli andamenti dei ristoranti.
    Admin: Pieno controllo sulle operazioni tramite un'interfaccia amministrativa.

INFORMAZIONI DI UTILIZZO:
il database del sito è stato impostato per avere dei ristoranti, nelle città di Carpi e Modena.
Essendo a scopo didattico non è sembrato utile aggiungere molte altre città.


  __________________________

  INSTALLAZIONE
  1) è possibile clonare il repository a questo url "https://github.com/mattepella/progetto_tecweb" oppure scaricare il file zip ed estrarlo
  2) una volta ottenuta la cartella contente il progetto, si suggerisce di creare un ambiente virtuale in questo modo:
python -m venv venv
dopo di chè attiviamo l'ambiente virtuale
WINDOWS:
venv\Scripts\activate
LINUX:
source venv/bin/activate

  4) installare le dipendenze necessarie, incluse nel file requirements.txt
     pip install -r requirements.txt

  5) caricare il database esistente:
    python manage.py migrate
    
  6) avviare il server di sviluppo
    python manage.py runserver
 
  7) visualizzare il sito
     Apri il browser e vai su http://127.0.0.1:8000/ per visualizzare l'applicazione in esecuzione localmente.
