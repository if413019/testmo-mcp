"""
Testmo API Client

Async HTTP client for interacting with the Testmo REST API.
Designed for use within the MCP server.
"""

import asyncio
import os
from typing import Any

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TestmoAPIError(Exception):
    """Custom exception for Testmo API errors."""

    def __init__(self, status_code: int, message: str, details: Any = None):
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(f"Testmo API Error {status_code}: {message}")


class TestmoClient:
    """
    Async client for interacting with Testmo REST API.

    Usage:
        async with TestmoClient() as client:
            projects = await client.list_projects()

    Environment Variables:
        TESTMO_URL: Base URL for Testmo instance (e.g., https://nanovest.testmo.net)
        TESTMO_API_KEY: API token for authentication
    """

    MAX_CASES_PER_REQUEST = 100
    REQUEST_TIMEOUT = 30.0
    RATE_LIMIT_DELAY = 0.5

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
    ):
        """
        Initialize the Testmo client.

        Args:
            base_url: Testmo instance URL (default: TESTMO_URL env var)
            api_key: API token (default: TESTMO_API_KEY env var)
        """
        self.base_url = (base_url or os.environ.get("TESTMO_URL", "")).rstrip("/")
        self.api_key = api_key or os.environ.get("TESTMO_API_KEY", "")

        if not self.base_url:
            raise ValueError(
                "TESTMO_URL not set. Set environment variable or pass base_url parameter."
            )
        if not self.api_key:
            raise ValueError(
                "TESTMO_API_KEY not set. Set environment variable or pass api_key parameter."
            )

        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "TestmoClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=f"{self.base_url}/api/v1",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=httpx.Timeout(self.REQUEST_TIMEOUT),
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client, ensuring it's initialized."""
        if self._client is None:
            raise RuntimeError(
                "Client not initialized. Use 'async with TestmoClient() as client:'"
            )
        return self._client

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an API request."""
        try:
            response = await self.client.request(
                method=method,
                url=endpoint,
                json=data,
                params=params,
            )

            if response.status_code == 204:
                return {"success": True}

            if response.status_code >= 400:
                try:
                    error_body = response.json()
                except Exception:
                    error_body = response.text
                raise TestmoAPIError(
                    response.status_code,
                    f"Request failed: {response.reason_phrase}",
                    error_body,
                )

            return response.json()

        except httpx.TimeoutException:
            raise TestmoAPIError(408, "Request timed out")
        except httpx.ConnectError as e:
            raise TestmoAPIError(0, f"Connection error: {e}")

    # =========================================================================
    # Projects
    # =========================================================================

    async def list_projects(self) -> list[dict[str, Any]]:
        """
        List all accessible projects.

        Returns:
            List of project objects with id, name, and other metadata.
        """
        result = await self._request("GET", "/projects")
        return result.get("result", [])

    async def get_project(self, project_id: int) -> dict[str, Any]:
        """
        Get details of a specific project.

        Args:
            project_id: The project ID.

        Returns:
            Project object with full details.
        """
        result = await self._request("GET", f"/projects/{project_id}")
        return result.get("result", result)

    # =========================================================================
    # Folders
    # =========================================================================

    async def list_folders(
        self,
        project_id: int,
        page: int = 1,
        per_page: int = 100,
    ) -> dict[str, Any]:
        """
        List folders in a project (paginated).

        Args:
            project_id: The project ID.
            page: Page number (1-indexed).
            per_page: Number of folders per page (max 100).

        Returns:
            Paginated result with folders and pagination info.
        """
        return await self._request(
            "GET",
            f"/projects/{project_id}/folders",
            params={"page": page, "per_page": per_page},
        )

    async def get_all_folders(self, project_id: int) -> list[dict[str, Any]]:
        """
        Get all folders in a project (handles pagination automatically).

        Args:
            project_id: The project ID.

        Returns:
            List of all folder objects in the project.
        """
        all_folders: list[dict[str, Any]] = []
        page = 1

        while True:
            result = await self.list_folders(project_id, page=page, per_page=100)
            folders = result.get("result", [])
            all_folders.extend(folders)

            if result.get("next_page") is None:
                break
            page += 1
            await asyncio.sleep(self.RATE_LIMIT_DELAY)

        return all_folders

    async def get_folder(self, project_id: int, folder_id: int) -> dict[str, Any]:
        """
        Get details of a specific folder.

        Args:
            project_id: The project ID.
            folder_id: The folder ID.

        Returns:
            Folder object with full details.
        """
        result = await self._request(
            "GET", f"/projects/{project_id}/folders/{folder_id}"
        )
        return result.get("result", result)

    async def create_folder(
        self,
        project_id: int,
        name: str,
        parent_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Create a folder in a project.

        Args:
            project_id: The project ID.
            name: Folder name.
            parent_id: Parent folder ID (None for root level).

        Returns:
            Created folder object.
        """
        data: dict[str, Any] = {"name": name}
        if parent_id:
            data["parent_id"] = parent_id

        result = await self._request(
            "POST", f"/projects/{project_id}/folders", data=data
        )
        return result.get("result", result)

    async def update_folder(
        self,
        project_id: int,
        folder_id: int,
        name: str | None = None,
        parent_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Update a folder.

        Args:
            project_id: The project ID.
            folder_id: The folder ID.
            name: New folder name (optional).
            parent_id: New parent folder ID (optional).

        Returns:
            Updated folder object.
        """
        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if parent_id is not None:
            data["parent_id"] = parent_id

        result = await self._request(
            "PUT", f"/projects/{project_id}/folders/{folder_id}", data=data
        )
        return result.get("result", result)

    async def delete_folder(self, project_id: int, folder_id: int) -> dict[str, Any]:
        """
        Delete a folder.

        Args:
            project_id: The project ID.
            folder_id: The folder ID.

        Returns:
            Success status.
        """
        return await self._request(
            "DELETE", f"/projects/{project_id}/folders/{folder_id}"
        )

    async def find_folder_by_name(
        self,
        project_id: int,
        name: str,
        parent_id: int | None = None,
    ) -> dict[str, Any] | None:
        """
        Find a folder by name at a specific level.

        Args:
            project_id: The project ID.
            name: Folder name to find.
            parent_id: Parent folder ID (None for root level).

        Returns:
            Folder object if found, None otherwise.
        """
        all_folders = await self.get_all_folders(project_id)

        for folder in all_folders:
            folder_parent = folder.get("parent_id") or 0
            search_parent = parent_id or 0

            if folder["name"] == name and folder_parent == search_parent:
                return folder

        return None

    # =========================================================================
    # Milestones
    # =========================================================================

    async def list_milestones(self, project_id: int) -> list[dict[str, Any]]:
        """
        List all milestones in a project.

        Args:
            project_id: The project ID.

        Returns:
            List of milestone objects.
        """
        result = await self._request("GET", f"/projects/{project_id}/milestones")
        return result.get("result", [])

    async def get_milestone(
        self, project_id: int, milestone_id: int
    ) -> dict[str, Any]:
        """
        Get details of a specific milestone.

        Args:
            project_id: The project ID.
            milestone_id: The milestone ID.

        Returns:
            Milestone object with full details.
        """
        result = await self._request(
            "GET", f"/projects/{project_id}/milestones/{milestone_id}"
        )
        return result.get("result", result)

    # =========================================================================
    # Test Cases
    # =========================================================================

    async def list_cases(
        self,
        project_id: int,
        folder_id: int | None = None,
        page: int = 1,
        per_page: int = 100,
    ) -> dict[str, Any]:
        """
        List test cases in a project (paginated).

        Args:
            project_id: The project ID.
            folder_id: Filter by folder (optional).
            page: Page number (1-indexed).
            per_page: Number of cases per page (max 100).

        Returns:
            Paginated result with test cases and pagination info.
        """
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        if folder_id:
            params["folder_id"] = folder_id

        return await self._request(
            "GET", f"/projects/{project_id}/cases", params=params
        )

    async def get_all_cases(
        self,
        project_id: int,
        folder_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get all test cases in a project or folder (handles pagination).

        Args:
            project_id: The project ID.
            folder_id: Filter by folder (optional).

        Returns:
            List of all test case objects.
        """
        all_cases: list[dict[str, Any]] = []
        page = 1

        while True:
            result = await self.list_cases(
                project_id, folder_id=folder_id, page=page, per_page=100
            )
            cases = result.get("result", [])
            all_cases.extend(cases)

            if result.get("next_page") is None:
                break
            page += 1
            await asyncio.sleep(self.RATE_LIMIT_DELAY)

        return all_cases

    async def get_case(self, project_id: int, case_id: int) -> dict[str, Any]:
        """
        Get details of a specific test case.

        Args:
            project_id: The project ID.
            case_id: The test case ID.

        Returns:
            Test case object with full details.
        """
        result = await self._request(
            "GET", f"/projects/{project_id}/cases/{case_id}"
        )
        return result.get("result", result)

    async def create_case(
        self, project_id: int, case_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Create a single test case.

        Args:
            project_id: The project ID.
            case_data: Test case data.

        Returns:
            Created test case object.
        """
        result = await self.create_cases(project_id, [case_data])
        cases = result.get("result", [])
        return cases[0] if cases else result

    async def create_cases(
        self, project_id: int, cases: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Create multiple test cases in a batch.

        Args:
            project_id: The project ID.
            cases: List of test case objects (max 100 per request).

        Returns:
            API response with created cases.

        Raises:
            ValueError: If more than 100 cases are provided.
        """
        if len(cases) > self.MAX_CASES_PER_REQUEST:
            raise ValueError(
                f"Too many cases: {len(cases)}. Max is {self.MAX_CASES_PER_REQUEST}. "
                "Use batch_create_cases for larger batches."
            )

        return await self._request(
            "POST",
            f"/projects/{project_id}/cases",
            data={"cases": cases},
        )

    async def batch_create_cases(
        self, project_id: int, cases: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Create test cases in batches (handles any number of cases).

        Args:
            project_id: The project ID.
            cases: List of test case objects.

        Returns:
            Combined result with all created cases and any errors.
        """
        all_created: list[dict[str, Any]] = []
        errors: list[str] = []

        # Split into batches
        for i in range(0, len(cases), self.MAX_CASES_PER_REQUEST):
            batch = cases[i : i + self.MAX_CASES_PER_REQUEST]
            batch_num = (i // self.MAX_CASES_PER_REQUEST) + 1

            try:
                result = await self.create_cases(project_id, batch)
                created = result.get("result", [])
                all_created.extend(created)
            except TestmoAPIError as e:
                errors.append(f"Batch {batch_num}: {e.message}")

            # Rate limiting between batches
            if i + self.MAX_CASES_PER_REQUEST < len(cases):
                await asyncio.sleep(self.RATE_LIMIT_DELAY)

        return {
            "result": all_created,
            "total_submitted": len(cases),
            "total_created": len(all_created),
            "errors": errors if errors else None,
        }

    async def update_case(
        self, project_id: int, case_id: int, data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Update a test case.

        Args:
            project_id: The project ID.
            case_id: The test case ID.
            data: Fields to update.

        Returns:
            Updated test case object.
        """
        result = await self._request(
            "PUT",
            f"/projects/{project_id}/cases/{case_id}",
            data=data,
        )
        return result.get("result", result)

    async def delete_case(self, project_id: int, case_id: int) -> dict[str, Any]:
        """
        Delete a test case.

        Args:
            project_id: The project ID.
            case_id: The test case ID.

        Returns:
            Success status.
        """
        return await self._request(
            "DELETE", f"/projects/{project_id}/cases/{case_id}"
        )

    async def batch_delete_cases(
        self, project_id: int, case_ids: list[int]
    ) -> dict[str, Any]:
        """
        Delete multiple test cases.

        Args:
            project_id: The project ID.
            case_ids: List of test case IDs to delete.

        Returns:
            Result with success count and any errors.
        """
        deleted: list[int] = []
        errors: list[str] = []

        for case_id in case_ids:
            try:
                await self.delete_case(project_id, case_id)
                deleted.append(case_id)
            except TestmoAPIError as e:
                errors.append(f"Case {case_id}: {e.message}")
            await asyncio.sleep(self.RATE_LIMIT_DELAY)

        return {
            "deleted": deleted,
            "total_deleted": len(deleted),
            "errors": errors if errors else None,
        }

    # =========================================================================
    # Search
    # =========================================================================

    async def search_cases(
        self,
        project_id: int,
        query: str | None = None,
        folder_id: int | None = None,
        tags: list[str] | None = None,
        state_id: int | None = None,
        page: int = 1,
        per_page: int = 100,
    ) -> dict[str, Any]:
        """
        Search for test cases with filters.

        Args:
            project_id: The project ID.
            query: Search query string (searches name and description).
            folder_id: Filter by folder.
            tags: Filter by tags.
            state_id: Filter by state.
            page: Page number.
            per_page: Results per page.

        Returns:
            Paginated search results.
        """
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        if query:
            params["query"] = query
        if folder_id:
            params["folder_id"] = folder_id
        if tags:
            params["tags"] = ",".join(tags)
        if state_id:
            params["state_id"] = state_id

        return await self._request(
            "GET", f"/projects/{project_id}/cases", params=params
        )

    # =========================================================================
    # Test Runs
    # =========================================================================

    async def list_runs(
        self,
        project_id: int,
        page: int = 1,
        per_page: int = 100,
    ) -> dict[str, Any]:
        """
        List test runs in a project.

        Args:
            project_id: The project ID.
            page: Page number.
            per_page: Results per page.

        Returns:
            Paginated list of test runs.
        """
        return await self._request(
            "GET",
            f"/projects/{project_id}/runs",
            params={"page": page, "per_page": per_page},
        )

    async def get_run(self, project_id: int, run_id: int) -> dict[str, Any]:
        """
        Get details of a specific test run.

        Args:
            project_id: The project ID.
            run_id: The test run ID.

        Returns:
            Test run object with full details.
        """
        result = await self._request(
            "GET", f"/projects/{project_id}/runs/{run_id}"
        )
        return result.get("result", result)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_web_url(
        self,
        project_id: int,
        resource_type: str = "repository",
        resource_id: int | None = None,
    ) -> str:
        """
        Generate a web URL for a Testmo resource.

        Args:
            project_id: The project ID.
            resource_type: Type of resource (repository, runs, etc.)
            resource_id: Optional resource ID (folder ID, run ID, etc.)

        Returns:
            URL string for the resource.
        """
        url = f"{self.base_url}/{resource_type}/{project_id}"
        if resource_id:
            url += f"?group_id={resource_id}"
        return url
