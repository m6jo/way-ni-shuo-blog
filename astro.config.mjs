// @ts-check

import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import { defineConfig } from 'astro/config';

import skills from 'astro-skills';
import spotlight from '@spotlightjs/astro';
import compress from 'astro-compress';
import { remarkReadingTime } from './src/utils/remark-reading-time.mjs';

// https://astro.build/config
export default defineConfig({
    site: 'https://way-ni-shuo-blog.pages.dev',
    markdown: {
        remarkPlugins: [remarkReadingTime],
    },
    integrations: [mdx(), sitemap(), skills(), spotlight(), compress()],
});