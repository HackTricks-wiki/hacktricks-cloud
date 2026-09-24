# Dataplex — open ideas

Open ideas — Dataplex.

- [ ] **`tasks.update` actAs-bypass (UNVERIFIED).** Create a Dataplex task bound to a service account,
  then as a principal WITHOUT `actAs` on that SA, attempt `tasks.update` to change the task's script /
  Spark args and re-run it. Confirm whether code executes as the task SA (confused-deputy) or whether
  update is gated by actAs like create. Pin the exact role that carries `dataplex.tasks.update`. Ship
  only if the actAs gate is genuinely bypassed.
