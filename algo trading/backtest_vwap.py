import pandas as pd
import pandas_ta as ta # ### NOUVEAU : On importe Pandas-TA ###
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# --- 1. DÉFINITION DE LA STRATÉGIE (VWAP + Volume) ---
class StratVWAP(Strategy):
    # Paramètres de la stratégie
    volume_moyenne_periode = 30 # Moyenne du volume sur 30 heures

    def init(self):
        # Cette fonction est appelée au début.
        # On utilise pandas-ta (ta) pour calculer les indicateurs.
        
        # 'self.data.df' donne accès au DataFrame Pandas complet
        # pandas-ta a besoin des colonnes 'High', 'Low', 'Close', 'Volume'
        
        # 1. Calculer le VWAP
        # Il se calcule automatiquement sur la journée, c'est ce qu'on veut.
        self.vwap = self.I(ta.vwap, self.data.High, self.data.Low, self.data.Close, self.data.Volume)
        
        # 2. Calculer la moyenne mobile du Volume
        self.volume_sma = self.I(ta.sma, self.data.Volume, length=self.volume_moyenne_periode)

    def next(self):
        # Cette fonction est appelée pour CHAQUE bougie (heure)
        
        prix_actuel = self.data.Close[-1]
        volume_actuel = self.data.Volume[-1]
        
        # --- Conditions d'ACHAT ---
        # 1. Le prix est au-dessus du VWAP
        condition_prix = prix_actuel > self.vwap[-1]
        
        # 2. Le volume est "anormal" (plus haut que la moyenne)
        condition_volume = volume_actuel > self.volume_sma[-1]
        
        # --- Conditions de VENTE (Sortie de trade) ---
        # 1. Le prix repasse en dessous du VWAP
        condition_sortie = prix_actuel < self.vwap[-1]

        
        # --- Logique d'exécution ---
        
        # Si on n'est PAS en position ET que nos conditions d'achat sont réunies
        if not self.position:
            if condition_prix and condition_volume:
                # On achète ! (On met un SL de 2% pour la sécurité)
                sl_achat = prix_actuel * 0.98 # Stop Loss 2%
                self.buy(sl=sl_achat)
                
        # Si on EST en position ACHETEUR et que la condition de sortie est réunie
        elif self.position.is_long:
            if condition_sortie:
                # On ferme la position
                self.position.close()


# --- 2. RÉCUPÉRATION DES DONNÉES (depuis le CSV) ---
NOM_DU_FICHIER_CSV = "XAUUSD-H1-2014-2024.csv" 
print(f"Chargement des données depuis {NOM_DU_FICHIER_CSV}...")

try:
    df = pd.read_csv(NOM_DU_FICHIER_CSV)
except FileNotFoundError:
    print(f"\nERREUR: Le fichier '{NOM_DU_FICHIER_CSV}' n'a pas été trouvé.")
    print("Veuillez d'abord lancer 'download_data.py' (demain, quand les marchés seront ouverts).")
    quit()

print("Données brutes chargées.")

# --- 3. PRÉPARATION DES DONNÉES (formatage OBLIGATOIRE) ---
df.rename(columns={
    'Time': 'time',
    'Open': 'Open',
    'High': 'High',
    'Low': 'Low',
    'Close': 'Close',
    'Volume': 'Volume'
}, inplace=True)

df['time'] = pd.to_datetime(df['time'])
df.set_index('time', inplace=True)
df = df[~df.index.duplicated(keep='first')]
df.dropna(inplace=True)

# !!! TRÈS IMPORTANT POUR PANDAS-TA !!!
# La bibliothèque a besoin que les colonnes soient en minuscule pour
# les reconnaître automatiquement.
df.columns = [col.lower() for col in df.columns]

print(f"Données formatées et prêtes : {len(df)} bougies.")

# --- 4. LANCEMENT DU BACKTEST ---
print("Lancement du backtest (VWAP + Volume)...")

bt = Backtest(df, StratVWAP, cash=10000, commission=.002)
stats = bt.run()

# --- 5. AFFICHER LES RÉSULTATS ---
print("\n--- RÉSULTATS DU BACKTEST (VWAP) ---")
print(stats)

# Générer un graphique HTML interactif !
bt.plot(filename='backtest_vwap.html')
print("\nUn fichier 'backtest_vwap.html' a été créé.")
print("Ouvrez-le dans votre navigateur pour voir le graphique interactif.")