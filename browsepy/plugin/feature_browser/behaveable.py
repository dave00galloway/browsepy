import logging
import os

from browsepy.file import File

logger = logging.getLogger(__name__)


class BehaveAbleFile(File):
    extensions = {
        'feature': 'text'
    }

    @classmethod
    def extensions_from_mimetypes(cls, mimetypes):
        logger.info("detecting mimetypes")
        mimetypes = frozenset(mimetypes)
        
        return {
            ext: mimetype
            for ext, mimetype in cls.extensions.items()
            if mimetype in mimetypes
        }

    @classmethod
    def detect(cls, node, os_sep=os.sep):
        logger.info("detecting type of {candidate}".format(candidate=node.path))
        return detect_behaveable_mimetype(node.path, os_sep=os_sep)


def detect_behaveable_mimetype(path, os_sep=os.sep):
    basename = path.rsplit(os_sep)[-1]
    if '.' in basename:
        ext = basename.rsplit('.')[-1]
        return BehaveAbleFile.extensions.get(ext, None)
    return None
