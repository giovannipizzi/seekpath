Clazz.declarePackage ("J.awtjs.swing");
Clazz.load (["J.awtjs.swing.JMenuItem"], "J.awtjs.swing.JMenu", null, function () {
c$ = Clazz.declareType (J.awtjs.swing, "JMenu", J.awtjs.swing.JMenuItem);
Clazz.makeConstructor (c$, 
function () {
Clazz.superConstructor (this, J.awtjs.swing.JMenu, ["mnu", 4]);
});
Clazz.defineMethod (c$, "getItemCount", 
function () {
return this.getComponentCount ();
});
Clazz.defineMethod (c$, "getItem", 
function (i) {
return this.getComponent (i);
}, "~N");
Clazz.overrideMethod (c$, "getPopupMenu", 
function () {
return this;
});
Clazz.overrideMethod (c$, "toHTML", 
function () {
return this.getMenuHTML ();
});
});
