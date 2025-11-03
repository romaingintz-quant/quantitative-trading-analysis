import pandas as pd
import pandas_ta as ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# --- 1. DÉFINITION DE LA STRATÉGIE (RSI + Filtre EMA) ---
class StratRSI_EMA(Strategy):
    periode_rsi = 14
    seuil_survente_rsi = 30
    seuil_surachat_rsi = 70
    periode_ema = 200

    def init(self):
        # On passe les colonnes manuellement (ex: self.data.Close)
        self.rsi = self.I(ta.rsi, self.data.Close, length=self.periode_rsi)
        self.ema_longue = self.I(ta.ema, self.data.Close, length=self.periode_ema)

    def next(self):
        prix_actuel = self.data.Close[-1]
        
        # --- DÉFINIR LES CONDITIONS ---
        tendance_haussiere = prix_actuel > self.ema_longue[-1]
        signal_achat = crossover(self.rsi, self.seuil_survente_rsi)
        signal_sortie = crossover(self.seuil_surachat_rsi, self.rsi)

        
        # --- LOGIQUE D'EXÉCUTION ---
        if not self.position:
            if tendance_haussiere and signal_achat:
                sl_achat = prix_actuel * 0.97 
                self.buy(sl=sl_achat)
                
        elif self.position.is_long:
            if signal_sortie:
                self.position.close()


# --- 2. RÉCUPÉRATION DES DONNÉES (depuis le CSV) ---
NOM_DU_FICHIER_CSV = "XAUUSD-H1-2014-2024.csv" 
print(f"Chargement des données depuis {NOM_DU_FICHIER_CSV}...")

try:
    df = pd.read_csv(NOM_DU_FICHIER_CSV)
except FileNotFoundError:
    print(f"\nERREUR: Le fichier '{NOM_DU_FICHIER_CSV}' n'a pas été trouvé.")
    print("Veuillez d'abord lancer 'download_data.py'.")
    quit()

print("Données brutes chargées.")

# --- 3. PRÉPARATION DES DONNÉES (LA CORRECTION EST ICI) ---

# On traduit les noms du CSV (minuscules) vers
# les noms exigés par backtesting.py (MAJUSCULES)
df.rename(columns={
    'Time': 'time',   # Le 'T' majuscule vient du CSV
    'open': 'Open',   # 'open' (csv) -> 'Open' (backtest)
    'high': 'High',   # 'high' (csv) -> 'High' (backtest)
    'low': 'Low',     # 'low' (csv)  -> 'Low' (backtest)
    'close': 'Close', # 'close' (csv)-> 'Close' (backtest)
    'volume': 'Volume' # 'volume' (csv)-> 'Volume' (backtest)
}, inplace=True)

df['time'] = pd.to_datetime(df['time'])
df.set_index('time', inplace=True)
df = df[~df.index.duplicated(keep='first')]
df.dropna(inplace=True)

print(f"Données formatées et prêtes : {len(df)} bougies.")

# --- 4. LANCEMENT DU BACKTEST ---
print("Lancement du backtest (RSI + Filtre EMA 200)...")

bt = Backtest(df, StratRSI_EMA, cash=10000, commission=.002)
stats = bt.run()

# --- 5. AFFICHER LES RÉSULTATS ---
print("\n--- RÉSULTATS DU BACKTEST (RSI + EMA) ---")
print(stats)

bt.plot(filename='backtest_rsi.html')
print("\nUn fichier 'backtest_rsi.html' a été créé.")
print("Ouvrez-le pour voir la simulation.")