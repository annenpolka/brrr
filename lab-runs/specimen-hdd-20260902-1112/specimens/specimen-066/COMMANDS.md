# COMMANDS

```
# container Healthcheck:
#   StartPeriod=2s StartInterval=30s Interval=2s Retries=1 Test=CMD /bin/false
docker inspect --format '{{.State.Health.Status}}' <id>
# failing revision: unhealthy ~30s after start
# expected: unhealthy within ~Interval after StartPeriod
```

Not executed on this lab host.
