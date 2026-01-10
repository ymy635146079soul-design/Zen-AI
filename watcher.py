import time
import os
import csv
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from engine import get_core_data

class ZenHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory: return
        
        filename = os.path.basename(event.src_path)
        if filename.startswith("wiki_"):
            print(f"\n[感知] 检测到世界信号: {filename}")
            time.sleep(1.5) # 等待 Crawler 彻底写完并释放文件
            
            try:
                # 1. 计算干支坐标
                now = datetime.now()
                gz = get_core_data(now.year, now.month, now.day, now.hour, now.minute)
                gz_str = f"{gz['year']} {gz['month']} {gz['day']} {gz['hour']}"
                
                # 2. 【核心逻辑】：提取新闻，跳过前3行页眉，过滤空格
                news_list = []
                with open(event.src_path, 'r', encoding='utf-8') as f:
                    # 读取所有行，[3:] 表示从第4行开始看（索引从0开始）
                    all_lines = f.readlines()[3:] 
                    for line in all_lines:
                        clean_line = line.strip()
                        # 只有长度大于 5 的才被视为有效新闻，这会自动过滤掉空白行
                        if len(clean_line) > 5:
                            news_list.append(clean_line)

                # 判定抓取结果
                if news_list:
                    primary_news = news_list[0] # 取第一条存入 CSV
                    full_text_for_ai = "\n".join(news_list) # 全部新闻给 AI
                else:
                    primary_news = "未发现有效条目"
                    full_text_for_ai = "未发现有效条目"

                # 3. 方案 A：归档到 CSV (记忆)
                self.save_to_history(now, gz_str, primary_news)
                
                # 4. 方案 B：生成 AI 提示词 (嘴巴)
                self.generate_ai_prompt(gz, full_text_for_ai)
                
            except Exception as e:
                print(f"❌ 处理过程中出错: {e}")

    def save_to_history(self, dt, gz_str, summary):
        file_exists = os.path.isfile('ZenAI_History.csv')
        with open('ZenAI_History.csv', 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['实际时间', '干支时空坐标', '首条新闻摘要'])
            writer.writerow([dt.strftime("%Y-%m-%d %H:%M"), gz_str, summary])
        print(f"📝 方案 A：已归档至 CSV (首条: {summary[:20]}...)")

    def generate_ai_prompt(self, gz, full_content):
        prompt = f"""你现在是 Zen-AI 时空解析助手。
当前时空坐标：{gz['year']}年 {gz['month']}月 {gz['day']}日 {gz['hour']}时
捕获世界信号详情：
{full_content}

请基于阴阳五行逻辑，解读这些信号在此时空坐标下的深层含义，并给出预测倾向。"""
        with open('Latest_AI_Prompt.txt', 'w', encoding='utf-8') as f:
            f.write(prompt)
        print(f"🤖 方案 B：AI 指令已就绪 (Latest_AI_Prompt.txt)")

if __name__ == "__main__":
    path = os.path.abspath("./news_data")
    if not os.path.exists(path): os.makedirs(path)
    
    event_handler = ZenHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    
    print(f"🚀 Zen-AI 档案员模式启动。")
    print(f"📍 正在监听: {path}")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()