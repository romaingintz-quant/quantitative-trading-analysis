import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt  ### NOUVEAU ###

# --- ÉTAPE 1: CONNEXION À METATRADER 5 ---
print("Lancement du script...")

if not mt5.initialize():
    print("initialize() a échoué, erreur =", mt5.last_error())
    quit()

print("Connecté à MetaTrader 5!")

# --- ÉTAPE 2: RÉCUPÉRER LES DONNÉES HISTORIQUES (XAUUSD) ---
symbol = "XAUUSD"
timeframe = mt5.TIMEFRAME_H1
nb_bougies = 1000  # On va garder 1000 bougies pour le calcul

rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, nb_bougies)
mt5.shutdown()
print("Connexion MT5 fermée.")

if rates is None:
    print(f"N'a pas pu récupérer les données pour {symbol}, erreur={mt5.last_error()}")
    quit()

# --- ÉTAPE 3: TRANSFORMER LES DONNÉES AVEC PANDAS ---
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
# On utilise la colonne 'time' comme index du graphique
df.set_index('time', inplace=True) 

print(f"Données pour {symbol} récupérées avec succès.")
# print(df.tail()) # On peut le commenter, plus besoin de l'afficher ici


# --- ÉTAPE 4: SIMULATION (BACKTEST TRÈS SIMPLE) ---
print("\n--- Lancement de la simulation (Backtest) ---")

mm_courte = 20
mm_longue = 50

df['MM_courte'] = df['close'].rolling(window=mm_courte).mean()
df['MM_longue'] = df['close'].rolling(window=mm_longue).mean()

# On enlève le signal, on se concentre sur le graphique
# (Vous pouvez le garder si vous voulez)
print("Calcul des moyennes mobiles terminé.")


# --- ÉTAPE 5: VISUALISATION AVEC MATPLOTLIB ### NOUVEAU ### ---
print("\n--- Génération du graphique ---")

# On ne veut afficher que les 200 dernières bougies pour y voir clair
df_recent = df.iloc[-200:]

# 1. Créer la figure (le cadre du graphique)
plt.figure(figsize=(15, 8)) # Taille du graphique (largeur, hauteur en pouces)

# 2. Tracer les lignes
plt.plot(df_recent.index, df_recent['close'], label='Prix de Clôture (XAUUSD)', color='blue', alpha=0.7)
plt.plot(df_recent.index, df_recent['MM_courte'], label=f'MM {mm_courte} heures', color='orange')
plt.plot(df_recent.index, df_recent['MM_longue'], label=f'MM {mm_longue} heures', color='red')

# 3. Ajouter les titres et légendes
plt.title(f'Analyse XAUUSD ({symbol}) - {timeframe} - 200 dernières heures')
plt.xlabel('Date et Heure')
plt.ylabel('Prix (USD)')
plt.legend() # Affiche la légende (les labels de chaque ligne)
plt.grid(True) # Ajoute une grille de fond

# 4. Afficher le graphique
print("Affichage du graphique... Fermez la fenêtre du graphique pour terminer le script.")
plt.show()

print("\nScript terminé.")