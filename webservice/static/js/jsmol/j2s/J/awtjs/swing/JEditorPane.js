Clazz.declarePackage ("J.awtjs.swing");
Clazz.load (["J.awtjs.swing.JComponent"], "J.awtjs.swing.JEditorPane", ["JU.SB"], function () {
c$ = Clazz.declareType (J.awtjs.swing, "JEditorPane", J.awtjs.swing.JComponent);
Clazz.makeConstructor (c$, 
function () {
Clazz.superConstructor (this, J.awtjs.swing.JEditorPane, ["txtJEP"]);
this.text = "";
});
Clazz.overrideMethod (c$, "toHTML", 
function () {
var sb =  new JU.SB ();
sb.append ("<textarea type=text id='" + this.id + "' class='JEditorPane' style='" + this.getCSSstyle (98, 98) + "'>" + this.text + "</textarea>");
return sb.toString ();
});
});
