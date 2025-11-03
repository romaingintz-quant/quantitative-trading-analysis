import dukascopy_python as dkp
from datetime import datetime
import pandas as pd # On importe Pandas pour assembler les fichiers

# --- Paramètres du téléchargement ---
SYMBOL = 'XAU/USD'
TIMEFRAME = dkp.INTERVAL_HOUR_1   # H1 (1 heure)
NOM_FICHIER_CSV = "XAUUSD-H1-2014-2024.csv" # Le fichier final

# Années qu'on veut télécharger
ANNEES_A_TELECHARGER = range(2014, 2025) # de 2014 à 2024 (inclus)

# On va stocker tous les morceaux de DataFrame ici
tous_les_dataframes = []

print(f"Lancement du téléchargement pour {SYMBOL} de {ANNEES_A_TELECHARGER[0]} à {ANNEES_A_TELECHARGER[-1]}...")
print("Cela peut prendre 10-15 minutes, soyez patient.\n")

try:
    # --- La Boucle Année par Année ---
    for annee in ANNEES_A_TELECHARGER:
        # Définir les dates de début et de fin pour cette année
        date_debut = datetime(annee, 1, 1) # 1er Janvier
        date_fin = datetime(annee, 12, 31) # 31 Décembre
        
        print(f"Téléchargement de l'année {annee}...")
        
        df_annee = dkp.fetch(
            SYMBOL,
            TIMEFRAME,
            dkp.OFFER_SIDE_BID,
            date_debut,
            date_fin
        )
        
        if df_annee is not None and not df_annee.empty:
            print(f" -> Année {annee} OK ({len(df_annee)} lignes).")
            tous_les_dataframes.append(df_annee)
        else:
            print(f" -> Aucune donnée pour l'année {annee}.")
    
    # --- Assemblage Final ---
    if not tous_les_dataframes:
        print("\n❌ Aucun DataFrame à assembler. Téléchargement échoué.")
        quit()
        
    print("\nAssemblage de toutes les années...")
    # Concatène tous les DataFrames en un seul
    df_complet = pd.concat(tous_les_dataframes)
    
    # On trie l'index (date) pour être sûr qu'il est en ordre chronologique
    df_complet.sort_index(inplace=True)
    
    # On enlève les doublons (au cas où les téléchargements se chevauchent)
    df_complet = df_complet[~df_complet.index.duplicated(keep='first')]

    # 2. Sauvegarder le fichier CSV final
    print(f"Sauvegarde dans le fichier : {NOM_FICHIER_CSV}...")
    df_complet.to_csv(NOM_FICHIER_CSV, index_label="Time")
    
    print("\n✅ Téléchargement des 10 ans terminé !")
    print(f"Total des bougies H1 récupérées : {len(df_complet)}")
    print("Vous pouvez maintenant lancer vos scripts de backtest.")

except Exception as e:
    print(f"\n❌ Une erreur est survenue pendant le téléchargement :")
    print(e)