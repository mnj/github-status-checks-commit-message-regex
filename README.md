# github-status-checks-commit-message-regex

A simple python scripts, that checks if the commit message in the pull request matches a defined regex pattern

Just requires a plain Github workflow to run, on ubuntu-latest (or anything that has python3)

There is a few options you can specify:
| Input                 | Description                                                   | Required? | Default |
|-----------------------|---------------------------------------------------------------|-----------|---------|
| pattern               | The regex pattern to use, to check for a valid commit message | Yes       | N/A     |
| check_commit_title    | Check for the pattern in the commit title (first line)        | No        | false   |
| check_commit_body     | Check for thee pattern in the rest of the commit message      | No        | false   |
| check_commit_message  | Check for the pattern in the full commit message (title+body) | No        | true    |
| check_all_commits     | Check all individual commit message in the pull request       | No        | false   |
| github_token          | The GITHUB_TOKEN to use for authenticating to github          | No        | N/A     |

Using check_all_commits, requires you to pass the {{ secrets.GITHUB_TOKEN }}, so it has access to all the commits in the pull request

## Example status check Github Action workflow simple
```yml
name: Check commit message
on: [pull_request]

jobs:
  check-commit-message:
  name: Check commit message
  runs-on: ubuntu-latest
  steps:
    - name: Check commit message
      uses: mnj/github-status-checks-commit-message-regex@v2.1
      with:
        pattern: '([A-Z][A-Z0-9]+-[0-9]+)' # Match all upper casee Jira ticket ids
```

## Example status check Github Action workflow, full example
```yml
name: Check commit message
on: [pull_request]

jobs:
  check-commit-message:
  name: Check commit message
  runs-on: ubuntu-latest
  steps:
    - name: Check commit message
      uses: mnj/github-status-checks-commit-message-regex@v2.1
      with:
        pattern: '([A-Z][A-Z0-9]+-[0-9]+)' # Match all upper casee Jira ticket ids
        check_commit_title: 'false'
        check_commit_body: 'false'
        check_commit_message: 'true'
        check_all_commits: 'true'

        github_token: ${{ secrets.GITHUB_TOKEN }}
```

## License

This project is released under the terms of the [MIT License](LICENSE)
