(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports) :
  typeof define === 'function' && define.amd ? define('inkjs', ['exports'], factory) :
  (factory((global.inkjs = global.inkjs || {})));
}(this, function (exports) { 'use strict';

  var babelHelpers = {};
  babelHelpers.typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) {
    return typeof obj;
  } : function (obj) {
    return obj && typeof Symbol === "function" && obj.constructor === Symbol ? "symbol" : typeof obj;
  };

  babelHelpers.classCallCheck = function (instance, Constructor) {
    if (!(instance instanceof Constructor)) {
      throw new TypeError("Cannot call a class as a function");
    }
  };

  babelHelpers.createClass = function () {
    function defineProperties(target, props) {
      for (var i = 0; i < props.length; i++) {
        var descriptor = props[i];
        descriptor.enumerable = descriptor.enumerable || false;
        descriptor.configurable = true;
        if ("value" in descriptor) descriptor.writable = true;
        Object.defineProperty(target, descriptor.key, descriptor);
      }
    }

    return function (Constructor, protoProps, staticProps) {
      if (protoProps) defineProperties(Constructor.prototype, protoProps);
      if (staticProps) defineProperties(Constructor, staticProps);
      return Constructor;
    };
  }();

  babelHelpers.extends = Object.assign || function (target) {
    for (var i = 1; i < arguments.length; i++) {
      var source = arguments[i];

      for (var key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
          target[key] = source[key];
        }
      }
    }

    return target;
  };

  babelHelpers.inherits = function (subClass, superClass) {
    if (typeof superClass !== "function" && superClass !== null) {
      throw new TypeError("Super expression must either be null or a function, not " + typeof superClass);
    }

    subClass.prototype = Object.create(superClass && superClass.prototype, {
      constructor: {
        value: subClass,
        enumerable: false,
        writable: true,
        configurable: true
      }
    });
    if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass;
  };

  babelHelpers.possibleConstructorReturn = function (self, call) {
    if (!self) {
      throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
    }

    return call && (typeof call === "object" || typeof call === "function") ? call : self;
  };

  babelHelpers;

  var Path$1 = function () {
  	function Path() /*polymorphic constructor*/{
  		babelHelpers.classCallCheck(this, Path);

  		this._isRelative;
  		this._components = [];

  		if (typeof arguments[0] == 'string') {
  			this.componentsString = arguments[0];
  		} else if (arguments[0] instanceof Component && arguments[1] instanceof Path) {
  			this._components.push(arguments[0]);
  			this._components = this._components.concat(arguments[1]);
  		} else if (arguments[0] instanceof Array) {
  			this._components = this._components.concat(arguments[0]);
  			this._isRelative = !!arguments[1];
  		}
  	}

  	babelHelpers.createClass(Path, [{
  		key: "PathByAppendingPath",
  		value: function PathByAppendingPath(pathToAppend) {
  			var p = new Path();

  			var upwardMoves = 0;
  			for (var i = 0; i < pathToAppend.components.length; ++i) {
  				if (pathToAppend.components[i].isParent) {
  					upwardMoves++;
  				} else {
  					break;
  				}
  			}

  			for (var i = 0; i < this.components.length - upwardMoves; ++i) {
  				p.components.push(this.components[i]);
  			}

  			for (var i = upwardMoves; i < pathToAppend.components.length; ++i) {
  				p.components.push(pathToAppend.components[i]);
  			}

  			return p;
  		}
  	}, {
  		key: "toString",
  		value: function toString() {
  			return this.componentsString;
  		}
  	}, {
  		key: "Equals",
  		value: function Equals(otherPath) {
  			if (otherPath == null) return false;

  			if (otherPath.components.length != this.components.length) return false;

  			if (otherPath.isRelative != this.isRelative) return false;

  			//the original code uses SequenceEqual here, so we need to iterate over the components manually.
  			for (var i = 0, l = otherPath.components.length; i < l; i++) {
  				//it's not quite clear whether this test should use Equals or a simple == operator, see https://github.com/y-lohse/inkjs/issues/22
  				if (!otherPath.components[i].Equals(this.components[i])) return false;
  			}

  			return true;
  		}
  	}, {
  		key: "isRelative",
  		get: function get() {
  			return this._isRelative;
  		}
  	}, {
  		key: "components",
  		get: function get() {
  			return this._components;
  		}
  	}, {
  		key: "head",
  		get: function get() {
  			if (this.components.length > 0) {
  				return this.components[0];
  			} else {
  				return null;
  			}
  		}
  	}, {
  		key: "tail",
  		get: function get() {
  			if (this.components.length >= 2) {
  				var tailComps = this.components.slice(1, this.components.length); //careful, the original code uses length-1 here. This is because the second argument of List.GetRange is a number of elements to extract, wherease Array.slice uses an index
  				return new Path(tailComps);
  			} else {
  				return Path.self;
  			}
  		}
  	}, {
  		key: "length",
  		get: function get() {
  			return this.components.length;
  		}
  	}, {
  		key: "lastComponent",
  		get: function get() {
  			if (this.components.length > 0) {
  				return this.components[this.components.length - 1];
  			} else {
  				return null;
  			}
  		}
  	}, {
  		key: "containsNamedComponent",
  		get: function get() {
  			for (var i = 0, l = this.components.length; i < l; i++) {
  				if (!this.components[i].isIndex) {
  					return true;
  				}
  			}
  			return false;
  		}
  	}, {
  		key: "componentsString",
  		get: function get() {
  			var compsStr = this.components.join(".");
  			if (this.isRelative) return "." + compsStr;else return compsStr;
  		},
  		set: function set(value) {
  			var _this = this;

  			this.components.length = 0;

  			var componentsStr = value;

  			if (componentsStr == null || componentsStr == '') return;

  			// When components start with ".", it indicates a relative path, e.g.
  			//   .^.^.hello.5
  			// is equivalent to file system style path:
  			//  ../../hello/5
  			if (componentsStr[0] == '.') {
  				this._isRelative = true;
  				componentsStr = componentsStr.substring(1);
  			}

  			var componentStrings = componentsStr.split('.');
  			componentStrings.forEach(function (str) {
  				if (!isNaN(parseInt(str))) {
  					_this.components.push(new Component(parseInt(str)));
  				} else {
  					_this.components.push(new Component(str));
  				}
  			});
  		}
  	}], [{
  		key: "self",
  		get: function get() {
  			var path = new Path();
  			path._isRelative = true;
  			return path;
  		}
  	}]);
  	return Path;
  }();

  var Component = function () {
  	function Component(indexOrName) {
  		babelHelpers.classCallCheck(this, Component);

  		if (typeof indexOrName == 'string') {
  			this._index = -1;
  			this._name = indexOrName;
  		} else {
  			this._index = parseInt(indexOrName);
  			this._name = null;
  		}
  	}

  	babelHelpers.createClass(Component, [{
  		key: "toString",
  		value: function toString() {
  			if (this.isIndex) {
  				return this.index.toString();
  			} else {
  				return this.name;
  			}
  		}
  	}, {
  		key: "Equals",
  		value: function Equals(otherComp) {
  			if (otherComp != null && otherComp.isIndex == this.isIndex) {
  				if (this.isIndex) {
  					return this.index == otherComp.index;
  				} else {
  					return this.name == otherComp.name;
  				}
  			}

  			return false;
  		}
  	}, {
  		key: "index",
  		get: function get() {
  			return this._index;
  		}
  	}, {
  		key: "name",
  		get: function get() {
  			return this._name;
  		}
  	}, {
  		key: "isIndex",
  		get: function get() {
  			return this.index >= 0;
  		}
  	}, {
  		key: "isParent",
  		get: function get() {
  			return this.name == Path$1.parentId;
  		}
  	}], [{
  		key: "ToParent",
  		value: function ToParent() {
  			return new Component(Path$1.parentId);
  		}
  	}]);
  	return Component;
  }();

  Path$1.parentId = "^";
  Path$1.Component = Component;

  var InkObject = function () {
  	function Object() {
  		babelHelpers.classCallCheck(this, Object);

  		this.parent = null;
  		this._path = null;
  	}

  	babelHelpers.createClass(Object, [{
  		key: 'ResolvePath',
  		value: function ResolvePath(path) {
  			if (path.isRelative) {
  				var nearestContainer = this;

  				if (nearestContainer instanceof Container === false) {
  					if (this.parent == null) console.warn("Can't resolve relative path because we don't have a parent");

  					nearestContainer = this.parent;
  					if (nearestContainer.constructor.name !== 'Container') console.warn("Expected parent to be a container");

  					//Debug.Assert (path.components [0].isParent);
  					path = path.tail;
  				}

  				return nearestContainer.ContentAtPath(path);
  			} else {
  				return this.rootContentContainer.ContentAtPath(path);
  			}
  		}
  	}, {
  		key: 'ConvertPathToRelative',
  		value: function ConvertPathToRelative(globalPath) {
  			var ownPath = this.path;

  			var minPathLength = Math.min(globalPath.components.length, ownPath.components.length);
  			var lastSharedPathCompIndex = -1;

  			for (var i = 0; i < minPathLength; ++i) {
  				var ownComp = ownPath.components[i];
  				var otherComp = globalPath.components[i];

  				if (ownComp.Equals(otherComp)) {
  					lastSharedPathCompIndex = i;
  				} else {
  					break;
  				}
  			}

  			// No shared path components, so just use global path
  			if (lastSharedPathCompIndex == -1) return globalPath;

  			var numUpwardsMoves = ownPath.components.length - 1 - lastSharedPathCompIndex;

  			var newPathComps = [];

  			for (var up = 0; up < numUpwardsMoves; ++up) {
  				newPathComps.push(Path$1.Component.ToParent());
  			}for (var down = lastSharedPathCompIndex + 1; down < globalPath.components.length; ++down) {
  				newPathComps.push(globalPath.components[down]);
  			}var relativePath = new Path$1(newPathComps, true);
  			return relativePath;
  		}
  	}, {
  		key: 'CompactPathString',
  		value: function CompactPathString(otherPath) {
  			var globalPathStr = null;
  			var relativePathStr = null;

  			if (otherPath.isRelative) {
  				relativePathStr = otherPath.componentsString;
  				globalPathStr = this.path.PathByAppendingPath(otherPath).componentsString;
  			} else {
  				var relativePath = this.ConvertPathToRelative(otherPath);
  				relativePathStr = relativePath.componentsString;
  				globalPathStr = otherPath.componentsString;
  			}

  			if (relativePathStr.Length < globalPathStr.Length) return relativePathStr;else return globalPathStr;
  		}
  	}, {
  		key: 'Copy',
  		value: function Copy() {
  			throw "Not Implemented";
  		}
  		//SetCHild works slightly diferently in the js implementation. SInce we can't pass an objets property by reference, we instead pass the object and the property string.

  	}, {
  		key: 'SetChild',
  		value: function SetChild(obj, prop, value) {
  			if (obj[prop]) obj[prop] = null;

  			obj[prop] = value;

  			if (obj[prop]) obj[prop].parent = this;
  		}
  	}, {
  		key: 'path',
  		get: function get() {
  			if (this._path == null) {

  				if (this.parent == null) {
  					this._path = new Path$1();
  				} else {
  					// Maintain a Stack so that the order of the components
  					// is reversed when they're added to the Path.
  					// We're iterating up the hierarchy from the leaves/children to the root.
  					var comps = [];

  					var child = this;
  					//				Container container = child.parent as Container;
  					var container = child.parent;

  					while (container instanceof Container) {

  						var namedChild = child;
  						if (namedChild.name && namedChild.hasValidName) {
  							comps.unshift(new Path$1.Component(namedChild.name));
  						} else {
  							comps.unshift(new Path$1.Component(container.content.indexOf(child)));
  						}

  						child = container;
  						//					container = container.parent as Container;
  						container = container.parent;
  					}

  					this._path = new Path$1(comps);
  				}
  			}

  			return this._path;
  		}
  	}, {
  		key: 'rootContentContainer',
  		get: function get() {
  			var ancestor = this;
  			while (ancestor.parent) {
  				ancestor = ancestor.parent;
  			}
  			return ancestor;
  		}
  	}]);
  	return Object;
  }();

  var ValueType = {
  	// Used in coersion
  	Int: 0,
  	Float: 1,
  	String: 2,

  	// Not used for coersion described above
  	DivertTarget: 3,
  	VariablePointer: 4
  };

  var AbstractValue = function (_InkObject) {
  	babelHelpers.inherits(AbstractValue, _InkObject);

  	function AbstractValue(val) {
  		babelHelpers.classCallCheck(this, AbstractValue);

  		var _this = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(AbstractValue).call(this));

  		_this._valueType;
  		_this._isTruthy;
  		_this._valueObject;
  		return _this;
  	}

  	babelHelpers.createClass(AbstractValue, [{
  		key: 'Cast',
  		value: function Cast(newType) {
  			throw "Trying to casting an AbstractValue";
  		}
  	}, {
  		key: 'Copy',
  		value: function Copy(val) {
  			return this.Create(val);
  		}
  	}, {
  		key: 'valueType',
  		get: function get() {
  			return this._valueType;
  		}
  	}, {
  		key: 'isTruthy',
  		get: function get() {
  			return this._isTruthy;
  		}
  	}, {
  		key: 'valueObject',
  		get: function get() {
  			return this._valueObject;
  		}
  	}], [{
  		key: 'Create',
  		value: function Create(val) {
  			// Implicitly convert bools into ints
  			if (typeof val === 'boolean') {
  				var b = !!val;
  				val = b ? 1 : 0;
  			}

  			if (Number.isInteger(Number(val))) {
  				return new IntValue(val);
  			} else if (!isNaN(val)) {
  				return new FloatValue(val);
  			} else if (typeof val === 'string') {
  				return new StringValue(val);
  			} else if (val instanceof Path$1) {
  				return new DivertTargetValue(val);
  			}

  			return null;
  		}
  	}]);
  	return AbstractValue;
  }(InkObject);

  var Value = function (_AbstractValue) {
  	babelHelpers.inherits(Value, _AbstractValue);

  	function Value(val) {
  		babelHelpers.classCallCheck(this, Value);

  		var _this2 = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(Value).call(this));

  		_this2.value = val;
  		return _this2;
  	}

  	babelHelpers.createClass(Value, [{
  		key: 'toString',
  		value: function toString() {
  			return this.value.toString();
  		}
  	}, {
  		key: 'value',
  		get: function get() {
  			return this._value;
  		},
  		set: function set(value) {
  			this._value = value;
  		}
  	}, {
  		key: 'valueObject',
  		get: function get() {
  			return this.value;
  		}
  	}]);
  	return Value;
  }(AbstractValue);

  var IntValue = function (_Value) {
  	babelHelpers.inherits(IntValue, _Value);

  	function IntValue(val) {
  		babelHelpers.classCallCheck(this, IntValue);

  		var _this3 = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(IntValue).call(this, val || 0));

  		_this3._valueType = ValueType.Int;
  		return _this3;
  	}

  	babelHelpers.createClass(IntValue, [{
  		key: 'Cast',
  		value: function Cast(newType) {
  			if (newType == this.valueType) {
  				return this;
  			}

  			if (newType == ValueType.Float) {
  				return new FloatValue(parseFloat(this.value));
  			}

  			if (newType == ValueType.String) {
  				return new StringValue("" + this.value);
  			}

  			throw "Unexpected type cast of Value to new ValueType";
  		}
  	}, {
  		key: 'isTruthy',
  		get: function get() {
  			return this.value != 0;
  		}
  	}, {
  		key: 'valueType',
  		get: function get() {
  			return ValueType.Int;
  		}
  	}]);
  	return IntValue;
  }(Value);

  var FloatValue = function (_Value2) {
  	babelHelpers.inherits(FloatValue, _Value2);

  	function FloatValue(val) {
  		babelHelpers.classCallCheck(this, FloatValue);

  		var _this4 = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(FloatValue).call(this, val || 0.0));

  		_this4._valueType = ValueType.Float;
  		return _this4;
  	}

  	babelHelpers.createClass(FloatValue, [{
  		key: 'Cast',
  		value: function Cast(newType) {
  			if (newType == this.valueType) {
  				return this;
  			}

  			if (newType == ValueType.Int) {
  				return new IntValue(parseInt(this.value));
  			}

  			if (newType == ValueType.String) {
  				return new StringValue("" + this.value);
  			}

  			throw "Unexpected type cast of Value to new ValueType";
  		}
  	}, {
  		key: 'isTruthy',
  		get: function get() {
  			return this._value != 0.0;
  		}
  	}, {
  		key: 'valueType',
  		get: function get() {
  			return ValueType.Float;
  		}
  	}]);
  	return FloatValue;
  }(Value);

  var StringValue = function (_Value3) {
  	babelHelpers.inherits(StringValue, _Value3);

  	function StringValue(val) {
  		babelHelpers.classCallCheck(this, StringValue);

  		var _this5 = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(StringValue).call(this, val || ''));

  		_this5._valueType = ValueType.String;

  		_this5._isNewline = _this5.value == "\n";
  		_this5._isInlineWhitespace = true;

  		_this5.value.split().every(function (c) {
  			if (c != ' ' && c != '\t') {
  				_this5._isInlineWhitespace = false;
  				return false;
  			}

  			return true;
  		});
  		return _this5;
  	}

  	babelHelpers.createClass(StringValue, [{
  		key: 'Cast',
  		value: function Cast(newType) {
  			if (newType == this.valueType) {
  				return this;
  			}

  			if (newType == ValueType.Int) {

  				var parsedInt;
  				if (parsedInt = parseInt(value)) {
  					return new IntValue(parsedInt);
  				} else {
  					return null;
  				}
  			}

  			if (newType == ValueType.Float) {
  				var parsedFloat;
  				if (parsedFloat = parsedFloat(value)) {
  					return new FloatValue(parsedFloat);
  				} else {
  					return null;
  				}
  			}

  			throw "Unexpected type cast of Value to new ValueType";
  		}
  	}, {
  		key: 'valueType',
  		get: function get() {
  			return ValueType.String;
  		}
  	}, {
  		key: 'isTruthy',
  		get: function get() {
  			return this.value.length > 0;
  		}
  	}, {
  		key: 'isNewline',
  		get: function get() {
  			return this._isNewline;
  		}
  	}, {
  		key: 'isInlineWhitespace',
  		get: function get() {
  			return this._isInlineWhitespace;
  		}
  	}, {
  		key: 'isNonWhitespace',
  		get: function get() {
  			return !this.isNewline && !this.isInlineWhitespace;
  		}
  	}]);
  	return StringValue;
  }(Value);

  var DivertTargetValue = function (_Value4) {
  	babelHelpers.inherits(DivertTargetValue, _Value4);

  	function DivertTargetValue(targetPath) {
  		babelHelpers.classCallCheck(this, DivertTargetValue);

  		var _this6 = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(DivertTargetValue).call(this, targetPath));

  		_this6._valueType = ValueType.DivertTarget;
  		return _this6;
  	}

  	babelHelpers.createClass(DivertTargetValue, [{
  		key: 'Cast',
  		value: function Cast(newType) {
  			if (newType == this.valueType) return this;

  			throw "Unexpected type cast of Value to new ValueType";
  		}
  	}, {
  		key: 'toString',
  		value: function toString() {
  			return "DivertTargetValue(" + this.targetPath + ")";
  		}
  	}, {
  		key: 'targetPath',
  		get: function get() {
  			return this.value;
  		},
  		set: function set(value) {
  			this.value = value;
  		}
  	}, {
  		key: 'isTruthy',
  		get: function get() {
  			throw "Shouldn't be checking the truthiness of a divert target";
  		}
  	}]);
  	return DivertTargetValue;
  }(Value);

  var VariablePointerValue = function (_Value5) {
  	babelHelpers.inherits(VariablePointerValue, _Value5);

  	function VariablePointerValue(variableName, contextIndex) {
  		babelHelpers.classCallCheck(this, VariablePointerValue);

  		var _this7 = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(VariablePointerValue).call(this, variableName));

  		_this7._valueType = ValueType.VariablePointer;
  		_this7.contextIndex = typeof contextIndex !== 'undefined' ? contextIndex : -1;
  		return _this7;
  	}

  	babelHelpers.createClass(VariablePointerValue, [{
  		key: 'Cast',
  		value: function Cast(newType) {
  			if (newType == this.valueType) return this;

  			throw "Unexpected type cast of Value to new ValueType";
  		}
  	}, {
  		key: 'toString',
  		value: function toString() {
  			return "VariablePointerValue(" + this.variableName + ")";
  		}
  	}, {
  		key: 'Copy',
  		value: function Copy() {
  			return new VariablePointerValue(this.variableName, this.contextIndex);
  		}
  	}, {
  		key: 'variableName',
  		get: function get() {
  			return this.value;
  		},
  		set: function set(value) {
  			this.value = value;
  		}
  	}, {
  		key: 'isTruthy',
  		get: function get() {
  			throw "Shouldn't be checking the truthiness of a variable pointer";
  		}
  	}]);
  	return VariablePointerValue;
  }(Value);

  var StoryException = function (_Error) {
  	babelHelpers.inherits(StoryException, _Error);

  	function StoryException(message) {
  		babelHelpers.classCallCheck(this, StoryException);

  		var _this = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(StoryException).call(this, message));

  		_this.message = message;
  		_this.name = 'StoryException';
  		return _this;
  	}

  	return StoryException;
  }(Error);

  var StringBuilder = function () {
  	function StringBuilder(str) {
  		babelHelpers.classCallCheck(this, StringBuilder);

  		str = typeof str !== 'undefined' ? str.toString() : '';
  		this._string = str;
  	}

  	babelHelpers.createClass(StringBuilder, [{
  		key: 'Append',
  		value: function Append(str) {
  			this._string += str;
  		}
  	}, {
  		key: 'AppendLine',
  		value: function AppendLine(str) {
  			if (typeof str !== 'undefined') this.Append(str);
  			this._string += "\n";
  		}
  	}, {
  		key: 'AppendFormat',
  		value: function AppendFormat(format) {
  			//taken from http://stackoverflow.com/questions/610406/javascript-equivalent-to-printf-string-format
  			var args = Array.prototype.slice.call(arguments, 1);
  			return format.replace(/{(\d+)}/g, function (match, number) {
  				return typeof args[number] != 'undefined' ? args[number] : match;
  			});
  		}
  	}, {
  		key: 'toString',
  		value: function toString() {
  			return this._string;
  		}
  	}, {
  		key: 'Length',
  		get: function get() {
  			return this._string.length;
  		}
  	}]);
  	return StringBuilder;
  }();

  var Container = function (_InkObject) {
  	babelHelpers.inherits(Container, _InkObject);
  	//also implements INamedContent. Not sure how to do it cleanly in JS.

  	function Container() {
  		babelHelpers.classCallCheck(this, Container);

  		var _this = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(Container).call(this));

  		_this.name = '';

  		_this._content = [];
  		_this.namedContent = {};

  		_this.visitsShouldBeCounted = false;
  		_this.turnIndexShouldBeCounted = false;
  		_this.countingAtStartOnly = false;

  		_this.CountFlags = {
  			Visits: 1,
  			Turns: 2,
  			CountStartOnly: 4
  		};

  		_this._pathToFirstLeafContent = null;
  		return _this;
  	}

  	babelHelpers.createClass(Container, [{
  		key: 'AddContent',
  		value: function AddContent(contentObj) {
  			var _this2 = this;

  			if (contentObj instanceof Array) {
  				contentObj.forEach(function (c) {
  					_this2.AddContent(c);
  				});
  			} else {
  				this._content.push(contentObj);

  				if (contentObj.parent) {
  					throw "content is already in " + contentObj.parent;
  				}

  				contentObj.parent = this;

  				this.TryAddNamedContent(contentObj);
  			}
  		}
  	}, {
  		key: 'TryAddNamedContent',
  		value: function TryAddNamedContent(contentObj) {
  			//so here, in the reference implementation, contentObj is casted to an INamedContent
  			//but here we use js-style duck typing: if it implements the same props as the interface, we treat it as valid
  			if (contentObj.hasValidName && contentObj.name) {
  				this.AddToNamedContentOnly(contentObj);
  			}
  		}
  	}, {
  		key: 'AddToNamedContentOnly',
  		value: function AddToNamedContentOnly(namedContentObj) {
  			if (namedContentObj instanceof InkObject === false) console.warn("Can only add Runtime.Objects to a Runtime.Container");
  			namedContentObj.parent = this;

  			this.namedContent[namedContentObj.name] = namedContentObj;
  		}
  	}, {
  		key: 'ContentAtPath',
  		value: function ContentAtPath(path, partialPathLength) {
  			partialPathLength = typeof partialPathLength !== 'undefined' ? partialPathLength : path.components.length;

  			var currentContainer = this;
  			var currentObj = this;

  			for (var i = 0; i < partialPathLength; ++i) {
  				var comp = path.components[i];
  				if (!(currentContainer instanceof Container)) throw "Path continued, but previous object wasn't a container: " + currentObj;

  				currentObj = currentContainer.ContentWithPathComponent(comp);
  				//			currentContainer = currentObj as Container;
  				currentContainer = currentObj;
  			}

  			return currentObj;
  		}
  	}, {
  		key: 'InsertContent',
  		value: function InsertContent(contentObj, index) {
  			this.content[i] = contentObj;

  			if (contentObj.parent) {
  				throw "content is already in " + contentObj.parent;
  			}

  			contentObj.parent = this;

  			this.TryAddNamedContent(contentObj);
  		}
  	}, {
  		key: 'AddContentsOfContainer',
  		value: function AddContentsOfContainer(otherContainer) {
  			var _this3 = this;

  			this.content = this.content.concat(otherContainer.content);

  			otherContainer.content.forEach(function (obj) {
  				obj.parent = _this3;
  				_this3.TryAddNamedContent(obj);
  			});
  		}
  	}, {
  		key: 'ContentWithPathComponent',
  		value: function ContentWithPathComponent(component) {
  			if (component.isIndex) {

  				if (component.index >= 0 && component.index < this.content.length) {
  					return this.content[component.index];
  				}

  				// When path is out of range, quietly return nil
  				// (useful as we step/increment forwards through content)
  				else {
  						return null;
  					}
  			} else if (component.isParent) {
  				return this.parent;
  			} else {
  				var foundContent = null;
  				if (foundContent = this.namedContent[component.name]) {
  					return foundContent;
  				} else {
  					throw new StoryException("Content '" + component.name + "' not found at path: '" + this.path + "'");
  				}
  			}
  		}
  	}, {
  		key: 'BuildStringOfHierarchy',
  		value: function BuildStringOfHierarchy(sb, indentation, pointedObj) {
  			if (arguments.length == 0) {
  				var sb = new StringBuilder();
  				this.BuildStringOfHierarchy(sb, 0, null);
  				return sb.toString();
  			}

  			function appendIndentation() {
  				var spacesPerIndent = 4;
  				for (var i = 0; i < spacesPerIndent * indentation; ++i) {
  					sb.Append(" ");
  				}
  			}

  			appendIndentation();
  			sb.Append("[");

  			if (this.hasValidName) {
  				sb.AppendFormat(" ({0})", this.name);
  			}

  			if (this == pointedObj) {
  				sb.Append("  <---");
  			}

  			sb.AppendLine();

  			indentation++;

  			for (var i = 0; i < this.content.length; ++i) {

  				var obj = this.content[i];

  				if (obj instanceof Container) {

  					var container = obj;

  					container.BuildStringOfHierarchy(sb, indentation, pointedObj);
  				} else {
  					appendIndentation();
  					if (obj instanceof StringValue) {
  						sb.Append("\"");
  						sb.Append(obj.toString().replace("\n", "\\n"));
  						sb.Append("\"");
  					} else {
  						sb.Append(obj.toString());
  					}
  				}

  				if (i != this.content.length - 1) {
  					sb.Append(",");
  				}

  				if (!(obj instanceof Container) && obj == pointedObj) {
  					sb.Append("  <---");
  				}

  				sb.AppendLine();
  			}

  			var onlyNamed = {};

  			for (var key in this.namedContent) {
  				if (this.content.indexOf(this.namedContent[key]) >= 0) {
  					continue;
  				} else {
  					onlyNamed[key] = this.namedContent[key];
  				}
  			}

  			if (Object.keys(onlyNamed).length > 0) {
  				appendIndentation();
  				sb.AppendLine("-- named: --");

  				for (var key in onlyNamed) {
  					if (!(onlyNamed[key] instanceof Container)) console.warn("Can only print out named Containers");

  					var container = onlyNamed[key];
  					container.BuildStringOfHierarchy(sb, indentation, pointedObj);
  					sb.Append("\n");
  				}
  			}

  			indentation--;

  			appendIndentation();
  			sb.Append("]");
  		}
  	}, {
  		key: 'hasValidName',
  		get: function get() {
  			return this.name != null && this.name.length > 0;
  		}
  	}, {
  		key: 'content',
  		get: function get() {
  			return this._content;
  		},
  		set: function set(value) {
  			this.AddContent(value);
  		}
  	}, {
  		key: 'namedOnlyContent',
  		get: function get() {
  			var namedOnlyContent = {};

  			for (var key in this.namedContent) {
  				namedOnlyContent[key] = this.namedContent[key];
  			}

  			this.content.forEach(function (c) {
  				//			var named = c as INamedContent;
  				var named = c;
  				if (named.name && named.hasValidName) {
  					delete namedOnlyContent[named.name];
  				}
  			});

  			if (namedOnlyContent.length == 0) namedOnlyContent = null;

  			return namedOnlyContent;
  		},
  		set: function set(value) {
  			var existingNamedOnly = this.namedOnlyContent;
  			if (existingNamedOnly != null) {
  				for (var key in existingNamedOnly) {
  					delete this.namedContent[key];
  				}
  			}

  			if (value == null) return;

  			for (var key in value) {
  				//			var named = kvPair.Value as INamedContent;
  				var named = value[key];
  				if (named.name && typeof named.hasValidName !== 'undefined') this.AddToNamedContentOnly(named);
  			}
  		}
  	}, {
  		key: 'countFlags',
  		get: function get() {
  			var flags = 0;
  			if (this.visitsShouldBeCounted) flags |= this.CountFlags.Visits;
  			if (this.turnIndexShouldBeCounted) flags |= this.CountFlags.Turns;
  			if (this.countingAtStartOnly) flags |= this.CountFlags.CountStartOnly;

  			// If we're only storing CountStartOnly, it serves no purpose,
  			// since it's dependent on the other two to be used at all.
  			// (e.g. for setting the fact that *if* a gather or choice's
  			// content is counted, then is should only be counter at the start)
  			// So this is just an optimisation for storage.
  			if (flags == this.CountFlags.CountStartOnly) {
  				flags = 0;
  			}

  			return flags;
  		},
  		set: function set(value) {
  			var flag = value;
  			if ((flag & this.CountFlags.Visits) > 0) this.visitsShouldBeCounted = true;
  			if ((flag & this.CountFlags.Turns) > 0) this.turnIndexShouldBeCounted = true;
  			if ((flag & this.CountFlags.CountStartOnly) > 0) this.countingAtStartOnly = true;
  		}
  	}, {
  		key: 'pathToFirstLeafContent',
  		get: function get() {
  			if (this._pathToFirstLeafContent == null) this._pathToFirstLeafContent = this.path.PathByAppendingPath(this.internalPathToFirstLeafContent);

  			return this._pathToFirstLeafContent;
  		}
  	}, {
  		key: 'internalPathToFirstLeafContent',
  		get: function get() {
  			var path = new Path();
  			var container = this;
  			while (container instanceof Container) {
  				if (container.content.length > 0) {
  					path.components.push(new Path.Component(0));
  					//				container = container.content [0] as Container;
  					container = container.content[0];
  				}
  			}
  			return path;
  		}
  	}]);
  	return Container;
  }(InkObject);

  var Glue = function (_InkObject) {
  	babelHelpers.inherits(Glue, _InkObject);

  	function Glue(type) {
  		babelHelpers.classCallCheck(this, Glue);

  		var _this = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(Glue).call(this));

  		_this.glueType = type;
  		return _this;
  	}

  	babelHelpers.createClass(Glue, [{
  		key: "toString",
  		value: function toString() {
  			switch (this.glueType) {
  				case GlueType.Bidirectional:
  					return "BidirGlue";
  				case GlueType.Left:
  					return "LeftGlue";
  				case GlueType.Right:
  					return "RightGlue";
  			}

  			return "UnexpectedGlueType";
  		}
  	}, {
  		key: "isLeft",
  		get: function get() {
  			return this.glueType == GlueType.Left;
  		}
  	}, {
  		key: "isBi",
  		get: function get() {
  			return this.glueType == GlueType.Bidirectional;
  		}
  	}, {
  		key: "isRight",
  		get: function get() {
  			return this.glueType == GlueType.Right;
  		}
  	}]);
  	return Glue;
  }(InkObject);

  var GlueType = {
  	Bidirectional: 0,
  	Left: 1,
  	Right: 2
  };

  var ControlCommand = function (_InkObject) {
  	babelHelpers.inherits(ControlCommand, _InkObject);

  	function ControlCommand(commandType) {
  		babelHelpers.classCallCheck(this, ControlCommand);

  		var _this = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(ControlCommand).call(this));

  		_this._commandType = typeof commandType != 'undefined' ? commandType : CommandType.NotSet;
  		return _this;
  	}

  	babelHelpers.createClass(ControlCommand, [{
  		key: 'copy',
  		value: function copy() {
  			return new ControlCommand(this.commandType);
  		}
  	}, {
  		key: 'toString',
  		value: function toString() {
  			return this.commandType.toString();
  		}
  	}, {
  		key: 'commandType',
  		get: function get() {
  			return this._commandType;
  		}
  	}], [{
  		key: 'EvalStart',
  		value: function EvalStart() {
  			return new ControlCommand(CommandType.EvalStart);
  		}
  	}, {
  		key: 'EvalOutput',
  		value: function EvalOutput() {
  			return new ControlCommand(CommandType.EvalOutput);
  		}
  	}, {
  		key: 'EvalEnd',
  		value: function EvalEnd() {
  			return new ControlCommand(CommandType.EvalEnd);
  		}
  	}, {
  		key: 'Duplicate',
  		value: function Duplicate() {
  			return new ControlCommand(CommandType.Duplicate);
  		}
  	}, {
  		key: 'PopEvaluatedValue',
  		value: function PopEvaluatedValue() {
  			return new ControlCommand(CommandType.PopEvaluatedValue);
  		}
  	}, {
  		key: 'PopFunction',
  		value: function PopFunction() {
  			return new ControlCommand(CommandType.PopFunction);
  		}
  	}, {
  		key: 'PopTunnel',
  		value: function PopTunnel() {
  			return new ControlCommand(CommandType.PopTunnel);
  		}
  	}, {
  		key: 'BeginString',
  		value: function BeginString() {
  			return new ControlCommand(CommandType.BeginString);
  		}
  	}, {
  		key: 'EndString',
  		value: function EndString() {
  			return new ControlCommand(CommandType.EndString);
  		}
  	}, {
  		key: 'NoOp',
  		value: function NoOp() {
  			return new ControlCommand(CommandType.NoOp);
  		}
  	}, {
  		key: 'ChoiceCount',
  		value: function ChoiceCount() {
  			return new ControlCommand(CommandType.ChoiceCount);
  		}
  	}, {
  		key: 'TurnsSince',
  		value: function TurnsSince() {
  			return new ControlCommand(CommandType.TurnsSince);
  		}
  	}, {
  		key: 'Random',
  		value: function Random() {
  			return new ControlCommand(CommandType.Random);
  		}
  	}, {
  		key: 'SeedRandom',
  		value: function SeedRandom() {
  			return new ControlCommand(CommandType.SeedRandom);
  		}
  	}, {
  		key: 'VisitIndex',
  		value: function VisitIndex() {
  			return new ControlCommand(CommandType.VisitIndex);
  		}
  	}, {
  		key: 'SequenceShuffleIndex',
  		value: function SequenceShuffleIndex() {
  			return new ControlCommand(CommandType.SequenceShuffleIndex);
  		}
  	}, {
  		key: 'StartThread',
  		value: function StartThread() {
  			return new ControlCommand(CommandType.StartThread);
  		}
  	}, {
  		key: 'Done',
  		value: function Done() {
  			return new ControlCommand(CommandType.Done);
  		}
  	}, {
  		key: 'End',
  		value: function End() {
  			return new ControlCommand(CommandType.End);
  		}
  	}]);
  	return ControlCommand;
  }(InkObject);

  var CommandType = {
  	NotSet: -1,
  	EvalStart: 0,
  	EvalOutput: 1,
  	EvalEnd: 2,
  	Duplicate: 3,
  	PopEvaluatedValue: 4,
  	PopFunction: 5,
  	PopTunnel: 6,
  	BeginString: 7,
  	EndString: 8,
  	NoOp: 9,
  	ChoiceCount: 10,
  	TurnsSince: 11,
  	Random: 12,
  	SeedRandom: 13,
  	VisitIndex: 14,
  	SequenceShuffleIndex: 15,
  	StartThread: 16,
  	Done: 17,
  	End: 18
  };
  CommandType.TOTAL_VALUES = Object.keys(CommandType).length - 1; //-1 because NotSet shoudn't count
  ControlCommand.CommandType = CommandType;

  var PushPopType = {
  	Tunnel: 0,
  	Function: 1
  };

  var Divert = function (_InkObject) {
  	babelHelpers.inherits(Divert, _InkObject);

  	function Divert(stackPushType) {
  		babelHelpers.classCallCheck(this, Divert);

  		var _this = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(Divert).call(this));

  		_this._targetPath;
  		_this._targetContent;

  		_this.variableDivertName;
  		_this.pushesToStack;
  		_this.stackPushType;

  		_this.isExternal;
  		_this.isConditional;
  		_this.externalArgs;

  		//actual constructor
  		_this.pushesToStack = false;
  		if (stackPushType) {
  			_this.pushesToStack = true;
  			_this.stackPushType = stackPushType;
  		}
  		return _this;
  	}

  	babelHelpers.createClass(Divert, [{
  		key: 'Equals',
  		value: function Equals(obj) {
  			//		var otherDivert = obj as Divert;
  			var otherDivert = obj;
  			if (otherDivert instanceof Divert) {
  				if (this.hasVariableTarget == otherDivert.hasVariableTarget) {
  					if (this.hasVariableTarget) {
  						return this.variableDivertName == otherDivert.variableDivertName;
  					} else {
  						return this.targetPath.Equals(otherDivert.targetPath);
  					}
  				}
  			}
  			return false;
  		}
  	}, {
  		key: 'toString',
  		value: function toString() {
  			if (this.hasVariableTarget) {
  				return "Divert(variable: " + this.variableDivertName + ")";
  			} else if (this.targetPath == null) {
  				return "Divert(null)";
  			} else {

  				var sb = new StringBuilder();

  				var targetStr = this.targetPath.toString();
  				//			int? targetLineNum = DebugLineNumberOfPath (targetPath);
  				var targetLineNum = null;
  				if (targetLineNum != null) {
  					targetStr = "line " + targetLineNum;
  				}

  				sb.Append("Divert");
  				if (this.pushesToStack) {
  					if (this.stackPushType == PushPopType.Function) {
  						sb.Append(" function");
  					} else {
  						sb.Append(" tunnel");
  					}
  				}

  				sb.Append(" (");
  				sb.Append(targetStr);
  				sb.Append(")");

  				return sb.toString();
  			}
  		}
  	}, {
  		key: 'targetPath',
  		get: function get() {
  			// Resolve any relative paths to global ones as we come across them
  			if (this._targetPath != null && this._targetPath.isRelative) {
  				var targetObj = this.targetContent;
  				if (targetObj) {
  					this._targetPath = targetObj.path;
  				}
  			}

  			return this._targetPath;
  		},
  		set: function set(value) {
  			this._targetPath = value;
  			this._targetContent = null;
  		}
  	}, {
  		key: 'targetContent',
  		get: function get() {
  			if (this._targetContent == null) {
  				this._targetContent = this.ResolvePath(this._targetPath);
  			}

  			return this._targetContent;
  		}
  	}, {
  		key: 'targetPathString',
  		get: function get() {
  			if (this.targetPath == null) return null;

  			return this.CompactPathString(this.targetPath);
  		},
  		set: function set(value) {
  			if (value == null) {
  				this.targetPath = null;
  			} else {
  				this.targetPath = new Path$1(value);
  			}
  		}
  	}, {
  		key: 'hasVariableTarget',
  		get: function get() {
  			return this.variableDivertName != null;
  		}
  	}]);
  	return Divert;
  }(InkObject);

  var ChoicePoint = function (_InkObject) {
  	babelHelpers.inherits(ChoicePoint, _InkObject);

  	function ChoicePoint(onceOnly) {
  		babelHelpers.classCallCheck(this, ChoicePoint);

  		var _this = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(ChoicePoint).call(this));

  		_this._pathOnChoice;
  		_this.hasCondition;
  		_this.hasStartContent;
  		_this.hasChoiceOnlyContent;
  		_this.onceOnly;
  		_this.isInvisibleDefault;

  		_this.onceOnly = !!onceOnly;
  		return _this;
  	}

  	babelHelpers.createClass(ChoicePoint, [{
  		key: 'toString',
  		value: function toString() {
  			//		int? targetLineNum = DebugLineNumberOfPath (pathOnChoice);
  			var targetLineNum = null;
  			var targetString = this.pathOnChoice.toString();

  			if (targetLineNum != null) {
  				targetString = " line " + targetLineNum;
  			}

  			return "Choice: -> " + targetString;
  		}
  	}, {
  		key: 'pathOnChoice',
  		get: function get() {
  			if (this._pathOnChoice != null && this._pathOnChoice.isRelative) {
  				var choiceTargetObj = this.choiceTarget;
  				if (choiceTargetObj) {
  					this._pathOnChoice = choiceTargetObj.path;
  				}
  			}
  			return this._pathOnChoice;
  		},
  		set: function set(value) {
  			this._pathOnChoice = value;
  		}
  	}, {
  		key: 'choiceTarget',
  		get: function get() {
  			//return this.ResolvePath (_pathOnChoice) as Container;
  			return this.ResolvePath(this._pathOnChoice);
  		}
  	}, {
  		key: 'pathStringOnChoice',
  		get: function get() {
  			return this.CompactPathString(this.pathOnChoice);
  		},
  		set: function set(value) {
  			this.pathOnChoice = new Path$1(value);
  		}
  	}, {
  		key: 'flags',
  		get: function get() {
  			var flags = 0;
  			if (this.hasCondition) flags |= 1;
  			if (this.hasStartContent) flags |= 2;
  			if (this.hasChoiceOnlyContent) flags |= 4;
  			if (this.isInvisibleDefault) flags |= 8;
  			if (this.onceOnly) flags |= 16;
  			return flags;
  		},
  		set: function set(value) {
  			this.hasCondition = (value & 1) > 0;
  			this.hasStartContent = (value & 2) > 0;
  			this.hasChoiceOnlyContent = (value & 4) > 0;
  			this.isInvisibleDefault = (value & 8) > 0;
  			this.onceOnly = (value & 16) > 0;
  		}
  	}]);
  	return ChoicePoint;
  }(InkObject);

  var VariableReference = function (_InkObject) {
  	babelHelpers.inherits(VariableReference, _InkObject);

  	function VariableReference(name) {
  		babelHelpers.classCallCheck(this, VariableReference);

  		var _this = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(VariableReference).call(this));

  		_this.name = name;
  		_this.pathForCount;
  		return _this;
  	}

  	babelHelpers.createClass(VariableReference, [{
  		key: 'toString',
  		value: function toString() {
  			if (this.name != null) {
  				return "var(" + this.name + ")";
  			} else {
  				var pathStr = this.pathStringForCount;
  				return "read_count(" + pathStr + ")";
  			}
  		}
  	}, {
  		key: 'containerForCount',
  		get: function get() {
  			return this.ResolvePath(this.pathForCount);
  		}
  	}, {
  		key: 'pathStringForCount',
  		get: function get() {
  			if (this.pathForCount == null) return null;

  			return this.CompactPathString(this.pathForCount);
  		},
  		set: function set(value) {
  			if (value == null) this.pathForCount = null;else this.pathForCount = new Path$1(value);
  		}
  	}]);
  	return VariableReference;
  }(InkObject);

  var VariableAssignment = function (_InkObject) {
  	babelHelpers.inherits(VariableAssignment, _InkObject);

  	function VariableAssignment(variableName, isNewDeclaration) {
  		babelHelpers.classCallCheck(this, VariableAssignment);

  		var _this = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(VariableAssignment).call(this));

  		_this._variableName = variableName || null;
  		_this._isNewDeclaration = !!isNewDeclaration;
  		_this.isGlobal;
  		return _this;
  	}

  	babelHelpers.createClass(VariableAssignment, [{
  		key: "toString",
  		value: function toString() {
  			return "VarAssign to " + this.variableName;;
  		}
  	}, {
  		key: "variableName",
  		get: function get() {
  			return this._variableName;
  		}
  	}, {
  		key: "isNewDeclaration",
  		get: function get() {
  			return this._isNewDeclaration;
  		}
  	}]);
  	return VariableAssignment;
  }(InkObject);

  var Void = function (_InkObject) {
    babelHelpers.inherits(Void, _InkObject);

    function Void() {
      babelHelpers.classCallCheck(this, Void);
      return babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(Void).apply(this, arguments));
    }

    return Void;
  }(InkObject);

  var NativeFunctionCall = function (_InkObject) {
  	babelHelpers.inherits(NativeFunctionCall, _InkObject);

  	function NativeFunctionCall(name) {
  		babelHelpers.classCallCheck(this, NativeFunctionCall);

  		var _this = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(NativeFunctionCall).call(this));

  		_this.name = name;
  		_this._numberOfParameters;

  		_this._prototype;
  		_this._isPrototype;
  		_this._operationFuncs = null;

  		NativeFunctionCall.GenerateNativeFunctionsIfNecessary();
  		return _this;
  	}

  	babelHelpers.createClass(NativeFunctionCall, [{
  		key: 'Call',
  		value: function Call(parameters) {
  			if (this._prototype) {
  				return this._prototype.Call(parameters);
  			}

  			if (this.numberOfParameters != parameters.length) {
  				throw "Unexpected number of parameters";
  			}

  			parameters.forEach(function (p) {
  				if (p instanceof Void) throw new StoryException("Attempting to perform operation on a void value. Did you forget to 'return' a value from a function you called here?");
  			});

  			var coercedParams = this.CoerceValuesToSingleType(parameters);
  			var coercedType = coercedParams[0].valueType;

  			//Originally CallType gets a type parameter taht is used to do some casting, but we can do without.
  			if (coercedType == ValueType.Int) {
  				return this.CallType(coercedParams);
  			} else if (coercedType == ValueType.Float) {
  				return this.CallType(coercedParams);
  			} else if (coercedType == ValueType.String) {
  				return this.CallType(coercedParams);
  			} else if (coercedType == ValueType.DivertTarget) {
  				return this.CallType(coercedParams);
  			}

  			return null;
  		}
  	}, {
  		key: 'CallType',
  		value: function CallType(parametersOfSingleType) {
  			var param1 = parametersOfSingleType[0];
  			var valType = param1.valueType;

  			var val1 = param1;

  			var paramCount = parametersOfSingleType.length;

  			if (paramCount == 2 || paramCount == 1) {

  				var opForTypeObj = this._operationFuncs[valType];
  				if (!opForTypeObj) {
  					throw new StoryException("Can not perform operation '" + this.name + "' on " + valType);
  				}

  				// Binary
  				if (paramCount == 2) {
  					var param2 = parametersOfSingleType[1];

  					var val2 = param2;

  					var opForType = opForTypeObj;

  					// Return value unknown until it's evaluated
  					var resultVal = opForType(val1.value, val2.value);

  					return Value.Create(resultVal);
  				}

  				// Unary
  				else {

  						var opForType = opForTypeObj;

  						var resultVal = opForType(val1.value);

  						return Value.Create(resultVal);
  					}
  			} else {
  				throw "Unexpected number of parameters to NativeFunctionCall: " + parametersOfSingleType.length;
  			}
  		}
  	}, {
  		key: 'CoerceValuesToSingleType',
  		value: function CoerceValuesToSingleType(parametersIn) {
  			var valType = ValueType.Int;

  			// Find out what the output type is
  			// "higher level" types infect both so that binary operations
  			// use the same type on both sides. e.g. binary operation of
  			// int and float causes the int to be casted to a float.
  			parametersIn.forEach(function (obj) {
  				var val = obj;
  				if (val.valueType > valType) {
  					valType = val.valueType;
  				}
  			});

  			// Coerce to this chosen type
  			var parametersOut = [];
  			parametersIn.forEach(function (val) {
  				var castedValue = val.Cast(valType);
  				parametersOut.push(castedValue);
  			});

  			return parametersOut;
  		}
  	}, {
  		key: 'AddOpFuncForType',
  		value: function AddOpFuncForType(valType, op) {
  			if (this._operationFuncs == null) {
  				this._operationFuncs = {};
  			}

  			this._operationFuncs[valType] = op;
  		}
  	}, {
  		key: 'toString',
  		value: function toString() {
  			return "Native '" + this.name + "'";
  		}
  	}, {
  		key: 'name',
  		get: function get() {
  			return this._name;
  		},
  		set: function set(value) {
  			this._name = value;
  			if (!this._isPrototype) this._prototype = NativeFunctionCall._nativeFunctions[this._name];
  		}
  	}, {
  		key: 'numberOfParameters',
  		get: function get() {
  			if (this._prototype) {
  				return this._prototype.numberOfParameters;
  			} else {
  				return this._numberOfParameters;
  			}
  		},
  		set: function set(value) {
  			this._numberOfParameters = value;
  		}
  	}], [{
  		key: 'internalConstructor',
  		value: function internalConstructor(name, numberOfParamters) {
  			var nativeFunc = new NativeFunctionCall(name);
  			nativeFunc._isPrototype = true;
  			nativeFunc.numberOfParameters = numberOfParamters;
  			return nativeFunc;
  		}
  	}, {
  		key: 'CallWithName',
  		value: function CallWithName(functionName) {
  			return new NativeFunctionCall(functionName);
  		}
  	}, {
  		key: 'CallExistsWithName',
  		value: function CallExistsWithName(functionName) {
  			this.GenerateNativeFunctionsIfNecessary();
  			return this._nativeFunctions[functionName];
  		}
  	}, {
  		key: 'GenerateNativeFunctionsIfNecessary',
  		value: function GenerateNativeFunctionsIfNecessary() {
  			if (this._nativeFunctions == null) {
  				this._nativeFunctions = {};

  				// Int operations
  				this.AddIntBinaryOp(this.Add, function (x, y) {
  					return x + y;
  				});
  				this.AddIntBinaryOp(this.Subtract, function (x, y) {
  					return x - y;
  				});
  				this.AddIntBinaryOp(this.Multiply, function (x, y) {
  					return x * y;
  				});
  				this.AddIntBinaryOp(this.Divide, function (x, y) {
  					return parseInt(x / y);
  				});
  				this.AddIntBinaryOp(this.Mod, function (x, y) {
  					return x % y;
  				});
  				this.AddIntUnaryOp(this.Negate, function (x) {
  					return -x;
  				});

  				this.AddIntBinaryOp(this.Equal, function (x, y) {
  					return x == y ? 1 : 0;
  				});
  				this.AddIntBinaryOp(this.Greater, function (x, y) {
  					return x > y ? 1 : 0;
  				});
  				this.AddIntBinaryOp(this.Less, function (x, y) {
  					return x < y ? 1 : 0;
  				});
  				this.AddIntBinaryOp(this.GreaterThanOrEquals, function (x, y) {
  					return x >= y ? 1 : 0;
  				});
  				this.AddIntBinaryOp(this.LessThanOrEquals, function (x, y) {
  					return x <= y ? 1 : 0;
  				});
  				this.AddIntBinaryOp(this.NotEquals, function (x, y) {
  					return x != y ? 1 : 0;
  				});
  				this.AddIntUnaryOp(this.Not, function (x) {
  					return x == 0 ? 1 : 0;
  				});

  				this.AddIntBinaryOp(this.And, function (x, y) {
  					return x != 0 && y != 0 ? 1 : 0;
  				});
  				this.AddIntBinaryOp(this.Or, function (x, y) {
  					return x != 0 || y != 0 ? 1 : 0;
  				});

  				this.AddIntBinaryOp(this.Max, function (x, y) {
  					return Math.max(x, y);
  				});
  				this.AddIntBinaryOp(this.Min, function (x, y) {
  					return Math.min(x, y);
  				});

  				// Float operations
  				this.AddFloatBinaryOp(this.Add, function (x, y) {
  					return x + y;
  				});
  				this.AddFloatBinaryOp(this.Subtract, function (x, y) {
  					return x - y;
  				});
  				this.AddFloatBinaryOp(this.Multiply, function (x, y) {
  					return x * y;
  				});
  				this.AddFloatBinaryOp(this.Divide, function (x, y) {
  					return x / y;
  				});
  				this.AddFloatBinaryOp(this.Mod, function (x, y) {
  					return x % y;
  				}); // TODO: Is this the operation we want for floats?
  				this.AddFloatUnaryOp(this.Negate, function (x) {
  					return -x;
  				});

  				this.AddFloatBinaryOp(this.Equal, function (x, y) {
  					return x == y ? 1 : 0;
  				});
  				this.AddFloatBinaryOp(this.Greater, function (x, y) {
  					return x > y ? 1 : 0;
  				});
  				this.AddFloatBinaryOp(this.Less, function (x, y) {
  					return x < y ? 1 : 0;
  				});
  				this.AddFloatBinaryOp(this.GreaterThanOrEquals, function (x, y) {
  					return x >= y ? 1 : 0;
  				});
  				this.AddFloatBinaryOp(this.LessThanOrEquals, function (x, y) {
  					return x <= y ? 1 : 0;
  				});
  				this.AddFloatBinaryOp(this.NotEquals, function (x, y) {
  					return x != y ? 1 : 0;
  				});
  				this.AddFloatUnaryOp(this.Not, function (x) {
  					return x == 0.0 ? 1 : 0;
  				});

  				this.AddFloatBinaryOp(this.And, function (x, y) {
  					return x != 0.0 && y != 0.0 ? 1 : 0;
  				});
  				this.AddFloatBinaryOp(this.Or, function (x, y) {
  					return x != 0.0 || y != 0.0 ? 1 : 0;
  				});

  				this.AddFloatBinaryOp(this.Max, function (x, y) {
  					return Math.max(x, y);
  				});
  				this.AddFloatBinaryOp(this.Min, function (x, y) {
  					return Math.min(x, y);
  				});

  				// String operations
  				this.AddStringBinaryOp(this.Add, function (x, y) {
  					return x + y;
  				}); // concat
  				this.AddStringBinaryOp(this.Equal, function (x, y) {
  					return x === y ? 1 : 0;
  				});

  				// Special case: The only operation you can do on divert target values
  				var divertTargetsEqual = function divertTargetsEqual(d1, d2) {
  					return d1.Equals(d2) ? 1 : 0;
  				};
  				this.AddOpToNativeFunc(this.Equal, 2, ValueType.DivertTarget, divertTargetsEqual);
  			}
  		}
  	}, {
  		key: 'AddOpToNativeFunc',
  		value: function AddOpToNativeFunc(name, args, valType, op) {
  			var nativeFunc = this._nativeFunctions[name];
  			if (!nativeFunc) {
  				nativeFunc = NativeFunctionCall.internalConstructor(name, args);
  				this._nativeFunctions[name] = nativeFunc;
  			}

  			nativeFunc.AddOpFuncForType(valType, op);
  		}
  	}, {
  		key: 'AddIntBinaryOp',
  		value: function AddIntBinaryOp(name, op) {
  			this.AddOpToNativeFunc(name, 2, ValueType.Int, op);
  		}
  	}, {
  		key: 'AddIntUnaryOp',
  		value: function AddIntUnaryOp(name, op) {
  			this.AddOpToNativeFunc(name, 1, ValueType.Int, op);
  		}
  	}, {
  		key: 'AddFloatBinaryOp',
  		value: function AddFloatBinaryOp(name, op) {
  			this.AddOpToNativeFunc(name, 2, ValueType.Float, op);
  		}
  	}, {
  		key: 'AddFloatUnaryOp',
  		value: function AddFloatUnaryOp(name, op) {
  			this.AddOpToNativeFunc(name, 1, ValueType.Float, op);
  		}
  	}, {
  		key: 'AddStringBinaryOp',
  		value: function AddStringBinaryOp(name, op) {
  			this.AddOpToNativeFunc(name, 2, ValueType.String, op);
  		}
  	}]);
  	return NativeFunctionCall;
  }(InkObject);

  NativeFunctionCall.Add = "+";
  NativeFunctionCall.Subtract = "-";
  NativeFunctionCall.Divide = "/";
  NativeFunctionCall.Multiply = "*";
  NativeFunctionCall.Mod = "%";
  NativeFunctionCall.Negate = "~";

  NativeFunctionCall.Equal = "==";
  NativeFunctionCall.Greater = ">";
  NativeFunctionCall.Less = "<";
  NativeFunctionCall.GreaterThanOrEquals = ">=";
  NativeFunctionCall.LessThanOrEquals = "<=";
  NativeFunctionCall.NotEquals = "!=";
  NativeFunctionCall.Not = "!";

  NativeFunctionCall.And = "&&";
  NativeFunctionCall.Or = "||";

  NativeFunctionCall.Min = "MIN";
  NativeFunctionCall.Max = "MAX";

  NativeFunctionCall._nativeFunctions = null;

  var Tag = function (_InkObject) {
  	babelHelpers.inherits(Tag, _InkObject);

  	function Tag(tagText) {
  		babelHelpers.classCallCheck(this, Tag);

  		var _this = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(Tag).call(this));

  		_this._text = tagText.toString() || '';
  		return _this;
  	}

  	babelHelpers.createClass(Tag, [{
  		key: 'toString',
  		value: function toString() {
  			return "# " + this._text;
  		}
  	}, {
  		key: 'text',
  		get: function get() {
  			return this._text;
  		}
  	}]);
  	return Tag;
  }(InkObject);

  var Choice = function () {
  	function Choice(choice) {
  		babelHelpers.classCallCheck(this, Choice);

  		this.text;
  		this.index;
  		this.choicePoint;
  		this.threadAtGeneration;

  		this._originalThreadIndex;
  		this._originalChoicePath;

  		if (choice) this.choicePoint = choice;
  	}

  	babelHelpers.createClass(Choice, [{
  		key: "pathStringOnChoice",
  		get: function get() {
  			return this.choicePoint.pathStringOnChoice;
  		}
  	}, {
  		key: "sourcePath",
  		get: function get() {
  			return this.choicePoint.path.componentsString;
  		}
  	}]);
  	return Choice;
  }();

  var JsonSerialisation = function () {
  	function JsonSerialisation() {
  		babelHelpers.classCallCheck(this, JsonSerialisation);
  	}

  	babelHelpers.createClass(JsonSerialisation, null, [{
  		key: 'ListToJArray',
  		value: function ListToJArray(serialisables) {
  			var _this = this;

  			var jArray = [];
  			serialisables.forEach(function (s) {
  				jArray.push(_this.RuntimeObjectToJToken(s));
  			});
  			return jArray;
  		}
  	}, {
  		key: 'JArrayToRuntimeObjList',
  		value: function JArrayToRuntimeObjList(jArray, skipLast) {
  			var count = jArray.length;
  			if (skipLast) count--;

  			var list = [];

  			for (var i = 0; i < count; i++) {
  				var jTok = jArray[i];
  				var runtimeObj = this.JTokenToRuntimeObject(jTok);
  				list.push(runtimeObj);
  			}

  			return list;
  		}
  	}, {
  		key: 'JObjectToDictionaryRuntimeObjs',
  		value: function JObjectToDictionaryRuntimeObjs(jObject) {
  			var dict = {};

  			for (var key in jObject) {
  				dict[key] = this.JTokenToRuntimeObject(jObject[key]);
  			}

  			return dict;
  		}
  	}, {
  		key: 'DictionaryRuntimeObjsToJObject',
  		value: function DictionaryRuntimeObjsToJObject(dictionary) {
  			var jsonObj = {};

  			for (var key in dictionary) {
  				//			var runtimeObj = keyVal.Value as Runtime.Object;
  				var runtimeObj = dictionary[key];
  				if (runtimeObj instanceof InkObject) jsonObj[key] = this.RuntimeObjectToJToken(runtimeObj);
  			}

  			return jsonObj;
  		}
  	}, {
  		key: 'JObjectToIntDictionary',
  		value: function JObjectToIntDictionary(jObject) {
  			var dict = {};
  			for (var key in jObject) {
  				dict[key] = parseInt(jObject[key]);
  			}
  			return dict;
  		}
  	}, {
  		key: 'IntDictionaryToJObject',
  		value: function IntDictionaryToJObject(dict) {
  			var jObj = {};
  			for (var key in dict) {
  				jObj[key] = dict[key];
  			}
  			return jObj;
  		}
  	}, {
  		key: 'JTokenToRuntimeObject',
  		value: function JTokenToRuntimeObject(token) {
  			//@TODO probably find a more robust way to detect numbers, isNaN seems happy to accept things that really aren't numberish.
  			if (!isNaN(token) && token !== "\n") {
  				//JS thinks "\n" is a number
  				return Value.Create(token);
  			}

  			if (typeof token === 'string') {
  				var str = token.toString();

  				// String value
  				var firstChar = str[0];
  				if (firstChar == '^') return new StringValue(str.substring(1));else if (firstChar == "\n" && str.length == 1) return new StringValue("\n");

  				// Glue
  				if (str == "<>") return new Glue(GlueType.Bidirectional);else if (str == "G<") return new Glue(GlueType.Left);else if (str == "G>") return new Glue(GlueType.Right);

  				// Control commands (would looking up in a hash set be faster?)
  				for (var i = 0; i < _controlCommandNames.length; ++i) {
  					var cmdName = _controlCommandNames[i];
  					if (str == cmdName) {
  						return new ControlCommand(i);
  					}
  				}

  				// Native functions
  				if (NativeFunctionCall.CallExistsWithName(str)) return NativeFunctionCall.CallWithName(str);

  				// Pop
  				if (str == "->->") return ControlCommand.PopTunnel();else if (str == "~ret") return ControlCommand.PopFunction();

  				// Void
  				if (str == "void") return new Void();
  			}

  			if ((typeof token === 'undefined' ? 'undefined' : babelHelpers.typeof(token)) === 'object' && token instanceof Array === false) {
  				var obj = token;
  				var propValue;

  				// Divert target value to path
  				if (obj["^->"]) {
  					propValue = obj["^->"];
  					return new DivertTargetValue(new Path$1(propValue.toString()));
  				}

  				// VariablePointerValue
  				if (obj["^var"]) {
  					propValue = obj["^var"];
  					var varPtr = new VariablePointerValue(propValue.toString());
  					if (obj["ci"]) {
  						propValue = obj["ci"];
  						varPtr.contextIndex = parseInt(propValue);
  					}
  					return varPtr;
  				}

  				// Divert
  				var isDivert = false;
  				var pushesToStack = false;
  				var divPushType = PushPopType.Function;
  				var external = false;
  				if (propValue = obj["->"]) {
  					isDivert = true;
  				} else if (propValue = obj["f()"]) {
  					isDivert = true;
  					pushesToStack = true;
  					divPushType = PushPopType.Function;
  				} else if (propValue = obj["->t->"]) {
  					isDivert = true;
  					pushesToStack = true;
  					divPushType = PushPopType.Tunnel;
  				} else if (propValue = obj["x()"]) {
  					isDivert = true;
  					external = true;
  					pushesToStack = false;
  					divPushType = PushPopType.Function;
  				}

  				if (isDivert) {
  					var divert = new Divert();
  					divert.pushesToStack = pushesToStack;
  					divert.stackPushType = divPushType;
  					divert.isExternal = external;

  					var target = propValue.toString();

  					if (propValue = obj["var"]) divert.variableDivertName = target;else divert.targetPathString = target;

  					divert.isConditional = !!obj["c"];

  					if (external) {
  						if (propValue = obj["exArgs"]) divert.externalArgs = parseInt(propValue);
  					}

  					return divert;
  				}

  				// Choice
  				if (propValue = obj["*"]) {
  					var choice = new ChoicePoint();
  					choice.pathStringOnChoice = propValue.toString();

  					if (propValue = obj["flg"]) choice.flags = parseInt(propValue);

  					return choice;
  				}

  				// Variable reference
  				if (propValue = obj["VAR?"]) {
  					return new VariableReference(propValue.toString());
  				} else if (propValue = obj["CNT?"]) {
  					var readCountVarRef = new VariableReference();
  					readCountVarRef.pathStringForCount = propValue.toString();
  					return readCountVarRef;
  				}

  				// Variable assignment
  				var isVarAss = false;
  				var isGlobalVar = false;
  				if (propValue = obj["VAR="]) {
  					isVarAss = true;
  					isGlobalVar = true;
  				} else if (propValue = obj["temp="]) {
  					isVarAss = true;
  					isGlobalVar = false;
  				}
  				if (isVarAss) {
  					var varName = propValue.toString();
  					var isNewDecl = !obj["re"];
  					var varAss = new VariableAssignment(varName, isNewDecl);
  					varAss.isGlobal = isGlobalVar;
  					return varAss;
  				}
  				if (propValue = obj["#"]) {
  					return new Tag(propValue.toString());
  				}

  				if (obj["originalChoicePath"] != null) return this.JObjectToChoice(obj);
  			}

  			// Array is always a Runtime.Container
  			if (token instanceof Array) {
  				return this.JArrayToContainer(token);
  			}

  			if (token == null) return null;

  			throw "Failed to convert token to runtime object: " + JSON.stringify(token);
  		}
  	}, {
  		key: 'RuntimeObjectToJToken',
  		value: function RuntimeObjectToJToken(obj) {
  			//		var container = obj as Container;
  			var container = obj;
  			if (container instanceof Container) {
  				return this.ContainerToJArray(container);
  			}

  			//		var divert = obj as Divert;
  			var divert = obj;
  			if (divert instanceof Divert) {
  				var divTypeKey = "->";
  				if (divert.isExternal) divTypeKey = "x()";else if (divert.pushesToStack) {
  					if (divert.stackPushType == PushPopType.Function) divTypeKey = "f()";else if (divert.stackPushType == PushPopType.Tunnel) divTypeKey = "->t->";
  				}

  				var targetStr;
  				if (divert.hasVariableTarget) targetStr = divert.variableDivertName;else targetStr = divert.targetPathString;

  				var jObj = {};
  				jObj[divTypeKey] = targetStr;

  				if (divert.hasVariableTarget) jObj["var"] = true;

  				if (divert.isConditional) jObj["c"] = true;

  				if (divert.externalArgs > 0) jObj["exArgs"] = divert.externalArgs;

  				return jObj;
  			}

  			//		var choicePoint = obj as ChoicePoint;
  			var choicePoint = obj;
  			if (choicePoint instanceof ChoicePoint) {
  				var jObj = {};
  				jObj["*"] = choicePoint.pathStringOnChoice;
  				jObj["flg"] = choicePoint.flags;
  				return jObj;
  			}

  			//		var intVal = obj as IntValue;
  			var intVal = obj;
  			if (intVal instanceof IntValue) return intVal.value;

  			//		var floatVal = obj as FloatValue;
  			var floatVal = obj;
  			if (floatVal instanceof FloatValue) return floatVal.value;

  			//		var strVal = obj as StringValue;
  			var strVal = obj;
  			if (strVal instanceof StringValue) {
  				if (strVal.isNewline) return "\n";else return "^" + strVal.value;
  			}

  			//		var divTargetVal = obj as DivertTargetValue;
  			var divTargetVal = obj;
  			if (divTargetVal instanceof DivertTargetValue) return {
  				"^->": divTargetVal.value.componentsString
  			};

  			//		var varPtrVal = obj as VariablePointerValue;
  			var varPtrVal = obj;
  			if (varPtrVal instanceof VariablePointerValue) return {
  				"^var": varPtrVal.value,
  				"ci": varPtrVal.contextIndex
  			};

  			//		var glue = obj as Runtime.Glue;
  			var glue = obj;
  			if (glue instanceof Glue) {
  				if (glue.isBi) return "<>";else if (glue.isLeft) return "G<";else return "G>";
  			}

  			//		var controlCmd = obj as ControlCommand;
  			var controlCmd = obj;
  			if (controlCmd instanceof ControlCommand) {
  				return _controlCommandNames[parseInt(controlCmd.commandType)];
  			}

  			//		var nativeFunc = obj as Runtime.NativeFunctionCall;
  			var nativeFunc = obj;
  			if (nativeFunc instanceof NativeFunctionCall) return nativeFunc.name;

  			// Variable reference
  			//		var varRef = obj as VariableReference;
  			var varRef = obj;
  			if (varRef instanceof VariableReference) {
  				var jObj = {};
  				var readCountPath = varRef.pathStringForCount;
  				if (readCountPath != null) {
  					jObj["CNT?"] = readCountPath;
  				} else {
  					jObj["VAR?"] = varRef.name;
  				}

  				return jObj;
  			}

  			// Variable assignment
  			//		var varAss = obj as VariableAssignment;
  			var varAss = obj;
  			if (varAss instanceof VariableAssignment) {
  				var key = varAss.isGlobal ? "VAR=" : "temp=";
  				var jObj = {};
  				jObj[key] = varAss.variableName;

  				// Reassignment?
  				if (!varAss.isNewDeclaration) jObj["re"] = true;

  				return jObj;
  			}

  			//		var voidObj = obj as Void;
  			var voidObj = obj;
  			if (voidObj instanceof Void) return "void";

  			//		var tag = obj as Tag;
  			var tag = obj;
  			if (tag instanceof Tag) {
  				var jObj = {};
  				jObj["#"] = tag.text;
  				return jObj;
  			}

  			// Used when serialising save state only
  			//		var choice = obj as Choice;
  			var choice = obj;
  			if (choice instanceof Choice) return this.ChoiceToJObject(choice);

  			throw "Failed to convert runtime object to Json token: " + obj;
  		}
  	}, {
  		key: 'ContainerToJArray',
  		value: function ContainerToJArray(container) {
  			var jArray = this.ListToJArray(container.content);

  			// Container is always an array [...]
  			// But the final element is always either:
  			//  - a dictionary containing the named content, as well as possibly
  			//    the key "#" with the count flags
  			//  - null, if neither of the above
  			var namedOnlyContent = container.namedOnlyContent;
  			var countFlags = container.countFlags;
  			if (namedOnlyContent != null && namedOnlyContent.length > 0 || countFlags > 0 || container.name != null) {

  				var terminatingObj;
  				if (namedOnlyContent != null) {
  					terminatingObj = this.DictionaryRuntimeObjsToJObject(namedOnlyContent);

  					// Strip redundant names from containers if necessary
  					for (var key in terminatingObj) {
  						//					var subContainerJArray = namedContentObj.Value as JArray;
  						var subContainerJArray = terminatingObj[key];
  						if (subContainerJArray != null) {
  							//						var attrJObj = subContainerJArray [subContainerJArray.Count - 1] as JObject;
  							var attrJObj = subContainerJArray[subContainerJArray.length - 1];
  							if (attrJObj != null) {
  								delete attrJObj["#n"];
  								if (Object.keys(attrJObj).length == 0) subContainerJArray[subContainerJArray.length - 1] = null;
  							}
  						}
  					}
  				} else terminatingObj = {};

  				if (countFlags > 0) terminatingObj["#f"] = countFlags;

  				if (container.name != null) terminatingObj["#n"] = container.name;

  				jArray.push(terminatingObj);
  			}

  			// Add null terminator to indicate that there's no dictionary
  			else {
  					jArray.push(null);
  				}

  			return jArray;
  		}
  	}, {
  		key: 'JArrayToContainer',
  		value: function JArrayToContainer(jArray) {
  			var container = new Container();
  			container.content = this.JArrayToRuntimeObjList(jArray, true);

  			// Final object in the array is always a combination of
  			//  - named content
  			//  - a "#" key with the countFlags
  			// (if either exists at all, otherwise null)
  			//		var terminatingObj = jArray [jArray.Count - 1] as JObject;
  			var terminatingObj = jArray[jArray.length - 1];
  			if (terminatingObj != null) {

  				var namedOnlyContent = {};

  				for (var key in terminatingObj) {
  					if (key == "#f") {
  						container.countFlags = parseInt(terminatingObj[key]);
  					} else if (key == "#n") {
  						container.name = terminatingObj[key].toString();
  					} else {
  						var namedContentItem = this.JTokenToRuntimeObject(terminatingObj[key]);
  						//					var namedSubContainer = namedContentItem as Container;
  						var namedSubContainer = namedContentItem;
  						if (namedSubContainer instanceof Container) namedSubContainer.name = key;
  						namedOnlyContent[key] = namedContentItem;
  					}
  				}

  				container.namedOnlyContent = namedOnlyContent;
  			}

  			return container;
  		}
  	}, {
  		key: 'JObjectToChoice',
  		value: function JObjectToChoice(jObj) {
  			var choice = new Choice();
  			choice.text = jObj["text"].toString();
  			choice.index = parseInt(jObj["index"]);
  			choice.originalChoicePath = jObj["originalChoicePath"].toString();
  			choice.originalThreadIndex = parseInt(jObj["originalThreadIndex"]);
  			return choice;
  		}
  	}, {
  		key: 'ChoiceToJObject',
  		value: function ChoiceToJObject(choice) {
  			var jObj = {};
  			jObj["text"] = choice.text;
  			jObj["index"] = choice.index;
  			jObj["originalChoicePath"] = choice.originalChoicePath;
  			jObj["originalThreadIndex"] = choice.originalThreadIndex;
  			return jObj;
  		}
  	}]);
  	return JsonSerialisation;
  }();

  var _controlCommandNames = [];

  _controlCommandNames[ControlCommand.CommandType.EvalStart] = "ev";
  _controlCommandNames[ControlCommand.CommandType.EvalOutput] = "out";
  _controlCommandNames[ControlCommand.CommandType.EvalEnd] = "/ev";
  _controlCommandNames[ControlCommand.CommandType.Duplicate] = "du";
  _controlCommandNames[ControlCommand.CommandType.PopEvaluatedValue] = "pop";
  _controlCommandNames[ControlCommand.CommandType.PopFunction] = "~ret";
  _controlCommandNames[ControlCommand.CommandType.PopTunnel] = "->->";
  _controlCommandNames[ControlCommand.CommandType.BeginString] = "str";
  _controlCommandNames[ControlCommand.CommandType.EndString] = "/str";
  _controlCommandNames[ControlCommand.CommandType.NoOp] = "nop";
  _controlCommandNames[ControlCommand.CommandType.ChoiceCount] = "choiceCnt";
  _controlCommandNames[ControlCommand.CommandType.TurnsSince] = "turns";
  _controlCommandNames[ControlCommand.CommandType.Random] = "rnd";
  _controlCommandNames[ControlCommand.CommandType.SeedRandom] = "srnd";
  _controlCommandNames[ControlCommand.CommandType.VisitIndex] = "visit";
  _controlCommandNames[ControlCommand.CommandType.SequenceShuffleIndex] = "seq";
  _controlCommandNames[ControlCommand.CommandType.StartThread] = "thread";
  _controlCommandNames[ControlCommand.CommandType.Done] = "done";
  _controlCommandNames[ControlCommand.CommandType.End] = "end";

  for (var i$1 = 0; i$1 < ControlCommand.CommandType.TOTAL_VALUES; ++i$1) {
  	if (_controlCommandNames[i$1] == null) throw "Control command not accounted for in serialisation";
  }

  var Element = function () {
  	function Element(type, container, contentIndex, inExpressionEvaluation) {
  		babelHelpers.classCallCheck(this, Element);

  		this.currentContainer = container;
  		this.currentContentIndex = contentIndex;
  		this.inExpressionEvaluation = inExpressionEvaluation || false;
  		this.temporaryVariables = {};
  		this.type = type;
  	}

  	babelHelpers.createClass(Element, [{
  		key: 'Copy',
  		value: function Copy() {
  			var copy = new Element(this.type, this.currentContainer, this.currentContentIndex, this.inExpressionEvaluation);
  			babelHelpers.extends(copy.temporaryVariables, this.temporaryVariables);
  			return copy;
  		}
  	}, {
  		key: 'currentObject',
  		get: function get() {
  			if (this.currentContainer && this.currentContentIndex < this.currentContainer.content.length) {
  				return this.currentContainer.content[this.currentContentIndex];
  			}

  			return null;
  		},
  		set: function set(value) {
  			var currentObj = value;
  			if (currentObj == null) {
  				this.currentContainer = null;
  				this.currentContentIndex = 0;
  				return;
  			}

  			//		currentContainer = currentObj.parent as Container;
  			this.currentContainer = currentObj.parent;
  			if (this.currentContainer instanceof Container) this.currentContentIndex = this.currentContainer.content.indexOf(currentObj);

  			// Two reasons why the above operation might not work:
  			//  - currentObj is already the root container
  			//  - currentObj is a named container rather than being an object at an index
  			if (this.currentContainer instanceof Container === false || this.currentContentIndex == -1) {
  				//			currentContainer = currentObj as Container;
  				this.currentContainer = currentObj;
  				this.currentContentIndex = 0;
  			}
  		}
  	}]);
  	return Element;
  }();

  var Thread = function () {
  	function Thread(jsonToken, storyContext) {
  		var _this = this;

  		babelHelpers.classCallCheck(this, Thread);

  		this.callstack = [];
  		this.threadIndex = 0;
  		this.previousContentObject = null;

  		if (jsonToken && storyContext) {
  			var jThreadObj = jsonToken;
  			this.threadIndex = parseInt(jThreadObj["threadIndex"]);

  			var jThreadCallstack = jThreadObj["callstack"];

  			jThreadCallstack.forEach(function (jElTok) {
  				var jElementObj = jElTok;

  				var pushPopType = parseInt(jElementObj["type"]);

  				var currentContainer = null;
  				var contentIndex = 0;

  				var currentContainerPathStr = null;
  				var currentContainerPathStrToken = jElementObj["cPath"];
  				if (typeof currentContainerPathStrToken !== 'undefined') {
  					currentContainerPathStr = currentContainerPathStrToken.toString();
  					//					currentContainer = storyContext.ContentAtPath (new Path(currentContainerPathStr)) as Container;
  					currentContainer = storyContext.ContentAtPath(new Path$1(currentContainerPathStr));
  					contentIndex = parseInt(jElementObj["idx"]);
  				}

  				var inExpressionEvaluation = !!jElementObj["exp"];

  				var el = new Element(pushPopType, currentContainer, contentIndex, inExpressionEvaluation);

  				var jObjTemps = jElementObj["temp"];
  				el.temporaryVariables = JsonSerialisation.JObjectToDictionaryRuntimeObjs(jObjTemps);

  				_this.callstack.push(el);
  			});

  			var prevContentObjPath = jThreadObj["previousContentObject"];
  			if (typeof prevContentObjPath !== 'undefined') {
  				var prevPath = new Path$1(prevContentObjPath.toString());
  				this.previousContentObject = storyContext.ContentAtPath(prevPath);
  			}
  		}
  	}

  	babelHelpers.createClass(Thread, [{
  		key: 'Copy',
  		value: function Copy() {
  			var copy = new Thread();
  			copy.threadIndex = this.threadIndex;
  			this.callstack.forEach(function (e) {
  				copy.callstack.push(e.Copy());
  			});
  			copy.previousContentObject = this.previousContentObject;
  			return copy;
  		}
  	}, {
  		key: 'jsonToken',
  		get: function get() {
  			var threadJObj = {};

  			var jThreadCallstack = [];
  			this.callstack.forEach(function (el) {
  				var jObj = {};
  				if (el.currentContainer) {
  					jObj["cPath"] = el.currentContainer.path.componentsString;
  					jObj["idx"] = el.currentContentIndex;
  				}
  				jObj["exp"] = el.inExpressionEvaluation;
  				jObj["type"] = parseInt(el.type);
  				jObj["temp"] = JsonSerialisation.DictionaryRuntimeObjsToJObject(el.temporaryVariables);
  				jThreadCallstack.push(jObj);
  			});

  			threadJObj["callstack"] = jThreadCallstack;
  			threadJObj["threadIndex"] = this.threadIndex;

  			if (this.previousContentObject != null) threadJObj["previousContentObject"] = this.previousContentObject.path.toString();

  			return threadJObj;
  		}
  	}]);
  	return Thread;
  }();

  var CallStack = function () {
  	function CallStack(copyOrrootContentContainer) {
  		var _this2 = this;

  		babelHelpers.classCallCheck(this, CallStack);

  		this._threads = [];
  		this._threadCounter = 0;
  		this._threads.push(new Thread());

  		if (copyOrrootContentContainer instanceof CallStack) {
  			this._threads = [];

  			copyOrrootContentContainer._threads.forEach(function (otherThread) {
  				_this2._threads.push(otherThread.Copy());
  			});
  		} else {
  			this._threads[0].callstack.push(new Element(PushPopType.Tunnel, copyOrrootContentContainer, 0));
  		}
  	}

  	babelHelpers.createClass(CallStack, [{
  		key: 'CanPop',
  		value: function CanPop(type) {
  			if (!this.canPop) return false;

  			if (type == null) return true;

  			return this.currentElement.type == type;
  		}
  	}, {
  		key: 'Pop',
  		value: function Pop(type) {
  			if (this.CanPop(type)) {
  				this.callStack.pop();
  				return;
  			} else {
  				throw "Mismatched push/pop in Callstack";
  			}
  		}
  	}, {
  		key: 'Push',
  		value: function Push(type) {
  			// When pushing to callstack, maintain the current content path, but jump out of expressions by default
  			this.callStack.push(new Element(type, this.currentElement.currentContainer, this.currentElement.currentContentIndex, false));
  		}
  	}, {
  		key: 'PushThread',
  		value: function PushThread() {
  			var newThread = this.currentThread.Copy();
  			newThread.threadIndex = this._threadCounter;
  			this._threadCounter++;
  			this._threads.push(newThread);
  		}
  	}, {
  		key: 'PopThread',
  		value: function PopThread() {
  			if (this.canPopThread) {
  				this._threads.splice(this._threads.indexOf(this.currentThread), 1); //should be equivalent to a pop()
  			} else {
  					throw "Can't pop thread";
  				}
  		}
  	}, {
  		key: 'SetJsonToken',
  		value: function SetJsonToken(token, storyContext) {
  			var _this3 = this;

  			this._threads.length = 0;

  			var jObject = token;

  			var jThreads = jObject["threads"];

  			jThreads.forEach(function (jThreadTok) {
  				var thread = new Thread(jThreadTok, storyContext);
  				_this3._threads.push(thread);
  			});

  			this._threadCounter = parseInt(jObject["threadCounter"]);
  		}
  	}, {
  		key: 'GetJsonToken',
  		value: function GetJsonToken() {
  			var jObject = {};

  			var jThreads = [];
  			this._threads.forEach(function (thread) {
  				jThreads.push(thread.jsonToken);
  			});

  			jObject["threads"] = jThreads;
  			jObject["threadCounter"] = this._threadCounter;

  			return jObject;
  		}
  	}, {
  		key: 'GetTemporaryVariableWithName',
  		value: function GetTemporaryVariableWithName(name, contextIndex) {
  			contextIndex = typeof contextIndex === 'undefined' ? -1 : contextIndex;

  			if (contextIndex == -1) contextIndex = this.currentElementIndex + 1;

  			var varValue = null;

  			var contextElement = this.callStack[contextIndex - 1];

  			if (varValue = contextElement.temporaryVariables[name]) {
  				return varValue;
  			} else {
  				return null;
  			}
  		}
  	}, {
  		key: 'SetTemporaryVariable',
  		value: function SetTemporaryVariable(name, value, declareNew, contextIndex) {
  			contextIndex = typeof contextIndex === 'undefined' ? -1 : contextIndex;

  			if (contextIndex == -1) contextIndex = this.currentElementIndex + 1;

  			var contextElement = this.callStack[contextIndex - 1];

  			if (!declareNew && !contextElement.temporaryVariables[name]) {
  				throw new StoryException("Could not find temporary variable to set: " + name);
  			}

  			contextElement.temporaryVariables[name] = value;
  		}
  	}, {
  		key: 'ContextForVariableNamed',
  		value: function ContextForVariableNamed(name) {
  			// Current temporary context?
  			// (Shouldn't attempt to access contexts higher in the callstack.)
  			if (this.currentElement.temporaryVariables[name]) {
  				return this.currentElementIndex + 1;
  			}

  			// Global
  			else {
  					return 0;
  				}
  		}
  	}, {
  		key: 'ThreadWithIndex',
  		value: function ThreadWithIndex(index) {
  			var filtered = this._threads.filter(function (t) {
  				if (t.threadIndex == index) return t;
  			});

  			return filtered[0];
  		}
  	}, {
  		key: 'currentThread',
  		get: function get() {
  			return this._threads[this._threads.length - 1];
  		},
  		set: function set(value) {
  			if (this._threads.length != 1) console.warn("Shouldn't be directly setting the current thread when we have a stack of them");

  			this._threads.length = 0;
  			this._threads.push(value);
  		}
  	}, {
  		key: 'callStack',
  		get: function get() {
  			return this.currentThread.callstack;
  		}
  	}, {
  		key: 'elements',
  		get: function get() {
  			return this.callStack;
  		}
  	}, {
  		key: 'currentElement',
  		get: function get() {
  			return this.callStack[this.callStack.length - 1];
  		}
  	}, {
  		key: 'currentElementIndex',
  		get: function get() {
  			return this.callStack.length - 1;
  		}
  	}, {
  		key: 'canPop',
  		get: function get() {
  			return this.callStack.length > 1;
  		}
  	}, {
  		key: 'canPopThread',
  		get: function get() {
  			return this._threads.length > 1;
  		}
  	}]);
  	return CallStack;
  }();

  var VariablesState = function () {
  	function VariablesState(callStack) {
  		babelHelpers.classCallCheck(this, VariablesState);

  		this._globalVariables = {};
  		this._callStack = callStack;

  		this._batchObservingVariableChanges = null;
  		this._changedVariables = null;

  		//the way variableChangedEvent is a bit different than the reference implementation. Originally it uses the C# += operator to add delegates, but in js we need to maintain an actual collection of delegates (ie. callbacks)
  		//to register a new one, there is a special ObserveVariableChange method below.
  		this.variableChangedEvent = null;
  		this.variableChangedEventCallbacks = [];

  		//if es6 proxies are available, use them.
  		try {
  			//the proxy is used to allow direct manipulation of global variables. It first tries to access the objetcs own property, and if none is found it delegates the call to the $ method, defined below
  			var p = new Proxy(this, {
  				get: function get(target, name) {
  					return name in target ? target[name] : target.$(name);
  				},
  				set: function set(target, name, value) {
  					if (name in target) target[name] = value;else target.$(name, value);
  					return true; //returning a fasly value make sthe trap fail
  				}
  			});

  			return p;
  		} catch (e) {
  			//thr proxy object is not available in this context. we should warn the dev but writting to the console feels a bit intrusive.
  			//			console.log("ES6 Proxy not available - direct manipulation of global variables can't work, use $() instead.");
  		}
  	}

  	babelHelpers.createClass(VariablesState, [{
  		key: 'ObserveVariableChange',


  		/**
     * This function is specific to the js version of ink. It allows to register a callback that will be called when a variable changes. The original code uses `state.variableChangedEvent += callback` instead.
     * @param {function} callback 
     */
  		value: function ObserveVariableChange(callback) {
  			var _this = this;

  			if (this.variableChangedEvent == null) {
  				this.variableChangedEvent = function (variableName, newValue) {
  					_this.variableChangedEventCallbacks.forEach(function (cb) {
  						cb(variableName, newValue);
  					});
  				};
  			}

  			this.variableChangedEventCallbacks.push(callback);
  		}
  	}, {
  		key: 'CopyFrom',
  		value: function CopyFrom(varState) {
  			this._globalVariables = varState._globalVariables;
  			this.variableChangedEvent = varState.variableChangedEvent;

  			if (varState.batchObservingVariableChanges != this.batchObservingVariableChanges) {

  				if (varState.batchObservingVariableChanges) {
  					this._batchObservingVariableChanges = true;
  					this._changedVariables = varState._changedVariables;
  				} else {
  					this._batchObservingVariableChanges = false;
  					this._changedVariables = null;
  				}
  			}
  		}
  	}, {
  		key: 'GetVariableWithName',
  		value: function GetVariableWithName(name, contextIndex) {
  			if (typeof contextIndex === 'undefined') contextIndex = -1;

  			var varValue = this.GetRawVariableWithName(name, contextIndex);

  			// Get value from pointer?
  			//		var varPointer = varValue as VariablePointerValue;
  			var varPointer = varValue;
  			if (varPointer instanceof VariablePointerValue) {
  				varValue = this.ValueAtVariablePointer(varPointer);
  			}

  			return varValue;
  		}
  	}, {
  		key: 'GetRawVariableWithName',
  		value: function GetRawVariableWithName(name, contextIndex) {
  			var varValue = null;

  			// 0 context = global
  			if (contextIndex == 0 || contextIndex == -1) {
  				if (varValue = this._globalVariables[name]) return varValue;
  			}

  			// Temporary
  			varValue = this._callStack.GetTemporaryVariableWithName(name, contextIndex);

  			if (varValue == null) throw "RUNTIME ERROR: Variable '" + name + "' could not be found in context '" + contextIndex + "'. This shouldn't be possible so is a bug in the ink engine. Please try to construct a minimal story that reproduces the problem and report to inkle, thank you!";

  			return varValue;
  		}
  	}, {
  		key: 'ValueAtVariablePointer',
  		value: function ValueAtVariablePointer(pointer) {
  			return this.GetVariableWithName(pointer.variableName, pointer.contextIndex);
  		}
  	}, {
  		key: 'Assign',
  		value: function Assign(varAss, value) {
  			var name = varAss.variableName;
  			var contextIndex = -1;

  			// Are we assigning to a global variable?
  			var setGlobal = false;
  			if (varAss.isNewDeclaration) {
  				setGlobal = varAss.isGlobal;
  			} else {
  				setGlobal = !!this._globalVariables[name];
  			}

  			// Constructing new variable pointer reference
  			if (varAss.isNewDeclaration) {
  				//			var varPointer = value as VariablePointerValue;
  				var varPointer = value;
  				if (varPointer instanceof VariablePointerValue) {
  					var fullyResolvedVariablePointer = this.ResolveVariablePointer(varPointer);
  					value = fullyResolvedVariablePointer;
  				}
  			}

  			// Assign to existing variable pointer?
  			// Then assign to the variable that the pointer is pointing to by name.
  			else {

  					// De-reference variable reference to point to
  					var existingPointer = null;
  					do {
  						//				existingPointer = GetRawVariableWithName (name, contextIndex) as VariablePointerValue;
  						existingPointer = this.GetRawVariableWithName(name, contextIndex);
  						if (existingPointer instanceof VariablePointerValue) {
  							name = existingPointer.variableName;
  							contextIndex = existingPointer.contextIndex;
  							setGlobal = contextIndex == 0;
  						}
  					} while (existingPointer instanceof VariablePointerValue);
  				}

  			if (setGlobal) {
  				this.SetGlobal(name, value);
  			} else {
  				this._callStack.SetTemporaryVariable(name, value, varAss.isNewDeclaration, contextIndex);
  			}
  		}
  	}, {
  		key: 'SetGlobal',
  		value: function SetGlobal(variableName, value) {
  			var oldValue = null;
  			oldValue = this._globalVariables[variableName];

  			this._globalVariables[variableName] = value;

  			if (this.variableChangedEvent != null && value !== oldValue) {

  				if (this.batchObservingVariableChanges) {
  					this._changedVariables.push(variableName);
  				} else {
  					this.variableChangedEvent(variableName, value);
  				}
  			}
  		}
  	}, {
  		key: 'ResolveVariablePointer',
  		value: function ResolveVariablePointer(varPointer) {
  			var contextIndex = varPointer.contextIndex;

  			if (contextIndex == -1) contextIndex = this.GetContextIndexOfVariableNamed(varPointer.variableName);

  			var valueOfVariablePointedTo = this.GetRawVariableWithName(varPointer.variableName, contextIndex);

  			// Extra layer of indirection:
  			// When accessing a pointer to a pointer (e.g. when calling nested or
  			// recursive functions that take a variable references, ensure we don't create
  			// a chain of indirection by just returning the final target.
  			//		var doubleRedirectionPointer = valueOfVariablePointedTo as VariablePointerValue;
  			var doubleRedirectionPointer = valueOfVariablePointedTo;
  			if (doubleRedirectionPointer instanceof VariablePointerValue) {
  				return doubleRedirectionPointer;
  			}

  			// Make copy of the variable pointer so we're not using the value direct from
  			// the runtime. Temporary must be local to the current scope.
  			else {
  					return new VariablePointerValue(varPointer.variableName, contextIndex);
  				}
  		}
  	}, {
  		key: 'GetContextIndexOfVariableNamed',
  		value: function GetContextIndexOfVariableNamed(varName) {
  			if (this._globalVariables[varName]) return 0;

  			return this._callStack.currentElementIndex;
  		}
  		//the original code uses a magic getter and setter for global variables, allowing things like variableState['varname]. This is not quite possible in js without a Proxy, so it is replaced with this $ function.

  	}, {
  		key: '$',
  		value: function $(variableName, value) {
  			if (typeof value === 'undefined') {
  				var varContents = this._globalVariables[variableName];
  				if (typeof varContents !== 'undefined')
  					//			return (varContents as Runtime.Value).valueObject;
  					return varContents.valueObject;else return null;
  			} else {
  				if (typeof this._globalVariables[variableName] === 'undefined') {
  					throw new StoryException("Variable '" + variableName + "' doesn't exist, so can't be set.");
  				}

  				var val = Value.Create(value);
  				if (val == null) {
  					if (value == null) {
  						throw new StoryException("Cannot pass null to VariableState");
  					} else {
  						throw new StoryException("Invalid value passed to VariableState: " + value.toString());
  					}
  				}

  				this.SetGlobal(variableName, val);
  			}
  		}
  	}, {
  		key: 'batchObservingVariableChanges',
  		get: function get() {
  			return this._batchObservingVariableChanges;
  		},
  		set: function set(value) {
  			var _this2 = this;

  			value = !!value;
  			this._batchObservingVariableChanges = value;
  			if (value) {
  				this._changedVariables = [];
  			}

  			// Finished observing variables in a batch - now send
  			// notifications for changed variables all in one go.
  			else {
  					if (this._changedVariables != null) {
  						this._changedVariables.forEach(function (variableName) {
  							var currentValue = _this2._globalVariables[variableName];
  							_this2.variableChangedEvent(variableName, currentValue);
  						});
  					}

  					this._changedVariables = null;
  				}
  		}
  	}, {
  		key: 'jsonToken',
  		get: function get() {
  			return JsonSerialisation.DictionaryRuntimeObjsToJObject(this._globalVariables);
  		},
  		set: function set(value) {
  			this._globalVariables = JsonSerialisation.JObjectToDictionaryRuntimeObjs(value);
  		}
  	}]);
  	return VariablesState;
  }();

  //Taken from https://gist.github.com/blixt/f17b47c62508be59987b
  //Ink uses a seedable PRNG of which there is none in native javascript.
  var PRNG = function () {
  	function PRNG(seed) {
  		babelHelpers.classCallCheck(this, PRNG);

  		this._seed = seed % 2147483647;
  		if (this._seed <= 0) this._seed += 2147483646;
  	}

  	babelHelpers.createClass(PRNG, [{
  		key: "next",
  		value: function next() {
  			return this._seed = this._seed * 16807 % 2147483647;
  		}
  	}, {
  		key: "nextFloat",
  		value: function nextFloat() {
  			return (this.next() - 1) / 2147483646;
  		}
  	}]);
  	return PRNG;
  }();

  var StoryState = function () {
  	function StoryState(story) {
  		babelHelpers.classCallCheck(this, StoryState);

  		//actual constructor
  		this.story = story;

  		this._outputStream = [];

  		this._evaluationStack = [];

  		this.callStack = new CallStack(story.rootContentContainer);
  		this._variablesState = new VariablesState(this.callStack);

  		this._visitCounts = {};
  		this._turnIndices = {};
  		this._currentTurnIndex = -1;

  		this.divertedTargetObject = null;

  		var timeSeed = new Date().getTime();
  		this.storySeed = new PRNG(timeSeed).next() % 100;
  		this.previousRandom = 0;

  		this._currentChoices = [];
  		this._currentErrors = null;

  		this.didSafeExit = false;

  		this._isExternalFunctionEvaluation = false;
  		this._originalCallstack = null;
  		this._originalEvaluationStackHeight = 0;

  		this.GoToStart();
  	}

  	babelHelpers.createClass(StoryState, [{
  		key: 'MatchRightGlueForLeftGlue',
  		value: function MatchRightGlueForLeftGlue(leftGlue) {
  			if (!leftGlue.isLeft) return null;

  			for (var i = this._outputStream.length - 1; i >= 0; i--) {
  				var c = this._outputStream[i];
  				//			var g = c as Glue;
  				var g = c;
  				if (g instanceof Glue && g.isRight && g.parent == leftGlue.parent) {
  					return g;
  				} else if (c instanceof ControlCommand) // e.g. BeginString
  					break;
  			}

  			return null;
  		}
  	}, {
  		key: 'GoToStart',
  		value: function GoToStart() {
  			this.callStack.currentElement.currentContainer = this.story.mainContentContainer;
  			this.callStack.currentElement.currentContentIndex = 0;
  		}
  	}, {
  		key: 'ResetErrors',
  		value: function ResetErrors() {
  			this._currentErrors = null;
  		}
  	}, {
  		key: 'ResetOutput',
  		value: function ResetOutput() {
  			this._outputStream.length = 0;
  		}
  	}, {
  		key: 'PushEvaluationStack',
  		value: function PushEvaluationStack(obj) {
  			this.evaluationStack.push(obj);
  		}
  	}, {
  		key: 'PopEvaluationStack',
  		value: function PopEvaluationStack(numberOfObjects) {
  			if (!numberOfObjects) {
  				var obj = this.evaluationStack.pop();
  				return obj;
  			} else {
  				if (numberOfObjects > this.evaluationStack.length) {
  					throw "trying to pop too many objects";
  				}

  				var popped = this.evaluationStack.splice(this.evaluationStack.length - numberOfObjects, numberOfObjects);
  				return popped;
  			}
  		}
  	}, {
  		key: 'PeekEvaluationStack',
  		value: function PeekEvaluationStack() {
  			return this.evaluationStack[this.evaluationStack.length - 1];
  		}
  	}, {
  		key: 'PushToOutputStream',
  		value: function PushToOutputStream(obj) {
  			var _this = this;

  			//		var text = obj as StringValue;
  			var text = obj;
  			if (text instanceof StringValue) {
  				var listText = this.TrySplittingHeadTailWhitespace(text);
  				if (listText != null) {
  					listText.forEach(function (textObj) {
  						_this.PushToOutputStreamIndividual(textObj);
  					});
  					return;
  				}
  			}

  			this.PushToOutputStreamIndividual(obj);
  		}
  	}, {
  		key: 'TrySplittingHeadTailWhitespace',
  		value: function TrySplittingHeadTailWhitespace(single) {
  			var str = single.value;

  			var headFirstNewlineIdx = -1;
  			var headLastNewlineIdx = -1;
  			for (var i = 0; i < str.length; ++i) {
  				var c = str[i];
  				if (c == '\n') {
  					if (headFirstNewlineIdx == -1) headFirstNewlineIdx = i;
  					headLastNewlineIdx = i;
  				} else if (c == ' ' || c == '\t') continue;else break;
  			}

  			var tailLastNewlineIdx = -1;
  			var tailFirstNewlineIdx = -1;
  			for (var i = 0; i < str.length; ++i) {
  				var c = str[i];
  				if (c == '\n') {
  					if (tailLastNewlineIdx == -1) tailLastNewlineIdx = i;
  					tailFirstNewlineIdx = i;
  				} else if (c == ' ' || c == '\t') continue;else break;
  			}

  			// No splitting to be done?
  			if (headFirstNewlineIdx == -1 && tailLastNewlineIdx == -1) return null;

  			var listTexts = [];
  			var innerStrStart = 0;
  			var innerStrEnd = str.length;

  			if (headFirstNewlineIdx != -1) {
  				if (headFirstNewlineIdx > 0) {
  					var leadingSpaces = str.substring(0, headFirstNewlineIdx);
  					listTexts.push(leadingSpaces);
  				}
  				listTexts.push(new StringValue("\n"));
  				innerStrStart = headLastNewlineIdx + 1;
  			}

  			if (tailLastNewlineIdx != -1) {
  				innerStrEnd = tailFirstNewlineIdx;
  			}

  			if (innerStrEnd > innerStrStart) {
  				var innerStrText = str.substring(innerStrStart, innerStrEnd - innerStrStart);
  				listTexts.push(new StringValue(innerStrText));
  			}

  			if (tailLastNewlineIdx != -1 && tailFirstNewlineIdx > headLastNewlineIdx) {
  				listTexts.push(new StringValue("\n"));
  				if (tailLastNewlineIdx < str.length - 1) {
  					var numSpaces = str.Length - tailLastNewlineIdx - 1;
  					var trailingSpaces = new StringValue(str.substring(tailLastNewlineIdx + 1, numSpaces));
  					listTexts.push(trailingSpaces);
  				}
  			}

  			return listTexts;
  		}
  	}, {
  		key: 'PushToOutputStreamIndividual',
  		value: function PushToOutputStreamIndividual(obj) {
  			var glue = obj;
  			var text = obj;

  			var includeInOutput = true;

  			if (glue instanceof Glue) {
  				// Found matching left-glue for right-glue? Close it.
  				var existingRightGlue = this.currentRightGlue;
  				var foundMatchingLeftGlue = !!(glue.isLeft && existingRightGlue && glue.parent == existingRightGlue.parent);
  				var matchingRightGlue = null;

  				if (glue.isLeft) matchingRightGlue = this.MatchRightGlueForLeftGlue(glue);

  				// Left/Right glue is auto-generated for inline expressions
  				// where we want to absorb newlines but only in a certain direction.
  				// "Bi" glue is written by the user in their ink with <>
  				if (glue.isLeft || glue.isBi) {
  					this.TrimNewlinesFromOutputStream(matchingRightGlue);
  				}

  				includeInOutput = glue.isBi || glue.isRight;
  			} else if (text instanceof StringValue) {

  				if (this.currentGlueIndex != -1) {

  					// Absorb any new newlines if there's existing glue
  					// in the output stream.
  					// Also trim any extra whitespace (spaces/tabs) if so.
  					if (text.isNewline) {
  						this.TrimFromExistingGlue();
  						includeInOutput = false;
  					}

  					// Able to completely reset when
  					else if (text.isNonWhitespace) {
  							this.RemoveExistingGlue();
  						}
  				} else if (text.isNewline) {
  					if (this.outputStreamEndsInNewline || !this.outputStreamContainsContent) includeInOutput = false;
  				}
  			}

  			if (includeInOutput) {
  				this._outputStream.push(obj);
  			}
  		}
  	}, {
  		key: 'TrimNewlinesFromOutputStream',
  		value: function TrimNewlinesFromOutputStream(rightGlueToStopAt) {
  			var removeWhitespaceFrom = -1;
  			var rightGluePos = -1;
  			var foundNonWhitespace = false;

  			// Work back from the end, and try to find the point where
  			// we need to start removing content. There are two ways:
  			//  - Start from the matching right-glue (because we just saw a left-glue)
  			//  - Simply work backwards to find the first newline in a string of whitespace
  			var i = this._outputStream.length - 1;
  			while (i >= 0) {
  				var obj = this._outputStream[i];
  				//			var cmd = obj as ControlCommand;
  				var cmd = obj;
  				//			var txt = obj as StringValue;
  				var txt = obj;
  				//			var glue = obj as Glue;
  				var glue = obj;

  				if (cmd instanceof ControlCommand || txt instanceof StringValue && txt.isNonWhitespace) {
  					foundNonWhitespace = true;
  					if (rightGlueToStopAt == null) break;
  				} else if (rightGlueToStopAt && glue instanceof Glue && glue == rightGlueToStopAt) {
  					rightGluePos = i;
  					break;
  				} else if (txt instanceof StringValue && txt.isNewline && !foundNonWhitespace) {
  					removeWhitespaceFrom = i;
  				}
  				i--;
  			}

  			// Remove the whitespace
  			if (removeWhitespaceFrom >= 0) {
  				i = removeWhitespaceFrom;
  				while (i < this._outputStream.length) {
  					//				var text = _outputStream [i] as StringValue;
  					var text = this._outputStream[i];
  					if (text instanceof StringValue) {
  						this._outputStream.splice(i, 1);
  					} else {
  						i++;
  					}
  				}
  			}

  			if (rightGlueToStopAt && rightGluePos > -1) {
  				i = rightGluePos;
  				while (i < this._outputStream.length) {
  					if (this._outputStream[i] instanceof Glue && this._outputStream[i].isRight) {
  						this.outputStream.splice(i, 1);
  					} else {
  						i++;
  					}
  				}
  			}
  		}
  	}, {
  		key: 'TrimFromExistingGlue',
  		value: function TrimFromExistingGlue() {
  			var i = this.currentGlueIndex;
  			while (i < this._outputStream.length) {
  				//			var txt = _outputStream [i] as StringValue;
  				var txt = this._outputStream[i];
  				if (txt instanceof StringValue && !txt.isNonWhitespace) this._outputStream.splice(i, 1);else i++;
  			}
  		}
  	}, {
  		key: 'RemoveExistingGlue',
  		value: function RemoveExistingGlue() {
  			for (var i = this._outputStream.length - 1; i >= 0; i--) {
  				var c = this._outputStream[i];
  				if (c instanceof Glue) {
  					this._outputStream.splice(i, 1);
  				} else if (c instanceof ControlCommand) {
  					// e.g. BeginString
  					break;
  				}
  			}
  		}
  	}, {
  		key: 'ForceEnd',
  		value: function ForceEnd() {
  			while (this.callStack.canPopThread) {
  				this.callStack.PopThread();
  			}while (this.callStack.canPop) {
  				this.callStack.Pop();
  			}this.currentChoices.length = 0;

  			this.currentContentObject = null;
  			this.previousContentObject = null;

  			this.didSafeExit = true;
  		}
  	}, {
  		key: 'SetChosenPath',
  		value: function SetChosenPath(path) {
  			// Changing direction, assume we need to clear current set of choices
  			this.currentChoices.length = 0;

  			this.currentPath = path;

  			this._currentTurnIndex++;
  		}
  	}, {
  		key: 'StartExternalFunctionEvaluation',
  		value: function StartExternalFunctionEvaluation(funcContainer, args) {
  			// We'll start a new callstack, so keep hold of the original,
  			// as well as the evaluation stack so we know if the function
  			// returned something
  			this._originalCallstack = this.callStack;
  			this._originalEvaluationStackHeight = this.evaluationStack.length;

  			// Create a new base call stack element.
  			this.callStack = new CallStack(funcContainer);
  			this.callStack.currentElement.type = PushPopType.Function;

  			// By setting ourselves in external function evaluation mode,
  			// we're saying it's okay to end the flow without a Done or End,
  			// but with a ~ return instead.
  			this._isExternalFunctionEvaluation = true;

  			// Pass arguments onto the evaluation stack
  			if (args != null) {
  				for (var i = 0; i < args.length; i++) {
  					if (!(typeof args[i] === 'number' || typeof args[i] === 'string')) {
  						throw "ink arguments when calling EvaluateFunction must be int, float or string";
  					}

  					this.evaluationStack.push(Value.Create(args[i]));
  				}
  			}
  		}
  	}, {
  		key: 'TryExitExternalFunctionEvaluation',
  		value: function TryExitExternalFunctionEvaluation() {
  			if (this._isExternalFunctionEvaluation && this.callStack.elements.length == 1 && this.callStack.currentElement.type == PushPopType.Function) {
  				this.currentContentObject = null;
  				this.didSafeExit = true;
  				return true;
  			}

  			return false;
  		}
  	}, {
  		key: 'CompleteExternalFunctionEvaluation',
  		value: function CompleteExternalFunctionEvaluation() {
  			// Do we have a returned value?
  			// Potentially pop multiple values off the stack, in case we need
  			// to clean up after ourselves (e.g. caller of EvaluateFunction may
  			// have passed too many arguments, and we currently have no way to check for that)
  			var returnedObj = null;
  			while (this.evaluationStack.length > this._originalEvaluationStackHeight) {
  				var poppedObj = this.PopEvaluationStack();
  				if (returnedObj == null) returnedObj = poppedObj;
  			}

  			// Restore our own state
  			this.callStack = this._originalCallstack;
  			this._originalCallstack = null;
  			this._originalEvaluationStackHeight = 0;

  			if (returnedObj) {
  				if (returnedObj instanceof Void) return null;

  				// Some kind of value, if not void
  				//			var returnVal = returnedObj as Runtime.Value;
  				var returnVal = returnedObj;

  				// DivertTargets get returned as the string of components
  				// (rather than a Path, which isn't public)
  				if (returnVal.valueType == ValueType.DivertTarget) {
  					return returnVal.valueObject.toString();
  				}

  				// Other types can just have their exact object type:
  				// int, float, string. VariablePointers get returned as strings.
  				return returnVal.valueObject;
  			}

  			return null;
  		}
  	}, {
  		key: 'AddError',
  		value: function AddError(message) {
  			if (this._currentErrors == null) {
  				this._currentErrors = [];
  			}

  			this._currentErrors.push(message);
  		}
  	}, {
  		key: 'VisitCountAtPathString',
  		value: function VisitCountAtPathString(pathString) {
  			var visitCountOut;
  			if (visitCountOut = this.visitCounts[pathString]) return visitCountOut;

  			return 0;
  		}
  	}, {
  		key: 'Copy',
  		value: function Copy() {
  			var copy = new StoryState(this.story);

  			copy.outputStream.push.apply(copy.outputStream, this._outputStream);
  			copy.currentChoices.push.apply(copy.currentChoices, this.currentChoices);

  			if (this.hasError) {
  				copy.currentErrors = [];
  				copy.currentErrors.push.apply(copy.currentErrors, this.currentErrors);
  			}

  			copy.callStack = new CallStack(this.callStack);

  			copy._variablesState = new VariablesState(copy.callStack);
  			copy.variablesState.CopyFrom(this.variablesState);

  			copy.evaluationStack.push.apply(copy.evaluationStack, this.evaluationStack);

  			if (this.divertedTargetObject != null) copy.divertedTargetObject = this.divertedTargetObject;

  			copy.previousContentObject = this.previousContentObject;

  			copy._visitCounts = this._visitCounts;
  			copy._turnIndices = this._turnIndices;
  			copy._currentTurnIndex = this.currentTurnIndex;
  			copy.storySeed = this.storySeed;
  			copy.previousRandom = this.previousRandom;

  			copy.didSafeExit = this.didSafeExit;

  			return copy;
  		}
  	}, {
  		key: 'toJson',
  		value: function toJson(indented) {
  			return JSON.stringify(this.jsonToken, null, indented ? 2 : 0);
  		}
  	}, {
  		key: 'LoadJson',
  		value: function LoadJson(jsonString) {
  			this.jsonToken = JSON.parse(jsonString);
  		}
  	}, {
  		key: 'currentChoices',
  		get: function get() {
  			return this._currentChoices;
  		}
  	}, {
  		key: 'currentErrors',
  		get: function get() {
  			return this._currentErrors;
  		}
  	}, {
  		key: 'visitCounts',
  		get: function get() {
  			return this._visitCounts;
  		}
  	}, {
  		key: 'turnIndices',
  		get: function get() {
  			return this._turnIndices;
  		}
  	}, {
  		key: 'currentTurnIndex',
  		get: function get() {
  			return this._currentTurnIndex;
  		}
  	}, {
  		key: 'variablesState',
  		get: function get() {
  			return this._variablesState;
  		}
  	}, {
  		key: 'currentContentObject',
  		get: function get() {
  			return this.callStack.currentElement.currentObject;
  		},
  		set: function set(value) {
  			this.callStack.currentElement.currentObject = value;
  		}
  	}, {
  		key: 'hasError',
  		get: function get() {
  			return this.currentErrors != null && this.currentErrors.length > 0;
  		}
  	}, {
  		key: 'inExpressionEvaluation',
  		get: function get() {
  			return this.callStack.currentElement.inExpressionEvaluation;
  		},
  		set: function set(value) {
  			this.callStack.currentElement.inExpressionEvaluation = value;
  		}
  	}, {
  		key: 'evaluationStack',
  		get: function get() {
  			return this._evaluationStack;
  		}
  	}, {
  		key: 'outputStreamEndsInNewline',
  		get: function get() {
  			if (this._outputStream.length > 0) {

  				for (var i = this._outputStream.length - 1; i >= 0; i--) {
  					var obj = this._outputStream[i];
  					if (obj instanceof ControlCommand) // e.g. BeginString
  						break;
  					var text = this._outputStream[i];
  					if (text instanceof StringValue) {
  						if (text.isNewline) return true;else if (text.isNonWhitespace) break;
  					}
  				}
  			}

  			return false;
  		}
  	}, {
  		key: 'outputStreamContainsContent',
  		get: function get() {
  			for (var i = 0; i < this._outputStream.length; i++) {
  				if (this._outputStream[i] instanceof StringValue) return true;
  			}
  			return false;
  		}
  	}, {
  		key: 'currentGlueIndex',
  		get: function get() {
  			for (var i = this._outputStream.length - 1; i >= 0; i--) {
  				var c = this._outputStream[i];
  				//			var glue = c as Glue;
  				var glue = c;
  				if (glue instanceof Glue) return i;else if (c instanceof ControlCommand) // e.g. BeginString
  					break;
  			}
  			return -1;
  		}
  	}, {
  		key: 'currentRightGlue',
  		get: function get() {
  			for (var i = this._outputStream.length - 1; i >= 0; i--) {
  				var c = this._outputStream[i];
  				//			var glue = c as Glue;
  				var glue = c;
  				if (glue instanceof Glue && glue.isRight) return glue;else if (c instanceof ControlCommand) // e.g. BeginString
  					break;
  			}
  			return null;
  		}
  	}, {
  		key: 'inStringEvaluation',
  		get: function get() {
  			for (var i = this._outputStream.length - 1; i >= 0; i--) {
  				//			var cmd = this._outputStream[i] as ControlCommand;
  				var cmd = this._outputStream[i];
  				if (cmd instanceof ControlCommand && cmd.commandType == ControlCommand.CommandType.BeginString) {
  					return true;
  				}
  			}

  			return false;
  		}
  	}, {
  		key: 'currentText',
  		get: function get() {
  			var sb = new StringBuilder();

  			this._outputStream.forEach(function (outputObj) {
  				//			var textContent = outputObj as StringValue;
  				var textContent = outputObj;
  				if (textContent instanceof StringValue) {
  					sb.Append(textContent.value);
  				}
  			});

  			return sb.toString();
  		}
  	}, {
  		key: 'currentTags',
  		get: function get() {
  			var tags = [];

  			this._outputStream.forEach(function (outputObj) {
  				//			var tag = outputObj as Tag;
  				var tag = outputObj;
  				if (tag instanceof Tag) {
  					tags.push(tag.text);
  				}
  			});

  			return tags;
  		}
  	}, {
  		key: 'outputStream',
  		get: function get() {
  			return this._outputStream;
  		}
  	}, {
  		key: 'currentPath',
  		get: function get() {
  			if (this.currentContentObject == null) return null;

  			return this.currentContentObject.path;
  		},
  		set: function set(value) {
  			if (value != null) this.currentContentObject = this.story.ContentAtPath(value);else this.currentContentObject = null;
  		}
  	}, {
  		key: 'currentContainer',
  		get: function get() {
  			return this.callStack.currentElement.currentContainer;
  		}
  	}, {
  		key: 'previousContentObject',
  		get: function get() {
  			return this.callStack.currentThread.previousContentObject;
  		},
  		set: function set(value) {
  			this.callStack.currentThread.previousContentObject = value;
  		}
  	}, {
  		key: 'jsonToken',
  		get: function get() {
  			var _this2 = this;

  			var obj = {};

  			var choiceThreads = null;
  			this.currentChoices.forEach(function (c) {
  				c.originalChoicePath = c.choicePoint.path.componentsString;
  				c.originalThreadIndex = c.threadAtGeneration.threadIndex;

  				if (_this2.callStack.ThreadWithIndex(c.originalThreadIndex) == null) {
  					if (choiceThreads == null) choiceThreads = {};

  					choiceThreads[c.originalThreadIndex.toString()] = c.threadAtGeneration.jsonToken;
  				}
  			});

  			if (this.choiceThreads != null) obj["choiceThreads"] = this.choiceThreads;

  			obj["callstackThreads"] = this.callStack.GetJsonToken();
  			obj["variablesState"] = this.variablesState.jsonToken;

  			obj["evalStack"] = JsonSerialisation.ListToJArray(this.evaluationStack);

  			obj["outputStream"] = JsonSerialisation.ListToJArray(this._outputStream);

  			obj["currentChoices"] = JsonSerialisation.ListToJArray(this.currentChoices);

  			if (this.divertedTargetObject != null) obj["currentDivertTarget"] = this.divertedTargetObject.path.componentsString;

  			obj["visitCounts"] = JsonSerialisation.IntDictionaryToJObject(this.visitCounts);
  			obj["turnIndices"] = JsonSerialisation.IntDictionaryToJObject(this.turnIndices);
  			obj["turnIdx"] = this.currentTurnIndex;
  			obj["storySeed"] = this.storySeed;

  			obj["inkSaveVersion"] = StoryState.kInkSaveStateVersion;

  			// Not using this right now, but could do in future.
  			obj["inkFormatVersion"] = this.story.inkVersionCurrent;

  			return obj;
  		},
  		set: function set(value) {
  			var _this3 = this;

  			var jObject = value;

  			var jSaveVersion = jObject["inkSaveVersion"];
  			if (jSaveVersion == null) {
  				throw new StoryException("ink save format incorrect, can't load.");
  			} else if (parseInt(jSaveVersion) < StoryState.kMinCompatibleLoadVersion) {
  				throw new StoryException("Ink save format isn't compatible with the current version (saw '" + jSaveVersion + "', but minimum is " + StoryState.kMinCompatibleLoadVersion + "), so can't load.");
  			}

  			this.callStack.SetJsonToken(jObject["callstackThreads"], this.story);
  			this.variablesState.jsonToken = jObject["variablesState"];

  			this._evaluationStack = JsonSerialisation.JArrayToRuntimeObjList(jObject["evalStack"]);

  			this._outputStream = JsonSerialisation.JArrayToRuntimeObjList(jObject["outputStream"]);

  			//		currentChoices = Json.JArrayToRuntimeObjList<Choice>((JArray)jObject ["currentChoices"]);
  			this._currentChoices = JsonSerialisation.JArrayToRuntimeObjList(jObject["currentChoices"]);

  			var currentDivertTargetPath = jObject["currentDivertTarget"];
  			if (currentDivertTargetPath != null) {
  				var divertPath = new Path$1(currentDivertTargetPath.toString());
  				this.divertedTargetObject = this.story.ContentAtPath(divertPath);
  			}

  			this._visitCounts = JsonSerialisation.JObjectToIntDictionary(jObject["visitCounts"]);
  			this._turnIndices = JsonSerialisation.JObjectToIntDictionary(jObject["turnIndices"]);
  			this._currentTurnIndex = parseInt(jObject["turnIdx"]);
  			this.storySeed = parseInt(jObject["storySeed"]);

  			//		var jChoiceThreads = jObject["choiceThreads"] as JObject;
  			var jChoiceThreads = jObject["choiceThreads"];

  			this.currentChoices.forEach(function (c) {
  				c.choicePoint = _this3.story.ContentAtPath(new Path$1(c.originalChoicePath));

  				var foundActiveThread = _this3.callStack.ThreadWithIndex(c.originalThreadIndex);
  				if (foundActiveThread != null) {
  					c.threadAtGeneration = foundActiveThread;
  				} else {
  					var jSavedChoiceThread = jChoiceThreads[c.originalThreadIndex.toString()];
  					c.threadAtGeneration = new CallStack.Thread(jSavedChoiceThread, _this3.story);
  				}
  			});
  		}
  	}]);
  	return StoryState;
  }();

  StoryState.kInkSaveStateVersion = 5;
  StoryState.kMinCompatibleLoadVersion = 4;

  if (!Number.isInteger) {
  	Number.isInteger = function isInteger(nVal) {
  		return typeof nVal === "number" && isFinite(nVal) && nVal > -9007199254740992 && nVal < 9007199254740992 && Math.floor(nVal) === nVal;
  	};
  }

  var Story = function (_InkObject) {
  	babelHelpers.inherits(Story, _InkObject);

  	function Story(jsonString) {
  		babelHelpers.classCallCheck(this, Story);

  		var _this = babelHelpers.possibleConstructorReturn(this, Object.getPrototypeOf(Story).call(this));

  		_this.inkVersionCurrent = 15;
  		_this.inkVersionMinimumCompatible = 15;

  		_this._variableObservers = null;
  		_this._externals = {};

  		if (jsonString instanceof Container) {
  			_this._mainContentContainer = jsonString;
  		} else {
  			//the original version only accepts a string as a constructor, but this is javascript and it's almost easier to get a JSON value than a string, so we're silently accepting btoh
  			var rootObject = typeof jsonString === 'string' ? JSON.parse(jsonString) : jsonString;

  			var versionObj = rootObject["inkVersion"];
  			if (versionObj == null) throw "ink version number not found. Are you sure it's a valid .ink.json file?";

  			var formatFromFile = parseInt(versionObj);
  			if (formatFromFile > _this.inkVersionCurrent) {
  				throw "Version of ink used to build story was newer than the current verison of the engine";
  			} else if (formatFromFile < _this.inkVersionMinimumCompatible) {
  				throw "Version of ink used to build story is too old to be loaded by this verison of the engine";
  			} else if (formatFromFile != _this.inkVersionCurrent) {
  				console.warn("WARNING: Version of ink used to build story doesn't match current version of engine. Non-critical, but recommend synchronising.");
  			}

  			var rootToken = rootObject["root"];
  			if (rootToken == null) throw "Root node for ink not found. Are you sure it's a valid .ink.json file?";

  			_this._mainContentContainer = JsonSerialisation.JTokenToRuntimeObject(rootToken);

  			_this._hasValidatedExternals = null;
  			_this.allowExternalFunctionFallbacks = false;

  			_this.ResetState();
  		}
  		return _this;
  	}

  	babelHelpers.createClass(Story, [{
  		key: 'ToJsonString',
  		value: function ToJsonString() {
  			var rootContainerJsonList = JsonSerialisation.RuntimeObjectToJToken(this._mainContentContainer);

  			var rootObject = {};
  			rootObject["inkVersion"] = this.inkVersionCurrent;
  			rootObject["root"] = rootContainerJsonList;

  			return JSON.stringify(rootObject);
  		}
  	}, {
  		key: 'ResetState',
  		value: function ResetState() {
  			this._state = new StoryState(this);
  			this._state.variablesState.ObserveVariableChange(this.VariableStateDidChangeEvent.bind(this));

  			this.ResetGlobals();
  		}
  	}, {
  		key: 'ResetErrors',
  		value: function ResetErrors() {
  			this._state.ResetErrors();
  		}
  	}, {
  		key: 'ResetCallstack',
  		value: function ResetCallstack() {
  			this._state.ForceEnd();
  		}
  	}, {
  		key: 'ResetGlobals',
  		value: function ResetGlobals() {
  			if (this._mainContentContainer.namedContent["global decl"]) {
  				var originalPath = this.state.currentPath;

  				this.ChoosePathString("global decl");

  				// Continue, but without validating external bindings,
  				// since we may be doing this reset at initialisation time.
  				this.ContinueInternal();

  				this.state.currentPath = originalPath;
  			}
  		}
  	}, {
  		key: 'Continue',
  		value: function Continue() {
  			if (!this._hasValidatedExternals) this.ValidateExternalBindings();

  			return this.ContinueInternal();
  		}
  	}, {
  		key: 'ContinueInternal',
  		value: function ContinueInternal() {
  			if (!this.canContinue) {
  				throw new StoryException("Can't continue - should check canContinue before calling Continue");
  			}

  			this._state.ResetOutput();

  			this._state.didSafeExit = false;

  			this._state.variablesState.batchObservingVariableChanges = true;

  			try {

  				var stateAtLastNewline = null;

  				// The basic algorithm here is:
  				//
  				//     do { Step() } while( canContinue && !outputStreamEndsInNewline );
  				//
  				// But the complexity comes from:
  				//  - Stepping beyond the newline in case it'll be absorbed by glue later
  				//  - Ensuring that non-text content beyond newlines are generated - i.e. choices,
  				//    which are actually built out of text content.
  				// So we have to take a snapshot of the state, continue prospectively,
  				// and rewind if necessary.
  				// This code is slightly fragile :-/
  				//

  				do {

  					// Run main step function (walks through content)
  					this.Step();

  					// Run out of content and we have a default invisible choice that we can follow?
  					if (!this.canContinue) {
  						this.TryFollowDefaultInvisibleChoice();
  					}

  					// Don't save/rewind during string evaluation, which is e.g. used for choices
  					if (!this.state.inStringEvaluation) {

  						// We previously found a newline, but were we just double checking that
  						// it wouldn't immediately be removed by glue?
  						if (stateAtLastNewline != null) {

  							// Cover cases that non-text generated content was evaluated last step
  							var currText = this.currentText;
  							var prevTextLength = stateAtLastNewline.currentText.length;
  							var prevTagCount = stateAtLastNewline.currentTags.length;

  							// Output has been extended?
  							if (currText !== stateAtLastNewline.currentText || prevTagCount != this.currentTags.length) {

  								// Original newline still exists?
  								if (currText.length >= prevTextLength && currText[prevTextLength - 1] == '\n') {

  									this.RestoreStateSnapshot(stateAtLastNewline);
  									break;
  								}

  								// Newline that previously existed is no longer valid - e.g.
  								// glue was encounted that caused it to be removed.
  								else {
  										stateAtLastNewline = null;
  									}
  							}
  						}

  						// Current content ends in a newline - approaching end of our evaluation
  						if (this.state.outputStreamEndsInNewline) {

  							// If we can continue evaluation for a bit:
  							// Create a snapshot in case we need to rewind.
  							// We're going to continue stepping in case we see glue or some
  							// non-text content such as choices.
  							if (this.canContinue) {
  								stateAtLastNewline = this.StateSnapshot();
  							}

  							// Can't continue, so we're about to exit - make sure we
  							// don't have an old state hanging around.
  							else {
  									stateAtLastNewline = null;
  								}
  						}
  					}
  				} while (this.canContinue);

  				// Need to rewind, due to evaluating further than we should?
  				if (stateAtLastNewline != null) {
  					this.RestoreStateSnapshot(stateAtLastNewline);
  				}

  				// Finished a section of content / reached a choice point?
  				if (!this.canContinue) {

  					if (this.state.callStack.canPopThread) {
  						this.Error("Thread available to pop, threads should always be flat by the end of evaluation?");
  					}

  					if (this.currentChoices.length == 0 && !this.state.didSafeExit && this._temporaryEvaluationContainer == null) {
  						if (this.state.callStack.CanPop(PushPopType.Tunnel)) {
  							this.Error("unexpectedly reached end of content. Do you need a '->->' to return from a tunnel?");
  						} else if (this.state.callStack.CanPop(PushPopType.Function)) {
  							this.Error("unexpectedly reached end of content. Do you need a '~ return'?");
  						} else if (!this.state.callStack.canPop) {
  							this.Error("ran out of content. Do you need a '-> DONE' or '-> END'?");
  						} else {
  							this.Error("unexpectedly reached end of content for unknown reason. Please debug compiler!");
  						}
  					}
  				}
  			} catch (e) {
  				throw e;
  				this.AddError(e.Message, e.useEndLineNumber);
  			} finally {
  				this.state.didSafeExit = false;

  				this._state.variablesState.batchObservingVariableChanges = false;
  			}

  			return this.currentText;
  		}
  	}, {
  		key: 'ContinueMaximally',
  		value: function ContinueMaximally() {
  			var sb = new StringBuilder();

  			while (this.canContinue) {
  				sb.Append(this.Continue());
  			}

  			return sb.toString();
  		}
  	}, {
  		key: 'ContentAtPath',
  		value: function ContentAtPath(path) {
  			return this.mainContentContainer.ContentAtPath(path);
  		}
  	}, {
  		key: 'StateSnapshot',
  		value: function StateSnapshot() {
  			return this.state.Copy();
  		}
  	}, {
  		key: 'RestoreStateSnapshot',
  		value: function RestoreStateSnapshot(state) {
  			this._state = state;
  		}
  	}, {
  		key: 'Step',
  		value: function Step() {
  			var shouldAddToStream = true;

  			// Get current content
  			var currentContentObj = this.state.currentContentObject;
  			if (currentContentObj == null) {
  				return;
  			}
  			// Step directly to the first element of content in a container (if necessary)
  			//		Container currentContainer = currentContentObj as Container;
  			var currentContainer = currentContentObj;
  			while (currentContainer instanceof Container) {

  				// Mark container as being entered
  				this.VisitContainer(currentContainer, true);

  				// No content? the most we can do is step past it
  				if (currentContainer.content.length == 0) break;

  				currentContentObj = currentContainer.content[0];
  				this.state.callStack.currentElement.currentContentIndex = 0;
  				this.state.callStack.currentElement.currentContainer = currentContainer;

  				//			currentContainer = currentContentObj as Container;
  				currentContainer = currentContentObj;
  			}
  			currentContainer = this.state.callStack.currentElement.currentContainer;

  			// Is the current content object:
  			//  - Normal content
  			//  - Or a logic/flow statement - if so, do it
  			// Stop flow if we hit a stack pop when we're unable to pop (e.g. return/done statement in knot
  			// that was diverted to rather than called as a function)
  			var isLogicOrFlowControl = this.PerformLogicAndFlowControl(currentContentObj);

  			// Has flow been forced to end by flow control above?
  			if (this.state.currentContentObject == null) {
  				return;
  			}

  			if (isLogicOrFlowControl) {
  				shouldAddToStream = false;
  			}

  			// Choice with condition?
  			//		var choicePoint = currentContentObj as ChoicePoint;
  			var choicePoint = currentContentObj;
  			if (choicePoint instanceof ChoicePoint) {
  				var choice = this.ProcessChoice(choicePoint);
  				if (choice) {
  					this.state.currentChoices.push(choice);
  				}

  				currentContentObj = null;
  				shouldAddToStream = false;
  			}

  			// If the container has no content, then it will be
  			// the "content" itself, but we skip over it.
  			if (currentContentObj instanceof Container) {
  				shouldAddToStream = false;
  			}

  			// Content to add to evaluation stack or the output stream
  			if (shouldAddToStream) {

  				// If we're pushing a variable pointer onto the evaluation stack, ensure that it's specific
  				// to our current (possibly temporary) context index. And make a copy of the pointer
  				// so that we're not editing the original runtime object.
  				//			var varPointer = currentContentObj as VariablePointerValue;
  				var varPointer = currentContentObj;
  				if (varPointer instanceof VariablePointerValue && varPointer.contextIndex == -1) {

  					// Create new object so we're not overwriting the story's own data
  					var contextIdx = this.state.callStack.ContextForVariableNamed(varPointer.variableName);
  					currentContentObj = new VariablePointerValue(varPointer.variableName, contextIdx);
  				}

  				// Expression evaluation content
  				if (this.state.inExpressionEvaluation) {
  					this.state.PushEvaluationStack(currentContentObj);
  				}
  				// Output stream content (i.e. not expression evaluation)
  				else {
  						this.state.PushToOutputStream(currentContentObj);
  					}
  			}

  			// Increment the content pointer, following diverts if necessary
  			this.NextContent();

  			// Starting a thread should be done after the increment to the content pointer,
  			// so that when returning from the thread, it returns to the content after this instruction.
  			//		var controlCmd = currentContentObj as ControlCommand;
  			var controlCmd = currentContentObj;
  			if (controlCmd instanceof ControlCommand && controlCmd.commandType == ControlCommand.CommandType.StartThread) {
  				this.state.callStack.PushThread();
  			}
  		}
  	}, {
  		key: 'VisitContainer',
  		value: function VisitContainer(container, atStart) {
  			if (!container.countingAtStartOnly || atStart) {
  				if (container.visitsShouldBeCounted) this.IncrementVisitCountForContainer(container);

  				if (container.turnIndexShouldBeCounted) this.RecordTurnIndexVisitToContainer(container);
  			}
  		}
  	}, {
  		key: 'VisitChangedContainersDueToDivert',
  		value: function VisitChangedContainersDueToDivert() {
  			var previousContentObject = this.state.previousContentObject;
  			var newContentObject = this.state.currentContentObject;

  			if (!newContentObject) return;

  			// First, find the previously open set of containers
  			var prevContainerSet = [];
  			if (previousContentObject) {
  				//			Container prevAncestor = previousContentObject as Container ?? previousContentObject.parent as Container;
  				var prevAncestor = previousContentObject instanceof Container ? previousContentObject : previousContentObject.parent;
  				while (prevAncestor instanceof Container) {
  					prevContainerSet.push(prevAncestor);
  					//				prevAncestor = prevAncestor.parent as Container;
  					prevAncestor = prevAncestor.parent;
  				}
  			}

  			// If the new object is a container itself, it will be visited automatically at the next actual
  			// content step. However, we need to walk up the new ancestry to see if there are more new containers
  			var currentChildOfContainer = newContentObject;
  			//		Container currentContainerAncestor = currentChildOfContainer.parent as Container;
  			var currentContainerAncestor = currentChildOfContainer.parent;
  			while (currentContainerAncestor instanceof Container && prevContainerSet.indexOf(currentContainerAncestor) < 0) {

  				// Check whether this ancestor container is being entered at the start,
  				// by checking whether the child object is the first.
  				var enteringAtStart = currentContainerAncestor.content.length > 0 && currentChildOfContainer == currentContainerAncestor.content[0];

  				// Mark a visit to this container
  				this.VisitContainer(currentContainerAncestor, enteringAtStart);

  				currentChildOfContainer = currentContainerAncestor;
  				//			currentContainerAncestor = currentContainerAncestor.parent as Container;
  				currentContainerAncestor = currentContainerAncestor.parent;
  			}
  		}
  	}, {
  		key: 'ProcessChoice',
  		value: function ProcessChoice(choicePoint) {
  			var showChoice = true;

  			// Don't create choice if choice point doesn't pass conditional
  			if (choicePoint.hasCondition) {
  				var conditionValue = this.state.PopEvaluationStack();
  				if (!this.IsTruthy(conditionValue)) {
  					showChoice = false;
  				}
  			}

  			var startText = "";
  			var choiceOnlyText = "";

  			if (choicePoint.hasChoiceOnlyContent) {
  				//			var choiceOnlyStrVal = state.PopEvaluationStack () as StringValue;
  				var choiceOnlyStrVal = this.state.PopEvaluationStack();
  				choiceOnlyText = choiceOnlyStrVal.value;
  			}

  			if (choicePoint.hasStartContent) {
  				//			var startStrVal = state.PopEvaluationStack () as StringValue;
  				var startStrVal = this.state.PopEvaluationStack();
  				startText = startStrVal.value;
  			}

  			// Don't create choice if player has already read this content
  			if (choicePoint.onceOnly) {
  				var visitCount = this.VisitCountForContainer(choicePoint.choiceTarget);
  				if (visitCount > 0) {
  					showChoice = false;
  				}
  			}

  			var choice = new Choice(choicePoint);
  			choice.threadAtGeneration = this.state.callStack.currentThread.Copy();

  			// We go through the full process of creating the choice above so
  			// that we consume the content for it, since otherwise it'll
  			// be shown on the output stream.
  			if (!showChoice) {
  				return null;
  			}

  			// Set final text for the choice
  			choice.text = startText + choiceOnlyText;

  			return choice;
  		}
  	}, {
  		key: 'IsTruthy',
  		value: function IsTruthy(obj) {
  			var truthy = false;
  			if (obj instanceof Value) {
  				var val = obj;

  				if (val instanceof DivertTargetValue) {
  					var divTarget = val;
  					this.Error("Shouldn't use a divert target (to " + divTarget.targetPath + ") as a conditional value. Did you intend a function call 'likeThis()' or a read count check 'likeThis'? (no arrows)");
  					return false;
  				}

  				return val.isTruthy;
  			}
  			return truthy;
  		}
  	}, {
  		key: 'PerformLogicAndFlowControl',
  		value: function PerformLogicAndFlowControl(contentObj) {
  			if (contentObj == null) {
  				return false;
  			}

  			// Divert
  			if (contentObj instanceof Divert) {
  				var currentDivert = contentObj;

  				if (currentDivert.isConditional) {
  					var conditionValue = this.state.PopEvaluationStack();

  					// False conditional? Cancel divert
  					if (!this.IsTruthy(conditionValue)) return true;
  				}

  				if (currentDivert.hasVariableTarget) {
  					var varName = currentDivert.variableDivertName;

  					var varContents = this.state.variablesState.GetVariableWithName(varName);

  					if (!(varContents instanceof DivertTargetValue)) {

  						//					var intContent = varContents as IntValue;
  						var intContent = varContents;

  						var errorMessage = "Tried to divert to a target from a variable, but the variable (" + varName + ") didn't contain a divert target, it ";
  						if (intContent instanceof IntValue && intContent.value == 0) {
  							errorMessage += "was empty/null (the value 0).";
  						} else {
  							errorMessage += "contained '" + varContents + "'.";
  						}

  						this.Error(errorMessage);
  					}

  					var target = varContents;
  					this.state.divertedTargetObject = this.ContentAtPath(target.targetPath);
  				} else if (currentDivert.isExternal) {
  					this.CallExternalFunction(currentDivert.targetPathString, currentDivert.externalArgs);
  					return true;
  				} else {
  					this.state.divertedTargetObject = currentDivert.targetContent;
  				}

  				if (currentDivert.pushesToStack) {
  					this.state.callStack.Push(currentDivert.stackPushType);
  				}

  				if (this.state.divertedTargetObject == null && !currentDivert.isExternal) {

  					// Human readable name available - runtime divert is part of a hard-written divert that to missing content
  					if (currentDivert && currentDivert.debugMetadata.sourceName != null) {
  						this.Error("Divert target doesn't exist: " + currentDivert.debugMetadata.sourceName);
  					} else {
  						this.Error("Divert resolution failed: " + currentDivert);
  					}
  				}

  				return true;
  			}

  			// Start/end an expression evaluation? Or print out the result?
  			else if (contentObj instanceof ControlCommand) {
  					var evalCommand = contentObj;

  					switch (evalCommand.commandType) {

  						case ControlCommand.CommandType.EvalStart:
  							if (this.state.inExpressionEvaluation) console.warn("Already in expression evaluation?");
  							this.state.inExpressionEvaluation = true;
  							break;

  						case ControlCommand.CommandType.EvalEnd:
  							if (!this.state.inExpressionEvaluation) console.warn("Not in expression evaluation mode");
  							this.state.inExpressionEvaluation = false;
  							break;

  						case ControlCommand.CommandType.EvalOutput:

  							// If the expression turned out to be empty, there may not be anything on the stack
  							if (this.state.evaluationStack.length > 0) {

  								var output = this.state.PopEvaluationStack();

  								// Functions may evaluate to Void, in which case we skip output
  								if (!(output instanceof Void)) {
  									// TODO: Should we really always blanket convert to string?
  									// It would be okay to have numbers in the output stream the
  									// only problem is when exporting text for viewing, it skips over numbers etc.
  									var text = new StringValue(output.toString());

  									this.state.PushToOutputStream(text);
  								}
  							}
  							break;

  						case ControlCommand.CommandType.NoOp:
  							break;

  						case ControlCommand.CommandType.Duplicate:
  							this.state.PushEvaluationStack(this.state.PeekEvaluationStack());
  							break;

  						case ControlCommand.CommandType.PopEvaluatedValue:
  							this.state.PopEvaluationStack();
  							break;

  						case ControlCommand.CommandType.PopFunction:
  						case ControlCommand.CommandType.PopTunnel:

  							var popType = evalCommand.commandType == ControlCommand.CommandType.PopFunction ? PushPopType.Function : PushPopType.Tunnel;

  							var overrideTunnelReturnTarget = null;
  							if (popType == PushPopType.Tunnel) {
  								var popped = this.state.PopEvaluationStack();
  								//					overrideTunnelReturnTarget = popped as DivertTargetValue;
  								overrideTunnelReturnTarget = popped;
  								if (overrideTunnelReturnTarget instanceof DivertTargetValue === false) {
  									if (popped instanceof Void === false) {
  										throw "Expected void if ->-> doesn't override target";
  									} else {
  										overrideTunnelReturnTarget = null;
  									}
  								}
  							}

  							if (this.state.TryExitExternalFunctionEvaluation()) {
  								break;
  							} else if (this.state.callStack.currentElement.type != popType || !this.state.callStack.canPop) {

  								var names = {};
  								names[PushPopType.Function] = "function return statement (~ return)";
  								names[PushPopType.Tunnel] = "tunnel onwards statement (->->)";

  								var expected = names[this.state.callStack.currentElement.type];
  								if (!this.state.callStack.canPop) expected = "end of flow (-> END or choice)";

  								var errorMsg = "Found " + names[popType] + ", when expected " + expected;

  								this.Error(errorMsg);
  							} else {
  								this.state.callStack.Pop();

  								if (overrideTunnelReturnTarget) this.state.divertedTargetObject = this.ContentAtPath(overrideTunnelReturnTarget.targetPath);
  							}
  							break;

  						case ControlCommand.CommandType.BeginString:
  							this.state.PushToOutputStream(evalCommand);

  							if (!this.state.inExpressionEvaluation) console.warn("Expected to be in an expression when evaluating a string");
  							this.state.inExpressionEvaluation = false;
  							break;

  						case ControlCommand.CommandType.EndString:

  							var contentStackForString = [];

  							var outputCountConsumed = 0;
  							for (var i = this.state.outputStream.length - 1; i >= 0; --i) {
  								var obj = this.state.outputStream[i];

  								outputCountConsumed++;

  								//					var command = obj as ControlCommand;
  								var command = obj;
  								if (command instanceof ControlCommand && command.commandType == ControlCommand.CommandType.BeginString) {
  									break;
  								}

  								if (obj instanceof StringValue) contentStackForString.push(obj);
  							}

  							// Consume the content that was produced for this string
  							this.state.outputStream.splice(this.state.outputStream.length - outputCountConsumed, outputCountConsumed);

  							//the C# version uses a Stack for contentStackForString, but we're using a simple array, so we need to reverse it before using it
  							contentStackForString = contentStackForString.reverse();

  							// Build string out of the content we collected
  							var sb = new StringBuilder();
  							contentStackForString.forEach(function (c) {
  								sb.Append(c.toString());
  							});

  							// Return to expression evaluation (from content mode)
  							this.state.inExpressionEvaluation = true;
  							this.state.PushEvaluationStack(new StringValue(sb.toString()));
  							break;

  						case ControlCommand.CommandType.ChoiceCount:
  							var choiceCount = this.currentChoices.length;
  							this.state.PushEvaluationStack(new IntValue(choiceCount));
  							break;

  						case ControlCommand.CommandType.TurnsSince:
  							var target = this.state.PopEvaluationStack();
  							if (!(target instanceof DivertTargetValue)) {
  								var extraNote = "";
  								if (target instanceof IntValue) extraNote = ". Did you accidentally pass a read count ('knot_name') instead of a target ('-> knot_name')?";
  								this.Error("TURNS_SINCE expected a divert target (knot, stitch, label name), but saw " + target + extraNote);
  								break;
  							}

  							//				var divertTarget = target as DivertTargetValue;
  							var divertTarget = target;
  							//				var container = ContentAtPath (divertTarget.targetPath) as Container;
  							var container = this.ContentAtPath(divertTarget.targetPath);
  							var turnCount = this.TurnsSinceForContainer(container);
  							this.state.PushEvaluationStack(new IntValue(turnCount));
  							break;

  						case ControlCommand.CommandType.Random:
  							var maxInt = this.state.PopEvaluationStack();
  							var minInt = this.state.PopEvaluationStack();

  							if (minInt == null || minInt instanceof IntValue === false) this.Error("Invalid value for minimum parameter of RANDOM(min, max)");

  							if (maxInt == null || minInt instanceof IntValue === false) this.Error("Invalid value for maximum parameter of RANDOM(min, max)");

  							// +1 because it's inclusive of min and max, for e.g. RANDOM(1,6) for a dice roll.
  							var randomRange = maxInt.value - minInt.value + 1;
  							if (randomRange <= 0) this.Error("RANDOM was called with minimum as " + minInt.value + " and maximum as " + maxInt.value + ". The maximum must be larger");

  							var resultSeed = this.state.storySeed + this.state.previousRandom;
  							var random = new PRNG(resultSeed);

  							var nextRandom = random.next();
  							var chosenValue = nextRandom % randomRange + minInt.value;
  							this.state.PushEvaluationStack(new IntValue(chosenValue));

  							// Next random number (rather than keeping the Random object around)
  							this.state.previousRandom = nextRandom;
  							break;

  						case ControlCommand.CommandType.SeedRandom:
  							var seed = this.state.PopEvaluationStack();
  							if (seed == null || seed instanceof IntValue === false) this.Error("Invalid value passed to SEED_RANDOM");

  							// Story seed affects both RANDOM and shuffle behaviour
  							this.state.storySeed = seed.value;
  							this.state.previousRandom = 0;

  							// SEED_RANDOM returns nothing.
  							this.state.PushEvaluationStack(new Void());
  							break;

  						case ControlCommand.CommandType.VisitIndex:
  							var count = this.VisitCountForContainer(this.state.currentContainer) - 1; // index not count
  							this.state.PushEvaluationStack(new IntValue(count));
  							break;

  						case ControlCommand.CommandType.SequenceShuffleIndex:
  							var shuffleIndex = this.NextSequenceShuffleIndex();
  							this.state.PushEvaluationStack(new IntValue(shuffleIndex));
  							break;

  						case ControlCommand.CommandType.StartThread:
  							// Handled in main step function
  							break;

  						case ControlCommand.CommandType.Done:

  							// We may exist in the context of the initial
  							// act of creating the thread, or in the context of
  							// evaluating the content.
  							if (this.state.callStack.canPopThread) {
  								this.state.callStack.PopThread();
  							}

  							// In normal flow - allow safe exit without warning
  							else {
  									this.state.didSafeExit = true;

  									// Stop flow in current thread
  									this.state.currentContentObject = null;
  								}

  							break;

  						// Force flow to end completely
  						case ControlCommand.CommandType.End:
  							this.state.ForceEnd();
  							break;

  						default:
  							this.Error("unhandled ControlCommand: " + evalCommand);
  							break;
  					}

  					return true;
  				}

  				// Variable assignment
  				else if (contentObj instanceof VariableAssignment) {
  						var varAss = contentObj;
  						var assignedVal = this.state.PopEvaluationStack();

  						// When in temporary evaluation, don't create new variables purely within
  						// the temporary context, but attempt to create them globally
  						//var prioritiseHigherInCallStack = _temporaryEvaluationContainer != null;

  						this.state.variablesState.Assign(varAss, assignedVal);

  						return true;
  					}

  					// Variable reference
  					else if (contentObj instanceof VariableReference) {
  							var varRef = contentObj;
  							var foundValue = null;

  							// Explicit read count value
  							if (varRef.pathForCount != null) {

  								var container = varRef.containerForCount;
  								var count = this.VisitCountForContainer(container);
  								foundValue = new IntValue(count);
  							}

  							// Normal variable reference
  							else {

  									foundValue = this.state.variablesState.GetVariableWithName(varRef.name);

  									if (foundValue == null) {
  										this.Error("Uninitialised variable: " + varRef.name);
  										foundValue = new IntValue(0);
  									}
  								}

  							this.state.evaluationStack.push(foundValue);

  							return true;
  						}

  						// Native function call
  						else if (contentObj instanceof NativeFunctionCall) {
  								var func = contentObj;
  								var funcParams = this.state.PopEvaluationStack(func.numberOfParameters);
  								var result = func.Call(funcParams);
  								this.state.evaluationStack.push(result);
  								return true;
  							}

  			// No control content, must be ordinary content
  			return false;
  		}
  	}, {
  		key: 'ChoosePathString',
  		value: function ChoosePathString(path) {
  			this.ChoosePath(new Path$1(path));
  		}
  	}, {
  		key: 'ChoosePath',
  		value: function ChoosePath(path) {
  			this.state.SetChosenPath(path);

  			// Take a note of newly visited containers for read counts etc
  			this.VisitChangedContainersDueToDivert();
  		}
  	}, {
  		key: 'ChooseChoiceIndex',
  		value: function ChooseChoiceIndex(choiceIdx) {
  			choiceIdx = choiceIdx;
  			var choices = this.currentChoices;
  			if (choiceIdx < 0 || choiceIdx > choices.length) console.warn("choice out of range");

  			// Replace callstack with the one from the thread at the choosing point,
  			// so that we can jump into the right place in the flow.
  			// This is important in case the flow was forked by a new thread, which
  			// can create multiple leading edges for the story, each of
  			// which has its own context.
  			var choiceToChoose = choices[choiceIdx];
  			this.state.callStack.currentThread = choiceToChoose.threadAtGeneration;

  			this.ChoosePath(choiceToChoose.choicePoint.choiceTarget.path);
  		}
  	}, {
  		key: 'HasFunction',
  		value: function HasFunction(functionName) {
  			try {
  				return this.ContentAtPath(new Path$1(functionName)) instanceof Container;
  			} catch (e) {
  				return false;
  			}
  		}
  	}, {
  		key: 'EvaluateFunction',
  		value: function EvaluateFunction(functionName, args, returnTextOutput) {
  			//EvaluateFunction behaves slightly differently than the C# version. In C#, you can pass a (second) parameter `out textOutput` to get the text outputted by the function. This is not possible in js. Instead, we maintain the regular signature (functionName, args), plus an optional third parameter returnTextOutput. If set to true, we will return both the textOutput and the returned value, as an object.
  			returnTextOutput = !!returnTextOutput;

  			if (functionName == null) {
  				throw "Function is null";
  			} else if (functionName == '' || functionName.trim() == '') {
  				throw "Function is empty or white space.";
  			}

  			var funcContainer = null;
  			try {
  				funcContainer = this.ContentAtPath(new Path$1(functionName));
  			} catch (e) {
  				if (e.message.indexOf("not found") >= 0) throw "Function doesn't exist: '" + functionName + "'";else throw e;
  			}

  			this.state.StartExternalFunctionEvaluation(funcContainer, args);

  			// Evaluate the function, and collect the string output
  			var stringOutput = new StringBuilder();
  			while (this.canContinue) {
  				stringOutput.Append(this.Continue());
  			}
  			var textOutput = stringOutput.toString();

  			var result = this.state.CompleteExternalFunctionEvaluation();

  			return returnTextOutput ? { 'returned': result, 'output': textOutput } : result;
  		}
  	}, {
  		key: 'EvaluateExpression',
  		value: function EvaluateExpression(exprContainer) {
  			var startCallStackHeight = this.state.callStack.elements.length;

  			this.state.callStack.Push(PushPopType.Tunnel);

  			this._temporaryEvaluationContainer = exprContainer;

  			this.state.GoToStart();

  			var evalStackHeight = this.state.evaluationStack.length;

  			this.Continue();

  			this._temporaryEvaluationContainer = null;

  			// Should have fallen off the end of the Container, which should
  			// have auto-popped, but just in case we didn't for some reason,
  			// manually pop to restore the state (including currentPath).
  			if (this.state.callStack.elements.length > startCallStackHeight) {
  				this.state.callStack.Pop();
  			}

  			var endStackHeight = this.state.evaluationStack.length;
  			if (endStackHeight > evalStackHeight) {
  				return this.state.PopEvaluationStack();
  			} else {
  				return null;
  			}
  		}
  	}, {
  		key: 'CallExternalFunction',
  		value: function CallExternalFunction(funcName, numberOfArguments) {
  			var func = this._externals[funcName];
  			var fallbackFunctionContainer = null;

  			var foundExternal = typeof func !== 'undefined';

  			// Try to use fallback function?
  			if (!foundExternal) {
  				if (this.allowExternalFunctionFallbacks) {
  					//				fallbackFunctionContainer = ContentAtPath (new Path (funcName)) as Container;
  					fallbackFunctionContainer = this.ContentAtPath(new Path$1(funcName));
  					if (!(fallbackFunctionContainer instanceof Container)) console.warn("Trying to call EXTERNAL function '" + funcName + "' which has not been bound, and fallback ink function could not be found.");

  					// Divert direct into fallback function and we're done
  					this.state.callStack.Push(PushPopType.Function);
  					this.state.divertedTargetObject = fallbackFunctionContainer;
  					return;
  				} else {
  					console.warn("Trying to call EXTERNAL function '" + funcName + "' which has not been bound (and ink fallbacks disabled).");
  				}
  			}

  			// Pop arguments
  			var args = [];
  			for (var i = 0; i < numberOfArguments; ++i) {
  				//			var poppedObj = state.PopEvaluationStack () as Value;
  				var poppedObj = this.state.PopEvaluationStack();
  				var valueObj = poppedObj.valueObject;
  				args.push(valueObj);
  			}

  			// Reverse arguments from the order they were popped,
  			// so they're the right way round again.
  			args.reverse();

  			// Run the function!
  			var funcResult = func(args);

  			// Convert return value (if any) to the a type that the ink engine can use
  			var returnObj = null;
  			if (funcResult != null) {
  				returnObj = Value.Create(funcResult);
  				if (returnObj == null) console.warn("Could not create ink value from returned object of type " + (typeof funcResult === 'undefined' ? 'undefined' : babelHelpers.typeof(funcResult)));
  			} else {
  				returnObj = new Void();
  			}

  			this.state.PushEvaluationStack(returnObj);
  		}
  	}, {
  		key: 'TryCoerce',
  		value: function TryCoerce(value) {
  			//we're skipping type coercition in this implementation. First of, js is loosely typed, so it's not that important. Secondly, there is no clean way (AFAIK) for the user to describe what type of parameters he/she expects.
  			return value;
  		}
  	}, {
  		key: 'BindExternalFunctionGeneral',
  		value: function BindExternalFunctionGeneral(funcName, func) {
  			if (this._externals[funcName]) console.warn("Function '" + funcName + "' has already been bound.");
  			this._externals[funcName] = func;
  		}
  	}, {
  		key: 'BindExternalFunction',
  		value: function BindExternalFunction(funcName, func) {
  			var _this2 = this;

  			if (!func) console.warn("Can't bind a null function");

  			this.BindExternalFunctionGeneral(funcName, function (args) {
  				if (args.length < func.length) console.warn("External function expected " + func.length + " arguments");

  				var coercedArgs = [];
  				for (var i = 0, l = args.length; i < l; i++) {
  					coercedArgs[i] = _this2.TryCoerce(args[i]);
  				}
  				return func.apply(null, coercedArgs);
  			});
  		}
  	}, {
  		key: 'UnbindExternalFunction',
  		value: function UnbindExternalFunction(funcName) {
  			if (typeof this._externals[funcName] === 'undefined') console.warn("Function '" + funcName + "' has not been bound.");
  			delete this._externals[funcName];
  		}
  	}, {
  		key: 'ValidateExternalBindings',
  		value: function ValidateExternalBindings(containerOrObject, missingExternals) {
  			var _this3 = this;

  			if (!containerOrObject) {
  				var missingExternals = [];
  				this.ValidateExternalBindings(this._mainContentContainer, missingExternals);
  				this._hasValidatedExternals = true;

  				// No problem! Validation complete
  				if (missingExternals.length == 0) {
  					this._hasValidatedExternals = true;
  				}

  				// Error for all missing externals
  				else {
  						var message = "Error: Missing function binding for external";
  						message += missingExternals.length > 1 ? "s" : "";
  						message += ": '";
  						message += missingExternals.join("', '");
  						message += "' ";
  						message += this.allowExternalFunctionFallbacks ? ", and no fallback ink function found." : " (ink fallbacks disabled)";

  						this.Error(message);
  					}
  			} else if (containerOrObject instanceof Container) {
  				var c = containerOrObject;

  				c.content.forEach(function (innerContent) {
  					_this3.ValidateExternalBindings(innerContent, missingExternals);
  				});
  				for (var key in c.namedContent) {
  					this.ValidateExternalBindings(c.namedContent[key], missingExternals);
  				}
  			} else {
  				var o = containerOrObject;
  				//the following code is already taken care of above in this implementation
  				//			var container = o as Container;
  				//            if (container) {
  				//                ValidateExternalBindings (container, missingExternals);
  				//                return;
  				//            }

  				//            var divert = o as Divert;
  				var divert = o;
  				if (divert instanceof Divert && divert.isExternal) {
  					var name = divert.targetPathString;

  					if (!this._externals[name]) {
  						if (this.allowExternalFunctionFallbacks) {
  							var fallbackFound = !!this.mainContentContainer.namedContent[name];
  							if (!fallbackFound) {
  								missingExternals.push(name);
  							}
  						} else {
  							missingExternals.push(name);
  						}
  					}
  				}
  			}
  		}
  	}, {
  		key: 'ObserveVariable',
  		value: function ObserveVariable(variableName, observer) {
  			if (this._variableObservers == null) this._variableObservers = {};

  			if (this._variableObservers[variableName]) {
  				this._variableObservers[variableName].push(observer);
  			} else {
  				this._variableObservers[variableName] = [observer];
  			}
  		}
  	}, {
  		key: 'ObserveVariables',
  		value: function ObserveVariables(variableNames, observers) {
  			for (var i = 0, l = variableNames.length; i < l; i++) {
  				this.ObserveVariable(variableNames[i], observers[i]);
  			}
  		}
  	}, {
  		key: 'RemoveVariableObserver',
  		value: function RemoveVariableObserver(observer, specificVariableName) {
  			if (this._variableObservers == null) return;

  			// Remove observer for this specific variable
  			if (typeof specificVariableName !== 'undefined') {
  				if (this._variableObservers[specificVariableName]) {
  					this._variableObservers[specificVariableName].splice(this._variableObservers[specificVariableName].indexOf(observer), 1);
  				}
  			}

  			// Remove observer for all variables
  			else {
  					for (var varName in this._variableObservers) {
  						this._variableObservers[varName].splice(this._variableObservers[varName].indexOf(observer), 1);
  					}
  				}
  		}
  	}, {
  		key: 'VariableStateDidChangeEvent',
  		value: function VariableStateDidChangeEvent(variableName, newValueObj) {
  			if (this._variableObservers == null) return;

  			var observers = this._variableObservers[variableName];
  			if (typeof observers !== 'undefined') {

  				if (!(newValueObj instanceof Value)) {
  					throw "Tried to get the value of a variable that isn't a standard type";
  				}
  				//			var val = newValueObj as Value;
  				var val = newValueObj;

  				observers.forEach(function (observer) {
  					observer(variableName, val.valueObject);
  				});
  			}
  		}
  	}, {
  		key: 'TagsForContentAtPath',
  		value: function TagsForContentAtPath(path) {
  			return this.TagsAtStartOfFlowContainerWithPathString(path);
  		}
  	}, {
  		key: 'TagsAtStartOfFlowContainerWithPathString',
  		value: function TagsAtStartOfFlowContainerWithPathString(pathString) {
  			var path = new Path$1(pathString);

  			// Expected to be global story, knot or stitch
  			//		var flowContainer = ContentAtPath (path) as Container;
  			var flowContainer = this.ContentAtPath(path);
  			while (true) {
  				var firstContent = flowContainer.content[0];
  				if (firstContent instanceof Container) flowContainer = firstContent;else break;
  			}

  			// Any initial tag objects count as the "main tags" associated with that story/knot/stitch
  			var tags = null;

  			flowContainer.content.every(function (c) {
  				//			var tag = c as Runtime.Tag;
  				var tag = c;
  				if (tag instanceof Tag) {
  					if (tags == null) tags = [];
  					tags.push(tag.text);
  					return true;
  				} else return false;
  			});

  			return tags;
  		}
  	}, {
  		key: 'BuildStringOfHierarchy',
  		value: function BuildStringOfHierarchy() {
  			var sb = new StringBuilder();

  			this.mainContentContainer.BuildStringOfHierarchy(sb, 0, this.state.currentContentObject);

  			return sb.toString();
  		}
  	}, {
  		key: 'NextContent',
  		value: function NextContent() {
  			// Setting previousContentObject is critical for VisitChangedContainersDueToDivert
  			this.state.previousContentObject = this.state.currentContentObject;

  			// Divert step?
  			if (this.state.divertedTargetObject != null) {

  				this.state.currentContentObject = this.state.divertedTargetObject;
  				this.state.divertedTargetObject = null;

  				// Internally uses state.previousContentObject and state.currentContentObject
  				this.VisitChangedContainersDueToDivert();

  				// Diverted location has valid content?
  				if (this.state.currentContentObject != null) {
  					return;
  				}

  				// Otherwise, if diverted location doesn't have valid content,
  				// drop down and attempt to increment.
  				// This can happen if the diverted path is intentionally jumping
  				// to the end of a container - e.g. a Conditional that's re-joining
  			}

  			var successfulPointerIncrement = this.IncrementContentPointer();

  			// Ran out of content? Try to auto-exit from a function,
  			// or finish evaluating the content of a thread
  			if (!successfulPointerIncrement) {

  				var didPop = false;

  				if (this.state.callStack.CanPop(PushPopType.Function)) {

  					// Pop from the call stack
  					this.state.callStack.Pop(PushPopType.Function);

  					// This pop was due to dropping off the end of a function that didn't return anything,
  					// so in this case, we make sure that the evaluator has something to chomp on if it needs it
  					if (this.state.inExpressionEvaluation) {
  						this.state.PushEvaluationStack(new Void());
  					}

  					didPop = true;
  				} else if (this.state.callStack.canPopThread) {
  					this.state.callStack.PopThread();

  					didPop = true;
  				} else {
  					this.state.TryExitExternalFunctionEvaluation();
  				}

  				// Step past the point where we last called out
  				if (didPop && this.state.currentContentObject != null) {
  					this.NextContent();
  				}
  			}
  		}
  	}, {
  		key: 'IncrementContentPointer',
  		value: function IncrementContentPointer() {
  			var successfulIncrement = true;

  			var currEl = this.state.callStack.currentElement;
  			currEl.currentContentIndex++;

  			// Each time we step off the end, we fall out to the next container, all the
  			// while we're in indexed rather than named content
  			while (currEl.currentContentIndex >= currEl.currentContainer.content.length) {

  				successfulIncrement = false;

  				//			Container nextAncestor = currEl.currentContainer.parent as Container;
  				var nextAncestor = currEl.currentContainer.parent;
  				if (nextAncestor instanceof Container === false) {
  					break;
  				}

  				var indexInAncestor = nextAncestor.content.indexOf(currEl.currentContainer);
  				if (indexInAncestor == -1) {
  					break;
  				}

  				currEl.currentContainer = nextAncestor;
  				currEl.currentContentIndex = indexInAncestor + 1;

  				successfulIncrement = true;
  			}

  			if (!successfulIncrement) currEl.currentContainer = null;

  			return successfulIncrement;
  		}
  	}, {
  		key: 'TryFollowDefaultInvisibleChoice',
  		value: function TryFollowDefaultInvisibleChoice() {
  			var allChoices = this._state.currentChoices;

  			// Is a default invisible choice the ONLY choice?
  			var invisibleChoices = allChoices.filter(function (c) {
  				return c.choicePoint.isInvisibleDefault;
  			});
  			if (invisibleChoices.length == 0 || allChoices.length > invisibleChoices.length) return false;

  			var choice = invisibleChoices[0];

  			this.ChoosePath(choice.choicePoint.choiceTarget.path);

  			return true;
  		}
  	}, {
  		key: 'VisitCountForContainer',
  		value: function VisitCountForContainer(container) {
  			if (!container.visitsShouldBeCounted) {
  				console.warn("Read count for target (" + container.name + " - on " + container.debugMetadata + ") unknown. The story may need to be compiled with countAllVisits flag (-c).");
  				return 0;
  			}

  			var count = 0;
  			var containerPathStr = container.path.toString();
  			count = this.state.visitCounts[containerPathStr] || count;
  			return count;
  		}
  	}, {
  		key: 'IncrementVisitCountForContainer',
  		value: function IncrementVisitCountForContainer(container) {
  			var count = 0;
  			var containerPathStr = container.path.toString();
  			if (this.state.visitCounts[containerPathStr]) count = this.state.visitCounts[containerPathStr];
  			count++;
  			this.state.visitCounts[containerPathStr] = count;
  		}
  	}, {
  		key: 'RecordTurnIndexVisitToContainer',
  		value: function RecordTurnIndexVisitToContainer(container) {
  			var containerPathStr = container.path.toString();
  			this.state.turnIndices[containerPathStr] = this.state.currentTurnIndex;
  		}
  	}, {
  		key: 'TurnsSinceForContainer',
  		value: function TurnsSinceForContainer(container) {
  			if (!container.turnIndexShouldBeCounted) {
  				this.Error("TURNS_SINCE() for target (" + container.name + " - on " + container.debugMetadata + ") unknown. The story may need to be compiled with countAllVisits flag (-c).");
  			}

  			var containerPathStr = container.path.toString();
  			var index = this.state.turnIndices[containerPathStr];
  			if (typeof index !== 'undefined') {
  				return this.state.currentTurnIndex - index;
  			} else {
  				return -1;
  			}
  		}
  	}, {
  		key: 'NextSequenceShuffleIndex',
  		value: function NextSequenceShuffleIndex() {
  			//		var numElementsIntVal = state.PopEvaluationStack () as IntValue;
  			var numElementsIntVal = this.state.PopEvaluationStack();
  			if (!(numElementsIntVal instanceof IntValue)) {
  				this.Error("expected number of elements in sequence for shuffle index");
  				return 0;
  			}

  			var seqContainer = this.state.currentContainer;

  			var numElements = numElementsIntVal.value;

  			//		var seqCountVal = state.PopEvaluationStack () as IntValue;
  			var seqCountVal = this.state.PopEvaluationStack();
  			var seqCount = seqCountVal.value;
  			var loopIndex = seqCount / numElements;
  			var iterationIndex = seqCount % numElements;

  			// Generate the same shuffle based on:
  			//  - The hash of this container, to make sure it's consistent
  			//    each time the runtime returns to the sequence
  			//  - How many times the runtime has looped around this full shuffle
  			var seqPathStr = seqContainer.path.toString();
  			var sequenceHash = 0;
  			for (var i = 0, l = seqPathStr.length; i < l; i++) {
  				sequenceHash += seqPathStr.charCodeAt[i] || 0;
  			}
  			var randomSeed = sequenceHash + loopIndex + this.state.storySeed;
  			var random = new PRNG(parseInt(randomSeed));

  			var unpickedIndices = [];
  			for (var i = 0; i < numElements; ++i) {
  				unpickedIndices.push(i);
  			}

  			for (var i = 0; i <= iterationIndex; ++i) {
  				var chosen = random.next() % unpickedIndices.length;
  				var chosenIndex = unpickedIndices[chosen];
  				unpickedIndices.splice(chosen, 1);

  				if (i == iterationIndex) {
  					return chosenIndex;
  				}
  			}

  			throw "Should never reach here";
  		}
  	}, {
  		key: 'Error',
  		value: function Error(message, useEndLineNumber) {
  			var e = new StoryException(message);
  			//		e.useEndLineNumber = useEndLineNumber;
  			throw e;
  		}
  	}, {
  		key: 'AddError',
  		value: function AddError(message, useEndLineNumber) {
  			//		var dm = this.currentDebugMetadata;
  			var dm = null;

  			if (dm != null) {
  				var lineNum = useEndLineNumber ? dm.endLineNumber : dm.startLineNumber;
  				message = "RUNTIME ERROR: '" + dm.fileName + "' line " + lineNum + ": " + message;
  			} else {
  				message = "RUNTIME ERROR: " + message;
  			}

  			this.state.AddError(message);

  			// In a broken state don't need to know about any other errors.
  			this.state.ForceEnd();
  		}
  	}, {
  		key: 'currentChoices',
  		get: function get() {
  			// Don't include invisible choices for external usage.
  			var choices = [];

  			this._state.currentChoices.forEach(function (c) {
  				if (!c.choicePoint.isInvisibleDefault) {
  					c.index = choices.length;
  					choices.push(c);
  				}
  			});

  			return choices;
  		}
  	}, {
  		key: 'currentText',
  		get: function get() {
  			return this.state.currentText;
  		}
  	}, {
  		key: 'currentTags',
  		get: function get() {
  			return this.state.currentTags;
  		}
  	}, {
  		key: 'currentErrors',
  		get: function get() {
  			return this.state.currentErrors;
  		}
  	}, {
  		key: 'hasError',
  		get: function get() {
  			return this.state.hasError;
  		}
  	}, {
  		key: 'variablesState',
  		get: function get() {
  			return this.state.variablesState;
  		}
  	}, {
  		key: 'state',
  		get: function get() {
  			return this._state;
  		}
  	}, {
  		key: 'mainContentContainer',
  		get: function get() {
  			if (this._temporaryEvaluationContainer) {
  				return this._temporaryEvaluationContainer;
  			} else {
  				return this._mainContentContainer;
  			}
  		}
  	}, {
  		key: 'canContinue',
  		get: function get() {
  			return this.state.currentContentObject != null && !this.state.hasError;
  		}
  	}, {
  		key: 'globalTags',
  		get: function get() {
  			return this.TagsAtStartOfFlowContainerWithPathString("");
  		}
  	}]);
  	return Story;
  }(InkObject);

  exports.Story = Story;

}));