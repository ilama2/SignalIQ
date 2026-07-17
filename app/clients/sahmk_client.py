"""
SignalIQ - SAHMK Client

Handles communication with the SAHMK API.
"""

from typing import Any
import time
import requests
from loguru import logger

from app.core import settings


class SahmkClient:
    """Client for SAHMK API."""

    def __init__(self):

        self.base_url = "https://app.sahmk.sa/api/v1"

        self.headers = {
            "X-API-Key": settings.SAHMK_API_KEY,
            "Accept": "application/json",
        }

        self.timeout = settings.REQUEST_TIMEOUT


    def _get(
        self,
        endpoint: str,
        params: dict | None = None
    ) -> dict[str, Any]:

        url = f"{self.base_url}{endpoint}"

        max_retries = 10

        for attempt in range(max_retries):

            try:

                response = requests.get(
                    url=url,
                    headers=self.headers,
                    params=params,
                    timeout=self.timeout,
                )


                if response.status_code == 429:

                    wait_time = min(
                        60,
                        10 * (attempt + 1)
                    )

                    logger.warning(
                        f"SAHMK rate limit {endpoint}. "
                        f"Waiting {wait_time}s"
                    )

                    time.sleep(wait_time)
                    continue


                response.raise_for_status()

                return response.json()


            except requests.exceptions.ConnectionError as e:

                wait_time = 15

                logger.warning(
                    f"Connection reset for {endpoint}. "
                    f"Retrying in {wait_time}s "
                    f"({attempt + 1}/{max_retries})"
                )

                time.sleep(wait_time)


            except requests.exceptions.Timeout:

                wait_time = 10

                logger.warning(
                    f"Timeout for {endpoint}. "
                    f"Retrying in {wait_time}s"
                )

                time.sleep(wait_time)


        raise Exception(
            f"SAHMK failed after {max_retries} retries: {endpoint}"
        )


    def get_quote(self, symbol: str) -> dict:
        return self._get(f"/quote/{symbol}/")