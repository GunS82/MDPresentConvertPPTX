from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

load_dotenv()

GIST_RE = re.compile(r"^[0-9a-f]{20,}$")
GIST_URL_RE = re.compile(r"https://gist\.github\.com/[^/]+/([0-9a-f]{20,})")

def fetch_markdown(src: str) -> str:
    """Загружает Markdown контент из различных источников"""
    if src.startswith("http://") or src.startswith("https://"):
        return _fetch_from_url(src)
    elif GIST_RE.match(src):
        return _fetch_from_gist(src)
    else:
        path = Path(src)
        return path.read_text(encoding="utf-8")

def _fetch_from_url(url: str) -> str:
    """Загружает контент по URL с обработкой Gist ссылок"""
    
    # Проверяем, является ли это Gist URL
    gist_match = GIST_URL_RE.search(url)
    if gist_match:
        gist_id = gist_match.group(1)
        return _fetch_from_gist(gist_id)
    
    # Обычная загрузка URL
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def _fetch_from_gist(gist_id: str) -> str:
    """Загружает Markdown файл из GitHub Gist через API"""
    
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    api_url = f"https://api.github.com/gists/{gist_id}"
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        gist = response.json()
        
        # Ищем Markdown файлы
        markdown_files = []
        for filename, file_info in gist["files"].items():
            if filename.endswith(".md") or file_info.get('type') == 'text/markdown':
                markdown_files.append((filename, file_info))
        
        if not markdown_files:
            # Если нет .md файлов, берем первый текстовый файл
            for filename, file_info in gist["files"].items():
                if file_info.get('type', '').startswith('text/'):
                    markdown_files.append((filename, file_info))
                    break
        
        if not markdown_files:
            available_files = list(gist["files"].keys())
            raise ValueError(f"No markdown file found in gist. Available files: {available_files}")
        
        # Берем первый найденный Markdown файл
        filename, file_info = markdown_files[0]
        
        # Загружаем raw контент
        raw_url = file_info["raw_url"]
        raw_response = requests.get(raw_url)
        raw_response.raise_for_status()
        
        return raw_response.text
        
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch gist {gist_id}: {e}")
    except KeyError as e:
        raise ValueError(f"Invalid gist response format: {e}")
