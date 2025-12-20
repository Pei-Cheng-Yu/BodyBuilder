import asyncio
import sys
from pathlib import Path

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# --- 1. Fix Python Path ---
current_file = Path(__file__).resolve()
backend_dir = current_file.parent.parent
sys.path.append(str(backend_dir))

# Import your graph builders\
if current_file:
    from app.graph.agents.diagnosis_doctor.agent import build_doctor_graph
    from app.graph.agents.exercise_curator.agent import build_curator_graph
    from app.graph.agents.profile_analyzer.agent import build_profile_graph
    from app.graph.agents.strategy_planner.agent import build_strategy_graph
    from app.graph.schema import UserProfile

console = Console()


async def run_full_system_test():
    console.rule("[bold magenta]🚀 Starting Full End-to-End System Test[/bold magenta]")

    # --- STEP 1: Profile Analysis (InBody) ---
    rprint("[bold blue]Step 1: Analyzing InBody PDF...[/bold blue]")
    pdf_path = backend_dir / "app" / "graph" / "temp" / "my_inbody.pdf"

    initial_profile = UserProfile(
        user_id="test_user_001",
        name="Pei-Cheng Yu",
        age=24,
        gender="Male",
        height_cm=175.0,
        user_goal="Muscle Gain",
        workout_frequency=3,  # Added frequency
    )

    state = {
        "inbody_pdf_input": str(pdf_path),
        "profile": initial_profile,
        "messages": [],
    }

    profile_app = build_profile_graph()
    state = await profile_app.ainvoke(state)
    rprint("✅ InBody Data Extracted.")

    # --- STEP 2: Doctor Diagnosis ---
    rprint("\n[bold blue]Step 2: Generating Medical Prescription...[/bold blue]")
    doctor_app = build_doctor_graph()
    state = await doctor_app.ainvoke(state)

    doc_sug = state.get("doctor_suggestion")
    rprint(
        Panel(
            f"[bold green]Focus:[/bold green] {doc_sug.target_focus_areas}\n"
            f"[bold red]Avoid:[/bold red] {doc_sug.safety_constraints}",
            title="Doctor's RX",
        )
    )

    # --- STEP 3: Strategy Planner ---
    rprint("\n[bold blue]Step 3: Creating Weekly Skeleton...[/bold blue]")
    strategy_app = build_strategy_graph()
    state = await strategy_app.ainvoke(state)
    rprint(
        f"✅ Strategy Created: [bold cyan]{state['weekly_plan'].plan_name}[/bold cyan]"
    )

    # --- STEP 4: Content Curator (Parallel Workers) ---
    rprint("\n[bold blue]Step 4: Curating Exercises (Parallel Agents)...[/bold blue]")
    curator_app = build_curator_graph()
    # Note: This is where the magic happens (Map-Reduce)
    state = await curator_app.ainvoke(state, config={"recursion_limit": 50})

    # --- FINAL VISUALIZATION ---
    console.rule("[bold green]🏁 Final Workout Plan[/bold green]")
    plan = state["weekly_plan"]

    for day in plan.schedule:
        table = Table(
            title=f"📅 {day.day} - {day.focus_area}",
            show_header=True,
            header_style="bold yellow",
        )
        table.add_column("Exercise", style="cyan")
        table.add_column("Sets/Reps", style="green")
        table.add_column("ID", style="dim")

        if day.is_rest_day:
            rprint(f"[grey50]🛌 {day.day}: Rest Day[/grey50]")
            continue

        for ex in day.exercises:
            table.add_row(ex.name, f"{ex.sets}x{ex.reps}", ex.exercise_id)

        console.print(table)
        rprint(f"[italic grey70]Coach Note: {day.coach_instructions}[/italic grey70]\n")


if __name__ == "__main__":
    # Use asyncio to run the async nodes
    asyncio.run(run_full_system_test())
