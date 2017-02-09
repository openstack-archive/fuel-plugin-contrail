"""Assertion helpers."""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from hamcrest import assert_that


class ManyAssertionsErrors(AssertionError):
    """Many assertions errors class."""

    def __init__(self, exceptions=None, *args, **kwargs):
        """Constructor."""
        super(ManyAssertionsErrors, self).__init__(*args, **kwargs)
        self._exceptions = exceptions or []

    def __str__(self):
        messages = (str(e) for e in self._exceptions)
        return '\n' + '\n'.join(messages)


class AssertsCollector(object):
    """Assertion class to check many asserts and report all of them later."""

    def __init__(self):
        """Constructor."""
        self._exceptions = []

    def check(self, *args, **kwargs):
        """Perform an assert check and store exception, if it was raised."""
        try:
            assert_that(*args, **kwargs)
        except AssertionError as e:
            self._exceptions.append(e)

    def report(self):
        """Raise ManyAssertionsErrors if there are any exceptions captured."""
        if self._exceptions:
            raise ManyAssertionsErrors(self._exceptions)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return self.report()
