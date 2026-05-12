# Release Rigor Templates

## RELEASE_PLAN
- Task:
- Scope:
- Source merge/tag status:
- Release tag:
- Artifacts/versions:
- Environments:
- Dependencies:
- Risk summary:
- Rollback strategy:

## STAGE_DEPLOY_REPORT
- Environment:
- Release tag:
- Artifacts/versions deployed:
- Deployment timestamp:
- Smoke checks executed:
- Result: PASS | FAIL
- Issues found:
- Action items:

## PROD_PROMOTION_SIGNOFF
- Environment: production
- Release tag:
- Approved by:
- Approval timestamp:
- Artifacts/versions promoted:
- Deployment result: PASS | FAIL
- Post-deploy smoke check result:
- Residual risks:

## ROLLBACK_REPORT
- Trigger reason:
- Rolled back environment:
- Target rollback version:
- Rollback timestamp:
- Verification checks:
- Final status:

## RELEASE_COMPLETION_CHECKLIST
- [ ] Branch policy followed.
- [ ] QA sign-off confirmed for release scope.
- [ ] Release source/tag identified and documented.
- [ ] Release artifacts built and versions documented.
- [ ] Test-stage deployment completed.
- [ ] Stage smoke checks completed and recorded.
- [ ] Production approval received before promotion.
- [ ] Production deployment completed, if approved.
- [ ] Production smoke checks completed, if deployed.
- [ ] Rollback readiness validated.
- [ ] Tracking docs updated if the repo defines them.
