import logging
import os

from gherkin.parser import Parser
from gherkin.pickles import compiler
from gherkin.token_scanner import TokenScanner

from browsepy.file import File

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('plugin/feature_browser/behaveable.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


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
        self.gherkin_document = parser.parse(scanner)
        self.pickles = compiler.compile(self.gherkin_document)

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


def detect_behaveable_mimetype(path, os_sep=os.sep):
    basename = path.rsplit(os_sep)[-1]
    logger.debug("checking {file}".format(file=basename))
    if '.' in basename:
        ext = basename.rsplit('.')[-1]
        return BehaveAbleFile.extensions.get(ext, None)
    return None
