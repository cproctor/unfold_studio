// inkjs global
define(['jquery'], function($) {

// Snagged from https://stackoverflow.com/questions/105034/how-do-i-create-a-guid-uuid
function uuid() {
  return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, c =>
    (+c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> +c / 4).toString(16)
  );
}

function InkPlayer(containerSelector) {
    this.container = document.querySelectorAll(containerSelector)[0];
    this.timeouts = [];
}

InkPlayer.prototype = {
    bindExternalFunctions: function(story) {
        story.BindExternalFunction("random", function() {
            return Math.random();
        });
        story.BindExternalFunction("random_integer", function(low, high) {
            return low + Math.floor(Math.random() * (high - low));
        });
        story.BindExternalFunction("ln", function(x) {
            return Math.log(x);
        });
        story.BindExternalFunction("log2", function(x) {
            return Math.log2(x);
        });
        story.BindExternalFunction("round", function(x) {
            return Math.round(x);
        });
        story.BindExternalFunction("floor", function(x) {
            return Math.floor(x);
        });
        story.BindExternalFunction("ceiling", function(x) {
            return Math.ceil(x);
        });
        // TODO: There is a race condition here: the ajax query is sent off
        // with a callback for when it returns. Meanwhile, a temporary span
        // is created with text "Loading..." and a unique ID. Once the query 
        // returns, the callback looks for the temp div and replaces its content
        // with the LLM-generated text. In all likelihood this will always work 
        // fine, but it is possible that the ajax query could return before 
        // the DOM update, in which case it will not find the span to update. 
        story.BindExternalFunction("generate", function (prompt_text) {
            // If the prompt contains a placeholder span, replace it with
            // the appropriate text if possible
            if (prompt_text.includes("data-loaded")) {
                const el = new DOMParser().parseFromString(
                    prompt_text,
                    "text/html",
                );
                let span = el.querySelector("span[data-loaded=false]");
                const id = span.id;
                const generated = JSON.parse(
                    sessionStorage.getItem("generated"),
                );
                if (generated?.[id]) {
                    span.replaceWith(generated[id]);
                    prompt_text = el.firstChild.children[1].innerHTML;
                }
            }
            let nonce = uuid();
            $.ajax("/generate", {
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", CSRF);
                },
                method: "POST",
                data: JSON.stringify({ prompt: prompt_text }),
                contentType: "application/json",
            }).done((data) => {
                let el = document.getElementById(nonce);
                let generated = JSON.parse(
                    sessionStorage.getItem("generated") ?? "{}",
                );
                generated[nonce] = data.result;
                sessionStorage.setItem(
                    "generated",
                    JSON.stringify(generated),
                );
                if (el) {
                    el.innerHTML = data.result;
                } else {
                    console.log("Could not find element " + nonce);
                }
            });
            return '<span id="' + nonce + '" data-loaded=false></span>';
        });
    },
    play: function(content) {
        this.events.prepareToPlay.bind(this)();
        this.content = content;
        if (content.status != 'ok') {
            this.events.reportError.bind(this)(content.error);
            return 
        } 
        this.story = new inkjs.Story(content.compiled);
        this.bindExternalFunctions(this.story);
        this.running = true;
        this.continueStory();
    },
    continueStory: function() {
        const self = this;
        this.events.renderWillStart.bind(this)();
        if (!this.running) {
            return;
        }
        var content = [];
        while (this.story.canContinue) { 
            try {
                var text = this.story.Continue()
                var tags = this.story.currentTags.slice()
                content.push({
                    tags: tags,
                    text: text
                });
            }
            catch (err) {
                this.events.reportError.bind(this)(err.message);
            }
        }
        if (!this.running) return;
        content.forEach(this.events.addContent, this);
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
        /*
        if (window.LOG_READING_URL) {
            const path = Array.from(this.story.state.turnIndices.keys()).join(';');
            console.log(path);
            return $.ajax(window.LOG_READING_URL, {
                beforeSend: function(xhr) { 
                    xhr.setRequestHeader("X-CSRFToken", CSRF);
                },
                method: 'POST',
                data: {
                    'story': parseInt(STORY_ID),
                    'path': path
                }
            })
        }
        */
    },
    events: {
        prepareToPlay: function() {
            $(this.container).html('');
            $('.scrollContainer').scrollTop(0);
        },
        addContent: function(content, i) {
            if (content.tags.includes("text-me")) {
                var wrapper = document.createElement('div')
                wrapper.classList.add('sms')
                wrapper.classList.add('text-me')
                wrapper.classList.add('story-content')
                var p = document.createElement('p');
                p.innerHTML = content.text;
                wrapper.appendChild(p)
                clear = document.createElement('div')
                clear.classList.add('clear')
                this.container.appendChild(wrapper);
                this.container.appendChild(clear);
                this.timeouts.push(setTimeout(function() { wrapper.classList.add("show") }, 200 * i));
            } else if (content.tags.includes("text-them")) {
                var wrapper = document.createElement('div')
                wrapper.classList.add('sms')
                wrapper.classList.add('text-them')
                wrapper.classList.add('story-content')
                var p = document.createElement('p');
                p.innerHTML = content.text;
                wrapper.appendChild(p)
                clear = document.createElement('div')
                clear.classList.add('clear')
                this.container.appendChild(wrapper);
                this.container.appendChild(clear);
                this.timeouts.push(setTimeout(function() { wrapper.classList.add("show") }, 200 * i));
            } else if (content.tags.includes("clear")) {
                var storyText = document.getElementsByClassName('story-content');
                while (storyText[0]) {
                    storyText[0].parentNode.removeChild(storyText[0]);
                }
            } else {
                var p = document.createElement('p');
                p.classList.add('regular-text')
                p.classList.add('story-content')
                p.innerHTML = content.text;
                this.container.appendChild(p);
                this.timeouts.push(setTimeout(function() { p.classList.add("show") }, 200 * i));
            }
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
