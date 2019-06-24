"""
Copyright (C) 2014 Adobe
"""

import argparse
import os
import sys

from buildrunner import (
    __version__,
    BuildRunner,
    BuildRunnerConfigurationError,
)


def parse_args(argv):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description='buildrunner runs builds defined in buildrunner.yaml'
    )

    parser.add_argument(
        '-c', '--global-config',
        default=None,
        dest='global_config_file',
        help='global configuration file (defaults to "~/.buildrunner.yaml")',
    )

    parser.add_argument(
        '-d', '--directory',
        default=os.getcwd(),
        dest='directory',
        help='build directory (defaults to current working directory)',
    )

    parser.add_argument(
        '-f', '--file',
        default=None,
        dest='config_file',
        #pylint: disable=C0301
        help='build configuration file (defaults to "buildrunner.yaml", then "gauntlet.yaml")',
    )

    parser.add_argument(
        '-n', '--build-number',
        default=None,
        dest='build_number',
        help='build number (defaults to unix/epoch time)',
    )

    parser.add_argument(
        '--push',
        default=False,
        action='store_true',
        dest='push',
        #pylint: disable=C0301
        help='push images to remote registries (without this flag buildrunner simply tags images)',
    )

    parser.add_argument(
        '--keep-images',
        default=False,
        action='store_true',
        dest='keep_images',
        #pylint: disable=C0301
        help='keep generated images at the end of the build (images are by default deleted to prevent clutter on build machines)',
    )

    parser.add_argument(
        '--keep-step-artifacts',
        default=False,
        action='store_true',
        dest='keep_step_artifacts',
        # pylint: disable=C0301
        help='keep artifacts generated for each step of the build (step artifacts are by default deleted to prevent clutter on build machines)',
    )

    parser.add_argument(
        '-s', '--steps',
        default=[],
        dest='steps',
        action='append',
        #pylint: disable=C0301
        help='only run the listed steps (use the argument multiple times or specify as comma-delimited)',
    )

    parser.add_argument(
        '--publish-ports',
        default=False,
        action='store_true',
        dest='publish_ports',
        #pylint: disable=C0301
        help='publish ports defined on a run step, this should never be used on a build server',
    )

    parser.add_argument(
        '--disable-timestamps',
        default=False,
        action='store_true',
        dest='disable_timestamps',
        #pylint: disable=C0301
        help='disables printing of timestamps in the logging output',
    )

    parser.add_argument(
        '--version',
        default=False,
        action='store_true',
        dest='print_version',
        #pylint: disable=C0301
        help='print the current buildrunner version and exit',
    )

    parser.add_argument(
        '--no-color',
        default=False,
        action='store_true',
        dest='no_log_color',
        #pylint: disable=C0301
        help='disable colors when logging',
    )

    parser.add_argument(
        '--log-generated-files',
        default=False,
        action='store_true',
        dest='log_generated_files',
        #pylint: disable=C0301
        help='logs the Jinja generated file contents',
    )

    args = parser.parse_args(argv[1:])

    # Only absolute directories can do a mount bind
    args.directory = os.path.realpath(args.directory)

    _steps = []
    for _step in args.steps:
        _steps.extend(_step.split(','))
    args.steps = _steps

    return args


def main(argv):
    """Main program execution."""
    args = parse_args(argv)

    # are we just printing the version?
    if args.print_version:
        print __version__
        return os.EX_OK

    try:
        build_runner = BuildRunner(
            args.directory,
            global_config_file=args.global_config_file,
            run_config_file=args.config_file,
            build_number=args.build_number,
            push=args.push,
            colorize_log=not args.no_log_color,
            cleanup_images=not args.keep_images,
            cleanup_step_artifacts=not args.keep_step_artifacts,
            steps_to_run=args.steps,
            publish_ports=args.publish_ports,
            log_generated_files=args.log_generated_files,
        )
        build_runner.run()
        if build_runner.exit_code:
            return build_runner.exit_code
    except BuildRunnerConfigurationError as brce:
        print str(brce)
        return os.EX_CONFIG
    return os.EX_OK


if __name__ == '__main__':
    sys.exit(main(sys.argv))