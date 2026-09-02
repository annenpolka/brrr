/* Reduced excerpt of rb_autoload_load on failing_ref
 * variable.c
 * ded5a66cb994c5731a17bc9a2420042248a2f1fe
 * leftover Qundef const_entry after helper loaded without defining the constant.
 */

result = rb_ensure(autoload_require, (VALUE)&state,
   autoload_reset, (VALUE)&state);

if (flag > 0 && (ce = rb_const_lookup(mod, id))) {
    ce->flag |= flag;
}
/* no rb_const_remove when ce missing or ce->value == Qundef */
