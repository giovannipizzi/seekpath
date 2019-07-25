Clazz.declarePackage ("J.awtjs.swing");
Clazz.load (["J.awtjs.swing.AbstractButton"], "J.awtjs.swing.JCheckBox", null, function () {
c$ = Clazz.declareType (J.awtjs.swing, "JCheckBox", J.awtjs.swing.AbstractButton);
Clazz.makeConstructor (c$, 
function () {
Clazz.superConstructor (this, J.awtjs.swing.JCheckBox, ["chkJCB"]);
});
Clazz.overrideMethod (c$, "toHTML", 
function () {
var s = "<label><input type=checkbox id='" + this.id + "' class='JCheckBox' style='" + this.getCSSstyle (0, 0) + "' " + (this.selected ? "checked='checked' " : "") + "onclick='SwingController.click(this)'>" + this.text + "</label>";
return s;
});
});
