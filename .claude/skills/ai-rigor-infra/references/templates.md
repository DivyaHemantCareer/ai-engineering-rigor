# Infrastructure Rigor Templates

## INFRA_CHANGE_PLAN
- Task:
- Environment target:
- Change type (new/update/maintenance):
- Resources impacted:
- Dependencies/order:
- Security controls impacted:
- Rollback strategy:

## INFRA_VALIDATION_REPORT
- Task:
- Validation date:
- Commands/checks executed:
- Dry-run/what-if result:
- Resource state verification:
- Security baseline verification:
- Issues found and mitigations:

## INFRA_SIGNOFF_PACKET
- Task:
- Environment:
- IaC/scripts changed:
- Validation summary:
- Residual risks:
- Approval gate status:
- Final decision: READY | NOT READY
- Notes:

## INFRA_COMPLETION_CHECKLIST
- [ ] Branch policy followed.
- [ ] Dev-to-Infra handoff reviewed and complete.
- [ ] IaC/script plan defined.
- [ ] No secrets introduced in code/config.
- [ ] Managed identity and least privilege reviewed.
- [ ] Encryption in transit and at rest validated.
- [ ] Stage validation checks completed.
- [ ] Infra sign-off packet issued.
- [ ] Tracking docs updated if the repo defines them.
