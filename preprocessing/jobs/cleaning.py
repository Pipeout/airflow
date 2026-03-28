import logging
import os
import re
import time
import unicodedata
from datetime import date
from typing import Any, Callable
from pathlib import Path

import numpy as np
import pandas as pd
import yaml






def mapping_disciplines_names(df: pd.DataFrame, column: str, new_column: str, curso: str) -> pd.DataFrame:
    """
    Still unsure of the usefulness of this function
    """
    if curso == 'CC':
      regex_mapping = {
             r".*calculo.*|.*Cálculo.*|.*Calculo.*|.*geometria analítica.*"
             r"|.*VGA.*|.*Vetores e Geometria Analítica.*|.*Geometria Analítica.*"
             r"|.*álgebra linear.*|.*Álgebra Linear.*|.*Matemática.*|.*Geometria Analítica.*"
             r"|.*Vetorial.*|.*Estatística.*": "Núcleo_de_Matemática",

             r".*programação.*|.*Programação.*|.*Redes.*|.*Software.*|.*Compiladores.*"
             r"|.*Laboratório.*|.*Dados.*|.*Sistemas.*|.*Computação.*"
             r"|.*Gráfica.*|.*Computadores.*|.*Inteligência Artificial.*|.*Microcontroladores.*"
             r"|.*Projeto.*|.*Processamento.*|.*Autômatos.*|.*Eletrônica Básica.*": "Núcleo_de_Computação",

            r".*Trabalho de Curso.*": "Núcleo_Trabalho_de_Curso",

             r".*Eletromagnetismo.*|.*Mecânica.*": "Núcleo_de_Física",

             r".*metodolodia.*|.*filosofia.*|.*Práticas de Leitura e Produção de Texto.*"
             r"|.*Empreendedorismo.*|.*Libras.*|.*Inglês Instrumental.*|.*Informática Aplicada à Educação.*": "Núcleo_de_Humanidades",

             r".*Lógica Digital.*|.*Arquitetura de Computadores.*"
             r"|.*Organização de Computadores.*": "Núcleo_de_Hardware"
         }
    else:
      regex_mapping = {}
    try:
      df[new_column] = df[column].apply(normalize_names)
      def apply_regex(name):
        if not isinstance(name, str):
            return name
        for pattern, correct_name in regex_mapping.items():
            if re.search(pattern, name, re.IGNORECASE):
                return correct_name
        return name
      if column in df.columns:
        df[new_column] = df[column].apply(apply_regex)
        return df
      raise KeyError(f"Column {column} does not exist")
    except KeyError as e:
      print(f"Column {e} does not exist in dataset.")
    except RuntimeError as e:
      print(f"Can't fill data{e}")


# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# CONFIG_PATH = os.path.join(BASE_DIR, "../configs/cleaning.yaml")


def get_config_file(): 
    try:
        base_dir = Path(__file__).resolve().parent.parent
        path = base_dir / "configs" / "cleaning.yaml"
        return path
    except NameError: # if it is a jupyter file 
        return Path("/training-app/configs/training.yaml")

CONFIG_PATH = get_config_file()

# this function takes two dates in string format and calculate their difference in years  (date1 - date2)
def calculate_age(df: pd.DataFrame, date1: str, date2: str, new_column_name: str) -> pd.DataFrame:
    """
    Users native datetime to calculate date1 - date2
    """
    try:
      # this one is "Data de Ocorrência"
        df[date1] = pd.to_datetime(df[date1], format="%d/%m/%Y %H:%M:%S", errors='raise')
        df[date2]= pd.to_datetime(df[date2], format="%m/%d/%Y",errors='raise')
        df.loc[:,new_column_name] = ((df[date1] - df[date2]).dt.days / 365.25)
    except Exception as e:
            logging.info(f'\n[ERRO]: {e}')
            raise
    return df



# def correct_period_formats(df: pd.DataFrame, date1: str, date2: str, new_column_name: str)
def fill_column_with_content(df: pd.DataFrame, column: str, content = 0, fill_all = False ) -> pd.DataFrame:
    """
    Fill all means fill the whole column with that content. False means fill NaN only.
    Content equall to zero defaults to fill zero
    """
    try:
        if column not in df.columns:
             raise KeyError("Column {column} does not exist in DataFrame.")
        if fill_all:
            df[column] = content
        else:
            df.fillna({column: content}, inplace=True)
        return df
    except RuntimeError as e:
            print(f'\n[ERRO]: There was an error filling data with content {e}')
    except KeyError as e:
            print(f'\n[ERRO]: Column was not found: {e}')

###################### Inserting new functions ######################


def calculate_ano_sem(df: pd.DataFrame) -> pd.DataFrame:
    df['Ano']  = df['AnoSem'].astype('int')
    df['Parcela'] = df['Semestre'] / 10
    if 'AnoSem' in df.columns:
        df.drop(columns={'AnoSem'}, inplace=True)
    df['AnoSem'] = df['Ano'] + df['Parcela']
    return df

def drop_columns(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df = df.copy()
    df.drop(columns=cols, inplace=True)
    return df 

def merge_dfs(df: pd.DataFrame, df_to_merge: pd.DataFrame, cols: list[str], how: str, key: str ) -> pd.DataFrame:
    return df.merge(df_to_merge[cols], on=key, how=how )

def standardize_column_text (df :pd.DataFrame, col: str) -> pd.DataFrame:
    df = df.copy() 
    df[col] = (
    df[col]
    .str.normalize('NFKD')
    .str.encode('ascii', errors='ignore')
    .str.decode('utf-8')
    .str.upper()
    .str.replace(r'\(OPTATIVA\)', '', regex=True)
    .str.strip())
    return df 

    
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



def load_datasets(CONFIG_PATH: str) -> pd.DataFrame:
  """
  Loads the datasets and separetes them
  """

  dfs = load_config(CONFIG_PATH)

  df_active = pd.read_csv(dfs['ACTIVE_DATASET'])
  df_deactive = pd.read_csv(dfs['EVADED_DATASET'])
  df_history = pd.read_csv(dfs['HISTORY_DATASET'])

  return df_active, df_deactive, df_history



def eliminating_duplicates_ap_ae(df: pd.DataFrame) -> pd.DataFrame:
    
    """
    AE and AP are duplicated in the dataset. 
    Therefore it must be converted to one single row. 
    """

    ae_ap_pairs = df.groupby(['RGA_Anon', 'Nome_Disciplina']) \
        .filter(lambda g: {'AP', 'AE'}.issubset(set(g['Situação'])))

    df_adjust = df.copy()

    nota_ap = ae_ap_pairs[ae_ap_pairs['Situação'] == 'AP'] \
        .groupby(['RGA_Anon', 'Nome_Disciplina'])['Nota'].max()

    mask_ae = (df_adjust['Situação'] == 'AE') & (
        df_adjust.set_index(['RGA_Anon', 'Nome_Disciplina']).index.isin(nota_ap.index)
    )

    df_adjust.loc[mask_ae, 'Nota'] = df_adjust.loc[mask_ae].set_index(
        ['RGA_Anon', 'Nome_Disciplina']
    ).index.map(nota_ap)

    mask_ap_to_drop = (df_adjust['Situação'] == 'AP') & (
        df_adjust.set_index(['RGA_Anon', 'Nome_Disciplina']).index.isin(nota_ap.index)
    )

    df_adjust = df_adjust[~mask_ap_to_drop].copy()
    return df_adjust


def setting_subject_faiulures (df: pd.DataFrame) -> pd.DataFrame: 
    """
    Convert subject status into a binary outcome:
    - 1 = failure in a subject
    - 0 = non-failure
    Rows with 'MA' status are excluded.
    """
    df = df.copy()
    df = df[df['Situação'] != "MA"]
    failures = ['RMF', 'RM', 'RP', 'RF']

    df['Situação']  = np.where(
        df['Situação'].isin(failures),
        1,
        0
    )
    return df 


def calculate_failure_ratio (df: pd.DataFrame) -> pd.DataFrame:

    df['Reprovacao_Ponderada_Semestral'] = df["Crédito"]* df["Situação"]

    df['Reprovacao_Ponderada_Semestral'] = (
            df.groupby(["AnoSem",  "RGA_Anon"])["Reprovacao_Ponderada_Semestral"]
                .transform("sum")
    )

    total_credit = df.groupby(["AnoSem",  "RGA_Anon"])['Crédito'].transform("sum")
    total_credit = total_credit.astype("float")
    df['Reprovacao_Ponderada_Semestral'] = df['Reprovacao_Ponderada_Semestral'].astype("float")
        
    df['Reprovação_Media_Semestral']  = (df['Reprovacao_Ponderada_Semestral'] / total_credit)
    df.drop(columns={'Reprovacao_Ponderada_Semestral'}, inplace=True)

    return df

def selecting_valid_period(df: pd.DataFrame) -> pd.DataFrame:
   return df[df['AnoSem'] >= 2009.1].copy()



def calculate_permanence_period_in_semesters(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # Ensure Período ingresso is float and convert to decimal
    df['Período ingresso'] = df['Período ingresso'].astype(float) / 10

    # Cap any fractional semester > 2 to 2 (e.g., 2024.3 -> 2024.2)
    def cap_sem(x):
        int_part = int(x)
        frac_part = int(round((x - int_part) * 10))
        frac_part = min(frac_part, 2)  # cap to 2
        return float(f"{int_part}.{frac_part}")

    df['AnoSemCap'] = df['AnoSem'].apply(cap_sem)
    df['Período ingresso Cap'] = df['Período ingresso'].apply(cap_sem)

    # Create chronological mapping
    all_values = pd.concat([df['AnoSemCap'], df['Período ingresso Cap']]).dropna().unique()
    mapping = {val: i+1 for i, val in enumerate(sorted(all_values))}

    # Map to ordered IDs
    df['AnoSemIdOrdered'] = df['AnoSemCap'].map(mapping)
    df['PeriodoIngressoIdOrdered'] = df['Período ingresso Cap'].map(mapping)

    # Calculate permanence in semesters
    df['Tempo_Permanencia_Em_Semestres'] = df['AnoSemIdOrdered'] - df['PeriodoIngressoIdOrdered'] + 1

    # Drop helper columns
    df.drop(columns=['AnoSemIdOrdered', 'PeriodoIngressoIdOrdered', 'AnoSemCap', 'Período ingresso Cap'], inplace=True)
    
    return df


def calculate_total_accumulated_credits(df: pd.DataFrame) -> pd.DataFrame: 

    mapping = {
        20241: 210,
        20191: 200,
        20091: 211
    }
    df = df.copy()

    df['Total_creditos_estrutura'] = df['Estrutura'].map(mapping)

    resumo_creditos = df.groupby(['RGA_Anon', 'Tempo_Permanencia_Em_Semestres'])['Crédito'].sum().reset_index()


    resumo_creditos['Total_Creditos_Acumulados'] = resumo_creditos.groupby('RGA_Anon')['Crédito'].cumsum()
    df = df.merge(
        resumo_creditos[['RGA_Anon', 'Tempo_Permanencia_Em_Semestres', 'Total_Creditos_Acumulados']],
        on=['RGA_Anon', 'Tempo_Permanencia_Em_Semestres'],
        how='left'
    )

    return df


def calculate_normalized_academic_age(df):
    # 1. Definir os limites por estrutura (ajuste os valores conforme sua realidade)
    metas = {
        20091: {'min_credits': 211, 'ideal_semesters': 8},
        20191: {'min_credits': 200, 'ideal_semesters': 8},
        20241: {'min_credits': 210, 'ideal_semesters': 8}
    }
    df = df.copy()
    def get_age(row):
        struct = row['Estrutura']
        if struct not in metas: return row['Tempo_Permanencia_Em_Semestres'] # fallback
        
        meta = metas[struct]
        progresso = min(1.0, row['Total_Creditos_Acumulados'] / meta['min_credits'])
        
        return progresso * meta['ideal_semesters']

    df['Idade_Academica'] = df.apply(get_age, axis=1)
    df['Estrutura'] = df['Estrutura'].astype(int)
    
    return df


def calculate_academic_lag_in_semesters(df: pd.DataFrame) -> pd.DataFrame: 
    
    df = df.copy()
    df = df.sort_values(['RGA_Anon', 'Tempo_Permanencia_Em_Semestres'])
    df['Tempo_Permanencia_Em_Semestres'] = df['Tempo_Permanencia_Em_Semestres'].astype(float)
    df['Idade_Academica'] = df['Idade_Academica'].astype(float)
    df['Lag_Academico_Em_Semestres'] = df.groupby('RGA_Anon').apply(
    lambda g: g['Tempo_Permanencia_Em_Semestres'] - g['Idade_Academica']
).reset_index(level=0, drop=True)
    return df


def log_and_pipe(df: pd.DataFrame,success_msg: str, func: Callable, *args: Any, **kwargs: Any) -> pd.DataFrame:
    """Logs the start, executes the function, logs success, and returns the DataFrame."""
    logging.info(f"\n\n[INFO]: Starting operation: {func.__name__}...")

    df_transformed = func(df, *args, **kwargs)

    logging.info(f"\n[OK]: {success_msg}")
    return df_transformed



def cleaning_pipeline ():

  """
  This is the main function. It defines and processes datasets
  """
  logging.basicConfig(level=logging.INFO)

  logging.info("\n\n[INFO]: Starting application...")

  try:

    logging.info("\n\n[INFO]: Loading datasets...")
    df_active, df_deactive, df_history,  = load_datasets(CONFIG_PATH)

    df_merged = df_history.copy()
    all_students = pd.concat([df_active, df_deactive], axis=0)

    logging.info("\n\n[OK]: Sucessfully loaded and merged the datasets")
  except Exception as e:
    logging.exception(f"[ERROR]: Could not load datasets properly{e}")

  try:
    df_merged = (
      df_merged

        .pipe(log_and_pipe, 
              '[OK]: Creating AnoSem column', 
              calculate_ano_sem)

        .pipe(log_and_pipe, 
           '[OK]: Merging all the datasets', 
              merge_dfs,
              all_students, ['RGA_Anon', 'Período ingresso', 'Estrutura', 'Situação atual'],  'left', 'RGA_Anon')

           .pipe(log_and_pipe, 
           '[OK]: Standardizing the column text',
            standardize_column_text,
            'Nome_Disciplina')

            .pipe(log_and_pipe,
            '[OK]: Eliminated duplicates of AE and AP',
            eliminating_duplicates_ap_ae)

            .pipe(log_and_pipe,
              '[OK]: Calculating the failure ratio per semester',
              calculate_failure_ratio)

            .pipe(log_and_pipe, 
              '[OK]: Selecting valid period - 2009.1 plus', 
              selecting_valid_period)

              .pipe(log_and_pipe, 
              '[OK]: Creating permance time', 
              calculate_permanence_period_in_semesters)

              .pipe(log_and_pipe, 
              '[OK]: Summing all the accumulated credits', 
              calculate_total_accumulated_credits) 

              .pipe(log_and_pipe, 
              '[OK]: Calculating academic age', 
              calculate_normalized_academic_age) 

              .pipe(log_and_pipe, 
              '[OK]: Calculating academic lag in semesters', 
              calculate_academic_lag_in_semesters) 
              


    )
    

  except Exception as e:
        logging.exception(f"[ERROR]: There was an exception creating new columns in the dataset {e}")
        raise
  try:
    # df_merged = (
    #   df_merged
    #   # .pipe(log_and_pipe,
    #   #      'Sucessfully corrected confusing city names',
    #   #       match_cities_name,
    #   #       "Naturalidade")
    #   # .pipe(log_and_pipe,
    #   #      'Sucessfully grouped disciplines together',
    #   #       mapping_disciplines_names,
    #   #       "Nome_Disciplina","Núcleo de Disciplinas" ,"CC")
     
    # )

    # Intermediate dataset after cleaning the dataset
    config_to_preprocessed = load_config(CONFIG_PATH)
    path_to_preprocessed = config_to_preprocessed["PREPROCESSED_DATASET"]

    df_merged.to_csv(path_to_preprocessed, index=False)

  except Exception as e:
    logging.exception(f"[ERROR]: There was an exception resolving name conflics{e} ")


if __name__ == "__main__":
  start_time = time.time()
  cleaning_pipeline()
  total_time = time.time() - start_time
  print(f"\ntotal time taken: {total_time:.2f}s\n")
