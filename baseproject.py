from abc import ABC, abstractmethod
from pathlib import Path

class BaseProject(ABC):
    def __init__(self, data_dir, chart_dir, report_dir, processed_dir):
        self.data_dir = Path(data_dir)
        self.chart_dir = Path(chart_dir)
        self.report_dir = Path(report_dir)
        self.processed_dir = Path(processed_dir)

    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def prepare_data(self):
        pass

    @abstractmethod
    def analyze(self):
        pass

    @abstractmethod
    def generate_charts(self):
        pass

    @abstractmethod
    def generate_reports(self):
        pass