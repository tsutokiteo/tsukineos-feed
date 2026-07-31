#!/usr/bin/env python3
import os
import re
import datetime
import feedparser
from xml.etree import ElementTree as ET

# 配置
FEED_FILES = ["feed_0.xml", "feed_1.xml", "feed_2.xml", "feed_3.xml", "feed_4.xml"]
OUTPUT_FILE = "aggregated_feed.xml"
MAX_ITEMS = 30  # 最多保留多少条
TIME_WINDOW_HOURS = 168  # 7天内的动态
SITE_URL = "https://tsutokiteo.github.io/TsukineOS"
SITE_TITLE = "Tsukine OS 动态聚合"

# 生成 feed
def build_aggregated_feed():
    root = ET.Element("rss", version="2.0")
    channel = ET.SubElement(root, "channel")

    ET.SubElement(channel, "title").text = SITE_TITLE
    ET.SubElement(channel, "link").text = SITE_URL
    ET.SubElement(channel, "description").text = "来自各平台的最新动态"
    ET.SubElement(channel, "language").text = "zh-cn"

    items = []
    for feed_file in FEED_FILES:
        if not os.path.exists(feed_file):
            continue
        try:
            feed = feedparser.parse(feed_file)
            for entry in feed.entries[:10]:  # 每个源最多取10条
                # 提取时间
                pub_time = entry.get("published_parsed") or entry.get("updated_parsed")
                if not pub_time:
                    continue
                dt = datetime.datetime(*pub_time[:6])
                # 过滤超过时间窗口的条目
                if (datetime.datetime.utcnow() - dt).total_seconds() > TIME_WINDOW_HOURS * 3600:
                    continue
                items.append({
                    "title": entry.get("title", "无标题"),
                    "link": entry.get("link", ""),
                    "pub_date": entry.get("published", ""),
                    "summary": entry.get("summary", ""),
                    "author": entry.get("author", ""),
                })
        except Exception as e:
            print(f"Error parsing {feed_file}: {e}")

    # 按时间排序（最新的在前）
    items.sort(key=lambda x: x["pub_date"], reverse=True)

    # 限制总数
    items = items[:MAX_ITEMS]

    # 写入 RSS
    for item in items:
        entry = ET.SubElement(channel, "item")
        ET.SubElement(entry, "title").text = item["title"]
        ET.SubElement(entry, "link").text = item["link"]
        ET.SubElement(entry, "pubDate").text = item["pub_date"]
        if item["summary"]:
            ET.SubElement(entry, "description").text = item["summary"]
        if item["author"]:
            ET.SubElement(entry, "author").text = item["author"]

    tree = ET.ElementTree(root)
    tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    print(f"✅ 已生成 {OUTPUT_FILE}，共 {len(items)} 条动态")

if __name__ == "__main__":
    build_aggregated_feed()
