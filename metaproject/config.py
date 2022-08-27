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

    def get_prompt(self) -> str:
        return f"Enter {' '.join(self.name.split('_'))}"

    def get_default(self) -> typing.Optional[str]:
        if isinstance(self.default, DefaultConfig):
            try:
                self.default = subprocess.getoutput(self.default.shell)
            except subprocess.CalledProcessError:
                return None
        return self.default

    def option(self) -> click.Option:
        if self.has_default:
            return click.Option(
                param_decls=[f"--{self.name}"],
                prompt=self.get_prompt(),
                default=self.get_default(),
            )
        else:
            return click.Option(
                param_decls=[f"--{self.name}"],
                prompt=self.get_prompt(),
            )


@dataclass
class Config:
    name: str
    variables: list[VariableConfig] = field(default_factory=list)

    @staticmethod
    def load(path: typing.Union[str, pathlib.Path]) -> "Config":
        if isinstance(path, str):
            path = pathlib.Path(path)
        contents = yaml.safe_load(path.read_text())
        variables = []
        name = contents["name"]
        for variable_dict in contents["variables"]:
            variables.append(VariableConfig.from_dict(variable_dict))
        return Config(name=name, variables=variables)

    def option_parser(self, ctx: click.Context) -> click.OptionParser:
        """
        Create a click option parser for a given variable spec.
        """
        option_parser = click.OptionParser(ctx)
        for spec in self.variables:
            spec.option().add_to_parser(option_parser, ctx)
        return option_parser

    def command(self, **kwargs) -> click.Command:
        """
        Create a click option parser for a given variable spec.
        """
        return click.Command(
            name=self.name,
            params=[spec.option() for spec in self.variables],
            **kwargs,
        )