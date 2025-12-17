import sys
import os
from pathlib import Path
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table
from rich.console import Console

# --- 1. Fix Python Path (Keep this logic!) ---
current_file = Path(__file__).resolve()
backend_dir = current_file.parent.parent
sys.path.append(str(backend_dir))

from app.graph.agents.profile_analyzer.agent import build_profile_graph
from app.graph.schema import UserProfile

console = Console()

def run_graph_test():
    console.rule("[bold blue]🧪 Starting Profile Graph Test[/bold blue]")

    # --- 2. Setup File Path ---
    pdf_path = backend_dir / "app" / "graph" / "temp" / "my_inbody.pdf"

    if not pdf_path.exists():
        rprint(f"[bold red]❌ Error: File not found at {pdf_path}[/bold red]")
        return
        
    rprint(f"[grey50]📂 Found PDF at: {pdf_path}[/grey50]")

    # --- 3. Create Initial State ---
    initial_profile = UserProfile(
        user_id="test_user_001",
        name="Pei-Cheng Yu",
        age=24,
        gender="Male",
        height_cm=175.0,
        goal="Muscle Gain"
    )

    input_state = {
        "inbody_pdf_input": str(pdf_path),
        "profile": initial_profile,
        "messages": []
    }

    # --- 4. Run Graph ---
    try:
        rprint("🔨 Building Graph...")
        app = build_profile_graph()
        
        rprint("🚀 Invoking Graph...")
        final_state = app.invoke(input_state)
        
        # --- 5. Verify & Print Results ---
        result_profile = final_state.get("profile")
        
        if not result_profile or not result_profile.latest_scan:
            rprint("[bold red]❌ Failure: No scan data found in profile.[/bold red]")
            return

        scan = result_profile.latest_scan

        # --- A. Print Basic Metrics Table ---
        table = Table(title=f"InBody Analysis for {result_profile.name}", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Unit", style="yellow")

        table.add_row("Height", str(scan.height_cm), "cm")
        table.add_row("Weight", str(scan.weight_kg), "kg")
        table.add_row("Skeletal Muscle Mass (SMM)", str(scan.skeletal_muscle_mass_kg), "kg")
        table.add_row("Body Fat (PBF)", str(scan.body_fat_percent), "%")
        table.add_row("Basal Metabolic Rate (BMR)", str(scan.basal_metabolic_rate), "kcal")
        table.add_row("Visceral Fat Level", str(scan.visceral_fat_level or "N/A"), "Level")
        table.add_row("InBody Score", str(scan.inbody_score or "N/A"), "Points")
        table.add_row("Curve Type", f"[bold]{scan.curve_type}[/bold]", "")
        
        console.print(table)

        # --- B. Print Segmental Analysis (Nested Data) ---
        if scan.segmental_muscle:
            seg = scan.segmental_muscle
            
            seg_table = Table(title="💪 Segmental Lean Analysis (Muscle Mass)", box=None)
            seg_table.add_column("Body Part", style="cyan")
            seg_table.add_column("Mass", style="bold green")
            
            seg_table.add_row("Right Arm", f"{seg.right_arm_kg} kg")
            seg_table.add_row("Left Arm", f"{seg.left_arm_kg} kg")
            seg_table.add_row("Trunk (Core)", f"{seg.trunk_kg} kg")
            seg_table.add_row("Right Leg", f"{seg.right_leg_kg} kg")
            seg_table.add_row("Left Leg", f"{seg.left_leg_kg} kg")
            
            console.print(Panel(seg_table, expand=False, border_style="blue"))
        else:
            rprint("[yellow]⚠️ No Segmental Analysis data extracted.[/yellow]")

        # --- C. Cleanup Check ---
        if final_state.get("inbody_pdf_input") is None:
            rprint("\n[bold green]✅ Memory Cleanup Successful (Input cleared)[/bold green]")
        else:
            rprint("\n[bold red]⚠️ Memory Warning: Input not cleared[/bold red]")

    except Exception as e:
        rprint(f"[bold red]❌ Test Crashed: {e}[/bold red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_graph_test()