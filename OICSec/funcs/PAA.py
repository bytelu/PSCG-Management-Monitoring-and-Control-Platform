import re
from difflib import SequenceMatcher

import pandas as pd
from fuzzywuzzy import process

from OICSec.models import Materia, Programacion, Enfoque, Temporalidad, Oic


def preprocess_dataframe(df, indices):
    """
    Realiza operaciones comunes de preprocesamiento en el DataFrame.

    Args:
        df (pd.DataFrame): DataFrame a preprocesar.
        indices (pd.Index): Índices de filas válidas a partir de las cuales se realiza el preprocesamiento.

    Returns:
        str or None: Nombre del órgano y DataFrame preprocesado, o None si no hay índices válidos.
    """
    if len(indices) == 0:
        return None

    organo_index = indices[0] - 1
    organo = clean_text(str(df.iloc[organo_index, 0]))

    df = df.applymap(lambda x: clean_text(x) if pd.notnull(x) else x)

    return organo, df


def extract_number_and_year(number):
    """
    Extrae el número y el año de una cadena de formato específico.

    Args:
        number (str): Cadena que contiene el número y el año en el formato especificado.

    Returns:
        dict: Diccionario con claves 'Numero' y 'Año'. Si no se encuentra el patrón, retorna None para ambas claves.
    """
    pattern = r"([A-Z])-([\d]{1,4})/(\d{4})"
    match = re.match(pattern, number)

    if match:
        return {"Numero": match.group(2), "Año": match.group(3)}
    else:
        return {"Numero": None, "Año": None}


def extract_ejercicio(alcance):
    """
    Extrae el año del alcance proporcionado.

    Args:
        alcance (str): Cadena que contiene el año a extraer.

    Returns:
        str or None: Año extraído o None si no se encuentra un año válido.
    """
    pattern = r"\b\d{4}\b"
    match = re.search(pattern, alcance)

    if match:
        return match.group()
    else:
        return None


def trim_to_number(trimestre):
    """
    Convierte un trimestre dado en su número correspondiente.

    Args:
        trimestre (str): Cadena que representa un trimestre.

    Returns:
        int or None: Número del trimestre (1 a 4) o None si no se encuentra una coincidencia suficientemente alta.
    """
    trimestres_posibles = ["Primero", "Segundo", "Tercero", "Cuarto"]
    match = process.extractOne(trimestre, trimestres_posibles)

    if match[1] >= 80:
        return trimestres_posibles.index(match[0]) + 1
    else:
        return None


def extract_mpet(**kwargs):
    """
    Extrae objetos de base de datos basados en el tipo de datos proporcionados.

    Args:
        **kwargs: Diccionario con claves 'Materia', 'Programacion', 'Enfoque', 'Temporalidad'.

    Returns:
        dict: Diccionario con los valores de los IDs correspondientes a los objetos encontrados en la base de datos.
              Si no se encuentra un objeto correspondiente, el valor asociado a la clave será None.
    """
    mappings = {
        'Materia': Materia,
        'Programacion': Programacion,
        'Enfoque': Enfoque,
        'Temporalidad': Temporalidad
    }

    result = {}

    for key, model in mappings.items():
        value = kwargs.get(key)
        if value:
            match = process.extractOne(value, model.objects.all().values_list('tipo', flat=True))
            obj = model.objects.filter(tipo=match[0]).first() if match else None
            if obj:
                result[key] = getattr(obj, model._meta.pk.attname)
            else:
                result[key] = None
        else:
            result[key] = None

    return result


def clean_text(text):
    """
    Limpia una cadena de texto de caracteres no deseados.

    Args:
        text (str): Cadena de texto a limpiar.

    Returns:
        str: Cadena de texto limpia.
    """
    cleaned_text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ").replace('"', '')
    return cleaned_text


def get_best_match(organo, options):
    """
    Encuentra la mejor coincidencia entre una cadena de texto y una lista de opciones.

    Args:
        organo (str): Cadena de texto para la cual se busca la mejor coincidencia.
        options (list): Lista de cadenas de texto entre las cuales se busca la mejor coincidencia.

    Returns:
        tuple: Tupla con la mejor coincidencia encontrada y el ratio de similitud más alto.
               Si no se encuentra ninguna coincidencia suficiente (ratio <= 0.5), retorna (None, 0.0).
    """
    best_match = None
    highest_ratio = 0.0

    for option in options:
        ratio = SequenceMatcher(None, organo, option).ratio()
        if ratio > highest_ratio:
            highest_ratio = ratio
            best_match = option

    return best_match, highest_ratio


def extract_paa(path):
    """
    Extrae datos de auditorías de un archivo Excel y los estructura en un formato específico.

    Args:
        path (str): Ruta del archivo Excel del cual se extraerán los datos.

    Returns:
        list or None: Lista con el nombre del Organo Interno de Control y un diccionario de datos de auditorías
                      estructurados, o None si no se encontraron auditorías válidas.
    """

    result = []
    sheets = pd.read_excel(path, sheet_name=None)
    for sheet in sheets:
        df = sheets.get(sheet)

        # Se extraen los indices de las auditorias: los que no tienen ninguna columna vacia
        auditorias_indices = df[df.notnull().all(axis=1)].index

        organo, df = preprocess_dataframe(df=df, indices=auditorias_indices)

        # Filtrar filas que no tienen valores nulos
        df_cleaned = df.dropna()

        best_match, best_ratio = get_best_match(organo, list(Oic.objects.all().values_list('nombre', flat=True)))

        if best_ratio <= 0.5:
            return None

        dat = [best_match, []]

        # Aplicar las operaciones a cada fila de manera vectorizada
        df_cleaned.apply(lambda row: dat[1].append({
            **extract_number_and_year(row.iloc[0]),
            "Denominacion": row.iloc[1],
            "Unidad": row.iloc[2],
            "Objetivo": row.iloc[3],
            "Alcance": row.iloc[4],
            **extract_mpet(
                Materia=row.iloc[5],
                Programacion=row.iloc[6],
                Enfoque=row.iloc[7],
                Temporalidad=row.iloc[8]
            ),
            "Trimestre": trim_to_number(row.iloc[9]),
            "Ejercicio": extract_ejercicio(row.iloc[4])
        }), axis=1)

        result.append(dat)

    return result
