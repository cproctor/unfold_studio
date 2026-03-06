 (function () {
  function qs(sel) { return document.querySelector(sel); }
  function qsa(sel) { return Array.from(document.querySelectorAll(sel)); }

  function showInlineAlert(text) {
    const msg = qs("[data-inline-alert]");
    if (msg) {
      msg.textContent = text;
      msg.style.display = "block";
      msg.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }
    alert(text);
  }

  // ---- Browse Stories: client-side search filtering ----
  function initBrowseSearch() {
    const list = qs("#storiesList");
    if (!list) return;

    const params = new URLSearchParams(window.location.search);
    const raw = params.get("query");
    const q = (raw || "").trim();

    // Keep query in the nav search input
    const navInput = qs("input[name='query']");
    if (navInput) navInput.value = q;

    // If empty query submitted (?query=)
    if (params.has("query") && q.length === 0) {
      showInlineAlert("Please enter a valid search query");
      return;
    }

    if (!q) return;

    const heading = qs("#storiesHeading");
    if (heading) heading.textContent = "Search results";

    const wrap = qs("#storiesListWrap");
    const noStories = qs("#noStories");
    const items = qsa("#storiesList .story-item");
    const qLower = q.toLowerCase();

    let shown = 0;
    items.forEach(li => {
      const title = (li.dataset.title || "").toLowerCase();
      const author = (li.dataset.author || "").toLowerCase();
      const match = title.includes(qLower) || author.includes(qLower);
      li.style.display = match ? "" : "none";
      if (match) shown += 1;
    });

    if (shown === 0) {
      if (wrap) wrap.style.display = "none";
      if (noStories) noStories.style.display = "block";
    } else {
      if (wrap) wrap.style.display = "";
      if (noStories) noStories.style.display = "none";
    }
  }

  // ---- New Story form → redirect to public editor with story_id ----
  function initCreateStory() {
    const form = qs("#createStoryForm");
    if (!form) return;

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      const title = (qs("#storyTitle")?.value || "Untitled Public Story").trim();
      const desc = (qs("#storyDesc")?.value || "").trim();

      // fake story id
      const storyId = "pub-" + Math.floor(Math.random() * 100000);

      const url = new URL("editor_public.html", window.location.href);
      url.searchParams.set("story_id", storyId);
      url.searchParams.set("title", title);
      url.searchParams.set("desc", desc);
      window.location.href = url.toString();
    });
  }

  // ---- Public editor: sign up handoff ----
  function initEditorPublic() {
    const label = qs("#publicStoryLabel");
    if (!label) return;

    const params = new URLSearchParams(window.location.search);
    const storyId = params.get("story_id") || "pub-demo";
    const title = params.get("title") || "Public Story";
    const desc = params.get("desc") || "";

    qs("#storyTitleText").textContent = title;
    qs("#storyIdText").textContent = storyId;
    qs("#storyDescText").textContent = desc;

    const authorInput = qs("#authorInput");
    const authorDisplay = qs("#authorDisplay");
    if (authorInput && authorDisplay) {
      let savedAuthor = "";
      try { savedAuthor = localStorage.getItem("unfold_author_" + storyId) || ""; } catch (_) {}
      authorInput.value = savedAuthor;
      authorDisplay.textContent = savedAuthor || "—";
    }

    // Update Sign up link to pass story_id
    const signupLink = qs("#signupClaimLink");
    if (signupLink) {
      signupLink.href = `signup.html?story_id=${encodeURIComponent(storyId)}`;
    }

    // Fork button → create another public story
    const forkBtn = qs("#forkPublicBtn");
    if (forkBtn) {
      forkBtn.addEventListener("click", function () {
        const newId = "pub-" + Math.floor(Math.random() * 100000);
        const url = new URL("editor_public.html", window.location.href);
        url.searchParams.set("story_id", newId);
        url.searchParams.set("title", title + " (fork)");
        url.searchParams.set("desc", desc);
        window.location.href = url.toString();
      });
    }
  }

  // ---- Signup: simulate claiming story and redirect to owned editor ----
  function initSignupClaim() {
    const claimBtn = qs("#completeSignupBtn");
    if (!claimBtn) return;

    const params = new URLSearchParams(window.location.search);
    const storyId = params.get("story_id");

    // show the story id on the signup page
    const claimText = qs("#claimStoryText");
    if (claimText && storyId) {
      claimText.textContent = `After signup, you will own story: ${storyId}`;
    }

    claimBtn.addEventListener("click", function () {
      if (!storyId) {
        window.location.href = "browse_stories.html";
        return;
      }
      window.location.href = `editor_owned.html?story_id=${encodeURIComponent(storyId)}`;
    });
  }

  // ---- Code panel toggle: Hide code / Show code ----
  function initCodeToggle() {
    const split = qs("#editorSplit");
    const btn = qs("#codeToggleBtn");
    if (!split || !btn) return;

    btn.addEventListener("click", function () {
      const hidden = split.classList.contains("codeHidden");
      if (hidden) {
        split.classList.remove("codeHidden");
        btn.textContent = "Hide code";
      } else {
        split.classList.add("codeHidden");
        btn.textContent = "Show code";
      }
    });
  }

  // ---- Demo actions: simple Save/Rename feedback ----
  function initDemoStoryActions() {
    const saveButtons = qsa("[data-demo-save]");
    const renameButtons = qsa("[data-demo-rename]");

    saveButtons.forEach(btn => {
      btn.addEventListener("click", function () {
        const authorInput = qs("#authorInput");
        const authorDisplay = qs("#authorDisplay");
        const storyIdText = qs("#storyIdText");
        const storyId = storyIdText?.textContent;

        if (authorInput && authorDisplay) {
          const name = (authorInput.value || "").trim();
          authorDisplay.textContent = name || "—";
          if (storyId && name) {
            try { localStorage.setItem("unfold_author_" + storyId, name); } catch (_) {}
          }
        }
        showInlineAlert("Saved. (Demo only, changes are not persisted.)");
      });
    });

    renameButtons.forEach(btn => {
      btn.addEventListener("click", function () {
        showInlineAlert("Rename is a visual demo only in this prototype.");
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initBrowseSearch();
    initCreateStory();
    initEditorPublic();
    initSignupClaim();
    initCodeToggle();
    initDemoStoryActions();
  });
})(); 