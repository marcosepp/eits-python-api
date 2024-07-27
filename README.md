# eits-python-api

Scrapes E-ITS API and generates JSON with all modules and measures. This can be used to update E-ITS measures in Jira.

Example output json is in file `modules_and_measures.json`.

There are `RISKS_2022` and `RISKS_2023` variables in `eits_python_api.data` which are pre-created based on "Alusohutude viitetabel" XLSX from E-ITS portal. This is used to add risk codes to measures.

Script is generating debugging log to `debug.log`.

## Usage

### Requirements

* Python == 3.10
* Pip >= 23.0.0

### Install from PyPi (recommended)

```bash
$ pip install eits-python-api
$
```

### Install manually: Python requirements (optional)

This project is managed by Poetry, so you can install all dependencies with:

```bash
$ poetry install
$ poetry shell
$ python run.py
/.../
```

### Setup environment (optional)

Either fill `.env` file in script working directory with needed information or set environment variables as you need. Default values are shown below:

```ini
EITS_URL=https://eits.ria.ee
EITS_VERSION=2023
EITS_OUTPUT_JSON=modules_and_measures.json
EITS_OUTPUT_FORMAT_HTML=False
```

| env | required/optional | default | description |
| - | - | - | - |
| EITS_URL | Optional | `https://eits.ria.ee` | Describes EITS portal base url with protocol |
| EITS_VERSION | Optional | `2023` | Describes EITS version |
| EITS_OUTPUT_JSON | Optional | `modules_and_measures.json` | Describes path to result JSON file |
| EITS_OUTPUT_FORMAT_HTML | Optional | `False` | Describes whether modules and measures text should be formated using HTML |

### Run Python script

```bash
$ python3 run.py
2024-01-12 15:55:47,167 [INFO] Requesting EITS MODULES for all ISMS. Turbehaldus
2024-01-12 15:55:48,623 [INFO] Requesting EITS MODULES for all ORP. Organisatsioon ja personal
2024-01-12 15:55:50,706 [INFO] Requesting EITS MODULES for all CON.  Kontseptsioonid ja metoodikad
2024-01-12 15:55:53,861 [INFO] Requesting EITS MODULES for all OPS. Käidutööd
2024-01-12 15:56:00,486 [INFO] Requesting EITS MODULES for all DER. Avastamine ja reageerimine
2024-01-12 15:56:03,550 [INFO] Requesting EITS MODULES for all INF. Taristu
2024-01-12 15:56:08,428 [INFO] Requesting EITS MODULES for all NET. Võrgud ja side
2024-01-12 15:56:12,461 [INFO] Requesting EITS MODULES for all SYS. IT-süsteemid
2024-01-12 15:56:23,093 [INFO] Requesting EITS MODULES for all APP. Rakendused
2024-01-12 15:56:31,110 [INFO] Requesting EITS MODULES for all IND. Tööstuse IT
2024-01-12 15:56:35,002 [INFO] Saving JSON output to modules_and_measures.json
2024-01-12 15:56:35,072 [INFO] Total time: 49.12 seconds.
```

## Methods

This package can be used to generate modules and measures for given year. It can also be used to get all basic risks from API. It can also be used to get diff between two years. Use EITSApi() to create an instance of the class and then call methods on it.

### EITSApi.get_modules_and_measures()

Generates list of all modules and measures for given year. Objects are managed by Pydantic objects which can be easily converted to JSON or dict. To use Pydantic objects, simply use `get_modules_and_measures(False)` which will return a list of EitsModule objects. If you want to get the raw JSON data, just call `get_modules_and_measures()` without any arguments.

### EITSApi.get_risks()

Gets all basic risks from API and returns them as a list of Risk objects. If you want to get the raw JSON data, just call `get_risks()` without any arguments.

### EITSApi.get_diff_all()

Gets diff between two years and returns it as a list of Diff objects. If you want to get the raw JSON data, just call `get_diff_all()` without any arguments.

## License

MIT

## Author

Marco Sepp
