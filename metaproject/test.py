from .config import Config
from .template import Template


def test(config: Config, template: Template) -> None:
    variable_names = set(variable.name for variable in config.variables)
    for file_template in template.file_templates:
        for variable_name in file_template.variables:
            assert (
                variable_name in variable_names
            ), f"Undefined variable '{variable_name}' in {file_template.template_path}"
