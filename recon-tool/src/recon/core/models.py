"""
Core Models - Data classes and enums for reconciliation
Modelos de datos y enumeraciones para la reconciliación
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class ValidationStatus(Enum):
    """
    Estados de validación para cada comparación.
    Principio de diseño: nunca asumir, siempre clasificar explícitamente.
    """
    MATCH = "MATCH"                         # Coincide exacto (o dentro de tolerancia configurada)
    MISMATCH = "MISMATCH"                   # Hay valor en ambos lados y no coincide
    MISSING_IN_PBI = "MISSING_IN_PBI"       # Existe en source, no existe en PBI-model
    MISSING_IN_SOURCE = "MISSING_IN_SOURCE" # Existe en PBI-model, no existe en source
    NOT_VERIFIABLE = "NOT_VERIFIABLE"       # No hay datos suficientes para comparar
    RULE_NOT_DEFINED = "RULE_NOT_DEFINED"   # No existe mapeo/regla para ese campo/servicio


class Severity(Enum):
    """Niveles de severidad para hallazgos"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ValidationResult:
    """Resultado de una validación individual"""
    status: ValidationStatus
    field_name: str
    source_value: Any
    pbi_value: Any
    message: str
    severity: Severity = Severity.INFO
    tolerance_used: Optional[float] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "field_name": self.field_name,
            "source_value": self.source_value,
            "pbi_value": self.pbi_value,
            "message": self.message,
            "severity": self.severity.value,
            "tolerance_used": self.tolerance_used,
            "metadata": self.metadata
        }


@dataclass
class EntityComparison:
    """Comparación de una entidad específica (ej: Site 146, Verizon, Broadband)"""
    entity_type: str  # "site", "vendor", "service_type"
    entity_id: str
    entity_filters: dict  # {"site_id": "146", "vendor": "Verizon", "service_type": "Broadband"}
    validations: list[ValidationResult] = field(default_factory=list)
    
    @property
    def match_count(self) -> int:
        return sum(1 for v in self.validations if v.status == ValidationStatus.MATCH)
    
    @property
    def mismatch_count(self) -> int:
        return sum(1 for v in self.validations if v.status == ValidationStatus.MISMATCH)
    
    @property
    def not_verifiable_count(self) -> int:
        return sum(1 for v in self.validations if v.status == ValidationStatus.NOT_VERIFIABLE)

    def to_dict(self) -> dict:
        return {
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "entity_filters": self.entity_filters,
            "summary": {
                "total": len(self.validations),
                "match": self.match_count,
                "mismatch": self.mismatch_count,
                "not_verifiable": self.not_verifiable_count
            },
            "validations": [v.to_dict() for v in self.validations]
        }


@dataclass
class IntegrityCheckResult:
    """Resultado de verificación de integridad referencial"""
    check_name: str
    source_table: str
    target_table: str
    source_key: str
    target_key: str
    status: ValidationStatus
    total_source_keys: int
    matched_keys: int
    missing_in_target: int
    orphan_keys: list[str] = field(default_factory=list)  # Muestra de claves huérfanas
    severity: Severity = Severity.WARNING
    
    @property
    def match_percentage(self) -> float:
        if self.total_source_keys == 0:
            return 0.0
        return (self.matched_keys / self.total_source_keys) * 100

    def to_dict(self) -> dict:
        return {
            "check_name": self.check_name,
            "source_table": self.source_table,
            "target_table": self.target_table,
            "source_key": self.source_key,
            "target_key": self.target_key,
            "status": self.status.value,
            "total_source_keys": self.total_source_keys,
            "matched_keys": self.matched_keys,
            "missing_in_target": self.missing_in_target,
            "match_percentage": round(self.match_percentage, 2),
            "orphan_keys_sample": self.orphan_keys[:10],
            "severity": self.severity.value
        }


@dataclass
class DataQualityMetric:
    """Métrica de calidad de datos para una tabla"""
    table_name: str
    total_rows: int
    total_columns: int
    duplicate_rows: int
    null_counts: dict[str, int]  # {column_name: null_count}
    
    def to_dict(self) -> dict:
        return {
            "table_name": self.table_name,
            "total_rows": self.total_rows,
            "total_columns": self.total_columns,
            "duplicate_rows": self.duplicate_rows,
            "duplicate_percentage": round((self.duplicate_rows / self.total_rows) * 100, 2) if self.total_rows > 0 else 0,
            "null_counts": self.null_counts
        }


@dataclass
class ReconciliationReport:
    """Reporte completo de reconciliación"""
    project_name: str
    generated_at: datetime
    config_file: str
    
    # Resultados
    integrity_checks: list[IntegrityCheckResult] = field(default_factory=list)
    data_quality: list[DataQualityMetric] = field(default_factory=list)
    entity_comparisons: list[EntityComparison] = field(default_factory=list)
    
    # Metadatos
    sources_loaded: dict[str, int] = field(default_factory=dict)  # {source_name: row_count}
    execution_time_seconds: float = 0.0
    filters_applied: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "project_name": self.project_name,
            "generated_at": self.generated_at.isoformat(),
            "config_file": self.config_file,
            "execution_time_seconds": self.execution_time_seconds,
            "sources_loaded": self.sources_loaded,
            "filters_applied": self.filters_applied,
            "summary": {
                "integrity_checks": len(self.integrity_checks),
                "integrity_passed": sum(1 for c in self.integrity_checks if c.status == ValidationStatus.MATCH),
                "data_quality_tables": len(self.data_quality),
                "entity_comparisons": len(self.entity_comparisons)
            },
            "integrity_checks": [c.to_dict() for c in self.integrity_checks],
            "data_quality": [d.to_dict() for d in self.data_quality],
            "entity_comparisons": [e.to_dict() for e in self.entity_comparisons]
        }
