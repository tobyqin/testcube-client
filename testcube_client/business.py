from .settings import API, config


def run(result_xml_pattern, name=None, **kwargs):
    """One step to save a run with multiple xml files."""
    team = kwargs.pop('team')
    product = kwargs.pop('product')
    version = kwargs.pop('version', None)
    start_run(team=team, product=product, version=version, name=name, **kwargs)
    finish_run(config['current_run']['url'], result_xml_pattern)


def start_run(team, product, version=None, name=None, **kwargs):
    """Will save current run id in config and print out."""
    if not name:
        name = 'Tests running on {}'.format(config['host'])

    team = get_or_create_team(team)
    product = get_or_create_product(product, version)



def finish_run(run_url, result_xml_pattern):
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
