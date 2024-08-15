# Cobertura de Tests

Este documento proporciona un resumen de la cobertura de los tests en el proyecto. La cobertura de código es una métrica importante que mide qué parte del código ha sido ejecutada durante la ejecución de los tests. Mantener una alta cobertura ayuda a asegurar la calidad y fiabilidad del software.

A continuación, se presenta un resumen de la última lectura de cobertura de los tests. Si deseas comprobar la cobertura por ti mismo, puedes seguir las instrucciones en la sección [Ejecutar Reporte de Cobertura](#ejecutar-reporte-de-cobertura).

## Reporte de Cobertura

| Nombre                                                                                  | Declaraciones | Faltantes | Cobertura |
|-----------------------------------------------------------------------------------------|---------------|-----------|-----------|
| OICSec\__init__.py                                                                      | 0             | 0         | 100%      |
| OICSec\admin.py                                                                         | 1             | 0         | 100%      |
| OICSec\apps.py                                                                          | 6             | 0         | 100%      |
| OICSec\forms.py                                                                         | 61            | 0         | 100%      |
| OICSec\funcs\Actividad.py                                                               | 27            | 24        | 11%       |
| OICSec\funcs\Cedula.py                                                                  | 90            | 56        | 38%       |
| OICSec\funcs\Minuta.py                                                                  | 114           | 83        | 27%       |
| OICSec\funcs\PAA.py                                                                     | 80            | 66        | 18%       |
| OICSec\funcs\PACI.py                                                                    | 72            | 59        | 18%       |
| OICSec\funcs\PINT.py                                                                    | 113           | 98        | 13%       |
| OICSec\funcs\__init__.py                                                                | 0             | 0         | 100%      |
| OICSec\migrations\0001_initial.py                                                       | 6             | 0         | 100%      |
| OICSec\migrations\0002_sectorrevision_controlinterno_id_sector_revision.py              | 5             | 0         | 100%      |
| OICSec\migrations\0003_alter_sectorrevision_clave_alter_tiporevision_clave.py           | 4             | 0         | 100%      |
| OICSec\migrations\0004_alter_sectorrevision_tipo.py                                     | 4             | 0         | 100%      |
| OICSec\migrations\0005_rename_sectorrevision_programarevision_and_more.py               | 4             | 0         | 100%      |
| OICSec\migrations\0006_rename_rubro_controlinterno_area_and_more.py                     | 4             | 0         | 100%      |
| OICSec\migrations\0007_alter_programarevision_clave_and_more.py                         | 4             | 0         | 100%      |
| OICSec\migrations\0008_alter_tiporevision_clave_alter_tiporevision_tipo.py              | 4             | 0         | 100%      |
| OICSec\migrations\0009_rename_id_sector_revision_controlinterno_id_programa_revision.py | 4             | 0         | 100%      |
| OICSec\migrations\0010_remove_intervencion_rubro_intervencion_alcance_and_more.py       | 4             | 0         | 100%      |
| OICSec\migrations\0011_remove_intervencion_rubro_alter_intervencion_alcance_and_more.py | 4             | 0         | 100%      |
| OICSec\migrations\0012_tipocedula_cedula_id_archivo_cedula_id_tipo_cedula.py            | 5             | 0         | 100%      |
| OICSec\migrations\0013_remove_cedula_id_tipo_cedula.py                                  | 4             | 0         | 100%      |
| OICSec\migrations\0014_delete_tipocedula.py                                             | 4             | 0         | 100%      |
| OICSec\migrations\0015_cedulaauditoria_cedulacontrolinterno_and_more.py                 | 5             | 0         | 100%      |
| OICSec\migrations\0016_cedula_fecha.py                                                  | 4             | 0         | 100%      |
| OICSec\migrations\0017_remove_cedula_fecha_and_more.py                                  | 5             | 0         | 100%      |
| OICSec\migrations\0018_alter_archivo_archivo.py                                         | 4             | 0         | 100%      |
| OICSec\migrations\0019_alter_archivo_nombre.py                                          | 4             | 0         | 100%      |
| OICSec\migrations\0020_remove_cedulacontrolinterno_id_cedula_and_more.py                | 4             | 0         | 100%      |
| OICSec\migrations\0021_persona_estado.py                                                | 4             | 0         | 100%      |
| OICSec\migrations\0022_alter_persona_estado_alter_persona_sexo.py                       | 4             | 0         | 100%      |
| OICSec\migrations\0023_alter_persona_estado.py                                          | 4             | 0         | 100%      |
| OICSec\migrations\0024_delete_persona.py                                                | 4             | 0         | 100%      |
| OICSec\migrations\0025_persona_tipocargo_personal_cargopersonal.py                      | 5             | 0         | 100%      |
| OICSec\migrations\0026_minuta_tipo_concepto.py                                          | 4             | 0         | 100%      |
| OICSec\migrations\0027_remove_minuta_tipo_concepto_and_more.py                          | 4             | 0         | 100%      |
| OICSec\migrations\0028_minuta_mes.py                                                    | 4             | 0         | 100%      |
| OICSec\migrations\0029_minutapersonal.py                                                | 5             | 0         | 100%      |
| OICSec\migrations\0030_alter_minuta_fin_alter_minuta_inicio.py                          | 4             | 0         | 100%      |
| OICSec\migrations\0031_delete_cargo_alter_conceptominuta_tipo_concepto.py               | 4             | 0         | 100%      |
| OICSec\migrations\0032_alter_intervencion_id_actividad_fiscalizacion.py                 | 5             | 0         | 100%      |
| OICSec\migrations\__init__.py                                                           | 0             | 0         | 100%      |
| OICSec\models.py                                                                        | 287           | 16        | 94%       |
| OICSec\signals.py                                                                       | 40            | 30        | 25%       |
| OICSec\tests.py                                                                         | 176           | 0         | 100%      |
| OICSec\urls.py                                                                          | 3             | 0         | 100%      |
| OICSec\views.py                                                                         | 824           | 633       | 23%       |
| ProyectoSCG\__init__.py                                                                 | 0             | 0         | 100%      |
| ProyectoSCG\asgi.py                                                                     | 4             | 4         | 0%        |
| ProyectoSCG\settings.py                                                                 | 24            | 0         | 100%      |
| ProyectoSCG\urls.py                                                                     | 4             | 0         | 100%      |
| ProyectoSCG\wsgi.py                                                                     | 4             | 4         | 0%        |
| manage.py                                                                               | 11            | 2         | 82%       |
| **TOTAL**                                                                               | **2078**      | **1075**  | **48%**   |

## Ejecutar Reporte de Cobertura

Para medir la cobertura de código y generar un reporte, usa los siguientes comandos:

```bash
coverage run --source='.' manage.py test

coverage report -m

coverage html
```

###### Explicación de los comandos
- `coverage run --source='.' manage.py test`: Ejecuta los tests del proyecto y mide la cobertura de código.
- `coverage report -m`: Muestra un resumen de la cobertura en la consola, indicando qué líneas no fueron cubiertas.
- `coverage html`: Genera un reporte en HTML que puedes abrir en un navegador para una visualización más detallada de la cobertura.

> Nota: Después de ejecutar el comando coverage html, abre el archivo htmlcov/index.html en tu navegador para ver el reporte de cobertura.