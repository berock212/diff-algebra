# encoding: utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from __future__ import unicode_literals

from mo_dots import Data

from mo_hg.hg_mozilla_org import HgMozillaOrg
import re

import json

from mo_logs import constants, Log, startup

import numpy as np
from mo_logs import Log
from numpy import copy

config = None
hg = None

GET_DIFF = "{{location}}/rev/{{rev}}"
GET_FILE = "{{location}}/file/{{rev}}{{path}}"

HUNK_HEADER = re.compile(r"^-(\d+),(\d+) \+(\d+),(\d+) @@.*")
FILE_SEP = re.compile(r"^--- ", re.MULTILINE)
HUNK_SEP = re.compile(r"^@@ ", re.MULTILINE)

MOVE = {
    ' ': np.array([1, 1], dtype=int),
    '\\': np.array([0, 0], dtype=int),  # FOR "\ no newline at end of file"
    '+': np.array([1, 0], dtype=int),
    '-': np.array([0, 1], dtype=int)
}
no_change = MOVE[' ']




class temporal:
    def __init__(self,TID,rev,file,line):
        self.TID = TID
        self.rev = rev
        self.file = file
        self.line = line



def parse_changeset_to_matrix(branch, changeset_id, new_source_code=None):
    """
    :param branch:  Data with `url` parameter pointing to hg instance
    :param changeset_id:
    :param new_source_code:  for testing - provide the resulting file (for file length only)
    :return:
    """
    diff = _get_changeset(branch, changeset_id)
    map = _parse_diff(diff, new_source_code)
    return _map_to_matrix(map)


def parse_diff_to_matrix(diff, new_source_code=None):
    """
    :param diff:  textual diff
    :param new_source_code:  for testing - provide the resulting file (for file length only)
    :return:
    """
    return _map_to_matrix(_parse_diff(diff, new_source_code))


def _map_to_matrix(map):
    output = {}
    for file_path, coord in map.items():
        maxx = np.max(coord, 0)
        matrix = np.zeros(maxx + 1, dtype=np.uint8)
        matrix[zip(*coord)] = 1
        output[file_path] = matrix.T  # OOPS! coordinates were reversed
    return output


def parse_to_map(branch, changeset_id):
    """
    MATRICIES ARE O(n^2), WE NEED A O(n) SOLUTION

    :param branch: OBJECT TO DESCRIBE THE BRANCH TO PULL INFO
    :param changeset_id: THE REVISION NUMEBR OF THE CHANGESET
    :return:  MAP FROM FULL PATH TO OPERATOR
    """

    map = _parse_diff(_get_changeset(branch, changeset_id))
    output = {}
    for file_path, coord in map.items():
        maxx = np.max(coord, 0)
        matrix = np.zeros(maxx + 1, dtype=np.uint8)
        matrix[zip(*coord)] = 1
        output[file_path] = matrix.T
    return output

def _parse_diff(changeset, new_source_code=None):
    output = hg._get_json_diff_from_hg(changeset)
    return output



def main():
    global config
    global hg
    try:
        config = startup.read_settings()
        constants.set(config.constants)
        Log.start(config.debug)
        hg = HgMozillaOrg(config)
        random = _parse_diff(
        Data(changeset={"id": "2d9d0bebb5c6"}, branch={"url": "https://hg.mozilla.org/mozilla-central"}))
    except Exception as e:
        Log.error("Problem with etl", e)

if __name__ == "__main__":
    main()
