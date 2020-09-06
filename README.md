# PEP 621 Dependency Specification: TOML Proposal Library

This is a library demonstrating loading proposed TOML dependency specification from and to 
[PEP 508](https://www.python.org/dev/peps/pep-0508/) strings for [PEP 621](https://www.python.org/dev/peps/pep-0621).

The library also implements a sample dataclass based instances with validation for dependency specifications. As an 
additional example, this also makes use of [lark-parser](https://github.com/lark-parser/lark) to parse a provided PEP 508
string. 

This is not supported code, this is put together for demonstration purposes only.

## Example Usage
### From PEP 508 to TOML
```console
$ python -m pep621_project_dependencies -f toml "sphinx @ git+ssh://git@github.com/sphinx-doc/sphinx.git@master"
[project.dependencies]
sphinx = { url = "git+ssh://git@github.com/sphinx-doc/sphinx.git@master" }

[project.optional-dependencies]

$ python -m pep621_project_dependencies -f toml "sphinx @ git+ssh://git@github.com/sphinx-doc/sphinx.git@master ; extra == 'doc'"
[project.dependencies]

[project.optional-dependencies.doc]
sphinx = { url = "git+ssh://git@github.com/sphinx-doc/sphinx.git@master" }
```

### From TOML to PEP 508
```console
$ python -m pep621_project_dependencies -f pep508 tests/fixtures/complete.toml 
flask
numpy (~=1.18)
pycowsay (==0.0.0.1)
sphinx @ git+ssh://git@github.com/sphinx-doc/sphinx.git@master
pip @ https://github.com/pypa/pip/archive/1.3.1.zip#sha1=da9234ee9982d4bbb3c72346a6de940a148ea686
docker[ssh] (>= 4.2.2, < 5)
requests[security,tests] (>= 2.8.1, == 2.8.*) ; python_version < '2.7'
backports.shutil_get_terminal_size (== 1.0.0) ; python_version < '3.3'
backports.ssl_match_hostname (>= 3.5, < 4) ; python_version < '3.5'
colorama (>= 0.4, < 1) ; sys_platform == 'win32'
enum34 (>= 1.0.4, < 2) ; python_version < '3.4'
keyring (>=18.0.1, <18.1.0) ; python_version ~= '2.7'
keyring (>=20.0.1, <21.0.0) ; python_version ~= '3.5'
keyring (>=21.2.0) ; python_version >= '3.6'
PySocks (>= 1.5.6, != 1.5.7, < 2) ; extra == 'socks'
ddt (>= 1.2.2, < 2) ; extra == 'tests'
pytest (<6) ; python_version < '3.5' and extra == 'tests'
pytest (>=6) ; python_version >= '3.5' and extra == 'tests'
mock (>= 1.0.1, < 4) ; python_version < '3.4' and extra == 'tests'
```