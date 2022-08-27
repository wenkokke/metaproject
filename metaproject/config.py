import click
import pathlib
import subprocess
import typing
import yaml

from click.decorators import FC
from collections.abc import Callable
from dataclasses import dataclass, field
from dataclasses_json import config, DataClassJsonMixin
from dataclasses_json.core import Json


@dataclass
class DefaultConfig(DataClassJsonMixin):
    shell: str

    @staticmethod
    def encoder(
        default_spec: typing.Union[None, str, "DefaultConfig"],
    ) -> Json:
        if default_spec is None or isinstance(default_spec, str):
            return default_spec
        elif isinstance(default_spec, dict):
            return DefaultConfig.to_dict(default_spec)
        else:
            raise TypeError(default_spec)

    @staticmethod
    def decoder(
        kvs: Json,
    ) -> typing.Union[None, str, "DefaultConfig"]:
        if kvs is None or isinstance(kvs, str):
            return kvs
        elif isinstance(kvs, dict):
            return DefaultConfig.from_dict(kvs)
        else:
            raise TypeError(kvs)


@dataclass
class VariableConfig(DataClassJsonMixin):
    name: str
    default: typing.Union[None, str, DefaultConfig] = field(
        default=None,
        metadata=config(decoder=DefaultConfig.decoder, encoder=DefaultConfig.encoder),
    )

    @property
    def has_default(self) -> bool:
        return self.default is not None

    @property
    def prompt(self) -> str:
        return f"Enter {' '.join(self.name.split('_'))}"

    def get_default(self) -> typing.Optional[str]:
        if isinstance(self.default, DefaultConfig):
            self.default = subprocess.getoutput(self.default.shell)
        return self.default

    def option(self) -> click.Option:
        if self.has_default:
            return click.Option(
                f"--{self.name}",
                prompt=self.prompt,
                default=self.get_default(),
            )
        else:
            return click.Option(
                f"--{self.name}",
                prompt=self.prompt,
            )


@dataclass
class Config:
    variables: list[VariableConfig] = field(default_factory=list)

    def load(self, path: typing.Union[str, pathlib.Path]):
        if isinstance(path, str):
            path = pathlib.Path(path)
        contents = yaml.safe_load(path.read_text())
        for variable_dict in contents["variables"]:
            self.variables.append(VariableConfig.from_dict(variable_dict))

    def command(self, **kwargs) -> click.Command:
        """
        Create a click option parser for a given variable spec.
        """
        params: list[click.Parameter] = [spec.option() for spec in self.variables]
        print(params)
        return click.Command(
            name="init_project",
            params=params,
            **kwargs,
        )
