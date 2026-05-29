from fastapi import Header, HTTPException, status

# =====================================================================
# STEP 2: SIMULATED CREDENTIAL STORAGE (PLUGGABLE CORE)
# =====================================================================
# This layout maps secure tokens to structural metadata. 
# You can swap this dictionary later for a database query (PostgreSQL/Redis/Vault).
API_KEYS = {
    "dev-key-company-a": {
        "tenant_id": "company-a",
        "tier": "enterprise",
        "rate_limit": 100
    },
    "dev-key-company-b": {
        "tenant_id": "company-b",
        "tier": "premium",
        "rate_limit": 50
    }
}


# =====================================================================
# STEP 3: CREENTIAL VALIDATION CORE ENGINE
# =====================================================================
def validate_api_key(api_key: str) -> dict | None:
    """
    Looks up an incoming API token against security storage.
    Returns the metadata dictionary if valid, otherwise returns None.
    """
    if not api_key or api_key not in API_KEYS:
        return None
        
    return API_KEYS[api_key]


# =====================================================================
# STEP 4: FASTAPI GATEWAY DEPENDENCY INTERCEPTOR
# =====================================================================
def authorize_request(x_api_key: str = Header(..., alias="X-API-Key")) -> dict:
    """
    FastAPI Security Dependency. 
    Intercepts headers, enforces validation, and rejects unauthenticated traffic.
    
    Alias maps parameter 'x_api_key' to search for standard HTTP 'X-API-Key'.
    """
    api_data = validate_api_key(x_api_key)

    if not api_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: The provided X-API-Key is invalid or has been revoked."
        )

    # Injects the security context straight into the downstream endpoint handler
    return api_data