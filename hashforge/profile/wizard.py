"""Interactive terminal profile wizard for HashForge."""

import sys
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from .models import Profile

console = Console()

def run_profile_wizard(show_banner: bool = True) -> Profile:
    if show_banner:
        console.print(Panel("[bold cyan]TARGET PROFILE[/bold cyan]", border_style="cyan"))

    first_name = Prompt.ask("[yellow]First name[/yellow]", default="").strip()
    last_name = Prompt.ask("[yellow]Last name[/yellow]", default="").strip()
    nickname = Prompt.ask("[yellow]Nickname[/yellow]", default="").strip()
    username = Prompt.ask("[yellow]Username[/yellow]", default="").strip()
    console.print("")
    partner_name = Prompt.ask("[yellow]Partner name[/yellow]", default="").strip()
    partner_nickname = Prompt.ask("[yellow]Partner nickname[/yellow]", default="").strip()
    console.print("")
    child_name = Prompt.ask("[yellow]Child name[/yellow]", default="").strip()
    pet_name = Prompt.ask("[yellow]Pet name[/yellow]", default="").strip()
    console.print("")
    company = Prompt.ask("[yellow]Company[/yellow]", default="").strip()
    org = Prompt.ask("[yellow]Organization[/yellow]", default="").strip()
    school = Prompt.ask("[yellow]School[/yellow]", default="").strip()
    college = Prompt.ask("[yellow]College[/yellow]", default="").strip()
    console.print("")
    city = Prompt.ask("[yellow]City[/yellow]", default="").strip()
    country = Prompt.ask("[yellow]Country[/yellow]", default="").strip()
    location = Prompt.ask("[yellow]Location[/yellow]", default="").strip()
    console.print("")
    ssid = Prompt.ask("[yellow]SSID[/yellow]", default="").strip()
    console.print("")
    sports = Prompt.ask("[yellow]Favorite sports[/yellow]", default="").strip()
    teams = Prompt.ask("[yellow]Favorite teams[/yellow]", default="").strip()
    console.print("")
    games = Prompt.ask("[yellow]Favorite games[/yellow]", default="").strip()
    movies = Prompt.ask("[yellow]Favorite movies[/yellow]", default="").strip()
    shows = Prompt.ask("[yellow]Favorite shows[/yellow]", default="").strip()
    music = Prompt.ask("[yellow]Favorite music/artists[/yellow]", default="").strip()
    console.print("")
    hobbies = Prompt.ask("[yellow]Hobbies[/yellow]", default="").strip()
    tech = Prompt.ask("[yellow]Technologies[/yellow]", default="").strip()
    lang = Prompt.ask("[yellow]Programming languages[/yellow]", default="").strip()
    console.print("")
    projects = Prompt.ask("[yellow]Projects[/yellow]", default="").strip()
    brands = Prompt.ask("[yellow]Brands[/yellow]", default="").strip()
    products = Prompt.ask("[yellow]Products[/yellow]", default="").strip()
    console.print("")
    dates = Prompt.ask("[yellow]Important dates[/yellow]", default="").strip()
    years = Prompt.ask("[yellow]Important years[/yellow]", default="").strip()
    console.print("")
    console.print("[bold]Enter additional keywords separated by commas:[/bold]")
    other_keywords = Prompt.ask("[yellow]>[/yellow]", default="").strip()

    # Aggregate fields
    words_list = []
    
    orgs = [company, org, school, college]
    locs = [city, country, location, ssid]
    interests = [sports, teams, games, movies, shows, music, hobbies]
    techs = [tech, lang]
    projs = [projects, brands, products]
    yrs = [dates, years]
    
    custom_words = [w.strip() for w in other_keywords.split(",") if w.strip()]
    
    for category in [orgs, locs, interests, techs, projs, yrs]:
        for item in category:
            if item:
                words_list.extend([w.strip() for w in item.split(",") if w.strip()])
    
    words_list.extend(custom_words)
    
    names_count = sum(1 for x in [first_name, last_name, nickname, username, partner_name, partner_nickname, child_name, pet_name] if x)
    orgs_count = sum(1 for x in orgs if x)
    locs_count = sum(1 for x in locs if x)
    ints_count = sum(1 for x in interests if x)
    techs_count = sum(1 for x in techs if x)
    projs_count = sum(1 for x in projs if x)
    yrs_count = sum(1 for x in yrs if x)
    custom_count = len(custom_words)

    summary_text = (
        f"Names:          [green]{names_count}[/green]\n"
        f"Organizations:  [green]{orgs_count}[/green]\n"
        f"Locations:      [green]{locs_count}[/green]\n"
        f"Interests:      [green]{ints_count}[/green]\n"
        f"Technologies:   [green]{techs_count}[/green]\n"
        f"Projects:       [green]{projs_count}[/green]\n"
        f"Years:          [green]{yrs_count}[/green]\n"
        f"Custom words:   [green]{custom_count}[/green]"
    )
    console.print(Panel(summary_text, title="[bold cyan]PROFILE SUMMARY[/bold cyan]", border_style="cyan"))
    
    if not Confirm.ask("Continue?", default=True):
        return run_profile_wizard(show_banner=False)

    return Profile(
        name=first_name.lower(),
        surname=last_name.lower(),
        nick=nickname.lower(),
        wife=partner_name.lower(),
        wifen=partner_nickname.lower(),
        kid=child_name.lower(),
        pet=pet_name.lower(),
        company=company.lower(),
        words=words_list,
        spechars1=True,
        randnum=True,
        leetmode=True,
    )
