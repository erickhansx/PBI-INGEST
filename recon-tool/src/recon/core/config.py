"""
Configuration Manager - Loads and validates YAML project configs
Maneja la carga y validación de configuraciones YAML por proyecto
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class SourceConfig:
    """Configuración de una fuente de datos"""
    name: str
    path: str
    type: str  # csv, excel, parquet
    encoding: str = "utf-8"
    delimiter: str = ","
    key_columns: list[str] = field(default_factory=list)
    
    def resolve_path(self, base_path: Path) -> Path:
        """Resuelve la ruta relativa a la base del proyecto"""
        if os.path.isabs(self.path):
            return Path(self.path)
        return base_path / self.path


@dataclass
class FieldMapping:
    """Mapeo de un campo entre source y PBI"""
    source_field: str
    pbi_field: str
    transform: Optional[str] = None  # Transformación opcional
    tolerance: Optional[float] = None  # Para comparación numérica
    compare_type: str = "exact"  # exact, numeric, substring, regex


@dataclass
class ValidationRule:
    """Regla de validación para un tipo de servicio/entidad"""
    service_type: str
    source_name: str  # Qué source usar como referencia
    field_mappings: list[FieldMapping] = field(default_factory=list)
    
    # Filtros para aplicar al extraer datos
    source_filters: dict[str, Any] = field(default_factory=dict)
    pbi_filters: dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrityCheck:
    """Configuración de verificación de integridad referencial"""
    name: str
    source_table: str
    target_table: str
    source_key: str
    target_key: str
    severity: str = "WARNING"


@dataclass
class ProjectConfig:
    """Configuración completa de un proyecto de reconciliación"""
    name: str
    description: str
    version: str
    
    # Rutas
    sources_base_path: str
    pbi_model_path: str
    reports_output_path: str
    
    # Fuentes de datos
    sources: dict[str, SourceConfig] = field(default_factory=dict)
    
    # Reglas de validación
    validation_rules: dict[str, ValidationRule] = field(default_factory=dict)
    
    # Verificaciones de integridad
    integrity_checks: list[IntegrityCheck] = field(default_factory=list)
    
    # Configuración global
    default_encoding: str = "utf-8"
    numeric_tolerance: float = 0.01
    
    @property
    def base_path(self) -> Path:
        return Path(self.sources_base_path)


class ConfigurationError(Exception):
    """Error en la configuración del proyecto"""
    pass


class ConfigLoader:
    """Cargador de configuraciones de proyecto"""
    
    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise ConfigurationError(f"Config file not found: {config_path}")
    
    def load(self) -> ProjectConfig:
        """Carga y valida la configuración del proyecto"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            raw_config = yaml.safe_load(f)
        
        return self._parse_config(raw_config)
    
    def _parse_config(self, raw: dict) -> ProjectConfig:
        """Parsea el diccionario YAML a objetos de configuración"""
        
        # Metadatos del proyecto
        project = raw.get('project', {})
        
        # Cargar fuentes
        sources = {}
        for name, src_config in raw.get('sources', {}).items():
            sources[name] = SourceConfig(
                name=name,
                path=src_config.get('path', ''),
                type=src_config.get('type', 'csv'),
                encoding=src_config.get('encoding', 'utf-8'),
                delimiter=src_config.get('delimiter', ','),
                key_columns=src_config.get('key_columns', [])
            )
        
        # Cargar reglas de validación
        validation_rules = {}
        for service_type, rule_config in raw.get('validation_rules', {}).items():
            mappings = []
            for mapping in rule_config.get('field_mappings', []):
                mappings.append(FieldMapping(
                    source_field=mapping.get('source_field', ''),
                    pbi_field=mapping.get('pbi_field', ''),
                    transform=mapping.get('transform'),
                    tolerance=mapping.get('tolerance'),
                    compare_type=mapping.get('compare_type', 'exact')
                ))
            
            validation_rules[service_type] = ValidationRule(
                service_type=service_type,
                source_name=rule_config.get('source_name', ''),
                field_mappings=mappings,
                source_filters=rule_config.get('source_filters', {}),
                pbi_filters=rule_config.get('pbi_filters', {})
            )
        
        # Cargar verificaciones de integridad
        integrity_checks = []
        for check in raw.get('integrity_checks', []):
            integrity_checks.append(IntegrityCheck(
                name=check.get('name', ''),
                source_table=check.get('source_table', ''),
                target_table=check.get('target_table', ''),
                source_key=check.get('source_key', ''),
                target_key=check.get('target_key', ''),
                severity=check.get('severity', 'WARNING')
            ))
        
        return ProjectConfig(
            name=project.get('name', 'unknown'),
            description=project.get('description', ''),
            version=project.get('version', '0.1.0'),
            sources_base_path=raw.get('paths', {}).get('sources_base', '.'),
            pbi_model_path=raw.get('paths', {}).get('pbi_model', ''),
            reports_output_path=raw.get('paths', {}).get('reports_output', './reports'),
            sources=sources,
            validation_rules=validation_rules,
            integrity_checks=integrity_checks,
            default_encoding=raw.get('settings', {}).get('default_encoding', 'utf-8'),
            numeric_tolerance=raw.get('settings', {}).get('numeric_tolerance', 0.01)
        )
    
    @staticmethod
    def get_available_projects(configs_dir: str | Path) -> list[str]:
        """Lista los proyectos disponibles en el directorio de configs"""
        configs_path = Path(configs_dir)
        if not configs_path.exists():
            return []
        
        return [p.stem for p in configs_path.glob('*.yaml')]
