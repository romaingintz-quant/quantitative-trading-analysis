# Fichier : utils/download_data.py

import dukascopy_python as dkp
from datetime import datetime
import pandas as pd
import os

# --- Mes Paramètres ---
SYMBOL = 'XAU/USD'
TIMEFRAME = dkp.INTERVAL_HOUR_1   # H1
NOM_FICHIER_CSV = os.path.join("data", "XAUUSD-H1-2014-2024.csv") # Sauvegarder dans le dossier data

# Années à récupérer : 2014 à 2024
ANNEES_A_TELECHARGER = range(2014, 2025) 

# Liste pour stocker les morceaux de données
tous_les_dataframes = []

print(f"Lancement du téléchargement pour {SYMBOL}...")
print("Ça peut prendre 10-15 minutes.\n")

try:
    # Boucle année par année, c'est plus stable
    for annee in ANNEES_A_TELECHARGER:
        date_debut = datetime(annee, 1, 1)
        date_fin = datetime(annee, 12, 31)
        
        print(f"Téléchargement de l'année {annee}...")
        
        # Récupérer les données de l'année
        df_annee = dkp.fetch(
            SYMBOL,
            TIMEFRAME,
            dkp.OFFER_SIDE_BID, # Prix BID, ok pour le backtest
            date_debut,
            date_fin
        )
        
        if df_annee is not None and not df_annee.empty:
            print(f" -> Année {annee} OK ({len(df_annee)} lignes).")
            tous_les_dataframes.append(df_annee)
        else:
            print(f" -> Aucune donnée pour l'année {annee}.")
    
    # --- Assemblage ---
    if not tous_les_dataframes:
        print("\nERREUR: Aucun DataFrame à assembler.")
        quit()
        
    print("\nAssemblage de toutes les années...")
    df_complet = pd.concat(tous_les_dataframes)
    
    # Trier par date et enlever les doublons
    df_complet.sort_index(inplace=True)
    df_complet = df_complet[~df_complet.index.duplicated(keep='first')]

    # Sauvegarder le CSV final
    print(f"Sauvegarde dans le fichier : {NOM_FICHIER_CSV}...")
    df_complet.to_csv(NOM_FICHIER_CSV, index_label="Time")
    
    print(f"\n✅ Téléchargement terminé ! (Total: {len(df_complet)} lignes)")

except Exception as e:
    print(f"\n❌ Une erreur est survenue : {e}")