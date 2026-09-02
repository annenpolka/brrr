KNOWN FIX (sealed): hashicorp/terraform PR 37709 squash merge 62540da0153899b20f7808026e9c8afa2b5a6112.

Decode unmarshaled IdentityJSON whenever it was non-nil, using schema.Identity.ImpliedType(). Encode already required schema.Identity != nil. A provider without a resource identity schema (downgrade) therefore fed leftover identity JSON through ImpliedType on a nil *configschema.Object (EmptyObject) and surfaced the unsupported-attribute provider-bug error instead of treating identity as absent. Repair: also require schema.Identity != nil before decoding, so leftover identity is skipped; a later Encode writes no IdentityJSON, and the added refresh-only downgrade test expects a null identity.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
