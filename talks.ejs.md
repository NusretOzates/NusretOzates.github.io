```{=html}
<div class="list talks-listing-list">
<% for (const item of items) { %>
  <div class="talk-card" <%= metadataAttrs(item) %>>
    <img src="<%- item.image %>" class="talk-image listing-image" alt="<%- item.title %>" loading="lazy" />
    <div class="talk-content">
      <h3 class="listing-title"><%= item.title %></h3>
      <p>📍 <span class="listing-venue"><%= item.venue %></span> | 📅 <span class="listing-date"><%= item.date %></span></p>
      <p class="listing-description"><%= item.description %></p>
      <div class="talk-links">
        <a href="<%- item.href %>" class="listing-href" target="_blank" rel="noopener noreferrer">LinkedIn Post</a>
      </div>
    </div>
  </div>
<% } %>
</div>
```
