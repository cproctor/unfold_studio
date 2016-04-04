// TODO: Check for "once" flag on choice
// TODO: Check subprocess "string" status to see whether to concatenate result
// TODO: Explicitly handle relative/absolute traverses using leading dot.
// TODO: Never push booleans; use 0 and 1 instead.

var InkInterface = function(ink) {
    this.init(ink)
}

InkInterface.prototype = {
    init: function(ink) {
        this.logs = []
        this.choices = []
        this.root = new InkNode(ink.root, null, this)
    },

    addChoice: function(choice) {
        console.log("ADDING CHOICE: " + JSON.stringify(choice))
        this.choices.push(choice)
    },

    onAsk: function(askFn) {
        this.ask = askFn
    },
    onPrint: function(printFn) {
        this.print = printFn
    },
    run: function(node) {
        var results = (node || this.root).evaluate()

        // Skim off extra glue
        while (typeof _.last(results) == "object" && _.last(results)['<>'] != undefined) {
            results.pop()
        }

        // Print the results
        _.each(results, function(statement) {
                this.print(statement)
        }, this)

        // Ask with the generated options
        if (_.any(this.choices)) {
            this.ask(this.choices)
        }
        this.choices = []
    },
    print: function() {},
    ask: function() {},
}

// ========== INK NODE ===============================
var InkNode = function(nodeObj, parent, interface) {
    this.init(nodeObj, parent, interface)
}
InkNode.prototype = {
    init: function(nodeObj, parentNode, interface) {
        this.parent = parentNode
        this.interface = interface
        this.children = []
        this.visits = 0

        if (nodeObj instanceof Array) { // Array constructor
            this.statements = nodeObj
        } 
        else if (typeof nodeObj === "object" && nodeObj.c instanceof Array) { // Object constructor
            this.statements = nodeObj.c
            this.name = nodeObj.name
            _.each(nodeObj.namedOnly || [], function(childNodeObj) {
                this.addChild(childNodeObj)
            }, this)
        }
        else throw("Error constructing node from " + JSON.stringify(nodeObj))
    },

    addChild: function(childNodeObj, index) {
        var child = new InkNode(childNodeObj, this, this.interface)
        child.index = index
        this.children.push(child)
        return child
    },

    fullName: function() {
        if (this.parent) {
            if (this.parent.fullName() != '') {
                return this.parent.fullName() + '.' + (this.name || this.index)
            }
            else {
                return this.name || '' + this.index
            }
        } else {
            return ''
        }
    },

    // Children can be located by name or by (statement) index.
    getChild: function(id) {
        var namedChild = _.findWhere(this.children, {name: id})
        var indexedChild = _.findWhere(this.children, {index: toInt(id)})
        var indexedStatement = this.statements[toInt(id)]
        return namedChild || indexedChild || indexedStatement
    },

    // Takes an array and returns a node or a statement
    // '^' represents parent; strings name children, 
    // and integers name statements by index. However, integers may name nodes
    // when nodes are dynamically defined by that statement.
    // An empty first item means relative traverse
    traverse: function(path) {
        // Relative paths start with an empty string.
        if (path[0] === "") {
            this.log("Relative traverse. Offsetting as if called from child")
            return this._traverse(_.rest(path, 2)) // ALERT! Relative traversal tries to pop up one too far.
        // Fully-qualified paths 
        } else {
            return this.interface.root._traverse(path)
        }
    },
    _traverse: function(path) {
        if (_.any(path)) {
            this.log("In " + (this.fullName() || "ROOT") + " and traversing path: " + path)
            var token = _.first(path)
            var rest = _.rest(path)
            if (token == "^") {
                if (this.parent) {
                    return this.parent._traverse(rest)
                } else {
                    this.log("traverse failure. no parent.")
                }
            }
            else {
                var child = this.getChild(token)
                if (child instanceof InkNode) {
                    return child._traverse(rest)
                }
                else if (child && !_.any(rest)) { // When child is a statement, can't end recursion there.
                    return child
                }
                else {
                    this.log("traverse failure. no such child.")
                }
            }
        }
        else {
            this.log("traverse success: returning " + this.fullName())
            return this
        }
    },

    // Returns a duplicate (non-ref) of statements.
    getStatements: function() {
        return JSON.parse(JSON.stringify(this.statements))
    },

    evaluate: function() {
        this.process = new InkProcess(this)
        var process = this.process
        console.log("EVALUATING NODE " + this.fullName() || "ROOT")
        var result = process.evaluate(this.getStatements())
        this.visits += 1
        return result
    },
    log: function(message) {
        console.log("==> [" + this.fullName() +'] ' + message)
    },
}

// ========== INK PROCESS ========================
var InkProcess = function(node, parentProcess) {
    this.node = node
    this.parent = parentProcess
    this.stack = []
}

InkProcess.prototype = {
    inSubprocess: false,
 
    // Evaluating a process consists of evaluating individual statements one at a time;
    // if they can be evaluated, their result is pushed onto the stack. If they take 
    // arguments, they are popped from the stack as needed. Once no more statements can
    // be evaluated, the resulting stack state is returned. 
    evaluate: function(statements) {
        this.branches = []
        _.each(statements, function(statement, statementIndex) {
            this.push(statement, statementIndex)
        }, this)

        // Experimental. My theory is that maybe branches have their results concatenated 
        // together at the end...
        _.each(this.branches, function(branchCode) {
            this.log("Evaluating cached branch: " + JSON.stringify(branchCode))
            var branchProcess = new InkProcess(this.node, this)
            this.push(branchProcess.evaluate(branchCode))
        }, this)

        return this.stack
    },   

    push: function(statement, statementIndex) { // Evaluate, then push result

        //if (this.branched) {
            //console.log("BRANCHED; SKIPPING STATEMENT: " + JSON.stringify(statement))
            //return 0
        //}

        console.log("[" + this.node.fullName() + "] EVAL STATEMENT: " + 
                JSON.stringify(statement) + " WITH STACK: " + JSON.stringify(this.stack))

        // GLUE MODE
        if (typeof this.peek() === "object" && this.peek()["<>"] != undefined && 
                (typeof statement === "string" || typeof statement === "number")) { // Are we in Glue Mode?
            if (typeof statement === "string" && !isWhitespace(statement)) { // Can the statement be glued?
                var glue = this.pop() 
                if (this.peek() != undefined) { // If there's anything to glue to
                    var oldString = this.pop()
                    this.push(oldString + statement)
                }
                else { // Put the glue back (maybe we need to pop back up)
                    this.stack.push(glue)
                    this.stack.push(statement)
                }
            }
            else {
                // throw away whitespace
                // and non-strings. This is a hack to get lists to work. Is this a problem?
            }
        }
        // NO-OPs
        else if (statement.cmd == "EvalStart") {
        }
        else if (statement.cmd == "BeginString") {
        }
        else if (statement.cmd == "EvalEnd") {
        }
        else if (statement.cmd == "EndString") {
        }
        else if (statement.cmd == "NoOp") {
        }
        else if (statement.cmd == "Done") {
            this.log("All done ================================")
        }
        else if (statement.cmd == "End") {
            this.log("All done ================================")
        }

        // LITERALS PUSHED WITHOUT INTERPRETATION
        else if (typeof statement === "number") {
            this.stack.push(statement)
        }
        else if (typeof statement === "string") {
            this.stack.push(statement)
        }
        else if (_.contains(["string", "number", "boolean"], typeof statement)) {
            this.stack.push(statement)
        } 

        // DIVERTS
        else if (statement.div) {
            this.log("Evaluating: " + statement.div)
            var path = statement.div.split(".")
            if (statement.push == "func") {
                //path = _.rest(path)
            } 
            var target = this.node.traverse(path)
            if (target instanceof InkNode) { // Traversal can yield either an statement or a node.
                                             // It remains to be seen whether statement traversal 
                                             // means you should execute just that statement, or 
                                             // redirect control flow there. 
                var result = target.evaluate()
                this.log("finished evaluating node; result is: " + JSON.stringify(result))
            }
            else {
                var result = [target]
                this.log("located statement: " + JSON.stringify(result))
            }
            _.each(result, function(statement) { // Idea: Should we continue the current process here?
                this.log("evaluating diverted statement: " + JSON.stringify(statement))
                this.push(statement)
            }, this)
        } 

        // DYNAMICALLY-DEFINED NODES
        else if (isNode(statement)) { // NOT IF IT'S ALREADY THERE
            var newNodePath = (this.node.fullName() ? this.node.fullName() + "." + statementIndex : "" + statementIndex).split(".")
            var possibleExtantChild = this.node.traverse(newNodePath)
            // Possible source of trouble. When statement index is not defined, we're in an ad-hoc 
            // node. Possibly these need to count visits too? In this case, it won't work right now.
            if (statementIndex != undefined && possibleExtantChild instanceof InkNode) {
                this.log("No need to re-instantiate child; already found " + newNodePath.join("."))
                var child = possibleExtantChild
            }
            else {
                this.log("Adding and evaluating a child node")
                var child = this.node.addChild(statement, statementIndex)
            }
            var results = child.evaluate()
            console.log("Finished evaluating child; result is: " + JSON.stringify(results))
            this.evaluate(results)
        } 

        // ADD CHOICES
        else if (statement['%t'] == "Choice") {
            var validChoice = (!statement.cond || this.pop())
                
            var choiceText = ""
            if (statement['[_]'] === true) {
                choiceText = this.pop()
            }
            if (statement['_['] === true) {
                choiceText = this.pop() + choiceText
            }
            var path = statement.path.split(".")
            var choiceNode = this.node.traverse(path)
            if (validChoice) {
                var self = this
                this.node.interface.addChoice({
                    text: choiceText, 
                    fn: function() { 
                        self.node.interface.run(choiceNode) 
                    }
                })
            }
        }

        // BRANCHES
        else if (statement['%t'] == "Branch") {
            if (this.pop()) {
                this.log("pushing a branch for later evaluation: " + JSON.stringify(statement['true']))
                this.branches.push([statement['true']]) // Check: Always just a divert?
                this.branched = true
            }
        }

        // VARIABLE READS
        else if (statement.readCount) {
            var node = this.node.traverse([statement.readCount])
            this.stack.push(node.visits)
        }
        else if (statement.cmd == "VisitIndex") {
            this.log("VisitIndex is " + this.node.visits + "; pushing to stack")
            this.stack.push(this.node.visits)
        }

        // OPERATORS
        else if (statement.cmd == "Duplicate") {
            var value = this.pop()
            this.stack.push(value)
            this.stack.push(value)
        }
        else if (typeof statement == "object" && statement['<>'] != undefined) { // glue concat
            this.stack.push(statement)
        }
        else if (statement.f === "+") {
            var right = this.pop()
            var left = this.pop()
            this.stack.push(left + right)
        }
        else if (statement.f === "-") {
            var right = this.pop()
            var left = this.pop()
            this.stack.push(left - right)
        }
        else if (statement.f === "*") {
            var right = this.pop()
            var left = this.pop()
            this.stack.push(left * right)
        }
        else if (statement.f === "/") {
            var right = this.pop()
            var left = this.pop()
            this.stack.push(left / right)
        }
        else if (statement.f === "%") {
            var right = this.pop()
            var left = this.pop()
            this.stack.push(left % right)
        }
        else if (statement.f === "MAX") {
            this.stack.push(Math.max(this.pop(), this.pop()))
        }
        else if (statement.f === "MIN") {
            this.stack.push(Math.min(this.pop(), this.pop()))
        }
        else if (statement.f === "==") {
            this.stack.push(intBool(this.pop() == this.pop()))
        }
        else if (statement.f === "<") {
            var right = this.pop()
            var left = this.pop()
            this.stack.push(intBool(left < right))
        }
        else if (statement.f === ">") {
            var right = this.pop()
            var left = this.pop()
            this.stack.push(intBool(left > right))
        }

        // ERROR
        else {
            throw("Error: Did not understand statement")
        }
    },
    pop: function() { 
        return this.stack.pop()
    },
    peek: function() {
        return _.last(this.stack)
    },
    log: function(message) {
        console.log("--> [" + this.node.fullName() + "] " + message)
    }
}

// ===============================================================
// HELPERS
// ===============================================================

// There are two valid representations for nodes: 
// 1. They can be arrays. In this case, they have no name and no named children. 
// 2. They can be objects. In this case, their elements are in an array under the key [c] 
//    and their children are in an object under the key [namedOnly]
var isNode = function(obj) {
    return (obj instanceof Array) || (typeof obj === "object" && obj.c instanceof Array)
}

// Strictly converts a string to an int. This function is actually a bit too strict, as it 
// will not succeed with input such as "05" but that's fine for our use in this program.
var toInt = function(str) {
    if (str === "" + parseInt(str)) {
        return parseInt(str)
    }
}

// Express a boolean as an int.
var intBool = function(bool) {
    return bool ? 1 : 0
}

var isWhitespace = function(str) {
    return /^\s*$/.test(str)
}














