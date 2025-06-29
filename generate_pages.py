#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成 pages.json 文件的脚本
遍历 public 目录下的所有 HTML 文件，提取标题和元数据，生成 JSON 配置文件
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

def extract_title_from_html(file_path):
    """从HTML文件中提取标题"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            soup = BeautifulSoup(content, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text().strip()
    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")
    return None

def extract_date_from_filename(filename):
    """从文件名中提取日期"""
    # 匹配 YYYY-MM-DD 格式的日期
    date_pattern = r'(\d{4}-\d{2}-\d{2})'
    match = re.search(date_pattern, filename)
    if match:
        return match.group(1)
    return None

def get_category_info(category_name):
    """获取分类的显示名称和图标"""
    category_mapping = {
        'culture': {
            'name': '文化 Culture',
            'icon': '🎨'
        },
        'history': {
            'name': '历史 History',
            'icon': '📚'
        },
        'politics': {
            'name': '政治 Politics',
            'icon': '🏛️'
        },
        'economy': {
            'name': '经济 Economy',
            'icon': '💰'
        },
        'science': {
            'name': '科学 Science',
            'icon': '🔬'
        },
        'art': {
            'name': '艺术 Art',
            'icon': '🎭'
        },
        'literature': {
            'name': '文学 Literature',
            'icon': '📖'
        }
    }
    
    return category_mapping.get(category_name, {
        'name': category_name.capitalize(),
        'icon': '📄'
    })

def scan_public_directory():
    """扫描 public 目录，生成页面数据"""
    public_dir = Path('public')
    
    if not public_dir.exists():
        print("错误: public 目录不存在")
        return None
    
    categories = {}
    
    # 遍历 public 目录下的所有子目录
    for category_dir in public_dir.iterdir():
        if category_dir.is_dir() and category_dir.name != '__pycache__':
            category_name = category_dir.name
            category_info = get_category_info(category_name)
            
            articles = []
            
            # 遍历分类目录下的所有 HTML 文件
            for html_file in category_dir.glob('*.html'):
                title = extract_title_from_html(html_file)
                date = extract_date_from_filename(html_file.name)
                
                if title and date:
                    # 计算相对于 public 目录的路径
                    relative_path = f"{category_name}/{html_file.name}"
                    
                    article = {
                        'title': title,
                        'url': relative_path,
                        'date': date
                    }
                    articles.append(article)
                else:
                    print(f"警告: 无法提取 {html_file} 的标题或日期")
            
            # 按日期倒序排序（最新的在前面）
            articles.sort(key=lambda x: x['date'], reverse=True)
            
            if articles:  # 只添加有文章的分类
                categories[category_name] = {
                    'name': category_info['name'],
                    'icon': category_info['icon'],
                    'articles': articles
                }
    
    return {
        'categories': categories
    }

def generate_pages_json():
    """生成 pages.json 文件"""
    print("开始扫描 public 目录...")
    
    pages_data = scan_public_directory()
    
    if pages_data is None:
        return False
    
    # 生成 JSON 文件
    output_file = Path('public/pages.json')
    
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(pages_data, file, ensure_ascii=False, indent=2)
        
        print(f"✅ 成功生成 {output_file}")
        
        # 打印统计信息
        total_articles = sum(len(cat['articles']) for cat in pages_data['categories'].values())
        print(f"📊 统计信息:")
        print(f"   - 分类数量: {len(pages_data['categories'])}")
        print(f"   - 文章总数: {total_articles}")
        
        for category_name, category_data in pages_data['categories'].items():
            print(f"   - {category_data['name']}: {len(category_data['articles'])} 篇文章")
        
        return True
        
    except Exception as e:
        print(f"❌ 生成文件时出错: {e}")
        return False

if __name__ == '__main__':
    print("🚀 自动生成 pages.json 文件")
    print("=" * 50)
    
    success = generate_pages_json()
    
    if success:
        print("\n🎉 任务完成！")
    else:
        print("\n❌ 任务失败！")
