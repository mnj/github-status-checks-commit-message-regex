# github-status-checks-commit-message-regex

A simple python scripts, that checks if the commit message in the pull request matches a defined regex pattern

Just requires a plain Github workflow to run, on ubuntu-latest (or anything that has python3)

## Example status check Github Action workflow
```yml
name: Check commit message
on: [pull_request]

jobs:
  check-commit-message:
  name: Check commit message
  runs-on: ubuntu-latest
  steps:
    - name: Check commit message
      uses: mnj/github-status-checks-commit-message-regex@v1
      with:
        pattern: '([A-Z][A-Z0-9]+-[0-9]+)' # Match all upper casee Jira ticket ids
```

## License

This project is released under the terms of the [MIT License](LICENSE)
