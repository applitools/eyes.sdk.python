from argparse import ArgumentParser


def init_config_command(_):
    from . import utils

    utils.copy_config_to(".")


def lint_config_command(namespace):
    from . import config_parser

    config_parser.try_verify_configuration(namespace.config)


def cli_parser():
    parser = ArgumentParser(
        prog="python -m EyesLibrary",
        description="Applitools Eyes Robot Framework support library",
    )
    parser.set_defaults(command=lambda _: parser.print_help())
    commands = parser.add_subparsers()
    init_config = commands.add_parser(
        "init-config",
        description="Create default config file",
        help="Create default config file",
    )
    init_config.set_defaults(command=init_config_command)

    lint_config = commands.add_parser(
        "lint-config",
        description="Verify that `applitools.yaml` config is correct",
        help="Verify that `applitools.yaml` config is correct",
    )
    lint_config.add_argument("config", default="applitools.yaml")
    lint_config.set_defaults(command=lint_config_command)
    return parser


args = cli_parser().parse_args()
args.command(args)
