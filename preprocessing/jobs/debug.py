import logging
import os

from cleaning import (
  calculate_age,
  load_datasets,
  merging_datasets_with_history,
  total_time_stay,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(BASE_DIR, "../configs/cleaning.yaml")


if __name__=="__main__":

  logging.info("\n\n[DEBUG]: Loading datasets...")



  df_active, df_deactive, df_history, df_finished, df_evaded = load_datasets(CONFIG_PATH)


  df_merged = merging_datasets_with_history(df_finished, df_evaded, df_active, df_history, 'RGA_Anon', 'right')

  df_merged = calculate_age(df_merged, 'Data ocorrência','Data Nascimento','Idade')
  df_merged = total_time_stay(df_merged, 'Data ocorrência', 'Ano Ingresso', 'Tempo_De_Permanencia')

  print(df_merged["Tempo_De_Permanencia"])
