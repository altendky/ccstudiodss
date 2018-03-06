from __future__ import unicode_literals

import os
import subprocess

import attr

import ccstudiodss.jenv


def join_path_lists(*path_lists):
    s = os.pathsep.join(
        path_list.strip(os.pathsep)
        for path_list in path_lists
    )

    return s.strip(os.pathsep)


relative_jar_paths = (
    'DebugServer/packages/ti/dss/java/dss.jar',
    (
        'DebugServer/packages/ti/dss/java/'
        'com.ti.ccstudio.scripting.environment_3.1.0.jar'
    ),
    'DebugServer/packages/ti/dss/java/com.ti.debug.engine_1.0.0.jar',
    'dvt/scripting/dvt_scripting.jar',
)


def jar_paths(base_path, relative=relative_jar_paths):
    return tuple(
        os.path.join(base_path, path)
        for path in relative
    )


@attr.s
class Session:
    base_path = attr.ib()
    cli_path = attr.ib(
        default=os.path.join(ccstudiodss.jenv.jenv_bin_path(), 'ccstudiodss'),
    )

    def load(self, ccxml, binary):
        env = dict(os.environ)
        env['CLASSPATH'] = join_path_lists(
            os.environ.get('CLASSPATH', ''),
            os.pathsep.join(jar_paths(base_path=self.base_path))
        )

        subprocess.run(
            [
                self.cli_path,
                'load',
                '--ccxml', ccxml,
                '--binary', binary,
            ],
            check=True,
            env=env,
        )
