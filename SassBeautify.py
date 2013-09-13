'''
SassBeautify - A Sublime Text 2/3 plugin that beautifies sass files.
https://github.com/badsyntax/SassBeautify
'''

import sublime
import sublime_plugin
import os
import subprocess
import threading

__version__   = '0.3.3'
__author__    = 'Richard Willis'
__email__     = 'willis.rh@gmail.com'
__copyright__ = 'Copyright 2013, Richard Willis'
__license__   = 'MIT'
__credits__   = ['scotthovestadt']

class ExecSassCmd(threading.Thread):
  '''
  This is a threaded class that we use for running the sass command in a
  different thread. We thread the sub-process se we don't lock up the UI.
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
        env    = self.env,
        shell  = sublime.platform() == 'windows',
        stdin  = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE
      )
      (self.stdout, self.stderr) = process.communicate(input = self.stdin)
      self.returncode = process.returncode;

    except OSError as e:
      self.stderr = str(e)
      self.returncode = 1;

class SassBeautifyCommand(sublime_plugin.TextCommand):
  '''
  Our main SassBeautify Sublime plugin.
  '''
  def run(self, edit, action='beautify', type=None):

    self.action = action
    self.type = type
    self.settings = sublime.load_settings('SassBeautify.sublime-settings')

    if self.check_file() != False:
      self.beautify(edit)

  def check_file(self):
    '''
    Perform some validation checks on the file to ensure we're working with
    something that we can beautify.
    '''
    # A file has to be saved so we can get the conversion type from the file extension.
    if self.view.file_name() == None:
      sublime.error_message('Please save this file before trying to beautify.')
      return False

    # Check the file has the correct extension before beautifying.
    if self.get_ext() not in ['sass', 'scss']:
      sublime.error_message('Not a valid Sass file.')
      return False

  def beautify(self, edit):
    '''
    Run the sass beautify command, update the sublime view and save the file.
    '''
    # The conversion operation might take a little while on slower
    # machines so we should let the user know something is happening.
    sublime.status_message('Beautifying your sass...')

    (returncode, output, error) = self.exec_cmd()

    if returncode != 0:
      return sublime.error_message(
        'There was an error beautifying your Sass:\n\n' + error
      )

    # Ensure we're working with unix-style newlines.
    # Fixes issue on windows with Sass < v3.2.10.
    output = '\n'.join(output.splitlines())

    self.update(output, edit)
    sublime.set_timeout(self.save, 1)

  def exec_cmd(self):
    '''
    Execute the threaded sass command.
    '''
    cmd = ExecSassCmd(
      self.get_cmd(),
      self.get_env(),
      self.get_text().encode('utf-8')
    )
    cmd.start()
    cmd.join()

    if type(cmd.stdout) is bytes:
       cmd.stdout = cmd.stdout.decode('utf-8')

    if type(cmd.stderr) is bytes:
       cmd.stderr = cmd.stderr.decode('utf-8')

    return (cmd.returncode, cmd.stdout, cmd.stderr)

  def get_cmd(self):
    '''
    Generate the sass command we'll use to beauitfy the sass.
    '''
    ext = self.get_ext()

    cmd = [
      'sass-convert',
      '--unix-newlines',
      '--stdin',
      '--indent', str(self.settings.get('indent')),
      '--from', ext if self.action == 'beautify' else self.type,
      '--to', ext
    ]

    # Convert underscores to dashes.
    if self.settings.get('dasherize') == True:
      cmd.append('--dasherize')

    # Output the old-style ':prop val' property syntax.
    # Only meaningful when generating Sass.
    if self.settings.get('old') == True and ext == 'sass':
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

  def get_text(self):
    '''
    Get the sass text from the Sublime view.
    '''
    return self.view.substr(sublime.Region(0, self.view.size()))

  def update(self, sass, edit):
    '''
    Update the sublime view.
    '''
    self.view.replace(edit, sublime.Region(0, self.view.size()), sass)

  def save(self):
    '''
    Save the file and show a success message.
    '''
    self.view.run_command('save')
    sublime.status_message('Successfully beautified ' + self.view.file_name())