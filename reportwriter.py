from pathlib import Path

from lib.savetext import save_text


class ReportWriter:
    # Define constructor with report output directory.
    def __init__(self, report_dir):
        # Store report directory.
        self.report_dir = Path(report_dir)

        # Create report directory.
        self.report_dir.mkdir(parents=True, exist_ok=True)

    # Create console information as text.
    def console_summary(self, results):
        # Store overview dictionary.
        overview = results["overview"]

        # Store runs-per-character table.
        runs_per_character = results["runs_per_character"]

        # Create beginning lines.
        lines = [
            "SLAY THE SPIRE RUN HISTORY SUMMARY",
            "-" * 70,
            f"Total runs: {overview['total_runs']}",
            f"Wins: {overview['wins']}",
            f"Losses: {overview['losses']}",
            f"Overall win rate: {overview['win_rate_percent']:.2f}%",
            f"Average run time: {overview['avg_run_time_minutes']:.2f} minutes",
            f"Average deck size: {overview['avg_deck_size']:.2f} cards",
            f"Average relic count: {overview['avg_relic_count']:.2f}",
            "",
            "Runs per character:",
        ]

        # Add one line for every character.
        for _, row in runs_per_character.iterrows():
            # Append character and run count.
            lines.append(f"- {row['character']}: {int(row['runs'])}")

        # Return text joined by newlines.
        return "\n".join(lines)

    # Create a full Markdown report with answers.
    def markdown_report(self, results):
        # Start the report lines.
        lines = [
            "# Slay the Spire Run History Analysis Report",
            "",
            "## Console information",
            "",
            "```text",
            self.console_summary(results),
            "```",
            "",
            "## Answers to research questions",
            "",
            "### Win rate of high pick-rate cards",
            "A scatter plot and a filtered bar chart are generated. The analysis filters to cards offered at least 10 times and appearing in at least 5 final decks.",
            "",
            results["high_pick_cards"].head(10).round(2).to_markdown(index=False),
            "",
            "### Potion use rate by character",
            "A grouped bar chart compares average potions used and average potions gained by character.",
            "",
            results["potion_use_by_character"].round(2).to_markdown(index=False),
            "",
            "### Top 5 most common cards in lost runs per character",
            "A grouped horizontal bar chart is generated.",
            "",
            results["lost_cards"].to_markdown(index=False),
            "",
            "### Top 5 most common cards in won runs per character",
            "A grouped horizontal bar chart is generated.",
            "",
            results["won_cards"].to_markdown(index=False),
            "",
            "### Duplicate-heavy decks performance",
            "A boxplot and category bar chart are generated to compare duplicate-heavy decks against win rate.",
            "",
            results["duplicate_performance"].round(2).to_markdown(index=False),
            "",
            "### Potions used vs potions found and effect on win rate",
            "A scatter plot compares potions found against potions used, and a bar chart compares potion-waste categories by win rate.",
            "",
            results["potion_waste_performance"].round(2).to_markdown(index=False),
            "",
            "### Total runs, win rate, average run time, average deck size, and runs per character",
            "These are printed as console information because a graph would be redundant for single summary values.",
            "",
            "### Turns by enemy type and act number",
            "A grouped bar chart and a boxplot are generated.",
            "",
            results["turns_by_type_act"].round(2).to_markdown(index=False),
            "",
            "### Win rate per character",
            "A bar chart is generated.",
            "",
            results["win_rate_per_character"].round(2).to_markdown(index=False),
            "",
            "### Runs over time/date",
            "A line chart is generated using the converted timestamp date.",
            "",
            "### Deck size effect on win rate",
            "A KDE plot shows the distribution of deck sizes by win/loss, and a binned bar chart shows win rate by deck-size category.",
            "",
            results["deck_size_performance"].round(2).to_markdown(index=False),
            "",
            "### Top 5 relics by win rate and comparison with/without relic",
            "A paired bar chart compares win rate for runs with each relic against runs without it.",
            "",
            results["top_relics"].round(2).to_markdown(index=False),
            "",
            "### Distribution of deaths per floor",
            "A histogram is generated from lost runs using the final floor column.",
            "",
            "### Amount of damage taken per floor",
            "A line chart is generated for average damage taken per floor, split by win/loss.",
            "",
            "### Top 10 most and least picked cards vs win rate per character",
            "A faceted Seaborn scatter plot is generated by character.",
            "",
            "### Do winning runs tend to be longer or shorter than losing runs?",
            "A KDE plot compares run-time distributions between won and lost runs.",
            "",
            "### Total damage taken distribution by win/loss",
            "A KDE plot compares total damage taken in won and lost runs.",
            "",
        ]

        # Return the Markdown report.
        return "\n".join(lines)

    # Save all report files.
    def save_reports(self, results):
        # Save console summary.
        save_text(self.report_dir / "console_summary.txt", self.console_summary(results))

        # Save Markdown report.
        save_text(self.report_dir / "analysis_report.md", self.markdown_report(results))