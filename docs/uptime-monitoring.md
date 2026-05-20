# Uptime Monitoring

## Recommended: UptimeRobot (Free Tier)

1. Sign up at https://uptimerobot.com
2. Add a new monitor:
   - **Monitor Type**: HTTP(S)
   - **Friendly Name**: History News
   - **URL**: `https://red-stone-0ed2b5d10.7.azurestaticapps.net/`
   - **Monitoring Interval**: 5 minutes
3. Add alert contacts (email, Slack, webhook)
4. Optionally add a second monitor for `/articles/` to verify content pages

## Alternative: GitHub Actions Cron Check

The daily cron rebuild (`0 5 * * *` UTC) already in our workflow acts as a basic
health check — if the build or deploy fails, the `notify_on_failure` job creates a
GitHub issue automatically.

## Monitoring Checklist

- [ ] Homepage returns 200
- [ ] `/articles/` returns 200
- [ ] `/sitemap.xml` returns 200
- [ ] SSL certificate is valid
- [ ] Response time < 2 seconds
