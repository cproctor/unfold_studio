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
    this.currentStoryPoint = 0;
    this.aiSeed = null;
    this.generateInProgress = false;
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
        story.BindExternalFunction("SEED_AI", function(seed) {
            this.aiSeed = seed;
            return "";
        }.bind(this));
        story.BindExternalFunction("continue", function(targetKnot) {
            this.currentTargetKnot = targetKnot
            this.scheduleInputBoxForContinue()
            return '';
        }.bind(this));
        story.BindExternalFunction("input", function (placeholder = "Enter text...", variableName) {
            this.scheduleInputBox(placeholder, variableName);
            return '';
        }.bind(this));
        
        
        
        
        // TODO: There is a race condition here: the ajax query is sent off
        // with a callback for when it returns. Meanwhile, a temporary span
        // is created with text "Loading..." and a unique ID. Once the query 
        // returns, the callback looks for the temp div and replaces its content
        // with the LLM-generated text. In all likelihood this will always work 
        // fine, but it is possible that the ajax query could return before 
        // the DOM update, in which case it will not find the span to update. 
        story.BindExternalFunction("generate", function (prompt_text) {
            this.generateInProgress = true;
            return prompt_text;
        }.bind(this));
    },
    play: function(content) {
        this.events.prepareToPlay.bind(this)();
        this.content = content;
        this.aiSeed = null;
        if (content.status != 'ok') {
            this.events.reportError.bind(this)(content.error);
            return 
        } 
        this.story = new inkjs.Story(content.compiled);
        this.bindExternalFunctions(this.story);
        this.running = true;
        this.createStoryPlayInstanceAndContinueStory(content.id);
    },
    generateAndInsertInDOM: async function(prompt_text) {
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
        let loadingSpan = '<span id="' + nonce + '" data-loaded="false">Loading...</span>';
        this.events.addContent.bind(this)({ text: loadingSpan, tags: [] });

        data = await this.api.generate(prompt_text, [], this.aiSeed)

        let generated = JSON.parse(
            sessionStorage.getItem("generated") ?? "{}",
        );
        generated[nonce] = data.result;
        sessionStorage.setItem(
            "generated",
            JSON.stringify(generated),
        );

        let el = document.getElementById(nonce);
        if (el) {
            el.innerHTML = data.result;
        } else {
            console.log("Could not find element " + nonce);
        }

        this.createStoryPlayRecord(this.getStoryPlayInstanceUUID(), "AI_GENERATED_TEXT", data.result);
        this.generateInProgress = false;
    },
    continueStory: async function() {
        const storyPlayInstanceUUID = this.getStoryPlayInstanceUUID();
        const self = this;
        this.events.renderWillStart.bind(this)();
        if (!this.running) {
            return;
        }

        this.story.state.context = [];
        while (this.story.canContinue) { 
            try {
                var text = this.story.Continue()
                var tags = this.story.currentTags.slice()
                if (this.generateInProgress) {
                    await this.generateAndInsertInDOM(text);
                    continue;
                }
                if (tags.includes('context')){
                    this.story.state.context.push(text);
                }
                
                content = { text: text, tags: tags }
                this.events.addContent.bind(this)(content);
                self.createStoryPlayRecord(storyPlayInstanceUUID, "AUTHORS_TEXT", content)
            }
            catch (err) {
                this.events.reportError.bind(this)(err.message);
            }
        }
        if (!this.running) return;
        
        this.events.renderScheduledInputBox.bind(this)();

        const choices = this.story.currentChoices.map(choice => choice.text);
        self.createStoryPlayRecord(storyPlayInstanceUUID, "AUTHORS_CHOICE_LIST", choices)
        if (this.story.currentChoices.length > 0) {
            this.story.currentChoices.forEach(function(choice, i) {
                this.events.addChoice.bind(self)(choice);
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
    createStoryPlayRecord: function(storyPlayInstanceUUID, data_type, data){
        if (
            data === null || 
            data === undefined || 
            (typeof data === "string" && data.trim() === "") || 
            (Array.isArray(data) && data.length === 0)
        ) {
            return;
        }
        this.currentStoryPoint +=1;
        this.api.createStoryPlayRecord(storyPlayInstanceUUID, data_type, data, this.currentStoryPoint);
    },
    createStoryPlayInstanceAndContinueStory: async function(storyID) {
        response = await this.api.createStoryPlayInstance(storyID)
        this.storyPlayInstanceUUID = response.story_play_instance_uuid
        this.continueStory();
    },
    scheduleInputBox: function(placeholder, variableName) {
        const eventHandler = (userInput) => {
            this.story.variablesState[variableName] = userInput;
            this.createStoryPlayRecord(
                this.getStoryPlayInstanceUUID(), 
                "READERS_ENTERED_TEXT", 
                userInput
            );
            this.running = true;
            this.continueStory();
        };
        
        formContainer = this.createInputForm(
            "AUTHORS_INPUT_BOX",
            eventHandler,
            placeholder,
            variableName,
        );
        this.inputBoxToInsert = formContainer;
    },
    scheduleInputBoxForContinue: function(placeholder = "What would you like to do next?") {
        const eventHandler = (userInput) => {
            this.createStoryPlayRecord(
                this.getStoryPlayInstanceUUID(), 
                "READERS_CONTINUE_ENTERED_TEXT", 
                userInput
            );
            this.handleUserInputForContinue(userInput);
        };
    
        formContainer = this.createInputForm(
            "AUTHORS_CONTINUE_INPUT_BOX",
            eventHandler,
            placeholder,
        );
        this.inputBoxToInsert = formContainer;
    },
    createInputForm: function(formType, eventHandler, placeholder, variableName=null) {
        const formContainer = document.createElement("div");
        formContainer.classList.add("input-container");
    
        const formElement = document.createElement("form");
        
        const inputElement = document.createElement("input");
        inputElement.type = "text";
        inputElement.placeholder = placeholder;
        inputElement.required = true;
        
        const buttonElement = document.createElement("button");
        buttonElement.type = "submit";
        buttonElement.innerText = "Submit";
        
        formElement.appendChild(inputElement);
        formElement.appendChild(buttonElement);
    
        formElement.addEventListener("submit", (event) => {
            event.preventDefault();
            const userInput = inputElement.value.trim();
            eventHandler(userInput);
            
            inputElement.disabled = true;
            buttonElement.disabled = true;
            formElement.style.opacity = "0.5";
        });
    
        this.createStoryPlayRecord(
            this.getStoryPlayInstanceUUID(),
            formType,
            {"placeholder": placeholder, "variableName": variableName}
        );
    
        formContainer.appendChild(formElement);

        return formContainer
    },
    handleUserInputForContinue: async function(userInput){
        targetKnotData = this.getKnotData(this.currentTargetKnot);
        response = await this.api.getNextDirection(userInput, this.getStoryPlayInstanceUUID(), targetKnotData)
        nextDirectionJson = response.result

        switch(nextDirectionJson.direction) {
            case 'NEEDS_INPUT':
                content = [{
                    text: nextDirectionJson.content.guidance_text,
                    tags: []
                }]
                content.forEach(this.events.addContent, this);
                this.scheduleInputBoxForContinue();
                this.events.renderScheduledInputBox.bind(this)();
                break;
    
            case 'DIRECT_CONTINUE':
                this.story.ChoosePathString(this.currentTargetKnot);
                this.continueStory();
                break;
            case 'BRIDGE_AND_CONTINUE':
                content = [{
                    text: nextDirectionJson.content.bridge_text,
                    tags: ['bridge']
                }]
                content.forEach(this.events.addContent, this);
                
                this.createStoryPlayRecord(
                    this.getStoryPlayInstanceUUID(),
                    "AI_GENERATED_TEXT",
                    nextDirectionJson.content.bridge_text
                );
                
                this.story.ChoosePathString(this.currentTargetKnot);
                this.continueStory();

                break;
            default:
                console.error("Unexpected direction:", nextDirectionJson);
                break;
        }
    },
    getStoryPlayInstanceUUID: function() {
        return this.storyPlayInstanceUUID;
    },
    getKnotData: function(knotName){
        const savedState = this.story.state.toJson();
        this.story.ChoosePathString(knotName);

        let knotContents = [];
        while (this.story.canContinue) {
            knotContents.push(this.story.Continue());
        }
        let knotChoices = this.story.currentChoices.map(choice => choice.text);

        this.story.state.LoadJson(savedState);
        this.currentTargetKnot = knotName;

        knotData = {
            "knotContents": knotContents,
            "knotChoices": knotChoices,
        }

        return knotData;
    },
    api: {
        // All the api calls below return a Promise, let's keep it consistent for any new calls too

        generate: function(prompt_text, contextArray, aiSeed) {
            const requestData = {
                prompt: prompt_text,
                context_array: contextArray,
                ai_seed: aiSeed,
            };
            
            return $.ajax("/generate", {
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("X-CSRFToken", CSRF);
                },
                method: "POST",
                data: JSON.stringify(requestData),
                contentType: "application/json",
            });
        },

        getNextDirection: function(userInput, storyPlayInstanceUUID, targetKnotData){
            const requestData = {
                "user_input": userInput,
                "story_play_instance_uuid": storyPlayInstanceUUID,
                "target_knot_data": targetKnotData,
            }

            return $.ajax("/get_next_direction", {
                beforeSend: function(xhr) {
                    xhr.setRequestHeader("X-CSRFToken", CSRF);
                },
                method: "POST",
                data: JSON.stringify(requestData),
                contentType: "application/json",
            });
        },

        createStoryPlayInstance: function(storyID){
            const requestData = {
                "story_id": storyID,
            }
            return $.ajax("/story_play_instance/new/", {
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", CSRF);
                },
                method: "POST",
                data: JSON.stringify(requestData),
                contentType: "application/json",
            });
        },

        createStoryPlayRecord: function(storyPlayInstanceUUID, data_type, data, currentStoryPoint){
            const requestData = {
                "story_play_instance_uuid": storyPlayInstanceUUID,
                "data_type": data_type,
                "data": data,
                "story_point": currentStoryPoint,
            }
            return $.ajax("/story_play_record/new/", {
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", CSRF);
                },
                method: "POST",
                data: JSON.stringify(requestData),
                contentType: "application/json",
            })
        }
    },
    events: {
        renderScheduledInputBox: function() {
            if(this.inputBoxToInsert){
                this.container.appendChild(this.inputBoxToInsert);
                this.inputBoxToInsert = null;
            }
        },
        prepareToPlay: function() {
            $(this.container).html('');
            $('.scrollContainer').scrollTop(0);
        },
        addContent: function(content, i) {
            if (content.tags.includes("context")){
                return
            } else if (content.tags.includes("text-me")) {
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
            }
            else {
                var p = document.createElement('p');
                p.classList.add('regular-text')
                p.classList.add('story-content')
                p.innerHTML = content.text;
                this.container.appendChild(p);
                this.timeouts.push(setTimeout(function() { p.classList.add("show") }, 200 * i));
            }
        },
        addChoice: function(choice) {
            var self = this;
            var p = document.createElement('p');
            p.classList.add("choice");
            p.innerHTML = `<a href='#'>${choice.text}</a>`
            this.container.appendChild(p);
            this.timeouts.push(setTimeout(function() { p.classList.add("show") }, 200 * (choice.index+choice.text.length)));
            var a = p.querySelectorAll("a")[0];
            a.addEventListener("click", function(event) {
                event.preventDefault();
                self.events.choose.bind(self)(choice.index);
            })
        },
        choose: function(i) {
            chosen_choice = this.story.currentChoices[i].text
            this.createStoryPlayRecord(this.getStoryPlayInstanceUUID(), "READERS_CHOSEN_CHOICE", chosen_choice)
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
