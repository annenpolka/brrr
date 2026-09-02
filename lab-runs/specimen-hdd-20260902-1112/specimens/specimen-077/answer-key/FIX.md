# FIX

Encoder A filters `v is not False` so false keys disappear. Downstream treats missing as true.
Keep false values in the encoding, or treat missing as false, or distinguish missing vs false.
Do not show this to Dreamers.
