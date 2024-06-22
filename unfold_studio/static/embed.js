// Defines the top-level Embed for embedding in external sites

define(
    [
        'story',
        'player'
    ], 
    function(
        Story,
        InkPlayer
    ) {

    return {
        init: function() {

            $(function() {
                $(EMBED_TARGET).append('<div class="scrollContainer"><div class="innerText"></div></div>');
                const player = new InkPlayer('.innerText');

                Story.setEvents({
                    storyFetched: function(story) {
                        player.play(story);
                    },
                });
                story = new Story(STORY_ID);
                story.fetch()
            });
        } // END INIT FUNCTION
    } // END RETURN OBJECT
}); // END DEFINE STATEMENT

