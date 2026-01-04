# THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.project_tpls v0.3.71
""" setup of aedev namespace module portion commands: software development operation commands helpers. """
import sys
# noinspection PyUnresolvedReferences
import pathlib
# noinspection PyUnresolvedReferences
import setuptools


print("SetUp " + __name__ + ": " + sys.executable + str(sys.argv) + f" {sys.path=}")

setup_kwargs = {
    'author': 'AndiEcker',
    'author_email': 'aecker2@gmail.com',
    'classifiers': [
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Typing :: Typed',
    ],
    'description': 'aedev namespace module portion commands: software development operation commands helpers',
    'extras_require': {
        'dev': [
            'aedev_project_tpls',
            'aedev_aedev',
            'anybadge',
            'coverage-badge',
            'flake8',
            'mypy',
            'pylint',
            'pytest',
            'pytest-cov',
            'pytest-django',
            'typing',
            'types-setuptools',
        ],
        'docs': [],
        'tests': [
            'anybadge',
            'coverage-badge',
            'flake8',
            'mypy',
            'pylint',
            'pytest',
            'pytest-cov',
            'pytest-django',
            'typing',
            'types-setuptools',
        ],
    },
    'install_requires': [
        'ae_base',
        'ae_core',
        'ae_console',
        'ae_shell',
        'aedev_base',
    ],
    'keywords': [
        'configuration',
        'development',
        'environment',
        'productivity',
    ],
    'license': 'GPL-3.0-or-later',
    'long_description': (pathlib.Path(__file__).parent / 'README.md').read_text(encoding='utf-8'),
    'long_description_content_type': 'text/markdown',
    'name': 'aedev_commands',
    'package_data': {
        '': [],
    },
    'packages': [
        'aedev',
    ],
    'project_urls': {
        'Bug Tracker': 'https://gitlab.com/aedev-group/aedev_commands/-/issues',
        'Documentation': 'https://aedev.readthedocs.io/en/latest/_autosummary/aedev.commands.html',
        'Repository': 'https://gitlab.com/aedev-group/aedev_commands',
        'Source': 'https://aedev.readthedocs.io/en/latest/_modules/aedev/commands.html',
    },
    'python_requires': '>=3.12',
    'url': 'https://gitlab.com/aedev-group/aedev_commands',
    'version': '0.3.6',
    'zip_safe': True,
}

if __name__ == "__main__":
    setuptools.setup(**setup_kwargs)
    pass
