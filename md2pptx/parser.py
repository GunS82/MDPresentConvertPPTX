from __future__ import annotations

import re
from typing import List

from bs4 import BeautifulSoup
import markdown
import requests
from tempfile import NamedTemporaryFile
from pathlib import Path

from .models import SlideModel, TextBlock, ImageBlock

SEPARATOR = re.compile(r"^---$", re.MULTILINE)


def clean_title(title: str) -> str:
    """Очищает заголовок от метаинформации"""
    if not title:
        return title
    
    # Удаляем префиксы типа "**Слайд X:"
    title = re.sub(r'^\*\*Слайд\s+\d+:\s*', '', title)
    title = re.sub(r'^Слайд\s+\d+:\s*', '', title)
    
    # Удаляем лишние звездочки и пробелы
    title = re.sub(r'^\*+\s*', '', title)
    title = re.sub(r'\s*\*+$', '', title)
    
    # Удаляем двойные пробелы
    title = re.sub(r'\s+', ' ', title)
    
    return title.strip()

def clean_text(text: str) -> str:
    """Очищает текст от лишней метаинформации"""
    if not text:
        return text
    
    # Удаляем промты для AI
    text = re.sub(r'\(Промт для AI:.*?\)', '', text, flags=re.DOTALL)
    
    # Удаляем лишние пробелы и переносы
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def extract_title_from_content(content: str) -> tuple[str, str]:
    """Извлекает заголовок из содержимого и возвращает (заголовок, оставшийся_контент)"""
    
    lines = content.strip().split('\n')
    title = None
    remaining_lines = lines
    
    # Ищем заголовок в первых строках
    for i, line in enumerate(lines[:3]):
        line = line.strip()
        
        # Проверяем различные форматы заголовков
        if line.startswith('#'):
            # Markdown заголовок
            title = re.sub(r'^#+\s*', '', line)
            remaining_lines = lines[i+1:]
            break
        elif line.startswith('**') and line.endswith('**'):
            # Жирный текст как заголовок
            title = line.strip('*')
            remaining_lines = lines[i+1:]
            break
        elif re.match(r'^\*\*Слайд\s+\d+:', line):
            # Специальный формат "**Слайд X:"
            title = re.sub(r'^\*\*Слайд\s+\d+:\s*', '', line).rstrip('*')
            remaining_lines = lines[i+1:]
            break
    
    if title:
        title = clean_title(title)
        remaining_content = '\n'.join(remaining_lines).strip()
        return title, remaining_content
    
    return None, content

def parse_markdown(text: str) -> List[SlideModel]:
    """Парсит Markdown текст в список слайдов с улучшенной обработкой"""
    
    # Разделяем на части по разделителям
    parts = [p.strip() for p in SEPARATOR.split(text) if p.strip()]
    slides: List[SlideModel] = []
    
    for i, part in enumerate(parts):
        # Извлекаем заголовок из содержимого
        title, content = extract_title_from_content(part)
        
        # Конвертируем в HTML
        html = markdown.markdown(content)
        soup = BeautifulSoup(html, "html.parser")
        
        # Если заголовок не найден, ищем в HTML
        if not title:
            title_el = soup.find(["h1", "h2", "h3", "strong"])
            if title_el:
                title = clean_title(title_el.get_text(strip=True))
                # Удаляем элемент заголовка из soup, чтобы не дублировать
                title_el.decompose()
        
        # Если заголовок все еще не найден, создаем автоматический
        if not title:
            title = f"Слайд {i + 1}"
        
        blocks = []
        
        # Обрабатываем списки
        bullets = []
        for li in soup.find_all("li"):
            bullet_text = clean_text(li.get_text(strip=True))
            if bullet_text:
                bullets.append(bullet_text)
        
        if bullets:
            blocks.append(TextBlock(text="", bullets=bullets))
        
        # Обрабатываем параграфы
        for p in soup.find_all("p"):
            p_text = clean_text(p.get_text(strip=True))
            if p_text:
                blocks.append(TextBlock(text=p_text))
        
        # Обрабатываем изображения
        for img in soup.find_all("img"):
            src = img.get("src", "")
            alt = img.get("alt", "")
            
            if src.startswith("http://") or src.startswith("https://"):
                try:
                    response = requests.get(src, timeout=10)
                    response.raise_for_status()
                    suffix = Path(src).suffix or ".img"
                    tmp = NamedTemporaryFile(delete=False, suffix=suffix)
                    tmp.write(response.content)
                    tmp.flush()
                    src = tmp.name
                except Exception as e:
                    print(f"⚠️  Не удалось загрузить изображение {src}: {e}")
                    continue
            elif not Path(src).exists():
                print(f"⚠️  Изображение не найдено: {src}")
                continue
            
            blocks.append(ImageBlock(src=src, alt=alt))
        
        # Создаем слайд
        slide = SlideModel(title=title, blocks=blocks)
        slides.append(slide)
    
    return slides
