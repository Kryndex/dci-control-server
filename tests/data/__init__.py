# -*- encoding: utf-8 -*-
#
# Copyright 2015-2016 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

JUNIT = """<testsuite errors="1" failures="1" name="pytest" skipped="1" tests="6" time="4.04239122">
    <testcase classname="classname_1" name="test_1" time="0.02311568802">
        <skipped message="skip message" type="skipped">test skipped</skipped>
    </testcase>
    <testcase classname="classname_1" name="test_2" time="0.91562318802">
        <error message="error message" type="error">test in error</error>
    </testcase>
    <testcase classname="classname_1" name="test_3" time="0.18802915623">
        <failure message="failure message" type="failure">test in failure</failure>
    </testcase>
    <testcase classname="classname_1" name="test_4" time="2.91562318802"/>
    <testcase classname="classname_1" name="test_5" time="3.23423443444">
        <system-out>STDOUT</system-out>
    </testcase>
    <testcase classname="classname_1" name="test_6" time="2.48294832443">
        <system-err>STDERR</system-err>
    </testcase>
</testsuite>
"""  # noqa
