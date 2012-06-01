#!/usr/bin/env python
#-*- coding:utf-8 -*-

from scope import Scope

import statements, expressions, operators, scalar, functions

syntaxScope = Scope([statements, expressions, operators, scalar])
stdScope = Scope([functions], syntaxScope)

