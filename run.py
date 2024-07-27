from time import perf_counter

from eits_python_api import EITSApi, common, logging_conf

LOGGER = logging_conf.setup_logger(__name__)


def main() -> None:
    """
    Main function to generate usable JSON from EITS2 API.

    This function initializes the EITSApi class, retrieves \
        modules and measures, retrieves risks, and saves the data \
            to JSON files.
    """
    eits_api = EITSApi()

    modules = eits_api.get_modules_and_measures()
    risks = eits_api.get_risks()

    modules_output_file: str = eits_api.output
    risks_output_file: str = "risks.json"

    common.save_json(modules, modules_output_file)
    common.save_json(risks, risks_output_file)


if __name__ == "__main__":
    start_time = perf_counter()
    main()
    LOGGER.info(f"Total time: {(perf_counter() - start_time):.2f} seconds.")
