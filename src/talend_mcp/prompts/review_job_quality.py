"""review_job_quality — Best practices checklist for a Talend job."""

from __future__ import annotations

from mcp.types import PromptMessage, TextContent


def register(mcp, services):
    @mcp.prompt()
    async def review_job_quality(job_name: str) -> list[PromptMessage]:
        """Review a Talend job against best practices and quality standards.

        Evaluates naming conventions, error handling, performance patterns,
        logging, and documentation.

        Args:
            job_name: Name of the job to review
        """
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""Please review the Talend job **{job_name}** for quality and best practices.

Use `job_get` to retrieve the job definition, then evaluate against this checklist:

## 1. Naming Conventions
- [ ] Job name follows project naming standard (e.g., prefix_domain_action)
- [ ] Component unique names are descriptive (not just tDBInput_1)
- [ ] Connection labels describe the data flow

## 2. Error Handling
- [ ] Reject flows are connected (not dangling)
- [ ] tDie/tWarn components used for critical error paths
- [ ] tLogCatcher or tStatCatcher present for monitoring
- [ ] Subjob error connections (On Subjob Error) are defined

## 3. Performance
- [ ] tMap lookups use LOAD_ONCE when possible
- [ ] Bulk operations used for large datasets (tDBOutput with batch commit)
- [ ] No unnecessary tSortRow on large datasets (use DB-side ORDER BY)
- [ ] Commit intervals are set appropriately (not 1-by-1)

## 4. Maintainability
- [ ] Context variables used for environment-specific values (not hardcoded)
- [ ] Repository connections used (not inline credentials)
- [ ] Repository schemas used where applicable
- [ ] Job has a description/purpose set in properties

## 5. Logging & Monitoring
- [ ] tLogRow or logging present for key checkpoints
- [ ] Row counts are tracked (tFlowMeter or tStatCatcher)
- [ ] Job execution statistics are available

## 6. Security
- [ ] No hardcoded passwords in component parameters
- [ ] Sensitive data not logged in tLogRow
- [ ] Context variables used for credentials

## 7. Dependencies
Use `job_dependencies` to check:
- [ ] All subjob references are valid
- [ ] All connection references exist
- [ ] No circular dependencies

For each issue found, explain:
- **What**: The specific issue
- **Where**: Which component has the issue
- **Why**: Why it matters
- **Fix**: How to fix it (for Phase 2 implementation)

Rate the overall job quality: Poor / Fair / Good / Excellent
""",
                ),
            )
        ]
