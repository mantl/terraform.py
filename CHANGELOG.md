0.4.4 (unreleased)
------------------

- Nothing changed yet.


0.4.3 (2017-05-12)
------------------

- Merge scaleway updates into new version


0.4.2 (2017-04-24)
------------------

- add ability to include an ssh key via tags.sshPrivateKey. this may be relative to where ansible is called from.

- switch from manually fetcing remote state to using "terraform state pull". To retain old behavior, use "--noterraform"


0.4.1 (2017-04-07)
------------------

- Removed python3 type hints. Moving back to python2 because of a pipsi
    bug.


0.4.0 (2017-04-07)
------------------
