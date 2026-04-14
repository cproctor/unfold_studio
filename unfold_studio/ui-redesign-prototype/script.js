/**
 * Unfold Studio UI prototype — browse sort + search + genre filters, books shelves, editor preview.
 * Story/book cards: hover reveals title + description overlay.
 * Works offline (file://). Not connected to the Django backend.
 */
(function () {
  var lastSearchQuery = "";
  var PROTO_DRAFT_KEY = "unfoldProtoStoryDraft";
  var PROTO_AUTH_KEY = "unfoldProtoAuth";
  var PROTO_INSTRUCTOR_EMAIL = "dr.chris.proctor@unfoldstudio.example";
  var DEFAULT_INK = "=== start ===\n\nHello world!\n\n-> END\n";

  var PROTO_STORIES = {
    lighthouse_keeper: {
      title: "The Last Lighthouse Keeper",
      by: "Maya Chen",
      love: 128,
      ink:
        "=== start ===\n" +
        "The lantern swings. Rain hammers the glass.\n\n" +
        "* [Answer the radio] -> radio\n" +
        "* [Climb to the lamp room] -> lamp\n" +
        "* [Read the logbook] -> logbook\n\n" +
        "=== radio ===\n" +
        "The voice on the other end uses your first name wrong on purpose.\n\n" +
        "=== lamp ===\n" +
        "Each step groans. Above you, the lens catches storm-light like a trapped moon.\n\n" +
        "=== logbook ===\n" +
        "The last line reads: Don’t answer if it uses your mother’s voice.\n\n" +
        "-> END\n",
      playerHtml:
        "<p>The lantern swings. Rain hammers the glass. Somewhere below, the town pretends it never needed the light.</p>" +
        "<p><em>You stand in the keeper’s chamber. A radio crackles with a voice you don’t recognize.</em></p>" +
        "<p>" +
        '<a class="choice" href="#">▸ Answer the radio</a><br />' +
        '<a class="choice" href="#">▸ Climb to the lamp room</a><br />' +
        '<a class="choice" href="#">▸ Read the logbook marked “Do not open after midnight”</a>' +
        "</p>",
    },
    ciphers_margins: {
      title: "Ciphers in the Margins",
      by: "N. Okonkwo",
      love: 512,
      ink:
        "=== start ===\n" +
        "The note is printed in the margin like it belongs there.\n" +
        "But you don’t remember writing it.\n\n" +
        "* [Check the library stamp] -> stamp\n" +
        "* [Read the footnote aloud] -> footnote\n" +
        "* [Close the book] -> close\n\n" +
        "=== stamp ===\n" +
        "The date is tomorrow.\n\n" +
        "=== footnote ===\n" +
        "The room gets quieter, as if listening.\n\n" +
        "=== close ===\n" +
        "The margin keeps talking anyway.\n\n" +
        "-> END\n",
      playerHtml:
        "<p>The note is printed in the margin like it belongs there. But you don’t remember writing it.</p>" +
        "<p><em>The librarian’s stamp is dated tomorrow.</em></p>" +
        "<p>" +
        '<a class="choice" href="#">▸ Check the library stamp</a><br />' +
        '<a class="choice" href="#">▸ Read the footnote aloud</a><br />' +
        '<a class="choice" href="#">▸ Close the book</a>' +
        "</p>",
    },
    greenhouse_shift: {
      title: "Greenhouse Shift",
      by: "EcoLit Club",
      love: 361,
      ink:
        "=== start ===\n" +
        "The greenhouse door sticks in the heat.\n" +
        "Inside, the seedlings lean toward the glass.\n\n" +
        "* [Measure temperature] -> temp\n" +
        "* [Measure humidity] -> humidity\n" +
        "* [Check the soil] -> soil\n\n" +
        "=== temp ===\n" +
        "The thermometer climbs fast.\n\n" +
        "=== humidity ===\n" +
        "The air clings to your sleeves.\n\n" +
        "=== soil ===\n" +
        "Dry at the top, damp underneath.\n\n" +
        "-> END\n",
      playerHtml:
        "<p>The greenhouse door sticks in the heat. Inside, the seedlings are leaning toward the glass.</p>" +
        "<p><em>You can change one variable today.</em></p>" +
        "<p>" +
        '<a class="choice" href="#">▸ Measure temperature</a><br />' +
        '<a class="choice" href="#">▸ Measure humidity</a><br />' +
        '<a class="choice" href="#">▸ Check the soil</a>' +
        "</p>",
    },
    quiet_room: {
      title: "The Quiet Room",
      by: "Dr. Patel",
      love: 290,
      ink:
        "=== start ===\n" +
        "The hallway is loud in the way a storm is loud.\n" +
        "You find the quiet room sign half-covered by a poster.\n\n" +
        "* [Step inside] -> inside\n" +
        "* [Find a friend] -> friend\n" +
        "* [Go back to class] -> class\n\n" +
        "=== inside ===\n" +
        "The lights are dim and the chair is empty.\n\n" +
        "=== friend ===\n" +
        "Your phone buzzes: “I’m here.”\n\n" +
        "=== class ===\n" +
        "You count breaths until the bell.\n\n" +
        "-> END\n",
      playerHtml:
        "<p>The hallway is loud in the way a storm is loud. You find the quiet room sign half-covered by a poster.</p>" +
        "<p><em>Inside, the lights are dim and the chair is empty.</em></p>" +
        "<p>" +
        '<a class="choice" href="#">▸ Step inside</a><br />' +
        '<a class="choice" href="#">▸ Find a friend</a><br />' +
        '<a class="choice" href="#">▸ Go back to class</a>' +
        "</p>",
    },
    addison_detour: {
      title: "Detour Through Addison Street",
      by: "riverdelta",
      love: 0,
      ink:
        "=== start ===\n" +
        "The bus arrives without a route number.\n" +
        "The map in your pocket redraws itself.\n\n" +
        "* [Sit near the front] -> front\n" +
        "* [Sit in the back] -> back\n" +
        "* [Stay at the stop] -> stop\n\n" +
        "=== front ===\n" +
        "The driver nods like they know you.\n\n" +
        "=== back ===\n" +
        "Someone whispers your old nickname.\n\n" +
        "=== stop ===\n" +
        "The street sign changes anyway.\n\n" +
        "-> END\n",
      playerHtml:
        "<p>The bus arrives without a route number. The map in your pocket redraws itself.</p>" +
        "<p><em>Every stop name feels almost familiar.</em></p>" +
        "<p>" +
        '<a class="choice" href="#">▸ Sit near the front</a><br />' +
        '<a class="choice" href="#">▸ Sit in the back</a><br />' +
        '<a class="choice" href="#">▸ Stay at the stop</a>' +
        "</p>",
    },
    peer_review_panic: {
      title: "Peer Review Panic (Ink)",
      by: "cwilk",
      love: 0,
      ink:
        "=== start ===\n" +
        "Your draft is due in an hour.\n" +
        "The comments are… enthusiastic.\n\n" +
        "* [Revise immediately] -> revise\n" +
        "* [Defend your choices] -> defend\n" +
        "* [Start over] -> restart\n\n" +
        "=== revise ===\n" +
        "You delete one sentence. Three appear.\n\n" +
        "=== defend ===\n" +
        "You write “intentional” in the margin.\n\n" +
        "=== restart ===\n" +
        "Blank page. Deep breath.\n\n" +
        "-> END\n",
      playerHtml:
        "<p>Your draft is due in an hour. The comments are… enthusiastic.</p>" +
        "<p><em>Which sentence do you touch first?</em></p>" +
        "<p>" +
        '<a class="choice" href="#">▸ Revise immediately</a><br />' +
        '<a class="choice" href="#">▸ Defend your choices</a><br />' +
        '<a class="choice" href="#">▸ Start over</a>' +
        "</p>",
    },
    archive_room_7b: {
      title: "Archive: Room 7B",
      by: "archive_kid",
      love: 0,
      ink:
        "=== start ===\n" +
        "The camera battery says 12%.\n" +
        "The hallway hums like a freezer.\n\n" +
        "* [Open the door] -> door\n" +
        "* [Check your inventory] -> inv\n" +
        "* [Turn back] -> back\n\n" +
        "=== door ===\n" +
        "Room 7B is on the map, but not on the door.\n\n" +
        "=== inv ===\n" +
        "Tape. Flashlight. A key you don’t remember taking.\n\n" +
        "=== back ===\n" +
        "The exit sign flickers and spells something else.\n\n" +
        "-> END\n",
      playerHtml:
        "<p>The camera battery says 12%. The hallway hums like a freezer.</p>" +
        "<p><em>Room 7B is on the map, but not on the door.</em></p>" +
        "<p>" +
        '<a class="choice" href="#">▸ Open the door</a><br />' +
        '<a class="choice" href="#">▸ Check your inventory</a><br />' +
        '<a class="choice" href="#">▸ Turn back</a>' +
        "</p>",
    },
    letters_never_sent: {
      title: "Letters Never Sent",
      by: "sam_writes",
      love: 0,
      ink:
        "=== start ===\n" +
        "Dear you,\n" +
        "I keep writing this letter and folding it into the same square.\n\n" +
        "* [Hide it in the dictionary] -> hide\n" +
        "* [Mail it anyway] -> mail\n" +
        "* [Burn it] -> burn\n\n" +
        "=== hide ===\n" +
        "Today the page number changed.\n\n" +
        "=== mail ===\n" +
        "The envelope addresses itself.\n\n" +
        "=== burn ===\n" +
        "The ash spells a name.\n\n" +
        "-> END\n",
      playerHtml:
        "<p>Dear you, I keep writing this letter and folding it into the same square.</p>" +
        "<p><em>In the morning I hide it in the dictionary again.</em></p>" +
        "<p>" +
        '<a class="choice" href="#">▸ Hide it in the dictionary</a><br />' +
        '<a class="choice" href="#">▸ Mail it anyway</a><br />' +
        '<a class="choice" href="#">▸ Burn it</a>' +
        "</p>",
    },
    civic_lab: {
      title: "Fork in the Road: Civic Lab",
      by: "Mr. Ortiz",
      love: 0,
      ink:
        "=== start ===\n" +
        "The bell rings and the room shifts.\n" +
        "On the board: “Who gets to decide what counts as fair?”\n\n" +
        "* [Start with a story] -> story\n" +
        "* [Start with a rule] -> rule\n" +
        "* [Start with a vote] -> vote\n\n" +
        "=== story ===\n" +
        "You pick a scenario the class can’t ignore.\n\n" +
        "=== rule ===\n" +
        "Three rules, one room.\n\n" +
        "=== vote ===\n" +
        "Hands up. A decision, then consequences.\n\n" +
        "-> END\n",
      playerHtml:
        "<p>The bell rings and the room shifts. On the board: “Who gets to decide what counts as fair?”</p>" +
        "<p><em>You have ten minutes and three choices for how to start.</em></p>" +
        "<p>" +
        '<a class="choice" href="#">▸ Start with a story</a><br />' +
        '<a class="choice" href="#">▸ Start with a rule</a><br />' +
        '<a class="choice" href="#">▸ Start with a vote</a>' +
        "</p>",
    },
  };

  var PROTO_BOOKS = {
    cipher_curriculum: {
      stories: [
        { title: "Ciphers in the Margins", by: "N. Okonkwo" },
        { title: "Footnote Detective", by: "N. Okonkwo" },
        { title: "The Librarian’s Stamp", by: "N. Okonkwo" },
        { title: "Chat Log #12", by: "N. Okonkwo" },
        { title: "Index of Vanishing Words", by: "N. Okonkwo" },
      ],
      storyIds: ["ciphers_margins"],
    },
    cold_case_club: {
      stories: [
        { title: "Receipt at Dawn", by: "Cold Case Club" },
        { title: "The Snowline Witness", by: "Cold Case Club" },
        { title: "Key Under the Mat", by: "Cold Case Club" },
        { title: "Locker 3B", by: "Cold Case Club" },
        { title: "Call Log", by: "Cold Case Club" },
      ],
      storyIds: ["archive_room_7b"],
    },
    after_midnight_pack: {
      stories: [
        { title: "The Last Lighthouse Keeper", by: "Maya Chen" },
        { title: "Bell in the Fog", by: "Maya Chen" },
        { title: "Harbor Without Names", by: "Maya Chen" },
        { title: "Storm Season", by: "Maya Chen" },
        { title: "Lantern Code", by: "Maya Chen" },
      ],
      storyIds: ["lighthouse_keeper"],
    },
    civic_lab_set: {
      stories: [
        { title: "Fork in the Road: Civic Lab", by: "Mr. Ortiz" },
        { title: "Three Rules, One Room", by: "Mr. Ortiz" },
        { title: "Town Hall Simulation", by: "Mr. Ortiz" },
        { title: "Budget Choices", by: "Mr. Ortiz" },
        { title: "Who Benefits?", by: "Mr. Ortiz" },
      ],
      storyIds: ["civic_lab"],
    },
    greenhouse_unit: {
      stories: [
        { title: "Greenhouse Shift", by: "EcoLit Club" },
        { title: "Variable: Light", by: "EcoLit Club" },
        { title: "Variable: Water", by: "EcoLit Club" },
        { title: "Variable: Heat", by: "EcoLit Club" },
        { title: "Reflection Journal", by: "EcoLit Club" },
      ],
      storyIds: ["greenhouse_shift"],
    },
    peer_review_pack: {
      stories: [
        { title: "Peer Review Panic (Ink)", by: "cwilk" },
        { title: "The Comment Storm", by: "cwilk" },
        { title: "Rewrite or Resist", by: "cwilk" },
        { title: "Deadline Dance", by: "cwilk" },
        { title: "One Last Pass", by: "cwilk" },
      ],
      storyIds: ["peer_review_panic"],
    },
    quiet_room_allies: {
      stories: [
        { title: "The Quiet Room", by: "Dr. Patel" },
        { title: "Breathing Exercise", by: "Dr. Patel" },
        { title: "Find an Ally", by: "Dr. Patel" },
        { title: "Hallway Storm", by: "Dr. Patel" },
        { title: "Come Back When Ready", by: "Dr. Patel" },
      ],
      storyIds: ["quiet_room"],
    },
    transit_detours: {
      stories: [
        { title: "Detour Through Addison Street", by: "riverdelta" },
        { title: "Transfer at 9th & Lark", by: "riverdelta" },
        { title: "Stop Name: Remember", by: "riverdelta" },
        { title: "The Last Bus", by: "riverdelta" },
        { title: "Map That Moves", by: "riverdelta" },
      ],
      storyIds: ["addison_detour"],
    },
    coast_storm_anthology: {
      stories: [
        { title: "The Last Lighthouse Keeper", by: "Maya Chen" },
        { title: "Bell in the Fog", by: "Maya Chen" },
        { title: "Storm Season", by: "Maya Chen" },
        { title: "Harbor Without Names", by: "Maya Chen" },
        { title: "Lantern Code", by: "Maya Chen" },
      ],
      storyIds: ["lighthouse_keeper"],
    },
    speculative_brunch: {
      stories: [
        { title: "Sunday Serial", by: "Various" },
        { title: "Notification Future", by: "Various" },
        { title: "Timeline Swipe", by: "Various" },
        { title: "Brunch at the End", by: "Various" },
        { title: "Tap on the Window", by: "Various" },
      ],
      storyIds: ["letters_never_sent"],
    },
  };

  function getBookIdFromLocation() {
    try {
      var u = new URL(window.location.href);
      var id = u.searchParams.get("book") || "";
      return String(id || "").trim();
    } catch (e) {
      return "";
    }
  }

  function initBookStoryLists() {
    var page = document.querySelector("[data-books-page]");
    if (!page) return;
    page.querySelectorAll("[data-book-id]").forEach(function (tile) {
      var id = tile.getAttribute("data-book-id") || "";
      var book = PROTO_BOOKS[id];
      if (!book) return;
      var ul = tile.querySelector("[data-book-storylist]");
      if (!ul) return;
      ul.innerHTML = "";
      book.stories.slice(0, 6).forEach(function (s) {
        var li = document.createElement("li");
        li.textContent = s.title + " — " + s.by;
        ul.appendChild(li);
      });
    });
  }

  function getStoryIdFromLocation() {
    try {
      var u = new URL(window.location.href);
      var id = u.searchParams.get("story") || "";
      return String(id || "").trim();
    } catch (e) {
      return "";
    }
  }

  function initStoryPreviewPage() {
    if (!document.querySelector("[data-proto-story-preview]")) return;
    var id = getStoryIdFromLocation() || "lighthouse_keeper";
    var s = PROTO_STORIES[id] || PROTO_STORIES.lighthouse_keeper;

    document.title = s.title + " — Unfold Studio (Prototype)";

    var titleEl = document.querySelector("[data-story-title]");
    if (titleEl) titleEl.textContent = s.title;

    var byEl = document.querySelector("[data-story-by]");
    if (byEl) byEl.textContent = s.by;

    var loveEl = document.querySelector("[data-story-love]");
    if (loveEl) {
      loveEl.textContent = s.love ? "<3 " + s.love : "";
      loveEl.hidden = !s.love;
    }

    var pre = document.querySelector("[data-story-ink]");
    if (pre) pre.textContent = s.ink || "";

    var player = document.querySelector("[data-story-player]");
    if (player) player.innerHTML = s.playerHtml || "";
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function protoInkToPreviewHtml(ink) {
    var lines = String(ink || "").split(/\r?\n/);
    var html = [];
    var paras = [];
    var choices = [];
    function flushPara() {
      if (paras.length) {
        html.push("<p>" + paras.join(" ") + "</p>");
        paras = [];
      }
    }
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i].trim();
      if (!line) {
        flushPara();
        continue;
      }
      var mK = line.match(/^===\s*(.+?)\s*===$/);
      if (mK) {
        flushPara();
        html.push("<p><strong>" + escapeHtml(mK[1]) + "</strong></p>");
        continue;
      }
      var mCh = line.match(/^\*\s*\[([^\]]+)\]/);
      if (mCh) {
        flushPara();
        var label = mCh[1].replace(/\s*->\s*\S+.*$/i, "").trim();
        choices.push(escapeHtml(label));
        continue;
      }
      if (/^->\s/.test(line) || /^VAR\s/i.test(line)) continue;
      paras.push(escapeHtml(line));
    }
    flushPara();
    if (choices.length) {
      html.push(
      "<p>" +
        choices
          .map(function (c) {
            return '<a class="choice" href="#">▸ ' + c + "</a>";
          })
          .join("<br />") +
        "</p>"
      );
    }
    var body = html.join("");
    if (!body.trim()) {
      body =
        "<p><em>Add lines under a knot such as</em> <code>=== start ===</code> <em>to see them here after Save.</em></p>";
    }
    return '<p class="proto-preview-tag">Player preview (after save)</p>' + body;
  }

  function updateEditorPlayerPreview() {
    var root = document.querySelector("[data-proto-story-editor]");
    if (!root) return;
    var ta = root.querySelector(".proto-ink-editor");
    var pane = root.querySelector("#player .innerText.active");
    if (!ta || !pane) return;
    pane.innerHTML = protoInkToPreviewHtml(ta.value);
  }

  function showProtoSaveFlash(msg) {
    var el = document.getElementById("proto-save-flash");
    if (!el) return;
    el.textContent = msg;
    el.hidden = false;
    if (el._t) clearTimeout(el._t);
    el._t = setTimeout(function () {
      el.hidden = true;
    }, 2200);
  }

  function getProtoDraftDescription() {
    var extra = document.getElementById("proto-draft-desc-extra");
    if (!extra || !extra.textContent) return "";
    var t = extra.textContent;
    if (t.indexOf(" — ") === 0) return t.slice(3).trim();
    return "";
  }

  function persistProtoDraft() {
    var titleEl = document.getElementById("proto-story-title");
    var ta = document.querySelector("[data-proto-story-editor] .proto-ink-editor");
    if (!titleEl || !ta) return;
    sessionStorage.setItem(
      PROTO_DRAFT_KEY,
      JSON.stringify({
        title: titleEl.textContent.trim() || "Untitled",
        description: getProtoDraftDescription(),
        ink: ta.value,
      })
    );
  }

  function initNewStoryForm() {
    var form = document.querySelector("[data-proto-new-story-form]");
    if (!form) return;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var titleIn = form.querySelector('[name="title"]');
      var descIn = form.querySelector('[name="description"]');
      var title =
        titleIn && titleIn.value.trim() ? titleIn.value.trim() : "Untitled";
      var description =
        descIn && descIn.value.trim() ? descIn.value.trim() : "";
      sessionStorage.setItem(
        PROTO_DRAFT_KEY,
        JSON.stringify({
          title: title,
          description: description,
          ink: DEFAULT_INK,
        })
      );
      window.location.href = "story-editor.html";
    });
  }

  function initStoryEditorFromStorage() {
    if (!document.querySelector("[data-proto-story-editor]")) return;
    var titleEl = document.getElementById("proto-story-title");
    var ta = document.querySelector("[data-proto-story-editor] .proto-ink-editor");
    var extra = document.getElementById("proto-draft-desc-extra");
    if (!titleEl || !ta) return;

    var d = null;
    try {
      d = JSON.parse(sessionStorage.getItem(PROTO_DRAFT_KEY) || "null");
    } catch (e) {
      d = null;
    }
    if (d && typeof d === "object") {
      titleEl.textContent = d.title || "Untitled";
      if (d.description && extra) extra.textContent = " — " + d.description;
      ta.value = typeof d.ink === "string" ? d.ink : DEFAULT_INK;
    } else {
      titleEl.textContent = "Untitled";
      ta.value = DEFAULT_INK;
      if (extra) extra.textContent = "";
    }
    document.title =
      titleEl.textContent.trim() + " — Unfold Studio (Prototype)";
    updateEditorPlayerPreview();
  }

  function initStorySaveRename() {
    if (!document.querySelector("[data-proto-story-editor]")) return;
    var titleEl = document.getElementById("proto-story-title");
    var save = document.getElementById("save_story");
    var ver = document.getElementById("save_version");
    var rename = document.getElementById("edit_story");
    if (!titleEl) return;

    function doSave() {
      persistProtoDraft();
      updateEditorPlayerPreview();
      showProtoSaveFlash("Saved locally (prototype).");
    }

    if (save) {
      save.addEventListener("click", function (e) {
        e.preventDefault();
        doSave();
      });
    }
    if (ver) {
      ver.addEventListener("click", function (e) {
        e.preventDefault();
        doSave();
      });
    }
    if (rename) {
      rename.addEventListener("click", function (e) {
        e.preventDefault();
        var t = window.prompt("Story title", titleEl.textContent.trim());
        if (t != null && String(t).trim()) {
          titleEl.textContent = String(t).trim();
          document.title =
            titleEl.textContent.trim() + " — Unfold Studio (Prototype)";
          persistProtoDraft();
        }
      });
    }

    var ta = document.querySelector("[data-proto-story-editor] .proto-ink-editor");
    if (ta) {
      ta.addEventListener("input", function () {
        updateEditorPlayerPreview();
      });
    }
  }

  function initBrowseSort() {
    var root = document.querySelector("[data-browse-root]");
    if (!root) return;

    var tabs = root.querySelectorAll("[data-sort-tab]");
    var panels = root.querySelectorAll("[data-browse-panel]");

    function activate(sort) {
      tabs.forEach(function (t) {
        t.classList.toggle("is-active", t.getAttribute("data-sort-tab") === sort);
      });
      panels.forEach(function (p) {
        var key = p.getAttribute("data-browse-panel");
        var show = sort === "all" ? key === "top" || key === "new" : key === sort;
        p.classList.toggle("is-visible", show);
      });
      if (history.replaceState) {
        history.replaceState(null, "", "#" + sort);
      }
      applySearch(lastSearchQuery);
    }

    tabs.forEach(function (tab) {
      tab.addEventListener("click", function (e) {
        e.preventDefault();
        activate(tab.getAttribute("data-sort-tab"));
      });
    });

    var hash = (location.hash || "").replace("#", "");
    if (hash === "new" || hash === "top" || hash === "all") {
      activate(hash);
    } else {
      activate("all");
    }
  }

  function initFilterChips() {
    document.querySelectorAll(".filter-chips").forEach(function (wrap) {
      wrap.querySelectorAll("button").forEach(function (btn) {
        btn.addEventListener("click", function () {
          wrap.querySelectorAll("button").forEach(function (b) {
            b.classList.remove("is-on");
          });
          btn.classList.add("is-on");
          applySearch(lastSearchQuery);
        });
      });
    });
  }

  function normalize(s) {
    return String(s || "")
      .toLowerCase()
      .replace(/\s+/g, " ")
      .trim();
  }

  function getBrowseGenre() {
    var el = document.querySelector(
      "[data-browse-root] [data-proto-filter-type='genre'] .is-on"
    );
    if (!el) return "all";
    return el.getAttribute("data-genre") || "all";
  }

  function getBrowseLength() {
    var el = document.querySelector(
      "[data-browse-root] [data-proto-filter-type='length'] .is-on"
    );
    if (!el) return "any";
    return el.getAttribute("data-length") || "any";
  }

  function getBooksGenre() {
    var el = document.querySelector(
      "[data-books-page] [data-proto-filter-type='book-genre'] .is-on"
    );
    if (!el) return "all";
    return el.getAttribute("data-genre") || "all";
  }

  function getTargetStoryCards() {
    var scope = document.querySelector("[data-search-scope]");
    if (!scope || scope.hasAttribute("data-books-page")) return [];
    var browseRoot = scope.querySelector("[data-browse-root]");
    if (browseRoot) {
      var visPanels = browseRoot.querySelectorAll("[data-browse-panel].is-visible");
      if (visPanels && visPanels.length) {
        var all = [];
        visPanels.forEach(function (p) {
          all = all.concat(Array.prototype.slice.call(p.querySelectorAll("[data-story-card]")));
        });
        return all;
      }
    }
    return Array.prototype.slice.call(scope.querySelectorAll("[data-story-card]"));
  }

  function applySearch(rawQuery) {
    lastSearchQuery = rawQuery;

    if (document.querySelector("[data-books-page]")) {
      applyBooksFilters(rawQuery);
      return;
    }

    var q = normalize(rawQuery);
    var words = q ? q.split(" ").filter(Boolean) : [];
    var genre = getBrowseGenre();
    var lengthF = getBrowseLength();
    var bookId = getBookIdFromLocation();
    var book = bookId ? PROTO_BOOKS[bookId] : null;
    var allowed = book ? (book.storyIds || []) : null;

    getTargetStoryCards().forEach(function (el) {
      var hay = normalize(el.getAttribute("data-search"));
      var searchOk =
        !words.length ||
        words.every(function (w) {
          return hay.indexOf(w) !== -1;
        });
      var g = normalize(el.getAttribute("data-genre") || "");
      var genreOk = genre === "all" || g === normalize(genre);
      var len = normalize(el.getAttribute("data-length") || "medium");
      var lengthOk = lengthF === "any" || len === normalize(lengthF);
      var sid = el.getAttribute("data-story-id") || "";
      var bookOk = !allowed || allowed.indexOf(sid) !== -1;
      var ok = searchOk && genreOk && lengthOk && bookOk;
      el.classList.toggle("is-search-hidden", !ok);
    });

    var empty = document.getElementById("proto-search-empty");
    if (empty) {
      var visible = getTargetStoryCards().filter(function (el) {
        return !el.classList.contains("is-search-hidden");
      });
      empty.hidden = visible.length > 0;
    }
  }

  function applyBooksFilters(rawQuery) {
    var page = document.querySelector("[data-books-page]");
    if (!page) return;

    var q = normalize(rawQuery);
    var words = q ? q.split(" ").filter(Boolean) : [];
    var genre = getBooksGenre();

    page.querySelectorAll("[data-book-card]").forEach(function (card) {
      var hay = normalize(card.getAttribute("data-search"));
      var searchOk =
        !words.length ||
        words.every(function (w) {
          return hay.indexOf(w) !== -1;
        });
      var gRaw = normalize(card.getAttribute("data-genre") || "");
      var gList = gRaw
        ? gRaw.split(/[,\s]+/).filter(Boolean)
        : [];
      var genreOk = genre === "all" || gList.indexOf(normalize(genre)) !== -1;
      var ok = searchOk && genreOk;
      card.classList.toggle("is-search-hidden", !ok);
    });

    page.querySelectorAll(".books-shelf").forEach(function (shelf) {
      var anyVisible = Array.prototype.some.call(
        shelf.querySelectorAll("[data-book-card]"),
        function (c) {
          return !c.classList.contains("is-search-hidden");
        }
      );
      shelf.classList.toggle("is-shelf-hidden", !anyVisible);
    });

    var empty = document.getElementById("proto-books-empty");
    if (empty) {
      var vis = Array.prototype.filter.call(
        page.querySelectorAll("[data-book-card]"),
        function (c) {
          return !c.classList.contains("is-search-hidden");
        }
      );
      empty.hidden = vis.length > 0;
    }
  }

  function initPrototypeSearch() {
    var inputs = document.querySelectorAll(".js-proto-search-input");
    if (!inputs.length) return;

    function sync(val) {
      Array.prototype.forEach.call(inputs, function (inp) {
        if (inp.value !== val) inp.value = val;
      });
    }

    Array.prototype.forEach.call(inputs, function (inp) {
      inp.addEventListener("input", function () {
        sync(inp.value);
        applySearch(inp.value);
      });
      inp.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
          inp.value = "";
          sync("");
          applySearch("");
        }
      });
    });

    document.querySelectorAll(".js-proto-search-form").forEach(function (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var inp = form.querySelector(".js-proto-search-input");
        if (inp) {
          sync(inp.value);
          applySearch(inp.value);
        }
      });
    });
  }

  function initStoryCodeToggle() {
    var root = document.getElementById("twopane");
    if (!root || !root.classList.contains("proto-twopane")) return;
    var showBtn = document.getElementById("show_code");
    var hideBtn = document.getElementById("hide_code");
    var showOpt = document.getElementById("show_code_opt");
    var hideOpt = document.getElementById("hide_code_opt");
    function setSolo(on) {
      root.classList.toggle("solo", on);
      if (showOpt) showOpt.style.display = on ? "" : "none";
      if (hideOpt) hideOpt.style.display = on ? "none" : "";
    }
    if (showBtn) {
      showBtn.addEventListener("click", function (e) {
        e.preventDefault();
        setSolo(false);
      });
    }
    if (hideBtn) {
      hideBtn.addEventListener("click", function (e) {
        e.preventDefault();
        setSolo(true);
      });
    }
  }

  function initStoryReplay() {
    var r = document.getElementById("replay_story");
    var sc = document.querySelector(".proto-story-page .scrollContainer");
    if (!r || !sc) return;
    r.addEventListener("click", function (e) {
      e.preventDefault();
      sc.scrollTop = 0;
    });
  }

  function initChoiceLinkStub() {
    document.body.addEventListener("click", function (e) {
      var a = e.target.closest(".proto-story-page a.choice");
      if (a) e.preventDefault();
    });
  }

  function initForkClaimDialog() {
    var trig = document.getElementById("proto-fork-trigger");
    var dlg = document.getElementById("proto-fork-dialog");
    if (!trig || !dlg) return;
    trig.addEventListener("click", function (e) {
      e.preventDefault();
      if (dlg.showModal) dlg.showModal();
    });
    var closeBtn = document.getElementById("proto-fork-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", function () {
        if (dlg.close) dlg.close();
      });
    }
  }

  function readProtoAuth() {
    try {
      var raw = sessionStorage.getItem(PROTO_AUTH_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) {
      return null;
    }
  }

  function writeProtoAuth(obj) {
    sessionStorage.setItem(PROTO_AUTH_KEY, JSON.stringify(obj));
  }

  function clearProtoAuth() {
    sessionStorage.removeItem(PROTO_AUTH_KEY);
  }

  function initProtoAuthNav() {
    var guest = document.querySelector(".proto-auth-guest");
    var sessionEl = document.querySelector(".proto-auth-session");
    var usernameOut = document.getElementById("proto-nav-username");
    var logout = document.getElementById("proto-nav-logout");
    if (!guest || !sessionEl) return;

    var data = readProtoAuth();
    var ok = data && data.loggedIn && data.username;

    if (ok) {
      guest.setAttribute("hidden", "");
      sessionEl.removeAttribute("hidden");
      if (usernameOut) usernameOut.textContent = data.username;
    } else {
      guest.removeAttribute("hidden");
      sessionEl.setAttribute("hidden", "");
    }

    if (logout) {
      logout.addEventListener("click", function (e) {
        e.preventDefault();
        clearProtoAuth();
        window.location.href = "featured.html";
      });
    }
  }

  function initProtoAuthLoggedBanner() {
    var root = document.querySelector("[data-proto-auth-page]");
    if (!root) return;

    var data = readProtoAuth();
    var banner = document.getElementById("proto-auth-logged-banner");
    var nameEl = document.getElementById("proto-auth-banner-name");
    var loginPanel = document.getElementById("proto-login-panel");
    var signupPanel = document.getElementById("proto-signup-panel");
    var logoutBtn = document.getElementById("proto-auth-banner-logout");

    if (data && data.loggedIn && data.username) {
      if (banner && nameEl) {
        nameEl.textContent = data.username;
        banner.hidden = false;
      }
      if (loginPanel) loginPanel.hidden = true;
      if (signupPanel) signupPanel.hidden = true;
    }

    if (logoutBtn) {
      logoutBtn.addEventListener("click", function () {
        clearProtoAuth();
        window.location.href = "featured.html";
      });
    }
  }

  function validateSignupPassword(pw) {
    if (!pw || pw.length < 8) return "Use at least 8 characters.";
    if (!/[a-z]/.test(pw)) return "Include a lowercase letter.";
    if (!/[A-Z]/.test(pw)) return "Include an uppercase letter.";
    if (!/[^A-Za-z0-9]/.test(pw)) return "Include at least one special symbol.";
    return "";
  }

  function validateStudentJoinPassword(pw) {
    if (!pw) return "Enter a password.";
    if (pw.length < 8 || pw.length > 14) return "Use 8–14 characters.";
    if (!/[0-9]/.test(pw)) return "Include at least one number.";
    if (!/[a-z]/.test(pw) || !/[A-Z]/.test(pw)) {
      return "Include uppercase and lowercase letters.";
    }
    return "";
  }

  function initJoinStudentForm() {
    var root = document.querySelector("[data-join-student-page]");
    if (!root) return;

    var form = document.getElementById("proto-form-join-student");
    var err = document.getElementById("proto-join-error");
    if (!form) return;

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (err) {
        err.hidden = true;
        err.textContent = "";
      }

      var code = (form.querySelector('[name="course_code"]') || {}).value;
      var u = (form.querySelector('[name="username"]') || {}).value;
      var pw = (form.querySelector('[name="password"]') || {}).value;
      var pw2 = (form.querySelector('[name="password2"]') || {}).value;

      code = code != null ? String(code).trim() : "";
      u = u != null ? String(u).trim() : "";
      pw = pw != null ? String(pw) : "";
      pw2 = pw2 != null ? String(pw2) : "";

      if (!code || !u || !pw || !pw2) {
        if (err) {
          err.textContent = "Fill in every field, including the course access code.";
          err.hidden = false;
        }
        return;
      }

      var pe = validateStudentJoinPassword(pw);
      if (pe) {
        if (err) {
          err.textContent = pe;
          err.hidden = false;
        }
        return;
      }

      if (pw !== pw2) {
        if (err) {
          err.textContent = "Passwords do not match.";
          err.hidden = false;
        }
        return;
      }

      writeProtoAuth({
        username: u,
        loggedIn: true,
        role: "student",
        courseCode: code,
      });
      window.location.href = "student-enrolled.html";
    });
  }

  function initStudentEnrolledPage() {
    if (!document.querySelector("[data-student-enrolled-page]")) return;
    var data = readProtoAuth();
    if (!data || !data.loggedIn || !data.username) {
      window.location.replace("login.html");
      return;
    }
    var u1 = document.getElementById("proto-enrolled-username");
    var u2 = document.getElementById("proto-enrolled-username2");
    if (u1) u1.textContent = data.username;
    if (u2) u2.textContent = data.username;
  }

  function initStudentDashboard() {
    var root = document.querySelector("[data-student-dashboard]");
    if (!root) return;
    var data = readProtoAuth();
    if (!data || !data.loggedIn || !data.username) {
      window.location.replace("login.html");
      return;
    }
    var greet = document.getElementById("proto-dashboard-greet-name");
    if (greet) greet.textContent = data.username;
  }

  function initAuthForms() {
    var root = document.querySelector("[data-proto-auth-page]");
    if (!root) return;

    var loginForm = document.getElementById("proto-form-login");
    var signupForm = document.getElementById("proto-form-signup");
    var loginErr = document.getElementById("proto-login-error");
    var signupErr = document.getElementById("proto-signup-error");
    var teacherModal = document.getElementById("proto-teacher-modal");
    var signupRoleSelect = document.getElementById("proto-signup-role");
    function getTeacherSignupPayload() {
      if (!signupForm) return null;
      var u = (signupForm.querySelector('[name="username"]') || {}).value;
      var email = (signupForm.querySelector('[name="email"]') || {}).value;
      u = u != null ? String(u).trim() : "";
      email = email != null ? String(email).trim() : "";
      return u ? { username: u, email: email } : null;
    }

    function openTeacherModalFromSignup() {
      if (!teacherModal || !teacherModal.showModal) return false;
      teacherModal._protoTeacherSignup = getTeacherSignupPayload() || teacherModal._protoTeacherSignup || null;
      teacherModal.showModal();
      return true;
    }
    if (signupRoleSelect) {
      signupRoleSelect.addEventListener("change", function () {
        if (signupRoleSelect.value === "student") {
          window.location.href = "join-student.html";
          return;
        }
        if (signupRoleSelect.value === "teacher") {
          if (!openTeacherModalFromSignup()) {
            window.alert("Instructor signup requires approval—email " + PROTO_INSTRUCTOR_EMAIL + ".");
          }
        }
      });
    }

    if (loginForm) {
      loginForm.addEventListener("submit", function (e) {
        e.preventDefault();
        if (loginErr) {
          loginErr.hidden = true;
          loginErr.textContent = "";
        }
        var u = (loginForm.querySelector('[name="username"]') || {}).value;
        var p = (loginForm.querySelector('[name="password"]') || {}).value;
        u = u != null ? String(u).trim() : "";
        p = p != null ? String(p) : "";
        if (!u || !p) {
          if (loginErr) {
            loginErr.textContent = "Enter a username and password.";
            loginErr.hidden = false;
          }
          return;
        }
        var isInstructorDemo = /^prof_chris$/i.test(u);
        writeProtoAuth({
          username: u,
          loggedIn: true,
          role: isInstructorDemo ? "teacher" : "demo",
        });
        window.location.href = isInstructorDemo ? "teacher-dashboard.html" : "index.html";
      });
    }

    if (signupForm) {
      signupForm.addEventListener("submit", function (e) {
        e.preventDefault();
        if (signupErr) {
          signupErr.hidden = true;
          signupErr.textContent = "";
        }

        var roleEl = signupForm.querySelector('[name="role"]');
        var role = roleEl ? roleEl.value : "";
        var u = (signupForm.querySelector('[name="username"]') || {}).value;
        var email = (signupForm.querySelector('[name="email"]') || {}).value;
        var pw = (signupForm.querySelector('[name="password"]') || {}).value;
        var pw2 = (signupForm.querySelector('[name="password2"]') || {}).value;

        u = u != null ? String(u).trim() : "";
        email = email != null ? String(email).trim() : "";
        pw = pw != null ? String(pw) : "";
        pw2 = pw2 != null ? String(pw2) : "";

        if (role === "student") {
          window.location.href = "join-student.html";
          return;
        }

        if (!role || !u || !email || !pw) {
          if (signupErr) {
            signupErr.textContent = "Fill in every field, including I am a…";
            signupErr.hidden = false;
          }
          return;
        }

        var pe = validateSignupPassword(pw);
        if (pe) {
          if (signupErr) {
            signupErr.textContent = pe;
            signupErr.hidden = false;
          }
          return;
        }
        if (pw !== pw2) {
          if (signupErr) {
            signupErr.textContent = "Passwords do not match.";
            signupErr.hidden = false;
          }
          return;
        }

        if (role === "teacher") {
          // Prototype flow: show approval modal, then continue into instructor pages.
          if (teacherModal && teacherModal.showModal) {
            teacherModal._protoTeacherSignup = { username: u, email: email };
            teacherModal.showModal();
          } else {
            alert("Instructor signup requires approval—email " + PROTO_INSTRUCTOR_EMAIL + " (prototype).");
          }
          return;
        }

        writeProtoAuth({ username: u, loggedIn: true, role: role, email: email });
        window.location.href = "index.html";
      });
    }

    function closeTeacherModal() {
      if (teacherModal && teacherModal.close) teacherModal.close();
    }

    var gotit = document.getElementById("proto-teacher-gotit");
    var closeBtn = document.getElementById("proto-teacher-modal-close");
    var copyBtn = document.getElementById("proto-teacher-copy-email");
    if (teacherModal && gotit) {
      gotit.addEventListener("click", function () {
        var payload = teacherModal._protoTeacherSignup || getTeacherSignupPayload() || null;
        // Prototype: always advance to the teacher flow from this modal.
        var username = payload && payload.username ? payload.username : "prof_chris";
        var email = payload && payload.email ? payload.email : "";
        writeProtoAuth({
          username: username,
          loggedIn: true,
          role: "teacher",
          email: email,
        });
        window.location.href = "teacher-dashboard.html";
      });
    }
    if (teacherModal && closeBtn) {
      closeBtn.addEventListener("click", closeTeacherModal);
    }
    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        var email = PROTO_INSTRUCTOR_EMAIL;
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(email).then(
            function () {
              copyBtn.textContent = "Copied!";
              setTimeout(function () {
                copyBtn.textContent = "Copy email address";
              }, 2000);
            },
            function () {
              window.prompt("Copy this email:", email);
            }
          );
        } else {
          window.prompt("Copy this email:", email);
        }
      });
    }
    if (teacherModal) {
      teacherModal.addEventListener("click", function (e) {
        if (e.target === teacherModal) closeTeacherModal();
      });
    }
  }

  function initTeacherDashboard() {
    if (!document.querySelector("[data-teacher-dashboard]")) return;
    var data = readProtoAuth();
    if (!data || !data.loggedIn || !data.username) {
      window.location.replace("login.html");
      return;
    }
    if (data.role !== "teacher" && data.role !== "instructor") {
      window.location.replace("index.html");
      return;
    }
    var nameEl = document.getElementById("proto-teacher-dash-name");
    if (nameEl) nameEl.textContent = data.username;
  }

  function initTeacherPages() {
    if (!document.querySelector("[data-teacher-page]")) return;
    var data = readProtoAuth();
    if (!data || !data.loggedIn || !data.username) {
      window.location.replace("login.html");
      return;
    }
    if (data.role !== "teacher" && data.role !== "instructor") {
      window.location.replace("index.html");
      return;
    }
  }

  function initTeacherGroupForm() {
    var f = document.getElementById("proto-teacher-new-group-form");
    if (!f) return;
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      window.location.href = "teacher-group-detail.html";
    });
  }

  function initTeacherPromptForm() {
    var f = document.getElementById("proto-teacher-new-prompt-form");
    if (!f) return;
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      window.location.href = "teacher-prompt-submissions.html";
    });
  }

  function initProtoDemoAlertButtons() {
    document.querySelectorAll("[data-proto-demo-alert]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        window.alert("Prototype only — no server action.");
      });
    });
  }

  function initLoginTabs() {
    var loginPanel = document.getElementById("proto-login-panel");
    var signupPanel = document.getElementById("proto-signup-panel");
    var authLogin = document.getElementById("proto-nav-login");
    var authSignup = document.getElementById("proto-nav-signup");
    if (!loginPanel || !signupPanel) return;

    var data = readProtoAuth();
    if (data && data.loggedIn && data.username) return;

    function sync() {
      var signup = (location.hash || "").toLowerCase() === "#signup";
      loginPanel.hidden = signup;
      signupPanel.hidden = !signup;
      if (authLogin) authLogin.classList.toggle("is-active", !signup);
      if (authSignup) authSignup.classList.toggle("is-active", signup);
      document.title = signup
        ? "Sign up — Unfold Studio (Prototype)"
        : "Log in — Unfold Studio (Prototype)";
    }

    sync();
    window.addEventListener("hashchange", sync);
  }

  document.addEventListener("DOMContentLoaded", function () {
    initStoryPreviewPage();
    initStudentDashboard();
    initTeacherDashboard();
    initTeacherPages();
    initProtoAuthNav();
    initProtoAuthLoggedBanner();
    initBrowseSort();
    initFilterChips();
    initPrototypeSearch();
    initLoginTabs();
    initAuthForms();
    initJoinStudentForm();
    initStudentEnrolledPage();
    initTeacherGroupForm();
    initTeacherPromptForm();
    initBookStoryLists();
    initProtoDemoAlertButtons();
    initForkClaimDialog();
    initNewStoryForm();
    initStoryEditorFromStorage();
    initStorySaveRename();
    initStoryCodeToggle();
    initStoryReplay();
    initChoiceLinkStub();
    applySearch("");
  });
})();
