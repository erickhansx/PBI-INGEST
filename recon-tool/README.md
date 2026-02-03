# 🔍 Recon Tool

Herramienta de reconciliación automática para validar datos de Power BI contra fuentes de datos.

## 📋 Descripción

**Recon Tool** automatiza el proceso de validación y reconciliación de datos entre:

- Archivos CSV fuente (SharePoint, exports, etc.)
- Tablas de hechos y dimensiones de Power BI
- Configuración del reporte PBI (Layout)

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
│   ├── mvh.yaml
│   └── another_project.yaml
├── src/recon/              # Código fuente
│   ├── cli.py              # Interfaz de línea de comandos
│   ├── core/               # Lógica principal
│   │   ├── ingest.py       # Carga de datos
│   │   ├── normalize.py    # Normalización de datos
│   │   ├── rules.py        # Motor de reglas
│   │   └── validators/     # Validadores específicos
│   │       ├── referential.py
│   │       ├── nulls.py
│   │       ├── duplicates.py
│   │       └── entity_compare.py
│   ├── adapters/           # Adaptadores de datos
│   │   ├── pbi_layout.py
│   │   ├── csv_model.py
│   │   └── powerbi_dataset.py
│   └── reporting/          # Generación de reportes
│       ├── markdown.py
│       ├── jsonout.py
│       └── artifacts.py
├── tests/                  # Pruebas unitarias
│   ├── test_rules.py
│   └── test_entity_compare.py
└── examples/               # Scripts de ejemplo
    ├── run_general.sh
    └── run_site_146.sh
```

## 🛠️ Instalación

```bash
# Clonar el repositorio
cd recon-tool

# Instalar en modo desarrollo
pip install -e ".[dev]"
```

## 📖 Uso

### Comando básico

```bash
# Ejecutar reconciliación con archivo de configuración
recon run --config configs/mvh.yaml

# Analizar un site específico
recon analyze --config configs/mvh.yaml --site-id 146 --vendor Verizon

# Generar reporte completo
recon report --config configs/mvh.yaml --output reports/
```

### Configuración (YAML)

```yaml
project:
  name: 'MVH Broadband DIA'
  version: '1.0'

sources:
  fact_quotes:
    path: 'data/factQuotes.csv'
    key: 'Site_Location_Key'

  dim_site:
    path: 'data/dimSite.csv'
    key: 'Site_Location_Key'

  sharepoint_arch1:
    path: 'data/Broadband DIA_Archetype 1_sharepoint.csv'
    key: 'Site_Location_Key'

validations:
  referential_integrity:
    - source: fact_quotes
      target: dim_site
      key: Site_Location_Key

  required_fields:
    fact_quotes:
      - Total MRC
      - Vendor
      - Service_Type

  allowed_values:
    Service_Type: ['DIA', 'Broadband', 'LTE', 'CPE']
```

## 🧪 Testing

```bash
# Ejecutar todas las pruebas
pytest

# Con cobertura
pytest --cov=src/recon --cov-report=html
```

## 📊 Ejemplo de Salida

```
================================================================================
RECON TOOL - Reconciliation Report
================================================================================

📁 Project: MVH Broadband DIA
📅 Date: 2026-02-02

✅ PASSED VALIDATIONS
---------------------
• Referential Integrity: dim_site ↔ fact_existing_costs
• Duplicate Check: dim_site (primary key unique)

⚠️ WARNINGS
-----------
• 1,955 Site_Location_Keys in fact_quotes missing from dim_site
• Service Types CPE, LTE not in dim_service_type

❌ FAILED VALIDATIONS
---------------------
• None

📋 RECOMMENDATIONS
------------------
1. Add missing Site_Location_Keys to dim_site
2. Update dim_service_type to include CPE and LTE
```

## 📝 Licencia

MIT License
