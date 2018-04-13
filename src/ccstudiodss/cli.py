import click
import ccstudiodss.api
import ccstudiodss.utils


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    '--binary',
    type=click.Path(exists=True, dir_okay=False),
    required=True,
)
@click.option(
    '--ccxml',
    type=click.Path(exists=True, dir_okay=False),
    required=True,
)
@click.option('--ccs-base-path', type=click.Path(exists=True, file_okay=False))
def load(binary, ccxml, ccs_base_path):
    ccstudiodss.api.add_jars(base_path=ccs_base_path)

    with ccstudiodss.api.Session(ccxml=ccxml) as session:
        session.load(binary=binary)
