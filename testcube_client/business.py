def run(name, files, **kwargs):
    """One step to save a run with multiple xml files."""
    pass


def start_run(name, team, product, version=None):
    """Will save current run id in config and print out."""
    pass


def finish_run(run_id, files):
    """Follow up step to save run info after starting a run."""
    pass


def get_or_create_team(name):
    pass


def update_team(name, owner):
    pass


def get_or_create_product(name, version=None):
    pass


def add_product(name, version):
    pass


def get_or_create_testcase(name, team, product):
    pass


def update_or_create_result(run_id, result):
    pass
