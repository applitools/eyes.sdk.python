from argparse import ArgumentParser


def init_config_command(_):
    from . import utils

    utils.copy_config_to(".")


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
    return parser


args = cli_parser().parse_args()
args.command(args)
