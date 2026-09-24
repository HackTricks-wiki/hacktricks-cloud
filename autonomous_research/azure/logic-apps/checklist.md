# Logic Apps — Candidate Attacks (not yet lab-fired)

- [ ] Enumerate which built-in connectors return a **reusable** connectionKey vs. which reject with
      `OperationNotAllowed`, and record the min token lifetime accepted.
- [ ] Confirm Standard `hostruntime` anonymous-invoke on a Consumption-vs-Standard split once a
      Function-App-backed Standard workflow can be provisioned (App Service quota wall permitting).
- [ ] Test whether a stolen callback URL keeps working after a workflow **disable/enable** cycle
      (persistence durability of the SAS sig).
