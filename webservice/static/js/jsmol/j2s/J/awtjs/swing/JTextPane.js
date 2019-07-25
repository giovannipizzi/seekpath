Clazz.declarePackage ("J.awtjs.swing");
Clazz.load (["J.awtjs.swing.Document", "$.JComponent"], "J.awtjs.swing.JTextPane", ["JU.SB"], function () {
c$ = Clazz.declareType (J.awtjs.swing, "JTextPane", J.awtjs.swing.JComponent, J.awtjs.swing.Document);
Clazz.makeConstructor (c$, 
function () {
Clazz.superConstructor (this, J.awtjs.swing.JTextPane, ["txtJTP"]);
this.text = "";
});
Clazz.defineMethod (c$, "getDocument", 
function () {
return this;
});
Clazz.overrideMethod (c$, "insertString", 
function (i, s, object) {
i = Math.min (i, this.text.length);
this.text = this.text.substring (0, i) + s + this.text.substring (i);
}, "~N,~S,~O");
Clazz.overrideMethod (c$, "toHTML", 
function () {
var sb =  new JU.SB ();
sb.append ("<textarea type=text id='" + this.id + "' class='JTextPane' style='" + this.getCSSstyle (98, 98) + "'>" + this.text + "</textarea>");
return sb.toString ();
});
});
