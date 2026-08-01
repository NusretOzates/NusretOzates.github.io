```{=html}
<div class="videos-preview-grid">
<% for (const item of items) { %>
  <a class="video-preview-card" href="videos.html#playlist-<%- item.playlist_id %>">
    <img src="<%- item.thumbnail %>" class="video-preview-thumb" alt="<%- item.title %>" loading="lazy" />
    <span class="video-preview-title"><%= item.title %></span>
  </a>
<% } %>
</div>
```
