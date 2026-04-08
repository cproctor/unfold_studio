
// Defines the top-level App for front-end story editing and playing

define(
    [
        'jquery',
        'lib/inky/util', 
        'lib/inky/split', 
        'lib/inky/editorView', 
        'lib/inky/playerView',
        'lib/inky/toolbarView',
        'lib/inky/expressionWatchView',
        'lib/inky/inkProject',
        'lib/inky/navHistory',
        'story',
        'player'
    ], 
    function(
        $,
        util, 
        split, 
        EditorView, 
        PlayerView, 
        ToolbarView, 
        ExpressionWatchView, 
        InkProject,
        NavHistory,
        Story,
        InkPlayer
    ) {

    return {
        init: function() {
            const player = new InkPlayer('.innerText');

            // parse errors from story object for use with ace editor
            // returns list of error objects
            function parseErrors(storyObj) {
                // Successful compiles send error: ""; "".split("\n") is [""] — feeding that into Ace
                // produced NaN row markers and broke the editor/player.
                if (!storyObj.error || !String(storyObj.error).trim()) {
                    return [];
                }
                const errList = [];
                for (let err of String(storyObj.error).split("\n")) {
                    err = err.trim();
                    if (!err) {
                        continue;
                    }
                    let lineNumber = null;
                    const lineMatch = err.match(/line\s+(\d+)/i);
                    if (lineMatch) {
                        lineNumber = parseInt(lineMatch[1], 10);
                    } else {
                        const colon = err.indexOf(":");
                        if (colon > 0) {
                            const ch = err[colon - 1];
                            if (/^\d$/.test(ch)) {
                                lineNumber = parseInt(ch, 10);
                            }
                        }
                    }
                    if (!lineNumber || lineNumber < 1 || !Number.isFinite(lineNumber)) {
                        continue;
                    }
                    const msgAt = err.lastIndexOf(":");
                    const message = msgAt >= 0 ? err.slice(msgAt + 1).trim() : err;
                    errList.push({ lineNumber: lineNumber, message: message || err });
                }
                return errList;
            }

            function draftStorageKey() {
                return "unfold_story_draft_" + STORY_ID;
            }

            function normalizeInk(s) {
                if (s === null || s === undefined) {
                    return "";
                }
                return String(s);
            }

            function readDraftBackup() {
                // Storage strategy (anonymous drafts):
                // - DB is the source of truth for explicit saves (POST /stories/<id>/compile/).
                // - Django session (via sessionid cookie) tracks which anonymous drafts the current
                //   browser session owns (anonymous_owned_story_ids).
                // - sessionStorage is only a temporary client-side backup for crash/refresh recovery
                //   within this same browser session. It is NOT the primary persistence mechanism.
                if (typeof window.DRAFT_LOCAL_BACKUP === "undefined" || !window.DRAFT_LOCAL_BACKUP) {
                    return null;
                }
                try {
                    var raw = sessionStorage.getItem(draftStorageKey());
                    if (!raw) {
                        return null;
                    }
                    return JSON.parse(raw);
                } catch (e) {
                    return null;
                }
            }

            /**
             * Persist ace text + the server revision (edit_date_ms) and server ink snapshot
             * that this text was typed on top of.
             *
             * This is a backup-only mechanism for anonymous drafts in the current browser session.
             * It helps recover unsaved typing after a refresh/crash, but explicit saves still go to
             * the server (compile_story -> story.save()) and the DB remains the source of truth.
             */
            function writeDraftBackup(storyObj) {
                if (typeof window.DRAFT_LOCAL_BACKUP === "undefined" || !window.DRAFT_LOCAL_BACKUP) {
                    return;
                }
                try {
                    var ink = storyObj.getAceValue();
                    var payload = {
                        ink: ink,
                        lastKnownServerEditMs: storyObj._serverEditMs != null ? storyObj._serverEditMs : 0,
                        lastKnownServerInk: storyObj._serverInk != null ? storyObj._serverInk : "",
                    };
                    sessionStorage.setItem(draftStorageKey(), JSON.stringify(payload));
                } catch (e) {}
            }

            function clearDraftBackup() {
                try {
                    sessionStorage.removeItem(draftStorageKey());
                } catch (e) {}
            }

            /**
             * If sessionStorage has a draft for the same server revision (edit_date_ms) as the
             * fetched story, and ace text differs from the last known server ink, apply the
             * draft (unsaved typing). If the server revision advanced, discard draft.
             */
            function mergeDraftIntoStory(story) {
                if (typeof window.DRAFT_LOCAL_BACKUP === "undefined" || !window.DRAFT_LOCAL_BACKUP) {
                    return;
                }
                var serverInk = normalizeInk(story._serverInk !== undefined ? story._serverInk : story.ink);
                var serverEditMs = story._serverEditMs != null ? Number(story._serverEditMs) : 0;
                var backup = readDraftBackup();
                if (!backup) {
                    return;
                }
                var bInk = normalizeInk(backup.ink);
                var bMs = backup.lastKnownServerEditMs != null ? Number(backup.lastKnownServerEditMs) : null;

                if (bMs !== null && bMs !== serverEditMs) {
                    clearDraftBackup();
                    return;
                }
                if (bMs === null) {
                    if (bInk !== serverInk) {
                        story.setAceValue(backup.ink);
                        story.ink = backup.ink;
                    } else {
                        clearDraftBackup();
                    }
                    return;
                }
                if (bInk !== serverInk) {
                    story.setAceValue(backup.ink);
                    story.ink = backup.ink;
                }
            }

            var draftDebounceTimer = null;
            function attachDraftBackupListeners(storyObj) {
                if (typeof window.DRAFT_LOCAL_BACKUP === "undefined" || !window.DRAFT_LOCAL_BACKUP) {
                    return;
                }
                if (storyObj._draftBackupListenersAttached) {
                    return;
                }
                storyObj._draftBackupListenersAttached = true;
                var sess = storyObj.getAceSession();
                sess.on("change", function() {
                    if (draftDebounceTimer) {
                        clearTimeout(draftDebounceTimer);
                    }
                    draftDebounceTimer = setTimeout(function() {
                        writeDraftBackup(storyObj);
                    }, 250);
                });
            }

            Story.setEvents({
                newStory: function(story) {
                },
                storyFetched: function(story) {
                    mergeDraftIntoStory(story);
                    EditorView.showStory(story);
                    EditorView.setEnabled(EDITABLE);
                    EditorView.setErrors(parseErrors(story));
                    attachDraftBackupListeners(story);
                    writeDraftBackup(story);
                    player.play(story);
                },
                storySaved: function(story) {
                    clearDraftBackup();
                    EditorView.showStory(story);
                    EditorView.setEnabled(EDITABLE);
                    EditorView.setErrors(parseErrors(story));
                    player.play(story);
                }
            });

            $(function() {
                story = new Story(STORY_ID);
                story.fetch().then(function() {
                    if (story.status === "error") {
                        $('.twopane.solo').removeClass('solo');
                        $('#show_code_opt').hide();
                        $('#hide_code_opt').show();
                    }
                })

                // A function which blocks until a story is saved. Useful to bind
                // to actions like "share" which potentially fail to save the story.
                async function presave_story() {
                    await story.save();
                }

                // Don't autosave on beforeunload: the XHR is commonly canceled by navigation,
                // which triggers a noisy "Save failed" alert. Explicit Save and other actions
                // (rename/share/version) already presave.

                if (typeof window.DRAFT_LOCAL_BACKUP !== "undefined" && window.DRAFT_LOCAL_BACKUP) {
                    setInterval(function() {
                        writeDraftBackup(story);
                    }, 4000);
                    window.addEventListener("beforeunload", function() {
                        writeDraftBackup(story);
                    });
                }

                $('#save_story').click(function() {
                    story.save();
                    return false;
                });

                $('#edit_story').click(presave_story);
                $('#share_story').click(presave_story);
                $('#unshare_story').click(presave_story);
                $('#save_version').click(presave_story);

                $('#replay_story').click(function() {
                    player.stop();
                    player.play(story, '.innerText');
                    return false;
                });
                $('#show_code').click(function() {
                    $('.twopane.solo').removeClass('solo');
                    $('#show_code_opt').hide();
                    $('#hide_code_opt').show();
                    return false;
                });
                $('#hide_code').click(function() {
                    $('.twopane').addClass('solo');
                    $('#show_code_opt').show();
                    $('#hide_code_opt').hide();
                    return false;
                });
            });

            // Mutation observer to update async generate calls
            const targetNode = document.getElementById("player");
            const config = {
                attributes: false,
                childList: true,
                subtree: true,
            };
            const callback = (mutationList, observer) => {
                for (const mutation of mutationList) {
                    if (
                        mutation.type === "childList" &&
                        mutation.addedNodes.length > 0
                    ) {
                        mutation.addedNodes.forEach((addedNode) => {
                            if (addedNode.querySelector) {
                                const spans = addedNode.querySelectorAll(
                                    "span[data-loaded=false]",
                                );
                                const generated = JSON.parse(
                                    sessionStorage.getItem("generated"),
                                );
                                spans.forEach((s) => {
                                    s.innerHTML =
                                        generated[s.id] ?? "Loading...";
                                });
                            }
                        });
                    }
                }
            };
            const observer = new MutationObserver(callback);
            observer.observe(targetNode, config);
        },
        
        originalInit: function() {

// SET EVENTS MAPS RELATIONSHIPS BETWEEN ALL THE PARTS
InkProject.setEvents({
    "newProject": (project) => {
        EditorView.focus();
        LiveCompiler.setProject(project);

        var filename = project.activeInkFile.filename();
        ToolbarView.setTitle(filename);
        remote.getCurrentWindow().setTitle(filename);
        NavView.setMainInkFilename(filename);
        NavHistory.reset();
        NavHistory.addStep();
    },
    "didSave": () => {
        var activeInk = InkProject.currentProject.activeInkFile;
        ToolbarView.setTitle(activeInk.filename());
        NavView.setMainInkFilename(InkProject.currentProject.mainInk.filename());
        NavView.highlightRelativePath(activeInk.relativePath());
    },
    "didSwitchToInkFile": (inkFile) => {
        var filename = inkFile.filename();
        ToolbarView.setTitle(filename);
        remote.getCurrentWindow().setTitle(filename);
        NavView.highlightRelativePath(inkFile.relativePath());
        var fileIssues = LiveCompiler.getIssuesForFilename(inkFile.relativePath());
        setImmediate(() => EditorView.setErrors(fileIssues));
        NavHistory.addStep();
    }
});

// Wait for DOM to be ready before kicking most stuff off
// (some of the views get confused otherwise)
$(document).ready(() => {
    if( InkProject.currentProject == null ) {
        InkProject.startNew();
    }
});

function gotoIssue(issue) {
    InkProject.currentProject.showInkFile(issue.filename);
    EditorView.gotoLine(issue.lineNumber);
    NavHistory.addStep();
}

NavHistory.setEvents({
    goto: (location) => {
        InkProject.currentProject.showInkFile(location.filePath);
        EditorView.gotoLine(location.position.row+1);
    }
})


LiveCompiler.setEvents({
    resetting: (sessionId) => {
        EditorView.clearErrors();
        ToolbarView.clearIssueSummary();
        PlayerView.prepareForNewPlaythrough(sessionId);
    },
    selectIssue: gotoIssue,
    textAdded: (text) => {
        PlayerView.addTextSection(text);
    },
    tagsAdded: (tags) => {
        PlayerView.addTags(tags);
    },
    choiceAdded: (choice, isLatestTurn) => {
        if( isLatestTurn ) {
            PlayerView.addChoice(choice, () => {
                LiveCompiler.choose(choice)
            });
        }
    },
    errorsAdded: (errors) => {
        for(var i=0; i<errors.length; i++) {
            var error = errors[i];
            if( error.filename == InkProject.currentProject.activeInkFile.relativePath() )
                EditorView.addError(error);

            if( error.type == "RUNTIME ERROR" )
                PlayerView.addLineError(error, () => gotoIssue(error));
        }

        ToolbarView.updateIssueSummary(errors);
    },
    playerPrompt: (replaying, doneCallback) => {

        var expressionIdx = 0;
        var tryEvaluateNextExpression = () => {

            // Finished evaluating expressions? End of this turn.
            if( expressionIdx >= ExpressionWatchView.numberOfExpressions() ) {
                if( replaying ) {
                    PlayerView.addHorizontalDivider();
                } else {
                    PlayerView.contentReady();
                }
                doneCallback();
                return;
            }

            // Try to evaluate this expression
            var exprText = ExpressionWatchView.getExpression(expressionIdx);
            LiveCompiler.evaluateExpression(exprText, (result, error) => {
                PlayerView.addEvaluationResult(result, error);
                expressionIdx++;
                tryEvaluateNextExpression();
            });
        };

        tryEvaluateNextExpression();
    },
    replayComplete: (sessionId) => {
        PlayerView.showSessionView(sessionId);
    },
    storyCompleted: () => {
        PlayerView.addTerminatingMessage("End of story", "end");
    },
    exitDueToError: () => {
        // No need to do anything - errors themselves being displayed are enough
    },
    unexpectedError: (error) => {
        if( error.indexOf("Unhandled Exception") != -1 ) {
            PlayerView.addTerminatingMessage("Sorry, the ink compiler crashed ☹", "error");
            PlayerView.addTerminatingMessage("Here is some diagnostic information:", "error");

            // Make it a bit less verbose and concentrate on the useful stuff
            // [0x000ea] in /Users/blah/blah/blah/blah/ink/ParsedHierarchy/FlowBase.cs:377
            // After replacement:
            // in FlowBase.cs line 377
            error = error.replace(/\[\w+\] in (?:[\w/]+?)(\w+\.cs):(\d+)/g, "in $1 line $2");

            PlayerView.addLongMessage(error, "diagnostic");
        } else {
            PlayerView.addTerminatingMessage("Ink compiler had an unexpected error ☹", "error");
            PlayerView.addLongMessage(error, "error");
        }
    }
});

EditorView.setEvents({
    "change": () => {
        LiveCompiler.setEdited();
    },
    "jumpToSymbol": (symbolName, contextPos) => {
        var foundSymbol = InkProject.currentProject.findSymbol(symbolName, contextPos);
        if( foundSymbol ) {
            InkProject.currentProject.showInkFile(foundSymbol.inkFile);
            EditorView.gotoLine(foundSymbol.row+1, foundSymbol.column);
            NavHistory.addStep();
        }
    },
    "jumpToInclude": (includePath) => {
        InkProject.currentProject.showInkFile(includePath);
        NavHistory.addStep();
    },
    "navigate": () => NavHistory.addStep()
});

PlayerView.setEvents({
    "jumpToSource": (outputTextOffset) => {
        LiveCompiler.getLocationInSource(outputTextOffset, (result) => {
            if( result && result.filename && result.lineNumber ) {
                InkProject.currentProject.showInkFile(result.filename);
                EditorView.gotoLine(result.lineNumber);
            }
        });
    }
});

ExpressionWatchView.setEvents({
    "change": () => {
        LiveCompiler.setEdited();
        $("#player .scrollContainer").css("top", ExpressionWatchView.totalHeight()+"px");
    }
});

ToolbarView.setEvents({
    toggleSidebar: () => { NavView.toggle(); },
    navigateBack: () => NavHistory.back(),
    navigateForward: () => NavHistory.forward(),
    selectIssue: gotoIssue,
    stepBack: () => {
        PlayerView.previewStepBack();
        LiveCompiler.stepBack();
    },
    rewind:   () => { LiveCompiler.rewind(); }
});

NavView.setEvents({
    clickFileId: (fileId) => {
        var inkFile = InkProject.currentProject.inkFileWithId(fileId);
        InkProject.currentProject.showInkFile(inkFile);
        NavHistory.addStep();
    },
    addInclude: (filename, addToMainInk) => {
        var newInkFile = InkProject.currentProject.addNewInclude(filename, addToMainInk);
        if( newInkFile ) {
            InkProject.currentProject.showInkFile(newInkFile);
            NavHistory.addStep();
            return true;
        }
        return false;
    }
});

/*
GotoAnything.setEvents({
    gotoFile: (file, row) => {
        InkProject.currentProject.showInkFile(file);
        if( typeof row !== 'undefined' )
            EditorView.gotoLine(row+1);
        NavHistory.addStep();
    }
});
*/

        } // END INIT FUNCTION
    } // END RETURN OBJECT
}); // END DEFINE STATEMENT
