```{=html}
<div class="video-playlist-list">
<% for (const item of items) { %>
  <article class="video-playlist-card" id="playlist-<%- item.playlist_id %>" <%= metadataAttrs(item) %>>
    <div class="video-embed">
      <iframe
        src="https://www.youtube.com/embed/videoseries?list=<%- item.playlist_id %>"
        title="<%- item.title %>"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        referrerpolicy="strict-origin-when-cross-origin"
        allowfullscreen
        loading="lazy"
      ></iframe>
    </div>
    <div class="video-playlist-content">
      <h3 class="listing-title"><%= item.title %></h3>
      <p class="listing-description"><%= item.description %></p>
      <div class="video-playlist-links">
        <a href="<%- item.href %>" target="_blank" rel="noopener noreferrer">Open playlist on YouTube</a>
      </div>
    </div>
  </article>
<% } %>
</div>
```
