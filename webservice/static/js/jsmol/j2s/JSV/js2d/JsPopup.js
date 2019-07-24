Clazz.declarePackage ("JSV.js2d");
Clazz.load (["JSV.popup.JSVGenericPopup"], "JSV.js2d.JsPopup", ["JSV.popup.JSVPopupResourceBundle", "J.popup.JSSwingPopupHelper"], function () {
c$ = Clazz.declareType (JSV.js2d, "JsPopup", JSV.popup.JSVGenericPopup);
Clazz.makeConstructor (c$, 
function () {
Clazz.superConstructor (this, JSV.js2d.JsPopup, []);
this.helper =  new J.popup.JSSwingPopupHelper (this);
});
Clazz.overrideMethod (c$, "jpiInitialize", 
function (viewer, menu) {
var bundle =  new JSV.popup.JSVPopupResourceBundle ();
this.initialize (viewer, bundle, menu);
}, "javajs.awt.PlatformViewer,~S");
Clazz.overrideMethod (c$, "menuShowPopup", 
function (popup, x, y) {
this.vwr.menuShowPopup (popup, x, y, this.isTainted);
}, "javajs.awt.SC,~N,~N");
Clazz.overrideMethod (c$, "getImageIcon", 
function (fileName) {
return null;
}, "~S");
Clazz.overrideMethod (c$, "menuFocusCallback", 
function (name, actionCommand, b) {
}, "~S,~S,~B");
});
