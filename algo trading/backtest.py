import MetaTrader5 as mt5
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# --- 1. DÉFINITION DE LA STRATÉGIE pour la bibliothèque ---
# On doit créer une "Classe" (c'est de la programmation objet,
# mais suis le modèle, c'est simple)

class MaStratCroisementMM(Strategy):
    # Paramètres de la stratégie
    mm_courte = 20
    mm_longue = 50

    def init(self):
        # Cette fonction est appelée au début.
        # On pré-calcule nos indicateurs.
        
        # 'self.data.Close' est un raccourci pour la colonne 'close'
        self.mm_courte_series = self.I(lambda x: pd.Series(x).rolling(self.mm_courte).mean(), self.data.Close)
        self.mm_longue_series = self.I(lambda x: pd.Series(x).rolling(self.mm_longue).mean(), self.data.Close)

    def next(self):
        # Cette fonction est appelée pour CHAQUE bougie (heure)
        
        # 'crossover(serie_1, serie_2)' est une fonction magique de la
        # bibliothèque qui est VRAIE seulement au moment du croisement
        
        # Si la MM courte croise AU-DESSUS de la MM longue
        if crossover(self.mm_courte_series, self.mm_longue_series):
            self.buy() # Signal d'achat

        # Si la MM courte croise EN DESSOUS de la MM longue
        elif crossover(self.mm_longue_series, self.mm_courte_series):
            self.sell() # Signal de vente


# --- 2. RÉCUPÉRATION DES DONNÉES (comme avant) ---
print("Connexion à MT5 pour les données...")
if not mt5.initialize():
    print("initialize() a échoué")
    quit()

# On prend BEAUCOUP plus de données pour un backtest !
# 20 000 bougies H1 = environ 2.2 ans
rates = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_H1, 0, 20000)
mt5.shutdown()

if rates is None:
    print("Pas de données récupérées.")
    quit()

# --- 3. PRÉPARATION DES DONNÉES (formatage OBLIGATOIRE) ---
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
df.set_index('time', inplace=True)

# La bibliothèque backtesting.py EXIGE ces noms de colonnes :
# 'Open', 'High', 'Low', 'Close', 'Volume' (avec des majuscules)
df.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'tick_volume': 'Volume'
}, inplace=True)

print(f"Données prêtes : {len(df)} bougies récupérées.")

# --- 4. LANCEMENT DU BACKTEST ---
# On crée le backtest
# On simule un capital de 10,000$
# On simule une commission de 0.2% (très important !)
bt = Backtest(df, MaStratCroisementMM, cash=10000, commission=.002)

# On lance la simulation
stats = bt.run()

# --- 5. AFFICHER LES RÉSULTATS ---
print("\n--- RÉSULTATS DU BACKTEST ---")
print(stats)

# Générer un graphique HTML interactif !
bt.plot(filename='mon_backtest.html')
print("\nUn fichier 'mon_backtest.html' a été créé.")
print("Ouvrez-le dans votre navigateur pour voir le graphique interactif.")