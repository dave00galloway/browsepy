import logging
import os

from browsepy.file import File

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('plugin/feature_browser/behaveable.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


class BehaveAbleFile(File):
    extensions = {
        'feature': 'feature'
    }

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
