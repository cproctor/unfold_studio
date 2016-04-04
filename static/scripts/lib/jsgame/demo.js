// Create the game object and say hello.
var demoGame = new JSGame('#game');
demoGame.print("Welcome to a demo of the JSGame library. It's pretty easy to use!");
var places_to_go = ["Go outside", "Go to loft", "Go into horse stall"];

// Try to load a saved game. Otherwise, set up a new game.
var loadedSavedGame = demoGame.load();
if (loadedSavedGame) {
    demoGame.print("*** Loaded your saved game ***");
    var place = demoGame.state.location;
    demoGame.print("You are a " + demoGame.state.role + " and you are " + place);
} else {
    demoGame.state.location = "in a dusty barn";
    demoGame.state.inventory = [];
}

// If the player hasn't chosen a role, let her do so.
// Once this is done, 
if (demoGame.state.role === undefined) {
    var roles = ["Farmer", "Farmhand", "Cow", "Mouse"];
    demoGame.print("Who would you like to be?");
    demoGame.wait_for_text(roles)
        .then(function(chosen_role) {
            demoGame.state.role = chosen_role;
            demoGame.save();
            go_somewhere("Go to barn");
        });
} else {
    go_somewhere();
}

// Take the player somewhere. The last thing this function does is wait for text 
// and say once the text is entered, we should go somewhere again--this will
// create an infinite loop so the game never ends.
function go_somewhere(where_to_go) {
    if (where_to_go == "Go outside") {
        demoGame.state.location = "outside";
        demoGame.print("You are outside!");
    } else if (where_to_go == "Go to barn") {
        demoGame.state.location = "Go to barn";
        demoGame.print("You are in a dusty barn.");
    } else if (where_to_go == "Go to loft") {
        demoGame.state.location = "in the hayloft";
        demoGame.print("You are high in the hayloft.");
    } else if (where_to_go == "Go into horse stall") {
        demoGame.state.location = "in the horse stall";
        demoGame.state.inventory.push("pitchfork");
        demoGame.print("You are in a dirty horse stall. You found a pitchfork.");
    } else if (where_to_go == "Inventory") {
        if (demoGame.state.inventory.length == 0) {
            demoGame.print("You have nothing at all!");
        } else {
            demoGame.print("You have: " + demoGame.state.inventory.join(', '));
        }
    }
    demoGame.save();
    demoGame.print("Where to now?")
    demoGame.wait_for_text(_.union(places_to_go, ["Inventory"])).then(go_somewhere);
}


