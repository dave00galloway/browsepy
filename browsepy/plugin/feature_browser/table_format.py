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
        self.scenario_count = suite_summary.scenario_count


class TableFormatSummary(Table):
    urlpath = Col('urlpath')
    scenario_count = Col('scenario_count')
    feature_count = Col('feature_count')
    suite_count = Col('suite_count')
    link = LinkCol(
        'Link', 'flask_link', url_kwargs=dict(id='urlpath'), allow_sort=False)

    def __init__(self, suite_summary=None, **kwargs):
        if suite_summary is None:
            suite_summary = SuiteSummary(**kwargs)
        items = [TableFormatEntry(suite_summary=suite_summary, **kwargs)]
        for summary in suite_summary.suites.values():
            items.append(TableFormatEntry(suite_summary=summary, **kwargs))
        for summary in suite_summary.features.values():
            items.append(TableFormatEntry(suite_summary=summary, **kwargs))
        super().__init__(items)

    # def table_format(self):
    #     pass

    def sort_url(self, col_id, reverse=False):
        pass
