import getReadingTime from 'remark-reading-time';
import { toString } from 'mdast-util-to-string';

export function remarkReadingTime() {
  return function (tree, { data }) {
    const textOnPage = toString(tree);
    // 中文：約 500 字/分鐘，英文：約 200 words/分鐘
    const chineseChars = (textOnPage.match(/[\u4e00-\u9fff]/g) || []).length;
    const englishWords = textOnPage.replace(/[\u4e00-\u9fff]/g, '').split(/\s+/).filter(Boolean).length;
    const minutes = Math.ceil(chineseChars / 500 + englishWords / 200);
    data.astro.frontmatter.readingTime = `${minutes} 分鐘`;
  };
}
