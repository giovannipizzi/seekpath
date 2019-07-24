Clazz.declarePackage ("J.awtjs.swing");
Clazz.load (["J.awtjs.swing.AbstractButton"], "J.awtjs.swing.JPopupMenu", null, function () {
c$ = Clazz.decorateAsClass (function () {
this.tainted = true;
Clazz.instantialize (this, arguments);
}, J.awtjs.swing, "JPopupMenu", J.awtjs.swing.AbstractButton);
Clazz.makeConstructor (c$, 
function (name) {
Clazz.superConstructor (this, J.awtjs.swing.JPopupMenu, ["mnu"]);
this.name = name;
}, "~S");
Clazz.defineMethod (c$, "setInvoker", 
function (applet) {
this.applet = applet;
{
SwingController.setMenu(this);
}}, "~O");
Clazz.defineMethod (c$, "show", 
function (applet, x, y) {
{
if (applet != null)
this.tainted = true;
SwingController.showMenu(this, x, y);
}}, "javajs.awt.Component,~N,~N");
Clazz.defineMethod (c$, "disposeMenu", 
function () {
{
SwingController.disposeMenu(this);
}});
Clazz.overrideMethod (c$, "toHTML", 
function () {
return this.getMenuHTML ();
});
{
{
SwingController.setDraggable(J.awtjs.swing.JPopupMenu);
}}});
