# Development

To start development you should begin by cloning the repo.

```bash
$ git clone https://github.com/artemistomaras/django-ethereum-events.git
```


# Pull Requests

In general, pull requests are welcome.  Please try to adhere to the following.

- code should conform to PEP8 and as well as the linting done by flake8
- include tests.
- include any relevant documentation updates.

It's a good idea to make pull requests early on.  A pull request represents the
start of a discussion, and doesn't necessarily need to be the final, finished
submission.

GitHub's documentation for working on pull requests is [available here](https://help.github.com/articles/creating-a-pull-request/).

Always run the tests before submitting pull requests, and ideally run `tox` in
order to check that your modifications don't break anything.

Once you've made a pull request take a look at the travis build status in the
GitHub interface and make sure the tests are runnning as you'd expect.