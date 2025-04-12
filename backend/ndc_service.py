# backend/ndc_service.py
import requests

FDA_NDC_URL = "https://api.fda.gov/drug/ndc.json"

def get_drug_info_by_ndc(ndc_code: str) -> dict | None:
    """
    Hit the open‑FDA NDC endpoint and return the *product‑level* record.
    We strip the package segment (the last hyphen‑delimited part)
    because open‑FDA indexes the product code.
    """
    if not ndc_code:
        raise ValueError("ndc_code cannot be empty")

    # keep everything up to the last hyphen
    product_ndc = "-".join(ndc_code.split("-")[:-1]) or ndc_code

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
