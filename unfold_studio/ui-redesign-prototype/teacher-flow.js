/* Prototype: teacher workflow helpers (jump-to + modals on student list). */
(function () {
  "use strict";

  function normalizeTarget(v) {
    v = v != null ? String(v).trim() : "";
    if (!v) return "";
    // allow users to type without .html
    if (!/\.html(\#.*)?$/i.test(v)) v += ".html";
    return v;
  }

  function initFlowJump() {
    document.querySelectorAll("[data-flow-jump]").forEach(function (wrap) {
      var input = wrap.querySelector("[data-flow-input]");
      var btn = wrap.querySelector("[data-flow-go]");
      if (!input || !btn) return;
      function go() {
        var target = normalizeTarget(input.value);
        if (!target) return;
        window.location.href = target;
      }
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        go();
      });
      input.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          e.preventDefault();
          go();
        }
      });
    });
  }

  function randTempPassword() {
    var chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    var out = "";
    for (var i = 0; i < 6; i++) out += chars[Math.floor(Math.random() * chars.length)];
    return out.slice(0, 2) + "7x" + out.slice(2); // similar vibe to screenshot
  }

  function initTeacherStudentsModals() {
    var root = document.querySelector("[data-teacher-students-proto]");
    if (!root) return;

    var toast = document.getElementById("proto-student-toast");
    var toastMsg = document.getElementById("proto-student-toast-msg");

    var resetDialog = document.getElementById("proto-reset-dialog");
    var resetClose = document.getElementById("proto-reset-close");
    var resetCancel = document.getElementById("proto-reset-cancel");
    var resetGo = document.getElementById("proto-reset-generate");
    var resetStudentName = document.getElementById("proto-reset-student");
    var resetCode = document.getElementById("proto-reset-code");

    var doneDialog = document.getElementById("proto-reset-done");
    var doneClose = document.getElementById("proto-reset-done-close");
    var doneDone = document.getElementById("proto-reset-done-done");
    var doneCopy = document.getElementById("proto-reset-copy");
    var donePass = document.getElementById("proto-reset-pass");

    function open(d) {
      if (d && d.showModal) d.showModal();
    }
    function close(d) {
      if (d && d.close) d.close();
    }

    function showToast(message) {
      if (!toast || !toastMsg) return;
      toastMsg.textContent = message;
      toast.hidden = false;
      window.clearTimeout(showToast._t);
      showToast._t = window.setTimeout(function () {
        toast.hidden = true;
      }, 3500);
    }

    root.addEventListener("click", function (e) {
      var resetBtn = e.target.closest("[data-action='reset']");
      var removeBtn = e.target.closest("[data-action='remove']");
      if (resetBtn) {
        e.preventDefault();
        var tr = resetBtn.closest("tr");
        if (!tr) return;
        var name = tr.getAttribute("data-student") || "Student";
        var code = tr.getAttribute("data-code") || "";
        if (resetStudentName) resetStudentName.textContent = name;
        if (resetCode) resetCode.textContent = code;
        open(resetDialog);
        return;
      }
      if (removeBtn) {
        e.preventDefault();
        var tr2 = removeBtn.closest("tr");
        if (!tr2) return;
        var name2 = tr2.getAttribute("data-student") || "Student";
        var code2 = tr2.getAttribute("data-code") || "";
        tr2.classList.add("is-removed");
        tr2.querySelectorAll("td").forEach(function (td, idx) {
          if (idx === 2) td.textContent = "Removed";
        });
        showToast(name2 + " (" + code2 + ") removed. Access code revoked.");
      }
    });

    if (resetClose) resetClose.addEventListener("click", function () { close(resetDialog); });
    if (resetCancel) resetCancel.addEventListener("click", function () { close(resetDialog); });
    if (resetDialog) {
      resetDialog.addEventListener("click", function (e) {
        if (e.target === resetDialog) close(resetDialog);
      });
    }

    if (resetGo) {
      resetGo.addEventListener("click", function () {
        var pw = randTempPassword();
        if (donePass) donePass.textContent = pw;
        close(resetDialog);
        open(doneDialog);
      });
    }

    function closeDone() {
      close(doneDialog);
    }
    if (doneClose) doneClose.addEventListener("click", closeDone);
    if (doneDone) doneDone.addEventListener("click", closeDone);
    if (doneDialog) {
      doneDialog.addEventListener("click", function (e) {
        if (e.target === doneDialog) closeDone();
      });
    }
    if (doneCopy) {
      doneCopy.addEventListener("click", function () {
        var pw2 = donePass ? donePass.textContent : "";
        if (!pw2) return;
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(pw2).then(
            function () {
              doneCopy.textContent = "Copied!";
              setTimeout(function () { doneCopy.textContent = "Copy Password"; }, 1500);
            },
            function () {
              window.prompt("Copy password:", pw2);
            }
          );
        } else {
          window.prompt("Copy password:", pw2);
        }
      });
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    initFlowJump();
    initTeacherStudentsModals();
  });
})();

