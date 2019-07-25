Clazz.declarePackage ("J.awtjs.swing");
Clazz.load (null, "J.awtjs.swing.ButtonGroup", ["javajs.awt.Component"], function () {
c$ = Clazz.decorateAsClass (function () {
this.id = null;
Clazz.instantialize (this, arguments);
}, J.awtjs.swing, "ButtonGroup");
Clazz.makeConstructor (c$, 
function () {
this.id = javajs.awt.Component.newID ("bg");
});
Clazz.defineMethod (c$, "add", 
function (item) {
(item).htmlName = this.id;
}, "javajs.awt.SC");
});
