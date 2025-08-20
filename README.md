# CUR Decomposition Project  

## 📌 Descrizione  
Questo progetto implementa e analizza la **decomposizione CUR** come alternativa alla **SVD (Singular Value Decomposition)** per l’approssimazione a rango basso di matrici di grandi dimensioni.  
L’obiettivo è valutare **accuratezza, efficienza e consumo di risorse** della CUR rispetto alla SVD, utilizzando dataset reali.  

## 🎯 Obiettivi  
- Implementare la decomposizione CUR in Python.  
- Confrontarla con la SVD in termini di:  
  - accuratezza (norma di Frobenius),  
  - tempo di calcolo,  
  - memoria e spazio disco utilizzati.  
- Studiare l’impatto della quantità di dati e del parametro `k`.  

## 🛠️ Strumenti utilizzati  
- **Dataset**: [Netflix Prize Data](https://www.kaggle.com/datasets/netflix-inc/netflix-prize-data) (~100M valutazioni, 480k utenti, 17k film).  
- **Librerie principali**:  
  - `numpy`, `scipy` (SVD e gestione matrici sparse),  
  - `sqlite3` (archiviazione dati),  
  - `psutil`, `codetiming` (monitoraggio prestazioni).  
- **Ambiente di test**:  
  - Windows 10/11, CPU Intel i5/i7, RAM 8–16 GB.  

## ⚠️ Criticità riscontrate
- Difficoltà nel calcolo dell’accuratezza della CUR su matrici sparse di grandi dimensioni.  
- SQL utile per l’archiviazione, ma inefficiente per operazioni algebriche.  
- Limitazioni hardware che impediscono l’uso dell’intero dataset.  

## 🚀 Possibili sviluppi futuri
- Calcolare l’accuratezza di CUR sull’intero dataset.  
- Applicare CUR a sistemi di raccomandazione reali.  
- Eseguire gli esperimenti su macchine più potenti per aumentare scala e qualità dei risultati. 



























































































