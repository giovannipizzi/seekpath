Clazz.declarePackage ("J.awtjs.swing");
Clazz.load (["J.awtjs.swing.JMenuItem"], "J.awtjs.swing.JRadioButtonMenuItem", null, function () {
c$ = Clazz.decorateAsClass (function () {
this.isRadio = true;
Clazz.instantialize (this, arguments);
}, J.awtjs.swing, "JRadioButtonMenuItem", J.awtjs.swing.JMenuItem);
Clazz.makeConstructor (c$, 
function () {
Clazz.superConstructor (this, J.awtjs.swing.JRadioButtonMenuItem, ["rad", 3]);
});
});
