function patchInterpreter (Interpreter) {
  const originalGetProperty = Interpreter.prototype.getProperty;
  const originalSetProperty = Interpreter.prototype.setProperty;

  function newGetProperty(obj, name) {
    if (obj == null || !obj._connected) {
      return originalGetProperty.call(this, obj, name);
    }

    const value = obj._connected[name];
    if (typeof value === 'object') {
      // if the value is an object itself, create another connected object
      return this.createConnectedObject(value);
    }
    return value;
  }
  function newSetProperty(obj, name, value, opt_descriptor) {
    if (obj == null || !obj._connected) {
      return originalSetProperty.call(this, obj, name, value, opt_descriptor);
    }

    obj._connected[name] = this.pseudoToNative(value);
  }

  let getKeys = [];
  let setKeys = [];
  for (const key of Object.keys(Interpreter.prototype)) {
    if (Interpreter.prototype[key] === originalGetProperty) {
      getKeys.push(key);
    }
    if (Interpreter.prototype[key] === originalSetProperty) {
      setKeys.push(key);
    }
  }

  for (const key of getKeys) {
    Interpreter.prototype[key] = newGetProperty;
  }
  for (const key of setKeys) {
    Interpreter.prototype[key] = newSetProperty;
  }

  Interpreter.prototype.createConnectedObject = function (obj) {
    const connectedObject = this.createObject(this.OBJECT);
    connectedObject._connected = obj;
    return connectedObject;
  };
}

