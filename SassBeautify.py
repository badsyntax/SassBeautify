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

__version__ = '1.1.0'
__author__ = 'Richard Willis'
__email__ = 'willis.rh@gmail.com'
__copyright__ = 'Copyright 2013, Richard Willis'
__license__ = 'MIT'
__credits__ = ['scotthovestadt','WilliamVercken','Napanee']


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
        Execute the command in a sub-process.
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


class ReplaceTextCommand(sublime_plugin.TextCommand):

    '''
    A custom ST text command to replace the entire view with new text.
    '''

    def run(self, edit, text=None):
        self.view.replace(edit, sublime.Region(0, self.view.size()), text)


class SassBeautifyCommand(sublime_plugin.TextCommand):

    '''
    Our main SassBeautify ST text command.
    '''

    def run(self, edit, action='beautify', convert_from_type=None):

        self.action = action
        self.convert_from_type = convert_from_type
        self.settings = sublime.load_settings('SassBeautify.sublime-settings')

        if self.check_file() != False:
            self.beautify()

    def check_file(self):
        '''
        Perform some validation checks on the file to ensure we're working with
        something that we can beautify.
        '''
        # A file has to be saved so we can get the conversion type from the
        # file extension.
        if self.view.file_name() == None:
            sublime.error_message('Please save this file before trying to beautify.')
            return False

        # Check the file has the correct extension before beautifying.
        if self.get_type() not in ['sass', 'scss']:
            sublime.error_message('Not a valid Sass file.')
            return False

    def beautify(self):
        '''
        Run the sass beautify command.
        '''
        # The conversion operation might take a little while on slower
        # machines so we should let the user know something is happening.
        sublime.status_message('Beautifying your sass...')
        self.exec_cmd()

    def exec_cmd(self):
        '''
        Execute the threaded sass command.
        '''
        thread = ExecSassCommand(
            self.get_cmd(),
            self.get_env(),
            self.get_text()
        )
        thread.start()
        self.check_thread(thread)

    def check_thread(self, thread, i=0, dir=1):

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

        if type(output) is bytes:
            output = output.decode('utf-8')

        if type(error) is bytes:
            error = error.decode('utf-8')

        if returncode != 0:
            return sublime.error_message(
                'There was an error beautifying your Sass:\n\n' + error
            )

        # Ensure we're working with unix-style newlines.
        # Fixes issue on windows with Sass < v3.2.10.
        output = '\n'.join(output.splitlines())

        # Insert a blank line between selectors. (Issue #30)
        if self.get_type() == 'scss' and self.settings.get('blanklineBetweenSelectors', False):
            output = re.sub(r'\n\n\n', '\n\n', re.sub(r'(.*)\{', r'\n\1{', output).strip())

        # Update the text in the editor
        self.view.run_command('replace_text', {'text': output})

        # Save the file
        sublime.set_timeout(self.save, 1)

    def get_cmd(self):
        '''
        Generate the sass command we'll use to beauitfy the sass.
        '''
        filetype = self.get_type()

        cmd = [
            'sass-convert',
            '--unix-newlines',
            '--stdin',
            '--indent', str(self.settings.get('indent')),
            '--from', filetype if self.action == 'beautify' else self.convert_from_type,
            '--to', filetype
        ]

        # Convert underscores to dashes.
        if self.settings.get('dasherize') == True:
            cmd.append('--dasherize')

        # Output the old-style ':prop val' property syntax.
        # Only meaningful when generating Sass.
        if self.settings.get('old') == True and filetype == 'sass':
            cmd.append('--old')

        return cmd

    def get_env(self):
        '''
        Generate the process environment.
        '''
        env = os.environ.copy()

        # If path is set, modify environment. (Issue #1)
        if self.settings.get('path'):
            env['PATH'] = self.settings.get('path')

        return env

    def get_ext(self):
        '''
        Extract the extension from the filename.
        '''
        (basename, ext) = os.path.splitext(self.view.file_name())
        return ext.strip('.')

    def get_type(self):
        '''
        Returns the file type.
        '''
        filetype = self.get_ext();
        # Added experimental CSS support with issue #27.
        # If this is a CSS file, then we're to treat it exactly like a SCSS file.
        if self.action == 'beautify' and filetype == 'css':
            filetype = 'scss'
        return filetype

    def get_text(self):
        '''
        Get the sass text from the Sublime view.
        '''
        return self.view.substr(sublime.Region(0, self.view.size())).encode('utf-8')

    def save(self):
        '''
        Save the file and show a success message.
        '''
        self.view.run_command('save')
        sublime.status_message('Successfully beautified ' + self.view.file_name())
