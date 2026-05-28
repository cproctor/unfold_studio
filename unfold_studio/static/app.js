
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

            // Map {line, message} error objects from the API to the {lineNumber, message}
            // shape expected by EditorView.setErrors (ACE editor annotation format).
            function mapErrors(story) {
                return (story.errors || []).map(function(e) {
                    return { lineNumber: e.line, message: e.message };
                });
            }

            Story.setEvents({
                newStory: function(story) {
                },
                storyFetched: function(story) {
                    EditorView.showStory(story);
                    EditorView.setEnabled(EDITABLE);
                    EditorView.setErrors(mapErrors(story));
                    player.play(story);
                },
                storySaved: function(story) {
                    EditorView.showStory(story);
                    EditorView.setEnabled(EDITABLE);
                    EditorView.setErrors(mapErrors(story));
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

                // autosave story before refresh/leaving page
                // window.addEventListener('beforeunload', presave_story);

                $('#save_story').click(function() {
                    story.save();
                    return false;
                });

                $('#edit_story').click(presave_story);
                // $('#share_story').click(presave_story);
                // $('#unshare_story').click(presave_story);
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
        }
    }
}); // END DEFINE STATEMENT
