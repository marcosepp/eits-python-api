import regex as re
import csv
import json
import os
from lxml import etree
from os.path import join, dirname
from dotenv import load_dotenv

from eits_python_api import (
    logging_conf,
    ApiModuleContent,
    JsonMeasure,
    JsonModule,
    CsvMeasure,
    EITSType,
    ValueErrorMeasureCodeMismatch,
    ValueErrorMeasureTitleMismatch,
    ValueErrorModuleCodeMismatch,
    ValueErrorModuleTitleMismatch,
)

LOGGER = logging_conf.LOGGER


def validate_eits_pattern(string: str, type: EITSType):
    """
    Validates the string against the specified EITSType pattern.

    Args:
        string (str): The string to validate.
        type (EITSType): The EITS pattern type.

    Raises:
        ValueErrorMeasureCodeMismatch: If the string does not \
            match MEASURE_CODE.
        ValueErrorMeasureTitleMismatch: If the string does not \
            match MEASURE_TITLE.
        ValueErrorModuleCodeMismatch: If the string does not \
            match MODULE_CODE.
        ValueErrorModuleTitleMismatch: If the string does not \
            match MODULE_TITLE.
    """
    if not re.match(type.value, string):
        match type:
            case EITSType.MEASURE_CODE | EITSType.MEASURE_CODE_RAW:
                raise ValueErrorMeasureCodeMismatch(
                    f"Invalid pattern. String '{string}' doesn't match "
                    + f"{type.name} format."
                )
            case EITSType.MEASURE_TITLE | EITSType.MEASURE_TITLE_RAW:
                raise ValueErrorMeasureTitleMismatch(
                    f"Invalid pattern. String '{string}' doesn't match "
                    + f"{type.name} format."
                )
            case EITSType.MODULE_CODE | EITSType.MODULE_CODE_RAW:
                raise ValueErrorModuleCodeMismatch(
                    f"Invalid pattern. String '{string}' doesn't match "
                    + f"{type.name} format."
                )
            case EITSType.MODULE_TITLE | EITSType.MODULE_TITLE_RAW:
                raise ValueErrorModuleTitleMismatch(
                    f"Invalid pattern. String '{string}' doesn't match "
                    + f"{type.name} format."
                )
            case _:
                raise ValueError(f"Wrong EITSType: {type}")
    else:
        LOGGER.debug(
            f"Valid pattern. String '{string}' matches "
            + f"{type.name} format."
        )


def create_module_object(
    module_details: ApiModuleContent, __risks: dict, html: bool
) -> JsonModule:
    """
    Constructs a JsonModule object from ApiModuleContent data.

    Args:
        module_details (ApiModuleContent): Module data from API.
        __risks (dict): Dictionary of risks to associate with the module.
        html (bool): Include HTML content in descriptions.

    Returns:
        JsonModule: The constructed JsonModule object.
    """
    measures: list[JsonMeasure] = []

    for measure_group in module_details.measureDetails:
        LOGGER.debug(
            "Creating JSON objects for measure group "
            + f"'{measure_group.groupTitle}' in module "
            + f"'{module_details.moduleTitle}'"
        )
        for measure in measure_group.measures:
            LOGGER.debug(
                f"Creating JSON objects for measure '{measure.measureTitle}'"
            )
            try:
                validate_eits_pattern(
                    measure.measureCode, EITSType.MEASURE_CODE_RAW
                )
                validate_eits_pattern(
                    measure.measureTitle, EITSType.MEASURE_TITLE_RAW
                )
            except ValueErrorMeasureCodeMismatch as ve:
                LOGGER.debug(ve)
            except ValueErrorMeasureTitleMismatch as ve:
                LOGGER.debug(ve)
            except ValueError as ve:
                LOGGER.debug(ve)

            code = fix_codes(measure.measureCode)

            measures.append(
                JsonMeasure(
                    code=code,
                    title=fix_titles(
                        measure.measureTitle,
                        measure.measureCode,
                        measure.securityCodes,
                    ),
                    description=(
                        measure.body
                        if html
                        else remove_html_tags(measure.body)
                    ),
                    security_code="".join(measure.securityCodes),
                    assignees=measure.assignees,
                    module_code=fix_codes(module_details.moduleCode),
                    group=get_group_name(measure_group.groupCode),
                    risks=get_risks(code, __risks),
                )
            )

    LOGGER.debug(
        f"Creating JSON objects for module '{module_details.moduleTitle}'"
    )
    try:
        validate_eits_pattern(
            module_details.moduleCode, EITSType.MODULE_CODE_RAW
        )
        validate_eits_pattern(
            module_details.moduleTitle, EITSType.MODULE_TITLE_RAW
        )
    except ValueErrorModuleCodeMismatch as ve:
        LOGGER.debug(ve)
    except ValueErrorModuleTitleMismatch as ve:
        LOGGER.debug(ve)
    except ValueError as ve:
        LOGGER.debug(ve)
    module: JsonModule = JsonModule(
        code=fix_codes(module_details.moduleCode),
        title=fix_titles(
            module_details.moduleTitle, module_details.moduleCode
        ),
        purpose=(
            module_details.description[0].content
            if html
            else remove_html_tags(module_details.description[0].content)
        ),
        responsibility=(
            module_details.description[1].content
            if html
            else remove_html_tags(module_details.description[1].content)
        ),
        limits=(
            module_details.description[2].content
            if html
            else remove_html_tags(module_details.description[2].content)
        ),
        additional_info=(
            module_details.additionalInfo
            if html
            else remove_html_tags(module_details.additionalInfo)
        ),
        risks=module_details.risks,
        measures=measures,
    )
    return module


def create_csv_object(module: ApiModuleContent) -> list[dict]:
    """
    Generates a list of dictionaries for CSV from ApiModuleContent.

    Args:
        module (ApiModuleContent): Module data from API.

    Returns:
        list[dict]: List of dictionaries for CsvMeasure objects.
    """
    result: list[dict] = []
    measure_groups = module.measureDetails

    for measure_group in measure_groups:
        group_name = get_group_name(measure_group.groupCode)

        measures = measure_group.measures
        for measure in measures:
            csv_measure = CsvMeasure(
                catalog_version=module.version,
                module_valid_from=module.validFrom,
                module_valid_to=module.validTo,
                module_purpose=remove_html_tags(
                    module.description[0].content.replace("\n", "\\n")
                ),
                module_responsibility=remove_html_tags(
                    module.description[1].content.replace("\n", "\\n")
                ),
                module_limits=remove_html_tags(
                    module.description[2].content.replace("\n", "\\n")
                ),
                module_additional_info=remove_html_tags(
                    module.additionalInfo.replace("\n", "\\n")
                ),
                module_code=module.moduleCode,
                module_title=module.moduleTitle,
                measure_code=measure.measureCode,
                measure_title=measure.measureTitle,
                measure_group=group_name,
                measure_body=remove_html_tags(
                    measure.body.replace("\n", "\\n")
                ),
                measure_assignees=", ".join(measure.assignees),
                measure_security_codes="".join(measure.securityCodes),
            )
            result.append(csv_measure.model_dump())

    return result


def remove_html_tags(string: str) -> str:
    """
    Strips HTML tags from the provided string.

    Args:
        string (str): String with potential HTML tags.

    Returns:
        str: String without HTML tags.
    """
    if not isinstance(string, str):
        raise TypeError("Expected string as input.")
    LOGGER.debug(f"Removing HTML tags from '{string}'")
    return (
        etree.tostring(
            etree.fromstring(string, etree.HTMLParser()),
            encoding="unicode",
            method="text",
        )
        if string
        else ""
    )


def fix_titles(title: str, code: str, security_codes: list[str] = []) -> str:
    """
    Cleans up titles by removing unnecessary info and formatting.

    Args:
        title (str): Original title to clean.
        code (str): Code for proper formatting.
        security_codes (list[str], optional): List of security codes.

    Returns:
        str: Cleaned title formatted for JSON.
    """
    LOGGER.debug(f"Fixing title '{title}' and code '{code}'")
    security_codes_string = "-".join(security_codes)
    clean_title = remove_strings_between_brackets_and_square_brackets(
        title, security_codes_string
    )

    if f"{code}: " in clean_title:
        return clean_title
    return add_colon_before_first_whitespace(clean_title)


def fix_codes(code: str) -> str:
    """
    Cleans up codes by removing extraneous characters.

    Args:
        code (str): Code string to fix.

    Returns:
        str: Cleaned code string.
    """
    if " " in code:
        LOGGER.debug(f"Fixing code '{code}'")
        return remove_whitespace_and_text_after_whitespace(code)
    return code


def remove_strings_between_brackets_and_square_brackets(
    title: str, security_codes: str
) -> str:
    """
    Removes text within brackets from the title string.

    Args:
        title (str): Title potentially containing brackets.
        security_codes (str): Security codes to consider.

    Returns:
        str: Title without brackets and their contents.
    """

    LOGGER.debug(f"Removing [] brackets from '{title}'.")
    title = re.sub(re.compile(r"\[[^]]+\]"), "", title).strip()

    security_code_pattern = r"\((?:[CIA]{1,})(?:[-IA\)]{1,})*$"

    if (
        re.search(security_code_pattern, title.strip())
        and f"{security_codes.lower()}" in title.lower()
    ):
        LOGGER.debug(
            f"Removing security code '{security_codes}' from '{title}'."
        )
        # New

        title = re.sub(
            re.compile(security_code_pattern), "", title.strip()
        ).strip()

    return title


def add_colon_before_first_whitespace(title: str) -> str:
    """
    Inserts a colon before the first whitespace in the title.

    Args:
        title (str): Title string to modify.

    Returns:
        str: Title with a colon added before the first whitespace.
    """
    LOGGER.debug(f"Adding colon to '{title}'")
    if not isinstance(title, str):
        raise TypeError("Title must be a string.")
    code, *title_parts = title.split(" ", 1)
    return f"{code}: {' '.join(title_parts)}"


def remove_tab_and_text_after_tab(string: str) -> str:
    """
    Removes the tab character and any text following it.

    Args:
        string (str): String to clean.

    Returns:
        str: Cleaned string without the tab and following text.
    """
    if not isinstance(string, str):
        raise TypeError("Input must be a string.")
    if "\t" in string:
        LOGGER.debug(f"Removing tab from '{string}'")
        return string.split("\t")[0]
    return string


def remove_whitespace_and_text_after_whitespace(string: str) -> str:
    """
    Removes whitespace and any text following it.

    Args:
        string (str): String to clean.

    Returns:
        str: Cleaned string without whitespace and following text.
    """
    if not isinstance(string, str):
        raise TypeError("Input must be a string.")
    if " " in string:
        LOGGER.debug(f"Removing whitespace and extra text from '{string}'")
        return string.split(" ")[0]
    return string


def get_group_name(code: str) -> str:
    """
    Retrieves the group name for a specific group ID. \
        "3.2" -> "Põhimeede"
        "3.3" -> "Standardmeede"
        "3.4" -> "Kõrgmeede"

    Args:
        code (str): Group ID.

    Returns:
        str: Group name associated with the ID.
    """
    if not isinstance(code, str):
        raise TypeError("Input must be a string.")
    LOGGER.debug(f"Matching group for '{code}'")
    match code:
        case "3.2":
            result: str = "Põhimeede"
            LOGGER.debug(f"Returning '{result}'")
            return result
        case "3.3":
            result: str = "Standardmeede"
            LOGGER.debug(f"Returning '{result}'")
            return result
        case "3.4":
            result: str = "Kõrgmeede"
            LOGGER.debug(f"Returning '{result}'")
            return result
        case _:
            result: str = ""
            LOGGER.debug(f"Returning '{result}'")
            return result


def get_risks(code: str, risks_in: dict) -> list[str] | None:
    """
    Retrieves risk codes associated with a given E-ITS measure code.

    Args:
        code (str): E-ITS measure code.
        risks_in (dict): Dictionary containing risk codes.

    Returns:
        list[str]: List of risk codes or None if not found.
    """
    try:
        risks: list[str] = risks_in[code]
    except KeyError as ke:
        LOGGER.warning(
            f"KeyError [{ke}]: Measure doesn't have risks in risk table."
        )
        return None

    LOGGER.debug(f"Getting risks for {code}")
    return risks


def load_environment_variables() -> None:
    """
    Loads environment variables from a .env file for configuration.
    """
    dotenv_path = join(dirname(__file__), "../../.env")
    if os.path.isfile(dotenv_path):
        load_dotenv(dotenv_path, override=True)
        LOGGER.debug(f"Using .env file from {dotenv_path}")
    else:
        LOGGER.debug(f"Didn't get .env file from {dotenv_path}")


def get_boolean_from_environment_string(
    env_str: str, env_str_default: str = "False"
) -> bool:
    """
    Converts the environment variable value to a boolean.

    Args:
        env_str (str): Name of the environment variable.
        env_str_default (str, optional): Default value if not set. \
            Defaults to "False".

    Returns:
        bool: Boolean representation of the variable's value.
    """
    __env_str: str = os.environ.get(env_str, env_str_default)
    if __env_str.lower() == "True".lower():
        return True
    else:
        return False


def save_json(data: list[dict], file: str) -> None:
    """
    Saves data as a JSON file.

    Args:
        data (list[dict]): Data to save.
        file (str): Filename for the JSON output.
    """
    LOGGER.info(f"Saving JSON output to {file}")
    with open(file, mode="w", newline="", encoding="utf-8") as outfile:
        outfile.write(json.dumps(data, indent=4, ensure_ascii=False))


def save_csv(data: list[dict], file: str) -> None:
    """
    Saves data as a CSV file.

    Args:
        data (list[dict]): Data to save.
        file (str): Filename for the CSV output.
    """
    LOGGER.info(f"Saving CSV output to {file}")
    with open(file, mode="w", newline="", encoding="utf-8") as file:
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(
            file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL
        )

        writer.writeheader()
        writer.writerows(data)
