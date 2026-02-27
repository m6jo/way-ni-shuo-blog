# CLAUDE.md

## Project Overview

**Way 你說** — m6jo 的個人 blog + 概念庫，Astro 5 靜態網站，部署到 Cloudflare Pages。

- Site: `https://way-ni-shuo-blog.pages.dev`
- Language: zh-TW Traditional Chinese（技術詞保留英文）
- Astro 5 + MDX + Pagefind（全文搜尋）+ Giscus（留言）

## Tech Stack

| Layer | Tool |
|-------|------|
| Framework | Astro 5 (SSG, `astro build`) |
| Content | `src/content/blog/` (MDX) + `src/content/concepts/` (MD) |
| Search | Pagefind (build 後 index) |
| Styling | Scoped `<style>` in `.astro`，全域 `src/styles/global.css` |
| Fonts | Atkinson (英文), Noto Serif TC (display), Noto Sans TC (UI) |
| Deploy | GitHub Actions → Cloudflare Pages (`main` branch push) |
| Comments | Giscus (GitHub Discussions) |
| Graph | D3.js (d3-force, d3-selection, d3-zoom, d3-drag) for concept graph |

## Directory Structure

```
src/
  components/     Astro 元件（BaseHead, Header, Footer, GraphView...）
  content/
    blog/         Blog 文章（MDX，frontmatter schema in content.config.ts）
    concepts/     概念卡（MD，從筆記庫 sync 過來）
  data/           靜態 JSON（concept-lookup.json）
  layouts/        BlogPost.astro
  pages/          路由頁面
    blog/         文章列表 + [slug]
    concepts/     概念庫列表 + [...slug]
    category/     分類頁
    tag/           標籤頁
  styles/         global.css
scripts/          同步腳本（sync-concepts.py）
public/           靜態資源（fonts, favicon）
```

## CSS Design System

### CSS Variables (defined in `global.css`)

```css
--accent: #d4572a          /* 主色（light） */
--accent-dark: #e8764a     /* 主色（dark） */
--font-display: "Noto Serif TC", serif    /* 標題、策展感 */
--font-ui: "Noto Sans TC", sans-serif     /* meta、正文、UI */
--black / --gray / --gray-light / --gray-dark / --bg  /* RGB triplets */
```

### Dark Mode

`[data-theme="dark"]` on `<html>` — CSS 變數自動切換，不需 JS re-render。
Theme detection inline script in `BaseHead.astro` prevents FOUC.

### Style Conventions

- Scoped `<style>` in each `.astro` file（不用 CSS modules）
- `border-radius: 2px`（報紙格風格，不圓潤）
- Type badge: `border: 1.5px solid var(--accent)`, transparent background
- Section 標題: `border-bottom: 3px solid rgb(var(--black))`
- Hover: 背景微變 + 文字變 accent，不動 border/shadow

## Content Schema

### Blog (`src/content/blog/`)

```yaml
title: string
description: string
pubDate: date
updatedDate?: date
heroImage?: image
category: string (default: '認知升級')
tags: string[]
```

### Concepts (`src/content/concepts/`)

```yaml
title: string
canonical: string           # 一句話定義
abstract?: string
type: string (default: '概念')
topic: string (default: '其他')
aliases: string[]
tags: string[]
links: { name: string, slug: string }[]
```

概念卡由 `scripts/sync-concepts.py` 從筆記庫同步，不手動編輯。

## Commands

```bash
npm run dev        # 本地開發 (localhost:4321)
npm run build      # astro build + pagefind index
npm run preview    # 預覽 build 結果
```

## Deployment

Push to `main` → GitHub Actions → `npm ci && npm run build` → Wrangler deploy to Cloudflare Pages。
不要直接 push 未測試的 code 到 main。

## User Preferences

- Address user as **m6jo**
- 繁體中文溝通
- 中英混排加空格（中文 English 中文）
- 全形標點（中文語境）、半形標點（純英文語句）
- 收到明確指令 → 直接執行，不做計畫分析
- 不確定時：做一個最小動作再問，不長篇分析

## Important Notes

- 概念庫功能目前是 WIP prototype，視覺和互動仍在迭代
- Blog 文章頁和概念頁的設計語言不同，之後再統一
- `sync-concepts.py` 從筆記庫拉資料，改概念內容要改源頭不是改這邊的 MD
