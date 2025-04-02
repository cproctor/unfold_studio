// Fetch and save story are defined in require_entry_point, where server-side templates
// can set needed props

// This roughly follow the implementation of InkFile from Inky, but networked instead of 
// persisted to a local file.

define([
    'ace/ace',
    'lib/inky/ace-ink-mode/ace-ink',
    'fetch_story',
    'save_story'
],
function(ace, InkMode, fetch_story, save_story) {
    const Document = ace.require('ace/document').Document;
    const EditSession = ace.require('ace/edit_session').EditSession;

    function Story(id, events) {
        this.aceDocument = new Document("");
        this.aceSession = null;
        this.includes = []; // Later, we'll model incudes on the backend.
        if (id) {
            this.events = events;
            this.id = id;
        }
        else {
            Story.events.newStory(this);
        }
    }

    Story.prototype = {
        fetch: function() {
            var self = this;
            if (!this.id) throw "Cannot fetch stories without ids";
            return fetch_story(this.id).done(function(data) {
                self.id = data.id;
                self.status = data.status;
                self.ink = data.ink;
                self.compiled = data.compiled;
                self.error = data.error;
                self.error_line = data.error_line;
                self.setAceValue(self.ink);
                Story.events.storyFetched(self);
            })
        },
        save: function() {
            var self = this;
            this.ink = this.getAceValue();
            return save_story(this).done(function(data) {
                self.id = data.id;
                self.status = data.status;
                self.id = data.id;
                self.ink = data.ink;
                self.compiled = data.compiled;
                self.error = data.error;
                self.error_line = data.error_line;
                Story.events.storySaved(self);
            })
        },
        getAceValue: function() {
            return this.aceDocument.getValue();
        },
        setAceValue: function(text) {
            this.aceDocument.setValue(text);
        },
        getAceSession: function() {
            if( this.aceSession == null ) {
                this.aceSession = new EditSession(this.aceDocument, new InkMode());
                this.aceSession.setUseWrapMode(true);
                this.aceSession.setUndoManager(new ace.UndoManager());
            }
            return this.aceSession;
        }
    }

    Story.setEvents = function(e) {
        Story.events = e;
    }

    return Story
})

