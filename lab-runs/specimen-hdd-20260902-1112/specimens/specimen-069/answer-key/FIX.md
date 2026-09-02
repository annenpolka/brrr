KNOWN FIX (sealed): actions/checkout PR 2530 squash 28802689a136bfcdb721715abd713740beecbe07.

tryConfigUnsetValue passed the Windows credentials path to git config --unset as a raw value-pattern. Git compiled it as a regex; backslashes made the pattern invalid, so includeIf entries were not removed. Repair: regexpHelper.escape(configValue) before --unset.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
