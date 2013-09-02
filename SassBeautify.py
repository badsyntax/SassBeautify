'''
SassBeautify - A Sublime Text 2/3 plugin that beautifies sass files.
https://github.com/badsyntax/SassBeautify
'''

import os
import subprocess
import sublime
import sublime_plugin

__version__   = '0.3.1'
__author__    = 'Richard Willis'
__email__     = 'willis.rh@gmail.com'
__copyright__ = 'Copyright 2013, Richard Willis'
__license__   = 'MIT'
__credits__   = ['scotthovestadt']

class SassBeautifyCommand(sublime_plugin.TextCommand):

  def run(self, edit, action='beautify', type=None):

    self.action = action
    self.type = type
    self.settings = sublime.load_settings('SassBeautify.sublime-settings')

    if self.check_file() != False:
      self.beautify(edit)

  def check_file(self):

    # A file has to be saved before beautifying so we can get the conversion type
    # from the file extension.
    if self.view.file_name() == None:
      sublime.error_message('Please save this file before trying to beautify.')
      return False

    # Check the file has the correct extension before beautifying.
    if self.get_ext() not in ['sass', 'scss']:
      sublime.error_message('Not a valid Sass file.')
      return False

  def beautify(self, edit):

    try:
      exitstatus, output, err = self.exec_cmd()
    except OSError as e:
      exitstatus, err = 1, str(e) + '\n\nDoes \'sass-convert\' exist in PATH?'

    if exitstatus != 0:
      return sublime.error_message(
        'There was an error beautifying your Sass:\n\n' + err
      )

    self.update(output, edit)
    sublime.set_timeout(self.save, 1)

  def exec_cmd(self):

    is_windows = sublime.platform() == 'windows'

    # If path is set, modify environment. (Issue #1)
    env = os.environ.copy()
    if self.settings.get('path'):
      env['PATH'] += ';' if is_windows else ':' + self.settings.get('path')

    process = subprocess.Popen(
      self.generate_cmd(),
      env    = env,
      shell  = is_windows,
      stdin  = subprocess.PIPE,
      stdout = subprocess.PIPE,
      stderr = subprocess.PIPE
    )

    output, err = process.communicate(
      # sass text to stdin
      input = self.get_text().encode('utf-8')
    )

    output = output.decode('utf-8')
    err = err.decode('utf-8')

    # Ensure we're working with unix-style newlines.
    # Fixes issue on windows with Sass < v3.2.10.
    output = '\n'.join(output.splitlines())

    return process.returncode, output, err

  def generate_cmd(self):

    ext = self.get_ext()

    cmd = [
      'sass-convert',
      '--unix-newlines',
      '--stdin',
      '--indent', str(self.settings.get('indent')),
      '--from', ext if self.action == 'beautify' else self.type,
      '--to', ext,
      '-E', 'utf-8' # Fixes issue 14
    ]

    # Convert underscores to dashes.
    if self.settings.get('dasherize') == True:
      cmd.append('--dasherize')

    # Output the old-style ':prop val' property syntax.
    # Only meaningful when generating Sass.
    if self.settings.get('old') == True and ext == 'sass':
      cmd.append('--old')

    return cmd

  def get_ext(self):
    basename, ext = os.path.splitext(self.view.file_name())
    return ext.strip('.')

  def get_text(self):
    return self.view.substr(sublime.Region(0, self.view.size()))

  def update(self, sass, edit):
    self.view.replace(edit, sublime.Region(0, self.view.size()), sass)

  def save(self):
    self.view.run_command('save')
    sublime.status_message('Successfully beautified ' + self.view.file_name())