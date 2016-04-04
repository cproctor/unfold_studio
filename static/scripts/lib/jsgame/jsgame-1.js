// JSGame
// ------
// (c) 2015 Chris Proctor. chris@chrisproctor.net
// This code is provided under the MIT license.

// JSGame defines a JSGame object which makes it easy to write a text-based
// role-playing game. For an example of a game written using JSGame, see demo.js.
// Here are the methods provided by JSGame:
// 
//  - init (Sets up the game. Called automatically on creation)
//  - print (prints a message to the screen)
//  - wait_for_text (gets input from the user)
//  - save (saves the game)
//  - load (loads a saved game). 


// This defines a JSGame object. You can make a new JSGame by using new:
// var game = new JSGame();
function JSGame(target) {
    this.init(target);
}

// Prototypes describe the properties that new copies of an object start
// with. Here, we define the methods that JSGames know how to do.
JSGame.prototype = {

    // Controls how many messages will be shown on the screen at once.
    max_messages: 8,

    // Init is run when a new game is created.
    // Sets up the game space on the page. Make sure 'target' is a valid css 
    // selector such as "#game".
    init: function(target) {
        this.state = {};
        $(target).html(
            '<div id="messages"></div>' + 
            '<div id="buttons"></div>' + 
            '<input type="text" id="input" autocomplete="off">' + 
            '<div id="options"></div>'
        );
        $('#input').keyup(_.bind(this._key_pressed, this)).focus();
    },

    // Prints a message to the screen. If there are too many messages, makes
    // some old messages disappear.
    print: function(message) {
        $('#messages').append('<p>' + message + '</p>');
        var all_messages = $('#messages p');
        if (all_messages.length > this.max_messages) {
            $(all_messages[0]).remove();
        }
    },

    // Puts the game in a waiting-for-text mode. If options is provided, it should
    // be an array of acceptable options. If options is provided, the user will be 
    // limited to the listed options. Otherwise, anything is allowed.
    // The proper way to use this method is to chain it to a "then" call, which should
    // be given a callback to process the text. For example:
    // var parrot = function(speech) {
    //      console.log("Graa! I'm a parrot! " + speech);
    // }
    // game.wait_for_text().then(parrot);
    wait_for_text: function(options) {
        if (this.waiting_for_text && this.waiting_for_text.state() == "pending") {
            throw new Error("Cannot wait for text; still waiting for previous text.");
        }
        this.valid_text_options = options || [];
        var options_html = _.reduce(options, function(html, option) {
            return html + "<li>" + option + "</li>";
        }, "<p>Options</p><ul>") + "</ul>";
        $('#options').html(options_html);            

        this.waiting_for_text = new $.Deferred();
        return this.waiting_for_text;
    },

    // Saves the game (the contents of game.state) in the user's browser. 
    // Anything you want saved should be saved into the game's state property.
    // If you want to be able to save different games, pass a string gameName
    // to identify the name you want to save the game under.
    save: function(gameName) {
        localStorage.setItem(gameName || 'JSGame', JSON.stringify(this.state));
    },

    // Tries to load a saved game into game.state, returning the saved game
    // or false if it didn't work.
    load: function(gameName) {
        try {
            var loaded = JSON.parse(localStorage.getItem(gameName || 'JSGame'));
        } catch(e) {
            console.log("Could not read saved game!");
            var loaded = false;
        }
        if (loaded) {
            this.state = loaded;
            return loaded;
        } 
    },

    // Generally, methods starting with an underscore (like all those below
    // here) are meant for internal use only.
    _key_pressed: function(evt) {
        var key_code = evt.which;
        var text = $('#input').val();
        if (_.any(this.valid_text_options)) {
            var valid = _.contains(this.valid_text_options, text);
        } else {
            var valid = true;
        }
        if (valid) {
            if (key_code == 13) {
                this._accept_text(text);
            } else {
                this._text_is_valid();
            }
        } else {
            this._text_is_not_valid();
        }
    },

    _accept_text: function(text) {
        this.waiting_for_text.resolve(text);
        $('#input').val('').removeClass('valid').removeClass('not-valid');
    },

    _text_is_valid: function() {
        $('#input').addClass('valid').removeClass('not-valid');
    },
    
    _text_is_not_valid: function() {
        $('#input').addClass('not-valid').removeClass('valid');
    }
}
