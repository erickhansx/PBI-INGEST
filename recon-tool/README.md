# 🔍 Recon Tool

Herramienta de reconciliación automática para validar datos de Power BI contra fuentes de datos.

## 📋 Descripción

**Recon Tool** automatiza el proceso de validación y reconciliación de datos entre:

- Archivos CSV fuente (SharePoint, exports, etc.)
- Tablas de hechos y dimensiones de Power BI
- Configuración del reporte PBI (Layout)

## 🎯 Principios de Diseño

La herramienta opera con estados **explícitos** para cada validación:

| Estado | Significado |
|--------|-------------|
| ✅ **MATCH** | Datos coinciden exactamente (o dentro de tolerancia configurada) |
| ❌ **MISMATCH** | Hay valor en ambos lados y NO coinciden |
| ⚠️ **MISSING_IN_PBI** | Existe en source original, NO existe en modelo PBI |
| ⚠️ **MISSING_IN_SOURCE** | Existe en modelo PBI, NO existe en source original |
| 🔵 **NOT_VERIFIABLE** | No hay datos suficientes para realizar la comparación |
| 🟣 **RULE_NOT_DEFINED** | No existe regla/mapeo configurado para ese campo |

> **Principio fundamental:** La herramienta NUNCA asume ni infiere.  
> Si no puede verificar, clasifica como `NOT_VERIFIABLE` o `RULE_NOT_DEFINED`.  
> *Nunca "podría ser..." o "probablemente..."*

## 🚀 Características

- ✅ Validación de integridad referencial
- ✅ Detección de valores nulos críticos
- ✅ Identificación de duplicados
- ✅ Comparación entidad por entidad
- ✅ Reportes en Markdown y JSON
- ✅ Configuración por proyecto (YAML)
- ✅ CLI intuitivo

## 📁 Estructura del Proyecto

```
recon-tool/
├── pyproject.toml          # Configuración del proyecto
├── README.md               # Este archivo
├── configs/                # Archivos de configuración por proyecto
│   └── mvh.yaml
├── src/recon/              # Código fuente
│   ├── __init__.py
│   ├── cli.py              # Interfaz de línea de comandos
│   ├── core/               # Lógica principal
│   │   ├── __init__.py
│   │   ├── models.py       # Modelos de datos y ValidationStatus
│   │   └── config.py       # Cargador de configuración
│   ├── adapters/           # Adaptadores de datos (placeholder)
│   │   └── __init__.py
│   ├── validators/         # Validadores específicos (placeholder)
│   │   └── __init__.py
│   └── reporting/          # Generación de reportes
│       ├── __init__.py
│       ├── markdown_reporter.py
│       └── json_reporter.py
├── tests/                  # Pruebas
│   └── test_sprint0.py
└── reports/                # Reportes generados (gitignore)
```

## 🛠️ Instalación

```bash
# Clonar el repositorio
git clone <repo-url>
cd recon-tool

# Instalar en modo desarrollo
pip install -e .

# O instalar dependencias directamente
pip install click pyyaml rich tabulate pandas
```

## 📖 Uso

### Comandos CLI

```bash
# Ver ayuda
recon --help

# Ver leyenda de estados de validación
recon status-legend

# Listar proyectos disponibles
recon list-projects

# Validar configuración de un proyecto
recon validate-config --project mvh

# Ejecutar reconciliación completa
recon run --project mvh

# Ejecutar con filtros específicos
recon run --project mvh --site 146 --vendor Verizon

# Generar reportes Markdown y JSON
recon run --project mvh --output all --output-dir ./reports
```

### Ejemplo: Validar Site 146 con Verizon

```bash
# Ejecutar reconciliación con filtros
recon run --project mvh --site 146 --vendor Verizon --output markdown

# Resultado: genera recon_mvh_site146_Verizon_YYYYMMDD_HHMMSS.md
```

## ⚙️ Configuración

Cada proyecto se configura en un archivo YAML en `configs/`:

```yaml
# configs/mvh.yaml
project:
  name: 'mvh'
  version: '1.0.0'
  description: 'MVH Broadband DIA Reconciliation'

paths:
  sources_base: '/path/to/data'
  pbi_model: '/path/to/pbix_unpacked'
  reports_output: './reports'

sources:
  fact_quotes:
    path: 'factQuotes.csv'
    type: 'csv'
    key_columns: ['Site_Location_Key', 'Service_Type', 'Vendor']

validation_rules:
  Broadband:
    source_name: 'sharepoint_arch1'
    field_mappings:
      - source_field: 'Broadband Circuit MRC $/Month'
        pbi_field: 'Total MRC'
        compare_type: 'numeric'
        tolerance: 0.01
```

## 🧪 Testing

```bash
# Ejecutar pruebas del Sprint 0
PYTHONPATH=./src python tests/test_sprint0.py
```

## 📅 Roadmap

### Sprint 0 (Actual) ✅
- [x] CLI skeleton con click
- [x] Modelos de datos con ValidationStatus enum
- [x] Cargador de configuración YAML
- [x] Generador de reportes Markdown
- [x] Generador de reportes JSON
- [x] Tests básicos

### Sprint 1 (Siguiente)
- [ ] Data Ingest: carga de CSVs con pandas
- [ ] Integrity Validators: referential checks
- [ ] Entity Comparison Engine
- [ ] Integración end-to-end

### Sprint 2
- [ ] PBI Layout parser
- [ ] Advanced field mapping
- [ ] Tolerance comparisons
- [ ] Bulk validation reports

## 📄 Licencia

MIT

---

*Generado como parte del proyecto MVH Broadband DIA Reconciliation*
