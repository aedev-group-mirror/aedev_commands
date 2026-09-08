"""
software development operation commands helpers
===============================================

.. hint::
    this module is designed to provide a comprehensive set of constants, types, and helper functions
    for executing and managing DevOps on your Python projects in your Python virtual environments.


fundamental shell execution helpers
-----------------------------------

the helper functions :func:`sh_exit_if_git_err` provides fundamental Git command tracing for in-depth logging/debugging.

the logging of executed command lines and their console output is highly useful for debugging and protocolling
purposes. this portion provides the following helper functions to implement logging for external commands.
logging gets automatically enabled, if the corresponding log file exists.

* :func:`sh_log`: writes a single command execution log entry.
* :func:`sh_logs`: determines the file paths of the currently existing/enabled log files.

* :data:`SHELL_LOG_FILE_NAME_SUFFIX`: the default filename suffix for shell command log files.

.. hint::
    this feature is implemented in :func:`sh_exit_if_git_err` for all the git command execution helpers (``git_*()``)
    of this portion. to enable logging of all executed git commands simply create a log file with the name
    ``git_sh.log``, situated in the current working directory and/or in the users home directory (~).


git command helpers
-------------------

this portion is providing helper functions for lots of git commands, most of them allow to activate git trace
for debugging or intensive testing.

git commands will be executed in repo root folder of a project. the current working directory will be changed
accordingly before a git command get executed (and restored to the old working directory after the execution).

to support `GIT HOOKS <https://git-scm.com/book/ms/v2/Customizing-Git-Git-Hooks>`__ that execute Python code,
the Python virtual environment of a project will be activated before the git command get executed, and restored
to the old value after the git command has finished.

extensive debugging using the `GIT TRACE <https://git-scm.com/docs/api-trace>`__ feature of the git commands
will be activating if your app based on :mod:`~ae.console.ConsoleApp` got executed with
the --debug_level/-D option specified.

* :func:`bytes_file_diff`: returns the differences between a byte buffer and a file, using the `git diff` command.
* :func:`check_commit_msg_file`: checks for the existence of a Git commit message file.
* :func:`editable_project_root_path`: determine the project path of a project package installed as editable.
* :func:`git_add`: executes the `git add` command to stage changes.
* :func:`git_any`: executes any generic Git command.
* :func:`git_branches`: determines branch names in a Git repository.
* :func:`git_branch_files`: finds added, changed, or deleted files on a specified branch.
* :func:`git_branch_remotes`: return the remote names where the specified branch name exists.
* :func:`git_checkout`: executes the `git checkout` command to switch branches.
* :func:`git_clone`: clone a git remote repository from a repository hoster onto your local machine.
* :func:`git_commit`: executes the `git commit` command.
* :func:`git_current_branch`: determine the currently checked-out branch of the specified git repository/project.
* :func:`git_diff`: determine the uncommited/unstaged changes of the specified git repository/project.
* :func:`git_fetch`: executes the `git fetch` command.
* :func:`git_init_if_needed`: check and create a git repository if already not exists in the specified project.
* :func:`git_merge`: merge current worktree with the specified [remote/]branch (exit app if an error occurred).
* :func:`git_push`: executes the `git push` command.
* :func:`git_ref_in_branch`: check if branch/tag/ref is in the specified branch.
* :func:`git_remote_domain_group: determine the domain and the repository owner group-/user-name from .git/config.
* :func:`git_remotes`: retrieves the remote URLs of the repository.
* :func:`git_renew_remotes`: renew the origin remote and optionally (if repo is forked) also the upstream remote.
* :func:`git_status`: get the status of the project repository.
* :func:`git_tag_add`: add a new tag onto the project in the specified project root path.
* :func:`git_tag_list`: determine a list of matching tags of a local or remote git repository.
* :func:`git_tag_remotes`: return the remote names where the specified tag name exists.
* :func:`git_uncommitted`: lists all uncommitted files.
* :func:`git_user_email`: retrieves the Git user's email.
* :func:`git_user_name`: retrieves the Git user's name.
* :func:`git_version_tag`: determines the current version tag of the repository.
* :func:`owner_project_from_url`: determine the project path, including owner and project name from the remote url.

git command constants and types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* :data:`EXEC_GIT_ERR_PREFIX`: the prefix used to mark Git execution errors.
* :data:`GIT_CLONE_CACHE_CONTEXT`: the temporary folder context identifier used for Git clone downloads.
* :data:`GIT_FOLDER_NAME`: the default name of the Git-internal subfolder.
* :data:`GIT_REMOTE_ORIGIN`: the default name for the origin remote.
* :data:`GIT_REMOTE_UPSTREAM`: the default name for the upstream remote.
* :data:`GIT_RELEASE_REF_PREFIX`: the default prefix, used for release branches.
* :data:`GIT_VERSION_TAG_PREFIX`: the default prefix, used for version tags.
* :data:`GitRemotesType`: the type hint for a dictionary of Git remotes.


pip command helpers
-------------------

* :func:`pip_install`: install/check/find outdated external Python projects/distributions required by a Python project.


virtual environment helpers
---------------------------

these helper functions are provided to assist with the management of Python virtual environments.

* :func:`in_prj_dir_venv`: a context manager that temporarily changes the working directory and activates
  the project's virtual environment.
* :func:`in_venv`: set the VENV OS environment variables in :attr:`os.environ` via a patched dict within the context.
* :func:`venv_bin_path`: determines the bin/scripts path of a Python virtual environment.
* :func:`venv_check_prefixes`: determine the possible VENV root/prefix paths of all the supported VENV systems.
* :func:`venv_module_var_val`: determine a variable value declared in a Python module, installed in any other VENV.
* :func:`venv_name: determine the name/id of the current VENV used by a project.
* :func:`venv_os_env_vars`: returns the OS environment variables of a VENV (Python virtual environment).
* :func:`venv_sh_exec_kwargs: determine the :func:`sh_exec`-kwargs to set/switch the OS-env vars of a VENV.


the following example installs the required packages of a project into its local virtual environment by
using the :func:`in_prj_dir_venv` context manager together with the shell execution function :func:`sh_exec`
and the constant :data:`~aedev.base.PIP_CMD` (which differs depending on your OS)::

    with in_prj_dir_venv(project_root_path):
        sh_err = sh_exec(PIP_CMD + " install -r requirements.txt")
"""
# pylint: disable=too-many-lines
import json
import os
import shlex
import subprocess
import sys
import tempfile

from ast import literal_eval
from collections.abc import Callable, Iterable, Iterator
from contextlib import contextmanager
from urllib.parse import urlparse
from typing import Any, cast

from ae.base import (                                                                                   # type: ignore
    DEF_PROJECT_PARENT_FOLDER, UNSET, UnsetType,
    dummy_function, extend_file, in_wd, norm_path, now_str,
    os_path_basename, os_path_dirname, os_path_expanduser, os_path_isdir, os_path_isfile, os_path_join,
    read_file, write_file)
from ae.system import norm_pip_name, os_env_venv, venv_prefix                                           # type: ignore
from ae.paths import path_folders                                                                       # type: ignore
from ae.core import main_app_instance, temp_context_get_or_create, AppBase                              # type: ignore
from ae.console import ConsoleApp                                                                       # type: ignore
from ae.shell import (                                                                                  # type: ignore
    STDERR_BEG_MARKER, hint, in_os_env, mask_token, output_zero_split, sh_exec, sh_exit_if_exec_err)
from aedev.base import COMMIT_MSG_FILE_NAME, DEF_MAIN_BRANCH, PIP_CMD                                   # type: ignore


__version__ = '0.3.18'


EXEC_GIT_ERR_PREFIX = "sh_exec() returned error "       #: used by sh_exit_if_exec_err to mark error in 1st output line

GIT_CLONE_CACHE_CONTEXT = 'shell.git_clone'             #: temp directory context for git clone downloads
GIT_FOLDER_NAME = '.git'                                #: git subfolder in project path root of local repository
GIT_REMOTE_ORIGIN = 'origin'                            #: git origin remote name of (fork) repository in user account
GIT_REMOTE_UPSTREAM = 'upstream'                        #: git upstream remote name of original/forked repository
GIT_RELEASE_REF_PREFIX = 'release'                      #: git repository release branch name prefix
GIT_VERSION_TAG_PREFIX = 'v'                            #: git repository version tag prefix

PIP_EDITABLE_PROJECT_PATH_PREFIX = 'Editable project location: '
""" caption/field-name of the console output of the `pip show` command. """

SHELL_LOG_FILE_NAME_SUFFIX = "_sh.log"                  #: default file name (suffix) of the shell log file

VENV_SUB_DIR_NAMES = ('.venv/', 'venv/', 'env/', '.env/')  #: recognized folder names of a project-local VENV
VENV_ID_SEARCH_DEPTH = 3                                #: number of folders to climb up to find a projects VENV name/id

# types ---------------------------------------------------------------------------------------------------------------

GitRemotesType = dict[str, str]                         #: git remote urls dict with keys like 'origin' / 'upstream'

# helper functions ----------------------------------------------------------------------------------------------------


def bytes_file_diff(file_content: bytes, file_path: str, line_sep: str = os.linesep) -> str:
    """ return the differences between the content of a file against the specified file content buffer.

    :param file_content:        older file bytes to be compared against the file content of the file specified by the
                                :paramref:`.file_path` argument.
    :param file_path:           path to the file of which newer content gets compared against the file bytes specified
                                by the :paramref:`.file_content` argument.
    :param line_sep:            string used to prefix, separate and indent the lines in the returned output string.
    :return:                    differences between the two file contents, compiled with the `git diff` command.
    """
    with tempfile.NamedTemporaryFile('w+b', delete=False) as tfp:  # delete_on_close kwarg available in Python 3.12+
        tfp.write(file_content)
        tfp.close()
        output = sh_exit_if_git_err(72, "git diff", extra_args=("--no-index", tfp.name, file_path), exit_on_err=False)
        os.remove(tfp.name)

    if output and not output[0].startswith(line_sep):
        output[0] = line_sep + output[0]

    return line_sep.join(output)


def check_commit_msg_file(project_path: str, *hint_args, commit_msg_file: str = COMMIT_MSG_FILE_NAME) -> str:
    """ check if the commit message file exists and if yes return the path of it.

    :param project_path:        project root path.
    :param hint_args:           hint arguments.
    :param commit_msg_file:     name of the git commit message file (default=:data:`aedev.base.COMMIT_MSG_FILE_NAME`).
    :return:                    the path of the git commit message file of this project.
    :raises:                    FileNotFoundError|shutdown if the commit message file is not readable or does not exist.
    """
    commit_msg_file = os_path_join(project_path, commit_msg_file)
    if not os_path_isfile(commit_msg_file) or not read_file(commit_msg_file):
        err = f"missing or unreadable commit message/file {commit_msg_file}" + (hint(*hint_args) if hint_args else "")
        if main_app := main_app_instance():
            main_app.shutdown(381, error_message=err)
        raise FileNotFoundError(err)  # un-skip-able-err fallback if shutdown() got mocked or main_app is not registered
    return commit_msg_file


def editable_project_root_path(project_name: str) -> str:
    """ determine the project path of a project package installed as editable.

    :param project_name:        project|package name to search for.
    :return:                    project source root path of an editable installed package
                                or empty string, if the package is not installed as editable.
    """
    output: list[str] = []
    if sh_exec(PIP_CMD, extra_args=("show", project_name), output_lines=output) == 0:
        for line in output:
            if line.startswith(PIP_EDITABLE_PROJECT_PATH_PREFIX):
                return line[len(PIP_EDITABLE_PROJECT_PATH_PREFIX):]

    # fallback if pip is an older version (before 21, without PEP 660 support)
    for install_path in sys.path:
        egg_link_file = os_path_join(install_path, project_name + '.egg-link')
        if os_path_isfile(egg_link_file):
            return read_file(egg_link_file).splitlines()[0]

    return ""


def git_add(project_path: str, *extra_args: str):
    """ execute the git add command.

    :param project_path:        project path.
    :param extra_args:          additional arguments passed onto git add command. default=["-A"].
    """
    with in_prj_dir_venv(project_path):
        sh_exit_if_git_err(331, "git add", extra_args=extra_args or ["-A"])


def git_any(project_path: str, *args: str) -> list[str]:
    """ execute any git command.

    :param project_path:        path to project root folder.
    :param args:                arguments passed onto the git executable. first arg is the git command.
    :return:                    list of console output lines of the git command optionally including the exit error code
                                (marked with :data:`EXEC_GIT_ERR_PREFIX` in the first returned list item),
                                like returned by :func:`sh_exit_if_git_err`.
    """
    with in_prj_dir_venv(project_path):
        output = sh_exit_if_git_err(329, "git", extra_args=args)
    return output


def git_branches(project_path: str, *extra_args: str) -> list[str]:
    """ determine all branch names with the git branch command.

    :param project_path:        path to project root folder.
    :param extra_args:          additional arguments passed onto git branch command. default=("-a", "--no-color").
    :return:                    list of branch names of the project repo.
    """
    with in_prj_dir_venv(project_path):
        all_branches = sh_exit_if_git_err(327, "git branch", extra_args=extra_args or ("-a", "--no-color"))
    return [branch_name[2:] for branch_name in all_branches]


def git_branch_files(project_path: str, branch_or_tag: str = DEF_MAIN_BRANCH, untracked: bool = False,
                     skip_file_path: Callable[[str], bool] = lambda _: False) -> set[str]:
    """ find all added/changed/deleted/renamed/unstaged worktree files that are not merged into the main branch.

    :param project_path:        path of the project root folder. pass empty string to use the current working directory.
    :param branch_or_tag:       branch(es)/tag(s)/commit(s) passed to `git diff <https://git-scm.com/docs/git-diff>`__
                                to specify the changed files between version(s).
    :param skip_file_path:      called for each found file passing the file path relative to the project root folder
                                (specified by the :paramref:`.project_path` argument), returning
                                True to exclude/skip the file with passed file path.
    :param untracked:           pass True to include untracked files from the returned result set.
    :return:                    set of file paths relative to worktree root specified by the project root path
                                specified by the :paramref:`.project_path` argument.

    .. hint:: see also func:`git_uncommitted` and the unit tests for the differences between them.
    """
    file_paths = set()

    def _call(_cmd: str, _args: tuple[str, ...], _dedent: int = 0):
        _output = sh_exit_if_git_err(318, _cmd, extra_args=_args, exit_on_err=False)
        for _fil_path in _output:
            _fil_path = _fil_path[_dedent:]
            if not skip_file_path(_fil_path):
                file_paths.add(_fil_path)

    with in_prj_dir_venv(project_path):
        if untracked:
            _call("git ls-files", ("--cached", "--others"))
            _call("git status", ("--find-renames", "--porcelain",  "--untracked-files", "-v"), _dedent=3)
        # --compact-summary is alternative to --name-only
        _call("git diff", ("--find-renames", "--full-index", "--name-only", "--no-color", branch_or_tag))

    return file_paths


def git_branch_remotes(project_path: str, branch_pattern: str, remote_names: Iterable[str] = ()) -> list[str]:
    """ return the remote names where the specified branch name exists.

    :param project_path:        path of the project root folder.
    :param branch_pattern:      branch name pattern to search for.
    :param remote_names:        iterable with the remote names. determined with :func:`git_remotes` if not specified.
    :return:                    list of remote names where the branch exists.
    """
    if not remote_names:
        remote_names = git_remotes(project_path)

    remotes = []
    for remote_name in remote_names:
        output = git_any(project_path, 'ls-remote', '--heads', remote_name, branch_pattern)  # --branches in future
        if output and not output[0].startswith(EXEC_GIT_ERR_PREFIX):
            remotes.append(remote_name)
    return remotes


def git_checkout(project_path: str, *extra_args: str,
                 new_branch: str = "", exit_on_err: bool = True, force: bool = False, remote_names: Iterable[str] = ()
                 ) -> str:
    """ checkout git branch.

    :param project_path:        path of the project root folder.
    :param extra_args:          additional arguments passed onto git checkout command.
    :param new_branch:          new branch name to create and check out.
    :param exit_on_err:         specify False to not exit the Python app on any git checkout error.
    :param force:               pass True to ignore uncommitted files and if undefined branch.
    :param remote_names:        iterable with the remote names. determined with :func:`git_remotes` if not specified.
    :return:                    error message or empty string if no error occurred.
    """
    if not force and new_branch:
        if (uncommitted_files := git_uncommitted(project_path)) and new_branch in git_branches(project_path):
            current_branch = git_current_branch(project_path)
            return f"{new_branch=} exists already and {current_branch=} has {uncommitted_files=}"
        if branch_remotes := git_branch_remotes(project_path, new_branch, remote_names=remote_names):
            return f"{new_branch} exists already on the remote(s): {', '.join(branch_remotes)}"

    args = ["--quiet"]
    if new_branch:
        args.extend(["-b", new_branch])
    args.extend(extra_args)

    with in_prj_dir_venv(project_path):
        output = sh_exit_if_git_err(357, "git checkout", extra_args=args, exit_on_err=exit_on_err)

    return os.linesep.join(output)


def git_clone(repo_parent_url: str, project_name: str, *extra_args: str,
              branch_or_tag: str = "", parent_path: str = "", enable_log: bool = False) -> str:
    """ clone a git remote repository from a repository hoster onto your local machine.

    :param repo_parent_url:     repository parent/group url (without the project name to clone).
    :param project_name:        project name to clone.
    :param extra_args:          extra arguments passed onto the git clone command.
    :param branch_or_tag:       repo branch to clone. if not specified then the main branch will be cloned.
    :param parent_path:         destination path on the local machine to clone onto. if not specified a temporary folder
                                will be used.
    :param enable_log:          pass True to enable git shell command logging.
    :return:                    path to the cloned repository folder or empty string if an error occurred.

    .. hint:: there could occur a user/password prompt if repo is private/invalid!
    """
    if not parent_path:
        parent_path = temp_context_get_or_create(context=GIT_CLONE_CACHE_CONTEXT, folder_name=DEF_PROJECT_PARENT_FOLDER)
    project_path = norm_path(os_path_join(parent_path, project_name))

    args = []
    if branch_or_tag:
        # https://stackoverflow.com/questions/791959/download-a-specific-tag-with-git says:
        # add -b <tag> to specify a release tag/branch to clone, adding --single-branch will speed up the download
        args.append("--branch")
        args.append(branch_or_tag)
        args.append("--single-branch")
    if extra_args:
        args.extend(extra_args)
    args.append(f"{repo_parent_url}/{project_name}.git")

    with in_prj_dir_venv(parent_path):
        output = sh_exit_if_git_err(315, "git clone", extra_args=args, exit_on_err=False,
                                    log_enable_dir=project_path if enable_log else "")

    if output and output[0].startswith(EXEC_GIT_ERR_PREFIX):
        return ""
    return project_path


def git_commit(project_path: str, project_version: str, *extra_args: str,
               commit_msg_text: str = "", commit_msg_file: str = COMMIT_MSG_FILE_NAME):
    """ execute the command 'git commit' for the specified project.

    :param project_path:        path of the project root folder, in which this git command gets executed.
    :param project_version:     project version string.
    :param extra_args:          additional options or args passed to the `git commit` command line,
                                e.g., ["--patch", "--dry-run"]. except from the --file option, which will be added
                                by this function with the name of the git commit message file.
    :param commit_msg_text:     used commit message. if specified then the argument
                                in :paramref:`.commit_msg_file` will be ignored.
    :param commit_msg_file:     name of the git commit message file (default=:data:`aedev.base.COMMIT_MSG_FILE_NAME`).
    """
    if commit_msg_text:
        args = ["--message", commit_msg_text]
    else:
        file_name = check_commit_msg_file(project_path, commit_msg_file=commit_msg_file)
        commit_msg = read_file(file_name)
        commit_msg = commit_msg.replace('{project_version}', project_version)  # no format() to allow e.g. {apk_ext}
        write_file(file_name, commit_msg)
        args = [f"--file={file_name}"]  # not valid: "--file <file>" nor "--file='<file>'
    args.extend(extra_args)

    with in_prj_dir_venv(project_path):
        sh_exit_if_git_err(382, "git commit", extra_args=args)


def git_current_branch(project_path: str) -> str:
    """ determine the currently checked-out branch of the specified git repository/project.

    :param project_path:        project root folder of the git repo.
    :return:                    name of the current branch, or an empty string if no branch is checked out.
    """
    if not os_path_isdir(os_path_join(project_path, GIT_FOLDER_NAME)):
        return ""

    with in_prj_dir_venv(project_path):
        cur_branch = sh_exit_if_git_err(328, "git branch --show-current")
    return cur_branch[0] if cur_branch else ""


def git_diff(project_path: str, *extra_args: str) -> list[str]:
    """ determine the uncommited/unstaged changes of the specified git repository/project.

    :param project_path:        project root folder.
    :param extra_args:          additional options and refs passed onto the git diff command, apart from the
                                always added options: --no-color, --find-copies-harder, --find-renames and --full-index.
                                pass e.g. --compact-summary or --name-only for a more compact output/return.
    :return:                    list of console output lines of the git diff command, optionally including the exit
                                error code (marked with :data:`EXEC_GIT_ERR_PREFIX` in the first returned list item),
                                like returned by :func:`sh_exit_if_git_err`.
    """
    args = ["--no-color", "--find-copies-harder", "--find-renames", "--full-index"]
    args.extend(extra_args)

    with in_prj_dir_venv(project_path):
        output = sh_exit_if_git_err(370, "git diff", extra_args=args, exit_on_err=False)

    return output


def git_fetch(project_path: str, *extra_args: str, exit_on_err: bool = False) -> list[str]:
    """ fetch repository from remotes.

    :param project_path:        project root folder.
    :param extra_args:          additional options and arguments (remote name) for the git fetch command.
    :param exit_on_err:         specify True to exit the Python app on any git fetch error.
    :return:                    list of lines from the console output that record an error (e.g. if no .git folder).
    """
    with in_prj_dir_venv(project_path):
        output = sh_exit_if_git_err(375, "git fetch", extra_args=extra_args, exit_on_err=exit_on_err)

    return [_ for _ in output if _.lstrip().startswith((EXEC_GIT_ERR_PREFIX, "!", 'fatal:'))]


def git_init_if_needed(project_path: str,
                       author: str = "", email: str = "", main_branch: str = DEF_MAIN_BRANCH) -> bool:
    """ check if a git repository already exists in the specified project root folder, and create it if not.

    :param project_path:        project root path
    :param author:              author of the project/repo added to git config (if specified).
    :param email:               email address of the author added to git config (if specified).
    :param main_branch:         first main branch name to be checked out if repo did not exist / got created.
                                if not specified then the value of :data:`aedev.base.DEF_MAIN_BRANCH` is used.
                                pass empty string to not do the initial checkout on a not existing repository.
    :return:                    boolean True if a new repo got created and initialized, else False.
    """
    if os_path_isdir(os_path_join(project_path, GIT_FOLDER_NAME)):
        return False

    with in_prj_dir_venv(project_path):
        # the next two config commands prevent error in test systems/containers
        sh_exit_if_git_err(351, "git init")
        if author:
            sh_exit_if_git_err(352, "git config", extra_args=("user.name", author))
        if email:
            sh_exit_if_git_err(353, "git config", extra_args=("user.email", email))
        if main_branch:
            sh_exit_if_git_err(354, "git checkout", extra_args=("-b", main_branch))
        sh_exit_if_git_err(355, "git commit", extra_args=("--allow-empty", "--message", "git repo initialization"))

    return True


def git_merge(project_path: str, from_branch: str, *extra_options: str,
              commit_msg_text: str = "", commit_msg_file: str = COMMIT_MSG_FILE_NAME, exit_on_err: bool = False
              ) -> list[str]:
    """ merge current worktree with the specified [remote/]branch (exit app if an error occurred).

    :param project_path:        project root path of worktree to merge.
    :param from_branch:         branch (or commit/tag) to merge into current worktree with (optional with a leading
                                upstream/origin remote name, e.g. "upstream/main_branch").
    :param extra_options:       extra arguments for the git command
    :param commit_msg_text:     commit message used for the optional merge commit. if specified then the argument
                                in :paramref:`.commit_msg_file` will be ignored.
    :param commit_msg_file:     name of the git commit message file (default=:data:`aedev.base.COMMIT_MSG_FILE_NAME`).
    :param exit_on_err:         specify True to exit the Python app on any git push error.
    :return:                    list with output lines of the git merge command (like returned by the function
                                :func:`sh_exit_if_git_err`, used to execute this git command).
                                if the git command returned with an error code and the argument in
                                :paramref:`.exit_on_err` got not specified or as a `True` argument, then
                                the app will quit. if :paramref:`.exit_on_err` got specified as 'False' and
                                git push returned an error code, then it will be returned in the first line/list-item
                                (prefixed with :data:`EXEC_GIT_ERR_PREFIX`).
    """
    extra_args: tuple[str, ...]
    if commit_msg_text:
        extra_args = ("--message", commit_msg_text)
    else:
        commit_msg_file = check_commit_msg_file(project_path, commit_msg_file=commit_msg_file)
        extra_args = ("--file", commit_msg_file)
    extra_args += extra_options + ("--log", "--no-stat", from_branch)

    with in_prj_dir_venv(project_path):
        output = sh_exit_if_git_err(377, "git merge", extra_args=extra_args, exit_on_err=exit_on_err)

    return output


def git_push(project_path: str, remote_repo_url: str, *options_and_refs: str, exit_on_err: bool = True) -> list[str]:
    """ push the repo of the specified project with the specified branch/tags to the specified remote.

    :param project_path:        project root folder.
    :param remote_repo_url:     remote repo url. if git credentials are not configured on the local system, then
                                a user token or password has to be included for the authentication against remote.
    :param options_and_refs:    extra arguments for the git command. pass additional options, e.g. "--delete" or
                                "--set-upstream" or "-u", and any references like branch/tag names to be pushed.
    :param exit_on_err:         specify False to not exit the Python app on any git push error.
    :return:                    list with output lines of the git push command (like returned by the function
                                :func:`sh_exit_if_git_err`, used to execute this git push command).
                                if git push returned with an error code and the argument in
                                :paramref:`.exit_on_err` got not specified or as a `True` argument, then
                                the app will quit. if :paramref:`.exit_on_err` got specified as 'False' and
                                git push returned an error code, then it will be returned in the first line/list-item
                                (prefixed with :data:`EXEC_GIT_ERR_PREFIX`).
    """
    options = []
    refs = []
    for arg in options_and_refs:
        if arg.startswith("-"):
            options.append(arg)
        else:
            refs.append(arg)

    with in_prj_dir_venv(project_path):
        output = sh_exit_if_git_err(380, "git push",
                                    extra_args=options + [remote_repo_url] + refs, exit_on_err=exit_on_err)

    return output


def git_ref_in_branch(project_path: str, ref: str, branch: str = f'{GIT_REMOTE_ORIGIN}/{DEF_MAIN_BRANCH}') -> bool:
    """ check if branch/tag/ref is in the specified branch.

    :param project_path:        project worktree root path.
    :param ref:                 any ref like a tag or another branch, to be searched within :paramref:`.branch`.
    :param branch:              branch to be searched in for :paramref:`.ref`. if not specified
                                then it defaults to the remote/origin main branch.
    :return:                    boolean True if the ref got found in the branch, else False.
    """
    with in_prj_dir_venv(project_path):
        extra_args = ("--all", "--contains", ref, "--format=%(refname:short)")
        output = sh_exit_if_git_err(388, "git branch", extra_args=extra_args, exit_on_err=False)
    return bool(output) and not output[0].startswith(EXEC_GIT_ERR_PREFIX) and branch in output


def git_remote_domain_group(project_path: str,
                            origin_name: str = GIT_REMOTE_ORIGIN, upstream_name: str = GIT_REMOTE_UPSTREAM,
                            remote_urls: GitRemotesType | None = None) -> tuple[str, str]:
    """ determine the domain and the repository owner group-/user-name from the git remote configuration (.git/config).

    :param project_path:        path to the project root folder of the repository.
    :param origin_name:         name of the origin git remote (to push to).
    :param upstream_name:       name of the upstream git remote (to request a merge from).
    :param remote_urls:         remote urls. defaults to :func:`git_remotes` if not provided.
    :return:                    tuple with the domain and the user/group of the upstream repository url. if no upstream
                                url is set/configured (not forked) then the origin url is used. if there is no remote
                                configured at all, then the returned tuple contains two empty strings.
    """
    if remote_urls is None:
        remote_urls = git_remotes(project_path)

    remote_url = remote_urls.get(upstream_name, remote_urls.get(origin_name))
    if not remote_url:
        return "", ""

    url_parts = urlparse(remote_url)
    return url_parts.hostname or "", url_parts.path[1:].split("/")[0]


def git_remotes(project_path: str) -> GitRemotesType:
    """ get mapping of hte project repository remotes.

    :param project_path:        path to the project root folder of the repository.
    :return:                    dict with the remote ids as keys and the url as the values.
    """
    remotes = {}
    if os_path_isdir(os_path_join(project_path, GIT_FOLDER_NAME)):
        with in_prj_dir_venv(project_path):
            remote_ids = sh_exit_if_git_err(321, "git remote")
            for remote_id in remote_ids:
                remote_url = sh_exit_if_git_err(322, "git remote", extra_args=("get-url", "--push", remote_id))
                remotes[remote_id] = remote_url[0]
    return remotes


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def git_renew_remotes(project_path: str, origin_url: str, upstream_url: str = "",
                      origin_name: str = GIT_REMOTE_ORIGIN, upstream_name: str = GIT_REMOTE_UPSTREAM,
                      remotes: GitRemotesType | None = None) -> list[str]:
    """ renew the origin remote and optionally (if repo is forked) also the upstream remote.

    :param project_path:        project root folder.
    :param origin_url:          new url of the origin repo. will append a missing .git extension to the specified url.
    :param upstream_url:        new url of the upstream repo if forked. if specified and differs to the actual upstream
                                url and to the specified origin url, then it will be automatically added.
                                appends a missing .git extension to the specified url.
    :param origin_name:         name of the origin git remote (to push to). if not specified defaults
                                to :data:`GIT_REMOTE_ORIGIN`.
    :param upstream_name:       name of the upstream git remote (to request a merge from). if not specified defaults
                                to :data:`GIT_REMOTE_UPSTREAM`.
    :param remotes:             pass the actual git remotes to prevent multiple execution of the git remote command.
                                determined via :func:`git_remotes` if not specified.
    :return:                    list of console output lines of the executed git remote commands.
                                an empty list no errors/warnings got outputted by the git remote command.
    """
    if not origin_url.endswith(".git"):
        origin_url += ".git"
    if upstream_url and not upstream_url.endswith(".git"):
        upstream_url += ".git"
    if not remotes:
        remotes = git_remotes(project_path)

    err = []
    with in_prj_dir_venv(project_path):
        if upstream_url:
            if upstream_name not in remotes:
                if upstream_url != origin_url:
                    err.extend(sh_exit_if_git_err(340, "git remote", extra_args=("add", upstream_name, upstream_url)))
            elif remotes[upstream_name] != upstream_url:
                err.extend(sh_exit_if_git_err(341, "git remote", extra_args=("set-url", upstream_name, upstream_url)))

        if origin_name not in remotes:
            err.extend(sh_exit_if_git_err(342, "git remote", extra_args=("add", origin_name, origin_url)))
        elif remotes[origin_name] != origin_url:
            err.extend(sh_exit_if_git_err(343, "git remote", extra_args=("set-url", origin_name, origin_url)))

    return err


def git_status(project_path: str, verbose: bool = False) -> list[str]:
    """ get the status of the project repository.

    :param project_path:        project root path.
    :param verbose:             pass True to return a more verbose console output (using --branch -vv --porcelain=2).
    :return:                    console output of the git status command.
    """
    args = ["--find-renames",  "--untracked-files"]  # --untracked-files=normal is missing a full subdir-rel-file-path
    if verbose:
        args.append("--branch")
        args.append("-vv")
        args.append("--porcelain=2")
    else:
        args.append("-v")
        args.append("--porcelain")

    with in_prj_dir_venv(project_path):
        output = sh_exit_if_git_err(376, "git status", extra_args=args)

    return output


def git_tag_add(project_path: str, tag: str, commit_msg_text: str = "", commit_msg_file: str = COMMIT_MSG_FILE_NAME
                ) -> list[str]:
    """ add a new tag onto the project in the specified project root path.

    :param project_path:        project root path.
    :param tag:                 tag to add.
    :param commit_msg_text:     commit message used for the optional merge commit. if specified then the argument
                                in :paramref:`.commit_msg_file` will be ignored.
    :param commit_msg_file:     name of the git commit message file (def=COMMIT_MSG_FILE_NAME).
    :return:                    console output of the git tag --annotate command.
    """
    if commit_msg_text:
        extra_args = ("--message", commit_msg_text)
    else:
        commit_msg_file = check_commit_msg_file(project_path, commit_msg_file=commit_msg_file)
        extra_args = ("--file", commit_msg_file)
    with in_prj_dir_venv(project_path):
        output = sh_exit_if_git_err(387, "git tag --annotate", extra_args=extra_args + (tag, ))
    return output


def git_tag_list(project_path: str, remote="", tag_pattern: str = "*") -> list[str]:
    """ determine a list of matching tags of a local or remote git repository.

    :param project_path:        project root folder.
    :param remote:              name of a remote.
                                if not specified then only local tags will be determined.
    :param tag_pattern:         matching pattern. if not specified then all tags will be returned.
    :return:                    list of matching repo tags, ordered via the git ls-remote option --sort=version:refname.
                                an empty list will be returned if no tag is matching the specified tag pattern
                                or an error occurred or if the project has no .git folder.
    """
    if not os_path_isdir(os_path_join(project_path, GIT_FOLDER_NAME)):
        return []

    with in_prj_dir_venv(project_path):
        if remote:
            output = sh_exit_if_git_err(389, "git ls-remote",
                                        extra_args=("--tags", "--refs", "--sort=version:refname", remote, tag_pattern),
                                        exit_on_err=False)
            if output and output[0].startswith(EXEC_GIT_ERR_PREFIX):
                output = []                                         # warning directly printed on console stderr
            else:
                output = [line.split("\t")[-1].split("/")[-1] for line in output]
        else:
            output = sh_exit_if_git_err(389, "git tag",
                                        extra_args=("--list", "--sort=version:refname", tag_pattern),
                                        exit_on_err=False)
            if output and output[0].startswith(EXEC_GIT_ERR_PREFIX):
                output = []

    return output


def git_tag_remotes(project_path: str, tag_pattern: str, remote_names: Iterable[str] = ()) -> list[str]:
    """ return the remote names where the specified tag name exists.

    :param project_path:        path of the project root folder.
    :param tag_pattern:         tag pattern to search for.
    :param remote_names:        iterable with the remote names. determined with :func:`git_remotes` if not specified.
    :return:                    list of remote names where the tag exists.
    """
    if not remote_names:
        remote_names = git_remotes(project_path)

    remotes = []
    for remote_name in remote_names:
        output = git_any(project_path, 'ls-remote', '--tags', remote_name, tag_pattern)
        if output and not output[0].startswith(EXEC_GIT_ERR_PREFIX):
            remotes.append(remote_name)
    return remotes


def git_uncommitted(project_path: str) -> set[str]:
    """ determine the changed/untracked/uncommitted files of a git repository/project.

    :param project_path:        project root folder.
    :return:                    set of changed/untracked/uncommitted file names.
                                an empty set will be returned if the git repo is not initialized or
                                if there are no uncommitted files in the git repo specified by project_path.

    .. hint:: see also func:`git_branch_files` and the unit tests for the differences between them.
    """
    if not os_path_isdir(os_path_join(project_path, GIT_FOLDER_NAME)):
        return set()

    with in_prj_dir_venv(project_path):
        output = sh_exit_if_git_err(379, "git status",
                                    extra_args=("--find-renames", "--untracked-files=all", "--porcelain"))
    return {_[3:] for _ in output}


@contextmanager
def in_prj_dir_venv(project_path: str = ".", venv_id: str = "") -> Iterator[None]:
    """ set CWD to the project root, os.environ from .env files and the specified or .python-version-configured VENV.

    :param project_path:        path to the project root folder to switch the current working directory in this context.
                                using the actual CWD if not specified.
    :param venv_id:             name/id of the Python Virtual Environment to activate in this context. if not specified
                                (or as empty string), then the VENV configured via the file .python-version will be
                                activated.
    :return:
    """
    with in_wd(project_path), in_os_env(project_path), in_venv(venv_id=venv_id):
        yield


@contextmanager
def in_venv(venv_id: str = "") -> Iterator[None]:
    """ set the VENV OS environment variables in :attr:`os.environ` via a patched dict within the context.

    :param venv_id:             the name of the VENV to activate. if not specified, then the VENV of the project in the
                                current working directory tree will be activated.

    .. note::
        changes done within this context on any variable value in :attr:`os.environ` will have no effect on the
        real/underlying environment variable value of the OS.
    """
    if not venv_id:
        venv_id = venv_name()  # detect current VENV name from the cwd/project_path or above, or from the OS env vars

    env_obj = None
    curr_id = os_env_venv()
    if curr_id != venv_id:
        env_obj = os.environ
        os.environ = cast(Any, env_obj.copy())  # cast to _Environ
        os.environ.update(venv_os_env_vars(venv_id))

    yield

    if env_obj:
        os.environ = env_obj


def owner_project_from_url(remote_url: str) -> str:
    """ determine the owner and project name path from the specified git remote repository url.

    :param remote_url:          remote repository url.
    :return:                    the owner name and the project name, separated with a slash character.
    """
    url_parts = urlparse(remote_url)
    url_path = url_parts.path
    if url_path.startswith("/"):
        url_path = url_path[1:]
    if url_path.endswith(".git"):
        url_path = url_path[:-4]
    return url_path


def pip_install(project_path: str, *required_projects: str, cooldown_period: str = "", dry_run: bool = False,
                force_reinstall: bool = False, return_implicits: bool = False) -> dict[str, dict[str, bool | str]]:
    """ install or check/find outdated external Python projects/distributions required by a Python project.

    :param project_path:        path to the project root folder for which the requirements will get installed/checked.
    :param required_projects:   list of required project names with optional project version numbers (separated by one
                                of the comparison operators supported by pip, like e.g.
                                :data:`~aedev.base.PROJECT_VERSION_SEP`).
    :param cooldown_period:     either ISO 8601 datetime (e.g., '2023-01-01T00:00:00Z') or number of days (e.g., 'P6D'
                                for uploaded at least 6 days ago).
    :param dry_run:             pass True to only check which (outdated) external Python projects would get installed.
    :param force_reinstall:     pass True to force the reinstallation of the required/outdated project versions.
    :param return_implicits:    pass True to return also implicit installed Python projects as comments.
    :return:                    dict of installed/outdated projects, with their normalized pip name as keys
                                and another/inner dict as values. the inner dict provides a "version" key
                                with the installed/found version as value. if True got specified for the
                                :paramref:`.return_implicits` argument, then also a "requested" key
                                will be available in the inner dict with a boolean value, which is True for
                                explicit installed/requiered projects and False for implicit ones.
    """
    args = ["--upgrade", "--quiet", "--report=-",
            "--root-user-action=ignore"]  # removes@CI "WARNING: Running pip as the 'root' user" on json-console-output
    if cooldown_period:
        # ISO 8601 datetime (e.g., '2023-01-01T00:00:00Z') or period (e.g., 'P6D' for uploaded at least 6 days ago)
        # using this option with "pip list" needs version>26.1.2 (issue #14189 created, will be fixed w/ #14190/v26.2)
        args.append(f"--uploaded-prior-to={cooldown_period}")
    if dry_run:
        args.append("--dry-run")
    if force_reinstall:
        args.append("--force-reinstall")

    out: list[str] = []
    with in_prj_dir_venv(project_path):
        err = sh_exec(PIP_CMD, extra_args=["install"] + args + list(required_projects), output_lines=out)
    outdated = {}
    if err == 0 and out:
        for item in json.loads(" ".join(out)).get("install", []):
            metadata = item["metadata"]
            requested = item["requested"]
            if requested or return_implicits:
                outdated[name := norm_pip_name(metadata["name"])] = {"version": metadata["version"]}
                if return_implicits:
                    outdated[name]["requested"] = requested

    return outdated


# pylint: disable-next=too-many-arguments,too-many-positional-arguments,too-many-locals
def sh_exit_if_git_err(err_code: int, command_line: str,
                       extra_args: Iterable[str] = (), output_lines: list[str] | None = None, exit_on_err: bool = False,
                       app_obj: ConsoleApp | UnsetType | None = None, log_enable_dir: str = "") -> list[str]:
    """ execute git command with optional git trace output, returning the stdout lines cleaned from any trace messages.

    :param err_code:            error code to pass to the console as exit code if :paramref:`.exit_on_err` is True.
    :param command_line:        command line string to execute on the console/shell. could contain command line args
                                separated by whitespace characters (alternatively use :paramref:`.extra_args`).
    :param extra_args:          optional iterable of extra command line arguments.
    :param output_lines:        optional list to return the lines printed to stdout/stderr on execution.
                                by passing an empty list, the stdout and stderr streams/pipes will be separated,
                                resulting in having the stderr output lines at the end of the list. specify at
                                least on list item to merge-in the stderr output (into the stdout output and return).
    :param exit_on_err:         pass True to exit the app on error.
    :param app_obj:             optional :class:`~ae.console.ConsoleApp` instance, used for logging.
                                if not specified or None then the Python :func:`print` function is used.
                                specify :data:`~ae.base.UNSET` to suppress any printing/logging output.
    :param app_obj:             :class:`~ae.console.ConsoleApp` instance, for logging and ignorable-error-checks.
    :param log_enable_dir:      pass the path of the directory in which git shell command logging have to get enabled.
    :return:                    output lines of git command - cleaned from GIT_TRACE messages,
                                if :paramref:`.exit_on_err` got specified as 'False' and the executed
                                git command returned an error code, then the error code will be returned in the first
                                line/list-item (prefixed with :data:`EXEC_GIT_ERR_PREFIX`).
    """
    if output_lines is None:
        output_lines = []
    if app_obj is None:
        app_obj = cast(ConsoleApp, main_app_instance())
    git_debug = isinstance(app_obj, AppBase) and app_obj.verbose
    print_out = dummy_function if app_obj is UNSET else app_obj.po if isinstance(app_obj, ConsoleApp) else print
    debug_out = dummy_function if app_obj is UNSET else app_obj.vpo if isinstance(app_obj, ConsoleApp) else print
    git_trace_vars = ('GIT_TRACE', 'GIT_TRACE_PACK_ACCESS', 'GIT_TRACE_PACKET', 'GIT_TRACE_SETUP')
    env_vars = {'GIT_TERMINAL_PROMPT': "0"}
    if git_debug:
        env_vars['GIT_CURL_VERBOSE'] = "1"
        env_vars['GIT_MERGE_VERBOSITY'] = "5"
        for var in git_trace_vars:
            env_vars[var] = "1"

    cl_err = sh_exit_if_exec_err(err_code, command_line,
                                 extra_args=extra_args, output_lines=output_lines, exit_on_err=exit_on_err,
                                 app_obj=app_obj, env_vars={**os.environ, **env_vars}, err_redirect=subprocess.PIPE)

    if log_files := sh_logs(log_enable_dir=log_enable_dir, log_name_prefix='git'):
        sh_log(command_line, extra_args=extra_args, cl_err=cl_err, output_lines=output_lines, log_file_paths=log_files)

    if cl_err:  # if cl_err and exit_on_err then it would have exit the Python interpreter (so never would run to here)
        cmd_line = mask_token([command_line] + list(extra_args))
        debug_out(f"    # ignored error {cl_err} of `{cmd_line}` and git trace {env_vars=}")
        output_lines.insert(0, EXEC_GIT_ERR_PREFIX + str(cl_err) + f" in {cmd_line}")

    start = next((_idx for _idx, _item in enumerate(output_lines) if _item == STDERR_BEG_MARKER), -1)  # lines.find()
    if start >= 0:
        if git_debug or any(os.environ.get(_, "0") in ("true", "1", "2") for _ in git_trace_vars):
            sep = " " * 6
            print_out(sep + "git trace output:")
            for line_no in range(start + 1, len(output_lines) - 1):
                print_out(sep + output_lines[line_no])
        output_lines[:] = output_lines[:start]      # remove stderr messages from returned console output

    return mask_token(output_lines)


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def sh_log(comment_or_command: str, extra_args: Iterable[str] = (), cl_err: int = 0, output_lines: Iterable[str] = (),
           log_file_paths: Iterable[str] = (), log_name_prefix: str = ""):
    """ append a log entry to each existing/enabled shell command log file.

    :param comment_or_command:  command line or comment line (if starts with the # character).
    :param extra_args:          extra arguments (added to the command line).
    :param cl_err:              command exit code.
    :param output_lines:        console output lines.
    :param log_file_paths:      log file paths - if specified then the search of the default locations for log files
                                will be skipped and therefore :paramref:`.log_name_prefix` will be ignored.
    :param log_name_prefix:     log file name prefix. extended with the :data:`SHELL_LOG_FILE_NAME_SUFFIX` results in
                                the file name to search for (and to log into if exists).
    """
    if not comment_or_command.startswith("#"):
        comment_or_command = " > " + comment_or_command

    sep = os.linesep
    log_lines = (now_str(sep='-') + sep +
                 comment_or_command + " " + " ".join('"' + _ + '"' if " " in _ else _ for _ in extra_args) + sep +
                 (f" * {cl_err=}" + sep if cl_err else "") +
                 ("   " + (sep + "   ").join(output_lines) + sep if output_lines else ""))

    log_lines = mask_token(log_lines)

    for log_path in log_file_paths or sh_logs(log_name_prefix=log_name_prefix):
        extend_file(log_path, log_lines)


def sh_logs(log_enable_dir: str = "", log_name_prefix: str = "") -> list[str]:
    """ determine paths of the existing/enabled shell command log files, optionally enabling/creating a new log file.

    :param log_enable_dir:      specify the directory/folder path in which to enable shell command logging, by creating
                                a new log file (and the folder) if they not exist. valid folder paths are
                                either the CWD where the shell command get executed (e.g. the project root folder)
                                or the users home directory (~).
    :param log_name_prefix:     log file name prefix. extended with the :data:`SHELL_LOG_FILE_NAME_SUFFIX` results in
                                the file name to search for (and to log into if exists).
    :return:                    list of existing/enabled shell log file name paths.
    """
    file_name = log_name_prefix + SHELL_LOG_FILE_NAME_SUFFIX
    log_files = []

    if os_path_isfile(file_name):
        log_files.append(norm_path(file_name))
    if os_path_isfile(file_path := norm_path(os_path_join("~", file_name))):
        log_files.append(file_path)

    if log_enable_dir:
        file_path = norm_path(os_path_join(log_enable_dir, file_name))
        if file_path not in log_files:
            log_files.append(file_path)
        if not os_path_isfile(file_path):
            write_file(file_path, f"# enabled shell command logging into {file_path}{os.linesep}", make_dirs=True)

    return log_files


def venv_bin_path(venv_id: str) -> str:
    """ determine the absolute bin/executables folder path of the specified, local or active Python virtual environment.

    :param venv_id:             name/id of the VENV or the name of a project-local VENV sub
                                folder (with a trailing slash).
    :return:                    absolute path of the bin/Scripts folder of the specified/determined virtual environment
                                or an empty string if no VENV could be found with the specified/determined id/name.

                                .. note::
                                    under Windows/win32 the base name of the returned path is 'Scripts' (not 'bin'), and
                                    some executables may have a file extension (e.g., activate.bat and python.exe).
                                    ensures "/" path separators to work properly in WSL/bash-emulation under MS Windows.
    """
    bin_dir = 'Scripts' if sys.platform == 'win32' else 'bin'
    chk_dirs = venv_check_prefixes(venv_id)

    for path_parts in chk_dirs:
        bin_path = os_path_join(*path_parts, bin_dir)
        if os_path_isdir(bin_path):
            return norm_path(bin_path)

    return ""


def venv_check_prefixes(venv_id: str) -> list[tuple[str, ...]]:
    """ determine the possible VENV root/prefix paths of all the supported VENV systems.

    :param venv_id:             name/id of the VENV or the name of a project-local VENV sub
                                folder (with a trailing slash).
    :return:                    list of joinable path parts of the possible and supported VENV root/prefix paths.
    """
    chk_dirs: list[tuple[str, ...]] = []

    if (env_root := venv_prefix()) and os_path_basename(env_root) == venv_id:
        chk_dirs.append((env_root, ))                                           # root from VIRTUAL_ENV/CONDA_PREFIX

    if env_root := os.getenv('PYENV_ROOT'):
        chk_dirs.append((env_root, 'versions', venv_id))                        # pyenv ==os_path_expanduser('~/.pyenv')

    if env_root := os.getenv('WORKON_HOME'):
        chk_dirs.append((env_root, venv_id))                                    # virtualenvwrapper

    if env_root := os.getenv('CONDA_ROOT'):
        chk_dirs.append((env_root, 'envs', venv_id))                            # Conda =='~/miniconda3'
    if env_root := os.getenv('CONDA_ENVS_PATH'):
        chk_dirs.append((env_root, venv_id))                                    # explicit Conda envs dir
    if env_root := os.getenv('CONDA_PREFIX'):
        chk_dirs.append((env_root, venv_id))                                    # derive envs-root from active env
    chk_dirs.append((os_path_expanduser('~/.conda/envs'), venv_id))
    chk_dirs.append((os_path_expanduser('~/anaconda3/envs'), venv_id))
    chk_dirs.append((os_path_expanduser('~/miniconda3/envs'), venv_id))
    env_root = os.getenv('CONDA_ROOT') or os.getenv('CONDA_PREFIX')
    if env_root and venv_id in ('anaconda3', 'base', 'miniconda3', os.getenv('CONDA_DEFAULT_ENV')):
        if os_path_basename(os_path_dirname(env_root)) == 'envs':
            env_root = os_path_dirname(os_path_dirname(env_root))   # climb to back to root from envs/<venv_id> folder
        chk_dirs.append((env_root, ))

    cache_dir = (os.path.expandvars('%APPDATA%/pypoetry/virtualenvs') if sys.platform == 'win32' else
                 os_path_expanduser('~/.cache/pypoetry/virtualenvs'))
    for path_part in path_folders(os_path_join(cache_dir, venv_id + '*')):
        chk_dirs.append((path_part, ))  # poetry VENVs get a hash suffix on the VENV id, e.g. "<name>-XXXXXXXX-py3.11"

    for path_part in ((venv_id + "/", ) if venv_id else ()) + VENV_SUB_DIR_NAMES:
        for _ in range(VENV_ID_SEARCH_DEPTH):
            chk_dirs.append((path_part, ))               # last fallback: project-local .venv/virtualenv folders
            path_part = os_path_join("..", path_part)

    return chk_dirs


def venv_module_var_val(import_name: str, var_name: str, cwd: str = ".", venv_id: str = "",
                        validator: Callable[[Any], bool] = lambda _: True) -> Any | UnsetType | None:
    """ determine a variable value that is declared in a Python module in any other VENV.

    :param import_name:         import-/dot-name of the module to get the variable value from.
    :param var_name:            name of the variable declared within the module. the value of the variable has to be
                                parsable by :func:`ast.literal_eval`.
    :param cwd:                 the CWD to set for the Python interpreter of the VENV to run.
    :param venv_id:             the name/id of the Python virtual environment to use. using the VENV of the
                                current working directory or :paramref:`.cwd`, if not specified.
    :param validator:           callable called for each line of the console output, with the variable value as
                                argument, returning True if the variable value is correct. useful if command line output
                                may contain extra prefixes/lines (e.g. warnings), that have to be skipped/ignored.
    :return:                    module variable value (parseable by :func:`ast.literal_eval`), or
                                `UNSET` on error, if the module got not found or if the module variable doesn't exist.

    .. note:: the PyPI package/project :mod:`ae.system` has to be installed in the used/destination VENV.
    """
    code = f"from ae.system import module_attr; print(module_attr('{import_name}', '{var_name}'))"
    output: list[str] = []
    with in_prj_dir_venv(project_path=cwd, venv_id=venv_id):
        sh_exit_if_exec_err(324, f'python -c "{code}"', output_lines=output, err_redirect=None)

    for line in output:
        try:
            val = literal_eval(line)
            if validator(val):
                return val
        except SyntaxError:
            pass    # ignoring errors and warnings like "__init__() called too early; no main app instance"

    return UNSET


def venv_name(project_path: str = ".") -> str:
    """ determine the name/id of the current VENV used by a project.

    :param project_path:        path to the project root folder; assuming and using the actual CWD if not specified.
    :return:                    the determined VENV name/id or an empty string if no VENV got found or is active.
                                the VENV name/id will be determined either from the first line of a local
                                ``.python-version`` file, or from an existing and allowed subfolder name
                                (:data:`VENV_SUB_DIR_NAMES` contains the commonly used ones) of a project-local
                                VENV. the search starts in the specified project path (or the CWD) and goes up
                                until 2 parent directories above it. if it did not find any there, then the
                                name of the currently active VENV (determined via the
                                function :func:`ae.system.os_env_venv`) will be returned.
    """
    for _ in range(VENV_ID_SEARCH_DEPTH):
        env_file = os_path_join(project_path, '.python-version')    # pyenv or any other VENV
        if os_path_isfile(env_file):
            venv_id = read_file(env_file).splitlines()[0].strip()
            if venv_id:
                break

        for venv_id in VENV_SUB_DIR_NAMES:
            if os_path_isdir(os_path_join(project_path, venv_id)):
                break
        else:
            project_path = os_path_join("..", project_path)
            continue
        break

    else:
        venv_id = os_env_venv()

    return venv_id


def venv_os_env_vars(venv_id: str, app_obj: ConsoleApp | UnsetType | None = None) -> dict[str, str]:
    """ return the OS env vars of the Python virtual environment specified by their VENV id.

    :param venv_id:             the id/name of the Python virtual environment (VENV) get the OS env vars for.
    :param app_obj:             optional :class:`~ae.console.ConsoleApp` instance, used for logging/console output.
    :return:                    dict with the OS environment variable values of the specified or currently set VENV
                                or an empty dict if the requested or no VENV was active, or if VENV is not supported.
    """
    bin_path = venv_bin_path(venv_id)
    if app_obj is None:
        app_obj = cast(ConsoleApp, main_app_instance())  # for console outputs / :meth:`ae.console.ConsoleApp.chk`-calls
    debug_out = dummy_function if app_obj is UNSET else app_obj.vpo if isinstance(app_obj, ConsoleApp) else print

    if not bin_path:
        debug_out(f"    * the {venv_id=} does not exist ({os_env_venv()=} {os.getcwd()=})")
        return {}

    exec_kwargs = venv_sh_exec_kwargs(bin_path, app_obj=app_obj)
    if not exec_kwargs:
        debug_out(f"    # empty sh_exec-kwargs to set OS-env-vars of {venv_id=} ({os_env_venv()=} {bin_path=})")
        return {}

    debug_out(f"    - setting {venv_id=} in OS env vars ({os_env_venv()=} {os.getcwd()=} {bin_path=} {exec_kwargs=})")

    output: list[str] = []    # inspired by Aundre's answer in https://stackoverflow.com/questions/7040592
    sh_exit_if_exec_err(323, "", **exec_kwargs, output_lines=output, err_redirect=subprocess.PIPE)

    if not output:
        debug_out(f"    # {venv_id=}-specific OS env vars not found ({os_env_venv()=} {bin_path=} {exec_kwargs=})")
        return {}

    env_var_lines = [line.strip() for line in output]
    return dict(line.split("=", maxsplit=1) for line in env_var_lines
                if "=" in line and not line.startswith("="))


def venv_sh_exec_kwargs(bin_path: str, app_obj: AppBase | UnsetType | None = None) -> dict[str, Any]:
    """ determine the kwargs to be passed onto a call of :func:`ae.sh_exec` to set OS-env vars of a VENV.

    :param bin_path:            the `bin`/`Scripts` folder path of the VENV.
    :param app_obj:             optional :class:`~ae.core.AppBase` instance, used for logging/console output.
    :return:                    OS- and VENV-specific command line and extra args to be passed to :func:`ae.sh_exec`
                                in order to set the VENV-specific OS-environment variables.
    """
    env_root = os_path_dirname(bin_path)
    print_out = dummy_function if app_obj is UNSET else app_obj.po if isinstance(app_obj, AppBase) else print
    debug_out = dummy_function if app_obj is UNSET else app_obj.vpo if isinstance(app_obj, AppBase) else print
    exec_kwargs: dict[str, Any] = {'app_obj': app_obj}
    is_conda = os_path_isdir(os_path_join(env_root, 'conda-meta'))

    if sys.platform == 'win32':
        if is_conda:
            activate_path = os_path_join(env_root, 'condabin', 'conda.bat')
            activate_cmd = f"{shlex.quote(activate_path)} activate {shlex.quote(env_root)}"
        else:
            activate_path = activate_cmd = os_path_join(bin_path, 'activate.bat')
        activate_cmd = f"cmd /c {shlex.quote(activate_cmd)} && set"

    else:
        sh_cmd = '/bin/sh' if os_path_isfile('/bin/sh') else 'bash'
        exec_kwargs['decoder_splitter'] = output_zero_split
        if is_conda:
            activate_path = ""
            activate_cmd = f'eval "$(conda shell.posix hook)" && conda activate {shlex.quote(env_root)}'
            exec_kwargs['shell'] = True  # shell=True because shell function `conda activate` is defined by the eval cmd
        else:
            activate_path = os_path_join(bin_path, 'activate')
            activate_cmd = f"source {shlex.quote(activate_path)}"
        activate_cmd = f"env -i {sh_cmd} -c 'set -a && {activate_cmd} && env -0'"

    exec_kwargs['extra_args'] = shlex.split(activate_cmd)
    debug_out(f"    = venv_sh_exec_kwargs() compiled the {exec_kwargs=} for VENV in {bin_path=}")

    if activate_path and not os_path_isfile(activate_path):
        print_out(f"    * activation script path '{activate_path}' not found for VENV in {bin_path=}")
        return {}

    return exec_kwargs
