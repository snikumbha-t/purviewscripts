Contributing to purviewscripts

Thanks for your interest. A few guidelines when contributing:

- Do not add secrets to the repository. Use environment variables or a
  secrets management service locally.
- If you add scripts that require credentials, document the required
  environment variables and add an example `.env.example` if helpful.
- Keep CSV test data out of version control. If you must include sample
  CSVs, ensure they contain only dummy data or headers.
- Run tests or smoke checks before opening a pull request.
- When in doubt, open an issue describing what you want to change and
  ask for review.
