// @ts-check
import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";
import sitemap from "@astrojs/sitemap";
import expressiveCode from "astro-expressive-code";
import rehypeRaw from "rehype-raw";

export default defineConfig({
  site: "https://nusretozates.github.io",
  outDir: "../docs",
  integrations: [
    expressiveCode({
      themes: ["github-light", "github-dark"],
      useDarkModeMediaQuery: false,
      themeCssSelector: (theme) =>
        theme.type === "dark"
          ? '[data-theme="dark"]'
          : ':root:not([data-theme="dark"])',
      styleOverrides: {
        borderRadius: "0.5rem",
        borderWidth: "1px",
        codeFontFamily:
          '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
        codeFontSize: "0.8125rem",
        codeLineHeight: "1.55",
        codePaddingBlock: "0.9rem",
        codePaddingInline: "1rem",
        uiFontFamily:
          '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
        uiFontSize: "0.75rem",
        frames: {
          frameBoxShadowCssValue: "none",
          editorTabBarBackground: "transparent",
        },
      },
    }),
    mdx(),
    sitemap(),
  ],
  markdown: {
    rehypePlugins: [rehypeRaw],
  },
  build: {
    format: "directory",
  },
});
