/* Prototype: bottom panel tabs on Completed Story page. */
(function () {
  "use strict";

  function initStudentStoryTabs() {
    var root = document.querySelector("[data-student-story-completed]");
    if (!root) return;

    var tabs = Array.prototype.slice.call(document.querySelectorAll("[data-panel-tab]"));
    var panels = Array.prototype.slice.call(document.querySelectorAll("[data-panel]"));

    function setActive(name) {
      tabs.forEach(function (t) {
        t.classList.toggle("is-active", t.getAttribute("data-panel-tab") === name);
      });
      panels.forEach(function (p) {
        p.classList.toggle("is-active", p.getAttribute("data-panel") === name);
      });
    }

    function fromHash() {
      var h = (window.location.hash || "").replace("#", "").toLowerCase();
      if (!h) return "history";
      if (h === "comments") return "feedback";
      if (h === "feedback" || h === "output" || h === "problems" || h === "history") return h;
      return "history";
    }

    tabs.forEach(function (t) {
      t.addEventListener("click", function (e) {
        e.preventDefault();
        var name = t.getAttribute("data-panel-tab");
        window.location.hash = name;
        setActive(name);
      });
    });

    window.addEventListener("hashchange", function () {
      setActive(fromHash());
    });

    setActive(fromHash());
  }

  document.addEventListener("DOMContentLoaded", initStudentStoryTabs);
})();

