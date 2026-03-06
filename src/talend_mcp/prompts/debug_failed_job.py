"""debug_failed_job — Structured diagnostic workflow for a failed job."""

from __future__ import annotations

from mcp.types import PromptMessage, TextContent


def register(mcp, services):
    @mcp.prompt()
    async def debug_failed_job(job_name: str, error_message: str = "") -> list[PromptMessage]:
        """Structured workflow to diagnose and fix a failed Talend job.

        Guides the LLM through a systematic debugging process:
        1. Get job definition and understand its structure
        2. Check last execution log
        3. Identify the failing component
        4. Cross-reference with known error patterns
        5. Propose a fix

        Args:
            job_name: Name of the failed job
            error_message: The error message or stack trace (if known)
        """
        error_context = ""
        if error_message:
            error_context = f"""
The reported error is:
```
{error_message}
```
"""

        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""I need to debug a failed Talend job: **{job_name}**
{error_context}
Please follow this diagnostic workflow:

## Step 1: Understand the job
Use `job_get` to retrieve the full job definition for "{job_name}".
Summarize: what does this job do? What are the main components and data flow?

## Step 2: Check the logs
Use the `job://last_log/{job_name}` resource to get the last execution log.
If not available locally, check if TAC has execution history.

## Step 3: Identify the failure point
From the error and logs, identify:
- Which component failed?
- At what stage (input, processing, output)?
- How many rows were processed before failure?

## Step 4: Check known patterns
Review the `errors://known_patterns` resource to see if this is a known error.
If the error matches a pattern, apply the documented fix.

## Step 5: Analyze dependencies
Use `job_dependencies` to check if the failure could be caused by:
- A missing or changed connection
- A modified routine
- A dependency on another job

## Step 6: Propose fix
Based on your analysis, propose a specific fix with:
- What needs to change
- Which component/property to modify
- Any risks or side effects of the change

Remember: In Phase 1, we can only diagnose. Actual modifications require Phase 2 tools.
""",
                ),
            )
        ]
