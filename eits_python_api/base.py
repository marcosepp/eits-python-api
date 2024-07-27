import asyncio
import ssl
import aiohttp
import requests

from eits_python_api import logging_conf

LOGGER = logging_conf.LOGGER


class AsyncAPIBase:
    """
    A base class for making synchronous and asynchronous HTTP GET requests.

    Attributes:
        url (str): URL for the HTTP GET request.
        limit (asyncio.Semaphore): Semaphore to limit concurrent requests.
        rate (int): Rate limit for requests in seconds.
        timeout (aiohttp.ClientTimeout): Timeout for HTTP requests.
        headers (dict): Headers for HTTP requests.
        ssl_context (ssl.SSLContext): SSL context for secure requests.
    """
    def __init__(
        self, url: str, limit: int = 100, rate: int = 0.1, verify: bool = True
    ) -> None:
        """
        Initializes AsyncAPIBase class.

        Args:
            url (str): URL for HTTP GET request.
            limit (int, optional): Limits concurrent requests. \
                Defaults to 100.
            rate (int, optional): Limits how often requests are made. \
                Defaults to 0.1.
            verify (bool, optional): Whether to verify SSL certificates. \
                Defaults to True.
        """
        LOGGER.debug("Creating AsyncAPIBase class")
        self.url = url
        self.limit: asyncio.Semaphore = asyncio.Semaphore(limit)
        self.rate: int = rate
        self.timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=60)
        self.headers: dict = {"accept": "application/json"}
        self.ssl_context: ssl.SSLContext = ssl.create_default_context()
        if verify:
            self.ssl_context.check_hostname = True
            self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        else:
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE

    async def get_async(self) -> dict | None:
        """
        Makes an asynchronous HTTP GET request.

        Returns:
            dict: JSON from HTTP GET response, or None on error.
        """

        async with self.limit:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                self.session = session
                try:
                    async with self.session.get(
                        url=self.url,
                        headers=self.headers,
                        ssl=self.ssl_context,
                    ) as response:

                        details: dict = await response.json()

                        if response.status == 200:
                            LOGGER.debug(f"Successful for {response.url}")
                            return details
                        else:
                            LOGGER.error(
                                f"Failed for {response.url}: {response.status}"
                            )
                            return None
                except aiohttp.ClientConnectionError as e:
                    # deal with this type of exception
                    LOGGER.warning(f"ClientConnectionError [{self.url}]: {e}")
                    # await self.session.close()
                except aiohttp.ClientResponseError as e:
                    # handle individually
                    LOGGER.debug(f"ClientResponseError [{self.url}]: {e}")
                    # await self.session.close()
                except asyncio.exceptions.TimeoutError:
                    # these kind of errors happened to me as well
                    LOGGER.debug(f"TimeoutError [{self.host}]")
                    # await self.session.close()
                except Exception as e:
                    LOGGER.debug(
                        f"Error getting details for [{self.url}]: {e}"
                    )
                    return None
                await asyncio.sleep(self.rate)

    def get_sync(self) -> dict | None:
        """
        Makes a synchronous HTTP GET request.

        Returns:
            dict: JSON from HTTP GET response, or None on error.
        """
        with requests.Session() as session:
            try:
                response = session.get(
                    url=self.url,
                    headers=self.headers,
                    verify=self.ssl_context.check_hostname,
                )

                response.raise_for_status()

                details: dict = response.json()
                LOGGER.debug(f"Successful for {response.url}")
                return details
            except (
                requests.exceptions.RequestException,
                requests.exceptions.Timeout,
            ) as e:
                LOGGER.error(f"Error: {e}")
                return None
            except Exception as e:
                LOGGER.error(f"Generic error for [{self.url}]: {e}")
                return None
