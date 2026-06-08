# Security Policy

## Supported Versions

Security fixes are applied to the latest released version. Older versions are not actively patched.

| Version | Supported          |
|---------|--------------------|
| V3.1    | :white_check_mark: Yes |
| < V3.1  | :x: No             |

## Reporting a Vulnerability

If you discover a security vulnerability in **Pipeline Visualization Tools**, please report it privately so we can address it before public disclosure.

**Please do NOT open a public GitHub issue for security vulnerabilities.**

### How to report

Send an email to: **a185531353@qq.com**

Include the following in your report:

1. A clear description of the vulnerability and its impact.
2. Steps to reproduce, ideally with a minimal sample XML/JSON file.
3. The affected version (e.g. `V3.1`).
4. Your environment (OS, Python version).
5. Any known workarounds, if applicable.

### What to expect

- **Acknowledgement** within **7 days** of your report.
- An initial assessment within **14 days**.
- Coordinated disclosure: we will work with you to determine a reasonable disclosure timeline. We aim to ship a fix before the issue is made public.
- Credit in the release notes / `CHANGELOG.md` (unless you prefer to remain anonymous).

## Scope

The following are in scope:

- Code execution or file-system access triggered by a crafted XML or JSON pipeline file.
- Path traversal, XML External Entity (XXE), or unsafe deserialization in the parsers under `UseCase.py`.
- Unsafe handling of user-supplied paths when saving edited JSON files.
- Vulnerabilities in the bundled PyInstaller build process or installer.

The following are **out of scope**:

- Bugs that require local code execution by an attacker who already has user-level access to the machine.
- Issues in third-party dependencies (please report upstream to PyQt5, `json5`, `networkx`, etc.).
- Best-practice suggestions without a concrete exploit.

## Security Notes for Users

- The application does not perform network requests; pipeline files are processed entirely locally.
- Always back up your JSON pipeline file before using **Edit Mode** and **Save**, as the save process strips JSON5 comments.
- Only open pipeline files from sources you trust — XML/JSON parsers have historically been a common source of CVEs in similar tools.

## Acknowledgements

We appreciate responsible disclosure and the security research community's help in keeping this project safe for everyone.
