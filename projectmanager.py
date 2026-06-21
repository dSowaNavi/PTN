import pandas as pd
from analizer import Analyzer
from baseproject import BaseProject
from dataloader import DataLoader
from reportwriter import ReportWriter
from visualizer import Visualizer

class ProjectManager(BaseProject):
    def __init__(self, data_dir="data/raw", chart_dir="outputs/charts", report_dir="outputs/reports", processed_dir="data/processed"):

        super().__init__(data_dir, chart_dir, report_dir, processed_dir)
        self.loader = DataLoader(self.data_dir)
        self.analyzer = None

        self.visualizer = Visualizer(self.chart_dir)
        self.report_writer = ReportWriter(self.report_dir)
        self.tables = None
        self.results = None


    def load_data(self):
        self.tables = self.loader.load_all()
        self.analyzer = Analyzer(self.tables)

    def prepare_data(self):
        self.analyzer.prepare()

    def analyze(self):
        self.results = self.analyzer.run()

    def generate_charts(self):
        self.visualizer.generate_all(self.results)


    def generate_reports(self):
        self.report_writer.save_reports(self.results)


    def save_processed_tables(self):
        self.processed_dir.mkdir(parents=True, exist_ok=True)


        for name, value in self.results.items():
            if isinstance(value, pd.DataFrame):
                value.to_csv(self.processed_dir / f"{name}.csv", index=False)


    def print_summary(self):
        print(self.report_writer.console_summary(self.results))