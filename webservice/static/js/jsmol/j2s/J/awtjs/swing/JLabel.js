Clazz.declarePackage ("J.awtjs.swing");
Clazz.load (["J.awtjs.swing.JComponent"], "J.awtjs.swing.JLabel", ["JU.SB"], function () {
c$ = Clazz.declareType (J.awtjs.swing, "JLabel", J.awtjs.swing.JComponent);
Clazz.makeConstructor (c$, 
function (text) {
Clazz.superConstructor (this, J.awtjs.swing.JLabel, ["lblJL"]);
this.text = text;
}, "~S");
Clazz.overrideMethod (c$, "toHTML", 
function () {
var sb =  new JU.SB ();
sb.append ("<span id='" + this.id + "' class='JLabel' style='" + this.getCSSstyle (0, 0) + "'>");
sb.append (this.text);
sb.append ("</span>");
return sb.toString ();
});
});
