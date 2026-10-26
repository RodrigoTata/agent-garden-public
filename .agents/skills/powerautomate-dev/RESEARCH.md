# Power Automate cloud flows: programmatic read / analyze / debug / simplify (research notes)

Researched 2026-09-26. Sources are primary only: learn.microsoft.com (Power Automate, Power Platform, Dataverse, Azure Logic Apps, REST references), MicrosoftDocs GitHub repos, and Microsoft's own PowerShell Gallery modules (read as source code). Every claim has its source URL next to it.
Labels used:
- **[OFFICIAL]**: documented and supported.
- **[UNSUPPORTED-DOCUMENTED]**: Microsoft says it exists but isn't supported.
- **[UNDOCUMENTED]**: seen only in Microsoft code or observed in practice, with no doc page.
- **[INFERENCE]**: my reasoning, not stated by Microsoft.

---

## 0. TL;DR for the skill

- **Supported ways to read flows:**
  - The Dataverse Web API: `workflow` table, `clientdata` = definition + connectionReferences. It covers **solution-aware flows only**.
  - The Power Automate Management / Power Automate for Admins connectors.
  - The Power Platform API (`api.powerplatform.com/powerautomate/...`).
  - The admin PowerShell module.
  - `api.flow.microsoft.com` (ProcessSimple) is explicitly **not supported** ("use at their own risk… breaking changes could occur"). https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code
- **Supported sources of run history:**
  - Dataverse `flowrun` table (solution flows only; 28-day TTL by default; not lossless). https://learn.microsoft.com/en-us/power-automate/dataverse/cloud-flow-run-metadata
  - Power Platform API `GET /powerautomate/environments/{env}/flowRuns?workflowId=…&api-version=2024-10-01`. https://learn.microsoft.com/en-us/rest/api/power-platform/powerautomate/flow-runs/list-flow-runs
  - Application Insights (Managed Environments only; has trigger and action telemetry). https://learn.microsoft.com/en-us/power-platform/admin/app-insights-cloud-flow
- **No supported API returns per-action inputs/outputs of a run.** The only way to get them is the unsupported `api.flow.microsoft.com …/runs/{runId}/actions` surface. It mirrors the documented Azure Logic Apps runs/actions/repetitions/trigger-histories REST model, so the Logic Apps REST reference is the best official description of the object shapes. https://learn.microsoft.com/en-us/rest/api/logic/workflow-run-actions/list **[INFERENCE: shape parity]**
- **Why `GET …/flows/{id}/runs` returned `value: []` for a Stopped flow.** Most likely it's simply that no run started in the retention window:
  - (a) Turning a flow off means "no new runs start". https://learn.microsoft.com/en-us/power-automate/limits-and-config#turn-off-or-delete-flows
  - (b) Run history is kept only 28 days in the portal ("Run history" page), and "Run retention in storage" is 30 days. https://learn.microsoft.com/en-us/troubleshoot/power-platform/power-automate/flow-run-issues/missing-runs-or-triggers-history-for-a-flow and https://learn.microsoft.com/en-us/power-automate/limits-and-config#duration-limits
  - (c) Trigger evaluations that did not fire (for example, trigger condition not met) are not runs. They appear as skipped trigger checks under "All runs" (portal), and in Logic Apps they are the separate `triggers/{name}/histories` resource. https://learn.microsoft.com/en-us/troubleshoot/power-platform/power-automate/flow-run-issues/triggers-troubleshoot#determine-whether-trigger-check-is-skipped and https://learn.microsoft.com/en-us/rest/api/logic/workflow-trigger-histories/list
  - (d) Microsoft's admin PowerShell module reads runs through a different, admin-scoped route (`…/scopes/admin/environments/{env}/flows/{flow}/runs`). If the caller isn't an owner of the flow, the maker route may not be the right one. **[UNDOCUMENTED, from module source]**
  - Next checks: the flow's `lastModifiedTime`/state; the admin route; trigger histories; the Dataverse `flowrun` table if the flow is solution-aware; Application Insights.

---

## 1. API surfaces

### 1.1 Comparison matrix

| Surface | Status | Flow list | Definition | State | Owners/sharing | Connections | Run history | Per-action run detail | Trigger history | Resubmit / cancel | Turn on/off |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Dataverse Web API `workflows` (+ `flowruns`) | [OFFICIAL] solution flows only | yes | yes (`clientdata`) | yes (`statecode`) | yes (`ownerid`, RetrieveSharedPrincipalsAndAccess) | via connectionReferences in `clientdata` | yes (`flowrun`, run-level only) | no | no | no | yes (PATCH `statecode`) |
| Power Platform API `powerautomate/*` | [OFFICIAL] needs Dataverse | yes (`cloudFlows`) | not documented in the response schema | ? | filter by owner/creator | ? | yes (`flowRuns`) | no | no | no | no |
| Power Automate Management connector | [OFFICIAL] | yes | yes (Get Flow / Get Flow as Admin `includeFlowDefinition`) | yes | yes | yes | **no list-runs action** | no | no | yes | yes |
| Power Automate for Admins connector | [OFFICIAL] | no | no | – | yes | no | no | no | no | no | yes |
| Admin PowerShell (`Microsoft.PowerApps.Administration.PowerShell`) | [OFFICIAL] Windows PowerShell 5.x | yes (`Get-AdminFlow`) | via object `.Internal` | yes | yes | yes | no documented admin cmdlet | no | no | no | yes |
| Maker PowerShell (`Microsoft.PowerApps.PowerShell`) `Get-FlowRun` | module on PSGallery; no Learn reference page found (404) | yes | – | – | – | – | yes (name/status/startTime) | no | no | no | yes |
| `api.flow.microsoft.com` (ProcessSimple) | [UNSUPPORTED-DOCUMENTED] | yes | yes | yes | yes | yes | yes | yes (inputsLink/outputsLink) | [UNDOCUMENTED] | [UNDOCUMENTED] | yes |

### 1.2 Dataverse Web API: `workflow` table [OFFICIAL]
- "All flows are stored in Dataverse and you can use either the Dataverse SDK for .NET or Web API to manage them." The article covers flows on the **Solutions** tab only: "Currently, managing flows under **My Flows** aren't supported with code." https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code
- Base URL: `https://<org>.<region>.dynamics.com/api/data/v9.2`. https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code
- **List cloud flows:** `GET [Org]/api/data/v9.2/workflows?$filter=category eq 5 and statecode eq 1&$select=category,_createdby_value,createdon,description,ismanaged,_modifiedby_value,modifiedon,name,_ownerid_value,statecode,type,workflowid,workflowidunique`. Add the header `Prefer: odata.include-annotations="*"` to get formatted values. https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code
- **Key columns** (https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code):
  - `category`: 5 = Modern Flow (automated/instant/scheduled), 6 = desktop flow.
  - `clientdata`: "string-encoded JSON of the flow definition and its connectionReferences".
  - `statecode`: 0 Draft(Off), 1 Activated(On), 2 Suspended.
  - `type`: 1 Definition, 2 Activation, 3 Template.
  - Also `workflowid`, `workflowidunique`, `ismanaged`, `ownerid`.
- **`statuscode` values:** 1 Draft (state 0), 2 Activated (state 1), **3 CompanyDLPViolation** (state 2 Suspended). https://learn.microsoft.com/en-us/power-apps/developer/data-platform/reference/entities/workflow
- **Other `workflow` columns useful for diagnosis** (https://learn.microsoft.com/en-us/power-apps/developer/data-platform/reference/entities/workflow):
  - `suspensionreasondetails` (Memo, 500 chars, no description).
  - `throttlingbehavior` (0 None, 1 TenantPool, 2 CopilotStudio).
  - `modernflowtype` (0 PowerAutomateFlow, 1 CopilotStudioFlow, 2 M365CopilotAgentFlow).
  - `clientdataiscompressed` ("For Internal Use Only"). **[OPEN: whether `clientdata` can come back compressed]**
  - `resourceid` ("For internal use only").
- **Turn on/off:** `PATCH workflows({id})` with `{"statecode":1}` (the article's example also changes the owner via `ownerid@odata.bind`). https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code
- **Create** (requires `category`, `name`, `type`, `primaryentity`="none", `clientdata`) and **delete**. A newly created flow has statecode 0 (off). https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code
- **Sharing:** `RetrieveSharedPrincipalsAndAccess`, `GrantAccess`, `ModifyAccess`, `RevokeAccess`. https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code
- **Authentication:** OAuth to the org URI. https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code
  - **[INFERENCE]** `az account get-access-token --resource https://<org>.crm.dynamics.com` should work. Not verified in these docs.

### 1.3 Dataverse run history: `flowrun`, `flowevent`, `flowlog` [OFFICIAL]
- "Only solution cloud flows, with their definitions in Dataverse, can have their run history stored in Dataverse." Storage is an elastic table. https://learn.microsoft.com/en-us/power-automate/dataverse/cloud-flow-run-metadata
- **Entity set** `flowruns`, TableType Elastic, UserOwned. https://learn.microsoft.com/en-us/power-apps/developer/data-platform/reference/entities/flowrun
- **Columns** (https://learn.microsoft.com/en-us/power-apps/developer/data-platform/reference/entities/flowrun):
  - `name` (the "logic app Id of the flow run", i.e. the run id; see https://learn.microsoft.com/en-us/power-automate/dataverse/cloud-flow-run-metadata)
  - `starttime`, `endtime`, `duration` (ms)
  - `status` (String; the doc lists Success/Failed/Cancelled)
  - `triggertype` (Automated/Scheduled/Manual)
  - `errorcode` (100 chars), `errormessage` (20,000 chars)
  - `workflowid` (string), `_workflow_value` (lookup)
  - `parentrunid`, `isprimary`, `modernflowtype`, `clienttrackingid`, `partitionid`, `ttlinseconds`
  - Relationship `flowrun_flowlog_cloudflowrunid` to `flowlog`.
- **What it does NOT hold:** no per-action inputs/outputs. The documented elements are run-level only. https://learn.microsoft.com/en-us/power-automate/dataverse/cloud-flow-run-metadata
- **Retention:**
  - Default 28 days (2,419,200 s), controlled by `Organization.FlowRunTimeToLiveInSeconds`.
  - The admin center offers 28/14/7 days/Disabled; a custom value can be set via the API. A value of 0 stops ingestion.
  - Source: https://learn.microsoft.com/en-us/power-automate/dataverse/cloud-flow-run-metadata
- **Completeness caveats:**
  - Ingestion "isn't 100 percent lossless". The portal run history "is transactional… lossless".
  - The `flowevent` table (EventType `FlowRunIngestion`) signals gaps, with codes TtlSettingEqual0, IngestionDisabledByOrgSettings, ElasticTableStorageCapacityReached, ElasticTablePartitionLimitReached, IngestionRateDataLoss, ElasticTableNoRoleForUser, and others.
  - Owners need read on FlowRun, or their records aren't stored. There is a 20 GB per-user partition limit.
  - Reads of FlowRun count toward Power Platform request limits; writes don't.
  - Source: https://learn.microsoft.com/en-us/power-automate/dataverse/cloud-flow-run-metadata
- Don't trigger flows on FlowRun/FlowLog changes (infinite loop). https://learn.microsoft.com/en-us/power-automate/dataverse/cloud-flow-run-metadata

### 1.4 Power Platform API (`api.powerplatform.com`) [OFFICIAL]
- **Cloud flows:** `GET https://api.powerplatform.com/powerautomate/environments/{environmentId}/cloudFlows?api-version=2024-10-01`. Optional filters: `workflowId`, `resourceId`, `createdBy`, `ownerId`, `createdOnStartDate/EndDate`, `modifiedOnStartDate/EndDate`. Returns 204 if nothing matches, and **404 "Environment does not have a Microsoft Dataverse database"**. https://learn.microsoft.com/en-us/rest/api/power-platform/powerautomate/cloud-flows/list-cloud-flows
- **Flow runs:** `GET https://api.powerplatform.com/powerautomate/environments/{environmentId}/flowRuns?workflowId={workflowId}&api-version=2024-10-01`. `workflowId` is required; returns 204 if there are no runs. https://learn.microsoft.com/en-us/rest/api/power-platform/powerautomate/flow-runs/list-flow-runs
  - The doc publishes no response schema. **[INFERENCE: backed by Dataverse FlowRun, given the Dataverse-required 404]**
- **Flow actions** (a design-time inventory of actions and triggers, not run results): `GET …/powerautomate/environments/{environmentId}/flowActions?workflowId=&connector=&isTrigger=&parameterName=&parameterValue=&exact=&parentProcessStageId=&api-version=2024-10-01`. https://learn.microsoft.com/en-us/rest/api/power-platform/powerautomate/flow-actions/list-flow-actions
  - Useful for tenant-wide "which flows use connector X / parameter Y" analysis.
- **Authentication** (https://learn.microsoft.com/en-us/power-platform/admin/programmability-authentication-v2):
  - Scope `https://api.powerplatform.com/.default`. The Power Platform API app id is `8578e004-a5c6-46e7-913e-12f58912df43`.
  - Delegated permissions only; service principals need an RBAC role.
  - PowerShell example: `Get-AzAccessToken -ResourceUrl "https://api.powerplatform.com"`.
  - **[INFERENCE]** `az account get-access-token --resource https://api.powerplatform.com` is the Azure CLI equivalent. Not tested here.

### 1.5 Management connectors [OFFICIAL]
- **Power Automate Management** actions (https://learn.microsoft.com/en-us/connectors/flowmanagement/):
  - Get Flow, Get Flow as Admin (`includeFlowDefinition`), List My Flows, List Flows as Admin (V2: `$top`, `expandSuspensionInfo`, `includeSoftDeletedFlows`; returns no definition).
  - List Flow Owners, List Run-Only Users, List My Connections, List Connectors, List Callback URL.
  - Turn On/Off Flow (`StartFlow`/`StopFlow`), Cancel Flow Run (`CancelFlowRun`: env, flow, runId), Resubmit Flow (`ResubmitFlow`: env, flow, **triggerName**, runId).
  - Create/Update/Delete Flow, Restore Deleted Flow as Admin.
  - Throttling: 5 calls/60 s and 300 non-GET/hour per connection.
- **No "list runs" or "get run actions" action.** The monitoring guidance says the connector retrieves "metadata and run history", but the action list doesn't back that up. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/monitoring-and-alerting vs https://learn.microsoft.com/en-us/connectors/flowmanagement/
- **Suspension data:** `AdminFlowProperties.estimatedSuspensionData` has `reason`, `time`, `powerAppPlanExcluded`. https://learn.microsoft.com/en-us/connectors/flowmanagement/
- **Power Automate for Admins** has only Disable/Enable/Remove Flow as Admin, Get/Edit Flow Owner Role, and Get/Remove Flow User Details, at 100 calls/60 s. https://learn.microsoft.com/en-us/connectors/microsoftflowforadmins/
- "List My Flows" doesn't return solution cloud flows. "List Flows as Admin" returns both non-solution and solution flows. https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/add-app-solution-default

### 1.6 PowerShell [OFFICIAL modules]
- Two modules: `Microsoft.PowerApps.Administration.PowerShell` (admin) and `Microsoft.PowerApps.PowerShell` (maker). They need **Windows PowerShell 5.x** (.NET Framework; incompatible with PS 6+). https://learn.microsoft.com/en-us/power-platform/admin/powerapps-powershell
- **Admin flow cmdlets** (https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/):
  - `Get-AdminFlow` (params `-EnvironmentName`, `-FlowName`, `-CreatedBy`, `-IncludeDeleted`, `-ApiVersion` default **2016-11-01**; see https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/get-adminflow)
  - `Enable-AdminFlow`, `Disable-AdminFlow`, `Remove-AdminFlow`, `Restore-AdminFlow`
  - `Get-AdminFlowOwnerRole`, `Get-AdminFlowWithHttpAction`, `Add-AdminFlowsToSolution`
  - `Get-AdminFlowAtRiskOfSuspension` (https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/get-adminflowatriskofsuspension)
- **What the module source shows** **[UNDOCUMENTED: read from Microsoft code, Microsoft.PowerApps.PowerShell 1.0.47 and Administration 2.0.217 from https://www.powershellgallery.com/packages/Microsoft.PowerApps.PowerShell and https://www.powershellgallery.com/packages/Microsoft.PowerApps.Administration.PowerShell]**:
  - Token audience mapping: `api.flow.microsoft.com` → `https://service.flow.microsoft.com/`. This matches the `az … --resource https://service.flow.microsoft.com/` you already verified.
  - `Get-FlowRun` = `GET https://api.flow.microsoft.com/providers/Microsoft.ProcessSimple/environments/{env}/flows/{flow}/runs?api-version=2016-11-01`. It exposes only `name`, `properties.status`, `properties.startTime` plus the raw object.
  - Enable/Disable (maker) = `POST …/flows/{flow}/start` and `…/stop`. Admin = `POST …/scopes/admin/environments/{env}/flows/{flow}/start|stop`.
  - Admin list = `GET …/scopes/admin/environments/{env}/v2/flows?api-version=…&$top=…`. Admin get = `…/scopes/admin/environments/{env}/flows/{flow}`.
  - Admin runs (used to find the last run time) = `GET …/scopes/admin/environments/{env}/flows/{flow}/runs?api-version=2016-11-01&$top=1`.
  - At-risk list = `GET …/scopes/admin/environments/{env}/scheduledSuspensionFlows?api-version=…&$top=50`. It reads `properties.estimatedSuspensionData.{reason,time,powerAppPlanExcluded,dynamicsPlanExcluded,isVisible}`.
  - Suspension reason values in the code: `MissingPremiumLicense`, `MissingAttendedRPA`, `MissingUnAttendedRPA`, `MissingRPAUnattendedAddOn`, `NonCompliantServicePrincipalFlow`.

### 1.7 `api.flow.microsoft.com` (ProcessSimple) [UNSUPPORTED-DOCUMENTED]
- "The API at **api.flow.microsoft.com** isn't supported… Customers can use the unsupported APIs at `api.flow.microsoft.com` at their own risk. These APIs are subject to change, so breaking changes could occur." https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code#what-about-the-api-at-apiflowmicrosoftcom
- **Shapes observed or from module source [UNDOCUMENTED]:**
  - `GET /providers/Microsoft.ProcessSimple/environments/{env}/flows/{flowId}?api-version=2016-11-01&$expand=properties.definition` (verified by you)
  - `…/flows/{flowId}/runs?api-version=2016-11-01[&$top=N]`
  - `…/runs/{runId}/actions`
  - `…/runs/{runId}/actions/{actionName}/repetitions`
  - `…/triggers/{triggerName}/histories`
  - `POST …/runs/{runId}/cancel`
  - `POST …/triggers/{triggerName}/histories/{runId}/resubmit`
  - The last five are **[INFERENCE by analogy to the Logic Apps REST routes; the connector's Resubmit taking triggerName+runId supports the resubmit shape]**. Verify each before relying on it.
- **Recommended skill policy:** use it for read-only diagnostics. Detect and handle schema drift. Prefer the Dataverse API or connectors for anything that writes.

### 1.8 Solution-aware vs non-solution flows
- **Connections:** non-solution flows use connections; solution flows use connection references and environment variables. Only solution flows support environment variables, versioning/drafts, run history in Dataverse, and unlimited ownership (non-solution: 600 per user). https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/understand-benefits-solution-aware-flows and https://learn.microsoft.com/en-us/power-automate/limits-and-config#my-flows-limit
- **Drafts:** solution flows can have unpublished drafts. Runtime uses the published version. Draft records expire after 6 months and published records after 12 months. **[OPEN: which version the API `$expand=properties.definition` returns]** https://learn.microsoft.com/en-us/power-automate/drafts-versioning
- **Default solution setting:** environments can create flows in solutions by default (`organization.enableFlowsInSolutionByDefault`). `Add-AdminFlowsToSolution` migrates existing flows, and moving a flow into a solution is one-way. https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/add-app-solution-default
  - **Doc contradiction:** the same page says "All new environments provisioned with a Dataverse database have the Cloud flows setting enabled by default" and also "The cloud flows setting continues to be off by default and optional." Check the org setting instead of assuming.
- **Flow ID in portal URLs:** both non-solution (`…/environments/{env}/flows/{flowId}/details`) and solution (`…/solutions/{solutionId}/flows/{flowId}/details`) URLs carry the FlowName GUID after `flows/`. https://learn.microsoft.com/en-us/power-platform/admin/powerapps-powershell#associate-in-context-flows-to-an-app

### 1.9 Run history retention (conflicting numbers; treat 28 days as the safe window)
- **28 days:**
  - Portal run history: "By default, flow run data is stored for 28 days." https://learn.microsoft.com/en-us/troubleshoot/power-platform/power-automate/flow-run-issues/missing-runs-or-triggers-history-for-a-flow
  - The portal labels it "28-day run history". https://learn.microsoft.com/en-us/power-automate/fix-flow-failures
  - Dataverse `flowrun`: 28 days by default, configurable. https://learn.microsoft.com/en-us/power-automate/dataverse/cloud-flow-run-metadata
- **30 days:**
  - Limits table: "Run retention in storage — 30 days (calculated using a run's start time)". https://learn.microsoft.com/en-us/power-automate/limits-and-config#duration-limits
  - Analytics shows "a rolling 30-day run history". https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/monitoring-and-alerting

---

## 2. Action-level run details, statuses, errors, suspension

### 2.1 Run and action object model (Logic Apps REST, the official reference for the engine's shapes)
- **Runs list:** `GET …/workflows/{wf}/runs?api-version=…&$top=&$filter=` where `$filter` supports **Status, StartTime, ClientTrackingId**. Paging uses `nextLink`. https://learn.microsoft.com/en-us/rest/api/logic/workflow-runs/list
  - `WorkflowRun.properties`: `status`, `code`, `error`, `startTime`, `endTime`, `waitEndTime`, `correlation.clientTrackingId`, `trigger`, `outputs`, `response`, `workflow` (version reference).
  - `trigger` includes `name`, `status`, `code`, `inputsLink`, `outputsLink`, `scheduledTime`, `trackedProperties`.
- **Run actions:** `GET …/runs/{runName}/actions?$top=&$filter=` (filter supports Status). https://learn.microsoft.com/en-us/rest/api/logic/workflow-run-actions/list
  - `WorkflowRunAction.properties`: `status`, `code`, `error`, `startTime`, `endTime`, `inputsLink`, `outputsLink`, `retryHistory[]` (code, error, clientRequestId, serviceRequestId, start/end), `correlation.actionTrackingId`, `trackedProperties`, `trackingId`.
- **ContentLink** = `{uri, contentVersion, contentSize, contentHash{algorithm,value}, metadata}`. https://learn.microsoft.com/en-us/rest/api/logic/workflow-run-actions/list
  - The `uri` is a pre-signed runtime URL with query `se=` (expiry), `sp=`, `sv=`, `sig=`. Fetch it with plain GET and no bearer token. https://learn.microsoft.com/en-us/rest/api/logic/workflow-run-action-repetitions/list **[INFERENCE from the sample URLs: SAS-style, expiring; don't persist]**
- **Loop repetitions:** `GET …/runs/{run}/actions/{actionName}/repetitions`. Each item has `name` "000000", "000001"…, `repetitionIndexes[{scopeName,itemIndex}]`, `iterationCount`, `status`, `code`, `error`, `inputsLink`, `outputsLink`, `retryHistory`. https://learn.microsoft.com/en-us/rest/api/logic/workflow-run-action-repetitions/list
  - **[INFERENCE]** For actions inside Foreach/Until, the top-level `/actions` entry is an aggregate. Drill into `/repetitions` to find the failing iteration.
- **Trigger histories:** `GET …/triggers/{triggerName}/histories?$top=&$filter=` (Status, StartTime, ClientTrackingId). Each item has `fired` (bool), `run` reference, `status`, `code`, `error`, `inputsLink`, `outputsLink`, `scheduledTime`. https://learn.microsoft.com/en-us/rest/api/logic/workflow-trigger-histories/list
- **Resubmit** = `POST …/triggers/{trigger}/histories/{historyName}/resubmit`, where historyName "corresponds to the run name". Returns 202. https://learn.microsoft.com/en-us/rest/api/logic/workflow-trigger-histories/resubmit
- **Cancel** = `POST …/runs/{run}/cancel`. https://learn.microsoft.com/en-us/rest/api/logic/workflow-runs/cancel
- **Rate limit on reading run content:** the runtime endpoint allows "Read calls per 5 minutes: 6,000 for Low; 60,000 for all others". This "applies to calls that get the raw inputs and outputs from a cloud flow's run history". https://learn.microsoft.com/en-us/power-automate/limits-and-config#runtime-endpoint-request-limits

### 2.2 Status values
- **WorkflowStatus enum** (runs, actions, triggers): NotSpecified, Paused, Running, Waiting, Succeeded, Skipped, Suspended, Cancelled, Failed, Faulted, TimedOut, Aborted, Ignored. https://learn.microsoft.com/en-us/rest/api/logic/workflow-runs/list
- **`runAfter` accepts only** Succeeded, Failed, Skipped, TimedOut. https://learn.microsoft.com/en-us/azure/logic-apps/error-exception-handling
- **How run status is derived:**
  - An unhandled failure marks the action Failed and its successors Skipped. If any branch ends in failure, the run is Failed.
  - A scope is Failed if its final action is Failed or Aborted.
  - Source: https://learn.microsoft.com/en-us/azure/logic-apps/error-exception-handling
- **Bulk cancel UI:** Waiting → Canceling → Canceled, which can take up to 24 h. If the flow is turned off, pending canceled runs "remain **Waiting**" until it's turned on again. https://learn.microsoft.com/en-us/power-automate/how-tos-bulk-resubmit
- **Cascade failures:** Power Automate treats skipped actions after a failed dependency as cascade failures. Look for the **first** failed action. https://learn.microsoft.com/en-us/power-automate/understand-flow-failure-notifications

### 2.3 Error codes (Power Automate reference)
- **Error names and categories** (https://learn.microsoft.com/en-us/power-automate/error-reference):
  - Design-time: InvalidTemplate, FlowCheckerError, DuplicateActionName, MissingRequiredProperty.
  - Runtime expressions: ExpressionEvaluationFailed, ContentConversionFailed.
  - Connections: InvalidConnection, ConnectionNotConfigured, Unauthorized 401, Forbidden 403, ConnectionAuthorizationFailed.
  - Connectors/APIs: ActionFailed, BadRequest 400, NotFound 404.
  - Triggers: TriggerConditionNotMet.
  - Timeouts/throttling: ActionTimedOut, OperationTimedOut, WorkflowRunActionRepetitionQuotaExceeded, FlowRunQuotaExceeded.
  - Licensing: DirectApiAuthorizationRequired.
- **Fix classes:**
  - 401/403 → fix the connection, then Resubmit.
  - 400/404 → fix the action configuration.
  - 500/502 → transient; resubmit.
  - Source: https://learn.microsoft.com/en-us/power-automate/fix-flow-failures
- **Connector throttling:** 429 with "Rate limit is exceeded. Try again in N seconds". https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/understand-limits
- **Duplicate side effects:** actions can run more than once because of the "at-least-once" design of Azure Logic Apps. Design idempotently. https://learn.microsoft.com/en-us/troubleshoot/power-platform/power-automate/flow-run-issues/triggers-troubleshoot#flow-or-actions-run-multiple-times

### 2.4 Why a flow is off, suspended or not triggering (documented causes)
| Cause | Rule | Source |
|---|---|---|
| Flows with errors | "A cloud flow that has a trigger or actions that fail continuously is turned off" after **14 days** | https://learn.microsoft.com/en-us/power-automate/limits-and-config#retention-limits |
| No trigger activity | Not triggered in **90 days** → "might be turned off". Owners of premium or Process/per-flow licensed flows are exempt. Owners are notified 30 days before. | https://learn.microsoft.com/en-us/power-automate/limits-and-config#retention-limits |
| Consistently throttled | Above throughput limits for 14 days → turned off | https://learn.microsoft.com/en-us/power-automate/limits-and-config#throughput-limits |
| DLP violation | "the service suspends the flow and the trigger doesn't fire"; Dataverse `statuscode` 3 CompanyDLPViolation | https://learn.microsoft.com/en-us/troubleshoot/power-platform/power-automate/flow-run-issues/triggers-troubleshoot and https://learn.microsoft.com/en-us/power-apps/developer/data-platform/reference/entities/workflow |
| Premium license enforcement | 90 days to remediate → environment lifecycle ops blocked → after 180 days total, "flow suspension" possible (owner left, expired premium, Power Apps/D365 out-of-context) | https://learn.microsoft.com/en-us/power-platform/admin/power-automate-licensing/when-flows-are-turned-off |
| Trigger registration failure | "There's a problem with the flow's trigger" (often allowlist/IP); re-save to re-register | https://learn.microsoft.com/en-us/troubleshoot/power-platform/power-automate/flow-run-issues/triggers-troubleshoot |
| Broken connection | Expired password or token lifetime policy | same |
| Admin mode (background ops off) | Dataverse-triggered flows don't fire | same |
| Environment URL changed | Edit and save each flow | same |
| HTTP/Teams webhook URL migration | Old `logic.azure.com` URLs stopped working on 2025-11-30 (Logic Apps architecture environments) | same |

- **Programmatic suspension signals:**
  - Connector `estimatedSuspensionData.reason/time`. https://learn.microsoft.com/en-us/connectors/flowmanagement/
  - `Get-AdminFlowAtRiskOfSuspension`. https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/get-adminflowatriskofsuspension
  - Dataverse `statecode`=2, `statuscode`, and `suspensionreasondetails`. https://learn.microsoft.com/en-us/power-apps/developer/data-platform/reference/entities/workflow
  - At runtime, `workflow().tags.environmentFlowSuspensionReason`. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/error-handling
  - **[UNDOCUMENTED]** The api.flow GET-flow payload may expose suspension properties such as `flowSuspensionReason`. Treat them as opportunistic.
- **Pending work when a flow is turned off:**
  - "When you turn off a cloud flow, no new runs start. All in-progress and pending runs continue until they finish." https://learn.microsoft.com/en-us/power-automate/limits-and-config#turn-off-or-delete-flows and https://learn.microsoft.com/en-us/power-automate/disable-flow
  - Deleting a flow cancels in-progress runs. https://learn.microsoft.com/en-us/power-automate/limits-and-config#turn-off-or-delete-flows
  - Approvals inside a run are bounded by the 30-day run duration: "After 30 days, any pending steps time out." https://learn.microsoft.com/en-us/power-automate/limits-and-config#duration-limits
- **Turning a flow back on:**
  - Polling triggers (for example, recurrence and SharePoint) catch up on all events missed while off. Webhook triggers only see new events.
  - To reset a polling trigger, copy the flow and delete the original.
  - Sources: https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/optimize-power-automate-triggers and https://learn.microsoft.com/en-us/troubleshoot/power-platform/power-automate/flow-run-issues/triggers-troubleshoot#trigger-fires-for-old-events

### 2.5 Other telemetry
- **Application Insights:**
  - Runs land in the `requests` table. Triggers and actions land in `dependencies`, with `customDimensions` fields `resourceProvider`='Cloud Flow', `signalCategory` ('Cloud flow runs'/'Cloud flow triggers'/'Cloud flow actions'), `environmentId`, `resourceId`=flowId, and `name`=action name.
  - Managed Environments only. Not lossless.
  - Source: https://learn.microsoft.com/en-us/power-platform/admin/app-insights-cloud-flow
- **Failure emails:**
  - Per-run alerts are sent only for known-fixable causes, with a 28-day cooldown per flow. There is also a weekly digest.
  - Admins use the PPAC "Monitor" view.
  - Source: https://learn.microsoft.com/en-us/power-automate/understand-flow-failure-notifications

---

## 3. Definition schema (Workflow Definition Language)

- **Container:** Power Automate `clientdata` = `{"properties":{"connectionReferences":{…},"definition":{…}},"schemaVersion":"1.0.0.0"}`. https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code
  - `definition.$schema` = `https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#`.
  - Standard parameters: `$connections` (Object) and `$authentication` (SecureObject).
- **connectionReferences entry:** `{ "runtimeSource": "embedded"|…, "connection": { "name" | "connectionReferenceLogicalName" }, "api": { "name": "shared_…" } }`. https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code
- **OpenApiConnection action:**
  - `inputs.host = {apiId: "/providers/Microsoft.PowerApps/apis/shared_…", connectionName, operationId}`, plus `inputs.parameters` and `inputs.authentication = "@parameters('$authentication')"`.
  - Example: Dataverse `ListRecords` with `$select`/`$top`.
  - Manual trigger: `type: "Request", kind: "Button"`.
  - Source: https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code
- **Top-level keys:** `$schema`, `actions`, `contentVersion`, `outputs`, `parameters`, `staticResults`, `triggers`. https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-workflow-definition-language
  - Logic Apps' own caps (actions 250, parameters 50, triggers 10, outputs 10) differ from Power Automate's. Use Power Automate's limits: 500 actions/workflow, nesting depth 8, 25 switch cases, 250 variables, action/trigger name ≤ 80 chars, expression ≤ 8,192 chars. https://learn.microsoft.com/en-us/power-automate/limits-and-config#flow-definition-limits
- **Action skeleton:** `{type, inputs, runAfter, runtimeConfiguration, operationOptions}`. `runAfter` = `{ "<prev>": ["Succeeded"|"Failed"|"Skipped"|"TimedOut", …] }`. https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-workflow-actions-triggers
- **Control actions** (https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-workflow-actions-triggers):
  - `Foreach`: `foreach` expression, nested `actions`, `runtimeConfiguration.concurrency.repetitions`, `operationOptions: "Sequential"`.
  - `If`: `expression`, `actions`, `else.actions`.
  - `Scope`: `actions`.
  - `Switch`: `expression`, `cases{…:{case, actions}}`, `default`.
  - `Until`: `expression`, `limit{count, timeout}`; defaults count 60, timeout PT1H.
  - `Terminate`: `runStatus` Failed/Cancelled/Succeeded, with `runError{code,message}`.
- **Until behavior:**
  - The loop runs its body first, then checks the condition. Hitting the limit ends the loop as success unless `operationOptions: "FailWhenLimitsReached"` is set. https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-control-flow-loops
  - Power Automate limits: Until iterations default 60, max 5,000. https://learn.microsoft.com/en-us/power-automate/limits-and-config#concurrency-looping-and-debatching-limits
- **Trigger options** (https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-workflow-actions-triggers):
  - `conditions: [{ "expression": "@…" }]` (trigger conditions).
  - `splitOn`.
  - `recurrence{frequency, interval, startTime, timeZone}`.
  - `runtimeConfiguration.concurrency{runs, maximumWaitingRuns}`.
- **Other `runtimeConfiguration` options:** `paginationPolicy.minimumItemCount`, `secureData.properties: ["inputs","outputs"]`, `staticResult`. https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-workflow-actions-triggers
  - Chunking is an action "content transfer" setting that raises the message cap from 100 MB to 1 GB. https://learn.microsoft.com/en-us/power-automate/limits-and-config#message-size
  - **[UNVERIFIED]** The JSON key is probably `runtimeConfiguration.contentTransfer.transferMode: "Chunked"`.
- **`retryPolicy`:** it goes **inside the action's `inputs`** as `{type: default|none|fixed|exponential, interval, count, minimumInterval, maximumInterval}`. If it's absent, the `default` policy applies. https://learn.microsoft.com/en-us/azure/logic-apps/error-exception-handling
  - It applies to 408, 429 and 5xx responses and to connectivity exceptions. https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-workflow-actions-triggers
  - Power Automate defaults: Low = 2 retries (about 5→10 min). Medium/High = 12 retries, exponential from 7 s up to about 1 h. Maximum settings: 90 attempts, delay 5 s–1 day. https://learn.microsoft.com/en-us/power-automate/limits-and-config#retry-policy
- **Expression syntax:** `@expr` returns a JSON value, `@{expr}` does string interpolation, `@@` escapes a literal `@`. Use single-quoted strings. `?` is null-safe property access (`triggerBody()?['x']`). https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-workflow-definition-language
- **Trigger inputs are evaluated at save time:** for triggers, expressions like `utcNow()` are calculated when the flow is saved and hardcoded. https://learn.microsoft.com/en-us/troubleshoot/power-platform/power-automate/flow-run-issues/triggers-troubleshoot#triggers-dont-respect-expressions-used-in-them
- **Expression functions most useful for debugging and simplifying** (reference: https://learn.microsoft.com/en-us/azure/logic-apps/expression-functions-reference):
  - `result('<scope>')`: array of first-level action results (status, inputs, outputs, error) of a Scope/Foreach/Until. Doesn't include deeper nested actions.
  - `actions('<name>')`, `outputs('<name>')`, `body('<name>')`, `trigger()`, `triggerBody()`, `triggerOutputs()`.
  - `workflow()`: `run.name`, `tags.environmentName`, `tags.logicAppName`, `tags.flowDisplayName`, `tags.environmentFlowSuspensionReason`, `tags.triggerType`. The Power Automate schema is at https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/error-handling
  - `items('<loop>')`, `item()`, `iterationIndexes('<untilLoop>')`, `variables()`, `parameters()`.
  - `coalesce`, `empty`, `if`, `equals`, `and`, `or`, `not`, `isInt`, `isFloat`.
  - `first`, `last`, `length`, `union`, `intersection`, `take`, `skip`, `slice`, `split`, `join`, `json`, `string`, `int`, `float`, `bool`.
  - `formatDateTime`, `parseDateTime`, `convertTimeZone`, `addDays`, `utcNow`.
  - `setProperty`, `addProperty`, `removeProperty`, `xpath`.
  - **[OPEN]** Some newer Logic Apps functions (for example `chunk`, `sort`, `reverse`, `dateDifference`) may not all be available in the Power Automate designer. Verify before recommending them.
- **Try/catch pattern:**
  - Put the work in a Try scope, add a Catch scope with `runAfter: {Try: ["Failed","TimedOut"]}`, then Filter array over `@result('Try')` where `status == 'Failed'`.
  - A Finally scope runs after Catch with all statuses. **[INFERENCE: standard composition of the runAfter semantics]**
  - The run URL is `https://make.powerautomate.com/environments/{env}/flows/{logicAppName}/runs/{run.name}` (built from `workflow()`).
  - Sources: https://learn.microsoft.com/en-us/azure/logic-apps/error-exception-handling and https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/error-handling

---

## 4. Best practices and limits for simple, efficient flows

### 4.1 Limits the analyzer should check against (https://learn.microsoft.com/en-us/power-automate/limits-and-config)
- **Duration:**
  - Run duration 30 days (includes pending approvals). Outbound sync request 120 s. Async up to 30 days. Inbound request 120 s. Recurrence interval 60 s–500 days.
  - Child flows must respond within 120 s, or use an asynchronous response (202 + Location). https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/asychronous-flow-pattern
- **Loops:**
  - Apply to each items: 5,000 (Low) / 100,000 (others).
  - Apply to each concurrency: default 1, range 1–50.
  - Until: default 60, max 5,000.
  - Pagination: 5,000 (Low) / 100,000.
  - Split on: 5,000 / 100,000, or 100 with trigger concurrency.
- **Trigger concurrency:** off by default. When on, 1–100 runs (default 25), and waiting runs = 10 + degree of parallelism. Turning it on "can't be undone without deleting and re-adding the trigger".
- **Messages and expressions:** message 100 MB (1 GB chunked). Expression evaluation 131,072 chars. URL 16,384 chars.
- **Throughput:** 100,000 requests/5 min. Content throughput 120 MB (Low) / 1.2 GB per 5 min. Concurrent outbound calls 500 (Low) / 2,500.
- **Power Platform requests per 24 h** (https://learn.microsoft.com/en-us/power-platform/admin/api-request-limits-allocations#request-limits-in-power-automate):

  | Plan | Official limit | Transition-period limit (currently enforced) |
  |---|---|---|
  | Premium | 40k per user | 200k per flow |
  | Process / per-flow | 250k per license | 500k per license |
  | Free / Office 365 | 6k per user | 10k per flow |

  - Every trigger and action counts, including Compose, Initialize variable and Scope. Failed actions count, skipped ones don't. Retries and pagination count. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/understand-limits
  - A flow uses its **owner's** plan. If the owner leaves, the flow drops to the Low profile. https://learn.microsoft.com/en-us/power-automate/limits-and-config#performance-profiles
  - Instant flows use the invoker's limits; automated and scheduled flows use the owner's. https://learn.microsoft.com/en-us/power-platform/admin/api-request-limits-allocations
  - **Doc discrepancy:** https://learn.microsoft.com/en-us/power-automate/error-reference (FlowRunQuotaExceeded) quotes the official per-user numbers (6k/40k/250k). The limits page quotes the transition numbers (10k/200k/500k).
- **Connector-specific limits:**
  - SharePoint: 600 calls/60 s per connection. https://learn.microsoft.com/en-us/connectors/sharepointonline/
  - Custom connectors: 500 requests/min per connection. https://learn.microsoft.com/en-us/power-automate/limits-and-config#custom-connector-limits

### 4.2 Simplification rules (anti-pattern → recommendation, all from Microsoft guidance)
1. **Filter at the source, not in the flow.**
   - Use OData `$filter` / `$top` / `$select` / "Limit columns by view" on Get items / List rows instead of looping with Conditions. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/work-with-relevant-data and https://learn.microsoft.com/en-us/power-automate/error-reference#workflowrunactionrepetitionquotaexceeded
   - SharePoint Get items page size:
     - The SharePoint guidance says the default is 100 items, paginated; Top Count goes up to 5,000; beyond that, enable Pagination. On lists over 5,000 items, a filtered query can return nothing if no match is in the first 5,000 unless Pagination is on. https://learn.microsoft.com/en-us/sharepoint/dev/business-apps/power-automate/guidance/working-with-get-items-and-get-files
     - The connector reference says Top Count "default = all". https://learn.microsoft.com/en-us/connectors/sharepointonline/
     - **Conflicting docs. Always set Top Count and Pagination explicitly.**
2. **Replace loops with data operations.** Filter array, Select, Join, Compose and Parse JSON transform arrays without per-item actions. Prefer `Select`/`Filter array` over Apply to each when only transforming or filtering. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/use-data-operations and https://learn.microsoft.com/en-us/power-automate/error-reference
3. **Avoid nested Apply to each.**
   - Iterations multiply. Replace the inner loop with OData `$expand` on the parent query. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/avoid-anti-patterns
   - Inner loops always run sequentially; concurrency applies only at the top level. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/implement-parallel-execution
4. **Bulk and batch instead of per-record loops.** Use SharePoint `$batch`, Dataverse `CreateMultiple`/`UpdateMultiple` (one request), or Apply to each with concurrency up to 50 when batching isn't possible. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/avoid-anti-patterns
5. **Large ETL belongs in Dataflows,** with the flow orchestrating the refresh. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/avoid-anti-patterns
6. **Trigger conditions and filters stop unnecessary runs.** Use trigger conditions or OData filters and filtering attributes on Dataverse triggers. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/optimize-power-automate-triggers
7. **Prevent self-trigger infinite loops** with trigger conditions or Terminate. The designer warns about possible infinite trigger loops. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/avoid-anti-patterns
8. **Variables:**
   - Prefer `Compose` for values that don't change. Use one JSON object variable instead of many scalar variables (fewer Initialize/Set actions). https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/use-data-operations
   - Increment/Decrement/Append to variable in **parallel** loops give unpredictable results. Run the loop sequentially or avoid shared variables. https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-control-flow-loops
9. **Concurrency:**
   - Parallel branches suit independent steps that take more than 5 s. Minimize skipped actions (for example, Switch branches with many actions; call child flows instead). https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/implement-parallel-execution
   - Leave trigger concurrency at its default (off) unless needed, because it's irreversible. If you do need it, isolate it in a child flow. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/optimize-power-automate-triggers
10. **Error handling:**
    - Use Try/Catch scopes with runAfter Failed/TimedOut, `result()` + Filter array, and Terminate with status and message. Use exponential retry policies. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/error-handling
    - Don't over-log: "excessive custom logging… can lead to an anti-pattern". Prefer Application Insights. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/error-handling
    - Don't overuse scopes. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/create-scopes
11. **Child flows:**
    - Modularize large flows (more than 500 actions, or depth beyond 8). The parent and children must be in the same solution. A child flow needs the "Manually trigger a flow" trigger and embedded connections (run-only users set to "Use this connection").
    - The parent waits for the child for up to 30 days, or 1 year for built-in/Dataverse-only flows.
    - Sources: https://learn.microsoft.com/en-us/power-automate/create-child-flows and https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/create-reusable-code
    - A Process license doesn't extend to child flows unless they're in the same flow group. https://learn.microsoft.com/en-us/power-platform/admin/api-request-limits-allocations
12. **Approvals and long waits:**
    - Set explicit expirations and timeout branches (`runAfter` "has timed out"). Split waits longer than 30 days into multiple runs ("relay" pattern). https://learn.microsoft.com/en-us/power-automate/error-reference#operationtimedout
    - Don't wrap approvals in Do until; use Condition or Switch on the final states. https://learn.microsoft.com/en-us/power-automate/approvals-known-issues
13. **Security:**
    - Secure inputs/outputs (`runtimeConfiguration.secureData`) hide values in run history. https://learn.microsoft.com/en-us/power-automate/how-tos-use-sensitive-input and https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/use-secure-inputs-outputs-triggers
    - Don't hardcode secrets; use Key Vault or environment variables. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/use-secure-inputs-outputs-triggers
    - Secure HTTP-request triggers with Entra ID or an IP firewall. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/use-secure-inputs-outputs-triggers
14. **Naming and documentation:** use descriptive action names (they become the JSON keys used in `runAfter` and expressions), a consistent case and prefixes, and notes on actions. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/use-consistent-naming-conventions
15. **Idempotency:** design for duplicate executions (at-least-once). https://learn.microsoft.com/en-us/troubleshoot/power-platform/power-automate/flow-run-issues/triggers-troubleshoot#flow-or-actions-run-multiple-times
16. **Tooling:**
    - Flow Checker (design time). https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/manage-flows-flow-checker
    - Power CAT Toolkit code review. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/
    - Process mining "Improve your flow" and flow Analytics (Actions tab = request consumption). https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/monitoring-and-alerting
    - Expression cookbook for null-safe patterns. https://learn.microsoft.com/en-us/power-automate/expression-cookbook
17. **Solution-aware flows for ALM:** connection references, environment variables, versioning, Dataverse run history, and service principal owners in production. https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/understand-benefits-solution-aware-flows

---

## 5. Export / import for offline analysis
- **Solution export** [OFFICIAL]:
  - `POST [Org]/api/data/v9.2/ExportSolution {"SolutionName": "...", "Managed": false}` returns `ExportSolutionFile` (a base64 zip). https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code#export-flows
  - Import uses `ImportSolution` with `OverwriteUnmanagedCustomizations`, `CustomizationFile`. https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code#import-flows
  - Inside the zip, flows live in the **`Workflows/`** folder, one JSON file per flow. They have been multi-line formatted JSON since February 2022. https://learn.microsoft.com/en-us/power-automate/export-flow-solution
  - Only published components are exported. Managed solutions can't be exported. Solution flows can't be exported from the flow details page. https://learn.microsoft.com/en-us/power-automate/export-flow-solution
- **Direct read without export:** `GET workflows({id})?$select=clientdata`, then JSON-parse the string twice (the string contains JSON). https://learn.microsoft.com/en-us/power-automate/manage-flows-with-code
- **Non-solution flows:**
  - Portal "Export → Package (.zip)" (legacy), owner or co-owner only. Needs third-party cookies. Package zips can't be used as Dataverse solution packages. https://learn.microsoft.com/en-us/power-automate/export-import-flow-non-solution
  - **[UNDOCUMENTED]** Package internal layout (the definition.json path) is not documented.
- **Connector route:** "Get Flow as Admin" with `includeFlowDefinition=true` returns the definition without the unsupported API. https://learn.microsoft.com/en-us/connectors/flowmanagement/
- **Documented JSON-edit workaround:** to remove SharePoint trigger concurrency, "export the flow and edit the JSON file to remove the 'concurrency control' element". https://learn.microsoft.com/en-us/connectors/sharepointonline/

---

## 6. Open questions / not verified
1. **Why the Stopped flow's runs were empty.** Most likely no runs in the last ~28–30 days (see §0). Confirm by checking the flow's `lastModifiedTime` and trigger type. Also try:
   - the admin-scoped route `…/scopes/admin/environments/{env}/flows/{id}/runs`
   - `…/triggers/{triggerName}/histories`
   - Dataverse `flowruns?$filter=workflowid eq '<id>'` (solution flows)
   - Power Platform API `flowRuns`
2. **Exact api.flow routes and params** for actions, repetitions, trigger histories, resubmit and cancel under `Microsoft.ProcessSimple`. They're not documented and are inferred from Logic Apps. Also unknown: whether `$filter=Status eq 'Failed'` and `nextLink` paging behave the same.
3. **Power Platform API `flowRuns` response schema, paging, and date filters.** Not published. Check whether it is backed by the Dataverse FlowRun table (so solution flows only).
4. **ID mapping.** How the api.flow flow `name` GUID maps to Dataverse `workflowid` / `resourceid` / `workflowidunique` for solution flows. The Power Platform API exposes both `workflowId` and `resourceId` filters.
5. **Drafts.** Whether api.flow `$expand=properties.definition` returns the published or the latest-draft definition for solution flows with unpublished drafts.
6. **Suspension properties.** Semantics of `workflow.suspensionreasondetails` and the api.flow suspension properties (for example `flowSuspensionReason`/`flowSuspensionTime`). Not documented.
7. **inputsLink/outputsLink.** SAS validity window, and behavior when Secure inputs/outputs are on (whether the link is omitted or its content redacted). Not confirmed for Power Automate.
8. **`clientdataiscompressed`.** Whether it can be true for cloud flows and how to decode it.
9. **Auth.** Whether Azure CLI's first-party client can obtain tokens for `https://api.powerplatform.com` and for Dataverse org URIs without an app registration (Microsoft documents `Get-AzAccessToken` for PP API).
10. **Retention.** 28-day vs 30-day run retention (the docs disagree). SharePoint Get items default page size (100 vs "all"). "Flows in solutions by default" default state (the docs disagree).
11. **Function availability.** Which newer Logic Apps expression functions (`chunk`, `sort`, `reverse`, `dateDifference`, …) Power Automate supports.
12. **Maker `Get-FlowRun`.** The cmdlet exists in module source, but its Learn reference page returned 404.
