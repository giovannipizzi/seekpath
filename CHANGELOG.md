# v2.2.1
* DevOps: Fix readthedocs configuration, update pre-commit configuration and transfer repo to the materialscloud-org organization

# v2.2.0
* DevOps: Replaced `setup.py` by `pyproject.toml`, updated README and fixed CI [710fd75](https://github.com/giovannipizzi/seekpath/commit/710fd7542a307adef3a18154860b298131284499)
* DevOps: Update CI and pre-commit (e.g., black to ruff, enable prospector again) [9ca3dd9](https://github.com/giovannipizzi/seekpath/commit/9ca3dd9cd9f10735db49b05b0ba468ab2558c792)
* Improve `spglib` version check [d910bb3](https://github.com/giovannipizzi/seekpath/commit/d910bb372139d642ef008931c7f39adf705faaa9)
* Refactor `get_BZ` and implement it as the `BZ` class [b056ae2](https://github.com/giovannipizzi/seekpath/commit/b056ae24a9cf0cd60bb1fd05d6298a019de1ec0a)
* Handle `spglib` DeprecationWarning [2bdcc05](https://github.com/giovannipizzi/seekpath/pull/105/commits/2bdcc052b20e41b51e663022854239c4998e9163)



# v2.1.0
* More recent Python version [154e681](https://github.com/giovannipizzi/seekpath/commit/154e681125f28074475415c78e4b99c51cb3aa02)
* `k path` for the original cell without standardization [1739078](https://github.com/giovannipizzi/seekpath/commit/1739078c4531a7bd1fe695a39d7b88629661ce48)


# v2.0.0
- Dropped python 2 support
- Moved out the web tool to [tools-seekpath](https://github.com/materialscloud-org/tools-seekpath), based on [tools-barebone](https://github.com/materialscloud-org/tools-barebone), whose codebases mostly take inspiration from the web tool implemented in seekpath v1.x

# v1.x
First versions of seekpath, supportinb both python 2 an python 3, and providing a web tool to interactively inspect the results of seekpath (hosted on the [Materials Cloud tools section](http://www.materialscloud.org/tools/seekpath/)).
