import json
import logging
import math
import time

import requests

RECORDS_PER_PAGE = 50
URL_API = "https://catalogodeteses.capes.gov.br/catalogo-teses/rest/busca"

logger = logging.getLogger(__name__)


def buscar_catalogo_teses(
    year: int,
    page: int,
    termo: str = "",
) -> dict:
    data = {
        "termo": termo,
        "filtros": [{"campo": "Ano", "valor": str(year)}],
        "pagina": page,
        "registrosPorPagina": RECORDS_PER_PAGE,
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
    }
    while True:
        try:
            logger.info(f"Requesting CAPES' data from year {year}, page {page}")
            r = requests.post(URL_API, data=json.dumps(data), headers=headers)
            json_data = r.json()
            break
        except json.decoder.JSONDecodeError:
            logger.error("JSON error while fetching data from CAPES' API.")
            time.sleep(5)
        except requests.exceptions.ConnectTimeout:
            logger.error(
                "Connection Timeout error while fetching data from CAPES' API."
            )
            time.sleep(5)
    return json_data


def buscar_todos_ano(
    year: int,
    start_page: int = 1,
    end_page: int = None,
) -> dict:
    page = start_page
    data = buscar_catalogo_teses(year=year, page=page)
    yield data
    page += 1
    max_page = math.ceil(data["total"] / RECORDS_PER_PAGE)
    while page <= max_page and (end_page is None or page <= end_page):
        yield buscar_catalogo_teses(year=year, page=page)
        page += 1
