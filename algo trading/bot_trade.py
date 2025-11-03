import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import time # On importe 'time' pour les petites pauses

# --- 1. PARAMÈTRES GLOBAUX DU BOT ---
# Symbol sur lequel on trade
TRADE_SYMBOL = "XAUUSD"
# Volume du trade (0.01 = 1 micro-lot, la plus petite taille)
TRADE_VOLUME = 0.01 
# Un "nombre magique" pour que le bot reconnaisse ses propres trades
MAGIC_NUMBER = 12345 
# Stratégie
MM_COURTE = 20
MM_LONGUE = 50

# --- 2. FONCTION POUR ENVOYER UN ORDRE (LA NOUVELLE PARTIE) ---
def passer_ordre(symbol, volume, type_ordre, magic_number):
    """
    Fonction pour ouvrir un trade (Achat ou Vente)
    type_ordre doit être mt5.ORDER_TYPE_BUY ou mt5.ORDER_TYPE_SELL
    """
    
    if type_ordre == mt5.ORDER_TYPE_BUY:
        price = mt5.symbol_info_tick(symbol).ask 
        stop_loss = price - 2.5  # Exemple: SL 2.5$ en dessous du prix d'achat
        take_profit = price + 5.0 # Exemple: TP 5.0$ au-dessus du prix d'achat
    else:
        price = mt5.symbol_info_tick(symbol).bid
        stop_loss = price + 2.5  # SL 2.5$ au-dessus du prix de vente
        take_profit = price - 5.0 # TP 5.0$ en dessous du prix de vente

    # 2. Préparer le dictionnaire de la requête
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": type_ordre,
        "price": price,
        "sl": stop_loss,       # ### NOUVELLE LIGNE ###
        "tp": take_profit,     # ### NOUVELLE LIGNE ###
        "deviation": 10,
        "magic": magic_number,
        "comment": "Bot avec SL/TP",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # 3. Envoyer l'ordre
    print(f"--- Envoi de l'ordre {type_ordre} pour {symbol} ---")
    result = mt5.order_send(request)
    
    # 4. Vérifier le résultat
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Échec de l'envoi de l'ordre, retcode={result.retcode}")
        # Afficher l'erreur
        print("   > Raison:", result.comment)
    else:
        print(f"✅ Ordre envoyé avec succès ! Ticket: {result.order}")
        
    return result

# --- 3. LOGIQUE PRINCIPALE DU SCRIPT ---

# Connexion à MT5
print("Lancement du bot...")
if not mt5.initialize():
    print("initialize() a échoué, erreur =", mt5.last_error())
    quit()
print("Connecté à MetaTrader 5!")

# Récupérer les données
timeframe = mt5.TIMEFRAME_H1
rates = mt5.copy_rates_from_pos(TRADE_SYMBOL, timeframe, 0, 1000)

if rates is None:
    print(f"N'a pas pu récupérer les données pour {TRADE_SYMBOL}")
    mt5.shutdown()
    quit()

# Calcul avec Pandas
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
df['MM_courte'] = df['close'].rolling(window=MM_COURTE).mean()
df['MM_longue'] = df['close'].rolling(window=MM_LONGUE).mean()

print(f"Données pour {TRADE_SYMBOL} analysées.")

# --- 4. LA LOGIQUE DE DÉCISION ---
# On prend la dernière bougie COMPLÈTE (iloc[-2])
# iloc[-1] est la bougie en cours, pas encore fiable
try:
    derniere_bougie = df.iloc[-2]
    
    print(f"Analyse de la bougie de : {derniere_bougie['time']}")
    print(f"  MM Courte: {derniere_bougie['MM_courte']:.2f}")
    print(f"  MM Longue: {derniere_bougie['MM_longue']:.2f}")

    # Définir le signal
    signal = "NEUTRE"
    if derniere_bougie['MM_courte'] > derniere_bougie['MM_longue']:
        signal = "ACHAT"
    elif derniere_bougie['MM_courte'] < derniere_bougie['MM_longue']:
        signal = "VENTE"

    print(f"==> Signal actuel: {signal}")

    # --- 5. EXÉCUTION DE L'ORDRE ---
    # Pour ce premier bot, on n'ouvre qu'UN SEUL trade à la fois.
    # On vérifie donc s'il y a déjà des positions ouvertes par CE bot
    
    positions = mt5.positions_get(symbol=TRADE_SYMBOL)
    
    # Filtrer les positions pour ne garder que celles de notre bot
    positions_bot = [p for p in positions if p.magic == MAGIC_NUMBER]

    if len(positions_bot) == 0:
        # Pas de trade ouvert par notre bot, on peut trader !
        if signal == "ACHAT":
            print("Aucune position. Signal d'ACHAT détecté. Ouverture d'un trade.")
            passer_ordre(TRADE_SYMBOL, TRADE_VOLUME, mt5.ORDER_TYPE_BUY, MAGIC_NUMBER)
            
        elif signal == "VENTE":
            print("Aucune position. Signal de VENTE détecté. Ouverture d'un trade.")
            passer_ordre(TRADE_SYMBOL, TRADE_VOLUME, mt5.ORDER_TYPE_SELL, MAGIC_NUMBER)
        else:
            print("Aucune position. Signal NEUTRE. On ne fait rien.")
            
    else:
        # Il y a déjà un trade ouvert par notre bot
        print(f"Un trade (Ticket {positions_bot[0].ticket}) est déjà ouvert. On ne fait rien.")
        print("Le bot doit d'abord apprendre à fermer les trades (prochaine étape !).")


except IndexError:
    print("Pas assez de données pour le calcul.")

# --- 6. DÉCONNEXION ---
print("Script terminé.")
mt5.shutdown()