# Git and GitHub

Git saves versions in the local folder. GitHub hosts a copy of the repository. A **commit** saves a snapshot locally. A **push** sends commits to GitHub. The usual name for the GitHub connection is `origin`.

## First push

Create an empty repository named `self-healing-llm-gateway` in your GitHub account. Leave the GitHub README, license, and gitignore options unchecked so the local files become the first commit.

From the project folder, set the author identity for this repository. Replace the placeholders. GitHub shows your exact no-reply address under **Settings → Emails**.

```powershell
git config --local user.name "YOUR DISPLAY NAME"
git config --local user.email "YOUR GITHUB NO-REPLY EMAIL"
git add .
git diff --cached --stat
git commit -m "Scaffold the LLM gateway"
git remote add origin https://github.com/YOUR-USERNAME/self-healing-llm-gateway.git
git push -u origin main
```

## Daily practice

Make one small improvement you can explain. It can be a test, a bug fix, or a note about an experiment. Run `git status` and `git diff` to see what changed, stage the files you intend to save with `git add`, then commit and push.

GitHub attributes commits using the author email. Push to the repository's default branch, or merge your changes into it. You can show anonymized private activity on your profile through the private contributions setting.

- [GitHub contribution criteria](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference)
- [Private contribution settings](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings)
