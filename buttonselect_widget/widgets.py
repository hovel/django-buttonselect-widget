# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from itertools import chain

from django.db.models.fields import BLANK_CHOICE_DASH
from django.forms.utils import flatatt
from django.forms.widgets import Select
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe


class ButtonSelect(Select):
    def render(self, name, value, attrs=None, choices=()):
        if self.allow_multiple_selected:
            error_msg = '{0}.render() does not support multi-selection.'
            raise NotImplementedError(error_msg.format(self.__class__.__name__))

        if value is None:
            value = ''

        final_attrs = self.build_attrs(attrs, name=name)
        final_attrs['class'] = final_attrs.get('class', '').replace('form-control', '')
        final_attrs['class'] += ' btn-group button-select-widget'

        input_attrs = {
            'id': final_attrs.pop('id'),
            'name': final_attrs.pop('name'),
            'value': value,
        }

        options = self.render_options(choices, [value])

        js = '''
        <script>
        function buttonClick(evt) {
            evt.preventDefault();
            var btn = this;
            var btnContainer = btn.parentNode;
            btnContainer.querySelector('input[type="hidden"]').value = btn.value;
            [].forEach.call(btnContainer.querySelectorAll('.btn'), function (elem) {
                elem.className = elem.className.replace(/active/, '');
            });
            btn.className += 'active';
        }
        [].forEach.call(document.querySelectorAll('.button-select-widget .btn'), function (elem) {
            if (!elem._hasButtonSelectEvent) {
                elem.addEventListener('click', buttonClick, false);
                elem._hasButtonSelectEvent = true;
            }
        });
        </script>
        '''

        output = [
            format_html('<div{0}>', flatatt(final_attrs)),
            format_html('<input{0} type="hidden">', flatatt(input_attrs)),
            options,
            '</div>',
            js,
        ]

        return mark_safe('\n'.join(output))

    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_text(option_value)

        if option_value in selected_choices:
            active_class = 'active'
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            active_class = ''

        return format_html(
            '<button value="{0}" class="btn btn-default {1}">{2}</button>',
            option_value, active_class, force_text(option_label)
        )

    def render_options(self, choices, selected_choices):
        # Normalize to strings.
        selected_choices = set(force_text(v) for v in selected_choices)

        # When the form is submitted by pressing "enter" key in text field,
        # "click" event is fired for first button in this set and it becomes
        # active. Dummy button is used to prevent this.
        output = ['<button style="display: none"></button>']

        for option_value, option_label in chain(self.choices, choices):
            if [(option_value, option_label)] == BLANK_CHOICE_DASH:
                continue
            output.append(self.render_option(selected_choices, option_value, option_label))

        return '\n'.join(output)
