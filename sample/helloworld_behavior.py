# -*- coding: utf_8 -*-

import helloworld     # 製品コードインポート
from pyspec import *  # テストコードインポート

class HelloWorld_Behavior:
    @spec
    def generate_python(self):
        """PythonのHello Worldのテスト."""
        About(helloworld.generate("Python")).should_equal("print 'Hello World!'")

    @spec(expected=KeyError)
    def generate_invalid_language(self):
        """未登録の言語を設定すると、KeyErrorが発生する."""
        helloworld.generate("Ruby")

if __name__ == "__main__":
    run_test()
