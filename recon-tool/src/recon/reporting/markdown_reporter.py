"""
Markdown Reporter - Generates detailed Markdown reports
Genera reportes detallados en formato Markdown
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from recon.core.models import (
    ReconciliationReport,
    ValidationStatus,
    Severity,
    EntityComparison,
    IntegrityCheckResult,
    ValidationResult
)


class MarkdownReporter:
    """Generador de reportes en formato Markdown"""
    
    STATUS_EMOJI = {
        ValidationStatus.MATCH: "✅",
        ValidationStatus.MISMATCH: "❌",
        ValidationStatus.MISSING_IN_PBI: "⚠️",
        ValidationStatus.MISSING_IN_SOURCE: "⚠️",
        ValidationStatus.NOT_VERIFIABLE: "🔵",
        ValidationStatus.RULE_NOT_DEFINED: "🟣"
    }
    
    SEVERITY_EMOJI = {
        Severity.INFO: "ℹ️",
        Severity.WARNING: "⚠️",
        Severity.ERROR: "❌",
        Severity.CRITICAL: "🔴"
    }
    
    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, report: ReconciliationReport, 
                 filters: Optional[dict] = None) -> Path:
        """Genera el reporte Markdown y lo guarda en un archivo"""
        
        content = self._build_content(report, filters)
        
        # Nombre del archivo basado en timestamp y filtros
        timestamp = report.generated_at.strftime("%Y%m%d_%H%M%S")
        filter_suffix = ""
        if filters:
            if filters.get('site_id'):
                filter_suffix += f"_site{filters['site_id']}"
            if filters.get('vendor'):
                filter_suffix += f"_{filters['vendor']}"
        
        filename = f"recon_{report.project_name}{filter_suffix}_{timestamp}.md"
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
    
    def _build_content(self, report: ReconciliationReport, 
                       filters: Optional[dict] = None) -> str:
        """Construye el contenido completo del reporte"""
        
        sections = [
            self._header(report),
            self._status_legend(),
            self._filters_section(filters),
            self._sources_section(report),
            self._integrity_section(report),
            self._entity_comparisons_section(report),
            self._summary_section(report),
            self._footer(report)
        ]
        
        return "\n\n".join(filter(None, sections))
    
    def _header(self, report: ReconciliationReport) -> str:
        """Genera el encabezado del reporte"""
        return f"""# 🔍 Reporte de Reconciliación

**Proyecto:** {report.project_name}  
**Generado:** {report.generated_at.strftime("%Y-%m-%d %H:%M:%S")}  
**Config:** `{report.config_file}`  
**Tiempo de ejecución:** {report.execution_time_seconds:.2f}s

---"""

    def _status_legend(self) -> str:
        """Genera la leyenda de estados"""
        return """## 📋 Leyenda de Estados

| Estado | Símbolo | Significado |
|--------|---------|-------------|
| MATCH | ✅ | Datos coinciden exactamente (o dentro de tolerancia configurada) |
| MISMATCH | ❌ | Hay valor en ambos lados y NO coinciden |
| MISSING_IN_PBI | ⚠️ | Existe en source original, NO existe en modelo PBI |
| MISSING_IN_SOURCE | ⚠️ | Existe en modelo PBI, NO existe en source original |
| NOT_VERIFIABLE | 🔵 | No hay datos suficientes para realizar la comparación |
| RULE_NOT_DEFINED | 🟣 | No existe regla/mapeo configurado para ese campo |

> **Principio de diseño:** La herramienta NUNCA asume ni infiere.  
> Si no puede verificar, clasifica como `NOT_VERIFIABLE` o `RULE_NOT_DEFINED`.  
> *Nunca "podría ser..." o "probablemente..."*

---"""

    def _filters_section(self, filters: Optional[dict]) -> str:
        """Genera la sección de filtros aplicados"""
        if not filters:
            return ""
        
        filter_lines = []
        for key, value in filters.items():
            filter_lines.append(f"- **{key}:** `{value}`")
        
        return f"""## 🔍 Filtros Aplicados

{chr(10).join(filter_lines)}

---"""

    def _sources_section(self, report: ReconciliationReport) -> str:
        """Genera la sección de fuentes cargadas"""
        if not report.sources_loaded:
            return """## 📁 Fuentes de Datos

*No se cargaron fuentes (Sprint 0 skeleton)*

---"""
        
        rows = []
        for source_name, row_count in report.sources_loaded.items():
            rows.append(f"| {source_name} | {row_count:,} |")
        
        return f"""## 📁 Fuentes de Datos Cargadas

| Fuente | Registros |
|--------|-----------|
{chr(10).join(rows)}

---"""

    def _integrity_section(self, report: ReconciliationReport) -> str:
        """Genera la sección de verificaciones de integridad"""
        if not report.integrity_checks:
            return """## 🔗 Verificaciones de Integridad

*No hay verificaciones de integridad configuradas o ejecutadas*

---"""
        
        rows = []
        for check in report.integrity_checks:
            emoji = self.STATUS_EMOJI.get(check.status, "❓")
            rows.append(
                f"| {emoji} {check.check_name} | {check.source_table} → {check.target_table} | "
                f"{check.match_percentage:.1f}% | {check.missing_in_target:,} |"
            )
        
        return f"""## 🔗 Verificaciones de Integridad

| Check | Tablas | Match % | Faltantes |
|-------|--------|---------|-----------|
{chr(10).join(rows)}

---"""

    def _entity_comparisons_section(self, report: ReconciliationReport) -> str:
        """Genera la sección de comparaciones de entidades"""
        if not report.entity_comparisons:
            return """## 📊 Comparaciones de Entidades

*No hay comparaciones de entidades ejecutadas*

---"""
        
        sections = []
        for entity in report.entity_comparisons:
            sections.append(self._entity_detail(entity))
        
        return f"""## 📊 Comparaciones de Entidades

{chr(10).join(sections)}

---"""

    def _entity_detail(self, entity: EntityComparison) -> str:
        """Genera el detalle de una comparación de entidad"""
        
        # Encabezado de la entidad
        filter_str = ", ".join(f"{k}={v}" for k, v in entity.entity_filters.items())
        header = f"### {entity.entity_type}: {entity.entity_id}\n\n**Filtros:** {filter_str}\n"
        
        # Tabla de resumen
        summary = f"""
**Resumen:** {entity.match_count} ✅ | {entity.mismatch_count} ❌ | {entity.not_verifiable_count} 🔵

| Campo | Source | PBI | Estado | Mensaje |
|-------|--------|-----|--------|---------|"""
        
        # Filas de validaciones
        rows = []
        for v in entity.validations:
            emoji = self.STATUS_EMOJI.get(v.status, "❓")
            source_val = str(v.source_value) if v.source_value is not None else "*N/A*"
            pbi_val = str(v.pbi_value) if v.pbi_value is not None else "*N/A*"
            rows.append(f"| {v.field_name} | {source_val} | {pbi_val} | {emoji} {v.status.value} | {v.message} |")
        
        return header + summary + "\n" + "\n".join(rows)

    def _summary_section(self, report: ReconciliationReport) -> str:
        """Genera el resumen ejecutivo"""
        
        total_validations = sum(
            len(e.validations) for e in report.entity_comparisons
        )
        total_match = sum(e.match_count for e in report.entity_comparisons)
        total_mismatch = sum(e.mismatch_count for e in report.entity_comparisons)
        total_not_verifiable = sum(e.not_verifiable_count for e in report.entity_comparisons)
        
        integrity_passed = sum(
            1 for c in report.integrity_checks if c.status == ValidationStatus.MATCH
        )
        
        return f"""## 📈 Resumen Ejecutivo

### Validaciones de Campos
- **Total validaciones:** {total_validations}
- **Coincidencias (MATCH):** {total_match} ✅
- **Discrepancias (MISMATCH):** {total_mismatch} ❌
- **No verificables:** {total_not_verifiable} 🔵

### Integridad Referencial
- **Checks ejecutados:** {len(report.integrity_checks)}
- **Checks pasados:** {integrity_passed}

---"""

    def _footer(self, report: ReconciliationReport) -> str:
        """Genera el pie del reporte"""
        return f"""---

*Generado automáticamente por Recon Tool v0.1.0*  
*{report.generated_at.strftime("%Y-%m-%d %H:%M:%S")}*"""
