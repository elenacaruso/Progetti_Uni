import sqlite3
import numpy as np
from codetiming import Timer
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import svds
import math

#Costruisce i dizionari: dizionarioUte={utente->coefficiente di probabilita'} e dizionarioFilm={film->coefficiente di probabilita'}.
##Crea e riempie le tabelle indiceU(utente,indice, PRIMARY KEY(utente)) e indiceF(film,indice, PRIMARY KEY(film)),
##dove seguendo l'ordine numerico vengono assegnati ad ogni utente e film un codice.
###Ritorna i due dizionari.
def dizionari():
    #inziate la tabelle su sql e i dizionari
    cur.execute("CREATE TABLE IF NOT EXISTS indiceU(utente,indice, PRIMARY KEY(utente))")
    cur.execute("CREATE TABLE IF NOT EXISTS indiceF(film,indice, PRIMARY KEY(film))")
    dizionarioUte={}
    dizionarioFilm={}
    
    #si riempiono il dizionario e la tabella relative ad utente
    cur.execute("SELECT utente, perc2 FROM utente")
    ute=cur.fetchall()
    indiceU=0
    for u in ute:
        cur.execute("INSERT INTO indiceU values(?,?)",(u[0],indiceU))
        dizionarioUte[u[0]]=u[1]
        indiceU=indiceU+1
    
    #si riempiono il dizionario e la tabella relative a film    
    cur.execute("SELECT film, perc2 FROM film")
    indiceF=0
    fil=cur.fetchall()
    for f in fil:
        cur.execute("INSERT INTO indiceF values(?,?)",(f[0],indiceF))
        dizionarioFilm[f[0]]=f[1]
        indiceF=indiceF+1
        
    print("Effettuata la creazione dei dizionari.")
    return dizionarioUte,dizionarioFilm

#A dal numero k di elementi da scegliere e dai dizionari,
#ritorna k utenti e k film che vengono scelti casualmente seguendo una distribuzione multinomiale
def sceltak(k,dizionarioUte,dizionarioFilm):
    #A partire dai dizionari crea 4 np.array, necessari per la scelta casuale
    ArUte=np.array(list(dizionarioUte.keys()))
    ArPer=np.array(list(dizionarioUte.values()))
    AcFil=np.array(list(dizionarioFilm.keys()))
    AcPer=np.array(list(dizionarioFilm.values()))

    #vengono scelti k utenti e k film seguendo una distribzione multinomile. Le probabilità sono dati dagli oggetti dei dizionari
    kutenti=np.random.choice(ArUte, size=k, replace=True, p=ArPer)
    kfilm=np.random.choice(AcFil, size=k, replace=True, p=AcPer)

    print("Effettuata la scelta dei",k,"elementi.")
    return kutenti,kfilm

#Dando il numero k di elementi necessari, il dizionario riferito a film e il vettore dei k film scelti, viene calcolata la matrice C in SQL.
def calcC(k,dizionarioFilm,kfilm):
    cur.execute("CREATE TABLE IF NOT EXISTS c(utenteI INT,filmI INT,val REAL, PRIMARY KEY(utenteI,filmI))")
    
    #per ogni film scelto viene prese la colonna corrispondente e il valore di valutazione viene diviso per sqrt(dizionarioFilm.get(kfilm[i])*k)
    for i in range(k):
            cur.execute("INSERT INTO c SELECT indice, ?, CAST(val AS REAL)/? FROM indiceU NATURAL JOIN (SELECT val, utente FROM valutazione WHERE film=?)",
                        (i,math.sqrt(dizionarioFilm.get(kfilm[i])*k),int(kfilm[i])))
    con.commit()
    print("Calcolata C, è contenuta nella tabella sql c.")

#Dando il numero k di elementi necessari, il dizionario riferito a utenti e il vettore dei k utenti scelti, viene calcolata la matrice R in SQL.            
def calcR(k,dizionarioUte,kutenti):
    cur.execute("CREATE TABLE IF NOT EXISTS r(utenteI INT,filmI INT,val REAL, PRIMARY KEY(utenteI,filmI))")

    #per ogni utente scelto viene presa la colonna corrispondente e il valore di valutazione viene diviso per sqrt(dizionarioUte.get(kutenti[i])*k) 
    for i in range(k):
        cur.execute("INSERT INTO r SELECT ?, indice, CAST(val AS REAL)/? FROM indiceF NATURAL JOIN (SELECT val, film FROM valutazione WHERE utente=? )",
                        (i,math.sqrt(dizionarioUte.get(kutenti[i])*k),int(kutenti[i])))
    print("Calcolata R, è contenuta nella tabella sql r.")
    con.commit()

#Dando il numero k, gli utenti e i film scelti viene calcolata la matrice U e viene inserita in SQL nella tabella u(utenteI INT,filmI INT,val REAL, PRIMARY KEY(utenteI,filmI))
def calcU(k,kutenti,kfilm):
    #Si costruisce la matrice W come matrice coo_matrix.
    indUteW=[]
    indFilmW=[]
    valW=[]
    f=0
    u=0
    for i in range(k):
        for j in range(k):         
            cur.execute("SELECT val FROM valutazione WHERE utente=? AND film=?", (int(kutenti[j]),int(kfilm[i])))
            cc=cur.fetchone()
            if cc!=None:
                indUteW.append(j)
                indFilmW.append(i)
                valW.append(float(cc[0]))        
    W=coo_matrix((valW,(indUteW,indFilmW)),shape=(k,k))

    #Si effettua la decomposizione SVD sulla matrice W
    X,sigma,Yt=svds(W, k=k-1, ncv=None, tol=0, which='LM', v0=None, maxiter=None, return_singular_vectors=True, solver='arpack', random_state=None, options=None)
    #Si calcola la psuedoinversa
    psSigma=np.linalg.pinv(np.diag(sigma))
    #Si calcola la matrice U
    U=X @ psSigma @ Yt
    #Caricata su SQL nella tabella u
    cur.execute("CREATE TABLE IF NOT EXISTS u(utenteI INT,filmI INT,val REAL, PRIMARY KEY(utenteI,filmI))")
    i=0
    j=0
    for u in U:
        for uu in u:
            cur.execute("INSERT INTO u values(?,?,?)",(i,j,uu))
            j=j+1
        i=i+1
    print("Calcolata U")
    con.commit()

#Funzione che a partire dai dizionari Utente e Film calcola la CUR per il k dato. Ritorna il tempo trascorso
def calcolaCUR(k,dizionarioUte,dizionarioFilm):
    t = Timer(name="class")
    t.start()
    kutenti,kfilm=sceltak(k,dizionarioUte,dizionarioFilm)
    
    calcC(k,dizionarioFilm,kfilm)
    calcR(k,dizionarioUte,kutenti)
    calcU(k,kutenti,kfilm)
    fine=t.stop()
    return fine

def prodottoCUR():
    cur.execute("CREATE TABLE IF NOT EXISTS cu(utenteI INT,filmI INT,val REAL, PRIMARY KEY(utenteI,filmI))")
    cur.execute("CREATE TABLE IF NOT EXISTS cur(utenteI INT,filmI INT,val REAL, PRIMARY KEY(utenteI,filmI))")

    cur.execute("INSERT INTO cu SELECT c.utenteI,u.filmI,SUM(c.val*u.val) FROM c JOIN u ON c.filmI=u.utenteI GROUP BY c.utenteI,u.filmI")

    cur.execute("INSERT INTO cur SELECT cu.utenteI,r.filmI,SUM(cu.val*r.val) FROM cu JOIN r ON cu.filmI=r.utenteI GROUP BY cu.utenteI,r.filmI")
    cur.execute("DROP TABLE cu")

    
def differenzaCURA():
    cur.execute("SELECT sum((cur.val-valutazione.val)*(cur.val-valutazione.val)) FROM cur JOIN indiceU ON cur.utenteI=indiceU.indice JOIN indiceF ON cur.filmI=indiceF.indice JOIN valutazione ON valutazione.utente=indiceU.utente AND valutazione.film=indiceF.film")
    return cur.fetchone()[0]
    
#Funzione che effettua il drop delle tabelle c,u,r e cur
def dropCUR():
    cur.execute("DROP TABLE c")
    cur.execute("DROP TABLE u")
    cur.execute("DROP TABLE r")
    cur.execute("DROP TABLE cur")
    con.commit()

if __name__=='__main__':
    dbname= 'lui2.db'
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    fx = open("valoricampione.txt","w")
    
    #prodottoCUR(k)
    dizionarioUte,dizionarioFilm=dizionari()
    tempok=0
    for k in range(10,50,10):
        tempok=calcolaCUR(k,dizionarioUte,dizionarioFilm)
        prodottoCUR()
        frobk=differenzaCURA()
        print(k,"fatto")
        print(k,tempok,frobk,file=fx)
        dropCUR()
    print("fatto tutto")
    fx.close()
    con.commit()
    con.close()
