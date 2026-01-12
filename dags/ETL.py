from preprocessing.jobs.cleaning import cleaning_pipeline
from preprocessing.jobs.selection import selection_pipeline


def main():
  cleaning_pipeline()
  selection_pipeline()
