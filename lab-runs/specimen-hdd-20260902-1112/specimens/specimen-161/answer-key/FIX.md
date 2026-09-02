KNOWN FIX (sealed): vercel/next.js PR 96022 squash 286862e35bbc4fa7c023077cf794d5852063463a.

failing_ref is parent 70f8b678877ba69f266e1522fcfacb95cfd3c76e.

getHmrRefreshHash on request stores read the HMR cookie. Cookieless requests omitted the server hash from cacheKeyParts and HIT leftover 'use cache' entries after an edit.

PR repair: attach a server-authored hash via request meta; stop writing the cookie.

Do not show this to Dreamers, initial Red Pen, initial Grounders, or first-selection judges.
