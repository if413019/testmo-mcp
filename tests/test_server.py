"""Tests for the MCP server."""


from mcp_testmo.server import FIELD_MAPPINGS, TOOLS, format_error, format_result


class TestTools:
    """Tests for tool definitions."""

    def test_tools_defined(self):
        """Test that tools are defined."""
        assert len(TOOLS) > 0

    def test_all_tools_have_names(self):
        """Test that all tools have names."""
        for tool in TOOLS:
            assert tool.name
            assert tool.name.startswith("testmo_")

    def test_all_tools_have_descriptions(self):
        """Test that all tools have descriptions."""
        for tool in TOOLS:
            assert tool.description
            assert len(tool.description) > 10

    def test_all_tools_have_schemas(self):
        """Test that all tools have input schemas."""
        for tool in TOOLS:
            assert tool.inputSchema
            assert tool.inputSchema.get("type") == "object"

    def test_expected_tools_exist(self):
        """Test that expected tools are defined."""
        tool_names = [t.name for t in TOOLS]

        expected = [
            # Projects
            "testmo_list_projects",
            "testmo_get_project",
            # Folders
            "testmo_list_folders",
            "testmo_get_folder",
            "testmo_create_folder",
            "testmo_update_folder",
            "testmo_delete_folder",
            "testmo_find_folder_by_name",
            # Milestones
            "testmo_list_milestones",
            "testmo_get_milestone",
            # Test Cases
            "testmo_list_cases",
            "testmo_get_all_cases",
            "testmo_get_case",
            "testmo_create_case",
            "testmo_create_cases",
            "testmo_batch_create_cases",
            "testmo_update_case",
            "testmo_delete_case",
            "testmo_batch_delete_cases",
            "testmo_search_cases",
            # Test Runs
            "testmo_list_runs",
            "testmo_get_run",
            # Run Results
            "testmo_list_run_results",
            # Attachments
            "testmo_list_case_attachments",
            "testmo_upload_case_attachment",
            "testmo_delete_case_attachments",
            # Automation Sources
            "testmo_list_automation_sources",
            "testmo_get_automation_source",
            # Automation Runs
            "testmo_list_automation_runs",
            "testmo_get_automation_run",
            # Utility
            "testmo_get_field_mappings",
            "testmo_get_web_url",
            # Composite (recursive)
            "testmo_get_folders_recursive",
            "testmo_get_cases_recursive",
            "testmo_search_cases_recursive",
        ]

        for expected_tool in expected:
            assert expected_tool in tool_names, f"Missing tool: {expected_tool}"

    def test_new_tools_count(self):
        """Test that we have all expected new tools."""
        tool_names = [t.name for t in TOOLS]
        # New tools added in this update
        new_tools = [
            "testmo_get_milestone",
            "testmo_list_run_results",
            "testmo_list_case_attachments",
            "testmo_upload_case_attachment",
            "testmo_delete_case_attachments",
            "testmo_list_automation_sources",
            "testmo_get_automation_source",
            "testmo_list_automation_runs",
            "testmo_get_automation_run",
        ]
        for tool in new_tools:
            assert tool in tool_names, f"New tool missing: {tool}"


class TestFieldMappings:
    """Tests for field mappings."""

    def test_mappings_defined(self):
        """Test that field mappings are defined."""
        assert FIELD_MAPPINGS
        assert isinstance(FIELD_MAPPINGS, dict)

    def test_project_mappings(self):
        """Test project ID mappings."""
        assert "project_id" in FIELD_MAPPINGS
        assert FIELD_MAPPINGS["project_id"]["example-project"] == 2
        assert FIELD_MAPPINGS["project_id"]["playground"] == 6

    def test_priority_mappings(self):
        """Test priority mappings."""
        assert "custom_priority" in FIELD_MAPPINGS
        priorities = FIELD_MAPPINGS["custom_priority"]
        assert priorities["Critical"] == 52
        assert priorities["High"] == 1
        assert priorities["Medium"] == 2
        assert priorities["Low"] == 3

    def test_type_mappings(self):
        """Test type mappings."""
        assert "custom_type" in FIELD_MAPPINGS
        types = FIELD_MAPPINGS["custom_type"]
        assert types["Functional"] == 59
        assert types["Acceptance"] == 64
        assert types["Security"] == 55

    def test_configuration_mappings(self):
        """Test configuration (platform) mappings."""
        assert "configurations" in FIELD_MAPPINGS
        configs = FIELD_MAPPINGS["configurations"]
        assert configs["Admin Portal"] == 4
        assert configs["IOS & Android"] == 5
        assert configs["Insti Web"] == 10

    def test_state_mappings(self):
        """Test state ID mappings."""
        assert "state_id" in FIELD_MAPPINGS
        states = FIELD_MAPPINGS["state_id"]
        assert states["Draft"] == 1
        assert states["Active"] == 4

    def test_tag_categories(self):
        """Test tag categories."""
        assert "tags" in FIELD_MAPPINGS
        tags = FIELD_MAPPINGS["tags"]
        assert "domain" in tags
        assert "tier-type" in tags
        assert "scope" in tags
        assert "risk" in tags

    def test_defaults(self):
        """Test default values."""
        assert "defaults" in FIELD_MAPPINGS
        defaults = FIELD_MAPPINGS["defaults"]
        assert defaults["template_id"] == 4
        assert defaults["state_id"] == 1
        assert defaults["custom_creator"] == 51

    def test_result_status_mappings(self):
        """Test result status ID mappings."""
        assert "result_status_id" in FIELD_MAPPINGS
        statuses = FIELD_MAPPINGS["result_status_id"]
        assert statuses["Untested"] == 1
        assert statuses["Passed"] == 2
        assert statuses["Failed"] == 3
        assert statuses["Retest"] == 4
        assert statuses["Blocked"] == 5
        assert statuses["Skipped"] == 6

    def test_automation_run_status_mappings(self):
        """Test automation run status mappings."""
        assert "automation_run_status" in FIELD_MAPPINGS
        statuses = FIELD_MAPPINGS["automation_run_status"]
        assert statuses["Success"] == 2
        assert statuses["Failure"] == 3
        assert statuses["Running"] == 4


class TestFormatters:
    """Tests for response formatters."""

    def test_format_result(self):
        """Test result formatting."""
        data = {"id": 1, "name": "Test"}
        result = format_result(data)
        assert '"id": 1' in result
        assert '"name": "Test"' in result

    def test_format_error_generic(self):
        """Test generic error formatting."""
        error = Exception("Something went wrong")
        result = format_error(error)
        assert '"error": true' in result
        assert "Something went wrong" in result

    def test_format_error_api(self):
        """Test API error formatting."""
        from mcp_testmo.client import TestmoAPIError

        error = TestmoAPIError(404, "Not found", {"detail": "Missing"})
        result = format_error(error)
        assert '"error": true' in result
        assert '"status_code": 404' in result
        assert '"message": "Not found"' in result
