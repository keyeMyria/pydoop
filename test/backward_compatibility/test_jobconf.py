# BEGIN_COPYRIGHT
#
# Copyright 2009-2016 CRS4.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# END_COPYRIGHT

import unittest
from pydoop.mapreduce.api import JobConf


class jobconf_tc(unittest.TestCase):
    def test_missing_key(self):
        jc = JobConf(((1, 2), (3, 4)))
        self.assertRaises(RuntimeError, jc.get, 'no_key')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(jobconf_tc('test_missing_key'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run((suite()))
