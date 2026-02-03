"""
Core Module - Main business logic for reconciliation
Modelos, configuración y lógica principal
"""

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
    ProjectConfig,
    SourceConfig,
    FieldMapping,
    ValidationRule,
    IntegrityCheck
)

__all__ = [
    # Models
    'ValidationStatus',
    'Severity',
    'ValidationResult',
    'EntityComparison',
    'IntegrityCheckResult',
    'DataQualityMetric',
    'ReconciliationReport',
    # Config
    'ConfigLoader',
    'ConfigurationError',
    'ProjectConfig',
    'SourceConfig',
    'FieldMapping',
    'ValidationRule',
    'IntegrityCheck'
]
