import pathlib
import tempfile

import python_minifier
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class MinifyHook(BuildHookInterface):
    """Minify phew's Python before it goes into the sdist or wheel."""

    PLUGIN_NAME = "custom"

    def initialize(self, version, build_data):
        self._tmp = tempfile.TemporaryDirectory()
        out = pathlib.Path(self._tmp.name)

        for source in pathlib.Path(self.root, "phew").glob("*.py"):
            minified = python_minifier.minify(
                source.read_text(),
                filename=str(source),
                remove_literal_statements=True,
            )
            target = out / source.name
            target.write_text(minified)
            build_data["force_include"][str(target)] = f"phew/{source.name}"
            self.app.display_info(
                f"minified phew/{source.name} "
                f"{source.stat().st_size} -> {target.stat().st_size} bytes"
            )

    def finalize(self, version, build_data, artifact_path):
        self._tmp.cleanup()
