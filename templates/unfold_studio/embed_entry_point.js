{% load staticfiles %}{% autoescape off %}

document.LOG_READING_URL = "{% url 'log_reading_event' %}";

require.config({
    baseUrl: "{{ request.scheme }}://{{ request.get_host }}{% static '' %}",
    paths: {
        jquery: 'lib/jquery/jquery-2.2.3.min'
    }

});

define('fetch_story', ['jquery'], function($) {
    return function(story_id) {
        return $.ajax("{{ request.scheme }}://{{ request.get_host }}{% url 'list_stories' %}" + story_id + '/json/');
    }
})

define('story', ['fetch_story'], function(fetch_story) {
    function Story(id, events) {
        if (id) {
            this.events = events;
            this.id = id;
        }
        else {
            Story.events.newStory(this);
        }
    };
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
                Story.events.storyFetched(self);
            })
        }
    }
    Story.setEvents = function(e) {
        Story.events = e;
    }
    return Story;

})

require(["embed"], function(app) {
    app.init();
});
{% endautoescape %}
