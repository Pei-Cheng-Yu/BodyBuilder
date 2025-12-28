# Development Workflow & Collaboration Guidelines

## 1. Overview
We use a **Pull Request (PR)** workflow. Developers work on isolated feature branches, submit a PR, undergo code review, and then merge into the `main` branch.
*Note: GitHub's "Pull Request" is equivalent to GitLab's "Merge Request".*

## 2. Repository Rules
*   **Protected Main**: Direct pushes to `main` are prohibited. All changes must go through a PR.
*   **No Force Push**: Never force push to `main` to preserve history.

## 3. Creating a Pull Request

### Option A: Local Development (CLI)
1.  **Setup**: Ensure SSH keys are added to GitHub. Clone the repo:
    ```bash
    git clone <repo_url>
    cd <project_folder>
    ```
2.  **Branching**: Always sync with main before starting:
    ```bash
    git checkout main
    git pull origin main
    git checkout -b <feature-branch-name>
    ```
3.  **Commit**:
    *   Use `git status` and `git diff` to verify changes.
    *   Keep commits atomic (one feature/fix per commit).
    *   Test locally before committing.
    *   `git commit -m "Your message"`
4.  **Push**:
    ```bash
    git push origin <feature-branch-name>
    ```
5.  **Open PR**: Click the link generated in the terminal or go to "Pull requests" > "New pull request" in GitHub.

### Option B: Web Editor (Small Fixes)
1.  Navigate to the file in GitHub.
2.  Click the **Edit** (pencil icon) button.
3.  Make changes, select "Create a **new branch** for this commit and start a pull request", then click **Propose changes**.

## 4. Best Practices for PRs
*   **Atomic Scope**: A PR should focus on **one** specific goal (e.g., "Add InBody parsing" OR "Fix typo", not both).
*   **Size**: Keep changes minimal to make the review process easier.
*   **Titles**: Be descriptive (e.g., `feat: add skeletal_muscle_mass to profile schema`).
*   **Descriptions**:
    *   Explain *what* and *why*.
    *   Link issues: Use `#123` to link or `Closes #123` to auto-close issues upon merging.
    *   Use `Draft:` prefix in the title if work is in progress.

## 5. Code Review
Every PR requires at least one approval.

### Reviewer Responsibilities
1.  **Check Code**: Look for logic errors, bugs, and coding style issues in the "Changes" tab.
2.  **Local Testing**:
    *   Fetch the branch: `git fetch origin <branch_name>`
    *   Checkout: `git checkout <branch_name>`
    *   **Verify**: Check if the feature works, DB migrations run correctly, and no regressions occur.
    *   **Environment**: Check if `requirements.txt` or `.env` examples need updates.
3.  **Feedback**: Leave comments on specific lines. Resolve threads once fixed.

### Approval
*   **Standard**: Wait for a reviewer to approve.
*   **Trivial Fixes**: For minor changes (e.g., typos), you may self-approve and merge after notifying the team.

## 6. Handling Conflicts
If a merge conflict occurs:
1.  **GitHub UI**: Use the "Resolve conflicts" button for simple text conflicts.
2.  **Local Resolution**:
    ```bash
    git checkout <your-branch>
    git pull origin main  # or git rebase main
    # Fix conflicts in editor
    git add .
    git commit
    git push origin <your-branch>
    ```

---
*Reference: Resolving Merge Conflicts*
