# Staging Environment

Azure Static Web Apps **automatically** creates staging preview environments for pull requests.

## How it works

1. Push a branch: `git checkout -b feature/my-change && git push origin feature/my-change`
2. Open a PR against `master`
3. Azure SWA deploys a preview environment and posts the URL in the PR comments
4. Preview URL format: `https://red-stone-0ed2b5d10-<number>.westus2.7.azurestaticapps.net/`
5. The preview is deleted when the PR is closed (handled by `close_pull_request_job`)

## Configuration

Already configured in `.github/workflows/azure-static-web-apps-red-stone-0ed2b5d10.yml`:
- `pull_request: [opened, synchronize, reopened, closed]` triggers PR previews
- `close_pull_request_job` cleans up previews when PRs close

## Usage

```bash
# Create a staging branch
git checkout -b staging/new-articles
# Make changes...
git push origin staging/new-articles
# Open PR → get preview URL → review → merge
```

No additional configuration needed — this is a built-in Azure SWA feature.
