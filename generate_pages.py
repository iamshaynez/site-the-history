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
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

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

def generate_sitemap_xml(pages_data, base_url="https://your-domain.com"):
    """生成 sitemap.xml 文件"""
    print("开始生成 sitemap.xml...")
    
    # 创建根元素
    urlset = Element('urlset')
    urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    
    # 添加首页
    url_elem = SubElement(urlset, 'url')
    SubElement(url_elem, 'loc').text = base_url
    SubElement(url_elem, 'lastmod').text = datetime.now().strftime('%Y-%m-%d')
    SubElement(url_elem, 'changefreq').text = 'daily'
    SubElement(url_elem, 'priority').text = '1.0'
    
    # 为每个文章添加 URL
    for category_name, category_data in pages_data['categories'].items():
        for article in category_data['articles']:
            url_elem = SubElement(urlset, 'url')
            
            # 构建完整 URL
            full_url = f"{base_url.rstrip('/')}/{article['url']}"
            SubElement(url_elem, 'loc').text = full_url
            
            # 使用文章日期作为最后修改时间
            SubElement(url_elem, 'lastmod').text = article['date']
            
            # 设置更新频率和优先级
            SubElement(url_elem, 'changefreq').text = 'weekly'
            SubElement(url_elem, 'priority').text = '0.8'
    
    # 生成格式化的 XML
    rough_string = tostring(urlset, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')
    
    # 移除空行
    pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
    
    # 保存文件
    output_file = Path('public/sitemap.xml')
    
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(pretty_xml)
        
        print(f"✅ 成功生成 {output_file}")
        
        # 统计信息
        total_urls = 1 + sum(len(cat['articles']) for cat in pages_data['categories'].values())
        print(f"📊 Sitemap 统计:")
        print(f"   - 总 URL 数量: {total_urls}")
        print(f"   - 首页: 1 个")
        
        for category_name, category_data in pages_data['categories'].items():
            print(f"   - {category_data['name']}: {len(category_data['articles'])} 个页面")
        
        return True
        
    except Exception as e:
        print(f"❌ 生成 sitemap.xml 时出错: {e}")
        return False

def generate_robots_txt(base_url="https://your-domain.com"):
    """生成 robots.txt 文件"""
    print("开始生成 robots.txt...")
    
    robots_content = f"""User-agent: *
Allow: /

# Sitemap
Sitemap: {base_url.rstrip('/')}/sitemap.xml

# 禁止访问的目录
Disallow: /admin/
Disallow: /private/
Disallow: /*.json$
"""
    
    output_file = Path('public/robots.txt')
    
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(robots_content)
        
        print(f"✅ 成功生成 {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ 生成 robots.txt 时出错: {e}")
        return False

if __name__ == '__main__':
    print("🚀 自动生成 pages.json 和 sitemap.xml 文件")
    print("=" * 60)
    
    # 生成 pages.json
    success_pages = generate_pages_json()
    
    if success_pages:
        # 重新读取生成的 pages.json 数据
        try:
            with open('public/pages.json', 'r', encoding='utf-8') as file:
                pages_data = json.load(file)
            
            print("\n" + "=" * 60)
            
            # 生成 sitemap.xml
            base_url = input("请输入网站的基础 URL (例如: https://your-domain.com): ").strip()
            if not base_url:
                base_url = "https://learn.xiaowenz.com"
                print(f"使用默认 URL: {base_url}")
            
            success_sitemap = generate_sitemap_xml(pages_data, base_url)
            
            # 生成 robots.txt
            success_robots = generate_robots_txt(base_url)
            
            print("\n" + "=" * 60)
            print("📋 完成总结:")
            print(f"   ✅ pages.json: {'成功' if success_pages else '失败'}")
            print(f"   ✅ sitemap.xml: {'成功' if success_sitemap else '失败'}")
            print(f"   ✅ robots.txt: {'成功' if success_robots else '失败'}")
            
            if success_pages and success_sitemap and success_robots:
                print("\n🎉 所有任务完成！")
            else:
                print("\n⚠️  部分任务失败，请检查错误信息！")
                
        except Exception as e:
            print(f"\n❌ 读取 pages.json 文件时出错: {e}")
    else:
        print("\n❌ pages.json 生成失败，跳过 sitemap.xml 生成！")
