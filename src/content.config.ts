import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';
import { skillsLoader } from 'astro-skills';

const blog = defineCollection({
	// Load Markdown and MDX files in the `src/content/blog/` directory.
	loader: glob({ base: './src/content/blog', pattern: '**/*.{md,mdx}' }),
	// Type-check frontmatter using a schema
	schema: ({ image }) =>
		z.object({
			title: z.string(),
			description: z.string(),
			// Transform string to Date object
			pubDate: z.coerce.date(),
			updatedDate: z.coerce.date().optional(),
			heroImage: image().optional(),
			category: z.string().default('認知升級'),
			tags: z.array(z.string()).default([]),
		}),
});

const concepts = defineCollection({
	loader: glob({ base: './src/content/concepts', pattern: '**/*.md' }),
	schema: z.object({
		title: z.string(),
		canonical: z.string(),
		abstract: z.string().optional(),
		type: z.string().default('概念'),
		topic: z.string().default('其他'),
		aliases: z.array(z.string()).default([]),
		tags: z.array(z.string()).default([]),
		links: z.array(z.object({
			name: z.string(),
			slug: z.string(),
		})).default([]),
	}),
});

const skills = defineCollection({
	loader: skillsLoader({ base: './skills' }),
});

export const collections = { blog, concepts, skills };
