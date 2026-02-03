"""
Sprint 0 Test - Verifica que los componentes básicos funcionan
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from datetime import datetime

def test_models():
    """Prueba los modelos de datos"""
    from recon.core.models import (
        ValidationStatus,
        Severity,
        ValidationResult,
        EntityComparison,
        ReconciliationReport
    )
    
    print("Testing models...")
    
    # Test ValidationStatus enum
    assert ValidationStatus.MATCH.value == "MATCH"
    assert ValidationStatus.MISMATCH.value == "MISMATCH"
    assert ValidationStatus.NOT_VERIFIABLE.value == "NOT_VERIFIABLE"
    assert ValidationStatus.RULE_NOT_DEFINED.value == "RULE_NOT_DEFINED"
    print("  ✓ ValidationStatus enum OK")
    
    # Test ValidationResult
    result = ValidationResult(
        status=ValidationStatus.MATCH,
        field_name="Total MRC",
        source_value=69.0,
        pbi_value=69.0,
        message="Values match exactly"
    )
    assert result.to_dict()['status'] == 'MATCH'
    print("  ✓ ValidationResult OK")
    
    # Test EntityComparison
    comparison = EntityComparison(
        entity_type="site",
        entity_id="146",
        entity_filters={"site_id": "146", "vendor": "Verizon"},
        validations=[result]
    )
    assert comparison.match_count == 1
    assert comparison.mismatch_count == 0
    print("  ✓ EntityComparison OK")
    
    # Test ReconciliationReport
    report = ReconciliationReport(
        project_name="mvh",
        generated_at=datetime.now(),
        config_file="configs/mvh.yaml"
    )
    report_dict = report.to_dict()
    assert report_dict['project_name'] == 'mvh'
    print("  ✓ ReconciliationReport OK")
    
    print("Models: ALL TESTS PASSED ✓")


def test_config():
    """Prueba el cargador de configuración"""
    from recon.core.config import ConfigLoader
    
    print("\nTesting config loader...")
    
    config_path = Path(__file__).parent.parent / 'configs' / 'mvh.yaml'
    
    if not config_path.exists():
        print(f"  ⚠ Config file not found: {config_path}")
        return
    
    loader = ConfigLoader(config_path)
    config = loader.load()
    
    assert config.name == 'mvh'
    print(f"  ✓ Project name: {config.name}")
    
    assert len(config.sources) == 7
    print(f"  ✓ Sources loaded: {len(config.sources)}")
    
    assert len(config.validation_rules) == 4
    print(f"  ✓ Validation rules: {len(config.validation_rules)}")
    
    assert len(config.integrity_checks) == 3
    print(f"  ✓ Integrity checks: {len(config.integrity_checks)}")
    
    # Verify validation rules have correct service types
    assert 'Broadband' in config.validation_rules
    assert 'DIA' in config.validation_rules
    assert 'CPE' in config.validation_rules
    assert 'LTE' in config.validation_rules
    print("  ✓ All service types defined")
    
    print("Config: ALL TESTS PASSED ✓")


def test_reporters():
    """Prueba los generadores de reportes"""
    from recon.core.models import ReconciliationReport
    from recon.reporting.markdown_reporter import MarkdownReporter
    from recon.reporting.json_reporter import JsonReporter
    
    print("\nTesting reporters...")
    
    # Create a test report
    report = ReconciliationReport(
        project_name="test",
        generated_at=datetime.now(),
        config_file="test.yaml"
    )
    
    # Test Markdown
    md_reporter = MarkdownReporter('./test_reports')
    content = md_reporter._build_content(report, {'site_id': '146'})
    assert '# 🔍 Reporte de Reconciliación' in content
    assert 'MATCH' in content
    assert 'NOT_VERIFIABLE' in content
    print("  ✓ MarkdownReporter OK")
    
    # Test JSON
    json_reporter = JsonReporter('./test_reports')
    json_str = json_reporter.to_string(report)
    assert '"project_name": "test"' in json_str
    print("  ✓ JsonReporter OK")
    
    print("Reporters: ALL TESTS PASSED ✓")


def main():
    """Ejecuta todas las pruebas"""
    print("=" * 60)
    print("SPRINT 0 TEST SUITE")
    print("=" * 60)
    
    test_models()
    test_config()
    test_reporters()
    
    print("\n" + "=" * 60)
    print("ALL SPRINT 0 TESTS PASSED ✓")
    print("=" * 60)


if __name__ == '__main__':
    main()
