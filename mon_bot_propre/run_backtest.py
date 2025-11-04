# Fichier : run_backtest.py

import pandas as pd
from backtesting import Backtest
import os

# --- 1. Importer mes stratégies ---
# On importe SEULEMENT la classe de la stratégie
from strategies.strat_ma_crossover import StratMACrossover
# (On n'importe pas d'indicateurs ici, C'EST LA CORRECTION)


# --- 2. Fonction pour charger les données ---
def charger_et_preparer_donnees():
    NOM_FICHIER_CSV = os.path.join("data", "XAUUSD-H1-2014-2024.csv")
    print(f"Chargement des données depuis {NOM_FICHIER_CSV}...")
    
    try:
        df = pd.read_csv(NOM_FICHIER_CSV)
    except FileNotFoundError:
        print(f"\nERREUR: Fichier '{NOM_FICHIER_CSV}' non trouvé.")
        print("Lancer d'abord 'python utils/download_data.py'")
        quit()
    
    print("Données brutes chargées.")
    
    # Formater les colonnes
    df.rename(columns={
        'Time': 'time', 'open': 'Open', 'high': 'High',
        'low': 'Low', 'close': 'Close', 'volume': 'Volume'
    }, inplace=True)
    
    # Mettre la date en index
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    
    df = df[~df.index.duplicated(keep='first')]
    df.dropna(inplace=True)
    
    print(f"Données formatées et prêtes : {len(df)} bougies.")
    return df

# --- 3. Choisir la Stratégie ---
STRATEGIE_A_TESTER = StratMACrossover
NOM_RAPPORT_HTML = 'backtest_ma_crossover.html'


# --- 4. Lancer le Backtest ---
df = charger_et_preparer_donnees()

print(f"\nLancement du backtest pour : {STRATEGIE_A_TESTER.__name__}...")

# Pas de pré-calcul ici. La strat s'en occupe.
bt = Backtest(df, STRATEGIE_A_TESTER, cash=10000, commission=.002)
stats = bt.run() # Lancer la simulation

# --- 5. Résultats ---
print("\n--- RÉSULTATS DU BACKTEST ---")
print(stats) # Afficher les stats

bt.plot(filename=NOM_RAPPORT_HTML) # Créer le HTML
print(f"\nFichier '{NOM_RAPPORT_HTML}' créé.")