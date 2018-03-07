from __future__ import unicode_literals

import tempfile

import click
import com.ti.ccstudio.scripting.environment


@click.group()
def cli():
    pass


@cli.command()
@click.option('--ccxml', type=click.Path(exists=True), required=True)
@click.option('--log', type=click.Path())
@click.option('--binary', type=click.Path(exists=True), required=True)
@click.option(
    '--trace-level',
    type=click.Choice((
        'off',
        'severe',
        'warning',
        'info',
        'config',
        'fine',
        'finer',
        'finest',
        'all',
    )),
    default='off',
)
def load(ccxml, log, binary, trace_level):
    script = com.ti.ccstudio.scripting.environment.ScriptingEnvironment.instance()

    trace_level = getattr(
        com.ti.ccstudio.scripting.environment.TraceLevel,
        trace_level.upper(),
    )

    script.traceSetConsoleLevel(trace_level)

    if log is not None:
        script.traceBegin(log, 'DefaultStylesheet.xsl')

        script.traceSetFileLevel(trace_level)

    script.setScriptTimeout(150000)

    debugServer = script.getServer('DebugServer.1')
    debugServer.setConfig(ccxml)

    debugSession = debugServer.openSession()

    debugSession.target.connect()

    debugSession.memory.loadProgram(binary)

    debugSession.target.restart()
    debugSession.target.runAsynch()

    debugServer.stop()
