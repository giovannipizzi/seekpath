Clazz.declarePackage ("J.awtjs.swing");
Clazz.load (["J.awtjs.swing.JComponent"], "J.awtjs.swing.JPanel", ["JU.SB", "J.awtjs.swing.Grid", "$.GridBagConstraints"], function () {
c$ = Clazz.decorateAsClass (function () {
this.grid = null;
this.nElements = 0;
this.last = null;
Clazz.instantialize (this, arguments);
}, J.awtjs.swing, "JPanel", J.awtjs.swing.JComponent);
Clazz.makeConstructor (c$, 
function (manager) {
Clazz.superConstructor (this, J.awtjs.swing.JPanel, ["JP"]);
this.grid =  new J.awtjs.swing.Grid (10, 10);
}, "javajs.awt.LayoutManager");
Clazz.defineMethod (c$, "add", 
function (btn, c) {
this.last = (++this.nElements == 1 ? btn : null);
if (Clazz.instanceOf (c, String)) {
if (c.equals ("North")) c =  new J.awtjs.swing.GridBagConstraints (0, 0, 3, 1, 0, 0, 10, 0, null, 0, 0);
 else if (c.equals ("South")) c =  new J.awtjs.swing.GridBagConstraints (0, 2, 3, 1, 0, 0, 10, 0, null, 0, 0);
 else if (c.equals ("East")) c =  new J.awtjs.swing.GridBagConstraints (2, 1, 1, 1, 0, 0, 13, 0, null, 0, 0);
 else if (c.equals ("West")) c =  new J.awtjs.swing.GridBagConstraints (0, 1, 1, 1, 0, 0, 17, 0, null, 0, 0);
 else c =  new J.awtjs.swing.GridBagConstraints (1, 1, 1, 1, 0, 0, 10, 0, null, 0, 0);
}this.grid.add (btn, c);
}, "J.awtjs.swing.JComponent,~O");
Clazz.overrideMethod (c$, "toHTML", 
function () {
if (this.last != null) {
this.grid =  new J.awtjs.swing.Grid (1, 1);
this.grid.add (this.last,  new J.awtjs.swing.GridBagConstraints (0, 0, 1, 1, 0, 0, 10, 0, null, 0, 0));
this.last = null;
}var sb =  new JU.SB ();
sb.append ("\n<div id='" + this.id + "' class='JPanel' style='" + this.getCSSstyle (100, 100) + "'>\n");
sb.append ("\n<span id='" + this.id + "_minimizer' style='width:" + this.minWidth + "px;height:" + this.minHeight + "px;'>");
sb.append (this.grid.toHTML (this.id));
sb.append ("</span>");
sb.append ("\n</div>\n");
return sb.toString ();
});
});
