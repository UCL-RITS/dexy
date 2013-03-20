from dexy.common import OrderedDict
from dexy.doc import Doc
from dexy.tests.utils import wrap

REGETRON_INPUT_1 = "hello\n"
REGETRON_INPUT_2 = """\
this is some text
9
nine
this is 100 mixed text and numbers
"""

def test_regetron_filter():
    with wrap() as wrapper:
        node = Doc("example.regex|regetron",
                wrapper,
                [
                    Doc("input1.txt",
                        wrapper,
                        [],
                        contents=REGETRON_INPUT_1),
                    Doc("input2.txt",
                        wrapper,
                        [],
                        contents=REGETRON_INPUT_2)
                    ],
                contents="^[a-z\s]+$"
                )

        wrapper.run(node)

        assert node.output_data()['input1.txt'] == """\
> ^[a-z\s]+$
0000: hello
> 

"""
        assert node.output_data()['input2.txt'] == """\
> ^[a-z\s]+$
0000: this is some text
0002: nine
> 

"""

def test_used_filter():
    with wrap() as wrapper:
        node = Doc("input.txt|used",
                wrapper,
                [
                    Doc("example.sed",
                        wrapper,
                        [],
                        contents="s/e/E/g")
                    ],
                contents="hello")

        wrapper.run(node)
        assert str(node.output_data()) == "hEllo"

def test_sed_filter_single_simple_input_file():
    with wrap() as wrapper:
        node = Doc("example.sed|sed",
                wrapper,
                [
                    Doc("input.txt",
                        wrapper,
                        [],
                        contents="hello")
                    ],
                contents="s/e/E/g")

        wrapper.run(node)
        assert str(node.output_data()) == "hEllo"

def test_sed_filter_single_input_file_with_sections():
    with wrap() as wrapper:
        node = Doc("example.sed|sed",
                wrapper,
                [
                    Doc("input.txt",
                        wrapper,
                        [],
                        contents=OrderedDict([
                            ('foo', 'hello'),
                            ('bar', 'telephone')
                            ]),
                        )
                        ],
                contents="s/e/E/g")

        wrapper.run(node)
        assert node.output_data()['foo'] == 'hEllo'
        assert node.output_data()['bar'] == 'tElEphonE'

def test_sed_filter_multiple_inputs():
    with wrap() as wrapper:
        node = Doc("example.sed|sed",
                wrapper,
                inputs = [
                    Doc("foo.txt",
                        wrapper,
                        [],
                        contents='hello'),
                    Doc("bar.txt",
                        wrapper,
                        [],
                        contents='telephone')
                    ],
                contents="s/e/E/g")

        wrapper.run(node)
        assert node.output_data()['foo.txt'] == 'hEllo'
        assert node.output_data()['bar.txt'] == 'tElEphonE'
