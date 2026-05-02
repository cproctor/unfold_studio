/**
 * Feedback terminal on story page (?feedback=1). WHAT BROKE: JS set #story-twopane { bottom: Npx }
 * (N = panel height) to "reserve" space above the fixed dock. That shrunk the editor and left a
 * huge blank band (Ace showed empty area). FIX: only resize the fixed .feedback-terminal height;
 * keep #story-twopane filling #main (CSS bottom:0 !important); panel overlays bottom; dispatch resize.
 */
(function () {
    var terminal = document.getElementById('feedback-terminal');
    if (!terminal) {
        return;
    }

    var storyPane = document.getElementById('story-twopane');
    var footer = document.getElementById('footer');
    var menu = document.getElementById('menu');
    var resizeHandle = document.getElementById('feedback-resize-handle');
    var minimizeBtn = document.getElementById('feedback-minimize');
    var skipBtn = document.getElementById('feedback-skip');
    var feedbackTab = document.getElementById('feedback-tab');
    var historyTab = document.getElementById('feedback-history-tab');
    var mainPanel = document.getElementById('feedback-main-panel');
    var historyPanel = document.getElementById('feedback-history-panel');

    var defaultHeight = parseInt(terminal.getAttribute('data-default-height'), 10) || 250;
    var minHeight = parseInt(terminal.getAttribute('data-min-height'), 10) || 220;
    var lastExpandedHeight = defaultHeight;
    var dragging = false;
    var startY = 0;
    var startHeight = 0;

    function getFooterHeight() {
        return footer ? footer.offsetHeight : 42;
    }

    function getMenuHeight() {
        return menu ? menu.offsetHeight : 44;
    }

    function getCollapsedHeight() {
        var handleHeight = resizeHandle ? resizeHandle.offsetHeight : 10;
        var header = terminal.querySelector('.feedback-terminal-header');
        var headerHeight = header ? header.offsetHeight : 28;
        return handleHeight + headerHeight;
    }

    function getMaxExpandedHeight() {
        return Math.max(minHeight, window.innerHeight - getMenuHeight() - getFooterHeight() - 90);
    }

    function syncFooterOffset() {
        terminal.style.setProperty('--feedback-footer-offset', getFooterHeight() + 'px');
    }

    function applyExpandedHeight(nextHeight) {
        var clampedHeight = Math.max(minHeight, Math.min(nextHeight, getMaxExpandedHeight()));
        terminal.style.height = clampedHeight + 'px'; // do not set story-twopane.bottom — see file header
        lastExpandedHeight = clampedHeight;
    }

    function applyCollapsedHeight() {
        terminal.style.height = 'auto';
        var collapsedHeight = terminal.offsetHeight || getCollapsedHeight();
        terminal.style.height = collapsedHeight + 'px';
    }

    function syncLayout() {
        syncFooterOffset();

        if (terminal.classList.contains('minimized')) {
            applyCollapsedHeight();
        } else {
            applyExpandedHeight(lastExpandedHeight);
        }

        // Clear any legacy inline bottom from older script versions; Ace needs a resize after layout.
        if (storyPane) {
            storyPane.style.removeProperty('bottom');
        }
        window.dispatchEvent(new Event('resize'));
    }

    if (minimizeBtn) {
        minimizeBtn.addEventListener('click', function () {
            terminal.classList.toggle('minimized');
            minimizeBtn.innerHTML = terminal.classList.contains('minimized') ? '&#8963;' : '&#8964;';
            syncLayout();
        });
    }

    if (resizeHandle) {
        resizeHandle.addEventListener('mousedown', function (event) {
            dragging = true;
            startY = event.clientY;
            startHeight = terminal.getBoundingClientRect().height;

            if (terminal.classList.contains('minimized')) {
                terminal.classList.remove('minimized');
                if (minimizeBtn) {
                    minimizeBtn.innerHTML = '&#8964;';
                }
                startHeight = lastExpandedHeight;
            }

            document.body.classList.add('feedback-terminal-resizing');
            event.preventDefault();
        });
    }

    document.addEventListener('mousemove', function (event) {
        if (!dragging) {
            return;
        }

        var nextHeight = startHeight + (startY - event.clientY);
        applyExpandedHeight(nextHeight);
    });

    document.addEventListener('mouseup', function () {
        if (!dragging) {
            return;
        }

        dragging = false;
        document.body.classList.remove('feedback-terminal-resizing');
    });

    window.addEventListener('resize', syncLayout);

    if (skipBtn) {
        skipBtn.addEventListener('click', function () {
            window.history.back();
        });
    }

    function showFeedbackPanel() {
        feedbackTab.classList.add('active');
        historyTab.classList.remove('active');
        mainPanel.classList.remove('is-hidden');
        historyPanel.classList.add('is-hidden');
    }

    function showHistoryPanel() {
        historyTab.classList.add('active');
        feedbackTab.classList.remove('active');
        historyPanel.classList.remove('is-hidden');
        mainPanel.classList.add('is-hidden');
    }

    if (feedbackTab && historyTab && mainPanel && historyPanel) {
        feedbackTab.addEventListener('click', showFeedbackPanel);
        historyTab.addEventListener('click', showHistoryPanel);
    }

    syncLayout();
})();
