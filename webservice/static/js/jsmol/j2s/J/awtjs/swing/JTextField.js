Clazz.declarePackage ("J.awtjs.swing");
Clazz.load (["J.awtjs.swing.JComponent"], "J.awtjs.swing.JTextField", ["JU.SB"], function () {
c$ = Clazz.declareType (J.awtjs.swing, "JTextField", J.awtjs.swing.JComponent);
Clazz.makeConstructor (c$, 
function (value) {
Clazz.superConstructor (this, J.awtjs.swing.JTextField, ["txtJT"]);
this.text = value;
}, "~S");
Clazz.overrideMethod (c$, "toHTML", 
function () {
var sb =  new JU.SB ();
sb.append ("<input type=text id='" + this.id + "' class='JTextField' style='" + this.getCSSstyle (0, 0) + "' value='" + this.text + "' onkeyup	=SwingController.click(this,event)	>");
return sb.toString ();
});
});
