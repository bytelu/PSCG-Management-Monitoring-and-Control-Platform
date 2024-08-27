import os
from copy import copy
from dataclasses import dataclass
from typing import List, Optional

from openpyxl import load_workbook
from openpyxl.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet


@dataclass
class SupervisionData:
    """
    Clase que almacena la información general de una supervisión.

    Atributos:
        OIC (str): Órgano Interno de Control.
        Numero (str): Número de la supervisión.
        Nombre (str): Nombre del sistema supervisado.
        Fecha (str): Fecha de la supervisión.
        Clave (str): Clave de la supervisión.
        Anyo_Trimestre (str): Año y trimestre de la supervisión.
        Objetivo (str): Objetivo de la supervisión.
        Area (str): Área supervisada.
        Ejercicio (str): Ejercicio fiscal.
    """
    OIC: str
    Numero: str
    Nombre: str
    Fecha: str
    Clave: str
    Anyo_Trimestre: str
    Objetivo: str
    Area: str
    Ejercicio: str


@dataclass
class Concepto:
    """
    Clase que almacena el estado y comentario de un concepto evaluado durante la supervisión.

    Atributos:
        Estado (int): Estado del concepto (0: No cumple, 1: Cumple, 2: Suspensión de términos, 3: No aplica).
        Comentario (str): Comentario del concepto.
    """
    Estado: int
    Comentario: str


@dataclass
class ConceptosLista:
    """
    Clase que almacena una lista de conceptos

    Atributos:
        Conceptos (list[Concepto]): Lista de conceptos
    """
    Conceptos: List[Concepto]


@dataclass
class Styles:
    """
    Clase que maneja estilos de celdas predefinidos en una hoja de cálculo Excel.

    Atributos:
        workbook (Worksheet): Hoja de cálculo de estilos.

    Métodos:
        __post_init__(): Copia los estilos de ejemplo de la hoja de estilos.
        style_cell(target_cell, kind): Aplica un estilo a una celda objetivo.
    """
    workbook: Worksheet

    def __post_init__(self):
        """
        Inicializa los estilos copiándolos de celdas de ejemplo en la hoja de estilos.
        """
        self.styles = {
            "ST": copy(self.workbook["E3"].fill),
            "CR": copy(self.workbook["E4"].fill),
            "NC": copy(self.workbook["E5"].fill),
            "NA": copy(self.workbook["E6"].fill)
        }

    def style_cell(self, target_cell: Cell, kind: str):
        """
        Aplica un estilo a una celda objetivo.

        Args:
            target_cell (Cell): Celda a la que se le aplicará el estilo.
            kind (str): Tipo de estilo a aplicar ("ST": Suspensión de terminos , "CR": Cumple con lo requerido, "NC": No cumple con lo requerido, "NA": Documentos que no aplican).
        """
        target_cell.fill = self.styles.get(kind)


def write_data(data: SupervisionData, sheet: Worksheet):
    """
    Escribe los datos generales de supervisión en celdas específicas de una hoja de cálculo.

    Args:
        data (SupervisionData): Datos generales de la supervisión.
        sheet (Worksheet): Hoja de cálculo donde se escribirán los datos.
    """
    datafields = {
        'OIC': 'C11',
        'Numero': 'C15',
        'Nombre': 'C17',
        'Fecha': 'J11',
        'Clave': 'J15',
        'Anyo_Trimestre': 'J17',
        'Objetivo': 'E19',
        'Area': 'C21',
        'Ejercicio': 'J21'
    }
    for key, field in datafields.items():
        value = getattr(data, key)
        if value is not None:
            sheet[field] = value


def write_concepto(sheet: Worksheet, concepto: Concepto, cell_row: str, styles: Styles):
    semaforo_cell = f"H{cell_row}"
    if concepto.Estado == '0':
        estado_cell = f"F{cell_row}"
        sheet[estado_cell] = "r"
        styles.style_cell(target_cell=sheet[semaforo_cell], kind="NC")
    elif concepto.Estado == '1':
        estado_cell = f"E{cell_row}"
        sheet[estado_cell] = "a"
        styles.style_cell(target_cell=sheet[semaforo_cell], kind="CR")
    elif concepto.Estado == '2':
        styles.style_cell(target_cell=sheet[semaforo_cell], kind="ST")
    elif concepto.Estado == '3':
        styles.style_cell(target_cell=sheet[semaforo_cell], kind="NA")
    elif concepto.Estado == '4':
        pass

    if concepto.Comentario:
        observacion_cell = f"J{cell_row}"
        sheet[observacion_cell] = concepto.Comentario


def write_conceptos(conceptos: ConceptosLista, sheet: Worksheet, kind: str, styles: Styles):
    """
    Escribe los conceptos evaluados, los comentarios y sus estados en celdas específicas de una hoja de cálculo,
    aplicando estilos de acuerdo a su estado.

    Args:
        conceptos (List[Concepto]): Lista de conceptos.
        sheet (Worksheet): Hoja de cálculo donde se escribirán los conceptos.
        kind (str): Tipo de supervisión ("Auditoria", "Intervención", "Control interno").
        styles (Styles): Estilos a aplicar a las celdas.
    """
    mappings = {
        'Auditoria': {
            0: "30", 1: "31", 2: "32", 3: "33", 4: "37", 5: "38", 6: "39", 7: "40", 8: "41", 9: "42",
            10: "43", 11: "44", 12: "45", 13: "46", 14: "53", 15: "54", 16: "55", 17: "56", 18: "58",
            19: "59", 20: "60", 21: "61", 22: "62", 23: "63", 24: "65", 25: "66", 26: "67", 27: "69",
            28: "70", 29: "71", 30: "72", 31: "73", 32: "75", 33: "76", 34: "77", 35: "78", 36: "80",
            37: "81", 38: "82", 39: "83", 40: "84", 41: "86", 42: "87", 43: "88", 44: "89", 45: "90",
            46: "92", 47: "94", 48: "96", 49: "97", 50: "98", 51: "99", 52: "100", 53: "101", 54: "102",
            55: "103", 56: "107", 57: "111", 58: "113", 59: "115"
        },
        'Intervención': {
            0: "30", 1: "31", 2: "35", 3: "36", 4: "37", 5: "38", 6: "39", 7: "40", 8: "42", 9: "43",
            10: "44", 11: "46", 12: "47", 13: "48", 14: "49", 15: "50", 16: "52", 17: "53", 18: "54",
            19: "55", 20: "57", 21: "58", 22: "59", 23: "60", 24: "61", 25: "63", 26: "64", 27: "65",
            28: "66", 29: "67", 30: "69", 31: "73", 32: "74", 33: "75", 34: "76", 35: "77", 36: "78",
            37: "79", 38: "80", 39: "81", 40: "82", 41: "84", 42: "85", 43: "86", 44: "87", 45: "88",
            46: "89", 47: "90", 48: "91", 49: "93", 50: "97", 51: "99", 52: "101"
        },
        'Control interno': {
            0: "30", 1: "31", 2: "32", 3: "33", 4: "34", 5: "36", 6: "37", 7: "38", 8: "40", 9: "41",
            10: "42", 11: "43", 12: "44", 13: "45", 14: "46", 15: "47", 16: "48", 17: "49", 18: "53",
            19: "54", 20: "55", 21: "56", 22: "57", 23: "59", 24: "60", 25: "61", 26: "62", 27: "63",
            28: "67", 29: "68", 30: "69", 31: "70", 32: "71", 33: "73", 34: "74", 35: "75", 36: "76",
            37: "77", 38: "79", 39: "80", 40: "81", 41: "82", 42: "84", 43: "85", 44: "86", 45: "87",
            46: "89", 47: "90", 48: "91", 49: "92", 50: "94", 51: "98", 52: "99", 53: "100", 54: '102',
            55: '103', 56: '104', 57: '105', 58: '106', 59: '107', 60: '108', 61: '109', 62: '110',
            63: '111', 64: '112', 65: '113', 66: '114', 67: '115', 68: '116', 69: '120', 70: '122'
        }
    }

    mapping = mappings.get(kind, {})
    order = 0
    for idx, concepto in enumerate(conceptos.Conceptos):
        cell_row = mapping.get(idx + order)
        if cell_row:
            write_concepto(sheet=sheet, concepto=concepto, cell_row=cell_row, styles=styles)


def cedula(kind: int, data: SupervisionData, conceptos: ConceptosLista) -> Optional[str]:
    """
    Genera una hoja de cálculo de supervisión, rellenando datos generales y conceptos evaluados,
    y ocultando las hojas que no son relevantes.

    Args:
        kind (int): Tipo de supervisión (1: Auditoria, 2: Intervención, 3: Control interno).
        data (SupervisionData): Datos generales de la supervisión.
        conceptos (List[Concepto]): Lista de conceptos con estado y comentario.

    Returns:
        Optional[str]: Ruta del archivo generado.
    """

    # Obtén la ruta absoluta al directorio del script
    script_dir = os.path.dirname(__file__)

    # Construye la ruta relativa al archivo Excel
    rel_path = '../../media/templatedocs/supervision-plantilla.xlsx'
    abs_file_path = os.path.normpath(os.path.join(script_dir, rel_path))

    try:
        workbook = load_workbook(filename=abs_file_path)
    except FileNotFoundError:
        return None

    sheet_names = {
        1: 'Auditoria',
        2: 'Intervención',
        3: 'Control interno'
    }
    sheet_name = sheet_names.get(kind)
    if not sheet_name:
        return None

    sheet = workbook[sheet_name]

    write_data(data=data, sheet=sheet)

    estilos = Styles(workbook['styles'])

    write_conceptos(conceptos=conceptos, sheet=sheet, kind=sheet_name, styles=estilos)

    for sheet_kind, sheet_title in sheet_names.items():
        if sheet_kind != kind:
            workbook[sheet_title].sheet_state = "hidden"

    file_name = f"Supervision - {data.Numero} - {data.OIC} - {data.Anyo_Trimestre}.xlsx"
    file_name = file_name.replace('/', '_')
    output_dir = os.path.normpath(os.path.join(script_dir, '../../media/cedulas'))
    abs_output_path = os.path.join(output_dir, file_name)
    os.makedirs(os.path.dirname(abs_output_path), exist_ok=True)
    workbook.save(abs_output_path)

    return abs_output_path

