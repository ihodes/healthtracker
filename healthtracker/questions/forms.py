# -*- coding: utf-8 -*-
import flask
from flask.ext.wtf import Form
from wtforms import TextField, HiddenField, IntegerField, BooleanField, validators


class GreaterThan(object):
    """
    Compares the value of two fields the value of self is to be greater than the supplied field.

    :param fieldname:
        The name of the other field to compare to.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated with `%(other_label)s` and `%(other_name)s` to provide a
        more helpful error.
    """
    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise validators.ValidationError(field.gettext(u"Invalid field name '%s'.") % self.fieldname)
        if field.data != '' and field.data < other.data:
            d = {
                'other_label': hasattr(other, 'label') and other.label.text or self.fieldname,
                'other_name': self.fieldname
            }
            if self.message is None:
                self.message = field.gettext(u'Field must be greater than %(other_name)s.')

            raise validators.ValidationError(self.message % d)


class QuestionForm(Form):
    qtype = HiddenField('qtype', default='yesno')
    created_by = HiddenField('created_by')
    name = TextField('name')
    text = TextField('text')
    min_value = IntegerField('min_value', validators=[validators.Optional()], default=0)
    max_value = IntegerField('max_value', validators=[validators.Optional(),
                                                      GreaterThan('min_value')], default=5)
    is_public = BooleanField('is_public', default=True)
    unlimited_number = BooleanField('unlimited_number', default=True)
    
