<!-- Banner -->
![alt Banner of the Solcast package](https://raw.githubusercontent.com/klaasnicolaas/python-solcast-pv/main/assets/header_solcast_pv-min.png)

<!-- PROJECT SHIELDS -->
[![GitHub Release][releases-shield]][releases]
[![Python Versions][python-versions-shield]][pypi]
![Project Stage][project-stage-shield]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

[![GitHub Activity][commits-shield]][commits-url]
[![PyPi Downloads][downloads-shield]][downloads-url]
[![GitHub Last Commit][last-commit-shield]][commits-url]
[![Open in Dev Containers][devcontainer-shield]][devcontainer]

[![Build Status][build-shield]][build-url]
[![Typing Status][typing-shield]][typing-url]
[![Maintainability][maintainability-shield]][maintainability-url]
[![Code Coverage][codecov-shield]][codecov-url]


Asynchronous Python client for [Solcast][solcast].

## About

[Solcast][solcast] provides solar radiation and solar power forecasts, estimated and
historical data. This package allows you to get the data from the [API][solcast-api]
and use it in your own application.

> [!NOTE]
> This package is still in development and rooftop forecast is not yet implemented.

## Installation

```bash
pip install solcast-pv
```

## Datasets

- List of all your created rooftop sites linked to your account.
- Get rate limits for your account.

<details>
  <summary>CLICK HERE! to see all datasets</summary>

### Rooftop Site

**Note**: _requesting the list of all your created rooftop sites linked to your account, will not affect your daily rate limit._

| Name | Type | Description |
| :--- | :--- | :---------- |
| `name` | `str` | The name of the rooftop site. |
| `resource_id` | `str` | The unique identifier of the rooftop site. |
| `install_date` | `datetime` | The installation date of your solar panels. |
| `capacity` | `float` | The capacity of the solar panels. |
| `capacity_dc` | `float` | The capacity of the solar panels in DC. |
| `azimuth` | `int` | The azimuth of the solar panels. |
| `tilt` | `int` | The tilt of the solar panels. |
| `loss_factor` | `float` | The loss factor of the solar panels. |

### Rate Limits

**Note**: _requesting the rate limits for your account will not affect your daily rate limit._

| Name | Type | Description |
| :--- | :--- | :---------- |
| `daily_limit` | `int` | The daily limit of API calls. |
| `remaining_daily` | `int` | The remaining daily limit of API calls. |
| `consumed_daily` | `int` | How many API calls you have consumed today. |
</details>

### Example

```python
import asyncio

from solcast_pv import Solcast, RooftopSite


async def main() -> None:
    """Show example on using this package."""
    async with Solcast(token="API_KEY") as client:
        rooftops: list[RooftopSite] = await client.get_rooftop_sites()
        print(rooftops)

if __name__ == "__main__":
    asyncio.run(main())
```

More examples can be found in the [examples folder](./examples/).

## Contributing

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We've set up a separate document for our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Setting up development environment

The simplest way to begin is by utilizing the [Dev Container][devcontainer]
feature of Visual Studio Code or by opening a CodeSpace directly on GitHub.
By clicking the button below you immediately start a Dev Container in Visual Studio Code.

[![Open in Dev Containers][devcontainer-shield]][devcontainer]

This Python project relies on [Poetry][poetry] as its dependency manager,
providing comprehensive management and control over project dependencies.

You need at least:

- Python 3.11+
- [Poetry][poetry-install]

Install all packages, including all development requirements:

```bash
poetry install
```

Poetry creates by default an virtual environment where it installs all
necessary pip packages, to enter or exit the venv run the following commands:

```bash
poetry shell
exit
```

Setup the pre-commit check, you must run this inside the virtual environment:

```bash
pre-commit install
```

*Now you're all set to get started!*

As this repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. You can run all checks and tests
manually, using the following command:

```bash
poetry run pre-commit run --all-files
```

To run just the Python tests:

```bash
poetry run pytest
```

To update the [syrupy](https://github.com/tophat/syrupy) snapshot tests:

```bash
poetry run pytest --snapshot-update
```

## License

MIT License

Copyright (c) 2024 Klaas Schoute

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


<!-- LINKS FROM PLATFORM -->
[solcast]: https://solcast.com/
[solcast-api]: https://docs.solcast.com.au/


<!-- MARKDOWN LINKS & IMAGES -->
[build-shield]: https://github.com/klaasnicolaas/python-solcast-pv/actions/workflows/tests.yaml/badge.svg
[build-url]: https://github.com/klaasnicolaas/python-solcast-pv/actions/workflows/tests.yaml
[codecov-shield]: https://codecov.io/gh/klaasnicolaas/python-solcast-pv/branch/main/graph/badge.svg?token=X4799ZA1V2
[codecov-url]: https://codecov.io/gh/klaasnicolaas/python-solcast-pv
[commits-shield]: https://img.shields.io/github/commit-activity/y/klaasnicolaas/python-solcast-pv.svg
[commits-url]: https://github.com/klaasnicolaas/python-solcast-pv/commits/main
[devcontainer-shield]: https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode
[devcontainer]: https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/klaasnicolaas/python-solcast-pv
[downloads-shield]: https://img.shields.io/pypi/dm/solcast-pv
[downloads-url]: https://pypistats.org/packages/solcast-pv
[last-commit-shield]: https://img.shields.io/github/last-commit/klaasnicolaas/python-solcast-pv.svg
[license-shield]: https://img.shields.io/github/license/klaasnicolaas/python-solcast-pv.svg
[maintainability-shield]: https://api.codeclimate.com/v1/badges/37e0267f0b2ab438f848/maintainability
[maintainability-url]: https://codeclimate.com/github/klaasnicolaas/python-solcast-pv/maintainability
[maintenance-shield]: https://img.shields.io/maintenance/yes/2024.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
[pypi]: https://pypi.org/project/solcast-pv/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/solcast-pv
[releases-shield]: https://img.shields.io/github/release/klaasnicolaas/python-solcast-pv.svg
[releases]: https://github.com/klaasnicolaas/python-solcast-pv/releases
[typing-shield]: https://github.com/klaasnicolaas/python-solcast-pv/actions/workflows/typing.yaml/badge.svg
[typing-url]: https://github.com/klaasnicolaas/python-solcast-pv/actions/workflows/typing.yaml

[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com
