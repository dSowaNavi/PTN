from pathlib import Path
import pandas as pd

class DataLoader:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)

    def load_csv(self, filename):
        path = self.data_dir / filename
        return pd.read_csv(path)

    def load_all(self):
        return {
            "runs": self.load_csv("runs.csv"),
            "floors": self.load_csv("floors.csv"),
            "deck_cards": self.load_csv("deck_cards.csv"),
            "card_offers": self.load_csv("card_offers.csv"),
            "card_picks": self.load_csv("card_picks.csv"),
            "relics": self.load_csv("relics.csv"),
            "potions_used": self.load_csv("potions_used.csv"),
            "potions_gained": self.load_csv("potions_gained.csv"),
            "card_combined_stats": self.load_csv("card_combined_stats.csv"),
            "relic_win_rates": self.load_csv("relic_win_rates.csv"),
        }