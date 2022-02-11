from fastapi import Header, HTTPException


async def get_qr_token_header(qr_token: str = Header(...)):
    if qr_token is None:
        raise HTTPException(status_code=400, detail="QR-Token is missing")
