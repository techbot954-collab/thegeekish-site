# Geekish Meta Autopost

This posts one unposted Geekish website story to Facebook and Instagram each time it runs.

## Required Meta Setup

Create a long-lived Meta access token with publishing access for the Facebook Page and connected Instagram professional account.

Environment variables:

```sh
export META_ACCESS_TOKEN="your-long-lived-token"
export META_PAGE_ID="your-facebook-page-id"
export META_IG_USER_ID="your-instagram-business-or-creator-id"
```

Optional:

```sh
export GEEKISH_SITE_URL="https://thegeekish.com"
export META_AUTOPOST_STATE="/root/.openclaw/workspace/geekish-site/.meta-autopost-state.json"
```

## Test

```sh
cd /root/.openclaw/workspace/geekish-site
scripts/meta_autopost.py --dry-run
```

## Run Hourly

Add this to cron after the Meta environment variables are available to the job:

```cron
0 * * * * cd /root/.openclaw/workspace/geekish-site && /usr/bin/env bash -lc 'source /root/.openclaw/workspace/geekish-site/.meta-autopost.env && scripts/meta_autopost.py >> /root/.openclaw/workspace/geekish-site/meta-autopost.log 2>&1'
```

The script records posted slugs in `.meta-autopost-state.json` so it does not repost the same article every hour.
