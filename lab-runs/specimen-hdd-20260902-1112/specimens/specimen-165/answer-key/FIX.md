KNOWN FIX (sealed): ruby/ruby PR 4715 commit 08759edea8fb75d46c3e75217e6613465426a0d2.

failing_ref is parent ded5a66cb994c5731a17bc9a2420042248a2f1fe.

rb_autoload_load left a Qundef const_entry after the helper loaded without defining the constant. Leftover undefined name / leftover autoload retry after $LOADED_FEATURES delete.

Repair: if the constant is missing or still Qundef after require, rb_const_remove(mod, id).

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
