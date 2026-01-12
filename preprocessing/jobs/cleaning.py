import logging
import os
import re
import time
from datetime import date
from typing import Any, Callable

import numpy as np
import pandas as pd
import unidecode
import yaml

CONFIG_PATH =  "../configs/cleaning.yaml"


def normalize_names(text: str) -> str:
  """
  Removes accents and make the text lowercase
  """
  if pd.isnull(text):
      return text
  text = str(text)
  text = unidecode.unidecode(text)
  text = text.lower().strip()
  text = re.sub(r'[^\w\s]', '', text)
  text = text.title()
  return text

# this functions maps the mispelled cities to their correct name
def match_cities_name(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Standardize confusing city names
    """
    regex_mapping = {
        r".*cuiaba.*|.*CUIABA.*|.*Cuiabamt.*": "Cuiabá",
        r".*aragarcas.*|.*Aragarcasgo.*|.*ARAGARÇAS.*": "Aragarças",
        r".*barra do garcas.*|.*Barra Do Garcas.*|.*BARRA DO GARÇAS.*": "Barra Do Garças",
        r".*alta floresta.*|.*Alta Floresta.*|.*ALTA FLORESTA.*": "Alta Floresta",
        r".*nova xavantina.*|.*Nova Xavantina.*": "Nova Xavantina",
        r".*baliza.*|.*Baliza Go.*": "Baliza",
        r".*rondonopolis.*|.*Rondonopolitano.*": "Rondonópolis",
        r".*braganca.*|.*Braganca Pa.*": "Bragança",
        r".*palmitos.*|.*Palmitossc.*": "Palmitos",
        r".*vazante.*|.*Vazante Mg.*": "Vazante",
        r".*jussara.*|.*Jussarago.*": "Jussara",
        r".*rio branco.*|.*Rio Branco  Mt.*": "Rio Branco",
        r".*mato grosso.*|.*Mato Grossointerior.*": "Mato Grosso",
        r".*chapeco.*|.*Chapecosc.*": "Chapecó",
        r".*agua boa.*|.*Agua Boamt.*": "Água Boa",
        r".*sao joaquim.*|.*Sao Joaquim Sc.*": "São Joaquim",
        r".*Brasilia.*|.*df.*|.*brasilia.*": "Brasília",
        r".*Goiania.*|.*goianiago.*|.*Goiânia.*": "Goiânia",
        r".*São Paulo.*|.*Sao Paulo.*|.*sao paulo.*": "São Paulo",
        r".*Canabravamg.*": "Canabrava"


    }
    try:

      df.loc[:, column] = df[column].apply(normalize_names)

      def apply_regex(name):
        if not isinstance(name, str):
            return name
        for pattern, correct_name in regex_mapping.items():
            if re.search(pattern, name, re.IGNORECASE):
                return correct_name
        return name

      if column in df.columns:
        df.loc[:, column] = df[column].apply(apply_regex)
        return df
      raise KeyError(f"Column {column} does not exist")

    except KeyError as e:
      print(f"Column {e} does not exist in dataset.")
    except RuntimeError as e:
      print(f"Can't fill data{e}")



# this function takes two dates in string format and calculate their difference in years  (date1 - date2)
def calculate_difference_between_dates(df: pd.DataFrame, date1: str, date2: str, new_column_name: str) -> pd.DataFrame:
    """
    Users native datetime to calculate date1 - date2
    """
    try:
        df[date1] = pd.to_datetime(df[date1], errors='raise')
        df[date2]= pd.to_datetime(df[date2], errors='raise')
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



def standardize_year_and_semester(df: pd.DataFrame, column: str ,year_col: str, semester_col: str) -> pd.DataFrame:
  """
  Extracts Semester something happened. As in [Perído] = 20201 -> means year = 2020 and semester = 1
  """
  if column in df.columns:
      df[column] = df[column].astype(str)
      df.loc[:,semester_col] = df[column].str[-1]
      df.loc[:,year_col] = df[column].str[:4]
      #df.loc[:,year_col] = df.loc[:,year_col].astype(date)
      return df
  else:
    raise KeyError(f"Column {column} does not exist in current dataset")


def total_time_stay(df: pd.DataFrame, ocurrence_date: str, entrance_date: str, target_column_name: str) -> pd.DataFrame:
  """
  Calculates the average time since the entrace of the student to the ocurrence of their evasion
  As in:
    - Ocurrence -> 2022
    - Entrance  -> 2020
    - Total_Time =  Ocurrence - Entrance
  Therefore the total time to evasion is 2 years
  """

  df = calculate_difference_between_dates(df, ocurrence_date, entrance_date, target_column_name)
  return df




def estimating_ocurrence_date_or_year(df: pd.DataFrame, ocurrence_date: str, estimate_year = False) ->  pd.DataFrame:
  """
  Returns the ['Data ocorrência'] field. If it is null, it returns the year of ['Periodo ingresso']
  """
  df.loc[:,ocurrence_date] = pd.to_datetime(df[ocurrence_date])
  filtered = (df['Período ingresso'] // 10)
  filtered = pd.to_datetime(filtered, format='%Y', errors='coerce')
  df.loc[:,ocurrence_date] = np.where(
    df[ocurrence_date].isnull(),
    filtered,
    df[ocurrence_date]
  )
  if estimate_year:
    df.loc[:,'Ano_AtualNaoEhPeriodo'] = df[ocurrence_date].dt.year
    return df


def merging_datasets_with_history(df_finished: pd.DataFrame, df_evaded: pd.DataFrame, df_active: pd.DataFrame, df_history: pd.DataFrame, key: str, how: str) -> pd.DataFrame:
  """
  Merges the three important datasets with the history one
  """
  x = pd.concat([
      df_finished.assign(classe="Concluinte"),
      df_evaded.assign(classe="Evadido"),
      df_active.assign(classe="Ativo")
  ])
  df_full = pd.merge(x, df_history, on=key, how=how)
  return df_full


def counting_amount_of_sf(df: pd.DataFrame, column_sf: str, key: str) -> pd.DataFrame:
  """
  Returns the amount of failure or approvation
  """
  counts = (
    df
    .groupby([key, column_sf])
    .size()
    .unstack(fill_value=0)
  )
  counts = counts.rename(columns={
    c: f"total_{c}" for c in counts.columns
  })
  counts.reset_index()
  return df


def load_datasets(CONFIG_PATH: str) -> pd.DataFrame:
  """
  Loads the datasets and separetes them
  """
  config = yaml.safe_load(open(CONFIG_PATH))

  df_active = pd.read_csv(config['DATA_CLEANING']['RAW_ACTIVE'])
  df_deactive = pd.read_csv(config['DATA_CLEANING']['RAW_DEACTIVE'])
  df_history = pd.read_csv(config['DATA_CLEANING']['RAW_HISTORY'])

  """
  Here we are distinguinshing those finished college and who dropped out
  """
  df_finished = df_deactive[df_deactive[config['COLUMNS']['MOTIVO_EVASAO_COLUMN']] == config['COLUMNS']['MOTIVO_EVASAO_VALUE']]
  df_evaded = df_deactive[df_deactive[config['COLUMNS']['MOTIVO_EVASAO_COLUMN']] != config['COLUMNS']['MOTIVO_EVASAO_VALUE']]
  return df_active, df_deactive, df_history, df_finished, df_evaded


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


def log_and_pipe(df: pd.DataFrame,success_msg: str, func: Callable, *args: Any, **kwargs: Any) -> pd.DataFrame:
    """Logs the start, executes the function, logs success, and returns the DataFrame."""
    logging.info(f"\n\n[INFO]: Starting operation: {func.__name__}...")

    df_transformed = func(df, *args, **kwargs)

    logging.info(f"\n[OK]: {success_msg}")
    return df_transformed


def counting_failure_per_nucleo(df: pd.DataFrame) -> pd.DataFrame:
  """
  Counts the which area of knowledge the person has most failled
  """
  failures = df[df['SF'].isin(['RM' ,'RMF', 'RP','RF'])]
  nucleo_counts = failures.groupby(["rga_anonimo","Núcleo de Disciplinas"]).size()
  for (rga, disciplina), nucleo_counts in nucleo_counts.items():
    df.loc[df['rga_anonimo'] == rga,
      f"reprovacoes_{disciplina}"] = nucleo_counts
    df.fillna({f"reprovacoes_{disciplina}": 0},inplace=True)
  return df


def extract_entrance_year(df: pd.DataFrame, entrance_year: str, target_col: str) -> pd.DataFrame:
  df.loc[:,target_col] = df[entrance_year] // 10
  return df




def cleaning_pipeline ():
  """
  This is the main function. It defines and processes datasets
  """
  logging.basicConfig(level=logging.INFO)
  logging.info("\n\n[INFO]: Starting application...")

  # Loading dataset
  try:
    logging.info("\n\n[INFO]: Loading datasets...")
    df_active, df_deactive, df_history, df_finished, df_evaded = load_datasets(CONFIG_PATH)
    df_merged = merging_datasets_with_history(df_finished, df_evaded, df_active, df_history, 'rga_anonimo', 'right')
    logging.info("\n\n[OK]: Sucessfully loaded and merged the datasets")
  except Exception as e:
    logging.exception(f"[ERROR]: Could not load datasets properly{e}")

  # Creating extra columns in dataset
  try:
    df_merged = (
      df_merged
      .pipe(log_and_pipe,
           '[OK]: Sucessfully created column - Idade',
            calculate_difference_between_dates,
           'Data ocorrência',  'Data Nascimento', 'Idade')
      .pipe(log_and_pipe,
           '[OK]: Sucessfully created column - Ano Ingresso e Semestre Ingresso',
            standardize_year_and_semester,
           'Período ingresso','Ano Ingresso', 'Semestre Ingresso')
      .pipe(log_and_pipe,
            '[OK]:Sucessfully extracted the current year and the current Semester',
            standardize_year_and_semester,
            'Período','Ano_Periodo_Atual', 'Semestre Atual',)
      .pipe(log_and_pipe,
           '[OK]:Sucessfully created average time to evade columns',
            total_time_stay,
           'Data ocorrência', 'Ano Ingresso', 'Tempo_De_Permanencia')
      .pipe(log_and_pipe,
           '[OK]:Sucessfully counted the amount of failure and approvation',
            counting_amount_of_sf,
           'SF', 'rga_anonimo')
    )
    # completatmente eerrado
    # print(df_merged['Ano Ingresso'].head(50))
    # print(df_merged['Ano_Periodo_Atual'])

  except Exception as e:
        logging.exception(f"[ERROR]: There was an exception creating new columns in the dataset {e}")
        raise
  try:
    df_merged = (
      df_merged
      .pipe(log_and_pipe,
           'Sucessfully corrected confusing city names',
            match_cities_name,
            "Naturalidade")
      .pipe(log_and_pipe,
           'Sucessfully grouped disciplines together',
            mapping_disciplines_names,
            "Disciplina","Núcleo de Disciplinas" ,"CC")
      .pipe(log_and_pipe,
           'Sucessfully mapped reprovations per nucleo',
            counting_failure_per_nucleo)
    )

    df_merged.to_csv("now.csv", index=False)

  except Exception as e:
    logging.exception(f"[ERROR]: There was an exception resolving name conflics{e} ")


if __name__ == "__main__":
  start_time = time.time()
  pipeline()
  total_time = time.time() - start_time
  print(f"\ntotal time taken: {total_time:.2f}s\n")
