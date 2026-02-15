#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动生成博客首页 /var/www/html/blog.html
文章目录: /var/www/html/blog/posts/
"""

import os
import re
from datetime import datetime
from pathlib import Path

# === 路径配置 ===
POSTS_DIR = Path("/var/www/html/blog/posts")      # Markdown 文章目录
OUTPUT_FILE = Path("/var/www/html/blog.html")     # 博客首页输出位置

def extract_metadata(md_text):
    """从 Markdown 提取 title 和 date"""
    title = "无标题"
    date_str = "1970-01-01"
    
    # 尝试解析 YAML Front Matter
    fm_match = re.match(r'^---\s*\n([\s\S]*?)\n---\s*\n', md_text)
    if fm_match:
        fm = fm_match.group(1)
        title_match = re.search(r'^title\s*[:=]\s*["\']?([^"\'\n]+)["\']?', fm, re.MULTILINE | re.IGNORECASE)
        date_match = re.search(r'^date\s*[:=]\s*(\d{4}-\d{2}-\d{2})', fm, re.MULTILINE | re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
        if date_match:
            date_str = date_match.group(1).strip()
        return title, date_str

    # 兼容旧格式：首行 #标题，第二行日期
    lines = md_text.strip().split('\n')
    if lines and lines[0].startswith('# '):
        title = lines[0][2:].strip()
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            if re.fullmatch(r'\d{4}-\d{2}-\d{2}', line):
                date_str = line
            break
    
    return title, date_str

def main():
    posts = []
    
    if not POSTS_DIR.exists():
        print(f"❌ 错误：文章目录不存在 {POSTS_DIR}")
        return

    for md_file in POSTS_DIR.glob("*.md"):
        slug = md_file.stem
        try:
            content = md_file.read_text(encoding='utf-8')
            title, date_str = extract_metadata(content)
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                date_obj = datetime(1970, 1, 1)
            posts.append({
                'slug': slug,
                'title': title,
                'date': date_str,
                'date_obj': date_obj
            })
        except Exception as e:
            print(f"⚠️ 跳过文件 {md_file.name}: {e}")
    
    # 按日期倒序（最新在前）
    posts.sort(key=lambda x: x['date_obj'], reverse=True)
    
    # 生成文章列表 HTML
    if posts:
        post_items = ""
        for post in posts:
            formatted_date = datetime.strptime(post['date'], "%Y-%m-%d").strftime("%Y年%m月%d日")
            post_items += f'''
        <div class="blog-post">
          <h2><a href="/blog/post.html?slug={post['slug']}">{post['title']}</a></h2>
          <div class="post-meta"><i class="far fa-calendar"></i> {formatted_date}</div>
        </div>
        '''
    else:
        post_items = '<p style="text-align:center;color:#bbb;font-size:1.1rem;">暂无文章</p>'
    
    # === 完整 HTML 模板 ===
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>博客 - 韩邦泽的小站</title>
  <!-- Font Awesome -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" />
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    }}
    body, html {{
      height: 100%;
    }}
    body {{
      background-size: cover;
      background-position: center;
      background-repeat: no-repeat;
      background-attachment: fixed;
      color: white;
      position: relative;
    }}
    body::before {{
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.4);
      z-index: -1;
    }}

    header {{
      background-color: rgba(44, 62, 80, 0.7);
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      backdrop-filter: blur(5px);
      position: sticky;
      top: 0;
      z-index: 10;
    }}
    .site-title {{
      color: #ecf0f1;
      font-size: 1.5rem;
      font-weight: bold;
    }}
    nav ul {{
      list-style: none;
      display: flex;
      gap: 1.5rem;
    }}
    nav a {{
      color: #ecf0f1;
      text-decoration: none;
      font-weight: 500;
      transition: color 0.3s;
    }}
    nav a:hover {{
      color: #3498db;
    }}

    main {{
      max-width: 900px;
      margin: 2.5rem auto;
      padding: 0 1.5rem;
    }}
    .page-title {{
      text-align: center;
      margin-bottom: 2rem;
      font-size: 2.2rem;
      color: #ecf0f1;
    }}

    .blog-post {{
      background: rgba(20, 25, 30, 0.85);
      padding: 1.8rem;
      margin-bottom: 1.8rem;
      border-radius: 12px;
      backdrop-filter: blur(4px);
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }}
    .blog-post h2 {{
      margin-bottom: 0.8rem;
      font-size: 1.6rem;
    }}
    .blog-post h2 a {{
      color: #3498db;
      text-decoration: none;
      transition: color 0.3s;
    }}
    .blog-post h2 a:hover {{
      color: #2980b9;
      text-decoration: underline;
    }}
    .post-meta {{
      color: #bbb;
      font-size: 0.95rem;
    }}

    @media (max-width: 600px) {{
      .page-title {{ font-size: 1.8rem; }}
      main {{ padding: 0 1rem; }}
      header {{ flex-direction: column; gap: 1rem; }}
      nav ul {{ flex-wrap: wrap; justify-content: center; }}
      .blog-post {{
        padding: 1.2rem;
      }}
    }}
  </style>
</head>
<body>

<header>
  <div class="site-title">韩邦泽的小站</div>
  <nav>
    <ul>
      <li><a href="/">首页</a></li>
      <li><a href="/about.html">关于我</a></li>
      <li><a href="/downloads/">下载</a></li>
      <li><a href="/apps.html">应用</a></li>
      <li><a href="/blog.html" class="active">博客</a></li>
    </ul>
  </nav>
</header>

<main>
  <h1 class="page-title">技术博客</h1>
  {post_items}
</main>

<script>
  // === 同步背景图（与 post.html 一致）===
  function getCookie(name) {{
    return document.cookie.split('; ').reduce((r, v) => {{
      const parts = v.split('=');
      return parts[0] === name ? decodeURIComponent(parts[1]) : r;
    }}, '');
  }}
  const images = [
    "bing-wallpaper/2025-10-10.jpg",
    "bing-wallpaper/2025-10-11.jpg",
    "bing-wallpaper/2025-10-12.jpg",
    "bing-wallpaper/2025-10-13.jpg",
    "bing-wallpaper/2025-10-14.jpg",
    "bing-wallpaper/2025-10-15.jpg",
    "bing-wallpaper/2025-10-16.jpg",
    "bing-wallpaper/2025-10-17.jpg",
    "bing-wallpaper/2025-10-18.jpg",
    "bing-wallpaper/2025-10-19.jpg",
    "bing-wallpaper/2025-10-1.jpg",
    "bing-wallpaper/2025-10-20.jpg",
    "bing-wallpaper/2025-10-21.jpg",
    "bing-wallpaper/2025-10-22.jpg",
    "bing-wallpaper/2025-10-23.jpg",
    "bing-wallpaper/2025-10-24.jpg",
    "bing-wallpaper/2025-10-25.jpg",
    "bing-wallpaper/2025-10-26.jpg",
    "bing-wallpaper/2025-10-27.jpg",
    "bing-wallpaper/2025-10-28.jpg",
    "bing-wallpaper/2025-10-29.jpg",
    "bing-wallpaper/2025-10-2.jpg",
    "bing-wallpaper/2025-10-30.jpg",
    "bing-wallpaper/2025-10-31.jpg",
    "bing-wallpaper/2025-10-3.jpg",
    "bing-wallpaper/2025-10-4.jpg",
    "bing-wallpaper/2025-10-5.jpg",
    "bing-wallpaper/2025-10-6.jpg",
    "bing-wallpaper/2025-10-7.jpg",
    "bing-wallpaper/2025-10-8.jpg",
    "bing-wallpaper/2025-10-9.jpg",
    "bing-wallpaper/2025-11-10.jpg",
    "bing-wallpaper/2025-11-11.jpg",
    "bing-wallpaper/2025-11-12.jpg",
    "bing-wallpaper/2025-11-13.jpg",
    "bing-wallpaper/2025-11-14.jpg",
    "bing-wallpaper/2025-11-15.jpg",
    "bing-wallpaper/2025-11-16.jpg",
    "bing-wallpaper/2025-11-17.jpg",
    "bing-wallpaper/2025-11-18.jpg",
    "bing-wallpaper/2025-11-19.jpg",
    "bing-wallpaper/2025-11-1.jpg",
    "bing-wallpaper/2025-11-20.jpg",
    "bing-wallpaper/2025-11-21.jpg",
    "bing-wallpaper/2025-11-22.jpg",
    "bing-wallpaper/2025-11-23.jpg",
    "bing-wallpaper/2025-11-24.jpg",
    "bing-wallpaper/2025-11-25.jpg",
    "bing-wallpaper/2025-11-26.jpg",
    "bing-wallpaper/2025-11-27.jpg",
    "bing-wallpaper/2025-11-28.jpg",
    "bing-wallpaper/2025-11-29.jpg",
    "bing-wallpaper/2025-11-2.jpg",
    "bing-wallpaper/2025-11-30.jpg",
    "bing-wallpaper/2025-11-3.jpg",
    "bing-wallpaper/2025-11-4.jpg",
    "bing-wallpaper/2025-11-5.jpg",
    "bing-wallpaper/2025-11-6.jpg",
    "bing-wallpaper/2025-11-7.jpg",
    "bing-wallpaper/2025-11-8.jpg",
    "bing-wallpaper/2025-11-9.jpg",
    "bing-wallpaper/2025-12-10.jpg",
    "bing-wallpaper/2025-12-11.jpg",
    "bing-wallpaper/2025-12-12.jpg",
    "bing-wallpaper/2025-12-13.jpg",
    "bing-wallpaper/2025-12-14.jpg",
    "bing-wallpaper/2025-12-15.jpg",
    "bing-wallpaper/2025-12-16.jpg",
    "bing-wallpaper/2025-12-17.jpg",
    "bing-wallpaper/2025-12-18.jpg",
    "bing-wallpaper/2025-12-19.jpg",
    "bing-wallpaper/2025-12-1.jpg",
    "bing-wallpaper/2025-12-20.jpg",
    "bing-wallpaper/2025-12-21.jpg",
    "bing-wallpaper/2025-12-22.jpg",
    "bing-wallpaper/2025-12-23.jpg",
    "bing-wallpaper/2025-12-24.jpg",
    "bing-wallpaper/2025-12-25.jpg",
    "bing-wallpaper/2025-12-26.jpg",
    "bing-wallpaper/2025-12-27.jpg",
    "bing-wallpaper/2025-12-28.jpg",
    "bing-wallpaper/2025-12-29.jpg",
    "bing-wallpaper/2025-12-2.jpg",
    "bing-wallpaper/2025-12-3.jpg",
    "bing-wallpaper/2025-12-4.jpg",
    "bing-wallpaper/2025-12-5.jpg",
    "bing-wallpaper/2025-12-6.jpg",
    "bing-wallpaper/2025-12-7.jpg",
    "bing-wallpaper/2025-12-8.jpg",
    "bing-wallpaper/2025-12-9.jpg",
    "bing-wallpaper/2025-5-30.jpg",
    "bing-wallpaper/2025-5-31.jpg",
    "bing-wallpaper/2025-6-10.jpg",
    "bing-wallpaper/2025-6-11.jpg",
    "bing-wallpaper/2025-6-12.jpg",
    "bing-wallpaper/2025-6-13.jpg",
    "bing-wallpaper/2025-6-14.jpg",
    "bing-wallpaper/2025-6-15.jpg",
    "bing-wallpaper/2025-6-16.jpg",
    "bing-wallpaper/2025-6-17.jpg",
    "bing-wallpaper/2025-6-18.jpg",
    "bing-wallpaper/2025-6-19.jpg",
    "bing-wallpaper/2025-6-1.jpg",
    "bing-wallpaper/2025-6-20.jpg",
    "bing-wallpaper/2025-6-21.jpg",
    "bing-wallpaper/2025-6-22.jpg",
    "bing-wallpaper/2025-6-23.jpg",
    "bing-wallpaper/2025-6-24.jpg",
    "bing-wallpaper/2025-6-25.jpg",
    "bing-wallpaper/2025-6-26.jpg",
    "bing-wallpaper/2025-6-27.jpg",
    "bing-wallpaper/2025-6-28.jpg",
    "bing-wallpaper/2025-6-29.jpg",
    "bing-wallpaper/2025-6-2.jpg",
    "bing-wallpaper/2025-6-30.jpg",
    "bing-wallpaper/2025-6-3.jpg",
    "bing-wallpaper/2025-6-4.jpg",
    "bing-wallpaper/2025-6-5.jpg",
    "bing-wallpaper/2025-6-6.jpg",
    "bing-wallpaper/2025-6-7.jpg",
    "bing-wallpaper/2025-6-8.jpg",
    "bing-wallpaper/2025-6-9.jpg",
    "bing-wallpaper/2025-7-10.jpg",
    "bing-wallpaper/2025-7-11.jpg",
    "bing-wallpaper/2025-7-12.jpg",
    "bing-wallpaper/2025-7-13.jpg",
    "bing-wallpaper/2025-7-14.jpg",
    "bing-wallpaper/2025-7-15.jpg",
    "bing-wallpaper/2025-7-16.jpg",
    "bing-wallpaper/2025-7-17.jpg",
    "bing-wallpaper/2025-7-18.jpg",
    "bing-wallpaper/2025-7-19.jpg",
    "bing-wallpaper/2025-7-1.jpg",
    "bing-wallpaper/2025-7-20.jpg",
    "bing-wallpaper/2025-7-21.jpg",
    "bing-wallpaper/2025-7-22.jpg",
    "bing-wallpaper/2025-7-23.jpg",
    "bing-wallpaper/2025-7-24.jpg",
    "bing-wallpaper/2025-7-25.jpg",
    "bing-wallpaper/2025-7-26.jpg",
    "bing-wallpaper/2025-7-27.jpg",
    "bing-wallpaper/2025-7-28.jpg",
    "bing-wallpaper/2025-7-29.jpg",
    "bing-wallpaper/2025-7-2.jpg",
    "bing-wallpaper/2025-7-30.jpg",
    "bing-wallpaper/2025-7-31.jpg",
    "bing-wallpaper/2025-7-3.jpg",
    "bing-wallpaper/2025-7-4.jpg",
    "bing-wallpaper/2025-7-5.jpg",
    "bing-wallpaper/2025-7-6.jpg",
    "bing-wallpaper/2025-7-7.jpg",
    "bing-wallpaper/2025-7-8.jpg",
    "bing-wallpaper/2025-7-9.jpg",
    "bing-wallpaper/2025-8-10.jpg",
    "bing-wallpaper/2025-8-11.jpg",
    "bing-wallpaper/2025-8-12.jpg",
    "bing-wallpaper/2025-8-13.jpg",
    "bing-wallpaper/2025-8-14.jpg",
    "bing-wallpaper/2025-8-15.jpg",
    "bing-wallpaper/2025-8-16.jpg",
    "bing-wallpaper/2025-8-17.jpg",
    "bing-wallpaper/2025-8-18.jpg",
    "bing-wallpaper/2025-8-19.jpg",
    "bing-wallpaper/2025-8-1.jpg",
    "bing-wallpaper/2025-8-20.jpg",
    "bing-wallpaper/2025-8-21.jpg",
    "bing-wallpaper/2025-8-22.jpg",
    "bing-wallpaper/2025-8-23.jpg",
    "bing-wallpaper/2025-8-24.jpg",
    "bing-wallpaper/2025-8-25.jpg",
    "bing-wallpaper/2025-8-26.jpg",
    "bing-wallpaper/2025-8-27.jpg",
    "bing-wallpaper/2025-8-28.jpg",
    "bing-wallpaper/2025-8-29.jpg",
    "bing-wallpaper/2025-8-2.jpg",
    "bing-wallpaper/2025-8-30.jpg",
    "bing-wallpaper/2025-8-31.jpg",
    "bing-wallpaper/2025-8-3.jpg",
    "bing-wallpaper/2025-8-4.jpg",
    "bing-wallpaper/2025-8-5.jpg",
    "bing-wallpaper/2025-8-6.jpg",
    "bing-wallpaper/2025-8-7.jpg",
    "bing-wallpaper/2025-8-8.jpg",
    "bing-wallpaper/2025-8-9.jpg",
    "bing-wallpaper/2025-9-10.jpg",
    "bing-wallpaper/2025-9-11.jpg",
    "bing-wallpaper/2025-9-12.jpg",
    "bing-wallpaper/2025-9-13.jpg",
    "bing-wallpaper/2025-9-14.jpg",
    "bing-wallpaper/2025-9-15.jpg",
    "bing-wallpaper/2025-9-16.jpg",
    "bing-wallpaper/2025-9-17.jpg",
    "bing-wallpaper/2025-9-18.jpg",
    "bing-wallpaper/2025-9-19.jpg",
    "bing-wallpaper/2025-9-1.jpg",
    "bing-wallpaper/2025-9-20.jpg",
    "bing-wallpaper/2025-9-21.jpg",
    "bing-wallpaper/2025-9-22.jpg",
    "bing-wallpaper/2025-9-23.jpg",
    "bing-wallpaper/2025-9-24.jpg",
    "bing-wallpaper/2025-9-25.jpg",
    "bing-wallpaper/2025-9-26.jpg",
    "bing-wallpaper/2025-9-27.jpg",
    "bing-wallpaper/2025-9-28.jpg",
    "bing-wallpaper/2025-9-29.jpg",
    "bing-wallpaper/2025-9-2.jpg",
    "bing-wallpaper/2025-9-30.jpg",
    "bing-wallpaper/2025-9-3.jpg",
    "bing-wallpaper/2025-9-4.jpg",
    "bing-wallpaper/2025-9-5.jpg",
    "bing-wallpaper/2025-9-6.jpg",
    "bing-wallpaper/2025-9-7.jpg",
    "bing-wallpaper/2025-9-8.jpg",
    "bing-wallpaper/2025-9-9.jpg"
  ];

  let bg = getCookie('selectedBg');
  if (!bg || !images.includes(bg)) {{
    bg = images[Math.floor(Math.random() * images.length)];
  }}
  document.body.style.backgroundImage = `url('/${{bg}}')`;
</script>

</body>
</html>
'''
    
    OUTPUT_FILE.write_text(html_content, encoding='utf-8')
    print(f"✅ 成功生成博客首页: {OUTPUT_FILE}")
    print(f"📊 共加载 {len(posts)} 篇文章")

if __name__ == "__main__":
    main()
