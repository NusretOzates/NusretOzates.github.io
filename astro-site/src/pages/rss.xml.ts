import rss from "@astrojs/rss";
import { getCollection } from "astro:content";
import type { APIRoute } from "astro";

export const GET: APIRoute = async (context) => {
  const posts = (await getCollection("posts")).sort(
    (a, b) => b.data.date.valueOf() - a.data.date.valueOf(),
  );
  return rss({
    title: "Nusret Özateş — Blog",
    description: "ML engineering, MLOps, and lessons learned.",
    site: context.site ?? "https://nusretozates.github.io",
    items: posts.map((post) => ({
      title: post.data.title,
      pubDate: post.data.date,
      link: `/posts/${post.id}/`,
    })),
  });
};
