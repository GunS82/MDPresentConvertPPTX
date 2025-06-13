#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправленная версия fetcher.py с правильной обработкой Gist URL
"""

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
        print(f"🔍 Обнаружен Gist URL, извлекаем ID: {gist_id}")
        return _fetch_from_gist(gist_id)
    
    # Обычная загрузка URL
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def _fetch_from_gist(gist_id: str) -> str:
    """Загружает Markdown файл из GitHub Gist через API"""
    
    print(f"📡 Загружаем Gist через API: {gist_id}")
    
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
        print("🔑 Используем GitHub токен")
    else:
        print("⚠️  GitHub токен не найден, используем публичный доступ")
    
    api_url = f"https://api.github.com/gists/{gist_id}"
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        gist = response.json()
        
        print(f"📄 Найдено файлов в Gist: {len(gist['files'])}")
        
        # Ищем Markdown файлы
        markdown_files = []
        for filename, file_info in gist["files"].items():
            print(f"   - {filename} ({file_info.get('type', 'unknown type')})")
            if filename.endswith(".md") or file_info.get('type') == 'text/markdown':
                markdown_files.append((filename, file_info))
        
        if not markdown_files:
            # Если нет .md файлов, берем первый текстовый файл
            for filename, file_info in gist["files"].items():
                if file_info.get('type', '').startswith('text/'):
                    markdown_files.append((filename, file_info))
                    print(f"📝 Используем текстовый файл как Markdown: {filename}")
                    break
        
        if not markdown_files:
            available_files = list(gist["files"].keys())
            raise ValueError(f"No markdown file found in gist. Available files: {available_files}")
        
        # Берем первый найденный Markdown файл
        filename, file_info = markdown_files[0]
        print(f"✅ Загружаем файл: {filename}")
        
        # Загружаем raw контент
        raw_url = file_info["raw_url"]
        print(f"🔗 Raw URL: {raw_url}")
        
        raw_response = requests.get(raw_url)
        raw_response.raise_for_status()
        
        content = raw_response.text
        print(f"📊 Загружено {len(content)} символов")
        print(f"📄 Первые 200 символов: {repr(content[:200])}")
        
        return content
        
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch gist {gist_id}: {e}")
    except KeyError as e:
        raise ValueError(f"Invalid gist response format: {e}")

def test_gist_fetching():
    """Тестирует загрузку конкретного Gist"""
    
    gist_url = "https://gist.github.com/GunS82/21462de6ea445f8ec4a78130eb71ed0a"
    
    print("🧪 ТЕСТИРОВАНИЕ ЗАГРУЗКИ GIST")
    print("=" * 50)
    
    try:
        content = fetch_markdown(gist_url)
        
        print(f"✅ Успешно загружено {len(content)} символов")
        print()
        
        # Анализ разделителей
        separator_count = len(re.findall(r'^---$', content, re.MULTILINE))
        print(f"🔍 Найдено разделителей '---': {separator_count}")
        
        # Разделение на слайды
        SEPARATOR = re.compile(r"^---$", re.MULTILINE)
        parts = [p.strip() for p in SEPARATOR.split(content) if p.strip()]
        print(f"📋 Количество слайдов: {len(parts)}")
        
        # Показать первые части
        for i, part in enumerate(parts[:3]):
            print(f"\n📄 СЛАЙД {i+1}:")
            print("-" * 30)
            print(part[:300])
            if len(part) > 300:
                print("...")
        
        if len(parts) > 3:
            print(f"\n... и ещё {len(parts) - 3} слайдов")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gist_fetching()