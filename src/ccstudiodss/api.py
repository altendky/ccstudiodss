import contextlib
import os
import pathlib

import attr
import javabridge

import ccstudiodss.utils


def add_jars(base_path=None):
    if base_path is None:
        base_path = ccstudiodss.utils.find_base_path()

    for jar in jar_paths(base_path=base_path):
        if jar not in javabridge.JARS:
            javabridge.JARS.append(str(jar))


def join_path_lists(*path_lists):
    s = os.pathsep.join(
        path_list.strip(os.pathsep)
        for path_list in path_lists
    )

    return s.strip(os.pathsep)


relative_jar_paths = tuple(
    pathlib.Path(path)
    for path in (
        'DebugServer/packages/ti/dss/java/dss.jar',
        (
            'DebugServer/packages/ti/dss/java/'
            'com.ti.ccstudio.scripting.environment_3.1.0.jar'
        ),
        'DebugServer/packages/ti/dss/java/com.ti.debug.engine_1.0.0.jar',
        'dvt/scripting/dvt_scripting.jar',
    )
)


def jar_paths(base_path, relative=relative_jar_paths):
    base_path = pathlib.Path(base_path)
    return tuple(
        base_path / path
        for path in relative
    )


@attr.s
class Session:
    ccxml = attr.ib()
    script = attr.ib(default=None)
    debug_server = attr.ib(default=None)
    debug_session = attr.ib(default=None)

    def __enter__(self):
        javabridge.start_vm(run_headless=True)

        try:
            ScriptingEnvironment = javabridge.JClassWrapper(
                'com.ti.ccstudio.scripting.environment.ScriptingEnvironment',
            )
            self.script = ScriptingEnvironment.instance()

            self.debug_server = self.script.getServer("DebugServer.1")
            self.debug_server.setConfig(str(self.ccxml))

            self.debug_session = self.debug_server.openSession()

            self.debug_session.target.connect()
        except:
            javabridge.kill_vm()

            raise

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.debug_session.target.disconnect()
            self.debug_server.stop()
        finally:
            javabridge.kill_vm()

    @contextlib.contextmanager
    def temporary_timeout(self, timeout):
        old_timeout = self.script.getScriptTimeout()
        self.script.setScriptTimeout(timeout * 1000)
        yield
        self.script.setScriptTimeout(old_timeout)

    def load(self, binary, timeout=150):
        with self.temporary_timeout(timeout):
            self.debug_session.memory.loadProgram(str(binary))

        self.debug_session.target.restart()

    def run(self):
        self.debug_session.target.runAsynch()

    def restart(self):
        self.debug_session.target.reset()
        self.debug_session.target.runAsynch()
