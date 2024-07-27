import asyncio
import os
from typing import Any
from bs4 import BeautifulSoup

from eits_python_api import (
    ApiCatalog,
    ApiDiffCatalog,
    ApiModuleContent,
    ApiModuleGroup,
    ApiModule,
    ApiMeasureDetail,
    JsonModule,
    common,
    logging_conf,
    AsyncAPIBase,
    JsonRisk,
)
from eits_python_api.data import RISKS_2022, RISKS_2023

LOGGER = logging_conf.LOGGER


class EITSApi(AsyncAPIBase):
    def __init__(
        self,
        url: str = "https://eits.ria.ee",
        version: int = 2023,
        html: bool = False,
        output: str = "modules_and_measures.json",
        limit: int = 100,
        rate: int = 0.1,
        verify_ssl: bool = True,
    ) -> None:
        """
        Initialize the EITSApi object.

        Args:
            url (str): The base URL for the EITS API. \
                Defaults to "https://eits.ria.ee".
            version (int): The version of the EITS API to use. \
                Defaults to 2023.
            html (bool): Whether to format the output as HTML. \
                Defaults to False.
            output (str): The file path to save the output JSON. \
                Defaults to "modules_and_measures.json".
            limit (int): The maximum number of records to fetch in a \
                single API call. Defaults to 100.
            rate (float): The rate limit for API calls in seconds. \
                Defaults to 0.1.
            verify_ssl (bool): Whether to verify SSL certificates for \
                API calls. Defaults to True.

        Attributes:
            eits_version (int): The EITS API version, determined \
                from environment variables or provided argument.
            format_as_html (bool): Flag indicating if the output \
                should be formatted as HTML.
            _url (str): The base URL for the EITS API, determined \
                from environment variables or provided argument.
            output (str): The file path to save the output JSON.
            catalog (ApiCatalog | None): The API catalog object.
            diff_catalog (ApiDiffCatalog | None): The API diff catalog \
                object for comparing versions.
            risks (dict | None): The risk data associated with the \
                specified EITS version.
        """
        super().__init__(url, limit, rate, verify_ssl)
        common.load_environment_variables()

        self.eits_version: int = (
            int(os.getenv("EITS_VERSION"))
            if os.getenv("EITS_VERSION")
            else version
        )
        self.format_as_html: bool = (
            common.get_boolean_from_environment_string(
                "EITS_OUTPUT_FORMAT_HTML", "False"
            )
            if common.get_boolean_from_environment_string(
                "EITS_OUTPUT_FORMAT_HTML"
            )
            else html
        )
        self._url: str = (
            os.getenv("EITS_URL") if os.getenv("EITS_URL") else url
        )
        self.output: str = (
            os.getenv("EITS_OUTPUT_JSON")
            if os.getenv("EITS_OUTPUT_JSON")
            else output
        )
        self.catalog: ApiCatalog | None = self.get_catalog()
        try:
            self.diff_catalog: ApiDiffCatalog | None = self.get_diff_catalog(
                self.eits_version - 1, self.eits_version
            )
        except Exception as e:
            LOGGER.warning(f"{e}")
            self.diff_catalog = None
        match self.eits_version:
            case 2022:
                self.risks = RISKS_2022
            case 2023:
                self.risks = RISKS_2023
            case _:
                self.risks = None

    def diff_catalog_url(self, old_version: str, new_version: str) -> str:
        """
        Generates the EITS2 diff catalog URL string for the EITS2 API.

        Args:
            old_version (str): The EITS2 old version (e.g., "2022", "2023").
            new_version (str): The EITS2 new version (e.g., "2022", "2023").

        Returns:
            str: The generated URL string with the base URL and diff \
                catalog path.
        """
        return (
            f"{self._url}/api/2/catalog/"
            + f"measures-diff/{old_version}/{new_version}"
        )

    def catalog_url(self) -> str:
        """
        Generates the EITS2 catalog URL string for the EITS2 API using \
            the current version.

        Returns:
            str: The generated URL string with the base URL and the \
                current EITS2 version.
        """
        return f"{self._url}/api/2/catalog/{self.eits_version}"

    def item_by_it_url(self, id: str) -> str:
        """
        Generates the URL string for an item using the catalog URL and item ID.

        Args:
            id (str): The item ID.

        Returns:
            str: The generated URL string with the base catalog URL and item \
                ID appended.
        """
        _catalog_url = self.catalog_url()
        return f"{_catalog_url}/{id}"

    def materials_url(self) -> str:
        """
        Generates the EITS2 Risks URL string for the EITS2 API.

        Returns:
            str: The URL string with the base URL and EITS2 version.
        """
        return f"{self._url}/api/2/materials"

    def get_catalog(self) -> ApiCatalog:
        """
        Gets the EITS2 catalog from the EITS2 API.

        Returns:
            ApiCatalog: The ApiCatalog object.
        """
        self.url = self.catalog_url()
        result: dict = self.get_sync()
        self.catalog: ApiCatalog = ApiCatalog(**result)
        return self.catalog

    def get_diff_catalog(
        self, old_version: int, new_version: int
    ) -> ApiDiffCatalog:
        """
        Gets the EITS2 diff catalog from the EITS2 API.

        Args:
            old_version (int): The old version of the EITS2 catalog.
            new_version (int): The new version of the EITS2 catalog.

        Returns:
            ApiDiffCatalog: The ApiDiffCatalog object created from the API DTO.
        """
        self.url = self.diff_catalog_url(old_version, new_version)
        result: dict = self.get_sync()
        self.diff_catalog: ApiDiffCatalog = ApiDiffCatalog(**result)
        return self.diff_catalog

    async def get_item(self, id: str) -> ApiModuleContent:
        """
        Gets EITS2 module content by ID from the EITS2 catalog API.

        Args:
            id (str): The module ID.

        Returns:
            ApiModuleContent: The ApiModuleContent object.
        """
        self.url = self.item_by_it_url(id)
        LOGGER.debug(f"Trying {self.url}/{id}")
        result: dict = await self.get_async()
        item: ApiModuleContent = ApiModuleContent(**result)
        return item

    async def get_raw_module_content(self) -> list[ApiModuleContent]:
        """
        Gets EITS2 module content for each module in each module group in the \
        provided catalog.

        Returns:
            list[ApiModuleContent]: List of ApiModuleContent objects.
        """

        __out: list[ApiModuleContent] = []

        for module_group in self.catalog.moduleGroups:
            tasks = []

            modules_in_group = self.get_modules_recursive(module_group)

            for module in modules_in_group:
                LOGGER.debug(
                    "Creating Aiohttp requests tasks"
                    + f"for '{module.moduleTitle}'"
                )
                tasks.append(
                    asyncio.create_task(self.get_item(module.moduleId))
                )

            LOGGER.info(
                "Requesting EITS MODULES for all modules in "
                + f"module group {module_group.groupTitle}"
            )
            __out.extend(await asyncio.gather(*tasks))

        return __out

    def get_modules_and_measures(
        self, json: bool = True
    ) -> list[JsonModule] | list[dict[str, Any]]:
        """
        Retrieves modules and measures, optionally returning them as JSON.

        Args:
            json (bool): If True, returns a list of JSON-compatible module \
                        representations. If False, returns module objects.

        Returns:
            list[JsonModule] | list[dict[str, Any]]: A list of modules as \
            either JsonModule objects or dictionaries, depending on the \
            'json' parameter.
        """
        async def run_async() -> list[JsonModule] | list[dict[str, Any]]:

            __out: list[JsonModule] | list[dict[str, Any]] = []
            raw_content: list[ApiModuleContent] = (
                await self.get_raw_module_content()
            )
            for module in raw_content:
                try:
                    json_module: JsonModule = common.create_module_object(
                        module, self.risks, self.format_as_html
                    )
                    __out.append(
                        json_module.model_dump() if json else json_module
                    )
                except Exception:
                    LOGGER.warning("MIDAGI JUHTUS")

            return __out

        return asyncio.run(run_async())

    def get_modules(self, group: ApiModuleGroup) -> list[ApiModule]:
        """
        Retrieves a list of modules from the ApiModuleGroup API DTO.

        Args:
            group (ApiModuleGroup): The object containing a list of modules.

        Returns:
            list[ApiModule]: A list of ApiModule objects from the API DTO.
        """
        LOGGER.debug(f"Getting modules for module group '{group.groupTitle}'")
        return group.modules

    def get_modules_recursive(self, group: ApiModuleGroup) -> list[ApiModule]:
        """
        Recursively retrieves all modules, including submodules, from the \
        ApiModuleGroup.

        Args:
            group (ApiModuleGroup): The ApiModuleGroup object from the API DTO.

        Returns:
            list[ApiModule]: A list of all modules under the specified module \
            group.
        """
        LOGGER.debug(f"Recursive getting modules for '{group.groupTitle}'")
        modules: list[ApiModule] = []

        if len(group.moduleSubgroups) > 0:
            for subgroup in group.moduleSubgroups:
                modules += self.get_modules_recursive(subgroup)
        modules += self.get_modules(group)

        return modules

    def get_diff_added(
        self, json: bool = True
    ) -> list[ApiMeasureDetail] | list[dict[str, Any]]:
        """
        Retrieves measures that were added in the diff catalog.

        Args:
            json (bool): If True, returns a list of JSON-compatible measure \
                        representations. If False, returns measure objects.

        Returns:
            list[ApiMeasureDetail] | list[dict[str, Any]]: A list of measures \
            that were added, either as ApiMeasureDetail objects or as \
            dictionaries, depending on the 'json' parameter.
        """
        __out_list: list[ApiMeasureDetail] | list[dict[str, Any]] = []
        for module_group in self.diff_catalog.added:

            modules_in_group = self.get_modules_recursive(module_group)

            for module in modules_in_group:
                for measure_detail in module.measureDetails:
                    for measure in measure_detail.measures:
                        __out_list.append(
                            measure.model_dump() if json else measure
                        )
        return __out_list

    def get_diff_removed(
        self, json: bool = True
    ) -> list[ApiMeasureDetail] | list[dict[str, Any]]:
        """
        Retrieves measures that were removed in the diff catalog.

        Args:
            json (bool): If True, returns a list of JSON-compatible measure \
                        representations. If False, returns measure objects.

        Returns:
            list[ApiMeasureDetail] | list[dict[str, Any]]: A list of measures \
            that were removed, either as ApiMeasureDetail objects or as \
            dictionaries, depending on the 'json' parameter.
        """
        __out_list: list[ApiMeasureDetail] | list[dict[str, Any]] = []
        for module_group in self.diff_catalog.removed:

            modules_in_group = self.get_modules_recursive(module_group)

            for module in modules_in_group:
                for measure_detail in module.measureDetails:
                    for measure in measure_detail.measures:
                        __out_list.append(
                            measure.model_dump() if json else measure
                        )
        return __out_list

    def get_diff_replaced(
        self, json: bool = True
    ) -> list[ApiMeasureDetail] | list[dict[str, Any]]:
        """
        Retrieves measures that were replaced in the diff catalog.

        Args:
            json (bool): If True, returns a list of JSON-compatible measure \
                        representations. If False, returns measure objects.

        Returns:
            list[ApiMeasureDetail] | list[dict[str, Any]]: A list of measures \
            that were replaced, either as ApiMeasureDetail objects or as \
            dictionaries, depending on the 'json' parameter.
        """
        __out_list: list[ApiMeasureDetail] | list[dict[str, Any]] = []
        for replaced in self.diff_catalog.replaced:

            modules_in_group = self.get_modules_recursive(replaced.newValue)

            for module in modules_in_group:
                for measure_detail in module.measureDetails:
                    for measure in measure_detail.measures:
                        __out_list.append(
                            measure.model_dump() if json else measure
                        )
        return __out_list

    def get_diff_all(
        self, json: bool = True
    ) -> list[ApiMeasureDetail] | list[dict[str, Any]]:
        """
        Retrieves all measures that were added, replaced, or removed in the \
        diff catalog.

        Args:
            json (bool): If True, returns a list of JSON-compatible measure \
                        representations. If False, returns measure objects.

        Returns:
            list[ApiMeasureDetail] | list[dict[str, Any]]: A list of measures \
            that were added, replaced, or removed, either as ApiMeasureDetail \
            objects or as dictionaries, depending on the 'json' parameter.
        """
        __out_list: list[ApiMeasureDetail] | list[dict[str, Any]] = []
        __out_list.extend(self.get_diff_added(json))
        __out_list.extend(self.get_diff_replaced(json))
        __out_list.extend(self.get_diff_removed(json))

        return __out_list

    def get_measure_risks_all(self) -> list[str]:
        """
        Retrieves all measure risks.

        Returns:
            list: A list of risks associated with measures.
        """
        return self.risks

    def parse_risks_html_items(self, html_string: str) -> list[dict[str, str]]:
        """
        Parses an HTML string and returns a list of items with titles and \
        descriptions.

        Args:
            html_string (str): The HTML string to parse.

        Returns:
            list[dict[str, str]]: A list of dictionaries, where each \
                dictionary contains keys "title" and "description".
        """
        soup = BeautifulSoup(html_string, "lxml")
        items: list[JsonRisk] = []

        titles = soup.find_all("h2")

        for title in titles:
            title_text: str = title.text.strip()
            item_code = title_text.split("\t")[0].strip()
            item_title = title_text.split("\t")[1].strip()

            description_element = title.find_next_sibling()
            description_text = ""
            while description_element and description_element.name != "h2":
                description_text += str(description_element).replace("\n", "")
                description_element = description_element.find_next_sibling()

            items.append(
                JsonRisk(
                    code=item_code,
                    title=item_title,
                    combined_title=f"{item_code}: {item_title}",
                    description=description_text,
                ).model_dump()
            )

        return items

    def get_risks(self) -> list[dict[str, str]]:
        """
        Retrieves risks from the materials URL.

        Returns:
            list[dict[str, str]]: A list of dictionaries containing risk \
                items with titles and descriptions.
        """
        self.url = self.materials_url()
        child_objects: list[dict[str, Any]] = self.get_sync()[0].get(
            "child_objects"
        )
        for item in child_objects:
            if item.get("title") == "Alusohtude kataloog":
                return self.parse_risks_html_items(item.get("content"))
