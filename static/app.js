
// Defines the top-level App for front-end story editing and playing

define(
    [
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

            Story.setEvents({
                newStory: function(story) {
                },
                storyFetched: function(story) {
                    EditorView.showStory(story);
                    EditorView.setEnabled(EDITABLE);
                    player.play(story);
                },
                storySaved: function(story) {
                    EditorView.showStory(story);
                    EditorView.setEnabled(EDITABLE);
                    player.play(story);
                }
            });

            $(function() {
                story = new Story(STORY_ID);
                story.fetch().then(function() {
                    if (story.status === "error") {
                        console.log("ERROR");
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
