'''
SassBeautify - A Sublime Text 2/3 plugin that beautifies sass files.
https://github.com/badsyntax/SassBeautify
'''
import sublime
import sublime_plugin
import os
import subprocess
import threading
import re

__version__ = '1.3.0'
__author__ = 'Richard Willis'
__email__ = 'willis.rh@gmail.com'
__copyright__ = 'Copyright 2013, Richard Willis'
__license__ = 'MIT'
__credits__ = ['scotthovestadt', 'WilliamVercken', 'Napanee']


class ExecSassCommand(threading.Thread):

    '''
    This is a threaded class that we use for running the sass command in a
    different thread. We thread the sub-process se we don't lockup the UI.
    '''

    def __init__(self, cmd, env, stdin):

        self.cmd = cmd
        self.env = env
        self.stdin = stdin
        self.returncode = 0
        self.stdout = None
        self.stderr = None

        threading.Thread.__init__(self)

    def run(self):
        '''
        Executes the command in a sub-process.
        '''
        try:
            process = subprocess.Popen(
                self.cmd,
                env=self.env,
                shell=sublime.platform() == 'windows',
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            (self.stdout, self.stderr) = process.communicate(input=self.stdin)
            self.returncode = process.returncode
        except OSError as e:
            self.stderr = str(e)
            self.returncode = 1


class SassBeautifyReplaceTextCommand(sublime_plugin.TextCommand):

    '''
    A Text Command to replace the entire view with new text.
    '''

    def run(self, edit, text=None):
        self.view.replace(edit, sublime.Region(0, self.view.size()), text)


class SassBeautifyEvents(sublime_plugin.EventListener):

    '''
    An EventListener class to utilize Sublime's events.
    '''

    def on_post_save(self, view):
        '''
        After saving the file, optionally beautify it. This is done
        on_post_save because the beautification is asynchronous.
        '''
        settings = sublime.load_settings('SassBeautify.sublime-settings')
        beautify_on_save = settings.get('beautifyOnSave', False)

        if not SassBeautifyCommand.saving and beautify_on_save:
            view.run_command('sass_beautify', {
                'show_errors': False
            })


class SassBeautifyCommand(sublime_plugin.TextCommand):

    '''
    Our main SassBeautify Text Command.
    '''

    saving = False

    def run(self, edit, action='beautify', convert_from_type=None, show_errors=True):

        self.action = action
        self.convert_from_type = convert_from_type
        self.settings = sublime.load_settings('SassBeautify.sublime-settings')
        self.show_errors = show_errors

        if self.check_file():
            self.beautify()

    def check_file(self):
        '''
        Performs some validation checks on the file to ensure we're working with
        something that we can beautify.
        '''
        # A file has to be saved so we can get the conversion type from the
        # file extension.
        if self.view.file_name() is None:
            self.error_message('Please save this file before trying to beautify.')
            return False

        # Check the file has the correct extension before beautifying.
        if self.get_type() not in ['sass', 'scss']:
            self.error_message('Not a valid Sass file.')
            return False

        return True

    def error_message(self, message):
        '''
        Shows a Sublime error message.
        '''
        if self.show_errors:
            sublime.error_message(message)

    def beautify(self):
        '''
        Runs the sass beautify command.
        '''
        thread = ExecSassCommand(
            self.get_cmd(),
            self.get_env(),
            self.get_text()
        )
        thread.start()
        self.check_thread(thread)

    def beautify_newlines(self, content):

        def repl1(m):
            return m.group(1) + '\n'

        def repl2(m):
            return m.group(1) + '\n' + m.group(2)
        
        # insert newline after }, but only if it's nested ("top" selector are already separated by newlines)
        content = re.sub('([ {]+})', repl1, content)
        
        # insert newline after semi-colon if the line after defines a selector, to make the selector stand out
        content = re.sub('(;)(\n.+{)', repl2, content)
        
        return content

    def check_thread(self, thread, i=0, dir=1):
        '''
        Checks if the thread is still running.
        '''

        # This animates a little activity indicator in the status area
        # Taken from https://github.com/wbond/sublime_prefixr
        before = i % 8
        after = (7) - before
        if not after:
            dir = -1
        if not before:
            dir = 1
        i += dir

        self.view.set_status(
            'sassbeautify',
            'SassBeautify [%s=%s]' % (' ' * before, ' ' * after)
        )

        if thread.is_alive():
            return sublime.set_timeout(lambda: self.check_thread(thread, i, dir), 100)

        self.view.erase_status('sassbeautify')
        self.handle_process(thread.returncode, thread.stdout, thread.stderr)

    def handle_process(self, returncode, output, error):
        '''
        Handles the streams from the threaded process.
        '''

        if type(output) is bytes:
            output = output.decode('utf-8')

        if type(error) is bytes:
            error = error.decode('utf-8')

        if returncode != 0:
            return self.error_message(
                'There was an error beautifying your Sass:\n\n' + error
            )

        # Ensure we're working with unix-style newlines.
        # Fixes issue on windows with Sass < v3.2.10.
        output = '\n'.join(output.splitlines())

        output = self.beautify_newlines(output)

        # Update the text in the editor
        self.view.run_command('sass_beautify_replace_text', {'text': output})

        # Save the file
        sublime.set_timeout(self.save, 1)

    def get_cmd(self):
        '''
        Generates the sass command.
        '''
        filetype = self.get_type()

        cmd = [
            'sass-convert',
            '--unix-newlines',
            '--stdin',
            '--indent', str(self.settings.get('indent', 't')),
            '--from', filetype if self.action == 'beautify' else self.convert_from_type,
            '--to', filetype
        ]

        # Convert underscores to dashes.
        if self.settings.get('dasherize', False):
            cmd.append('--dasherize')

        # Output the old-style ':prop val' property syntax.
        # Only meaningful when generating Sass.
        if self.settings.get('old', False) and filetype == 'sass':
            cmd.append('--old')

        return cmd

    def get_env(self):
        '''
        Generates the process environment.
        '''
        env = os.environ.copy()

        # If path is set, modify environment. (Issue #1)
        if self.settings.get('path', False):
            env['PATH'] = self.settings.get('path')

        return env

    def get_ext(self):
        '''
        Extracts the extension from the filename.
        '''
        (basename, ext) = os.path.splitext(self.view.file_name())
        return ext.strip('.')

    def get_type(self):
        '''
        Returns the file type.
        '''
        filetype = self.get_ext()
        # Added experimental CSS support with issue #27.
        # If this is a CSS file, then we're to treat it exactly like a SCSS file.
        if self.action == 'beautify' and filetype == 'css':
            filetype = 'scss'
        return filetype

    def get_text(self):
        '''
        Gets the sass text from the Sublime view.
        '''
        return self.view.substr(sublime.Region(0, self.view.size())).encode('utf-8')

    def save(self):
        '''
        Saves the file and show a success message.
        '''

        # We have to store the state to prevent us getting in an infinite loop
        # when beautifying on_post_save.
        SassBeautifyCommand.saving = True
        self.view.run_command('save')
        SassBeautifyCommand.saving = False

        sublime.status_message('Successfully beautified ' + self.view.file_name())
