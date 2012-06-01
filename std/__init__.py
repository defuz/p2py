#!/usr/bin/env python
#-*- coding:utf-8 -*-

from scope import Scope


stdScope = Scope()

import statements, expressions, operators, scalar, functions

stdScope.registerModule(statements)
stdScope.registerModule(expressions)
stdScope.registerModule(operators)
stdScope.registerModule(scalar)
stdScope.registerModule(functions)

