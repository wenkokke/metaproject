import click
import jinja2
import jinja2.meta
import pathlib
import typing

PathTemplate = jinja2.Template

ContentsTemplate = jinja2.Template


class FileTemplate:
    template_path: pathlib.Path
    path_template: PathTemplate
    contents_template: ContentsTemplate
    variables: set[str]

    def __init__(
        self,
        template_path: pathlib.Path,
        *,
        template_dir: typing.Optional[pathlib.Path] = None,
        env: typing.Optional[jinja2.Environment] = None,
    ):
        # Save the template path
        self.template_path = template_path

        # Use default environment
        env = env or jinja2.Environment()

        # Create the path_template
        if template_dir:
            path_template_str = str(template_path.relative_to(template_dir))
        else:
            path_template_str = str(template_path)
        self.path_template = env.from_string(source=path_template_str)

        # Create the contents_template
        contents_template_str = template_path.read_text()
        self.contents_template = env.from_string(source=contents_template_str)

        # Store variables used in path_template and contents_template
        self.variables = set(
            (
                *jinja2.meta.find_undeclared_variables(env.parse(path_template_str)),
                *jinja2.meta.find_undeclared_variables(
                    env.parse(contents_template_str)
                ),
            )
        )

    def output_path(self, context: typing.Any) -> pathlib.Path:
        return pathlib.Path(self.path_template.render(context))

    def output_file_contents(self, context: typing.Any) -> str:
        return self.contents_template.render(context)


class Template:
    file_templates: typing.Sequence[FileTemplate]

    def __init__(
        self,
        template_dir: pathlib.Path,
        *,
        env: typing.Optional[jinja2.Environment] = None,
    ):
        self.file_templates = []
        for template_path in template_dir.glob("**/*"):
            if (
                template_path.is_file()
                and template_path.name != "metaproject-config.yaml"
            ):
                self.file_templates.append(
                    FileTemplate(template_path, template_dir=template_dir, env=env)
                )

    def init(self, **context):
        # Render file paths:
        output_paths = []
        for file_template in self.file_templates:
            output_paths.append(str(file_template.output_path(context)))

        # Ask for confirmation:
        click.confirm(
            "\n".join(
                [
                    "Create the following files?",
                    *output_paths,
                ]
            )
        )

        for file_template in self.file_templates:
            # Render file path:
            output_path = file_template.output_path(context)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # Render file contents:
            output_contents = file_template.output_file_contents(context)
            output_path.write_text(output_contents)
