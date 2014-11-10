# To run the tests:
#    1. Install Sublime Text plugin: https://sublime.wbond.net/packages/UnitTesting
#    2. Open the Command Palette and run "UnitTesting: Run any project test suite"
#    3. Enter "SassBeautify"

import sublime, sys, textwrap
from unittest import TestCase

# st2
if sublime.version() < '3000':
   SassBeautifyCommand = sys.modules["SassBeautify"].SassBeautifyCommand;
# st3
else:
   SassBeautifyCommand = sys.modules["SassBeautify.SassBeautify"].SassBeautifyCommand;

SassBeautifyCommandInstance = SassBeautifyCommand(None);


class test_internal_function_restore_end_of_line_comments(TestCase):

    # Check that inline comments starting with ---end-of-line-comment---
    # (which are inserted to "mark" those comments before running sass-convert)
    # are moved back to the previous line and restored to the original comment
    def test_inline_comment(self):
        beautified = SassBeautifyCommandInstance.restore_end_of_line_comments(textwrap.dedent("""\

            h1 {}
            //---end-of-line-comment--- test

            """))

        self.assertEqual(beautified, textwrap.dedent("""\

            h1 {} // test

            """))

    # Check that block comments are moved back and restored as well
    def test_block_comment(self):
        beautified = SassBeautifyCommandInstance.restore_end_of_line_comments(textwrap.dedent("""\

            h1 {}
            /*---end-of-line-comment--- line 1
            line 2 */

            """))

        self.assertEqual(beautified, textwrap.dedent("""\

            h1 {} /* line 1
            line 2 */

            """))


class test_internal_function_beautify_newlines(TestCase):

    # Check that a newline is inserted between two selectors
    def test_insert_newline_1(self):
        beautified = SassBeautifyCommandInstance.beautify_newlines(textwrap.dedent("""\

            .ClassA {
                color: red;
            }
            .ClassB {
                color: blue;
            }

            """))

        self.assertEqual(beautified, textwrap.dedent("""\

            .ClassA {
                color: red;
            }

            .ClassB {
                color: blue;
            }

            """))

    # Check that a property followed by a selector is separated with a newline
    def test_insert_newline_2(self):
        beautified = SassBeautifyCommandInstance.beautify_newlines(textwrap.dedent("""\

            .ClassA {
                color: red;
                .ClassB {
                    color: blue;
                }
            }

            """))

        self.assertEqual(beautified, textwrap.dedent("""\

            .ClassA {
                color: red;

                .ClassB {
                    color: blue;
                }
            }

            """))

    # Check that a propery followed by inline comment and then selector is separated with newline
    def test_insert_newline_3(self):
        beautified = SassBeautifyCommandInstance.beautify_newlines(textwrap.dedent("""\

            .ClassA {
                color: red;
                // This is class b
                .ClassB {
                    color: blue;
                }
            }

            """))

        self.assertEqual(beautified, textwrap.dedent("""\

            .ClassA {
                color: red;

                // This is class b
                .ClassB {
                    color: blue;
                }
            }

            """))

    # Check that propery followed by inline comment and then selector is separated with newline
    def test_insert_newline_4(self):
        beautified = SassBeautifyCommandInstance.beautify_newlines(textwrap.dedent("""\

            .ClassA {
                color: red;
                /*
                 This is class b
                */
                .ClassB {
                    color: blue;
                }
            }

            """))

        self.assertEqual(beautified, textwrap.dedent("""\

            .ClassA {
                color: red;

                /*
                 This is class b
                */
                .ClassB {
                    color: blue;
                }
            }

            """))


    # Check that two selectors already separated by a newline doesn't get an additional newline
    def test_skip_insert_newline_1(self):
        beautified = SassBeautifyCommandInstance.beautify_newlines(textwrap.dedent("""\

            .ClassA {
                color: red;
            }

            .ClassB {
                color: blue;
            }

            """))

        self.assertEqual(beautified, textwrap.dedent("""\

            .ClassA {
                color: red;
            }

            .ClassB {
                color: blue;
            }

            """))

    # Check that two nested selectors doesn't get any newlines
    def test_skip_insert_newline_2(self):
        beautified = SassBeautifyCommandInstance.beautify_newlines(textwrap.dedent("""\

            .ClassA {
                .ClassB {
                    color: blue;
                }
            }

            """))

        self.assertEqual(beautified, textwrap.dedent("""\

            .ClassA {
                .ClassB {
                    color: blue;
                }
            }

            """))
