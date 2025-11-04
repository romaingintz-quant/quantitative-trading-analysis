# Fichier : strategies/strat_ma_crossover.py

import pandas_ta as ta
from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd # ### AJOUTE CET IMPORT ###

class StratMACrossover(Strategy):
    # Mes paramètres
    periode_courte = 50
    periode_longue = 200

    def init(self):
        # ### LA CORRECTION EST ICI ###
        
        # 1. Convertir l'objet "Array" en "pandas Series"
        # C'est pour que pandas-ta puisse le lire
        close_series = pd.Series(self.data.Close)
        
        # 2. Calculer les indicateurs en utilisant cette Series
        self.ema_courte = self.I(ta.ema, close_series, self.periode_courte)
        self.ema_longue = self.I(ta.ema, close_series, self.periode_longue)


    def next(self):
        
        # Le reste du code est parfait
        signal_achat = crossover(self.ema_courte, self.ema_longue)
        signal_vente = crossover(self.ema_longue, self.ema_courte)

        # Logique de trade
        if not self.position:
            if signal_achat:
                self.buy()
        
        elif self.position.is_long:
            if signal_vente:
                self.position.close()