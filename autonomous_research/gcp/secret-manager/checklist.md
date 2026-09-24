# Secret Manager — open ideas

Open ideas — Secret Manager.

- [ ] **`secrets.rotate` / `enableManagedRotation` confused-deputy (UNVERIFIED).** Set a secret's
  rotation topic / managed-rotation config and determine whether the rotation mechanism performs any
  action *as a Google service agent* that a caller holding only `secretmanager.secrets.update` could
  abuse (e.g. publish to an attacker topic, or trigger a rotation function as a higher-priv identity).
  Confirm min-perm and that it is not merely a self-scheduled notification. Ship only if a real
  confused-deputy / privilege-crossing effect is demonstrated.
