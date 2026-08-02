// @ts-check
import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";
import sitemap from "@astrojs/sitemap";
import rehypeRaw from "rehype-raw";

export default defineConfig({
  site: "https://nusretozates.github.io",
  outDir: "../docs",
  integrations: [mdx(), sitemap()],
  markdown: {
    shikiConfig: {
      theme: "github-dark",
    },
    rehypePlugins: [rehypeRaw],
  },
  build: {
    format: "directory",
  },
});
