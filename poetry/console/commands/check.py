from trove_classifiers import classifiers
from trove_classifiers import deprecated_classifiers

from poetry.core.pyproject.toml import PyProjectTOML
from poetry.factory import Factory
from poetry.utils._compat import Path

from .command import Command


class CheckCommand(Command):

    name = "check"
    description = "Checks the validity of the <comment>pyproject.toml</comment> file."

    def handle(self):
        # Load poetry config and display errors, if any
        poetry_file = Factory.locate(Path.cwd())
        config = PyProjectTOML(poetry_file).poetry_config
        check_result = Factory.validate(config, strict=True)

        unrecognized = sorted(
            set(config.get("classifiers", []))
            - set(classifiers)
            - set(deprecated_classifiers)
        )
        if unrecognized:
            check_result["errors"].append(
                "Unrecognized classifiers: {}.".format(", ".join(unrecognized))
            )

        deprecated = sorted(
            set(config.get("classifiers", [])).intersection(set(deprecated_classifiers))
        )
        if deprecated:
            for old_classifier in deprecated:
                message = 'Deprecated classifiers "{}".'.format(old_classifier)
                new_classifier = deprecated_classifiers[old_classifier]
                if new_classifier:
                    message += ' Must be replaced by "{}".'.format(new_classifier)
                else:
                    message += " Must be removed."
                check_result["warnings"].append(message)

        if not check_result["errors"] and not check_result["warnings"]:
            self.info("All set!")

            return 0

        for error in check_result["errors"]:
            self.line("<error>Error: {}</error>".format(error))

        for error in check_result["warnings"]:
            self.line("<warning>Warning: {}</warning>".format(error))

        return 1
