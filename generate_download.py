import os
from pathlib import Path
import time

# ===== 配置区 =====
DOWNLOADS_ROOT = Path("downloads")     # 必须是网站根目录下的 downloads 文件夹
SITE_TITLE = "韩邦泽的小站"

ALLOWED_EXTENSIONS = {
    '.zip', '.rar', '.7z', '.tar', '.gz',
    '.pdf', '.doc', '.docx', '.txt', '.md',
    '.exe', '.msi', '.dmg',
    '.apk', '.ipa',
    '.jar', '.py', '.sh', '.bat',
    '.mp4', '.avi', '.mkv', '.mov',
    '.jpg', '.jpeg', '.png', '.gif'
}
# ==================

def get_file_size(filepath):
    try:
        size = os.path.getsize(filepath)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except OSError:
        return "N/A"

def format_time(timestamp):
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp))

def get_icon(is_dir, filename=""):
    if is_dir:
        return "fa-folder"
    ext = filename.lower()
    if any(ext.endswith(e) for e in ['.zip', '.rar', '.7z']):
        return "fa-file-archive"
    elif ext.endswith('.pdf'):
        return "fa-file-pdf"
    elif any(ext.endswith(e) for e in ['.doc', '.docx']):
        return "fa-file-word"
    elif any(ext.endswith(e) for e in ['.jpg', '.jpeg', '.png', '.gif']):
        return "fa-file-image"
    elif any(ext.endswith(e) for e in ['.mp4', '.avi', '.mkv']):
        return "fa-file-video"
    elif ext.endswith('.txt') or ext.endswith('.md'):
        return "fa-file-alt"
    elif ext.endswith('.exe') or ext.endswith('.msi'):
        return "fa-cogs"
    else:
        return "fa-file"

def generate_index_html(current_dir: Path):
    """为 current_dir 生成 index.html，使用相对路径"""
    items = []

    try:
        for item in current_dir.iterdir():
            name = item.name
            if item.is_dir():
                # 子目录：链接到 "subdir/"（浏览器会加载 subdir/index.html）
                url = name + "/"
                meta = ""
                is_dir = True
            else:
                # 文件：仅允许特定扩展名
                if not any(name.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS):
                    continue
                url = name
                meta = f"{get_file_size(item)} • {format_time(item.stat().st_mtime)}"
                is_dir = False

            icon = get_icon(is_dir, name)
            items.append({
                'name': name,
                'url': url,
                'is_dir': is_dir,
                'icon': icon,
                'meta': meta
            })
    except PermissionError:
        pass

    # 排序：目录在前，文件在后
    items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

    # 面包屑：从 downloads/ 开始
    try:
        rel_path = current_dir.relative_to(DOWNLOADS_ROOT)
        path_parts = ["downloads"] + list(rel_path.parts)
    except ValueError:
        path_parts = ["downloads"]

    breadcrumb_items = ['<a href="/">首页</a>']
    for i, part in enumerate(path_parts):
        if i == 0:
            breadcrumb_items.append('<span>downloads</span>')
        else:
            # 构造路径：downloads/part1/part2/
            href = "/".join(path_parts[:i+1]) + "/"
            breadcrumb_items.append(f'<a href="/{href}">{part}</a>')
    breadcrumb = " / ".join(breadcrumb_items)

    # HTML 模板（使用相对路径 + 绝对路径导航）
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <link rel="icon" type="image/png" href="/favicon-96x96.png" sizes="96x96" />
  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="shortcut icon" href="/favicon.ico" />
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
  <meta name="apple-mobile-web-app-title" content="韩邦泽的小站" />
  <link rel="manifest" href="/site.webmanifest" />
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{"/".join(path_parts)} - {SITE_TITLE}</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  <style>
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: "Microsoft YaHei", sans-serif;
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
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 2rem;
      z-index: 1;
    }}
    .breadcrumb {{
      margin-bottom: 1.5rem;
      font-size: 1rem;
      color: #bbb;
    }}
    .breadcrumb a {{
      color: #3498db;
      text-decoration: none;
    }}
    .breadcrumb a:hover {{
      text-decoration: underline;
    }}
    .folder-section {{
      max-width: 900px;
      width: 100%;
      background-color: rgba(0, 0, 0, 0.7);
      padding: 2rem;
      border-radius: 12px;
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5);
    }}
    h1 {{
      font-size: 2rem;
      margin-bottom: 1.5rem;
      text-align: center;
    }}
    .item {{
      display: flex;
      align-items: flex-start;
      padding: 0.8rem 0;
      border-bottom: 1px solid rgba(255,255,255,0.1);
    }}
    .item:last-child {{
      border-bottom: none;
    }}
    .item-icon {{
      width: 36px;
      text-align: center;
      font-size: 1.3rem;
      margin-right: 1rem;
      margin-top: 3px;
    }}
    .item-info {{
      flex: 1;
    }}
    .item-name {{
      font-size: 1.15rem;
      margin-bottom: 0.2rem;
    }}
    .item-link {{
      color: #3498db;
      text-decoration: none;
    }}
    .item-link:hover {{
      text-decoration: underline;
    }}
    .item-meta {{
      font-size: 0.95rem;
      color: #bbb;
    }}
    .empty {{
      text-align: center;
      color: #aaa;
      padding: 2rem 0;
    }}
  </style>
</head>
<body>

<header>
  <div class="site-title">{SITE_TITLE}</div>
  <nav>
    <ul>
      <li><a href="/">首页</a></li>
      <li><a href="/about.html">关于我</a></li>
      <li><a href="/downloads/">下载</a></li>
      <li><a href="/apps.html">应用</a></li>
      <li><a href="/blog.html">博客</a></li>
    </ul>
  </nav>
</header>

<main>
  <section class="folder-section">
    <div class="breadcrumb">{breadcrumb}</div>
    <h1>{" / ".join(path_parts)}</h1>
'''

    if not items:
        html += '<p class="empty">此目录为空</p>'
    else:
        for item in items:
            color = "#f39c12" if item['is_dir'] else "#3498db"
            html += f'''
    <div class="item">
      <div class="item-icon">
        <i class="fas {item["icon"]}" style="color:{color};"></i>
      </div>
      <div class="item-info">
        <div class="item-name">
          <a class="item-link" href="{item["url"]}">{item["name"]}</a>
        </div>
        <div class="item-meta">{item["meta"]}</div>
      </div>
    </div>
'''

    html += '''
  </section>
</main>

<script>
  function getCookie(name) {
    return document.cookie.split('; ').reduce((r, v) => {
      const parts = v.split('=');
      return parts[0] === name ? decodeURIComponent(parts[1]) : r;
    }, '');
  }

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
  if (!bg || !images.includes(bg)) {
    bg = images[Math.floor(Math.random() * images.length)];
  }
  document.body.style.backgroundImage = `url('/${bg}')`;
</script>

</body>
</html>
'''
    index_file = current_dir / "index.html"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ 生成: {index_file}")

def main():
    if not DOWNLOADS_ROOT.exists():
        print(f"❌ 目录 {DOWNLOADS_ROOT} 不存在！")
        return

    # 递归遍历 downloads 下所有目录（包括自身）
    for dir_path in DOWNLOADS_ROOT.rglob(''):
        if dir_path.is_dir():
            generate_index_html(dir_path)

    print("\n🎉 所有 index.html 已生成完毕！")

if __name__ == "__main__":
    main()
