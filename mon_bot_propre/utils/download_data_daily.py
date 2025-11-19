# Fichier : utils/download_data_daily.py
# (Nouveau script pour télécharger les données Daily des Actions/ETFs)

import yfinance as yf
import pandas_ta as ta # On l'importe ici pour être sûr qu'il est installé
import os
from datetime import datetime

# --- Paramètres ---
SYMBOLS = ['IWM', 'SPY'] # IWM (Russell 2000), SPY (S&P 500 pour comparer)
START_DATE = "2010-01-01"
END_DATE = datetime.now().strftime('%Y-%m-%d')

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- Exécution ---
if __name__ == "__main__":
    print("Téléchargement des données Daily (via yfinance)...")
    
    for symbol in SYMBOLS:
        try:
            print(f"Téléchargement de {symbol}...")
            data = yf.download(symbol, start=START_DATE, end=END_DATE, interval="1d")
            
            if data.empty:
                print(f"Aucune donnée reçue pour {symbol}.")
                continue
                
            # yfinance utilise déjà les bons noms (Open, High, Low, Close, Volume)
            # On renomme juste l'index pour être cohérent
            data.index.name = "Time"
            
            # Nom du fichier
            filename = f"{symbol}-D1-{START_DATE[:4]}-{END_DATE[:4]}.csv"
            filepath = os.path.join(DATA_DIR, filename)
            
            data.to_csv(filepath)
            print(f"Données pour {symbol} sauvegardées dans {filepath}")

        except Exception as e:
            print(f"Erreur lors du téléchargement de {symbol}: {e}")
            
    print("Téléchargement terminé.")