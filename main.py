
from lib.ensuredirectories import ensure_directories
from projectmanager import ProjectManager


def main():
    ensure_directories(["data/raw", "data/processed", "outputs/charts", "outputs/reports"])
    project = ProjectManager()

    project.load_data()
    project.prepare_data()
    project.analyze()
    project.save_processed_tables()
    project.generate_charts()
    project.generate_reports()

    # Print a blank line.
    print()

    project.print_summary()

    print("Charts saved in: outputs/charts/")
    print("Reports saved in: outputs/reports/")

if __name__ == "__main__":
    main()
