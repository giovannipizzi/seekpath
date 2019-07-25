Clazz.declarePackage ("J.awtjs.swing");
Clazz.load (["J.awtjs.swing.AbstractButton"], "J.awtjs.swing.JButton", ["JU.SB"], function () {
c$ = Clazz.declareType (J.awtjs.swing, "JButton", J.awtjs.swing.AbstractButton);
Clazz.makeConstructor (c$, 
function () {
Clazz.superConstructor (this, J.awtjs.swing.JButton, ["btnJB"]);
});
Clazz.overrideMethod (c$, "toHTML", 
function () {
var sb =  new JU.SB ();
sb.append ("<input type=button id='" + this.id + "' class='JButton' style='" + this.getCSSstyle (80, 0) + "' onclick='SwingController.click(this)' value='" + this.text + "'/>");
return sb.toString ();
});
});
