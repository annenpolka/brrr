KNOWN FIX (sealed): moby/moby PR 52317 merge 69b8083c9ba419d30e60f8232e4e1dbe9e7a25db.

getInterval returned the full StartInterval whenever status was still starting, even if that sleep overran StartPeriod. Repair: while starting, if startInterval > remaining start-period time, return remaining so the monitor wakes at the period boundary and then uses the regular probe interval.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
