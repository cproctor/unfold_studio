// From inky/app/renderer/editorView.js v0.8.0
// Begin require.js wrapper
define([
    "require", 
    "ace/ace",
    "ace/range",
    "lib/inky/inkCompleter",
    "ace/ext/language_tools"
], function (require) {
// End require.js wrapper

const ace = require('ace/ace'); // Added by CP
const editor = ace.edit("editor");
const Range = ace.require("ace/range").Range;
const TokenIterator = ace.require("ace/token_iterator").TokenIterator;
const language_tools = ace.require("ace/ext/language_tools");
const inkCompleter = require("lib/inky/inkCompleter"); // Modified by CP

var editorMarkers = [];
var editorAnnotations = [];

// Used when reloading files so that cursor doesn't jump back to the top
var savedCursorPos = null;
var savedScrollRow = null;

// Overriden by controller.js
var events = {
    change:         () => {},
    jumpToInclude:  () => {},
    jumpToSymbol:   () => {}
};

editor.setShowPrintMargin(false);
editor.setOptions({
    enableBasicAutocompletion: true,
    enableLiveAutocompletion: true,
});
editor.on("change", () => {
    events.change();
});

// Exclude language_tools.textCompleter but add the Ink completer
editor.completers = editor.completers.filter(
    (completer) => completer !== language_tools.textCompleter);
editor.completers.push(inkCompleter);

// Unfortunately standard jquery events don't work since 
// Ace turns pointer events off
editor.on("click", function(e){

    /* Disabled by CP
    if( e.domEvent.altKey ) {
        tryClickCodeLink(e);
    } else {
        setImmediate(() => events.navigate());
    }
    */
});

function tryClickCodeLink(event) {
    var editor = event.editor;
    var pos = editor.getCursorPosition();
    var searchToken = editor.session.getTokenAt(pos.row, pos.column);

    if( searchToken && searchToken.type == "include.filepath" ) {
        events.jumpToInclude(searchToken.value);
        return;
    }

    if( searchToken && searchToken.type == "divert.target" ) {
        event.preventDefault();
        var targetPath = searchToken.value;
        events.jumpToSymbol(targetPath, pos);
        return;
    }
}

// Unfortunately standard CSS for hover doesn't work in the editor
// since they turn pointer events off.
editor.on("mousemove", function (e) {

    var editor = e.editor;

    // Have to hold down modifier key to jump
    if( e.domEvent.altKey ) {

        var character = editor.renderer.screenToTextCoordinates(e.x, e.y);
        var token = editor.session.getTokenAt(character.row, character.column);
        if( !token )
            return;

        var tokenStartPos = editor.renderer.textToScreenCoordinates(character.row, token.start);
        var tokenEndPos = editor.renderer.textToScreenCoordinates(character.row, token.start + token.value.length);

        const lineHeight = 12;
        if( e.x >= tokenStartPos.pageX && e.x <= tokenEndPos.pageX && e.y >= tokenStartPos.pageY && e.y <= tokenEndPos.pageY+lineHeight) {
            if( token ) {
                if( token.type == "divert.target" || token.type == "include.filepath" ) {
                    editor.renderer.setCursorStyle("pointer");
                    return;
                }
            }
        }
    }
    
    editor.renderer.setCursorStyle("default");
});

function addError(error) {

    var editorErrorType = "error";
    var editorClass = "ace-error";
    if( error.type == "WARNING" ) {
        editorErrorType = "warning";
        editorClass = "ace-warning";
    }
    else if( error.type == "TODO" ) {
        editorErrorType = "information";
        editorClass = 'ace-todo';
    }

    editorAnnotations.push({
        row: error.lineNumber-1,
        column: 0,
        text: error.message,
        type: editorErrorType
    });
    editor.getSession().setAnnotations(editorAnnotations);

    var aceClass = "ace-error";
    var markerId = editor.session.addMarker(
        new Range(error.lineNumber-1, 0, error.lineNumber, 0),
        editorClass, 
        "line",
        false
    );
    editorMarkers.push(markerId);
}

function setErrors(errors) {
    clearErrors();
    errors.forEach(addError);
}

function clearErrors() {

    var editorSession = editor.getSession();
    editorSession.clearAnnotations();
    editorAnnotations = [];

    for(var i=0; i<editorMarkers.length; i++) {
        editorSession.removeMarker(editorMarkers[i]);
    }
    editorMarkers = [];
}

// Changed to AMD by CP
return {
    // New function implemented by CP to support Story instead of InkProject
    // (since we're working with server endpoint instead of file-based ink
    showStory: (story) => {
        editor.setSession(story.getAceSession());
        editor.focus();
    },
    clearErrors: clearErrors,
    setEvents: (e) => { events = e; },
    getValue: () => { return editor.getValue(); },
    setValue: (v) => { editor.setValue(v); },
    gotoLine: (row, col) => { editor.gotoLine(row, col); editor.focus(); },
    addError: addError,
    setErrors: setErrors,
    setFiles: (inkFiles) => {
        inkCompleter.inkFiles = inkFiles;
    },
    showInkFile: (inkFile) => {
        editor.setSession(inkFile.getAceSession());
        editor.focus();
    },
    focus: () => { editor.focus(); },
    saveCursorPos: () => { 
        savedCursorPos = editor.getCursorPosition(); 
        savedScrollRow = editor.getFirstVisibleRow(); 
    },
    restoreCursorPos: () => { 
        if( savedCursorPos ) {
            editor.moveCursorToPosition(savedCursorPos); 
            editor.scrollToRow(savedScrollRow);
        } 
    },
    // New function implemented by CP
    setEnabled: (enabled) => { 
        editor.setReadOnly(!enabled); 
        if (enabled) editor.renderer.showCursor();
        else editor.renderer.hideCursor();
    }
};
// Begin require wrapper
});
// End require wrapper
