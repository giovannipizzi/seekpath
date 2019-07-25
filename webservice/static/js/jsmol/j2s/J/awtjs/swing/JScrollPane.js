Clazz.declarePackage ("J.awtjs.swing");
Clazz.load (["J.awtjs.swing.JComponent"], "J.awtjs.swing.JScrollPane", ["JU.SB"], function () {
c$ = Clazz.declareType (J.awtjs.swing, "JScrollPane", J.awtjs.swing.JComponent);
Clazz.makeConstructor (c$, 
function (component) {
Clazz.superConstructor (this, J.awtjs.swing.JScrollPane, ["JScP"]);
this.add (component);
}, "J.awtjs.swing.JComponent");
Clazz.defineMethod (c$, "toHTML", 
function () {
var sb =  new JU.SB ();
sb.append ("\n<div id='" + this.id + "' class='JScrollPane' style='" + this.getCSSstyle (98, 98) + "overflow:auto'>\n");
if (this.list != null) {
var c = this.list.get (0);
sb.append (c.toHTML ());
}sb.append ("\n</div>\n");
return sb.toString ();
});
Clazz.overrideMethod (c$, "setMinimumSize", 
function (dimension) {
}, "javajs.awt.Dimension");
});
