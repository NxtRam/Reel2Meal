"""
routers/media.py — Video/audio proxy endpoint.

Proxies external media URLs through our backend so the browser never
hits cross-origin restrictions. Sends full browser-like headers to
bypass hotlink protection on sites like Pexels, Mixkit, Coverr, etc.

Endpoint:
  GET /api/v1/media/proxy?url=<encoded_url>

Supports:
  - Range requests (video seeking)
  - CORS=* on all responses
  - Chunked streaming (512 KB chunks)
"""
import urllib.error
import urllib.parse
import urllib.request

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/media", tags=["Media"], redirect_slashes=False)

CHUNK_SIZE = 512 * 1024  # 512 KB
ALLOWED_CONTENT_TYPES = ("video/", "audio/", "application/octet-stream")
BLOCKED_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0", "169.254.169.254"}

# Full Chrome 120 browser header set — bypasses most hotlink-protection CDNs
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "video/webm,video/mp4,video/*,audio/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "identity",   # no compression → stream raw bytes
    "Sec-Fetch-Dest": "video",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "cross-site",
    "Connection": "keep-alive",
}

# Per-domain Referer spoofing
DOMAIN_REFERERS = {
    "pexels.com":   "https://www.pexels.com/",
    "mixkit.co":    "https://mixkit.co/",
    "coverr.co":    "https://coverr.co/",
    "videvo.net":   "https://www.videvo.net/",
    "pixabay.com":  "https://pixabay.com/",
    "soundhelix.com": "https://www.soundhelix.com/",
}


def _make_headers(source_url: str, range_header: str | None) -> dict:
    parsed = urllib.parse.urlparse(source_url)
    hostname = (parsed.hostname or "").lower()

    headers = {**BROWSER_HEADERS}

    # Add domain-specific referer
    for domain, referer in DOMAIN_REFERERS.items():
        if domain in hostname:
            headers["Referer"] = referer
            headers["Origin"] = referer.rstrip("/")
            break
    else:
        # Generic referer: same origin as the file
        base = f"{parsed.scheme}://{parsed.hostname}"
        headers["Referer"] = base + "/"
        headers["Origin"] = base

    if range_header:
        headers["Range"] = range_header

    return headers


def _validate_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http/https URLs allowed.")
    if parsed.hostname and parsed.hostname.lower() in BLOCKED_HOSTS:
        raise HTTPException(status_code=400, detail="Private network URLs not allowed.")
    return url


@router.get("/proxy")
async def proxy_media(
    url: str = Query(..., description="URL-encoded media source URL"),
    request: Request = None,
):
    """
    Stream a remote video or audio file through the backend with full
    browser-like headers to bypass hotlink protection.
    Supports Range requests for video seeking.
    """
    source_url = _validate_url(url)
    range_header = request.headers.get("Range") if request else None
    headers = _make_headers(source_url, range_header)

    try:
        req = urllib.request.Request(source_url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=20)
    except urllib.error.HTTPError as e:
        raise HTTPException(status_code=e.code, detail=f"Source returned HTTP {e.code}")
    except urllib.error.URLError as e:
        raise HTTPException(status_code=502, detail=f"Could not reach source: {e.reason}")

    content_type = resp.headers.get("Content-Type", "video/mp4")
    if not any(content_type.startswith(t) for t in ALLOWED_CONTENT_TYPES):
        resp.close()
        raise HTTPException(status_code=400, detail=f"Unsupported content type: {content_type}")

    response_headers = {
        "Accept-Ranges": "bytes",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
        "Cache-Control": "public, max-age=3600",
    }
    if cl := resp.headers.get("Content-Length"):
        response_headers["Content-Length"] = cl
    if cr := resp.headers.get("Content-Range"):
        response_headers["Content-Range"] = cr

    status_code = 206 if (range_header and resp.status == 206) else 200

    def iter_chunks():
        try:
            while chunk := resp.read(CHUNK_SIZE):
                yield chunk
        finally:
            resp.close()

    return StreamingResponse(
        iter_chunks(),
        status_code=status_code,
        media_type=content_type,
        headers=response_headers,
    )
