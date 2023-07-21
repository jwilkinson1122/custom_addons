# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today  Carlos Eduardo Vercelino - CLVsol
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

import yaml

from functools import reduce
from ast import literal_eval
from datetime import datetime

from odoo import models

_logger = logging.getLogger(__name__)


def secondsToStr(t):

    return "%d:%02d:%02d.%03d" % reduce(lambda ll, b: divmod(ll[0], b) + ll[1:], [(t * 1000,), 1000, 60, 60])


class AbstractProcess(models.AbstractModel):
    _inherit = 'clv.abstract.process'

    def survey_question_answer(
        self, doc, yaml_out_file, xml_out_file, key1, key2, key3, key4,
        question_type, question_code, question_nr, question_answer_sequence
    ):

        global sheet
        global row_nr
        global style_choice

        _question_answer_value_ = doc[key1][key2][key3][key4]['value']
        _question_answer_model_ = doc[key1][key2][key3][key4]['model']
        if question_answer_sequence < 100:
            _question_answer_code_ = question_code + '_0' + str(int(question_answer_sequence / 10))
        else:
            _question_answer_code_ = question_code + '_' + str(int(question_answer_sequence / 10))
        _question_code_ = question_code
        _question_answer_sequence_ = str(question_answer_sequence)

        try:
            _question_id_ = doc[key1][key2][key3][key4]['question_id']
        except KeyError:
            _question_id_ = False
        try:
            _matrix_question_id_ = doc[key1][key2][key3][key4]['matrix_question_id']
        except KeyError:
            _matrix_question_id_ = False

        yaml_out_file.write('            %s:\n' % (_question_answer_code_))
        yaml_out_file.write('                model: %s\n' % (_question_answer_model_))
        yaml_out_file.write('                value: \'%s\'\n' % (_question_answer_value_))
        yaml_out_file.write('                code: \'%s\'\n' % (_question_answer_code_))
        if _question_id_:
            yaml_out_file.write('                question_id: %s\n' % (_question_code_))
        if _matrix_question_id_:
            yaml_out_file.write('                _matrix_question_id_: %s\n' % (_question_code_))
        yaml_out_file.write('                sequence: %s\n' % (_question_answer_sequence_))

        xml_out_file.write('                    <record model="%s" id="%s">\n' %
                           (_question_answer_model_, _question_answer_code_))
        xml_out_file.write('                        <field name="value">%s</field>\n' % (_question_answer_value_))
        xml_out_file.write('                        <field name="code">%s</field>\n' % (_question_answer_code_))
        if _question_id_:
            xml_out_file.write('                        <field name="question_id" ref="%s"/>\n' % (_question_code_))
        if _matrix_question_id_:
            xml_out_file.write('                        <field name="matrix_question_id" ref="%s"/>\n' % (_question_code_))
        xml_out_file.write('                        <field name="sequence" eval="%s"/>\n' % (_question_answer_sequence_))

        xml_out_file.write('                    </record>\n')
        xml_out_file.write('\n')

    def survey_question(
        self, doc, yaml_out_file, xml_out_file, key1, key2, key3,
        survey_code, page_code, page_nr, page_sequence, question_sequence
    ):

        _survey_code_ = survey_code
        if question_sequence < 100:
            _question_code_ = page_code + '_0' + str(int(question_sequence / 10))
            _nr_ = page_nr + '.' + str(int(question_sequence / 10))
        else:
            _question_code_ = page_code + '_' + str(int(question_sequence / 10))
            _nr_ = page_nr + '.' + str(int(question_sequence / 10))

        _question_model_ = doc[key1][key2][key3]['model']
        _question_title_ = doc[key1][key2][key3]['title']
        _question_type_ = doc[key1][key2][key3]['question_type']
        try:
            _question_comments_message_ = doc[key1][key2][key3]['comments_message']
        except KeyError:
            _question_comments_message_ = False
        _is_page_ = doc[key1][key2][key3]['is_page']
        try:
            _question_parameter_ = doc[key1][key2][key3]['parameter']
        except KeyError:
            _question_parameter_ = False
        _question_sequence_ = doc[key1][key2][key3]['sequence']
        _question_sequence_ = str(page_sequence + question_sequence)
        try:
            _question_description_ = doc[key1][key2][key3]['description']
        except KeyError:
            _question_description_ = False
        _question_constr_mandatory_ = doc[key1][key2][key3]['constr_mandatory']
        _question_constr_error_msg_ = doc[key1][key2][key3]['constr_error_msg']

        if _question_type_ == 'char_box' or _question_type_ == 'text_box' or _question_type_ == 'datetime':

            yaml_out_file.write('        %s:\n' % (_question_code_))
            yaml_out_file.write('            model: %s\n' % (_question_model_))
            yaml_out_file.write('            title: \'%s\'\n' % (_question_title_))
            yaml_out_file.write('            is_page: %s\n' % (_is_page_))
            yaml_out_file.write('            code: \'%s\'\n' % (_question_code_))
            if _question_parameter_:
                yaml_out_file.write('            parameter: \'%s\'\n' % (_question_parameter_))
            yaml_out_file.write('            question_type: \'%s\'\n' % (_question_type_))
            yaml_out_file.write('            survey_id: %s\n' % (_survey_code_))
            yaml_out_file.write('            sequence: %s\n' % (_question_sequence_))
            if _question_description_ is not False:
                yaml_out_file.write('            description: \'%s\'\n' % (_question_description_))
            yaml_out_file.write('            constr_mandatory: %s\n' % (_question_constr_mandatory_))
            yaml_out_file.write('            constr_error_msg: \'%s\'\n' % (_question_constr_error_msg_))
            yaml_out_file.write('\n')

            # _question_title_ = '' + str(_nr_) + '. ' + _question_title_

            xml_out_file.write('                <!-- %s -->\n' % (_question_title_))
            xml_out_file.write('                <record model="%s" id="%s">\n' % (_question_model_, _question_code_))
            xml_out_file.write('                    <field name="title">%s</field>\n' % (_question_title_))
            xml_out_file.write('                    <field name="is_page" eval="%s"/>\n' % (_is_page_))
            xml_out_file.write('                    <field name="code">%s</field>\n' % (_question_code_))
            if _question_parameter_:
                xml_out_file.write('                    <field name="parameter">%s</field>\n' % (_question_parameter_))
            xml_out_file.write('                    <field name="question_type">%s</field>\n' % (_question_type_))
            xml_out_file.write('                    <field name="survey_id" ref="%s"/>\n' % (_survey_code_))
            xml_out_file.write('                    <field name="sequence" eval="%s"/>\n' % (_question_sequence_))
            if _question_description_ is not False:
                xml_out_file.write('                    <field name="description">&lt;p&gt;%s&lt;/p&gt;</field>\n' %
                                   (_question_description_))
            xml_out_file.write('                    <field name="constr_mandatory">%s</field>\n' % (_question_constr_mandatory_))
            xml_out_file.write('                    <field name="constr_error_msg">%s</field>\n' % (_question_constr_error_msg_))
            xml_out_file.write('                </record>\n')
            xml_out_file.write('\n')

        if _question_type_ == 'simple_choice':

            _question_column_nb_ = doc[key1][key2][key3]['column_nb']
            _question_comments_allowed_ = str(doc[key1][key2][key3]['comments_allowed'])
            _question_comments_message_ = doc[key1][key2][key3]['comments_message']
            _question_comment_count_as_answer_ = doc[key1][key2][key3]['comment_count_as_answer']

            yaml_out_file.write('        %s:\n' % (_question_code_))
            yaml_out_file.write('            model: %s\n' % (_question_model_))
            yaml_out_file.write('            title: \'%s\'\n' % (_question_title_))
            yaml_out_file.write('            is_page: %s\n' % (_is_page_))
            yaml_out_file.write('            code: \'%s\'\n' % (_question_code_))
            if _question_parameter_:
                yaml_out_file.write('            parameter: \'%s\'\n' % (_question_parameter_))
            yaml_out_file.write('            question_type: \'%s\'\n' % (_question_type_))
            yaml_out_file.write('            survey_id: %s\n' % (_survey_code_))
            yaml_out_file.write('            sequence: %s\n' % (_question_sequence_))
            if _question_description_ is not False:
                yaml_out_file.write('            description: \'%s\'\n' % (_question_description_))
            yaml_out_file.write('            column_nb: %s\n' % (_question_column_nb_))
            yaml_out_file.write('            constr_mandatory: %s\n' % (_question_constr_mandatory_))
            yaml_out_file.write('            constr_error_msg: \'%s\'\n' % (_question_constr_error_msg_))
            yaml_out_file.write('            comments_allowed: %s\n' % (_question_comments_allowed_))
            yaml_out_file.write('            comments_message: \'%s\'\n' % (_question_comments_message_))
            yaml_out_file.write('            comment_count_as_answer: %s\n' % (_question_comment_count_as_answer_))
            yaml_out_file.write('\n')

            # _question_title_ = '' + str(_nr_) + '. ' + _question_title_

            xml_out_file.write('                <!-- %s -->\n' % (_question_title_))
            xml_out_file.write('                <record model="%s" id="%s">\n' % (_question_model_, _question_code_))
            xml_out_file.write('                    <field name="title">%s</field>\n' % (_question_title_))
            xml_out_file.write('                    <field name="is_page" eval="%s"/>\n' % (_is_page_))
            xml_out_file.write('                    <field name="code">%s</field>\n' % (_question_code_))
            if _question_parameter_:
                xml_out_file.write('                    <field name="parameter">%s</field>\n' % (_question_parameter_))
            xml_out_file.write('                    <field name="question_type">%s</field>\n' % (_question_type_))
            xml_out_file.write('                    <field name="survey_id" ref="%s"/>\n' % (_survey_code_))
            xml_out_file.write('                    <field name="sequence" eval="%s"/>\n' % (_question_sequence_))
            if _question_description_ is not False:
                xml_out_file.write('                    <field name="description">&lt;p&gt;%s&lt;/p&gt;</field>\n' %
                                   (_question_description_))
            xml_out_file.write('                    <field name="column_nb">%s</field>\n' % (_question_column_nb_))
            xml_out_file.write('                    <field name="constr_mandatory">%s</field>\n' % (_question_constr_mandatory_))
            xml_out_file.write('                    <field name="constr_error_msg">%s</field>\n' % (_question_constr_error_msg_))
            xml_out_file.write('                    <field name="comments_allowed">%s</field>\n' % (_question_comments_allowed_))
            xml_out_file.write('                    <field name="comments_message">%s</field>\n' % (_question_comments_message_))
            xml_out_file.write('                    <field name="comment_count_as_answer">%s</field>\n' %
                               (_question_comment_count_as_answer_))
            xml_out_file.write('                </record>\n')
            xml_out_file.write('\n')

            question_answer_sequence = 0
            for key4 in sorted(doc[key1][key2][key3].keys()):
                if key3 in key4:
                    _question_answer_model_ = doc[key1][key2][key3][key4]['model']
                    _logger.info(u'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> key4, _question_model_: %s, %s,',
                                 key4, _question_answer_model_)
                    if _question_answer_model_ == 'survey.question.answer':
                        question_answer_sequence += 10
                        self.survey_question_answer(
                            doc, yaml_out_file, xml_out_file, key1, key2, key3, key4, _question_type_, _question_code_, _nr_,
                            question_answer_sequence
                        )
            yaml_out_file.write('\n')

        if _question_type_ == 'multiple_choice':

            _question_column_nb_ = doc[key1][key2][key3]['column_nb']
            _question_comments_allowed_ = str(doc[key1][key2][key3]['comments_allowed'])
            _question_comments_message_ = doc[key1][key2][key3]['comments_message']
            _question_comment_count_as_answer_ = doc[key1][key2][key3]['comment_count_as_answer']

            yaml_out_file.write('        %s:\n' % (_question_code_))
            yaml_out_file.write('            model: %s\n' % (_question_model_))
            yaml_out_file.write('            title: \'%s\'\n' % (_question_title_))
            yaml_out_file.write('            is_page: %s\n' % (_is_page_))
            yaml_out_file.write('            code: \'%s\'\n' % (_question_code_))
            if _question_parameter_:
                yaml_out_file.write('            parameter: \'%s\'\n' % (_question_parameter_))
            yaml_out_file.write('            question_type: \'%s\'\n' % (_question_type_))
            yaml_out_file.write('            survey_id: %s\n' % (_survey_code_))
            yaml_out_file.write('            sequence: %s\n' % (_question_sequence_))
            if _question_description_ is not False:
                yaml_out_file.write('            description: \'%s\'\n' % (_question_description_))
            yaml_out_file.write('            column_nb: %s\n' % (_question_column_nb_))
            yaml_out_file.write('            constr_mandatory: %s\n' % (_question_constr_mandatory_))
            yaml_out_file.write('            constr_error_msg: \'%s\'\n' % (_question_constr_error_msg_))
            yaml_out_file.write('            comments_allowed: %s\n' % (_question_comments_allowed_))
            yaml_out_file.write('            comments_message: \'%s\'\n' % (_question_comments_message_))
            yaml_out_file.write('            comment_count_as_answer: %s\n' % (_question_comment_count_as_answer_))
            yaml_out_file.write('\n')

            # _question_title_ = '' + str(_nr_) + '. ' + _question_title_

            xml_out_file.write('                <!-- %s -->\n' % (_question_title_))
            xml_out_file.write('                <record model="%s" id="%s">\n' % (_question_model_, _question_code_))
            xml_out_file.write('                    <field name="title">%s</field>\n' % (_question_title_))
            xml_out_file.write('                    <field name="is_page" eval="%s"/>\n' % (_is_page_))
            xml_out_file.write('                    <field name="code">%s</field>\n' % (_question_code_))
            if _question_parameter_:
                xml_out_file.write('                    <field name="parameter">%s</field>\n' % (_question_parameter_))
            xml_out_file.write('                    <field name="question_type">%s</field>\n' % (_question_type_))
            xml_out_file.write('                    <field name="survey_id" ref="%s"/>\n' % (_survey_code_))
            xml_out_file.write('                    <field name="sequence" eval="%s"/>\n' % (_question_sequence_))
            if _question_description_ is not False:
                xml_out_file.write('                    <field name="description">&lt;p&gt;%s&lt;/p&gt;</field>\n' %
                                   (_question_description_))
            xml_out_file.write('                    <field name="column_nb">%s</field>\n' % (_question_column_nb_))
            xml_out_file.write('                    <field name="constr_mandatory">%s</field>\n' % (_question_constr_mandatory_))
            xml_out_file.write('                    <field name="constr_error_msg">%s</field>\n' % (_question_constr_error_msg_))
            xml_out_file.write('                    <field name="comments_allowed">%s</field>\n' % (_question_comments_allowed_))
            xml_out_file.write('                    <field name="comments_message">%s</field>\n' % (_question_comments_message_))
            xml_out_file.write('                    <field name="comment_count_as_answer">%s</field>\n' %
                               (_question_comment_count_as_answer_))
            xml_out_file.write('                </record>\n')
            xml_out_file.write('\n')

            question_answer_sequence = 0
            for key4 in sorted(doc[key1][key2][key3].keys()):
                if key3 in key4:
                    _question_answer_model_ = doc[key1][key2][key3][key4]['model']
                    _logger.info(u'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> key4, _question_model_: %s, %s,',
                                 key4, _question_answer_model_)
                    if _question_answer_model_ == 'survey.question.answer':
                        question_answer_sequence += 10
                        self.survey_question_answer(
                            doc, yaml_out_file, xml_out_file, key1, key2, key3, key4, _question_type_, _question_code_, _nr_,
                            question_answer_sequence
                        )
            yaml_out_file.write('\n')

        if _question_type_ == 'matrix':

            _question_matrix_subtype_ = str(doc[key1][key2][key3]['matrix_subtype'])
            _question_column_nb_ = doc[key1][key2][key3]['column_nb']

            yaml_out_file.write('        %s:\n' % (_question_code_))
            yaml_out_file.write('            model: %s\n' % (_question_model_))
            yaml_out_file.write('            title: \'%s\'\n' % (_question_title_))
            yaml_out_file.write('            is_page: %s\n' % (_is_page_))
            yaml_out_file.write('            code: \'%s\'\n' % (_question_code_))
            if _question_parameter_:
                yaml_out_file.write('            parameter: \'%s\'\n' % (_question_parameter_))
            yaml_out_file.write('            question_type: \'%s\'\n' % (_question_type_))
            yaml_out_file.write('            matrix_subtype: \'%s\'\n' % (_question_matrix_subtype_))
            yaml_out_file.write('            survey_id: %s\n' % (_survey_code_))
            yaml_out_file.write('            sequence: %s\n' % (_question_sequence_))
            if _question_description_ is not False:
                yaml_out_file.write('            description: \'%s\'\n' % (_question_description_))
            yaml_out_file.write('            column_nb: %s\n' % (_question_column_nb_))
            yaml_out_file.write('            constr_mandatory: %s\n' % (_question_constr_mandatory_))
            yaml_out_file.write('            constr_error_msg: \'%s\'\n' % (_question_constr_error_msg_))
            yaml_out_file.write('\n')

            # _question_title_ = '' + str(_nr_) + '. ' + _question_title_

            xml_out_file.write('                <!-- %s -->\n' % (_question_title_))
            xml_out_file.write('                <record model="%s" id="%s">\n' % (_question_model_, _question_code_))
            xml_out_file.write('                    <field name="title">%s</field>\n' % (_question_title_))
            xml_out_file.write('                    <field name="is_page" eval="%s"/>\n' % (_is_page_))
            xml_out_file.write('                    <field name="code">%s</field>\n' % (_question_code_))
            if _question_parameter_:
                xml_out_file.write('                    <field name="parameter">%s</field>\n' % (_question_parameter_))
            xml_out_file.write('                    <field name="question_type">%s</field>\n' % (_question_type_))
            xml_out_file.write('                    <field name="matrix_subtype">%s</field>\n' %
                               (_question_matrix_subtype_))
            xml_out_file.write('                    <field name="survey_id" ref="%s"/>\n' % (_survey_code_))
            xml_out_file.write('                    <field name="sequence" eval="%s"/>\n' % (_question_sequence_))
            if _question_description_ is not False:
                xml_out_file.write('                    <field name="description">&lt;p&gt;%s&lt;/p&gt;</field>\n' %
                                   (_question_description_))
            xml_out_file.write('                    <field name="constr_mandatory">%s</field>\n' % (_question_constr_mandatory_))
            xml_out_file.write('                    <field name="constr_error_msg">%s</field>\n' % (_question_constr_error_msg_))
            xml_out_file.write('                </record>\n')
            xml_out_file.write('\n')

            question_answer_sequence = 0

            for key4 in sorted(doc[key1][key2][key3].keys()):
                if key3 in key4:
                    _question_answer_model_ = doc[key1][key2][key3][key4]['model']
                    _logger.info(u'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> key4, _question_model_: %s, %s,',
                                 key4, _question_answer_model_)
                    try:
                        _matrix_question_id_ = doc[key1][key2][key3][key4]['matrix_question_id']
                    except KeyError:
                        _matrix_question_id_ = False

                    if _question_answer_model_ == 'survey.question.answer' and _matrix_question_id_:
                        question_answer_sequence += 10
                        self.survey_question_answer(
                            doc, yaml_out_file, xml_out_file, key1, key2, key3, key4, _question_type_, _question_code_, _nr_,
                            question_answer_sequence
                        )
            yaml_out_file.write('\n')

            for key4 in sorted(doc[key1][key2][key3].keys()):
                if key3 in key4:
                    _question_answer_model_ = doc[key1][key2][key3][key4]['model']
                    _logger.info(u'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> key4, _question_model_: %s, %s,',
                                 key4, _question_answer_model_)
                    try:
                        _question_id_ = doc[key1][key2][key3][key4]['question_id']
                    except KeyError:
                        _question_id_ = False

                    if _question_answer_model_ == 'survey.question.answer' and _question_id_:
                        question_answer_sequence += 10
                        self.survey_question_answer(
                            doc, yaml_out_file, xml_out_file, key1, key2, key3, key4, _question_type_, _question_code_, _nr_,
                            question_answer_sequence
                        )
            yaml_out_file.write('\n')

    def survey_page(self, doc, yaml_out_file, xml_out_file, key1, key2, survey_code, page_sequence):

        # global sheet
        # global row_nr

        # _page_title_ = doc[key1][key2]['title'].encode("utf-8")
        _page_title_ = doc[key1][key2]['title']
        _page_model_ = doc[key1][key2]['model']
        if page_sequence < 100000:
            _page_code_ = survey_code + '_0' + str(int(page_sequence / 10000))
            _nr_ = '' + str(int(page_sequence / 10000))
        else:
            _page_code_ = survey_code + '_' + str(int(page_sequence / 10000))
            _nr_ = str(int(page_sequence / 10000))
        _is_page_ = doc[key1][key2]['is_page']
        try:
            # _page_description_ = doc[key1][key2]['description'].encode("utf-8")
            _page_parameter_ = doc[key1][key2]['page_parameter']
        except KeyError:
            _page_parameter_ = False
        _page_sequence_ = doc[key1][key2]['sequence']
        _page_sequence_ = str(page_sequence)
        try:
            # _page_description_ = doc[key1][key2]['description'].encode("utf-8")
            _page_description_ = doc[key1][key2]['description']
        except KeyError:
            _page_description_ = False
        _survey_code_ = key1

        # yaml_out_file.write('    %s:\n' % (_page_code_))
        # yaml_out_file.write('        model: %s\n' % (_page_model_))
        # yaml_out_file.write('        title: \'%s\'\n' % (_page_title_))
        # yaml_out_file.write('        page_description: \'%s\'\n' % (_page_description_))
        # yaml_out_file.write('\n')

        yaml_out_file.write('    %s:\n' % (_page_code_))
        yaml_out_file.write('        model: %s\n' % (_page_model_))
        yaml_out_file.write('        title: \'%s\'\n' % (_page_title_))
        yaml_out_file.write('        is_page: %s\n' % (_is_page_))
        yaml_out_file.write('        code: \'%s\'\n' % (_page_code_))
        yaml_out_file.write('        parameter: \'%s\'\n' % (_page_parameter_))
        yaml_out_file.write('        survey_id: %s\n' % (_survey_code_))
        yaml_out_file.write('        sequence: %s\n' % (_page_sequence_))
        if _page_description_ is not False:
            yaml_out_file.write('        description: \'%s\'\n' % (_page_description_))
        yaml_out_file.write('\n')

        # # _title_ = '[' + _page_code_ + '] ' + _title_
        # _title_ = '' + _nr_ + '. ' + _title_
        # # _description_ = '[' + _page_code_ + '] ' + _description_

        # # txt_file.write('    %s\n' % (_title_))

        # row = sheet.row(row_nr)
        # row.write(0, '[' + key2 + ']')
        # row.write(3, _title_.decode("utf-8"))
        # row_nr += 1
        # row = sheet.row(row_nr)
        # row.write(0, '[' + key2 + ']')
        # row.write(3, _description_.decode("utf-8"))
        # row_nr += 2

        # xml_out_file.write('            <!-- %s -->\n' % (_page_title_))
        # xml_out_file.write('            <record model="%s" id="%s">\n' % (_page_model_, _page_code_))
        # xml_out_file.write('                <field name="title">%s</field>\n' % (_page_title_))
        # xml_out_file.write('                <field name="survey_code" ref="%s"/>\n' % (_survey_code_))
        # xml_out_file.write('                <field name="sequence" eval="%s"/>\n' % (_sequence_))
        # xml_out_file.write('                <field name="description">&lt;p&gt;%s&lt;/p&gt;</field>\n' % (_page_description_))
        # xml_out_file.write('            </record>' + '\n')
        # xml_out_file.write('\n')

        xml_out_file.write('            <!-- %s -->\n' % (_page_title_))
        xml_out_file.write('            <record model="%s" id="%s">\n' % (_page_model_, _page_code_))
        xml_out_file.write('                <field name="title">%s</field>\n' % (_page_title_))
        xml_out_file.write('                <field name="is_page" eval="%s"/>\n' % (_is_page_))
        xml_out_file.write('                <field name="code">%s</field>\n' % (_page_code_))
        xml_out_file.write('                <field name="parameter">%s</field>\n' % (_page_parameter_))
        xml_out_file.write('                <field name="survey_id" ref="%s"/>\n' % (_survey_code_))
        xml_out_file.write('                <field name="sequence" eval="%s"/>\n' % (_page_sequence_))
        if _page_description_ is not False:
            xml_out_file.write('                <field name="description">&lt;p&gt;%s&lt;/p&gt;</field>\n' %
                               (_page_description_))
        xml_out_file.write('            </record>' + '\n')
        xml_out_file.write('\n')

        question_sequence = 0
        for key3 in sorted(doc[key1][key2].keys()):
            if key2 in key3:
                # try:
                #     _model_ = doc[key1][key2][key3]['model']
                #     print('        ', key3, _model_)
                #     if _model_ == 'survey.question':

                #         question_sequence += 10
                #         survey_question(
                #             doc, yaml_out_file, xml_out_file, txt_file, key1, key2, key3, _page_code_, _nr_, question_sequence
                #         )
                # except Exception, e:
                #     print('(4) >>>>>', e.message, e.args)
                #     PrintException()
                _question_model_ = doc[key1][key2][key3]['model']
                is_page_ = doc[key1][key2][key3]['is_page']
                _logger.info(u'>>>>>>>>>>>>>>>>>>>>>>>>> key3, _question_model_, _is_page_: %s, %s, %s',
                             key3, _question_model_, is_page_)
                if _question_model_ == 'survey.question':

                    question_sequence += 10
                    self.survey_question(
                        doc, yaml_out_file, xml_out_file, key1, key2, key3,
                        _survey_code_, _page_code_, _nr_, page_sequence, question_sequence
                    )

    def _survey(self, doc, yaml_out_file, xml_out_file, key1):

        _survey_title_ = doc[key1]['title']
        _survey_model_ = doc[key1]['model']
        _survey_code_ = key1
        _survey_state_ = doc[key1]['state']
        _survey_users_login_required_ = doc[key1]['users_login_required']
        _survey_attempts_limit_ = doc[key1]['attempts_limit']
        _survey_users_can_go_back_ = doc[key1]['users_can_go_back']
        try:
            _survey_description_ = doc[key1]['description']
        except KeyError:
            _survey_description_ = False
        _survey_questions_layout_ = doc[key1]['questions_layout']
        _survey_progression_mode_ = doc[key1]['progression_mode']
        _survey_is_time_limited_ = doc[key1]['is_time_limited']
        _survey_questions_selection_ = doc[key1]['questions_selection']

        yaml_out_file.write('%s:\n' % (key1))
        yaml_out_file.write('    model: %s\n' % (_survey_model_))
        yaml_out_file.write('    title: \'%s\'\n' % (_survey_title_))
        yaml_out_file.write('    code: \'%s\'\n' % (_survey_code_))
        yaml_out_file.write('    state: \'%s\'\n' % (_survey_state_))
        yaml_out_file.write('    users_login_required: %s\n' % (_survey_users_login_required_))
        yaml_out_file.write('    attempts_limit: %s\n' % (_survey_attempts_limit_))
        yaml_out_file.write('    users_can_go_back: %s\n' % (_survey_users_can_go_back_))
        if _survey_description_:
            yaml_out_file.write('    description: \'%s\'\n' % (_survey_description_))
        yaml_out_file.write('    questions_layout: \'%s\'\n' % (_survey_questions_layout_))
        yaml_out_file.write('    progression_mode: \'%s\'\n' % (_survey_progression_mode_))
        yaml_out_file.write('    is_time_limited: %s\n' % (_survey_is_time_limited_))
        yaml_out_file.write('    questions_selection: \'%s\'\n' % (_survey_questions_selection_))
        yaml_out_file.write('\n')

        xml_out_file.write('        <!-- %s -->\n' % (_survey_title_))
        xml_out_file.write('        <record model="%s" id="%s">\n' % (_survey_model_, _survey_code_))
        xml_out_file.write('            <field name="title">%s</field>\n' % (_survey_title_))
        xml_out_file.write('            <field name="code">%s</field>\n' % (_survey_code_))
        xml_out_file.write('            <field name="state">%s</field>\n' % (_survey_state_))
        xml_out_file.write('            <field name="users_login_required" eval="%s"/>\n' % (_survey_users_login_required_))
        xml_out_file.write('            <field name="attempts_limit" eval="%s"/>\n' % (_survey_attempts_limit_))
        xml_out_file.write('            <field name="users_can_go_back" eval="%s"/>\n' % (_survey_users_can_go_back_))
        if _survey_description_:
            xml_out_file.write('            <field name="description">&lt;p&gt;%s&lt;/p&gt;</field>\n' % (_survey_description_))
        xml_out_file.write('            <field name="questions_layout">%s</field>\n' % (_survey_questions_layout_))
        xml_out_file.write('            <field name="progression_mode">%s</field>\n' % (_survey_progression_mode_))
        xml_out_file.write('            <field name="is_time_limited" eval="%s"/>\n' % (_survey_is_time_limited_))
        xml_out_file.write('            <field name="questions_selection">%s</field>\n' % (_survey_questions_selection_))
        xml_out_file.write('        </record>\n')
        xml_out_file.write('\n')

        page_sequence = 0
        for key2 in sorted(doc[key1].keys()):
            if key1 in key2:
                page_model_ = doc[key1][key2]['model']
                is_page_ = doc[key1][key2]['is_page']
                _logger.info(u'>>>>>>>>>>>>>>>>>>>> key2, page_model, _is_page_: %s, %s, %s', key2, page_model_, is_page_)
                if page_model_ == 'survey.question' and is_page_:
                    page_sequence += 10000
                    self.survey_page(doc, yaml_out_file, xml_out_file, key1, key2, key1, page_sequence)

    def _survey_process_yaml(
        self, yaml_in_filepath, yaml_out_filepath, xml_out_filepath, txt_filepath=False, xls_filepath=False
    ):

        global sheet
        global row_nr

        yaml_in_file = open(yaml_in_filepath, 'r')
        doc = yaml.safe_load(yaml_in_file)

        yaml_out_file = open(yaml_out_filepath, "w")
        xml_out_file = open(xml_out_filepath, "w")

        xml_out_file.write('<?xml version="1.0" encoding="utf-8"?>\n')
        xml_out_file.write('<odoo>\n')
        xml_out_file.write('    <data noupdate="0">\n')
        xml_out_file.write('\n')

        for key1 in sorted(doc.keys()):
            _survey_model_ = doc[key1]['model']
            _logger.info(u'>>>>>>>>>>>>>>> key1, _survey_model_: %s, %s', key1, _survey_model_)
            if _survey_model_ == 'survey.survey':

                self._survey(doc, yaml_out_file, xml_out_file, key1)

        xml_out_file.write('    </data>\n')
        xml_out_file.write('</odoo>\n')

        yaml_in_file.close()
        yaml_out_file.close()
        xml_out_file.close()

    def _do_survey_process_yaml(self, schedule):

        _logger.info(u'%s %s', '>>>>>>>> schedule:', schedule.name)

        schedule.processing_log = 'Executing: "' + '_do_survey_process_yaml' + '"...\n\n'
        schedule.processing_log += '>>>>>>>> schedule:' + schedule.name + '"...\n\n'
        date_last_exec = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        from time import time
        start = time()

        method_args = {}
        if schedule.method_args is not False:
            method_args = literal_eval(schedule.method_args)
        _logger.info(u'%s %s', '>>>>>>>>>> method_args: ', method_args)

        yaml_in_filepath = method_args['yaml_in_filepath']
        _logger.info(u'>>>>>>>>>> yaml_in_filepath: %s', yaml_in_filepath)
        yaml_out_filepath = method_args['yaml_out_filepath']
        _logger.info(u'>>>>>>>>>> yaml_out_filepath: %s', yaml_out_filepath)
        xml_out_filepath = method_args['xml_out_filepath']
        _logger.info(u'>>>>>>>>>> xml_out_filepath: %s', xml_out_filepath)

        self._survey_process_yaml(yaml_in_filepath, yaml_out_filepath, xml_out_filepath)

        _logger.info(u'%s %s', '>>>>>>>> Execution time: ', secondsToStr(time() - start))

        schedule.processing_log +=  \
            'date_last_exec: ' + str(date_last_exec) + '\n' + \
            'Execution time: ' + str(secondsToStr(time() - start)) + '\n'
