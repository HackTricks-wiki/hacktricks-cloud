# Datastream — open ideas

- [ ] With synthetic SaaS tenants, verify whether `discover` for preview Workday, Dataverse,
  Salesforce Marketing Cloud and ServiceNow profiles returns sensitive sample values as well as
  schema, and whether every v1 method is correctly classified as Data Access.
- [ ] Test minimum permissions and destination-project validation for BigQuery
  `sourceHierarchyDatasets.projectId` using only synthetic datasets. Confirm whether the service
  agent or caller must hold each destination permission; fold into the existing confused-deputy
  technique unless a distinct boundary appears.
- [ ] Verify whether a running stream permits `streams.update` changes to include/exclude object
  sets and BigQuery partitioning/clustering rules, and capture whether this is distinguishable from
  an ordinary update. Fold object omission into the existing DoS/anti-forensics section unless it
  creates a distinct capability.
- [ ] Re-test vestigial `*.setIamPolicy` endpoints after API revisions; currently they return 404 and
  are not a self-grant primitive.
