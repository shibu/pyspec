=============
PySpec Report
=============

This document was generated at {{summary.now}} by pyspec {{summary.version}}

.. contents::

Result Summary
==============

Ran: {{summary.ran}}  Failure: {{summary.failure}}  Error: {{summary.error}}

Failure Report
==============

{{summary.message.failure}}


{{for module in modules}}
{{if module.failures}}
{{module.name}}


{{for failure in module.failures}}


{{if failure.contexts}}
{{for context in failure.contexts}}
- {{context}}
{{endfor}}

  - {{failure.spec_name}}
{{else}}
- {{failure.spec_name}}
{{endif}}


    Status::

{{failure.error_message}}

{{endfor}}


{{endif}}
{{endfor}}

Error Report
============

{{summary.message.error}}


{{for module in modules}}
{{if module.errors}}
{{module.name}}


{{for error in module.errors}}


{{if error.contexts}}
{{for context in error.contexts}}
- {{context}}
{{endfor}}

  - {{error.spec_name}}
{{else}}
- {{error.spec_name}}
{{endif}}


    Status::

{{error.error_message}}

{{endfor}}


{{endif}}
{{endfor}}

