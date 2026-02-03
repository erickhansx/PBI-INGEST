"""
JSON Reporter - Generates machine-readable JSON reports
Genera reportes en formato JSON para integración con otros sistemas
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from recon.core.models import ReconciliationReport


class JsonReporter:
    """Generador de reportes en formato JSON"""
    
    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, report: ReconciliationReport, 
                 filters: Optional[dict] = None,
                 pretty: bool = True) -> Path:
        """
        Genera el reporte JSON y lo guarda en un archivo.
        
        Args:
            report: El reporte de reconciliación
            filters: Filtros aplicados (para el nombre del archivo)
            pretty: Si True, formatea el JSON con indentación
            
        Returns:
            Path al archivo generado
        """
        
        # Construir el diccionario completo
        output_data = report.to_dict()
        
        # Agregar metadatos del reporte
        output_data['_meta'] = {
            'tool_version': '0.1.0',
            'format_version': '1.0',
            'generated_by': 'recon-tool',
            'documentation': 'https://github.com/your-org/recon-tool'
        }
        
        # Nombre del archivo basado en timestamp y filtros
        timestamp = report.generated_at.strftime("%Y%m%d_%H%M%S")
        filter_suffix = ""
        if filters:
            if filters.get('site_id'):
                filter_suffix += f"_site{filters['site_id']}"
            if filters.get('vendor'):
                filter_suffix += f"_{filters['vendor']}"
        
        filename = f"recon_{report.project_name}{filter_suffix}_{timestamp}.json"
        output_path = self.output_dir / filename
        
        # Escribir el archivo
        with open(output_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
            else:
                json.dump(output_data, f, ensure_ascii=False, default=str)
        
        return output_path
    
    def to_string(self, report: ReconciliationReport, pretty: bool = True) -> str:
        """
        Retorna el reporte como string JSON (sin guardar archivo).
        
        Útil para APIs o procesamiento en memoria.
        """
        output_data = report.to_dict()
        
        if pretty:
            return json.dumps(output_data, indent=2, ensure_ascii=False, default=str)
        else:
            return json.dumps(output_data, ensure_ascii=False, default=str)
