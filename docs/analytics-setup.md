# Analytics Setup

## Recommended: Plausible Analytics (Privacy-Friendly)

Plausible is GDPR-compliant, lightweight (< 1KB), and doesn't require cookie banners.

### Setup

1. Sign up at https://plausible.io (free 30-day trial, then $9/month or self-host free)
2. Add your site domain
3. Add the script tag to `layouts/_default/baseof.html` before `</head>`:

```html
{{ if hugo.IsProduction }}
<script defer data-domain="red-stone-0ed2b5d10.7.azurestaticapps.net" src="https://plausible.io/js/script.js"></script>
{{ end }}
```

The `hugo.IsProduction` guard ensures analytics only loads in production, not during local development.

## Alternative: Umami (Self-Hosted, Free)

1. Deploy Umami to Azure App Service or Vercel
2. Add tracking script similar to Plausible above
3. Dashboard at your own domain

## Alternative: Azure Application Insights (Free Tier)

1. Create an Application Insights resource in Azure Portal
2. Copy the connection string
3. Add the snippet to baseof.html (heavier JavaScript payload ~30KB)

## What to Track

- Page views by article (which topics are popular?)
- Referral sources (where do readers come from?)
- Top pages (homepage vs. individual articles)
- Geographic distribution
- Device types (mobile vs. desktop)
