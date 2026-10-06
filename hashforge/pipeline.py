"""Main orchestration pipeline for HashForge."""

import os
import time
import sys
from typing import Optional, Dict, Any, List

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table

from .config import AppConfig, load_config
from .profile.models import Profile
from .profile.wizard import run_profile_wizard
from .generators.combinations import generate_base_candidates
from .hashcat.discovery import discover_rule_files, RuleMetadata
from .hashcat.estimator import estimate_search_space
from .mutations.rules import load_rule_file, HashcatRule
from .mutations.engine import transform_candidates_stream
from .output.writer import stream_candidates_to_file

console = Console()

def format_rules_menu(rules_found: List[RuleMetadata]) -> None:
    """Format the discovered rules into a selectable menu."""
    if not rules_found:
        console.print("[red]No rule files found.[/red]")
        return
    
    table = Table(title="AVAILABLE RULES", show_header=True, header_style="bold cyan")
    table.add_column("No.", style="yellow", justify="right")
    table.add_column("Rule File", style="green")
    
    for i, meta in enumerate(rules_found, start=1):
        table.add_row(str(i), meta.name)
        
    console.print(table)


def run_hashforge_pipeline(
    profile: Optional[Profile] = None,
    rule_path: Optional[str] = None,
    output_path: Optional[str] = None,
    rules_dir: str = "rules",
    dry_run: bool = False,
    min_len: Optional[int] = None,
    max_len: Optional[int] = None,
    max_candidates: Optional[int] = None,
    interactive: bool = True,
    config: Optional[AppConfig] = None,
    skip_transformation_prompt: bool = False,
) -> Dict[str, Any]:
    if config is None:
        config = load_config()

    eff_min_len = min_len if min_len is not None else config.wcfrom
    eff_max_len = max_len if max_len is not None else config.wcto
    eff_max_candidates = max_candidates if max_candidates is not None else config.max_candidates
    eff_output_path = output_path if output_path else config.default_output_file

    if profile is None:
        profile = run_profile_wizard(show_banner=True)

    console.print("\n[bold cyan]Generating base candidates...[/bold cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Building base profile combinations...", total=None)
        base_candidates = generate_base_candidates(
            profile,
            config=config,
            min_len=1,
            max_len=100,
            max_candidates=10000000,
        )
    
    console.print(f"[bold green][+] Base candidates generated: {len(base_candidates):,}[/bold green]")

    selected_rule_path = rule_path
    selected_rule_name = "None"
    loaded_rules: List[HashcatRule] = []

    if interactive and not skip_transformation_prompt and not selected_rule_path:
        console.print("\n[bold]Would you like to apply a Hashcat rule?[/bold]")
        console.print("[yellow][Y][/yellow] Yes\n[yellow][N][/yellow] No\n[yellow][ENTER][/yellow] No")
        add_rule = Prompt.ask("[yellow]>[/yellow]", default="").strip().lower()
        
        if add_rule in ("y", "yes"):
            while True:
                rules_found = discover_rule_files(rules_dir)
                format_rules_menu(rules_found)
                console.print("\nSelect a rule or press [yellow]ENTER[/yellow] for none:")
                choice = Prompt.ask("[yellow]>[/yellow]", default="").strip()
                if not choice:
                    console.print("\n[bold green][+] Rule processing skipped.[/bold green]")
                    break
                
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(rules_found):
                        chosen_meta = rules_found[idx]
                        selected_rule_path = chosen_meta.path
                        selected_rule_name = chosen_meta.name
                        
                        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
                            progress.add_task(description=f"Loading rules from {selected_rule_name}...", total=None)
                            loaded_rules = load_rule_file(selected_rule_path)
                        
                        rule_summary = f"[bold]Selected:[/bold]\n[cyan]{selected_rule_name}[/cyan]\n\n[bold]Rules:[/bold]\n{len(loaded_rules):,}"
                        console.print(Panel(rule_summary, border_style="cyan"))
                        
                        if Confirm.ask("Proceed?", default=True):
                            break
                        else:
                            selected_rule_path = None
                            loaded_rules = []
                            continue
                    else:
                        console.print("[red][-] Invalid selection.[/red]")
                except ValueError:
                    console.print("[red][-] Invalid selection.[/red]")
        else:
            console.print("\n[bold green][+] Rule processing skipped.[/bold green]")

    elif selected_rule_path:
        if not os.path.isfile(selected_rule_path) and os.path.isfile(os.path.join(rules_dir, selected_rule_path)):
            selected_rule_path = os.path.join(rules_dir, selected_rule_path)

        if os.path.isfile(selected_rule_path):
            try:
                loaded_rules = load_rule_file(selected_rule_path)
                selected_rule_name = os.path.basename(selected_rule_path)
            except Exception as e:
                console.print(f"[red][-] Error loading rule file {selected_rule_path}: {e}[/red]")
                loaded_rules = []

    estimated_total = max(len(base_candidates) * len(loaded_rules) if loaded_rules else len(base_candidates), len(base_candidates))
    
    if estimated_total > eff_max_candidates:
        console.print(f"\n[bold red]WARNING: The selected configuration may generate more than {eff_max_candidates:,} candidates.[/bold red]")
        console.print("[yellow][1][/yellow] Reduce rule count\n[yellow][2][/yellow] Continue anyway\n[yellow][3][/yellow] Cancel\n")
        resp = Prompt.ask("[yellow]>[/yellow]", default="").strip()
        if resp == "1":
            limit = Prompt.ask("Enter maximum number of rules").strip()
            if limit.isdigit():
                loaded_rules = loaded_rules[:int(limit)]
                estimated_total = len(base_candidates) * len(loaded_rules)
        elif resp == "3":
            return {"count": 0, "output_path": eff_output_path}

    if interactive:
        console.print("\n[bold cyan]WORDLIST SETTINGS[/bold cyan]")
        console.print("[cyan]=================[/cyan]\n")
        
        min_in = Prompt.ask(f"Minimum length", default=str(eff_min_len)).strip()
        if min_in.isdigit(): eff_min_len = int(min_in)
        
        max_in = Prompt.ask(f"Maximum length", default=str(eff_max_len)).strip()
        if max_in.isdigit(): eff_max_len = int(max_in)
        
        out_in = Prompt.ask(f"Output filename", default=eff_output_path).strip()
        if out_in: eff_output_path = out_in
        if not eff_output_path.endswith(".txt"): eff_output_path += ".txt"

    if dry_run:
        return {"count": 0, "output_path": eff_output_path}

    avg_len = 10
    estimated_size_bytes = estimated_total * (avg_len + 1)
    estimated_size_mb = estimated_size_bytes / (1024 * 1024)
    write_speed_est = 250000
    estimated_time_sec = estimated_total / write_speed_est

    est_panel = (
        f"Candidates    : ~{estimated_total:,}\n"
        f"Size on Disk  : ~{estimated_size_mb:.2f} MB\n"
        f"Time          : ~{estimated_time_sec:.2f} seconds"
    )
    console.print(Panel(est_panel, title="[bold]ESTIMATION[/bold]", border_style="yellow"))

    console.print("\n[bold cyan]GENERATING[/bold cyan]")
    console.print("[cyan]==========[/cyan]\n")

    candidate_stream = transform_candidates_stream(
        base_candidates=base_candidates,
        rules=loaded_rules,
        min_len=eff_min_len,
        max_len=eff_max_len,
        max_candidates=eff_max_candidates,
    )

    start_time = time.time()
    
    # We don't know exact final count due to deduplication, so we use an indeterminate progress or estimate
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
    ) as progress:
        task_id = progress.add_task(description="Writing wordlist...", total=estimated_total)
        
        def progress_callback(current_count: int) -> None:
            progress.update(task_id, completed=current_count)

        result = stream_candidates_to_file(
            candidate_stream=candidate_stream,
            output_path=eff_output_path,
            on_progress=progress_callback,
        )
    
    duration = time.time() - start_time

    final_panel = (
        f"[bold]Output:[/bold]\n{result['output_path']}\n\n"
        f"[bold]Unique candidates:[/bold]\n{result['count']:,}\n\n"
        f"[bold]File size:[/bold]\n{result['size_formatted']}\n\n"
        f"[bold]Generation time:[/bold]\n{duration:.2f} seconds"
    )
    
    console.print(Panel(final_panel, title="[bold green]COMPLETE[/bold green]", border_style="green"))

    return result
