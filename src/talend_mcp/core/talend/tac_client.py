"""Client for Talend Administration Center (TAC) MetaServlet API."""

from __future__ import annotations

import base64
import json
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class TacClient:
    """Async client for the TAC MetaServlet API.

    The TAC API is RPC-style: requests are JSON objects Base64-encoded
    and passed as a query parameter to the metaServlet endpoint.
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout_ms: int = 30000,
        vault=None,
    ):
        self.base_url = base_url
        self.timeout_ms = timeout_ms
        self._vault = vault
        self._client: httpx.AsyncClient | None = None

    @property
    def is_available(self) -> bool:
        return self.base_url is not None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout_ms / 1000)
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    def _encode_request(self, payload: dict) -> str:
        """Encode a request payload as Base64 for the metaServlet."""
        json_str = json.dumps(payload)
        return base64.b64encode(json_str.encode("utf-8")).decode("ascii")

    async def _get_credentials(self) -> tuple[str, str]:
        """Get TAC credentials from vault."""
        if self._vault:
            user = await self._vault.get_secret("TAC_AUTH_USER")
            password = await self._vault.get_secret("TAC_AUTH_PASS")
            return user or "", password or ""
        return "", ""

    async def call(self, action: str, params: dict[str, Any] | None = None) -> dict:
        """Make a call to the TAC MetaServlet API.

        Args:
            action: The TAC action name (e.g. "runTask", "getTaskIdByName")
            params: Additional parameters for the action
        """
        if not self.is_available:
            return {"error": "TAC not configured", "available": False}

        user, password = await self._get_credentials()

        payload = {
            "actionName": action,
            "authUser": user,
            "authPass": password,
        }
        if params:
            payload.update(params)

        encoded = self._encode_request(payload)
        url = f"{self.base_url}/metaServlet?{encoded}"

        client = await self._get_client()
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error("TAC API HTTP error: %s", e)
            return {"error": f"HTTP {e.response.status_code}", "detail": str(e)}
        except httpx.RequestError as e:
            logger.error("TAC API request error: %s", e)
            return {"error": "Request failed", "detail": str(e)}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "raw": response.text[:500]}

    async def get_task_id_by_name(self, task_name: str) -> str | None:
        """Get the system task ID for a named task."""
        result = await self.call("getTaskIdByName", {"taskName": task_name})
        if "taskId" in result:
            return result["taskId"]
        return None

    async def run_task(self, task_id: str, context: str | None = None) -> dict:
        """Execute a task by ID."""
        params: dict[str, Any] = {"taskId": task_id, "mode": "asynchronous"}
        if context:
            params["context"] = context
        return await self.call("runTask", params)

    async def list_tasks(self) -> dict:
        """List all tasks defined in TAC."""
        return await self.call("listTasks")

    async def get_task_status(self, task_id: str) -> dict:
        """Get the execution status of a task."""
        return await self.call("getTaskStatus", {"taskId": task_id})

    async def get_task_execution_history(
        self, task_id: str, limit: int = 20
    ) -> dict:
        """Get execution history for a task."""
        return await self.call(
            "getTaskExecutionHistory",
            {"taskId": task_id, "nbLines": str(limit)},
        )
