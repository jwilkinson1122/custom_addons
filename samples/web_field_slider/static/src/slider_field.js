/** @odoo-module **/

import {_t} from '@web/core/l10n/translation';
import {registry} from '@web/core/registry';
import {standardFieldProps} from '@web/views/fields/standard_field_props';
import {Component, useState} from '@odoo/owl';
import {useInputField} from '@web/views/fields/input_field_hook';

export class SliderField extends Component {

    static template = 'web_field_slider.SliderField';
    static props = {
        ...standardFieldProps,
        step: {type: String, optional: true},
        min: {type: String, optional: true},
        max: {type: String, optional: true},
    };
    static defaultProps = {
        step: 1,
        min: 0,
        max: 100,
    };

    setup() {
        useInputField({
            getValue: () => this.value,
            refName: 'input',
        });
        this.state = useState({
            value: this.value,
        })
    }

    get value() {
        return this.props.record.data[this.props.name] || 0;
    }

    eval(expression) {
        return py.eval(expression, this.props.record.evalContext)
    }

}

export const fieldSlider = {
    component: SliderField,
    displayName: _t('Slider'),
    supportedTypes: ['integer', 'float'],
    isEmpty: () => false,
    extractProps: ({attrs, options}) => ({
        step: attrs.step,
        min: attrs.min,
        max: attrs.max,
    }),
}

registry.category('fields').add('slider', fieldSlider);
