# Workbench and Colab Enterprise — open ideas

## Resolved

- [x] Determine whether a schedule update can replace notebook content or a custom container while
      retaining another identity. Supported clients make `createNotebookExecutionJobRequest`
      immutable, the execution job has no PATCH, and documented named-user/actAs gates apply.
- [x] Determine whether a schedule preserves VM-local user ADC. It does not: ADC is a runtime-local
      credential file, not schedule state.

## Regression-only authorization test

- [ ] If future API/client releases make notebook execution requests updateable, create a paused,
      far-future schedule and first test the full and nested update masks as owner. Only if the schema
      accepts one should a caller with schedule update but no actAs repeat it. Never resume the
      schedule; delete the schedule, notebook object, bucket and grants after the negative control.

