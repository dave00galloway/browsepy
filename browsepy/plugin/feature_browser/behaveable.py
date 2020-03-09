import logging
import os

from gherkin.parser import Parser
from gherkin.pickles import compiler
from gherkin.token_scanner import TokenScanner
from werkzeug.utils import cached_property

import browsepy
from browsepy.file import File, Directory

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('plugin/feature_browser/behaveable.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


class GherkinError(Exception):
    pass


class SuiteSummary(object):
    def __init__(self, behaveable_suite=None, feature_summary=None, **kwargs):
        super().__init__(**kwargs)
        if behaveable_suite is None:
            behaveable_suite = BehaveAbleDir()
        if feature_summary is None:
            feature_summary = {behaveable_suite.path: behaveable_suite.summarise(), "": {}}
        self.features = {}
        self.suites = {}
        self.scenario_count = 0
        self.suite_count = 0
        self.feature_count = 0
        for entry in feature_summary:
            if isinstance(feature_summary[entry], FeatureSummary):
                self.features[entry] = feature_summary[entry]
                self.scenario_count += feature_summary[entry].scenario_count
            elif isinstance(feature_summary[entry], dict):
                suite = BehaveAbleDir(file=entry, path=entry, app=None)
                self.suites[entry] = suite
                suite_summary = SuiteSummary(behaveable_suite=suite,
                                             feature_summary=feature_summary[entry], **kwargs)
                self.features.update(suite_summary.features)
                self.suites.update(suite_summary.suites)
                self.scenario_count += suite_summary.scenario_count
        self.feature_count = len(self.features)
        self.suite_count = len(self.suites)


class FeatureSummary(object):
    def __init__(self, behaveable_file=None, **kwargs):
        super().__init__(**kwargs)
        if behaveable_file is None:
            behaveable_file = BehaveAbleFile()
        self.gherkin_document = behaveable_file.gherkin_document
        self.pickles = behaveable_file.pickles
        self.scenario_count = len(self.pickles)


class BehaveAbleFile(File):
    extensions = {
        'feature': 'feature'
    }

    def __init__(self, file=None, path=None, **defaults):
        if file is None:
            file = self
        if path is None:
            path = file.path
        super().__init__(path=path, **defaults)

        self.file = file
        self.path = file.path
        parser = Parser()
        scanner = TokenScanner(self.path)
        # noinspection PyBroadException
        try:
            self.gherkin_document = parser.parse(scanner)
            self.pickles = compiler.compile(self.gherkin_document)
        except Exception as e:
            raise GherkinError("unable to parse / pickle doc {doc}".format(doc=self.path)) from e

    def summarise(self, **kwargs):
        feature_summary = FeatureSummary(behaveable_file=self, **kwargs)
        return feature_summary  # return gherkin_document

    @classmethod
    def from_urlpath(cls, path, app=None, **defaults):
        kls = super().from_urlpath(path, app=app)
        return BehaveAbleFile(file=kls, app=kls.app, **defaults)

    @classmethod
    def extensions_from_mimetypes(cls, mimetypes):
        logger.debug("detecting mimetypes")
        mimetypes = frozenset(mimetypes)

        return {
            ext: mimetype
            for ext, mimetype in cls.extensions.items()
            if mimetype in mimetypes
        }

    @classmethod
    def detect(cls, node, os_sep=os.sep):
        logger.debug("detecting type of {candidate}".format(candidate=node.path))
        return detect_behaveable_mimetype(node.path, os_sep=os_sep)


class BehaveAbleDir(Directory):
    file_class = BehaveAbleFile
    name = ''

    def __init__(self, file=None, path=None, **defaults):
        if file is None:
            file = self
        if path is None:
            path = file.path
        super().__init__(path=path, **defaults)

    @cached_property
    def parent(self):
        return Directory(self.path)

    @classmethod
    def detect(cls, node):
        if node.is_directory:
            for file in node._listdir():
                if BehaveAbleFile.detect(file):
                    return cls.mimetype
                if BehaveAbleDir.detect(file):
                    return cls.mimetype
        return None

    def entries(self, sortkey=None, reverse=None):
        listdir_fnc = super(BehaveAbleDir, self).listdir
        for file in listdir_fnc(sortkey=sortkey, reverse=reverse):
            if BehaveAbleFile.detect(file):
                yield file
            elif BehaveAbleDir.detect(file):
                logger.warning("yielding dir {file} as file?".format(file=file.path))
                yield file

    def _listdir(self, precomputed_stats=(os.name == 'nt')):
        '''
        Iter unsorted entries on this directory.

        :yields: Directory or File instance for each entry in directory
        :ytype: Node
        '''
        for entry in browsepy.file.scandir(self.path, self.app):
            kwargs = {
                'path': entry.path,
                'app': self.app,
                'parent': self,
                'is_excluded': False
            }
            try:
                if precomputed_stats and not entry.is_symlink():
                    kwargs['stats'] = entry.stat()
                if entry.is_dir(follow_symlinks=True):
                    yield self.directory_class(**kwargs)
                else:
                    try:
                        yield self.file_class(**kwargs)
                    except GherkinError as e:
                        if detect_behaveable_mimetype(self.path):
                            raise GherkinError("unable to parse / pickle doc {doc}".format(doc=self.path)) from e
                        continue
            except OSError as e:
                logger.exception(e)

    @classmethod
    def from_urlpath(cls, path, app=None, **defaults):
        kls = super().from_urlpath(path, app=app)
        return BehaveAbleDir(file=kls, app=kls.app, **defaults)

    def summarise(self, **kwargs):
        feature_summary = {}
        for entry in self.entries(**kwargs):
            if self.detect(entry) and not hasattr(entry, 'summarise'):
                # child dirs may not have been inited as Behaveable so that needs to happen now

                entry = BehaveAbleDir(file=self, path=entry.path, **kwargs)
            # behaveable files should already have been inited.
            # any other node should have been filtered out by BehaveAbleDir.detect()
            feature_summary[entry.urlpath] = entry.summarise()
        return feature_summary  # return gherkin_document


def detect_behaveable_mimetype(path, os_sep=os.sep):
    basename = path.rsplit(os_sep)[-1]
    logger.debug("checking {file}".format(file=basename))
    if '.' in basename:
        ext = basename.rsplit('.')[-1]
        return BehaveAbleFile.extensions.get(ext, None)
    return None
