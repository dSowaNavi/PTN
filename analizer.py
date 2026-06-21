import pandas as pd
from lib.safedivide import safe_divide
from lib.safepercent import safe_percent

class Analyzer:

    def __init__(self, tables):

        self.tables = tables
        self.results = {}

    def prepare(self):
        runs = self.tables["runs"].copy()

        runs["win"] = runs["win"].astype(bool)
        runs["date"] = pd.to_datetime(runs["timestamp"], unit="s", errors="coerce").dt.date
        runs["duplicate_card_count"] = runs["deck_size"] - runs["unique_deck_cards"]
        runs["potions_wasted"] = (runs["total_potions_gained"] - runs["total_potions_used"]).clip(lower=0)
        runs["potion_use_ratio"] = runs.apply(lambda row: safe_divide(row["total_potions_used"], row["total_potions_gained"]), axis=1)
        runs["deck_size_category"] = pd.cut(runs["deck_size"], bins=[0, 20, 30, 40, 200], labels=["<=20", "21-30", "31-40", "40+"], include_lowest=True)
        runs["duplicate_category"] = pd.cut(runs["duplicate_card_count"], bins=[-1, 2, 5, 8, 200], labels=["0-2", "3-5", "6-8", "9+"], include_lowest=True)
        runs["potion_waste_category"] = pd.cut(runs["potions_wasted"], bins=[-1, 0, 2, 4, 200], labels=["0", "1-2", "3-4", "5+"], include_lowest=True)


        floors = self.tables["floors"].copy()
        floors["act_number"] = floors["floor"].apply(self.floor_to_act)
        floors = floors.merge(runs[["run_id", "win", "character"]], on="run_id", how="left")
        deck_cards = self.tables["deck_cards"].copy()
        deck_cards = deck_cards.merge(runs[["run_id", "win", "character"]], on="run_id", how="left")
        card_offers = self.tables["card_offers"].copy()
        card_offers = card_offers.merge(runs[["run_id", "win", "character"]], on="run_id", how="left")
        relics = self.tables["relics"].copy()
        relics = relics.merge(runs[["run_id", "win", "character"]], on="run_id", how="left")
        potions_used = self.tables["potions_used"].copy()
        potions_used = potions_used.merge(runs[["run_id", "win", "character"]], on="run_id", how="left")
        potions_gained = self.tables["potions_gained"].copy()

        # Join potion-gained rows with run result and character.
        potions_gained = potions_gained.merge(runs[["run_id", "win", "character"]], on="run_id", how="left")


        self.tables["runs"] = runs
        self.tables["floors"] = floors
        self.tables["deck_cards"] = deck_cards
        self.tables["card_offers"] = card_offers
        self.tables["relics"] = relics
        self.tables["potions_used"] = potions_used
        self.tables["potions_gained"] = potions_gained

    def floor_to_act(self, floor):
        # Return act 1 for floors up to 17.
        if floor <= 17:
            return 1

        # Return act 2 for floors 18 to 33.
        if floor <= 33:
            return 2

        # Return act 3 for later floors.
        return 3


    def run(self):
        runs = self.tables["runs"]
        floors = self.tables["floors"]
        deck_cards = self.tables["deck_cards"]
        card_offers = self.tables["card_offers"]
        relics = self.tables["relics"]
        card_combined = self.tables["card_combined_stats"].copy()
        relic_win_rates = self.tables["relic_win_rates"].copy()

        overview = {
            "total_runs": len(runs),
            "wins": int(runs["win"].sum()),
            "losses": int((~runs["win"]).sum()),
            "win_rate_percent": safe_percent(runs["win"].sum(), len(runs)),
            "avg_run_time_minutes": round(runs["run_time_minutes"].mean(), 2),
            "avg_deck_size": round(runs["deck_size"].mean(), 2),
            "avg_relic_count": round(runs["relic_count"].mean(), 2),
        }

        runs_per_character = runs.groupby("character").agg(runs=("run_id", "count")).reset_index().sort_values("runs", ascending=False)

        win_rate_per_character = runs.groupby("character").agg(runs=("run_id", "count"), wins=("win", "sum")).reset_index()

        win_rate_per_character["losses"] = win_rate_per_character["runs"] - win_rate_per_character["wins"]

        win_rate_per_character["win_rate_percent"] = win_rate_per_character.apply(lambda row: safe_percent(row["wins"], row["runs"]), axis=1)

        potion_use_by_character = runs.groupby("character").agg(runs=("run_id", "count"), avg_potions_used=("total_potions_used", "mean"), avg_potions_gained=("total_potions_gained", "mean"), avg_potion_use_ratio=("potion_use_ratio", "mean")).reset_index()
        potion_use_by_character["avg_potion_use_percent"] = potion_use_by_character["avg_potion_use_ratio"] * 100

        # Top cards used in won and lost runs.
        lost_cards = self.top_cards_by_character(deck_cards, False)
        won_cards = self.top_cards_by_character(deck_cards, True)

        duplicate_performance = runs.groupby("duplicate_category", observed=False).agg(runs=("run_id", "count"), wins=("win", "sum"), avg_deck_size=("deck_size", "mean"), avg_duplicates=("duplicate_card_count", "mean")).reset_index()
        duplicate_performance["win_rate_percent"] = duplicate_performance.apply(lambda row: safe_percent(row["wins"], row["runs"]), axis=1)


        potion_waste_performance = runs.groupby("potion_waste_category", observed=False).agg(runs=("run_id", "count"), wins=("win", "sum"), avg_potions_used=("total_potions_used", "mean"), avg_potions_gained=("total_potions_gained", "mean"), avg_potions_wasted=("potions_wasted", "mean")).reset_index()
        potion_waste_performance["win_rate_percent"] = potion_waste_performance.apply(lambda row: safe_percent(row["wins"], row["runs"]), axis=1)

        # save floors with only monsters, elite or bosses then count turns per type
        combat_floors = floors[floors["floor_type"].isin(["monster", "elite", "boss"])].copy()
        turns_by_type_act = combat_floors.groupby(["act_number", "floor_type"]).agg(avg_turns=("turns", "mean"), floor_count=("floor", "count")).reset_index()

        runs_over_time = runs.groupby("date").agg(runs=("run_id", "count"), wins=("win", "sum")).reset_index()
        runs_over_time["win_rate_percent"] = runs_over_time.apply(lambda row: safe_percent(row["wins"], row["runs"]), axis=1)

        deck_size_performance = runs.groupby("deck_size_category", observed=False).agg(runs=("run_id", "count"), wins=("win", "sum"), avg_deck_size=("deck_size", "mean")).reset_index()
        deck_size_performance["win_rate_percent"] = deck_size_performance.apply(lambda row: safe_percent(row["wins"], row["runs"]), axis=1)

        high_pick_cards = card_combined[(card_combined["offered"] >= 10) & (card_combined["total_runs_with_card"] >= 5)].copy()
        high_pick_cards = high_pick_cards.sort_values("pick_rate_percent", ascending=False)

        top_relics = relic_win_rates[relic_win_rates["total_runs_with_relic"] >= 5].copy()
        top_relics = top_relics.sort_values("win_rate_percent", ascending=False).head(5)
        relic_comparison = self.compare_relics(top_relics, relics, runs)

        lost_runs = runs[runs["win"] == False].copy()

        damage_per_floor = floors.groupby("floor").agg(avg_damage_taken=("damage_taken", "mean"), total_damage_taken=("damage_taken", "sum")).reset_index()

        card_character_stats = self.card_stats_by_character(card_offers, deck_cards)

        self.results = {
            "overview": overview,
            "runs": runs,
            "floors": floors,
            "combat_floors": combat_floors,
            "deck_cards": deck_cards,
            "card_offers": card_offers,
            "relics": relics,
            "runs_per_character": runs_per_character,
            "win_rate_per_character": win_rate_per_character,
            "potion_use_by_character": potion_use_by_character,
            "lost_cards": lost_cards,
            "won_cards": won_cards,
            "duplicate_performance": duplicate_performance,
            "potion_waste_performance": potion_waste_performance,
            "turns_by_type_act": turns_by_type_act,
            "runs_over_time": runs_over_time,
            "deck_size_performance": deck_size_performance,
            "high_pick_cards": high_pick_cards,
            "top_relics": top_relics,
            "relic_comparison": relic_comparison,
            "deaths_per_floor": lost_runs,
            "damage_per_floor": damage_per_floor,
            "card_character_stats": card_character_stats,
        }

        return self.results

    # Fetch top 5 most common cards per character in either lost or won run
    def top_cards_by_character(self, deck_cards, win_value):
        filtered = deck_cards[deck_cards["win"] == win_value].copy()
        counts = filtered.groupby(["character", "card_name"]).agg(count=("card_name", "count")).reset_index()
        top = counts.sort_values(["character", "count"], ascending=[True, False]).groupby("character").head(5).reset_index(drop=True)
        top["character_card"] = top["character"] + " — " + top["card_name"]
        return top

    # Compare win rates for runs with and without selected relics.
    def compare_relics(self, top_relics, relics, runs):
        rows = []

        for _, relic_row in top_relics.iterrows():
            relic_id = relic_row["relic_id"]
            relic_name = relic_row["relic_name"]
            run_ids_with_relic = set(relics.loc[relics["relic_id"] == relic_id, "run_id"])

            temp = runs.copy()
            temp["group"] = temp["run_id"].apply(lambda run_id: "With relic" if run_id in run_ids_with_relic else "Without relic")
            grouped = temp.groupby("group").agg(runs=("run_id", "count"), wins=("win", "sum")).reset_index()

            for _, row in grouped.iterrows():
                rows.append({"relic_name": relic_name, "group": row["group"], "runs": row["runs"], "wins": row["wins"], "win_rate_percent": safe_percent(row["wins"], row["runs"])})

        return pd.DataFrame(rows)

    def card_stats_by_character(self, card_offers, deck_cards):
        pick_stats = card_offers.groupby(["character", "card_id", "card_name"]).agg(offered=("card_id", "count"), picked=("picked", "sum")).reset_index()
        pick_stats["pick_rate_percent"] = pick_stats.apply(lambda row: safe_percent(row["picked"], row["offered"]), axis=1)
        unique_card_runs = deck_cards[["run_id", "character", "card_id", "card_name", "win"]].drop_duplicates()
        win_stats = unique_card_runs.groupby(["character", "card_id", "card_name"]).agg(total_runs_with_card=("run_id", "count"), wins=("win", "sum")).reset_index()
        win_stats["win_rate_percent"] = win_stats.apply(lambda row: safe_percent(row["wins"], row["total_runs_with_card"]), axis=1)
        combined = pick_stats.merge(win_stats, on=["character", "card_id", "card_name"], how="outer").fillna(0)

        selected = []

        for character, group in combined.groupby("character"):
            reliable = group[group["offered"] >= 5].copy()

            if reliable.empty:
                continue

            most = reliable.sort_values("picked", ascending=False).head(10).copy()
            most["pick_group"] = "Most picked"

            least = reliable.sort_values("picked", ascending=False).tail(10).copy()
            least["pick_group"] = "Least picked"

            selected.append(most)
            selected.append(least)

        if selected:
            return pd.concat(selected, ignore_index=True)

        return combined.head(0)