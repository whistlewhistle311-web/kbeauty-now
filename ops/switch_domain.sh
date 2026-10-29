#!/bin/sh
# One-time move from whistlewhistle311-web.github.io/kbeauty-now/ to the custom domain.
# GitHub keeps redirecting the old github.io URLs (same paths) to the custom domain, so old pins and posts keep working.
set -e
NEW=koreanbeautynow.com
OLD=whistlewhistle311-web.github.io/kbeauty-now
cd "$(dirname "$0")/.."
sed -i "s#https://$OLD/#https://$NEW/#g" build.py pin_post.py
sed -i "s#\\\\\"host\\\\\":\\\\\"whistlewhistle311-web.github.io\\\\\"#\\\\\"host\\\\\":\\\\\"$NEW\\\\\"#; s#https://$OLD/#https://$NEW/#g" .github/workflows/daily.yml
echo "$NEW" > docs/CNAME
grep -rn "$OLD" build.py pin_post.py .github/workflows/daily.yml || echo "no old base left"
