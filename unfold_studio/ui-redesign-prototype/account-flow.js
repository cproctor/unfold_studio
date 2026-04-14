/* Prototype-only: account signup + join code flow (isolated from script.js). */
(function () {
  "use strict";

  var AUTH_KEY = "unfoldProtoAuth";
  var CODES_KEY = "unfoldProtoJoinCodesV1";
  var LAST_JOIN_KEY = "unfoldProtoLastJoinV1";
  var TEACHER_EMAIL = "chrisp@buffalo.edu";

  function safeJsonParse(s, fallback) {
    try {
      return JSON.parse(s);
    } catch (e) {
      return fallback;
    }
  }

  function readAuth() {
    return safeJsonParse(sessionStorage.getItem(AUTH_KEY) || "null", null);
  }

  function writeAuth(data) {
    sessionStorage.setItem(AUTH_KEY, JSON.stringify(data));
  }

  function clearAuth() {
    sessionStorage.removeItem(AUTH_KEY);
  }

  function newCode() {
    var chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    var out = "";
    for (var i = 0; i < 8; i++) out += chars[Math.floor(Math.random() * chars.length)];
    return out;
  }

  function seedCodesIfEmpty() {
    var cur = safeJsonParse(localStorage.getItem(CODES_KEY) || "null", null);
    if (cur && cur.codes && Array.isArray(cur.codes)) return cur;
    var seeded = {
      groupId: "group_b",
      groupName: "Group B",
      codes: [
        { id: "c1", code: "AB461", assignedUser: null },
        { id: "c2", code: "IK200", assignedUser: null },
        { id: "c3", code: "TH847", assignedUser: null },
        { id: "c4", code: "QR503", assignedUser: null },
        { id: "c5", code: "LJ318", assignedUser: null },
      ],
    };
    localStorage.setItem(CODES_KEY, JSON.stringify(seeded));
    return seeded;
  }

  function readCodes() {
    return seedCodesIfEmpty();
  }

  function writeCodes(state) {
    localStorage.setItem(CODES_KEY, JSON.stringify(state));
  }

  function setError(el, msg) {
    if (!el) return;
    el.textContent = msg || "";
    el.hidden = !msg;
  }

  function validateUsername(u) {
    if (!u) return "Enter a username.";
    if (!/^[0-9a-zA-Z_]+$/.test(u)) return "Only letters, numbers, and _ are allowed in usernames.";
    if (!/^[a-zA-Z][0-9a-zA-Z_]+$/.test(u)) return "Username must start with a letter.";
    return "";
  }

  function validatePassword(pw) {
    if (!pw) return "Enter a password.";
    if (pw.length < 8) return "Password must be at least 8 characters.";
    if (pw.length > 14) return "Password must be at most 14 characters.";
    if (!/[0-9]/.test(pw)) return "Password must contain a number.";
    if (!/[a-z]/.test(pw) || !/[A-Z]/.test(pw)) return "Password must contain uppercase and lowercase letters.";
    return "";
  }

  function initSignupPage() {
    var root = document.querySelector("[data-account-signup-page]");
    if (!root) return;

    var form = document.getElementById("account-signup-form");
    var err = document.getElementById("account-signup-error");
    var userType = document.getElementById("account-user-type");
    var emailField = document.getElementById("account-email-field");

    var modal = document.getElementById("account-teacher-modal");
    var modalClose = document.getElementById("account-teacher-modal-close");
    var modalGotit = document.getElementById("account-teacher-gotit");
    var modalCopy = document.getElementById("account-teacher-copy-email");

    function syncEmailVisibility() {
      if (!userType || !emailField) return;
      var isStudent = userType.value === "student";
      emailField.style.display = isStudent ? "none" : "";
    }

    if (userType) {
      userType.addEventListener("change", function () {
        syncEmailVisibility();
        if (userType.value === "student") {
          window.location.href = "account-join-student.html";
          return;
        }
        if (userType.value === "teacher" && modal && modal.showModal) {
          modal.showModal();
        }
      });
      syncEmailVisibility();
    }

    function closeModal() {
      if (modal && modal.close) modal.close();
    }

    if (modalClose) modalClose.addEventListener("click", closeModal);
    if (modal) {
      modal.addEventListener("click", function (e) {
        if (e.target === modal) closeModal();
      });
    }

    if (modalCopy) {
      modalCopy.addEventListener("click", function () {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(TEACHER_EMAIL).then(
            function () {
              modalCopy.textContent = "Copied!";
              setTimeout(function () {
                modalCopy.textContent = "Copy email address";
              }, 2000);
            },
            function () {
              window.prompt("Copy this email:", TEACHER_EMAIL);
            }
          );
        } else {
          window.prompt("Copy this email:", TEACHER_EMAIL);
        }
      });
    }

    if (modalGotit) {
      modalGotit.addEventListener("click", function () {
        var username = (document.getElementById("account-username") || {}).value;
        username = username != null ? String(username).trim() : "";
        writeAuth({ username: username || "prof_chris", loggedIn: true, role: "teacher" });
        window.location.href = "teacher-dashboard.html";
      });
    }

    if (!form) return;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      setError(err, "");

      var u = (document.getElementById("account-username") || {}).value;
      var email = (document.getElementById("account-email") || {}).value;
      var pw = (document.getElementById("account-password") || {}).value;
      var pw2 = (document.getElementById("account-password2") || {}).value;
      var role = userType ? userType.value : "regular";

      u = u != null ? String(u).trim() : "";
      email = email != null ? String(email).trim() : "";
      pw = pw != null ? String(pw) : "";
      pw2 = pw2 != null ? String(pw2) : "";

      if (role === "student") {
        window.location.href = "account-join-student.html";
        return;
      }

      var ue = validateUsername(u);
      if (ue) return setError(err, ue);

      if ((role === "regular" || role === "teacher") && !email) {
        return setError(err, "Email is required for this account type.");
      }

      var pe = validatePassword(pw);
      if (pe) return setError(err, pe);
      if (pw !== pw2) return setError(err, "Passwords do not match.");

      writeAuth({ username: u, loggedIn: true, role: role === "teacher" ? "teacher" : "demo", email: email });

      if (role === "teacher") {
        if (modal && modal.showModal) modal.showModal();
        else window.location.href = "teacher-dashboard.html";
        return;
      }

      window.location.href = "featured.html";
    });
  }

  function initJoinStudentPage() {
    var root = document.querySelector("[data-account-join-student-page]");
    if (!root) return;

    var form = document.getElementById("account-join-student-form");
    var err = document.getElementById("account-join-error");
    if (!form) return;

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      setError(err, "");

      var code = (document.getElementById("account-join-code") || {}).value;
      var u = (document.getElementById("account-join-username") || {}).value;
      var pw = (document.getElementById("account-join-password") || {}).value;
      var pw2 = (document.getElementById("account-join-password2") || {}).value;

      code = code != null ? String(code).trim().toUpperCase() : "";
      u = u != null ? String(u).trim() : "";
      pw = pw != null ? String(pw) : "";
      pw2 = pw2 != null ? String(pw2) : "";

      var ue = validateUsername(u);
      if (ue) return setError(err, ue);

      var pe = validatePassword(pw);
      if (pe) return setError(err, pe);
      if (pw !== pw2) return setError(err, "Passwords do not match.");

      var state = readCodes();
      var match = state.codes.find(function (c) {
        return c.code === code;
      });

      if (!match) return setError(err, "Invalid or expired join code.");
      if (match.assignedUser && match.assignedUser !== u) {
        return setError(err, "This code has already been used.");
      }

      match.assignedUser = u;
      writeCodes(state);

      writeAuth({ username: u, loggedIn: true, role: "student" });
      sessionStorage.setItem(LAST_JOIN_KEY, JSON.stringify({ groupName: state.groupName, code: code }));
      window.location.href = "account-student-welcome.html";
    });
  }

  function initStudentWelcomePage() {
    var root = document.querySelector("[data-account-student-welcome-page]");
    if (!root) return;

    var auth = readAuth();
    var uEl = document.getElementById("account-welcome-username");
    var gEl = document.getElementById("account-welcome-group");
    if (uEl) uEl.textContent = auth && auth.username ? auth.username : "student";

    var joined = safeJsonParse(sessionStorage.getItem(LAST_JOIN_KEY) || "null", null);
    if (gEl && joined && joined.groupName) gEl.textContent = joined.groupName;

    var logout = document.getElementById("account-welcome-logout");
    if (logout) {
      logout.addEventListener("click", function (e) {
        e.preventDefault();
        clearAuth();
        window.location.href = "account-signup.html";
      });
    }
  }

  function initTeacherCodesPage() {
    var root = document.querySelector("[data-account-teacher-codes-page]");
    if (!root) return;

    var auth = readAuth();
    if (!auth || !auth.loggedIn) {
      window.location.href = "account-signup.html";
      return;
    }

    var uEl = document.getElementById("account-teacher-codes-username");
    if (uEl) uEl.textContent = auth.username || "prof_chris";

    var logout = document.getElementById("account-teacher-codes-logout");
    if (logout) {
      logout.addEventListener("click", function (e) {
        e.preventDefault();
        clearAuth();
        window.location.href = "account-signup.html";
      });
    }

    function render() {
      var state = readCodes();
      var tbody = document.getElementById("account-codes-tbody");
      var count = document.getElementById("account-codes-count");
      if (!tbody) return;

      if (count) count.textContent = state.codes.length + " total";

      tbody.innerHTML = "";
      state.codes
        .slice()
        .sort(function (a, b) {
          if (!!a.assignedUser === !!b.assignedUser) return a.code.localeCompare(b.code);
          return a.assignedUser ? 1 : -1;
        })
        .forEach(function (c) {
          var tr = document.createElement("tr");
          tr.innerHTML =
            "<td><code class=\"proto-teacher-code\">" +
            c.code +
            "</code></td>" +
            "<td>" +
            (c.assignedUser ? c.assignedUser : "<span class=\"proto-dash-muted\">Unused</span>") +
            "</td>" +
            "<td class=\"proto-teacher-table-actions\">" +
            (c.assignedUser
              ? '<button type="button" class="btn btn-ghost btn-sm" data-action="remove" data-id="' +
                c.id +
                '">→ Remove</button>'
              : '<button type="button" class="btn btn-ghost-danger btn-sm" data-action="delete" data-id="' +
                c.id +
                '">Delete</button>') +
            "</td>";
          tbody.appendChild(tr);
        });
    }

    var form = document.getElementById("account-generate-codes-form");
    if (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var qty = parseInt((document.getElementById("account-generate-quantity") || {}).value, 10);
        qty = isFinite(qty) ? Math.max(1, Math.min(50, qty)) : 5;
        var state = readCodes();
        for (var i = 0; i < qty; i++) {
          state.codes.push({ id: "c_" + Date.now() + "_" + i, code: newCode(), assignedUser: null });
        }
        writeCodes(state);
        render();
      });
    }

    var tbody = document.getElementById("account-codes-tbody");
    if (tbody) {
      tbody.addEventListener("click", function (e) {
        var btn = e.target && e.target.closest ? e.target.closest("button[data-action]") : null;
        if (!btn) return;
        var action = btn.getAttribute("data-action");
        var id = btn.getAttribute("data-id");
        var state = readCodes();
        var idx = state.codes.findIndex(function (c) {
          return c.id === id;
        });
        if (idx < 0) return;

        var code = state.codes[idx];
        if (action === "remove") {
          code.assignedUser = null;
          writeCodes(state);
          render();
          return;
        }
        if (action === "delete") {
          state.codes.splice(idx, 1);
          writeCodes(state);
          render();
        }
      });
    }

    render();
  }

  document.addEventListener("DOMContentLoaded", function () {
    initSignupPage();
    initJoinStudentPage();
    initStudentWelcomePage();
    initTeacherCodesPage();
  });
})();

