# -*- coding: utf-8 -*-

should_equal = {
  'fail':'${variable_name} は ${expected_value} でなければならないが、'
         '${actual_value} だった.',
  'ok':'${variable_name} は ${expected_value} である.'
}

should_not_equal = {
  'fail':'${variable_name} は ${unexpected_value} 以外でなければならない、'
         '${unexpected_value} だった.',
  'ok':"${variable_name} は ${unexpected_value} ではない."
}

should_equal_nearly = {
   'fail':'${variable_name} は ${expected_value} '
          'でなければならないが、${actual_value} だった(許容誤差:${delta}).',
   'ok':'${variable_name} は ${expected_value} である.'
        '(許容誤差: ${delta}).'
}

should_not_equal_nearly = {
   'fail':'${variable_name} は ${expected_value} であってはならないが一致した'
          '(許容誤差:${delta}).',
   'ok':'${variable_name} は ${expected_value} ではない.'
        '(許容誤差: ${delta}).'
}

should_be_true = {
  'fail':'${variable_name} は True でなければならないが、False だった.',
  'ok':'${variable_name} は True である.'
}

should_be_false = {
  'fail':'${variable_name} は False でなければならないが、True だった.',
  'ok':'${variable_name} は False 以外である.'
}

should_be_none = {
  'fail':'${variable_name} は None でなければならないが、None ではなかった.',
  'ok':'${variable_name} は None である.'
}

should_not_be_none = {
  'fail':'${variable_name} は None であってはならないが、None だった.',
  'ok':'${variable_name} は None 以外の値である.'
}

should_be_same = {
  'fail':'${actual_expression} は ${expected_expression} と'
         '同一のオブジェクトでなければならないが、異なっていた.',
  'ok':'${actual_expression} は ${expected_expression} と同一のオブジェクト'
       'である.'
}

should_not_be_same = {
  'fail':'${actual_expression} は ${expected_expression} '
         'と異なるオブジェクトでなければならないが、同一だった',
  'ok':'${actual_expression} は ${expected_expression} と'
       '異なるオブジェクトである.'
}

should_include = {
  'error':'${sequence} は __contains__()メソッドもしくは、__iter__()'
  'のどちらかを持つオブジェクトや配列でなければならない.',
  'fail':'${sequence} は ${expected_value} を含まなければならないが'
  '含んでいなかった.',
  'ok':"${sequence} は ${expected_value} を含む.",
}

should_not_include = {
  'error':'${sequence} は __contains__()メソッドもしくは、__iter__()'
  'のどちらかを持つオブジェクトや配列でなければならない.',
  'fail':'${sequence} は ${expected_value} を含んではならないが, 含んでいた.',
  'ok':"${sequence} は ${expected_value} を含む.",
}

should_be_empty = {
  'error':'${sequence} は __len__()メソッドを持たなければならない',
  'fail':'${sequence} は空でなければならないが、空ではなかった.',
  'ok':'${sequence} は空である.'
}

should_not_be_empty = {
  'error':'${sequence} は __len__()メソッドを持たなければならない',
  'fail':'${sequence} は空であってはならないが、空だった.',
  'ok':'${sequence} は空ではない.'
}

should_be_in = {
  'error':'${sequence} は __contains__()メソッドを持たなければならない',
  'fail':'${actual_value} は ${sequence} に含まれていなければならないが、'
         '含まれていなかった.',
  'ok':"${actual_value} は ${sequence} の中に含まれる.",
}

should_not_be_in = {
  'error':'${sequence} は __contains__()メソッドを持たなければならない',
  'fail':'${actual_value} は ${sequence} に含まれてはならないが、'
         '含まれていた.',
  'ok':"${actual_value} は ${sequence} の中に含まれるない.",
}

should_not_be_changed = {
  'fail':'変数 ${target} の値が ${actual_value} に変更されました. ',
  'ok':'変数 %s の値は変更されていません.',
  'recorded':'レガシーテスト用データとして ${target} が記録されました.'
}

framework = {
  'expected':'${expected_exception} 例外が投げられませんでした.',
  'record_legacy':'レガシーテスト用データが記録されました.',
  'data_porvider_error':'data_providerが作成したキー(=${key})とデータ(=${data})'
                        'の長さが違います.'
}
