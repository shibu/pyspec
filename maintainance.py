import sys, os
sys.path.append(os.path.join(os.path.abspath("."), "sample", "rst2codeplex"))


document_source_list = ["usage-jp", "reference-jp", "legacy_test",
                        "tutorial", "usage", "reference", "dbc",
                        "why_is_pyspec_so_fat"]


def create_html_doc_from_rest():
    if not os.path.exists("htmldoc"):
        os.makedirs("htmldoc")
    from docutils.core import publish_cmdline, default_description

    description = ('Generates (X)HTML documents from standalone reStructuredText '
                   'sources.  ' + default_description)

    for source in document_source_list:
        source_path = "doc/%s.txt" % source
        output_path = "htmldoc/%s.html" % source
        print "generating... ", output_path
        publish_cmdline(writer_name='html', description=description,
                        argv=[source_path, output_path])

def create_codeplex_source_from_rest():
    if not os.path.exists("codeplex"):
        os.makedirs("codeplex")

    from docutils.core import publish_cmdline, default_description
    import rst2codeplex

    description = ("Generates CodePlex's wiki source from standalone "
                   "reStructuredText sources.  " + default_description)

    for source in document_source_list:
        source_path = "doc/%s.txt" % source
        output_path = "codeplex/%s.txt" % source
        print "generating... ", output_path
        publish_cmdline(writer_name='codeplex', description=description,
                        writer=rst2codeplex.Writer(translator=rst2codeplex.CodePlexTranslator),
                        argv=[source_path, output_path, "--traceback"])

def append_change_log():
    import time

    changelog  = """%s  Shibukawa Yoshiki  <yoshiki@shibu.jp>

    \t*%s

    """ % (time.ctime(), " ") + file("ChangeLog.txt").read()

    file("ChangeLog.txt", "w").write(changelog)


def create_pydoc():
    import sys, os
    from epydoc.cli import cli

    for x in "-v -o pyspec_epydoc --name pyspec --graph all --dotpath".split():
        sys.argv.append(x)
    sys.argv.append(r"C:\Program Files\ATT\Graphviz\bin\dot.exe")
    sys.argv.append("pyspec")

    cli()


def trailing_whitespace(path="."):
    for name in os.listdir(path):
        fullpath = os.path.abspath(os.path.join(path, name))
        if os.path.isdir(fullpath):
            trailing_whitespace(fullpath)
        elif os.path.isfile(fullpath):
            ext = os.path.splitext(name)[1]
            if ext in (".py", ".pyw", ".txt", ".html", ".css", ".psproj",
                    ".xrc", ".in") or name=="PKG-INFO":
                trailing_whitespace_of_file(fullpath)


def trailing_whitespace_of_file(path):
    contents = file(path, "rb").read()
    contents = contents.replace("\r\n", "\n")
    result = ["%s\n" % line.replace('\r', '').rstrip() for line in contents.splitlines()]
    output = file(path, "wb")
    output.writelines(result)


def main():
    import sys
    if "pydoc" in sys.argv:
        create_pydoc()
    elif "changelog" in sys.argv:
        append_change_log()
    elif "htmldoc" in sys.argv:
        create_html_doc_from_rest()
    elif "codeplex" in sys.argv:
        create_codeplex_source_from_rest()
    elif "whitespace" in sys.argv:
        trailing_whitespace()
    else:
        print """maintainance tool for pyspec.
- maintainance.py pydoc
    create pydoc document
- maintainance.py changelog
    append change log
- maintainance.py htmldoc
    create html document from reST document
- maintainance.py codeplex
    create codeplex wiki from reST document
- maintainance.py whitespace
    trailing whitespace(for git)
"""


if __name__ == "__main__":
    main()
