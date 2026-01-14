import logging
import os
import time

import pandas as pd
import yaml
# from cleaning import load_config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(BASE_DIR, "../configs/cleaning.yaml")

def load_config(CONFIG_PATH) :
  """
  Selects the current dataset's config file we are interest in.
  """
  with open(CONFIG_PATH, "r") as f:
    full_config = yaml.safe_load(f)

  try:
    current_dataset = full_config["CURRENT_DATASET"]
    logging.info(f"\nloading current dataset: {current_dataset}")
    if current_dataset not in full_config['DATASETS']:
      raise ValueError(f"\nDataset {current_dataset} not found!")

    return full_config["DATASETS"][current_dataset]

  except Exception as e:
    logging.exception(f"There was an error handling the config cleaning.yaml file {e}")
    raise

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
  return df.drop_duplicates()


def drop_columns(df: pd.DataFrame) -> pd.DataFrame:
  try:
      df = df.drop(
        columns=[
                "CH",
                "Estrutura",
                "Núcleo de Disciplinas",
                "Situação atual",
                "Estrangeiro",
                "Situação",
                "Nacionalidade",
                "Período",
                "Ano",
                'Período ingresso'
        ])
  except KeyError as e:
    raise KeyError(f"[ERROR]: column did not exist or was null{e}")
  return df


def selection_pipeline():
    logging.basicConfig(level=logging.INFO)

    config = load_config(CONFIG_PATH)

    df = pd.read_csv(config["PREPROCESSED_DATASET"])
    logging.info("\n\n[INFO]: Starting to drop useless columns...")
    df = (df
      .pipe(drop_columns)
      .pipe(remove_duplicates)
    )
    print(df)
    df.to_csv(config["TRAINING_DATASET"], index=False)
    logging.info("\n\n[OK]: Final training dataset saved to Bucket...")

if __name__ == "__main__":
    start_time = time.time()
    selection_pipeline()
    total_time = time.time() - start_time
    print(f"Total time taken:{total_time:.2f}s\n")
