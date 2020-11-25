import contextlib
import enum
import os
import pathlib
import shutil
import subprocess

import attr
try:
    import jpype
except ImportError:
    jpype = None

if jpype is not None:
    import jpype.imports

import lxml.etree

import ccstudiodss.utils


class BuildTypes(enum.Enum):
    incremental = enum.auto()
    full = enum.auto()
    clean = enum.auto()


def add_jars(base_path=None):
    if base_path is None:
        base_path = ccstudiodss.utils.find_base_path()

    for jar in jar_paths(base_path=base_path):
        if jar not in jpype.getClassPath().split(os.pathsep):
            jpype.addClassPath(ccstudiodss.utils.fspath(jar))


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
    device_pattern = attr.ib(default='.*')

    def __enter__(self):
        jpype.startJVM()
        import com.ti.ccstudio.scripting.environment

        try:
            self.script = (
                com.ti.ccstudio.scripting.environment.ScriptingEnvironment.instance()
            )

            self.debug_server = self.script.getServer("DebugServer.1")
            self.debug_server.setConfig(ccstudiodss.utils.fspath(self.ccxml))

            self.debug_session = self.debug_server.openSession(self.device_pattern)

            self.debug_session.target.connect()
        except:
            jpype.shutdownJVM()

            raise

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.debug_session.target.disconnect()
            self.debug_server.stop()
        finally:
            jpype.shutdownJVM()

    @contextlib.contextmanager
    def temporary_timeout(self, timeout):
        old_timeout = self.script.getScriptTimeout()
        self.script.setScriptTimeout(timeout * 1000)
        yield
        self.script.setScriptTimeout(old_timeout)

    def load(self, binary, timeout=150):
        with self.temporary_timeout(timeout):
            self.debug_session.memory.loadProgram(
                ccstudiodss.utils.fspath(binary)
            )

        self.debug_session.target.restart()

    def run(self):
        self.debug_session.target.runAsynch()

    def restart(self):
        self.debug_session.target.reset()
        self.debug_session.target.runAsynch()


def build(target, build_type, project_root, project_name, suffix=None):
    if project_name is None:
        project_name = pathlib.Path(project_root).parts[-1]

    workspace = ccstudiodss.utils.generated_workspace_path(
        project_root=project_root,
        suffix=suffix,
    )

    workspace.mkdir(parents=True, exist_ok=True)

    base_command = (
        ccstudiodss.utils.fspath(ccstudiodss.utils.find_executable()),
        '-noSplash',
        '-data', ccstudiodss.utils.fspath(workspace),
    )

    if not any(True for _ in workspace.iterdir()):
        subprocess.run(
            [
                *base_command,
                '-application', 'com.ti.ccstudio.apps.projectImport',
                '-ccs.location', ccstudiodss.utils.fspath(project_root),
                '-ccs.renameTo', project_name,
            ],
            check=True,
        )

    subprocess.run(
        [
            *base_command,
            '-application', 'com.ti.ccstudio.apps.projectBuild',
            '-ccs.projects', project_name,
            '-ccs.configuration', target,
            '-ccs.buildType', build_type.name,
        ],
        check=True,
    )

    return pathlib.Path(project_root)/target/(project_name + '.out')


def remove_generated_directory(project_root, suffix=None):
    path = ccstudiodss.utils.generated_project_root(
        project_root=project_root,
        suffix=suffix,
    )
    shutil.rmtree(ccstudiodss.utils.fspath(path))


def remove_generated_directories():
    path = ccstudiodss.utils.generated_path_root()
    shutil.rmtree(ccstudiodss.utils.fspath(path))


def get_cproject_targets_from_path(path):
    with open(path) as f:
        return get_cproject_targets(f)


def get_cproject_targets(file):
    tree = lxml.etree.parse(file)
    targets = tree.xpath(
        '//storageModule[@moduleId="org.eclipse.cdt.core.settings"]/@name',
    )
    return targets
