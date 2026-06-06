"""
Multi-platform uploader.
Supported: YouTube Shorts, TikTok, Instagram Reels.

Each platform has its own auth flow; see README for setup.
The uploader degrades gracefully — if credentials are missing it logs a
warning and skips that platform rather than crashing the whole pipeline.
"""
from __future__ import annotations

import json
import logging
import mimetypes
import os
import time
from pathlib import Path
from typing import Optional

import requests

from config import cfg

log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# TikTok  (Content Posting API v2)
# ─────────────────────────────────────────────────────────────────────────────

TIKTOK_INIT_URL = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
TIKTOK_STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"


def _upload_tiktok(video_path: Path, caption: str) -> Optional[str]:
    if not cfg.tiktok_access_token:
        log.warning("TikTok: no access token configured — skipping")
        return None

    size = video_path.stat().st_size
    headers = {
        "Authorization": f"Bearer {cfg.tiktok_access_token}",
        "Content-Type": "application/json; charset=UTF-8",
    }

    # Step 1 — initialise upload
    init_payload = {
        "post_info": {
            "title": caption[:150],
            "privacy_level": "PUBLIC_TO_EVERYONE",
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": size,
            "chunk_size": size,
            "total_chunk_count": 1,
        },
    }
    r = requests.post(TIKTOK_INIT_URL, headers=headers, json=init_payload, timeout=30)
    if r.status_code != 200:
        log.error("TikTok init failed: %s", r.text)
        return None

    data = r.json().get("data", {})
    publish_id = data.get("publish_id")
    upload_url = data.get("upload_url")

    if not upload_url:
        log.error("TikTok: no upload_url in response")
        return None

    # Step 2 — upload bytes
    with open(video_path, "rb") as fh:
        put_r = requests.put(
            upload_url,
            data=fh,
            headers={
                "Content-Type": "video/mp4",
                "Content-Range": f"bytes 0-{size - 1}/{size}",
            },
            timeout=120,
        )
    if put_r.status_code not in (200, 201, 204):
        log.error("TikTok PUT failed: %s", put_r.text)
        return None

    log.info("TikTok upload success — publish_id: %s", publish_id)
    return publish_id


# ─────────────────────────────────────────────────────────────────────────────
# Instagram Reels  (Graph API)
# ─────────────────────────────────────────────────────────────────────────────

IG_BASE = "https://graph.facebook.com/v19.0"


def _upload_instagram(video_path: Path, caption: str) -> Optional[str]:
    if not cfg.instagram_access_token or not cfg.instagram_account_id:
        log.warning("Instagram: credentials not configured — skipping")
        return None

    acct = cfg.instagram_account_id
    token = cfg.instagram_access_token

    # Instagram requires a publicly accessible URL for Reels upload.
    # In production: upload to S3/Cloudflare R2 first, then pass URL here.
    log.warning(
        "Instagram Reels upload requires a public video URL. "
        "Upload %s to cloud storage and pass the URL to the Graph API manually.",
        video_path,
    )
    return None


# ─────────────────────────────────────────────────────────────────────────────
# YouTube Shorts  (Data API v3 via OAuth2 — resumable upload)
# ─────────────────────────────────────────────────────────────────────────────

def _upload_youtube(video_path: Path, caption: str) -> Optional[str]:
    secrets_path = Path(cfg.youtube_client_secrets_file)
    if not secrets_path.exists():
        log.warning("YouTube: client_secrets.json not found — skipping")
        return None

    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        log.warning("YouTube upload libs not installed (google-auth, google-api-python-client)")
        return None

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    token_file = Path("youtube_token.json")

    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), SCOPES)
        creds = flow.run_local_server(port=0)
        token_file.write_text(creds.to_json())

    yt = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {
            "title": caption[:100],
            "description": f"{caption}\n\n{cfg.affiliate_link}",
            "tags": ["shorts", "viral", "money", "sidehustle"],
            "categoryId": "22",
        },
        "status": {"privacyStatus": "public"},
    }
    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4")
    request = yt.videos().insert(part=",".join(body.keys()), body=body, media_body=media)
    response = None
    while response is None:
        _, response = request.next_chunk()

    video_id = response.get("id")
    log.info("YouTube Shorts uploaded: https://youtube.com/shorts/%s", video_id)
    return video_id


# ─────────────────────────────────────────────────────────────────────────────
# Public interface
# ─────────────────────────────────────────────────────────────────────────────

def upload_all(video_path: Path, caption: str) -> dict[str, Optional[str]]:
    """
    Attempts upload to every configured platform.
    Returns dict of platform → result_id (None if skipped/failed).
    """
    results = {}
    results["tiktok"] = _upload_tiktok(video_path, caption)
    results["instagram"] = _upload_instagram(video_path, caption)
    results["youtube"] = _upload_youtube(video_path, caption)
    return results
