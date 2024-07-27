from __future__ import annotations
from enum import Enum
from pydantic import BaseModel

# Uncomment for model values
# from pydantic import BaseModel, Field


class ApiElementInfo(BaseModel):
    title: str | None | None = None
    content: str | None | None = None


class ApiMeasureDetail(BaseModel):
    # Change model values:
    # measureId: str | None | None = Field(default=None, alias="measureId")
    measureId: str | None | None = None
    measureTitle: str | None | None = None
    body: str | None | None = None
    assignees: list[str | None] | None = None
    securityCodes: list[str | None] | None = None
    measureCode: str | None | None = None


class ApiMeasureGroup(BaseModel):
    groupId: str | None | None = None
    groupTitle: str | None | None = None
    measures: list[ApiMeasureDetail] | None = None
    groupCode: str | None | None = None


class ApiModule(BaseModel):
    moduleId: str | None | None = None
    groupId: str | None | None = None
    moduleTitle: str | None = None
    link: str | None = None
    measureDetails: list[ApiMeasureGroup] | None = None
    moduleCode: str | None = None
    description: list[ApiElementInfo] | None = None


class ApiModuleContent(BaseModel):
    version: str | None = None
    lang: str | None = None
    validFrom: str | None = None
    validTo: str | None = None
    moduleId: str | None = None
    moduleTitle: str | None = None
    description: list[ApiElementInfo] | None = None
    risks: list[ApiElementInfo] | None = None
    additionalInfo: str | None = None
    measureDetails: list[ApiMeasureGroup] | None = None
    moduleCode: str | None = None


class ApiModuleGroup(BaseModel):
    groupId: str | None = None
    groupTitle: str | None = None
    parentGroupId: str | None = None
    moduleSubgroups: list[ApiModuleGroup] | None = None
    modules: list[ApiModule] | None = None
    groupCode: str | None = None


class ApiCatalog(BaseModel):
    version: str | None = None
    lang: str | None = None
    validFrom: str | None = None
    validTo: str | None = None
    id: str | None = None
    moduleGroups: list[ApiModuleGroup] | None = None


class ApiDiffReplaced(BaseModel):
    oldValue: ApiModuleGroup | None = None
    newValue: ApiModuleGroup | None = None


class ApiDiffCatalog(BaseModel):
    oldVersion: str | None = None
    newVersion: str | None = None
    lang: str | None = None
    added: list[ApiModuleGroup] | None = None
    removed: list[ApiModuleGroup] | None = None
    replaced: list[ApiDiffReplaced] | None = None


class JsonMeasure(BaseModel):
    code: str | None = None
    title: str | None = None
    group: str | None = None
    description: str | None = None
    security_code: str | None = None
    assignees: list[str] | None = None
    module_code: str | None = None
    lifecycle: str | None = None
    risks: list[str] | None = None


class JsonModule(BaseModel):
    code: str | None = None
    title: str | None = None
    purpose: str | None = None
    responsibility: str | None = None
    limits: str | None = None
    measures: list[JsonMeasure] | None = None
    risks: list[ApiElementInfo] | None = None
    additional_info: str | None = None
    group: str | None = None


class JsonRisk(BaseModel):
    code: str
    title: str
    combined_title: str
    description: str


class CsvMeasure(BaseModel):
    catalog_version: str | None = None
    module_valid_from: str | None = None
    module_valid_to: str | None = None
    module_purpose: str | None = None
    module_responsibility: str | None = None
    module_limits: str | None = None
    module_additional_info: str | None = None
    module_code: str | None = None
    module_title: str | None = None
    measure_code: str | None = None
    measure_title: str | None = None
    measure_group: str | None = None
    measure_body: str | None = None
    measure_assignees: str | None = None
    measure_security_codes: str | None = None


class ValueErrorMeasureCodeMismatch(Exception):
    pass


class ValueErrorMeasureTitleMismatch(Exception):
    pass


class ValueErrorModuleCodeMismatch(Exception):
    pass


class ValueErrorModuleTitleMismatch(Exception):
    pass


class EITSType(Enum):

    ONLY_SECURITY_CODE = r"(?P<security_code>\((?:[CIA]+)(?:[-IA]*?)\))"
    ONLY_MEASURE_CODE = (
        r"(?P<measure_code>(?:[A-Z]{3,})"
        + r"(?:\.[0-9E]{1,2}){1,}\.[ME]{1,2}(?:[0-9]){1,2})"
    )
    ONLY_RESPONSIBILITY = r"(?P<responsibility>(?:\[.+\]))"
    ONLY_MODULE_CODE = r"(?P<module_code>(?:[A-Z]{3,})(?:\.[0-9E]{1,2}){1,2})"

    MEASURE_CODE = f"{r'^'}{ONLY_MEASURE_CODE}{r'$'}"
    MEASURE_TITLE = (
        r"^((?:[A-Z]{3,})(?:\.[0-9E]{1,2}){1,}\."
        + r"[ME]{1,2}([0-9]){1,})(: )(?:[\p{L}\s\-,\(\)\d\/]+)$"
    )
    MODULE_CODE = r"^((?:[A-Z]{3,})(?:\.[0-9E]{1,2}){1,})$"
    MODULE_TITLE = (
        r"^((?:[A-Z]{3,})(?:\.[0-9E]{1,2}){1,})(: )(?:[\p{L}\s\-,\(\)\d\/]+)$"
    )
    MEASURE_TITLE_RAW = (
        r"^(?P<measure_code>(?:[A-Z]{3,})(?:\.[0-9E]{1,2}){1,}\.[ME]{1,2}(?:[0-9]){1,2})(?:\s+(?P<title>.+?))(?:\s+(?P<security_code>\((?:[CIA]+)(?:[-IA]*?)\)))?(?:\s+(?P<responsibility>\[.+\]))?$"
    )
    MEASURE_CODE_RAW = (
        r"^((?:[A-Z]{3,})(?:\.[0-9E]{1,2}){1,}\.[ME]{1,2}(?:[0-9]){1,})$"
    )
    # MEASURE_TITLE_RAW = (
    #     r"^(?P<measure_code>(?:[A-Z]{3,})(?:\.[0-9E]{1,2}){1,}\.[ME]{1,2}(?:[0-9]){1,2})(?:\s+(?P<title>.+?))(?:\s+(?P<security_code>\((?:[CIA]+)(?:[-IA]*?)\)))?(?:\s+(?P<responsibility>\[.+\]))?(?:\s+(?P<security_code_after>\((?:[CIA]+)(?:[-IA]*?)\)))?$"
    # )
    MODULE_TITLE_RAW = (
        r"^(?P<code_and_title>(?P<code>(?:[A-Z]{3,})"
        + r"(?:\.[0-9E]{1,2}){1,}): (?P<title>.+?))$"
    )
    MODULE_CODE_RAW = r"^((?:[A-Z]{3,})(?:\.[0-9E]{1,2}){1,})$"
