#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для анализа исходного Markdown контента из Gist
"""

import re
from md2pptx.fetcher import fetch_markdown

def debug_gist_content():
    """Анализирует содержимое Gist и показывает проблемы с разделением слайдов"""
    
    gist_url = 'https://gist.github.com/GunS82/21462de6ea445f8ec4a78130eb71ed0a'
    
    print("🔍 АНАЛИЗ ИСХОДНОГО MARKDOWN ИЗ GIST")
    print("=" * 60)
    
    try:
        content = fetch_markdown(gist_url)
        print(f"📊 Длина контента: {len(content)} символов")
        print(f"📄 Количество строк: {len(content.splitlines())}")
        print()
        
        # Показать первые 1000 символов
        print("📝 ПЕРВЫЕ 1000 СИМВОЛОВ:")
        print("-" * 40)
        print(content[:1000])
        print("-" * 40)
        print()
        
        # Анализ разделителей
        print("🔍 АНАЛИЗ РАЗДЕЛИТЕЛЕЙ СЛАЙДОВ:")
        print("-" * 40)
        
        # Поиск различных вариантов разделителей
        separator_patterns = [
            (r'^---$', 'Стандартный разделитель (---)'),
            (r'^-{3,}$', 'Три или более дефисов'),
            (r'---', 'Любые три дефиса'),
            (r'\n\n+', 'Двойные переносы строк'),
        ]
        
        for pattern, description in separator_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            parts = re.split(pattern, content, flags=re.MULTILINE)
            print(f"   {description}: найдено {len(matches)} совпадений, {len(parts)} частей")
        
        print()
        
        # Используем стандартный разделитель из парсера
        SEPARATOR = re.compile(r"^---$", re.MULTILINE)
        parts = [p.strip() for p in SEPARATOR.split(content) if p.strip()]
        
        print(f"📋 РАЗДЕЛЕНИЕ НА СЛАЙДЫ (стандартный алгоритм):")
        print(f"   Найдено частей: {len(parts)}")
        print()
        
        if len(parts) == 1:
            print("⚠️  ПРОБЛЕМА: Весь контент попал в один слайд!")
            print("   Возможные причины:")
            print("   - Отсутствуют разделители ---")
            print("   - Разделители не на отдельной строке")
            print("   - Неправильный формат разделителей")
            print()
            
            # Поиск потенциальных разделителей
            lines = content.splitlines()
            potential_separators = []
            for i, line in enumerate(lines):
                if '---' in line or line.strip() == '' and i > 0 and i < len(lines)-1:
                    potential_separators.append((i+1, repr(line)))
            
            if potential_separators:
                print("🔍 ПОТЕНЦИАЛЬНЫЕ РАЗДЕЛИТЕЛИ:")
                for line_num, line_content in potential_separators[:10]:
                    print(f"   Строка {line_num}: {line_content}")
            print()
        
        # Показать первые несколько частей
        for i, part in enumerate(parts[:3]):
            print(f"📄 ЧАСТЬ {i+1} (первые 300 символов):")
            print("-" * 30)
            print(part[:300])
            if len(part) > 300:
                print("...")
            print("-" * 30)
            print()
        
        if len(parts) > 3:
            print(f"... и ещё {len(parts) - 3} частей")
            print()
        
        # Анализ заголовков
        print("📋 АНАЛИЗ ЗАГОЛОВКОВ:")
        print("-" * 30)
        
        h1_count = len(re.findall(r'^# ', content, re.MULTILINE))
        h2_count = len(re.findall(r'^## ', content, re.MULTILINE))
        h3_count = len(re.findall(r'^### ', content, re.MULTILINE))
        
        print(f"   H1 заголовков: {h1_count}")
        print(f"   H2 заголовков: {h2_count}")
        print(f"   H3 заголовков: {h3_count}")
        
        # Найти все заголовки
        headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        if headers:
            print("\n   Найденные заголовки:")
            for level, title in headers[:10]:
                print(f"   {level} {title}")
            if len(headers) > 10:
                print(f"   ... и ещё {len(headers) - 10} заголовков")
        
        print()
        
    except Exception as e:
        print(f"❌ Ошибка при анализе: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_gist_content()