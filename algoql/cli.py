import click
import algoql

@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.pass_context
def cli(ctx):
    "algoql"
    ctx.ensure_object(dict)

@click.command()
@click.argument("query")
@click.pass_context
def query(ctx, query):
    """Execute algoql query"""
    for row in algoql.execute(query):
        print(row)

cli.add_command(query)