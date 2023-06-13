def pagination_params(offset: int = 0, limit: int = 15) -> dict:
    return {"offset": offset, "limit": limit}
