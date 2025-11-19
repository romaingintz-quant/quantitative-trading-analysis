# Fichier : utils/download_data.py
# (Version 4 - Ajout de XAUUSD H1/M15)

import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import os

# --- Paramètres de Téléchargement ---
# On s'assure d'avoir tous les actifs
SYMBOLS = ["EURUSD", "USDX", "XAUUSD"] 
TIMEFRAMES = {
    'M15': mt5.TIMEFRAME_M15,
    'H1': mt5.TIMEFRAME_H1,
}
DATE_FROM = datetime(2023, 1, 1) 
DATE_TO = datetime.now()

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- Connexion à MT5 ---
def connect_to_mt5():
    if not mt5.initialize():
        print(f"initialize() a échoué, code d'erreur = {mt5.last_error()}")
        return False
    print("Connecté à MT5 avec succès.")
    return True

# --- Fonction de Téléchargement ---
def download_data(symbol, timeframe_mt5, start_date, end_date):
    tf_name = [name for name, val in TIMEFRAMES.items() if val == timeframe_mt5][0]
    print(f"Téléchargement de {symbol} en {tf_name}...")
    
    try:
        rates = mt5.copy_rates_range(symbol, timeframe_mt5, start_date, end_date)
        
        if rates is None or len(rates) == 0:
            print(f"Aucune donnée reçue pour {symbol} en {tf_name}. Erreur MT5: {mt5.last_error()}")
            return None
            
        df = pd.DataFrame(rates)
        df['Time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('Time', inplace=True)
        df.drop('time', axis=1, inplace=True)
        
        df.rename(columns={
            'open': 'Open', 'high': 'High', 'low': 'Low',
            'close': 'Close', 'tick_volume': 'Volume'
        }, inplace=True)
        
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        print(f"Données reçues pour {symbol} {tf_name} : {len(df)} bougies.")
        return df

    except Exception as e:
        print(f"Erreur {symbol} {tf_name}: {e}")
        return None

# --- Exécution Principale ---
if __name__ == "__main__":
    if connect_to_mt5():
        for symbol in SYMBOLS:
            for tf_name, tf_mt5 in TIMEFRAMES.items():
                
                # Le DXY n'a peut-être pas de M15, on saute
                if symbol == "DXY" and tf_name == "M15":
                    print("Saut du téléchargement M15 pour DXY (non nécessaire).")
                    continue

                # Le nom du fichier de XAUUSD peut-être différent
                symbol_filename = symbol
                if symbol == "XAUUSD":
                    # Ajuste ceci si ton broker utilise "GOLD" ou "XAUUSD.m"
                    symbol_filename = "XAUUSD" 

                filename = f"{symbol_filename}-{tf_name}-{DATE_FROM.year}-{DATE_TO.year}.csv"
                filepath = os.path.join(DATA_DIR, filename)
                
                data = download_data(symbol, tf_mt5, DATE_FROM, DATE_TO)
                
                if data is not None:
                    data.to_csv(filepath)
                    print(f"Données sauvegardées : {filepath}")
                else:
                    print(f"Échec de la sauvegarde pour {symbol} {tf_name}.")
                
        mt5.shutdown()
        print("Déconnecté de MT5.")
    else:
        print("Impossible d'exécuter le script sans connexion MT5.")