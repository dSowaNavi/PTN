from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class Visualizer:
    def __init__(self, chart_dir):
        self.chart_dir = Path(chart_dir)
        self.chart_dir.mkdir(parents=True, exist_ok=True)
        sns.set_theme(style="whitegrid")


    def save(self, filename):
        plt.tight_layout()
        plt.savefig(self.chart_dir / filename, dpi=150)
        plt.close()
        print(f"Saved chart: {filename}")


    def generate_all(self, results):
        #
        self.high_pick_cards_scatter(results)
        self.high_pick_cards_bar(results)
        self.potion_use_by_character(results)
        self.top_cards(results["lost_cards"], "Top 5 most common cards in lost runs per character", "04_lost_cards_per_character.png")
        self.top_cards(results["won_cards"], "Top 5 most common cards in won runs per character", "05_won_cards_per_character.png")
        self.duplicate_boxplot(results)
        self.duplicate_category_bar(results)
        self.potions_used_vs_found(results)
        self.potion_waste_bar(results)
        self.runs_per_character(results)
        self.turns_bar(results)
        self.turns_boxplot(results)
        self.win_rate_per_character(results)
        self.runs_over_time(results)
        self.deck_size_kde(results)
        self.deck_size_bar(results)
        self.relic_comparison(results)
        self.deaths_per_floor(results)
        self.damage_per_floor(results)
        self.card_pick_vs_win_per_character(results)
        self.run_time_kde(results)
        self.total_damage_kde(results)
        self.card_pickrate_winrate_heatmap(results)

    def high_pick_cards_scatter(self, results):

        df = results["high_pick_cards"].copy()
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df, x="pick_rate_percent", y="win_rate_percent", size="total_runs_with_card", alpha=0.7)
        plt.title("Win rate of high-pick-rate cards")
        plt.xlabel("Pick rate [%]")
        plt.ylabel("Win rate [%]")
        self.save("01_high_pick_cards_scatter.png")


    def high_pick_cards_bar(self, results):
        # Select top ten cards by pick rate.
        df = results["high_pick_cards"].head(10).sort_values("pick_rate_percent", ascending=True)
        plt.figure(figsize=(12, 7))
        sns.barplot(data=df, x="pick_rate_percent", y="card_name", color="steelblue")
        plt.title("Top high-pick-rate cards")
        plt.xlabel("Pick rate [%]")
        plt.ylabel("Card")
        self.save("02_high_pick_cards_bar.png")


    def potion_use_by_character(self, results):
        df = results["potion_use_by_character"].copy()
        long_df = df.melt(id_vars="character", value_vars=["avg_potions_used", "avg_potions_gained"], var_name="metric", value_name="average")
        plt.figure(figsize=(10, 6))
        sns.barplot(data=long_df, x="character", y="average", hue="metric")
        plt.title("Potion use rate by character")
        plt.xlabel("Character")
        plt.ylabel("Average potions per run")
        plt.xticks(rotation=30)
        self.save("03_potion_use_by_character.png")


    def top_cards(self, df, title, filename):

        df = df.sort_values(["character", "count"], ascending=[True, True])
        plt.figure(figsize=(13, 10))
        sns.barplot(data=df, x="count", y="character_card", hue="character")
        plt.title(title)
        plt.xlabel("Card count")
        plt.ylabel("Character — card")
        self.save(filename)


    def duplicate_boxplot(self, results):
        df = results["runs"].copy()
        plt.figure(figsize=(8, 6))
        sns.boxplot(data=df, x="win", y="duplicate_card_count")
        plt.title("Duplicate-heavy decks: wins vs losses")
        plt.xlabel("Won run")
        plt.ylabel("Duplicate card count")
        self.save("06_duplicate_heavy_boxplot.png")

    # Plot win rate by duplicate-card category.
    def duplicate_category_bar(self, results):
        df = results["duplicate_performance"].copy()
        plt.figure(figsize=(8, 6))
        sns.barplot(data=df, x="duplicate_category", y="win_rate_percent", color="steelblue")

        plt.title("Win rate by duplicate-card category")
        plt.xlabel("Duplicate card category")
        plt.ylabel("Win rate [%]")

        self.save("07_duplicate_category_winrate.png")

    # Plot potions used versus potions found.
    def potions_used_vs_found(self, results):
        df = results["runs"].copy()
        plt.figure(figsize=(9, 6))
        sns.scatterplot(data=df, x="total_potions_gained", y="total_potions_used", hue="win", alpha=0.8)
        plt.title("Potions used vs potions found")
        plt.xlabel("Potions found")
        plt.ylabel("Potions used")

        self.save("08_potions_used_vs_found.png")

    # Plot potion-waste category by win rate.
    def potion_waste_bar(self, results):
        df = results["potion_waste_performance"].copy()
        plt.figure(figsize=(8, 6))
        sns.barplot(data=df, x="potion_waste_category", y="win_rate_percent", color="steelblue")
        plt.title("Potion waste and win rate")
        plt.xlabel("Unused potions")
        plt.ylabel("Win rate [%]")

        self.save("09_potion_waste_winrate.png")

    # Plot runs per character.
    def runs_per_character(self, results):
        df = results["runs_per_character"].copy()
        plt.figure(figsize=(9, 6))
        sns.barplot(data=df, x="character", y="runs", color="steelblue")
        plt.title("Runs per character")
        plt.xlabel("Character")
        plt.ylabel("Runs")
        plt.xticks(rotation=30)

        self.save("10_runs_per_character.png")

    # Plot average turns by floor type and act.
    def turns_bar(self, results):
        df = results["turns_by_type_act"].copy()
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df, x="act_number", y="avg_turns", hue="floor_type")
        plt.title("Average turns by enemy type and act")
        plt.xlabel("Act")
        plt.ylabel("Average turns")

        # Save chart.
        self.save("11_turns_by_type_act_bar.png")

    # Plot turn distribution by floor type and act.
    def turns_boxplot(self, results):
        df = results["combat_floors"].copy()
        plt.figure(figsize=(10, 6))
        sns.boxplot(data=df, x="act_number", y="turns", hue="floor_type")
        plt.title("Turn distribution by enemy type and act")
        plt.xlabel("Act")
        plt.ylabel("Turns")

        self.save("12_turns_by_type_act_boxplot.png")

    # Plot win rate per character.
    def win_rate_per_character(self, results):
        df = results["win_rate_per_character"].sort_values("win_rate_percent", ascending=False)
        plt.figure(figsize=(9, 6))
        sns.barplot(data=df, x="character", y="win_rate_percent", color="steelblue")
        plt.title("Win rate per character")
        plt.xlabel("Character")
        plt.ylabel("Win rate [%]")
        plt.xticks(rotation=30)

        self.save("13_win_rate_per_character.png")

    # Plot runs over time.
    def runs_over_time(self, results):
        df = results["runs_over_time"].copy()
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df, x="date", y="runs", marker="o")
        plt.title("Runs over time")
        plt.xlabel("Date")
        plt.ylabel("Number of runs")
        plt.xticks(rotation=45)
        self.save("14_runs_over_time.png")

    # Plot deck-size KDE by win/loss.
    def deck_size_kde(self, results):
        df = results["runs"].copy()
        plt.figure(figsize=(10, 6))
        sns.kdeplot(data=df, x="deck_size", hue="win", common_norm=False)
        plt.title("Deck size distribution by win/loss")
        plt.xlabel("Deck size")
        plt.ylabel("Density")

        self.save("15_deck_size_kde.png")


    def deck_size_bar(self, results):
        df = results["deck_size_performance"].copy()
        plt.figure(figsize=(8, 6))
        sns.barplot(data=df, x="deck_size_category", y="win_rate_percent", color="steelblue")
        plt.title("Deck size category and win rate")
        plt.xlabel("Deck size category")
        plt.ylabel("Win rate [%]")

        self.save("16_deck_size_winrate.png")

    # Plot relic win rate with and without each top relic.
    def relic_comparison(self, results):
        df = results["relic_comparison"].copy()
        plt.figure(figsize=(12, 6))
        plt.title("Top 5 relics: win rate with relic vs without relic")
        plt.xlabel("Relic")
        plt.ylabel("Win rate [%]")
        plt.xticks(rotation=35, ha="right")

        self.save("17_top_relics_with_without.png")

    # Plot distribution of deaths per floor.
    def deaths_per_floor(self, results):
        df = results["deaths_per_floor"].copy()
        plt.figure(figsize=(10, 6))
        sns.histplot(data=df, x="final_floor", bins=20, color="steelblue")
        plt.title("Distribution of deaths per floor")
        plt.xlabel("Final floor")
        plt.ylabel("Lost runs")

        self.save("18_deaths_per_floor.png")

    # Plot average damage taken per floor.
    def damage_per_floor(self, results):
        df = results["floors"].copy()
        plt.figure(figsize=(12, 6))
        # Draw line chart with win/loss split.
        sns.lineplot(data=df, x="floor", y="damage_taken", hue="win", estimator="mean", errorbar=None)
        plt.title("Average damage taken per floor")
        plt.xlabel("Floor")
        plt.ylabel("Average damage taken")

        self.save("19_damage_per_floor.png")

    def card_pickrate_winrate_heatmap(self, results):
        df = results["card_character_stats"].copy()
        df = df[(df["offered"] >= 5) & (df["total_runs_with_card"] >= 3)].copy()
        if df.empty:
            print("Not enough card data to generate heatmap.")
            return

        df["pick_rate_bin"] = pd.cut(
            df["pick_rate_percent"],
            bins=[0, 20, 40, 60, 80, 100],
            labels=["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"],
            include_lowest=True
        )

        df["win_rate_bin"] = pd.cut(
            df["win_rate_percent"],
            bins=[0, 20, 40, 60, 80, 100],
            labels=["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"],
            include_lowest=True
        )

        # Loop through each character separately.
        for character in df["character"].unique():
            character_df = df[df["character"] == character].copy()
            heatmap_data = character_df.pivot_table(
                index="win_rate_bin",
                columns="pick_rate_bin",
                values="card_name",
                aggfunc="count",
                fill_value=0,
                observed=False
            )

            plt.figure(figsize=(8, 6))

            sns.heatmap(
                heatmap_data,
                annot=True,
                fmt="",
                cmap="Blues",
                linewidths=0.5
            )

            plt.title(f"Card pick rate vs win rate heatmap — {character}")

            plt.xlabel("Pick rate")

            plt.ylabel("Win rate")

            self.save(f"23_card_pickrate_winrate_heatmap_{character}.png")

    # Plot card pick rate against win rate per character.
    def card_pick_vs_win_per_character(self, results):
        df = results["card_character_stats"].copy()
        df = df[(df["offered"] >= 5) & (df["total_runs_with_card"] >= 3)].copy()
        if df.empty:
            return

        grid = sns.relplot(data=df, x="pick_rate_percent", y="win_rate_percent", hue="pick_group", col="character", col_wrap=2, kind="scatter", height=4, aspect=1.2, alpha=0.8)

        grid.fig.suptitle("Top 10 most and least picked cards vs win rate per character", y=1.03)

        grid.savefig(self.chart_dir / "20_card_pick_vs_win_per_character.png", dpi=150, bbox_inches="tight")

        plt.close(grid.fig)

        print("Saved chart: 20_card_pick_vs_win_per_character.png")

    # Plot run time distribution by win/loss.
    def run_time_kde(self, results):
        df = results["runs"].copy()
        plt.figure(figsize=(10, 6))
        sns.kdeplot(data=df, x="run_time_minutes", hue="win", common_norm=False)
        plt.title("Run time distribution by win/loss")
        plt.xlabel("Run time [minutes]")
        plt.ylabel("Density")

        self.save("21_run_time_kde.png")

    # Plot total damage taken distribution by win/loss.
    def total_damage_kde(self, results):
        df = results["runs"].copy()
        plt.figure(figsize=(10, 6))
        sns.kdeplot(data=df, x="total_damage_taken", hue="win", common_norm=False)
        plt.title("Total damage taken distribution by win/loss")
        plt.xlabel("Total damage taken")
        plt.ylabel("Density")

        self.save("22_total_damage_kde.png")