import typer
import enum
from rich.console import Console
from rich.table import Table
import sys
from hmt.core import HMT, SECS_MAP
from typing import Optional
from typer.core import TyperGroup
import warnings

warnings.simplefilter("ignore")

__version__ = "0.0.1"


class GranularityChoices(enum.StrEnum):
    second = "second"
    hour = "hour"
    day = "day"
    week = "week"
    month = "month"
    year = "year"


app = typer.Typer(

)

hmt = HMT()

console = Console()


def version_callback(value: bool):
    if value:
        
        typer.echo(f"HMT version: {__version__}")
        raise typer.Exit()


@app.command()
def main(
    ctx: typer.Context,
    
    date: list[str] = typer.Argument(None),
    from_: list[str] = typer.Option(
        None, "-f", "--from", help="Usually time point in the past", rich_help_panel="Default options"
    ),
    to: list[str] = typer.Option(
        None, "-t", "--to", help="Usually time point in the future",rich_help_panel="Default options"
    ),
    granularity: GranularityChoices = typer.Option(
        GranularityChoices.day,
        "-g",
        "--granularity",
        help="Choose single time unit to show result",
        rich_help_panel="Format options"
    ),
    long: bool = typer.Option(
        False,
        "-l",
        "--long",
        help="Long format will show every possible granularity e.g. seconds, days, weeks",
        rich_help_panel="Format options",
    ),
    version: bool = typer.Option(
        None,
        "-v",
        "--version",
        callback=version_callback,
        rich_help_panel="Utility",
    ),
):
    """
    Additional help information
    """

    f, t = (from_ or date), (to or None)

    if to or (f and t):
        result = hmt.get_distance(f, t)
    else:
        result = hmt.get_offset(f)

    # Print section
    if long:
        for repr_key in result.timeframes.keys():
            if result.get_timeframe(repr_key):
                console.print(result.get_timeframe(repr_key).string_representation) #type: ignore
        sys.exit(0)
    else:
        repr = result.get_timeframe(granularity)
        if repr:
            console.print(repr.string_representation)
        else:
            console.print("Invalid granularity [{granularity}] try [day] instead")

        
        


if __name__ == "__main__":
    app()
