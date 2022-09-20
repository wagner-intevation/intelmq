# SPDX-FileCopyrightText: 2022 Intevation GmbH
#
# SPDX-License-Identifier: AGPL-3.0-or-later

# -*- coding: utf-8 -*-
"""
Tests the example configurations for the modify bot for syntactical correctness by initializing the modify bot with the configuration files
"""

import unittest

from glob import glob
from pkg_resources import resource_filename

import intelmq.lib.test as test
from intelmq.bots.experts.modify.expert import ModifyExpertBot


class TestModifyExpertBot(test.BotTestCase, unittest.TestCase):
    """
    A TestCase for ModifyExpertBot.
    """

    @classmethod
    def set_bot(cls):
        cls.bot_reference = ModifyExpertBot
        examples_path = resource_filename('intelmq',
                                          'bots/experts/modify/examples/')
        cls.examples = glob(f'{examples_path}/*.conf')

    def test_init(self):
        """
        Tests the example configurations for the modify bot for syntactical correctness by initializing the modify bot with the configuration files
        """
        for example in self.examples:
            self.prepare_bot(parameters={'configuration_path': example})

        # clear the input queue so that the automatic check does not raise
        self.input_queue = []


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
