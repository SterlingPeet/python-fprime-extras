""" Entry point to the JPL FPLINT linting script

This is the main entry point to the fplint script.
"""
import argparse
import glob
import logging
import sys
from pathlib import Path

import fprime_extras.lint.migrations.checks  # noqa: F401
from fprime_extras.lint.migrations.check import CheckBase
from fprime_extras.lint.migrations.config import ConfigurationException
from fprime_extras.lint.migrations.config import load_configuration
from fprime_extras.lint.migrations.model.patcher import InconsistencyException
from fprime_extras.lint.migrations.model.patcher import load_patched_topology

log = logging.getLogger(__name__)


def main():
    """ Entry point to the fplint code"""
    parser = argparse.ArgumentParser(
        description="A linting module for F´ topologies")
    parser.add_argument("--config", type=argparse.FileType("r"),
                        help="Configuration YAML file to read linting configuration. Default: fplint.yml, if available")
    parser.add_argument(
        "model", nargs='?', help="Topology model to run linting against. **/*TopologyAppAi.xml")

    # Allow checks to require additional inputs.
    # TODO: is this the best way to handel needing extra inputs
    # TODO: almost certainly not.
    for key, vals in CheckBase.get_all_extra_args().items():
        parser.add_argument("--" + key, **vals)
    arguments = parser.parse_args()

    # Load defailt fplint.yml file of ./fplint.yml
    if arguments.config is None and Path("fplint.yml").exists():
        arguments.config = open(Path("fplint.yml"), "r")

    # Attempt to find a topology model to verify if not specified by looking for matching children files
    if not arguments.model:
        globs = glob.glob("**/*TopologyAppAi.xml", recursive=True)
        if len(globs) != 1:
            log.error("[ERROR] Found {} toplogies matching **/*TopologyAppAi.xml in current working directory"
                      .format("no" if not globs else "too many"))
            sys.exit(1)
        arguments.model = globs[0]

    # Loads configuration and check that configuration matches available code
    try:
        # Note: load config after all imports have been done
        config = load_configuration(arguments.config, list(
            CheckBase.get_all_identifiers([])))
    except ConfigurationException as exc:
        log.error("[ERROR] {}".format(exc))
        sys.exit(1)

    # Try to load the model and  report errors if it fails to load a consistent model
    # TODO: XML linting checks should clear up any errors here.  Can we get them to run first, before loading models?
    try:
        topology_model = load_patched_topology(Path(arguments.model))
    except InconsistencyException as inc:
        log.error("[ERROR] Loading model detected specification error {}".format(
            inc))
        sys.exit(1)

    # Run all topology model checking
    success = CheckBase.run_all(topology_model, excluded=config.get("exclusions", []),
                                filters=config.get("filters", []), arguments=arguments)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
