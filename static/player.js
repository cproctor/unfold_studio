// inkjs global
define(['jquery'], function($) {

function InkPlayer(content) {
}

InkPlayer.prototype = {
    play: function(content, containerSelector) {
        this.content = content;
        if (content.error) throw "ERROR: " + content.error;
        this.story = new inkjs.Story(content.compiled);
        this.container = document.querySelectorAll(containerSelector)[0];
        $(this.container).html('');
        this.running = true;
        this.timeouts = [];
        this.continueStory();
    },
    continueStory: function() {
        this.events.renderWillStart.bind(this)();
        if (!this.running) return;
        var text = [];
        while (this.story.canContinue) { text.push(this.story.Continue());}
        text.forEach(this.events.addText, this);
        this.story.currentChoices.forEach(this.events.addChoice, this);
        this.events.renderDidEnd.bind(this)();
    },
    stop: function() { 
        this.timeouts.forEach(clearTimeout);
        this.running = false;
    },
    events: {
        addText: function(text, i) {
            var p = document.createElement('p');
            p.innerHTML = text;
            this.container.appendChild(p);
            this.timeouts.push(setTimeout(function() { p.classList.add("show") }, 200 * i));
        },
        addChoice: function(choice, i) {
            var self = this;
            var p = document.createElement('p');
            p.classList.add("choice");
            p.innerHTML = `<a href='#'>${choice.text}</a>`
            this.container.appendChild(choiceParagraphElement);
            this.timeouts.push(setTimeout(function() { p.classList.add("show") }, 200 * i));
            var a = p.querySelectorAll("a")[0];
            choiceAnchorEl.addEventListener("click", function(event) {
                event.preventDefault();
                self.events.choose(choice.index);
            })
        },
        choose: function(i) {
            self.story.ChooseChoiceIndex(choice.index);
            self.continueStory();
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
        }
    }
}

return InkPlayer;
})
