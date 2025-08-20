import sqlite3

#Apre file di nome fname e insersice i valori nel database di nome dbname
#Crea tabella valutazione(film,utente,val) e la riempie
def CreazioneValutazione(fname,dbname):
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS valutazione (film, utente, val INT, PRIMARY KEY(film,utente))")
    file=open(fname, mode='r')
    film=0
    utente=0
    val=0
    while lett:= file.readline():
         if ':' in lett :
             film= int(lett.replace(":\n",""))
             print(film)
         else:
             vect=lett.split(',')
             utente= int(vect[0])
             val=int(vect[1])
             cur.execute("insert into valutazione values (?, ?, ?)", (film, utente, val))
    print("Fatto")
    file.close()
    con.commit()
    con.close()

def FilmUtente(dbname):
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    cur.execute( "SELECT SUM(val*val) FROM valutazione")
    SOMMATOT2= int(cur.fetchone()[0])
    cur.execute("CREATE TABLE IF NOT EXISTS utente(utente,somma2 INT,perc2 REAL, PRIMARY KEY(utente))")
    cur.execute("INSERT INTO utente SELECT utente,SUM(val*val),cast(SUM(val*val) as REAL)/?  FROM valutazione GROUP BY utente",(SOMMATOT2,))
    
    cur.execute("CREATE TABLE IF NOT EXISTS film(film,somma2 INT,perc2 REAL, PRIMARY KEY(film))")
    cur.execute("INSERT INTO film SELECT film,SUM(val*val),cast(SUM(val*val) as REAL)/?  FROM valutazione GROUP BY film",(SOMMATOT2,))
    print("Creato film e utente!")
    con.commit()
    con.close()
    
if __name__=='__main__':
    fname="combined_data_1.txt"
    dbname= 'ciccio1.db'

    FilmUtente(dbname)


            
            
