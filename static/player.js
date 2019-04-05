// inkjs global
define(['jquery'], function($) {

function InkPlayer(containerSelector) {
    this.container = document.querySelectorAll(containerSelector)[0];
    this.timeouts = [];
}

InkPlayer.prototype = {
    play: function(content) {
        this.events.prepareToPlay.bind(this)();
        this.content = content;
        if (content.status != 'ok') {
            this.events.reportError.bind(this)(content.error);
            return 
        } 
        this.story = new inkjs.Story(content.compiled);
        this.running = true;
        this.continueStory();
    },
    continueStory: function() {
        const self = this;
        this.events.renderWillStart.bind(this)();
        if (!this.running) {
            return;
        }
        var text = [];
        while (this.story.canContinue) { 
            try {
                text.push(this.story.Continue());
            }
            catch (err) {
                this.events.reportError.bind(this)(err.message);
            }
        }
        if (!this.running) return;
        text.forEach(this.events.addText, this);
        if (this.story.currentChoices.length > 0) {
            this.story.currentChoices.forEach(function(choice, i) {
                this.events.addChoice.bind(self)(choice, i, text);
            }, this);
            this.events.renderDidEnd.bind(this)();
        }
        else {
            this.logPath();
        }
    },
    stop: function() { 
        this.timeouts.forEach(clearTimeout);
        this.running = false;
    },
    logPath: function() {
        const path = Array.from(this.story.state.turnIndices.keys()).join(';');
        console.log(path);
        return $.ajax(LOG_READING_URL, {
            beforeSend: function(xhr) { 
                xhr.setRequestHeader("X-CSRFToken", CSRF);
            },
            method: 'POST',
            data: {
                'story': parseInt(STORY_ID),
                'path': path
            }
        })
    },
    events: {
        prepareToPlay: function() {
            $(this.container).html('');
            $('.scrollContainer').scrollTop(0);
        },
        addText: function(text, i) {
            var p = document.createElement('p');
            p.innerHTML = text;
            this.container.appendChild(p);
            this.timeouts.push(setTimeout(function() { p.classList.add("show") }, 200 * i));
        },
        addChoice: function(choice, i, text) {
            var self = this;
            var p = document.createElement('p');
            p.classList.add("choice");
            p.innerHTML = `<a href='#'>${choice.text}</a>`
            this.container.appendChild(p);
            this.timeouts.push(setTimeout(function() { p.classList.add("show") }, 200 * (i+text.length)));
            var a = p.querySelectorAll("a")[0];
            a.addEventListener("click", function(event) {
                event.preventDefault();
                self.events.choose.bind(self)(choice.index);
            })
        },
        choose: function(i) {
            this.story.ChooseChoiceIndex(i);
            this.continueStory();
        },
        renderWillStart: function() {
            var existingChoices = this.container.querySelectorAll('p.choice');
            for(var i=0; i<existingChoices.length; i++) {
                var c = existingChoices[i];
                c.parentNode.removeChild(c);
            }
        },
        renderDidEnd: function() {
            var scrollWrapper = $('.scrollContainer');
            var start = scrollWrapper.scrollTop();
            var end = scrollWrapper[0].scrollHeight - scrollWrapper.height()
            var dist = end - start;

            var duration = 300 + 300*dist/100;
            var startTime = null;
            function step(time) {
                if( startTime == null ) startTime = time;
                var t = (time-startTime) / duration;
                var lerp = 3*t*t - 2*t*t*t;
                scrollWrapper.scrollTop(start + lerp*dist);
                if( t < 1 ) requestAnimationFrame(step);
            }
            requestAnimationFrame(step);
        },
        reportError: function(message) {
            this.stop.bind(this)();
            var p = document.createElement('p');
            p.classList.add("error");
            p.innerHTML = message;
            this.container.appendChild(p);
        }
    }
}

return InkPlayer;
})
