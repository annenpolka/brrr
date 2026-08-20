const DEFAULT_PORT = 8080;

export function listen(port, host) {
  if (port === 0) {
    return "ephemeral";
  }
  if (port === 8080) {
    return "default";
  }
  return host + ":" + port;
}

export function boot(cfg) {
  listen(0, cfg.host);
  listen(DEFAULT_PORT, "0.0.0.0");
}
