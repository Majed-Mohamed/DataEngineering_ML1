"""
Functions to fetch data from NYC Open Data API and provide loaders
for crashes / persons / vehicles datasets.
"""

from pathlib import Path
from typing import Optional

import pandas as pd
import requests

from config import (
    CRASHES_URL,
    PERSONS_URL,
    VEHICLES_URL,
    API_LIMIT,
    APP_TOKEN,
    CACHE_DIR,
)

# Make sure CACHE_DIR exists
CACHE_DIR = Path(CACHE_DIR)
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def fetch_nyc_data(
    url: str,
    limit: int = API_LIMIT,
    offset: int = 0,
    app_token: Optional[str] = APP_TOKEN,
    use_cache: bool = True,
) -> pd.DataFrame:
    """
    Fetch ONE page of data from NYC Open Data Socrata API.

    Parameters
    ----------
    url : str
        API endpoint URL.
    limit : int
        Number of records to fetch per request.
    offset : int
        Starting record offset.
    app_token : str, optional
        NYC Open Data app token for higher rate limits.
    use_cache : bool
        If True, cache the result locally.

    Returns
    -------
    pd.DataFrame
    """
    # Build a simple cache file name based on URL + offset + limit
    cache_file = CACHE_DIR / (
        f"{Path(url).name}_limit{limit}_offset{offset}.parquet"
    )

    if use_cache and cache_file.exists():
        return pd.read_parquet(cache_file)

    headers = {}
    if app_token:
        headers["X-App-Token"] = app_token

    params = {
        "$limit": limit,
        "$offset": offset,
    }

    resp = requests.get(url, headers=headers, params=params, timeout=60)
    resp.raise_for_status()

    data = resp.json()
    df = pd.DataFrame(data)

    if use_cache:
        df.to_parquet(cache_file, index=False)

    return df


def fetch_all_data(
    url: str,
    max_records: Optional[int] = None,
    use_cache: bool = True,
) -> pd.DataFrame:
    """
    Fetch all available data from the API using pagination.

    Parameters
    ----------
    url : str
        API endpoint URL.
    max_records : int, optional
        Maximum total records to fetch. If None, fetch until API returns no data.
    use_cache : bool
        Whether to use caching in fetch_nyc_data.

    Returns
    -------
    pd.DataFrame
    """
    all_chunks = []
    offset = 0
    remaining = max_records

    while True:
        # Decide how many rows to request in this page
        limit = API_LIMIT if remaining is None else min(API_LIMIT, remaining)

        df_chunk = fetch_nyc_data(
            url=url,
            limit=limit,
            offset=offset,
            use_cache=use_cache,
        )

        if df_chunk.empty:
            break

        all_chunks.append(df_chunk)

        offset += len(df_chunk)
        if remaining is not None:
            remaining -= len(df_chunk)
            if remaining <= 0:
                break

    if not all_chunks:
        return pd.DataFrame()

    return pd.concat(all_chunks, ignore_index=True)


def load_crashes(
    use_cache: bool = True,
    sample_size: Optional[int] = None,
    max_records: Optional[int] = None,
) -> pd.DataFrame:
    """
    Load crashes dataset from NYC Open Data API.

    Parameters
    ----------
    use_cache : bool
        Use cached pages if available.
    sample_size : int, optional
        If provided, return a random sample of this size.
    max_records : int, optional
        Maximum number of records to fetch in total.

    Returns
    -------
    pd.DataFrame
    """
    df = fetch_all_data(CRASHES_URL, max_records=max_records, use_cache=use_cache)
    if sample_size is not None and not df.empty:
        df = df.sample(sample_size, random_state=42)
    return df


def load_persons(
    use_cache: bool = True,
    sample_size: Optional[int] = None,
    max_records: Optional[int] = None,
) -> pd.DataFrame:
    """Load persons dataset from NYC Open Data API."""
    df = fetch_all_data(PERSONS_URL, max_records=max_records, use_cache=use_cache)
    if sample_size is not None and not df.empty:
        df = df.sample(sample_size, random_state=42)
    return df


def load_vehicles(
    use_cache: bool = True,
    sample_size: Optional[int] = None,
    max_records: Optional[int] = None,
) -> pd.DataFrame:
    """Load vehicles dataset from NYC Open Data API."""
    df = fetch_all_data(VEHICLES_URL, max_records=max_records, use_cache=use_cache)
    if sample_size is not None and not df.empty:
        df = df.sample(sample_size, random_state=42)
    return df
