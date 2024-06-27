import re
from difflib import SequenceMatcher

import pandas as pd
from fuzzywuzzy import process

from OICSec.models import Oic, TipoRevision, ProgramaRevision
from PAA import clean_text


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
    if "-" in text:
        tipo_revision_text, programa_revision_text = map(str.strip, text.split("-", 1))
    else:
        tipo_revision_text = text.strip()
        programa_revision_text = None

    result = {
        "tipo_revision": None,
        "programa_revision": None
    }

    # Buscar coincidencia para tipo de revisión
    if tipo_revision_text:
        try:
            match_tipo = process.extractOne(tipo_revision_text, TipoRevision.objects.values_list('tipo', flat=True))
            if match_tipo:
                tipo_revision_obj = TipoRevision.objects.get(tipo=match_tipo[0])
                result["tipo_revision"] = tipo_revision_obj.pk
        except TipoRevision.DoesNotExist:
            result["tipo_revision"] = None
        except Exception as e:
            # Manejar excepciones específicas aquí
            result["tipo_revision"] = None
            # logging.error(f"Error en búsqueda de tipo de revisión: {e}")

    # Buscar coincidencia para programa de revisión
    if programa_revision_text:
        try:
            match_programa = process.extractOne(programa_revision_text,
                                                ProgramaRevision.objects.values_list('tipo', flat=True))
            if match_programa:
                programa_revision_obj = ProgramaRevision.objects.get(tipo=match_programa[0])
                result["programa_revision"] = programa_revision_obj.pk
        except ProgramaRevision.DoesNotExist:
            result["programa_revision"] = None
        except Exception as e:
            # Manejar excepciones específicas aquí
            result["programa_revision"] = None
            # logging.error(f"Error en búsqueda de programa de revisión: {e}")

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
    result = []
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

        # Se comprueba que existan controles internos
        if len(controles_indices) == 0:
            return None

        # Obtener el indice de la fila anterior al inicio de los controles internos
        organo_index = controles_indices[0] - 1

        # Obtener el nombre del "organo" de la primera columna de la fila de organo_index
        organo = clean_text(str(df.iloc[organo_index, 0]))

        # Limpiar todos los datos del dataframe
        df = df.map(lambda x: clean_text(x) if pd.notnull(x) else x)

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

    return result
