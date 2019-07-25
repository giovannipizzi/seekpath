Clazz.declarePackage ("J.popup");
Clazz.load (["J.popup.PopupHelper"], "J.popup.JSSwingPopupHelper", ["J.awtjs.swing.ButtonGroup", "$.JCheckBoxMenuItem", "$.JMenu", "$.JMenuItem", "$.JPopupMenu", "$.JRadioButtonMenuItem"], function () {
c$ = Clazz.decorateAsClass (function () {
this.popup = null;
this.buttonGroup = null;
Clazz.instantialize (this, arguments);
}, J.popup, "JSSwingPopupHelper", null, J.popup.PopupHelper);
Clazz.makeConstructor (c$, 
function (popup) {
this.popup = popup;
}, "javajs.awt.GenericMenuInterface");
Clazz.overrideMethod (c$, "menuCreatePopup", 
function (name, applet) {
var j =  new J.awtjs.swing.JPopupMenu (name);
j.setInvoker (applet);
return j;
}, "~S,~O");
Clazz.overrideMethod (c$, "getMenu", 
function (name) {
return  new J.awtjs.swing.JMenu ();
}, "~S");
Clazz.overrideMethod (c$, "getMenuItem", 
function (name) {
return  new J.awtjs.swing.JMenuItem (name);
}, "~S");
Clazz.overrideMethod (c$, "getRadio", 
function (name) {
return  new J.awtjs.swing.JRadioButtonMenuItem ();
}, "~S");
Clazz.overrideMethod (c$, "getCheckBox", 
function (name) {
return  new J.awtjs.swing.JCheckBoxMenuItem ();
}, "~S");
Clazz.overrideMethod (c$, "menuAddButtonGroup", 
function (item) {
if (item == null) {
this.buttonGroup = null;
return;
}if (this.buttonGroup == null) this.buttonGroup =  new J.awtjs.swing.ButtonGroup ();
this.buttonGroup.add (item);
}, "javajs.awt.SC");
Clazz.overrideMethod (c$, "getItemType", 
function (m) {
return (m).btnType;
}, "javajs.awt.SC");
Clazz.overrideMethod (c$, "menuInsertSubMenu", 
function (menu, subMenu, index) {
(subMenu).setParent (menu);
}, "javajs.awt.SC,javajs.awt.SC,~N");
Clazz.overrideMethod (c$, "getSwingComponent", 
function (component) {
return component;
}, "~O");
Clazz.overrideMethod (c$, "menuClearListeners", 
function (menu) {
if (menu != null) (menu).disposeMenu ();
}, "javajs.awt.SC");
Clazz.defineMethod (c$, "itemStateChanged", 
function (e) {
this.popup.menuCheckBoxCallback (e.getSource ());
}, "javajs.awt.event.ItemEvent");
Clazz.defineMethod (c$, "actionPerformed", 
function (e) {
this.popup.menuClickCallback (e.getSource (), e.getActionCommand ());
}, "javajs.awt.event.ActionEvent");
Clazz.overrideMethod (c$, "getButtonGroup", 
function () {
return this.buttonGroup;
});
});
