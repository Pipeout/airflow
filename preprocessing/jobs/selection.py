import logging

import pandas as pd


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
  return df.drop_duplicates()


def drop_columns(df: pd.DataFrame) -> pd.DataFrame:
  try:
      df = df.drop(
        columns=["Grupo de Disciplinas",
                "MF", # media final da disciplina
                "TU", # Turma
                "CR", # Coeficiente de rendimento
                "CH", # carga horaria da disciplina
                "Código",# codigo da disciplina
                "SE", # indefinido
                "Estrutura", # estrura do pcc vigente
                "Optativa", # nao eh util
                "Núcleo de Disciplinas",
                "Situação atual",
                "Estrangeiro",
                "Disciplina",
                "Nome da Disciplina",
                "SF",
                "FA",
                "Tipo de Disciplina",
                "Nacionalidade",
                "Período",
             #   "Unnamed: 0",
                "Ano",
                'Período ingresso'
        ])
  except KeyError as e:
    raise KeyError(f"[ERROR]: column did not exist or was null{e}")
  return df


def selection_pipeline():
    logging.basicConfig(level=logging.INFO)
    df = pd.read_csv("now.csv")
    logging.info("\n\n[INFO]: Starting to drop useless columns...")
    df = (df
      .pipe(drop_columns)
      .pipe(remove_duplicates)
    )

    print(df)
    df.to_csv("final_one.csv", index=True)
    logging.info("\n\n[OK]: Final dataset saved to Bucket...")
