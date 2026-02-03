"""
CLI - Command Line Interface for Reconciliation Tool
Interfaz de línea de comandos usando Click
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from recon.core.config import ConfigLoader, ConfigurationError
from recon.core.models import (
    ReconciliationReport,
    ValidationStatus,
    Severity
)

console = Console()


def get_status_color(status: ValidationStatus) -> str:
    """Retorna el color para cada estado de validación"""
    colors = {
        ValidationStatus.MATCH: "green",
        ValidationStatus.MISMATCH: "red",
        ValidationStatus.MISSING_IN_PBI: "yellow",
        ValidationStatus.MISSING_IN_SOURCE: "yellow",
        ValidationStatus.NOT_VERIFIABLE: "blue",
        ValidationStatus.RULE_NOT_DEFINED: "magenta"
    }
    return colors.get(status, "white")


def get_severity_color(severity: Severity) -> str:
    """Retorna el color para cada nivel de severidad"""
    colors = {
        Severity.INFO: "blue",
        Severity.WARNING: "yellow",
        Severity.ERROR: "red",
        Severity.CRITICAL: "bold red"
    }
    return colors.get(severity, "white")


@click.group()
@click.version_option(version='0.1.0', prog_name='recon-tool')
def cli():
    """
    🔍 Recon Tool - PBI Data Reconciliation
    
    Herramienta para validar datos de Power BI contra fuentes originales.
    
    Principios de diseño:
    
    \b
    - MATCH: Datos coinciden exactamente (o dentro de tolerancia)
    - MISMATCH: Hay valores en ambos lados pero no coinciden
    - MISSING_IN_PBI: Existe en source, no existe en PBI
    - MISSING_IN_SOURCE: Existe en PBI, no existe en source
    - NOT_VERIFIABLE: No hay datos suficientes para comparar
    - RULE_NOT_DEFINED: No existe regla de mapeo definida
    """
    pass


@cli.command()
@click.option('--project', '-p', required=True, help='Nombre del proyecto (ej: mvh)')
@click.option('--config-dir', '-c', default='./configs', help='Directorio de configuraciones')
@click.option('--site', '-s', help='Filtrar por Site ID específico')
@click.option('--vendor', '-v', help='Filtrar por Vendor')
@click.option('--service-type', '-t', help='Filtrar por tipo de servicio')
@click.option('--output', '-o', type=click.Choice(['console', 'markdown', 'json', 'all']), 
              default='console', help='Formato de salida')
@click.option('--output-dir', default='./reports', help='Directorio para guardar reportes')
def run(project: str, config_dir: str, site: str, vendor: str, 
        service_type: str, output: str, output_dir: str):
    """
    Ejecuta la reconciliación de datos para un proyecto.
    
    \b
    Ejemplos:
      recon run --project mvh
      recon run --project mvh --site 146 --vendor Verizon
      recon run --project mvh --service-type Broadband --output markdown
    """
    start_time = datetime.now()
    
    # Banner
    console.print(Panel.fit(
        "[bold blue]🔍 Recon Tool[/bold blue] - Data Reconciliation",
        subtitle=f"Project: {project}"
    ))
    
    # Cargar configuración
    config_path = Path(config_dir) / f"{project}.yaml"
    
    try:
        console.print(f"\n📁 Loading config: [cyan]{config_path}[/cyan]")
        loader = ConfigLoader(config_path)
        config = loader.load()
        console.print(f"   ✓ Project: [green]{config.name}[/green] v{config.version}")
        console.print(f"   ✓ Sources: {len(config.sources)}")
        console.print(f"   ✓ Validation rules: {len(config.validation_rules)}")
    except ConfigurationError as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗ Unexpected error:[/red] {e}")
        sys.exit(1)
    
    # Mostrar filtros aplicados
    filters = {}
    if site:
        filters['site_id'] = site
        console.print(f"\n🔍 Filter: Site ID = [yellow]{site}[/yellow]")
    if vendor:
        filters['vendor'] = vendor
        console.print(f"🔍 Filter: Vendor = [yellow]{vendor}[/yellow]")
    if service_type:
        filters['service_type'] = service_type
        console.print(f"🔍 Filter: Service Type = [yellow]{service_type}[/yellow]")
    
    # TODO: Implementar el engine de reconciliación en Sprint 1
    console.print("\n" + "="*60)
    console.print("[yellow]⚠️  Sprint 0: Skeleton mode - Engine not yet implemented[/yellow]")
    console.print("="*60)
    
    # Crear reporte vacío para demo
    report = ReconciliationReport(
        project_name=config.name,
        generated_at=datetime.now(),
        config_file=str(config_path),
        filters_applied=filters,
        execution_time_seconds=(datetime.now() - start_time).total_seconds()
    )
    
    # Generar salida según formato
    if output in ['markdown', 'all']:
        from recon.reporting.markdown_reporter import MarkdownReporter
        reporter = MarkdownReporter(output_dir)
        output_path = reporter.generate(report, filters)
        console.print(f"\n📄 Markdown report: [cyan]{output_path}[/cyan]")
    
    if output in ['json', 'all']:
        from recon.reporting.json_reporter import JsonReporter
        reporter = JsonReporter(output_dir)
        output_path = reporter.generate(report)
        console.print(f"\n📄 JSON report: [cyan]{output_path}[/cyan]")
    
    if output == 'console':
        _display_console_report(report)
    
    # Resumen final
    elapsed = (datetime.now() - start_time).total_seconds()
    console.print(f"\n⏱️  Completed in [green]{elapsed:.2f}s[/green]")


@cli.command()
@click.option('--config-dir', '-c', default='./configs', help='Directorio de configuraciones')
def list_projects(config_dir: str):
    """Lista los proyectos disponibles."""
    configs_path = Path(config_dir)
    
    if not configs_path.exists():
        console.print(f"[red]✗ Config directory not found:[/red] {config_dir}")
        sys.exit(1)
    
    projects = ConfigLoader.get_available_projects(configs_path)
    
    if not projects:
        console.print("[yellow]No projects found.[/yellow]")
        return
    
    console.print("\n[bold]Available Projects:[/bold]\n")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Project")
    table.add_column("Config File")
    table.add_column("Status")
    
    for project in projects:
        config_file = configs_path / f"{project}.yaml"
        try:
            loader = ConfigLoader(config_file)
            config = loader.load()
            table.add_row(
                config.name,
                str(config_file),
                "[green]✓ Valid[/green]"
            )
        except Exception as e:
            table.add_row(
                project,
                str(config_file),
                f"[red]✗ Error: {str(e)[:30]}...[/red]"
            )
    
    console.print(table)


@cli.command()
@click.option('--project', '-p', required=True, help='Nombre del proyecto')
@click.option('--config-dir', '-c', default='./configs', help='Directorio de configuraciones')
def validate_config(project: str, config_dir: str):
    """Valida la configuración de un proyecto."""
    config_path = Path(config_dir) / f"{project}.yaml"
    
    console.print(f"\n🔍 Validating: [cyan]{config_path}[/cyan]\n")
    
    try:
        loader = ConfigLoader(config_path)
        config = loader.load()
        
        console.print("[green]✓ Configuration is valid![/green]\n")
        
        # Mostrar resumen
        console.print(f"[bold]Project:[/bold] {config.name}")
        console.print(f"[bold]Description:[/bold] {config.description}")
        console.print(f"[bold]Version:[/bold] {config.version}")
        
        console.print(f"\n[bold]Sources ({len(config.sources)}):[/bold]")
        for name, src in config.sources.items():
            path_status = "✓" if src.resolve_path(config.base_path).exists() else "✗ NOT FOUND"
            console.print(f"  - {name}: {src.path} [{path_status}]")
        
        console.print(f"\n[bold]Validation Rules ({len(config.validation_rules)}):[/bold]")
        for service_type, rule in config.validation_rules.items():
            console.print(f"  - {service_type}: {len(rule.field_mappings)} field mappings")
        
        console.print(f"\n[bold]Integrity Checks ({len(config.integrity_checks)}):[/bold]")
        for check in config.integrity_checks:
            console.print(f"  - {check.name}: {check.source_table} → {check.target_table}")
        
    except ConfigurationError as e:
        console.print(f"[red]✗ Configuration Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        sys.exit(1)


@cli.command()
def status_legend():
    """Muestra la leyenda de estados de validación."""
    console.print("\n[bold]Validation Status Legend:[/bold]\n")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Status")
    table.add_column("Meaning")
    table.add_column("Action Required")
    
    table.add_row(
        "[green]MATCH[/green]",
        "Datos coinciden exactamente (o dentro de tolerancia configurada)",
        "Ninguna"
    )
    table.add_row(
        "[red]MISMATCH[/red]",
        "Hay valor en ambos lados y NO coinciden",
        "Investigar discrepancia"
    )
    table.add_row(
        "[yellow]MISSING_IN_PBI[/yellow]",
        "Existe en source original, NO existe en modelo PBI",
        "Verificar carga de datos"
    )
    table.add_row(
        "[yellow]MISSING_IN_SOURCE[/yellow]",
        "Existe en modelo PBI, NO existe en source original",
        "Verificar origen del dato"
    )
    table.add_row(
        "[blue]NOT_VERIFIABLE[/blue]",
        "No hay datos suficientes para realizar la comparación",
        "Revisar disponibilidad de datos"
    )
    table.add_row(
        "[magenta]RULE_NOT_DEFINED[/magenta]",
        "No existe regla/mapeo configurado para ese campo",
        "Definir regla en config YAML"
    )
    
    console.print(table)
    
    console.print("\n[bold]Principio de diseño:[/bold]")
    console.print("La herramienta NUNCA asume ni infiere. Si no puede verificar,")
    console.print("clasifica como NOT_VERIFIABLE o RULE_NOT_DEFINED.")
    console.print("[italic]Nunca 'podría ser...' o 'probablemente...'[/italic]\n")


def _display_console_report(report: ReconciliationReport):
    """Muestra el reporte en consola"""
    console.print("\n" + "="*60)
    console.print(f"[bold]RECONCILIATION REPORT[/bold]")
    console.print("="*60)
    
    console.print(f"\nProject: {report.project_name}")
    console.print(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    console.print(f"Config: {report.config_file}")
    
    if report.filters_applied:
        console.print(f"Filters: {report.filters_applied}")
    
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Integrity Checks: {len(report.integrity_checks)}")
    console.print(f"  Data Quality Tables: {len(report.data_quality)}")
    console.print(f"  Entity Comparisons: {len(report.entity_comparisons)}")
    
    if not report.entity_comparisons and not report.integrity_checks:
        console.print("\n[yellow]No validation results yet (Sprint 0 skeleton)[/yellow]")


def main():
    """Entry point principal"""
    cli()


if __name__ == '__main__':
    main()
