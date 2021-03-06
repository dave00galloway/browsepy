from flask_table import Table, Col, LinkCol

from browsepy.plugin.feature_browser import SuiteSummary


class TableFormatEntry(object):
    def __init__(self, suite_summary=None, **kwargs):
        if suite_summary is None:
            suite_summary = SuiteSummary(**kwargs)
        self.urlpath = suite_summary.urlpath
        try:
            self.suite_count = suite_summary.suite_count
            self.feature_count = suite_summary.feature_count
            self.type = "Suite"
        except AttributeError:
            self.type = "Feature"
            self.feature_count = None
            self.suite_count = None
        self.scenario_count = suite_summary.scenario_count


class TableFormatSummary(Table):
    urlpath = LinkCol('urlpath', 'browser.summarise_directory',
                      url_kwargs=dict(path='urlpath'),
                      allow_sort=True,
                      attr_list=['urlpath'])
    suite_count = Col('suite_count')
    feature_count = Col('feature_count')
    scenario_count = Col('scenario_count')

    def __init__(self, suite_summary=None, **kwargs):
        if suite_summary is None:
            suite_summary = SuiteSummary(**kwargs)
        items = [TableFormatEntry(suite_summary=suite_summary, **kwargs)]
        for summary in suite_summary.suites.values():
            items.append(TableFormatEntry(suite_summary=summary, **kwargs))
        for summary in suite_summary.features.values():
            items.append(TableFormatEntry(suite_summary=summary, **kwargs))
        super().__init__(items)
        self.sort_url(None, reverse=False)

    def sort_url(self, col_id, reverse=False):
        self.items = sorted(self.items, key=lambda x: x.urlpath, reverse=reverse)
