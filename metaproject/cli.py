import os
from pathlib import Path
import click
import itertools
import sys
import tempfile
import wget
import zipfile

from metaproject.test import test

from .config import Config
from .template import Template


@click.group(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
)
@click.pass_context
def cli(ctx: click.Context) -> None:
    pass


@cli.command(
    name="init",
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    ),
)
@click.pass_context
@click.argument("repo", type=str)
def init(
    ctx: click.Context,
    repo: str,
) -> None:
    with tempfile.TemporaryDirectory(prefix="metaproject") as temp_dir:

        # Download repository zipfile from GitHub:
        repo_zip_file = wget.download(
            url=f"https://github.com/{repo}/archive/refs/heads/dev.zip",
            out=f"{temp_dir}/{repo.replace('/','_')}.zip",
            bar=lambda current, total, width: (),
        )

        # Extract repository zipfile from GitHub:
        repo_zip_obj = zipfile.ZipFile(repo_zip_file)
        repo_zip_obj.extractall(path=temp_dir)

        # Parse metaproject configuration:
        template_dir: Path
        config: Config
        for config_path in Path(temp_dir).glob(f"*/metaproject-config.yaml"):
            template_dir = config_path.parent
            config = Config.load(config_path)

        # Parse metaproject template:
        template: Template = Template(template_dir)

        # Verify metaproject:
        test(config, template)

        command = config.command(callback=template.init)
        command.parse_args(ctx, ctx.args)
        command.invoke(ctx)


if __name__ == "__main__":
    cli()


# confirmation_dialog = "\n".join(
#     [
#         "Initialize project with the following options:",
#         "\n".join([f"{key}: {val}" for key, val in kwargs.items()]),
#         "Ok?",
#     ]
# )
# click.confirm(text=confirmation_dialog)
# output_dir = pathlib.Path(__file__).parent.parent
# template_dir = pathlib.Path(__file__).parent / ".template"
# env = jinja2.Environment()
# for template_path in template_dir.glob("**/*"):
#     output_path_template: str = str(
#         template_path.relative_to(template_dir)
#     ).replace(".jinja2", "")
#     output_path = env.from_string(source=output_path_template).render(**kwargs)
#     print(f"{output_path_template} -> {output_path}")
#     output_path = project_dir / output_path
#     if template_path.is_dir():
#         output_path.mkdir(parents=True, exist_ok=True)
#     else:
#         output_path_contents = env.get_template(output_path_template).render(**kwargs)
#         output_path.write_text(output_path_contents)
