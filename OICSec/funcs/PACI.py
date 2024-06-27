import logging
import re
from difflib import SequenceMatcher

import pandas as pd
from fuzzywuzzy import process

from OICSec.models import Oic, TipoRevision, ProgramaRevision
from PAA import preprocess_dataframe


def get_object_id_by_text(text, model):
    """
    Busca un objeto en el modelo basado en el texto proporcionado y retorna su ID.

    Args:
        text (str): Texto a buscar.
        model (Model): Clase del modelo de Django.

    Returns:
        int or None: ID del objeto encontrado o None si no se encuentra.
    """
    try:
        match = process.extractOne(text, model.objects.values_list('tipo', flat=True))
        if match:
            obj = model.objects.get(tipo=match[0])
            return obj.pk
    except model.DoesNotExist:
        return None
    except Exception as e:
        logging.error(f"Error en búsqueda de {model._meta.verbose_name}: {e}")

    return None


def extract_number_and_year(number):
    """
    Extrae el número y el año de una cadena de formato específico.

    Args:
        number (str): Cadena que contiene el número y el año en el formato especificado.

    Returns:
        dict: Diccionario con claves 'Numero' y 'Año'. Si no se encuentra el patrón, retorna None para ambas claves.
    """
    pattern = r"([\d]{2})/(\d{4})"
    match = re.match(pattern, number)

    if match:
        return {"Numero": match.group(1), "Año": match.group(2)}
    else:
        return {"Numero": None, "Año": None}


def extract_programa_tipo(text):
    """
    Extrae el tipo y programa de revisión basado en el texto proporcionado.

    Args:
        text (str): Cadena que contiene el tipo y programa de revisión.

    Returns:
        dict: Diccionario con las claves 'tipo_revision' y 'programa_revision' y sus respectivos IDs.
    """
    if "-" in text:
        tipo_revision_text, programa_revision_text = map(str.strip, text.split("-", 1))
    else:
        tipo_revision_text = text.strip()
        programa_revision_text = None

    result = {
        "tipo_revision": None,
        "programa_revision": None
    }

    if tipo_revision_text:
        result["tipo_revision"] = get_object_id_by_text(tipo_revision_text, TipoRevision)

    if programa_revision_text:
        result["programa_revision"] = get_object_id_by_text(programa_revision_text, ProgramaRevision)

    return result


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


def extract_paci(path):
    """
    Extrae información específica de un archivo Excel de PACI.

    Args:
        path (str): Ruta al archivo Excel.

    Returns: list or None: Lista de datos extraídos del archivo Excel de PACI o None si no se encuentra información
    suficiente.
    """
    result = []
    try:
        sheets = pd.read_excel(path, sheet_name=None)
        for sheet in sheets:
            df = sheets.get(sheet)

            # Se extraen los indices de las filas que no tienen ninguna columna vacia
            indices = df[df.notnull().all(axis=1)].index

            # Elimina el primer valor de indices que es el encabezado de datos para solo tener los controles
            if len(indices) > 0:
                controles_indices = indices.drop(indices[0])
            else:
                return None

            organo, df = preprocess_dataframe(df=df, indices=controles_indices)

            # Filtrar filas que no tienen valores nulos
            df_cleaned = df.dropna().iloc[1:]

            best_match, best_ratio = get_best_match(organo, list(Oic.objects.all().values_list('nombre', flat=True)))

            if best_ratio <= 0.5:
                return None

            dat = [best_match, []]

            df_cleaned.apply(lambda row: dat[1].append({
                **extract_number_and_year(row.iloc[0]),
                "Denominacion": row.iloc[1],
                "Objetivo": row.iloc[2],
                "Area": row.iloc[3],
                "Trimestre": trim_to_number(row.iloc[4]),
                **extract_programa_tipo(row.iloc[5])
            }), axis=1)

            result.append(dat)

        return result if result else None
    except Exception as e:
        logging.error(f"Error al extraer información del archivo PACI: {e}")
        return None
