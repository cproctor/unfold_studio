{% load staticfiles %}{% autoescape off %}
require.config({
    baseUrl: "{{ request.scheme }}://{{ request.get_host }}{% static '' %}",
    paths: {
        jquery: 'lib/jquery/jquery-2.2.3.min',
        ace: 'lib/ace_src'
    }

});

define('fetch_story', ['jquery'], function($) {
    return function(story_id) {
        return $.ajax("{% url 'list_stories' %}" + story_id + '/json/');
    }
})

define('save_story', ['jquery'], function($) {
    return function(story) {
        if (story.id) {
            var url = "{% url 'list_stories' %}" + story.id + '/compile/';
        }
        else {
            var url = "{% url 'list_stories' %}new/" 
        }
        return $.ajax(url, {
            beforeSend: function(xhr) { 
                xhr.setRequestHeader("X-CSRFToken", CSRF);
            },
            method: 'POST',
            data: {'ink': story.ink}
        })
    }
})

require(["app"], function(app) {
    app.init();
});
{% endautoescape %}
