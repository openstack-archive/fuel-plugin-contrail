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
from hamcrest.core.base_matcher import BaseMatcher


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


class BaseSequencesMatcher(BaseMatcher):

    def __init__(self, sequence):
        self.sequence = sequence

    @staticmethod
    def _get_extra_items(sequence, other):
        extra = []
        for item in sequence:
            if item not in other:
                extra.append(item)
        return extra

    def _get_wrong_items(self, item):
        raise NotImplementedError

    def _matches(self, item):
        return not self._get_wrong_items(item)


class IsSubsetOf(BaseSequencesMatcher):

    def _get_wrong_items(self, item):
        return self._get_extra_items(item, self.sequence)

    def describe_to(self, description):
        description.append_text('a subset of ').append_text(self.sequence)

    def describe_mismatch(self, item, mismatch_description):
        super(IsSubsetOf, self).describe_mismatch(item, mismatch_description)
        mismatch_description.append_text(' with unexpected items ') \
            .append_description_of(self._get_wrong_items(item))


class IsSupersetOf(BaseSequencesMatcher):

    def _get_wrong_items(self, item):
        return self._get_extra_items(self.sequence, item)

    def describe_to(self, description):
        description.append_text('a superset of ').append_text(self.sequence)

    def describe_mismatch(self, item, mismatch_description):
        super(IsSupersetOf, self).describe_mismatch(item, mismatch_description)
        mismatch_description.append_text(' without expected items ') \
            .append_description_of(self._get_wrong_items(item))


def is_subset_of(sequence):
    return IsSubsetOf(sequence)


def is_superset_of(sequence):
    return IsSupersetOf(sequence)
