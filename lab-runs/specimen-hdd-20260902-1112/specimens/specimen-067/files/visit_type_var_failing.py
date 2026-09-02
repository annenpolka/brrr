# Reduced excerpt of TypeExpander.visit_type_var on failing_ref
# mypy/expandtype.py

repl = self.variables.get(t.id, t)
if isinstance(repl, ProperType) and isinstance(repl, Instance):
    # TODO: do we really need to do this?
    # If I try to remove this special-casing ~40 tests fail on reveal_type().
    return repl.copy_modified(last_known_value=None)
return repl
