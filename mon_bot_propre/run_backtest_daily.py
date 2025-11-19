import pandas as pd
from backtesting import Backtest
import os

from strategies.strat_daily_mr import StratDailyMR

CSV_FILE = os.path.join("data", "IWM-D1-2010-2025.csv")

def charger_et_preparer_donnees():
    print(f"Chargement des données {CSV_FILE}...")
    try:
        df = pd.read_csv(CSV_FILE, skiprows=[0,1])
        df.columns = ['Time', 'Close', 'High', 'Low', 'Open', 'Volume']
        df['Time'] = pd.to_datetime(df['Time'])
        df.set_index('Time', inplace=True)
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        df = df.apply(pd.to_numeric, errors='coerce')
    except FileNotFoundError:
        print(f"ERREUR: Fichier {CSV_FILE} non trouvé. Lancez utils/download_data_daily.py")
        return None

    df = df[~df.index.duplicated(keep='first')]
    df.dropna(inplace=True)
    
    print(f"Données prêtes : {len(df)} bougies.")
    return df

print(f"Lancement du Backtest (StratDailyMR sur {CSV_FILE})...")

df = charger_et_preparer_donnees()

if df is not None:
    
    STRATEGIE_A_TESTER = StratDailyMR
    NOM_RAPPORT_HTML = 'backtest_iwm_daily_mr.html'
    
    bt = Backtest(df, STRATEGIE_A_TESTER, cash=10000, commission=.001)
    
    stats = bt.run()

    print(f"\n\n--- RÉSULTATS FINAUX (IWM Daily MR) ---")
    print("-------------------------------------------------------")
    print(stats)
    print("-------------------------------------------------------")
    
    bt.plot(filename=NOM_RAPPORT_HTML)
    print(f"\nFichier '{NOM_RAPPORT_HTML}' créé.")
else:
    print("Erreur lors du chargement des données. Backtest annulé.")