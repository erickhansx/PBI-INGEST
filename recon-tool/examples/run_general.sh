#!/bin/bash
# run_general.sh - Ejecutar reconciliación general
# Ejemplo de uso de la herramienta recon

# Cambiar al directorio del proyecto
cd "$(dirname "$0")/.."

# Ejecutar reconciliación completa
echo "==================================="
echo "RECON TOOL - General Reconciliation"
echo "==================================="

recon run --config configs/mvh.yaml --output reports/general_$(date +%Y%m%d).md

echo ""
echo "Reporte generado en reports/"
