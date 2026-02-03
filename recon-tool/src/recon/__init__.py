"""
Recon Tool - PBI Data Reconciliation Package
Herramienta para validar datos de Power BI contra fuentes originales.

Design Principles:
- MATCH: Datos coinciden exactamente (o dentro de tolerancia configurada)
- MISMATCH: Hay valor en ambos lados y NO coinciden
- MISSING_IN_PBI: Existe en source original, NO existe en modelo PBI
- MISSING_IN_SOURCE: Existe en modelo PBI, NO existe en source original  
- NOT_VERIFIABLE: No hay datos suficientes para realizar la comparación
- RULE_NOT_DEFINED: No existe regla/mapeo configurado para ese campo

Nunca asumir. Nunca "podría ser...". Siempre clasificar explícitamente.
"""

__version__ = "0.1.0"

from recon.core.models import (
    ValidationStatus,
    Severity,
    ValidationResult,
    EntityComparison,
    IntegrityCheckResult,
    DataQualityMetric,
    ReconciliationReport
)

from recon.core.config import (
    ConfigLoader,
    ConfigurationError,
    ProjectConfig
)

__all__ = [
    '__version__',
    'ValidationStatus',
    'Severity',
    'ValidationResult',
    'EntityComparison',
    'IntegrityCheckResult',
    'DataQualityMetric', 
    'ReconciliationReport',
    'ConfigLoader',
    'ConfigurationError',
    'ProjectConfig'
]
