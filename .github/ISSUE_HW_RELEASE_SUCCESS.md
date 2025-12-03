---
title: ✅ AUTOMATED release {{env.NAME}} succeeded
labels: bot, hardware
assignees: {{tools.context.actor}}
---
<!-- name:{{env.NAME}} -->
<!-- sha:{{env.SHA}} -->
<!-- run_id:{{env.RUN_ID}} -->
<!-- url:https://github.com/{{env.REPO}}/actions/runs/{{env.RUN_ID}} -->
<!-- artifact_url:{{env.URL}} -->

Workflow [{{env.RUN_ID}}](https://github.com/{{env.REPO}}/actions/runs/{{env.RUN_ID}}) (based on {{env.SHA}}) succeeded, [hardware.zip]({{env.URL}}) is available.
Please verify its contents and run release publisher by using:
---
/release

Some description of the release...
---
This will create a release draft.
