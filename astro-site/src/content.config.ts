import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const categoryEnum = z.enum(["academy", "general", "gnn", "llm", "ml", "mlops", "software"]);

const posts = defineCollection({
  loader: glob({ base: "./src/content/posts", pattern: "**/*.md" }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    date: z.coerce.date(),
    categories: z.array(categoryEnum).default(["ml"]),
    image: z.string().optional(),
    mediumUrl: z.string().url().optional(),
  }),
});

const notes = defineCollection({
  loader: glob({ base: "./src/content/notes", pattern: "**/*.md" }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    date: z.coerce.date(),
    categories: z.array(categoryEnum).default(["ml"]),
  }),
});

const talks = defineCollection({
  loader: glob({ base: "./src/content/talks", pattern: "**/*.{yaml,yml,json}" }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    venue: z.string(),
    description: z.string(),
    image: z.string(),
    href: z.string().url(),
  }),
});

const videos = defineCollection({
  loader: glob({ base: "./src/content/videos", pattern: "**/*.{yaml,yml,json}" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    playlistId: z.string(),
    href: z.string().url(),
    thumbnail: z.string().url(),
  }),
});

const publications = defineCollection({
  loader: glob({ base: "./src/content/publications", pattern: "**/*.{yaml,yml,json}" }),
  schema: z.object({
    title: z.string(),
    authors: z.string(),
    venue: z.string(),
    links: z.array(
      z.object({
        label: z.string(),
        href: z.string().url(),
      }),
    ),
  }),
});

export const collections = { posts, notes, talks, videos, publications };
