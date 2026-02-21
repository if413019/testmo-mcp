"""Tests for composite recursive tools."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from mcp_testmo.tools.composite import (
    _build_folder_map,
    _build_folder_tree,
    _collect_subtree,
    _get_folder_path,
    get_cases_recursive,
    get_folders_recursive,
    search_cases_recursive,
)


# ---- Test data ----

FLAT_FOLDERS = [
    {"id": 1, "name": "Root A", "parent_id": 0},
    {"id": 2, "name": "Child A1", "parent_id": 1},
    {"id": 3, "name": "Child A2", "parent_id": 1},
    {"id": 4, "name": "Grandchild A1a", "parent_id": 2},
    {"id": 5, "name": "Root B", "parent_id": 0},
    {"id": 6, "name": "Child B1", "parent_id": 5},
]


def make_case(case_id: int, name: str, folder_id: int, **extras: object) -> dict:
    """Create a minimal test case dict."""
    return {"id": case_id, "name": name, "folder_id": folder_id, **extras}


# ---- Helper function tests ----


class TestCollectSubtree:
    def test_single_folder_no_children(self):
        result = _collect_subtree(FLAT_FOLDERS, 5)
        assert result == {5, 6}

    def test_deep_subtree(self):
        result = _collect_subtree(FLAT_FOLDERS, 1)
        assert result == {1, 2, 3, 4}

    def test_leaf_folder(self):
        result = _collect_subtree(FLAT_FOLDERS, 4)
        assert result == {4}

    def test_nonexistent_folder(self):
        result = _collect_subtree(FLAT_FOLDERS, 999)
        assert result == {999}


class TestBuildFolderMap:
    def test_builds_correct_map(self):
        fmap = _build_folder_map(FLAT_FOLDERS)
        assert len(fmap) == 6
        assert fmap[1]["name"] == "Root A"
        assert fmap[4]["name"] == "Grandchild A1a"


class TestGetFolderPath:
    def test_root_folder_path(self):
        fmap = _build_folder_map(FLAT_FOLDERS)
        assert _get_folder_path(1, fmap) == "Root A"

    def test_nested_folder_path(self):
        fmap = _build_folder_map(FLAT_FOLDERS)
        assert _get_folder_path(4, fmap) == "Root A / Child A1 / Grandchild A1a"

    def test_missing_folder(self):
        fmap = _build_folder_map(FLAT_FOLDERS)
        assert _get_folder_path(999, fmap) == ""


class TestBuildFolderTree:
    def test_builds_nested_tree(self):
        fmap = _build_folder_map(FLAT_FOLDERS)
        subtree = _collect_subtree(FLAT_FOLDERS, 1)
        tree = _build_folder_tree(FLAT_FOLDERS, subtree, 1, fmap)

        assert tree is not None
        assert tree["name"] == "Root A"
        assert len(tree["children"]) == 2

        child_names = {c["name"] for c in tree["children"]}
        assert child_names == {"Child A1", "Child A2"}

        # Check grandchild
        child_a1 = next(c for c in tree["children"] if c["name"] == "Child A1")
        assert len(child_a1["children"]) == 1
        assert child_a1["children"][0]["name"] == "Grandchild A1a"

    def test_leaf_folder_tree(self):
        fmap = _build_folder_map(FLAT_FOLDERS)
        subtree = _collect_subtree(FLAT_FOLDERS, 4)
        tree = _build_folder_tree(FLAT_FOLDERS, subtree, 4, fmap)

        assert tree is not None
        assert tree["name"] == "Grandchild A1a"
        assert tree["children"] == []

    def test_missing_root_returns_none(self):
        fmap = _build_folder_map(FLAT_FOLDERS)
        tree = _build_folder_tree(FLAT_FOLDERS, {999}, 999, fmap)
        assert tree is None


# ---- Tool handler tests ----


def _mock_client(folders: list[dict] | None = None) -> MagicMock:
    """Create a mock TestmoClient."""
    client = MagicMock()
    client.RATE_LIMIT_DELAY = 0.0
    client.get_all_folders = AsyncMock(return_value=folders or FLAT_FOLDERS)
    client.get_all_cases = AsyncMock(return_value=[])
    client.search_cases = AsyncMock(return_value={"result": [], "next_page": None})
    return client


class TestGetFoldersRecursive:
    @pytest.mark.asyncio
    async def test_returns_tree(self):
        client = _mock_client()
        result = await get_folders_recursive(
            client, {"project_id": 1, "folder_id": 1}
        )

        assert result["total_folders"] == 4
        assert result["tree"]["name"] == "Root A"
        assert len(result["tree"]["children"]) == 2

    @pytest.mark.asyncio
    async def test_folder_not_found(self):
        client = _mock_client()
        result = await get_folders_recursive(
            client, {"project_id": 1, "folder_id": 999}
        )
        assert "error" in result


class TestGetCasesRecursive:
    @pytest.mark.asyncio
    async def test_collects_cases_from_subtree(self):
        client = _mock_client()

        cases_by_folder = {
            1: [make_case(10, "Case in root", 1)],
            2: [make_case(20, "Case in child", 2)],
            3: [],
            4: [make_case(30, "Case in grandchild", 4)],
        }

        async def mock_get_all_cases(
            project_id: int, folder_id: int | None = None
        ) -> list[dict]:
            return cases_by_folder.get(folder_id, [])

        client.get_all_cases = AsyncMock(side_effect=mock_get_all_cases)

        result = await get_cases_recursive(
            client, {"project_id": 1, "folder_id": 1}
        )

        assert result["total_cases"] == 3
        assert result["total_folders_searched"] == 4
        assert len(result["folder_summary"]) == 3  # 3 folders have cases

        # Check folder annotations
        case_names = [c["name"] for c in result["cases"]]
        assert "Case in root" in case_names
        assert "Case in child" in case_names
        assert "Case in grandchild" in case_names

        for case in result["cases"]:
            assert "_folder_name" in case
            assert "_folder_path" in case

    @pytest.mark.asyncio
    async def test_folder_not_found(self):
        client = _mock_client()
        result = await get_cases_recursive(
            client, {"project_id": 1, "folder_id": 999}
        )
        assert "error" in result

    @pytest.mark.asyncio
    async def test_no_folder_path_when_disabled(self):
        client = _mock_client()
        client.get_all_cases = AsyncMock(
            return_value=[make_case(10, "Case", 1)]
        )

        result = await get_cases_recursive(
            client,
            {"project_id": 1, "folder_id": 1, "include_folder_path": False},
        )
        for case in result["cases"]:
            assert "_folder_name" in case
            assert "_folder_path" not in case


class TestSearchCasesRecursive:
    @pytest.mark.asyncio
    async def test_search_across_subtree(self):
        client = _mock_client()

        call_count = 0

        async def mock_search(
            project_id: int,
            query: str | None = None,
            folder_id: int | None = None,
            tags: list[str] | None = None,
            state_id: int | None = None,
            page: int = 1,
            per_page: int = 100,
        ) -> dict:
            nonlocal call_count
            call_count += 1
            if folder_id == 2:
                return {
                    "result": [make_case(20, "Login Test", 2)],
                    "next_page": None,
                }
            return {"result": [], "next_page": None}

        client.search_cases = AsyncMock(side_effect=mock_search)

        result = await search_cases_recursive(
            client,
            {"project_id": 1, "folder_id": 1, "query": "Login"},
        )

        assert result["total_matches"] == 1
        assert result["cases"][0]["name"] == "Login Test"
        # Should have searched all 4 folders in subtree
        assert call_count == 4

    @pytest.mark.asyncio
    async def test_custom_filters(self):
        client = _mock_client()

        async def mock_search(
            project_id: int,
            query: str | None = None,
            folder_id: int | None = None,
            tags: list[str] | None = None,
            state_id: int | None = None,
            page: int = 1,
            per_page: int = 100,
        ) -> dict:
            return {
                "result": [
                    make_case(1, "High priority", 1, custom_priority=1),
                    make_case(2, "Low priority", 1, custom_priority=3),
                ],
                "next_page": None,
            }

        client.search_cases = AsyncMock(side_effect=mock_search)

        result = await search_cases_recursive(
            client,
            {
                "project_id": 1,
                "folder_id": 4,  # leaf folder, subtree = {4}
                "custom_filters": {"custom_priority": 1},
            },
        )

        assert result["total_matches"] == 1
        assert result["cases"][0]["name"] == "High priority"

    @pytest.mark.asyncio
    async def test_pagination_within_folder(self):
        client = _mock_client()

        page_data = {
            1: {
                "result": [make_case(i, f"Case {i}", 4) for i in range(100)],
                "next_page": 2,
            },
            2: {
                "result": [make_case(100 + i, f"Case {100 + i}", 4) for i in range(50)],
                "next_page": None,
            },
        }

        async def mock_search(
            project_id: int,
            query: str | None = None,
            folder_id: int | None = None,
            tags: list[str] | None = None,
            state_id: int | None = None,
            page: int = 1,
            per_page: int = 100,
        ) -> dict:
            if folder_id == 4:
                return page_data.get(page, {"result": [], "next_page": None})
            return {"result": [], "next_page": None}

        client.search_cases = AsyncMock(side_effect=mock_search)

        result = await search_cases_recursive(
            client,
            {"project_id": 1, "folder_id": 4},  # leaf, subtree = {4}
        )

        assert result["total_matches"] == 150

    @pytest.mark.asyncio
    async def test_folder_not_found(self):
        client = _mock_client()
        result = await search_cases_recursive(
            client, {"project_id": 1, "folder_id": 999}
        )
        assert "error" in result
