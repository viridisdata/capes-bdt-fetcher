import json
import logging
import math
import time
from pathlib import Path

import httpx

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
            r = httpx.post(URL_API, data=json.dumps(data), headers=headers)
            json_data = r.json()
            break
        except json.decoder.JSONDecodeError:
            logger.error("JSON error while fetching data from CAPES' API.")
            time.sleep(5)
        # except httpx.exceptions.ConnectTimeout:
        #     logger.error(
        #         "Connection Timeout error while fetching data from CAPES' API."
        #     )
        #     time.sleep(5)
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


def fetch(year, start_page, end_page, destdir, sleep):
    for data in buscar_todos_ano(year, start_page, end_page):
        page = data["pagina"]
        filename = f"capes-btd_{year}-{page:04}.json"
        filepath = destdir / str(year) / filename
        if not filepath.parent.exists():
            filepath.parent.mkdir(parents=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)
        time.sleep(sleep)


def fetch_years(year_start, year_end, destdir, sleep):
    for year in range(year_start, year_end + 1):
        fetch(year, 1, None, destdir=destdir, sleep=sleep)


def parse_year_range(year_range):
    if ":" in year_range:
        year_start, year_end = year_range.split(":")
        return {"year_start": int(year_start), "year_end": int(year_end)}
    return {"year_start": int(year_range), "year_end": int(year_range)}


def _cli():

    def get_args():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("year")
        parser.add_argument("-start-page", default=1, type=int)
        parser.add_argument("-end-page", default=None, type=int)
        parser.add_argument(
            "-dest",
            "-o",
            "--output-dir",
            default=Path("."),
            type=Path,
        )
        parser.add_argument("-sleep", default=1.0, type=float)

        return parser.parse_args()

    args = get_args()
    year = parse_year_range(args.year)
    start_page = args.start_page
    end_page = args.end_page
    destdir = args.output_dir
    sleep = args.sleep

    logger = logging.getLogger("capes_btd_fetcher")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    try:
        fetch_years(**year, destdir=destdir, sleep=sleep)
    except Exception:
        logger.exception("Unexpected Error")
        raise


if __name__ == "__main__":
    _cli()
