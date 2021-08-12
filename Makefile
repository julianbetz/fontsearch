# -*- coding: utf-8 -*-

# Copyright 2021 Julian Betz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

### Main control of the project.
# ============================================================================


.DEFAULT_GOAL := help


# Self-documentation
# ----------------------------------------------------------------------------

# Prints help messages.
# 
# Document-level documentation blocks are indicated by three hash characters
# at the beginning of lines.  Target documentation strings are indicated by
# two hash characters at the beginning of lines and must comprise only a
# single line right before the target to be documented.  They should be no
# longer than 60 characters; the targets themselves should be no longer than
# 19 characters.
# 
# A document-level documentation block at the end of the file results in no
# vertical spacing between this block and the command list.

### The following subcommands can be used by typing "make SUBCOMMAND":

.PHONY: help
## Print this message and exit.
help:
	@sed -e '/^###\($$\|[^#]\)/,/^$$\|^[^#]\|^#[^#]\|^##[^#]/!d' $(MAKEFILE_LIST) | sed 's/^\($$\|[^#].*$$\|#[^#].*$$\|##[^#].*$$\)//' | sed 's/^### *//' | sed 's/  / /'
	@grep -E '^##[^#]' -A 1 $(MAKEFILE_LIST) | sed 's/^\([^ #][^ ]*\):\($$\| .*$$\)/\1/' | awk 'BEGIN {RS = "\n--\n"; FS = "\n"}; {sub(/^## */, "", $$1); printf "\033[32m%-19s\033[0m %s\n", $$2, $$1}'


# Virtualenvs
# ----------------------------------------------------------------------------

requirements.txt:
	@touch requirements.txt

virtualenvs/py3:
	@virtualenv virtualenvs/py3 --python=python3.8
	@touch virtualenvs/py3/bin/activate
	@touch virtualenvs/py3

virtualenvs/py3/bin/activate: virtualenvs/py3 requirements.txt
	@. virtualenvs/py3/bin/activate && pip install -r requirements.txt
	@touch virtualenvs/py3/bin/activate

## Make virtual environments meet requirements.
virtualenvs: virtualenvs/py3/bin/activate
	@touch virtualenvs

# Due to a Ubuntu 18.04 bug, the invalid package pkg-resources is reported
# during a pip freeze.  This is patched here for convenience.

.PHONY: freeze
## Document all required Python packages in requirements.txt.
freeze: virtualenvs
	@. virtualenvs/py3/bin/activate && pip freeze | ( grep -v "^pkg-resources==" > requirements.txt; [ "$$?" -eq 0 -o "$$?" -eq 1 ] )
	@touch virtualenvs/py3/bin/activate
	@touch virtualenvs
