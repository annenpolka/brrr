# COMMANDS

```
# in-tree on failing_ref 96f62ae6e9cb1b123de383fa2542812c9ba3b7db
# (not executed on this lab host)

# case A (honest, in-tree)
go test golang.org/x/mod/sumdb -run TestClientLookup
# Lookup("rsc.io/sampler", "v1.3.0") ->
#   rsc.io/sampler v1.3.0 h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4=

# case C
go test golang.org/x/mod/sumdb -run TestClientGONOSUMDB
# matching GONOSUMDB prefix -> ErrGONOSUMDB

# case D
go test golang.org/x/mod/sumdb -run TestClientFork
# disagreeing signed trees -> ErrSecurity

# case B (fixture, not an in-tree test on this revision)
# log contains only golang.org/x/good@v1.0.0 as a real record
# /lookup/golang.org/x/bad@v1.0.0 = FormatRecord(good) + signed tree
# whose Note.Text is FormatTree + "golang.org/x/bad v1.0.0 h1:7uVkIFmeBqHfdjD+gZwtXXI+RODJ2Wc4O7MPEh/QiW4=\n"
# Client.Lookup("golang.org/x/bad", "v1.0.0")
# ParseRecord authenticates the good record; prefix scan walks the cache payload
```

Not executed on this lab host.
