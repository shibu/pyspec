# -*- coding: ascii -*-

should_equal = {
  'fail':'${variable_name} should equal ${expected_value}, '
         'but was ${actual_value}.',
  'ok':'${variable_name} equals ${expected_value}.'
}

should_not_equal = {
  'fail':"${variable_name} should not equal ${unexpected_value}, but equals.",
  'ok':"${variable_name} doesn't not equal ${unexpected_value}."
}

should_equal_nearly = {
   'fail':'${variable_name} should equal ${expected_value}'
          '(within ${delta}), but was ${actual_value}.',
   'ok':'${variable_name} equals ${expected_value}(delta: ${delta}).'
}

should_not_equal_nearly = {
   'fail':'${variable_name} should not equal ${expected_value}'
          '(within ${delta}), but was.',
   'ok':"${variable_name} doesn't not equal ${expected_value}"
        '(delta ${delta}).'
}

should_be_true = {
  'fail':'${variable_name} should be True, but was False.',
  'ok':'${variable_name} is True.'
}

should_be_false = {
  'fail':'${variable_name} should be False, but was True.',
  'ok':'${variable_name} is False.'
}

should_be_none = {
  'fail':'${variable_name} should be None, but was not.',
  'ok':'${variable_name} is None.'
}

should_not_be_none = {
  'fail':'${variable_name} should not be None, but was.',
  'ok':'${variable_name} is not None.'
}

should_be_same = {
  'fail':'${actual_expression} and ${expected_expression} should be same, '
         'but was not.',
  'ok':'${actual_expression} and ${expected_expression} are same object.'
}

should_not_be_same = {
  'fail':'${actual_expression} and ${expected_expression}'
         ' should not be same, but were same',
  'ok':"${actual_expression} and ${expected_expression} aren't same."
}

should_include = {
  'error':'${sequence} should have __contains__ or __iter__ method.',
  'fail':"${sequence} should include ${expected_value}, but didn't.",
  'ok':"${sequence} includes ${expected_value}.",
}

should_not_include = {
  'error':'${sequence} should have __contains__ or __iter__ method.',
  'fail':"${sequence} should not include ${expected_value}, "
         "but includes",
  'ok':"${sequence} doesn't include ${expected_value}.",
}

should_be_empty = {
  'error':'${sequence} should have __len__ method.',
  'fail':'${sequence} should be empty, but was not.',
  'ok':'${sequence} is empty.'
}

should_not_be_empty = {
  'error':'${sequence} should have __len__ method.',
  'fail':'${sequence} should not be empty, but was not.',
  'ok':"${sequence} isn't empty."
}

should_be_in = {
  'error':'${sequence} should have __contains__ method.',
  'fail':"${actual_value} should be in ${sequence}, but wasn't.",
  'ok':"${actual_value} is in ${sequence}.",
}

should_not_be_in = {
  'error':'${sequence} should have __contains__ method.',
  'fail':"${actual_value} should not be in ${sequence}, but was.",
  'ok':"${actual_value} isn't in ${sequence}.",
}

should_not_be_changed = {
  'fail':'${target} should not be changed, '
         'but was changed to ${actual_value}.',
  'ok':'%s is not changed.',
  'recorded':'Test value ${target} was recorded.'
}

framework = {
  'expected':'${expected_exception} must be raised in this spec.',
  'record_legacy':'Legacy test data is recorded.',
  'data_porvider_error':'Key(=${key}) and data(=${data}) '
                        'from data_provider method should be same size'
}
