#!/bin/bash
# run_site_146.sh - Analizar Site 146 específicamente
# Ejemplo de análisis específico por site y vendor

# Cambiar al directorio del proyecto
cd "$(dirname "$0")/.."

# Ejecutar análisis específico para Site 146, Verizon
echo "==================================="
echo "RECON TOOL - Site 146 Analysis"
echo "==================================="

recon analyze \
    --config configs/mvh.yaml \
    --site-id 146 \
    --vendor Verizon \
    --output reports/site_146_verizon_$(date +%Y%m%d).md

echo ""
echo "Análisis completado para Site 146, Verizon"
