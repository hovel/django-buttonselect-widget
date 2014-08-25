# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from itertools import chain

from django.db.models.fields import BLANK_CHOICE_DASH
from django.forms.util import flatatt
from django.forms.widgets import Select
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe


class ButtonSelect(Select):
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        if 'class' in final_attrs:
            final_attrs['class'] = final_attrs['class'].replace('form-control', 'btn-group')
        else:
            final_attrs['class'] = 'btn-group'
        final_attrs['class'] += ' button-select-widget'
        input_attrs = {
            'id': final_attrs.pop('id'),
            'name': final_attrs.pop('name'),
            'value': value,
        }
        output = [
            format_html('<input{0} type="hidden">', flatatt(input_attrs)),
            format_html('<div{0}>', flatatt(final_attrs)),
        ]
        options = self.render_options(choices, [value])
        if options:
            output.append(options)
        output.append('</div>')
        js = '''
        <script>
        function buttonClick(evt) {
            evt.preventDefault();
            var btn = this;
            var btnContainer = btn.parentNode;
            var input = btnContainer.parentNode.querySelector('input');
            [].forEach.call(btnContainer.querySelectorAll('.btn'), function (elem) {
                elem.className = elem.className.replace(/active/g, '');
            });
            btn.className += 'active';
            input.value = btn.value;
        }
        [].forEach.call(document.querySelectorAll('.button-select-widget .btn'), function (elem) {
            if (!elem._hasButtonSelectEvent) {
                elem.addEventListener('click', buttonClick, false);
                elem._hasButtonSelectEvent = true;
            }
        });
        </script>
        '''
        output.append(js)
        return mark_safe('\n'.join(output))

    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_text(option_value)
        if option_value in selected_choices:
            selected_html = 'active'
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        return format_html(
            '<button value="{0}" class="btn btn-default {1}">{2}</button>',
            option_value, selected_html, force_text(option_label)
        )

    def render_options(self, choices, selected_choices):
        # Normalize to strings.
        selected_choices = set(force_text(v) for v in selected_choices)
        output = []
        for option_value, option_label in chain(self.choices, choices):
            if [(option_value, option_label, )] == BLANK_CHOICE_DASH:
                continue
            output.append(self.render_option(selected_choices, option_value, option_label))
        return '\n'.join(output)
