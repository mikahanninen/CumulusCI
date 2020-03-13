import pytest
from glob import glob

from cumulusci.tasks.salesforce import BaseSalesforceApiTask
from cumulusci.core.utils import process_list_arg
from cumulusci.core.config import TaskConfig
from cumulusci.core.exceptions import TaskOptionsError


class IntegrationTest(BaseSalesforceApiTask):

    task_docs = """
    Run pytest to test Custom or built-in CumulusCI tasks.

    Pytest files can have the following fixtures injected into them:

        * `project_config` - a cumulusci.core.config.project_config.BaseProjectConfig object
        * `org_config` - a cumulusci.core.config.ScratchOrgConfig.ScratchOrgConfig object
        * `sf` - a simple_salesforce.api.Salesforce object
        * `create_task` - Create and run a task with options

    Look at tests/integration/test_integration_test.py for examples of how to use them.
    """

    task_options = {
        "tests": {
            "description": "A comma-separated list of directories, filenames or globs to test with Pytest and a Salesforce Org",
            "required": False,
        }
    }

    def _init_options(self, kwargs):
        super()._init_options(kwargs)

        # Split and trim tests list
        self.globs = process_list_arg(self.options.get("tests"))
        if not self.globs:
            raise TaskOptionsError("No tests specified.")

        filename_lists = [glob(a_glob, recursive=True) for a_glob in self.globs]

        flat_list = [item for sublist in filename_lists for item in sublist]
        self.files = flat_list

    def _run_task(self):
        if self.files:
            self.logger.info(f"Running tests for {self.globs}")
            return pytest.main(
                args=self.files,
                plugins=[Fixtures(self.sf, self.project_config, self.org_config)],
            )
        else:
            self.logger.info(f"Could not find tests matching {self.globs}")


class Fixtures:
    def __init__(self, sf, project_config, org_config):
        fixture_spec = pytest.fixture(autouse=True, scope="session")
        self.sf = fixture_spec(lambda: sf)
        self.project_config = fixture_spec(lambda: project_config)
        self.org_config = fixture_spec(lambda: org_config)

    @pytest.fixture(autouse=True, scope="session")
    def create_task(self, project_config, org_config):
        default_project_config = project_config
        default_org_config = org_config

        def create_task(task_class, options=None, project_config=None, org_config=None):
            project_config = project_config or default_project_config
            org_config = org_config or default_org_config
            options = options or {}

            task_config = TaskConfig({"options": options})

            return task_class(project_config, task_config, org_config)

        return create_task
