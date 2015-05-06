import sublime, sublime_plugin
import subprocess, os

class GitOpenChangedFiles(sublime_plugin.TextCommand):
  def print_with_status(self, message):
    sublime.status_message(message)
    print(message)

  def print_with_error(self, error_message):
    sublime.error_message(error_message)
    print(error_message)

  def system_folder_seperator(self):
    if sublime.platform() == "windows":
      return "\\\\"
    else:
      return "/"

  # http://stackoverflow.com/questions/9877462/is-there-a-python-equivalent-to-the-which-command
  def which(self, program_name):
    path = os.getenv('PATH')
    for p in path.split(os.path.pathsep):
        p = os.path.join(p, program_name)
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p

  def run(self, edit):
    current_folder = sublime.active_window().folders()[0]
    git_path = self.which('git')

    if not git_path:
      self.print_with_error("git not found in PATH")
      return

    pr = subprocess.Popen( git_path + " diff --name-only origin/master" , cwd = current_folder, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    (files_modified, error) = pr.communicate()

    if error:
      self.print_with_error(error)
      return
    else:
      files_modified_split = files_modified.splitlines()
      for file_modified in files_modified_split:
        sublime.active_window().open_file(current_folder + self.system_folder_seperator() + bytes.decode(file_modified))
      self.print_with_status("Git: Opened files modified in branch")

