from dexy.filter import DexyFilter
import json
import re

class MarkdownSections(DexyFilter):
    """
    Base class for filters which divide markdown scripts into code/prose
    sections.
    """

    aliases = ['mdsections']
    _settings = {
            "input-extensions" : [".md"],
            "output-extensions" : [".json"],
            "output" : True,
            "language" : ("Default programming language for code blocks.", "python"),
            "pprint"  : ("Whether to pretty print JSON.", True),
            }


    def process_code(self, source, language, metadata=None):
        return {
                "type" : "source",
                "language" : language,
                "source" : source,
                "metadata" : metadata
                }

    def process_heading(self, level, text, metadata=None):
        return {
                "type" : "heading",
                "level" : level,
                "text" : text,
                "metadata" : metadata
                }

    def process_prose(self, source, metadata=None):
        return {
                "type" : "markdown",
                "text" : source,
                "metadata" : metadata
                }

    def process_sections(self, input_text):
        self.blocks = []

        self.proseblock = []
        self.codeblock = None

        self.language = None
        self.state = "md"

        for line in input_text.splitlines():
             self.dispatch_line(line)

        # Finish trailing proseblock
        self.finish_prose_block()
        return self.blocks

    def dispatch_line(self, line):
        if self.state == "md":
            if line.lstrip().startswith("```"):
                self.finish_prose_block()
                self.new_code_block(line)
            else:
                m = re.match("^(#+)(\s*)(.*)$", line)
                if m:
                    self.finish_prose_block()
                    self.header_block(m)
                else:
                    self.proseblock.append(line)
        elif self.state == "code":
            if line.lstrip().startswith("```"):
                self.finish_code_block()
            else:
                self.codeblock.append(line)

    def finish_code_block(self):
         block = self.process_code(self.codeblock, self.language)
         self.blocks.append(block)
         self.state = "md"

    def header_block(self, match):
         self.finish_prose_block()
         level = len(match.groups()[0])
         block = self.process_heading(level, match.groups()[2])
         self.blocks.append(block)

    def new_code_block(self, line):
        self.state = "code"
        self.codeblock = []

        # Detect lexer, if specified
        match_lexer = re.match("``` *([A-Za-z-]+)", line)
        if match_lexer:
            self.language = match_lexer.groups()[0]
        else:
            self.language = self.setting('language')

    def finish_prose_block(self):
        # save exististing prose block, if any
        if self.proseblock:
            block = self.process_prose(self.proseblock)
            self.blocks.append(block)
            self.proseblock = []

    def process_text(self, input_text):
        blocks = self.process_sections(input_text)

        if self.setting('pprint'):
            return json.dumps(blocks, indent=4, sort_keys=True)
        else:
            return json.dumps(blocks)


class MarkdownJupyter(MarkdownSections):
    """
    Generate a Jupyter (IPython) notebook from markdown with embedded code.
    """
    aliases = ['mdipynb', 'mdjup']
    _settings = {
            "output-extensions" : [".ipynb"],
            "nbformat" : ("Setting to use for IPython nbformat setting", 3),
            "nbformat_minor" : ("Setting to use for IPython nbformat_minor setting.", 0),
            "name" : ("Name of notebook.", None),
            "collapsed" : ("Whether to collapse code blocks by default.", False),
            "python-only" : ("Whether to render only Python code blocks as code cells", False)
            }

    def process_code(self, source, language, metadata=None):
        if self.setting('python-only') and language != "python":
            return self.process_raw(source)

        if language is None:
            raise Exception("no language specified")

        return {
                "cell_type" : "code",
                "collapsed" : self.setting('collapsed'),
                "metadata" : metadata or {},
                "language" : language,
                "input" : source,
                "outputs" : [],
                "prompt_number" : None
                }

    def process_raw(self, source):
        return {
                "cell_type" : "raw",
                "metadata" : {},
                "source" : [
                    "\n".join(source)
                    ]
                }

    def process_heading(self, level, text, metadata = None):
        return {
                "cell_type" : "heading",
                "level" : level,
                "metadata" : metadata or {},
                "source" : [text]
                }

    def process_prose(self, source):
        return {
                "cell_type" : "markdown",
                "metadata" : {},
                "source" : [
                    "\n".join(source)
                    ]
                }

    def process_text(self, input_text):
        workbook_name = self.setting("name")
        cells = self.process_sections(input_text)

        notebook = {
            "nbformat" : self.setting('nbformat'),
            "nbformat_minor" : self.setting('nbformat-minor'),
            "metadata" : {
                "name" : workbook_name
                },
            "worksheets" : [{
                "cells" : cells
                }]
            }

        if self.setting('pprint'):
            return json.dumps(notebook, indent=4, sort_keys=True)
        else:
            return json.dumps(notebook)
