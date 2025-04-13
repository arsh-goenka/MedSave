# backend/ndc_service.py
import requests
from typing import Union

FDA_NDC_URL = "https://api.fda.gov/drug/ndc.json"

def get_drug_info_by_ndc(ndc_code: str) -> Union[dict, None]:
    """
    Hit the open‑FDA NDC endpoint and return the *product‑level* record.
    If given a package NDC (e.g., "12345-6789-01"), strips the package segment.
    If given a product NDC (e.g., "12345-6789"), uses it as is.
    """
    if not ndc_code:
        raise ValueError("ndc_code cannot be empty")

    # If it has multiple hyphens, it's a package NDC, so chop off the last segment
    # If it has one hyphen, it's already a product NDC, so use it as is
    product_ndc = "-".join(ndc_code.split("-")[:-1]) if ndc_code.count("-") > 1 else ndc_code

    params = {"search": f"product_ndc:{product_ndc}", "limit": 1}

    try:
        resp = requests.get(FDA_NDC_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data["results"][0] if data.get("results") else None
    except requests.exceptions.RequestException as exc:
        # You can do fancier logging here if you like
        print("NDC lookup failed:", exc)
        return None
