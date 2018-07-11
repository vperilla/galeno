from trytond.pool import PoolMeta
from trytond.config import config

__all__ = ['Attachment']

max_size = config.getint('galeno', 'max_attachment_size', default=5)


class Attachment(metaclass=PoolMeta):
    __name__ = 'ir.attachment'

    @classmethod
    def __setup__(cls):
        super(Attachment, cls).__setup__()
        cls._error_messages.update({
                'invalid_size': ('Max size for attachments is 5MB, '
                    'your attachment size has %(size)sMB'),
                })

    @classmethod
    def validate(cls, attachments):
        super(Attachment, cls).validate(attachments)
        cls.check_size(attachments)

    @classmethod
    def check_size(cls, attachments):
        for attachment in attachments:
            size = len(attachment.data_size) / (1000 * 1000)
            if size > max_size:
                cls.raise_user_error('invalid_size', {
                    'size': int(size),
                    })
