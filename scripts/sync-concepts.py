#!/usr/bin/env python3
"""
從 Oh_Hiu 筆記庫同步 publish: true 的卡片到 blog 的 concepts collection。
只同步 L1（canonical + abstract + 連結），不含全文。

用法：python3 scripts/sync-concepts.py
"""

import os
import re
import glob
import json
import unicodedata

VAULT_PATH = os.path.expanduser("~/Oh_Hiu 筆記庫/04_Permanent")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "content", "concepts")

# 主題分群（用於列表頁分類）
TOPIC_KEYWORDS = {
    "認知與心理": ["偏誤", "效應", "心理", "認知", "記憶", "注意力", "意志力", "迷你習慣"],
    "思維模型": ["思考", "決策", "原理", "機率", "剃刀", "反向", "囚徒", "博弈", "證偽", "貝葉斯", "黑暗森林", "思想實驗"],
    "學習方法": ["閱讀", "學習", "練習", "測驗", "遺忘", "筆記術", "零秒"],
    "知識管理": ["卡片盒", "筆記法", "知識", "Zettelkasten", "MOC", "連結", "Obsidian", "Inbox", "改寫", "飛輪", "圖譜"],
    "AI 時代": ["AI", "人工智慧"],
}


def slugify(text):
    """將 id 欄位轉為 URL-safe slug。"""
    # 去掉時間戳前綴 (YYYYMMDDHHMMSS-)
    text = re.sub(r"^\d{14}-", "", text)
    # 轉小寫，空格換 hyphen
    text = text.lower().strip().replace(" ", "-")
    # 只保留 ASCII 字母、數字、hyphen
    text = re.sub(r"[^a-z0-9-]", "", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def classify_topic(name, canonical):
    """根據標題和 canonical 判斷主題群。"""
    combined = name + " " + canonical
    for topic, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw in combined:
                return topic
    return "其他"


def extract_frontmatter(content):
    """用 regex 解析 frontmatter 欄位。"""
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return None, content
    fm_text = fm_match.group(1)
    body = content[fm_match.end():]
    return fm_text, body


def get_field(fm, field):
    """取得單行欄位值。"""
    m = re.search(rf"^{field}:\s*(.+)", fm, re.M)
    return m.group(1).strip().strip("'\"") if m else ""


def get_multiline_field(fm, field):
    """取得 >- 多行欄位值。"""
    m = re.search(rf"^{field}:\s*>-\s*\n((?:\s+.+\n?)+)", fm, re.M)
    if m:
        # 只取有縮排的行，遇到非縮排行（如 publish: true）停止
        lines = []
        for line in m.group(1).split("\n"):
            if line and not line[0].isspace():
                break
            lines.append(line.strip())
        return " ".join(l for l in lines if l)
    # fallback: single line
    return get_field(fm, field)


def get_list_field(fm, field):
    """取得 YAML list 欄位。"""
    m = re.search(rf"^{field}:\s*\n((?:\s+-\s+.+\n?)+)", fm, re.M)
    if m:
        return [line.strip().lstrip("- ").strip("'\"") for line in m.group(1).strip().split("\n")]
    # inline format: [a, b, c]
    m = re.search(rf"^{field}:\s*\[(.+)\]", fm, re.M)
    if m:
        return [item.strip().strip("'\"") for item in m.group(1).split(",")]
    return []


def extract_links(body):
    """從本文抽取 WikiLink 目標（去重、保留順序）。"""
    raw = re.findall(r"\[\[([^\]|]+)", body)
    seen = set()
    result = []
    for link in raw:
        if link not in seen:
            seen.add(link)
            result.append(link)
    return result


def build_link_lookup(all_cards):
    """建立 卡片名 → slug 的對照表。"""
    lookup = {}
    for card in all_cards:
        lookup[card["name"]] = card["slug"]
        for alias in card["aliases"]:
            lookup[alias] = card["slug"]
    return lookup


def main():
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    # 先收集所有 publish:true 卡片的資訊
    all_cards = []
    for filepath in glob.glob(os.path.join(VAULT_PATH, "*.md")):
        with open(filepath, "r") as f:
            content = f.read()

        fm_text, body = extract_frontmatter(content)
        if not fm_text:
            continue

        if not re.search(r"^publish:\s*true", fm_text, re.M):
            continue

        name = os.path.basename(filepath).replace(".md", "")
        card_id = get_field(fm_text, "id")
        slug = slugify(card_id) if card_id else slugify(name)
        if not slug:
            slug = re.sub(r"\s+", "-", name)

        canonical = get_field(fm_text, "canonical")
        abstract = get_multiline_field(fm_text, "abstract")
        tags = get_list_field(fm_text, "tags")
        aliases = get_list_field(fm_text, "aliases")
        type_tag = tags[0] if tags else "概念"
        topic = classify_topic(name, canonical)
        links = extract_links(body)

        all_cards.append({
            "name": name,
            "slug": slug,
            "canonical": canonical,
            "abstract": abstract,
            "type_tag": type_tag,
            "topic": topic,
            "tags": tags,
            "aliases": aliases,
            "links": links,
        })

    # 建立連結對照表
    link_lookup = build_link_lookup(all_cards)

    # 寫出每張概念卡的 markdown
    for card in all_cards:
        # 連結區：只保留庫內有對應 slug 的連結
        resolved_links = []
        for link_name in card["links"]:
            if link_name in link_lookup:
                resolved_links.append({
                    "name": link_name,
                    "slug": link_lookup[link_name],
                })

        # 建立輸出 frontmatter
        def esc(s):
            return s.replace('"', '\\"')

        out_lines = [
            "---",
            f'title: "{esc(card["name"])}"',
            f'canonical: "{esc(card["canonical"])}"',
        ]
        if card["abstract"]:
            out_lines.append(f'abstract: "{esc(card["abstract"])}"')
        out_lines.append(f'type: "{card["type_tag"]}"')
        out_lines.append(f'topic: "{card["topic"]}"')
        if card["aliases"]:
            out_lines.append("aliases:")
            for a in card["aliases"]:
                out_lines.append(f'  - "{a}"')
        if card["tags"][1:]:  # skip type tag
            out_lines.append("tags:")
            for t in card["tags"][1:]:
                out_lines.append(f'  - "{t}"')
        if resolved_links:
            out_lines.append("links:")
            for rl in resolved_links:
                out_lines.append(f'  - name: "{rl["name"]}"')
                out_lines.append(f'    slug: "{rl["slug"]}"')
        out_lines.append("---")

        out_content = "\n".join(out_lines) + "\n"
        out_path = os.path.join(OUTPUT_PATH, f"{card['slug']}.md")
        with open(out_path, "w") as f:
            f.write(out_content)

    print(f"Synced {len(all_cards)} concepts to {OUTPUT_PATH}")

    # 寫出一份 lookup JSON 給 remark plugin 用
    lookup_path = os.path.join(os.path.dirname(__file__), "..", "src", "data", "concept-lookup.json")
    os.makedirs(os.path.dirname(lookup_path), exist_ok=True)
    with open(lookup_path, "w") as f:
        json.dump(link_lookup, f, ensure_ascii=False, indent=2)
    print(f"Wrote concept lookup to {lookup_path}")


if __name__ == "__main__":
    main()
