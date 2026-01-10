import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

def crawl_wikipedia_events_zh():
    # 中文维基百科每日大事页面
    url = "https://zh.wikipedia.org/wiki/Portal:新闻动态"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }

    print(f"🌐 正在同步维基百科【中文】全球信号...")
    
    try:
        # 使用 verify=True 是默认的，如果遇到证书问题可以尝试 False
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        # 显式设置编码，防止中文乱码
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # 中文版维基百科的结构：通常在 id="mw-content-text" 下的列表项里
        events = []
        
        # 寻找最近的新闻列表内容
        content = soup.find('div', {'class': 'mw-parser-output'})
        if content:
            # 抓取最近的 li 标签内容（通常是最近的新闻条目）
            for li in content.find_all('li'):
                text = li.get_text().strip()
                # 过滤掉太短的或者导航类的干扰项
                if len(text) > 10 and not text.startswith('近期'):
                    events.append(text)

        if not events:
            print("⚠️ 未能提取到中文条目，请检查网络是否能访问 zh.wikipedia.org")
            return

        # 存储
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"wiki_zh_{timestamp}.txt"
        filepath = os.path.join("news_data", filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"来源: 中文维基百科 新闻动态\n")
            f.write(f"抓取时间: {datetime.now()}\n")
            f.write("-" * 30 + "\n")
            # 只取前 15 条最相关的，防止文件过大
            f.write("\n\n".join(events[:15]))

        print(f"✅ 中文信号已捕获: {filename}")

    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        print("💡 提示：如果报连接错误，可能是需要‘梯子’。如果不想折腾网络，我们可以换成‘百度新闻’。")

if __name__ == "__main__":
    if not os.path.exists("news_data"):
        os.makedirs("news_data")
    crawl_wikipedia_events_zh()