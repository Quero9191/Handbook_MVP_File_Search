---
title: "UTM Tracking Best Practices"
description: "How to use UTM parameters to track campaign performance and attribute conversions"
department: "growth"
doc_type: "guide"
owner_team: "Growth & Marketing"
maintainer: "Growth Lead"
visibility: "internal"
keywords: ["utm", "tracking", "analytics", "campaigns", "attribution"]
last_updated: "2025-12-17"
---

## Purpose
UTM parameters let us track where traffic comes from and measure campaign ROI. This guide ensures consistent tagging.

## Scope
- Applies to: All marketing campaigns (email, paid ads, social, partnerships)
- Doesn't apply to: Organic website traffic, internal links

## UTM Parameters Explained

### Basic 4 (Required)
- **utm_source**: Platform or channel (email, twitter, linkedin, google_ads, partner_site)
- **utm_medium**: Type of traffic (email, cpc, cpm, organic, referral)
- **utm_campaign**: Campaign identifier (holiday_sale_2025, webinar_dec, product_launch)
- **utm_content**: Ad variant or version (blue_button_v1, headline_a, discount_10pct)

### Building a URL
```
https://example.com/signup
?utm_source=email
&utm_medium=newsletter
&utm_campaign=holiday_2025
&utm_content=cta_button_v1
```

## Examples

### Email Campaign
```
utm_source=email
utm_medium=newsletter
utm_campaign=product_update_dec
utm_content=footer_link
```

### Paid LinkedIn Ad
```
utm_source=linkedin
utm_medium=cpc
utm_campaign=demo_request
utm_content=carousel_v2
```

### Twitter Organic
```
utm_source=twitter
utm_medium=organic
utm_campaign=feature_launch
utm_content=tweet_thread
```

## Notes / Gotchas
- **Lowercase always**—utm_source=Email vs utm_source=email will split data
- **Use underscores, not spaces**—utm_campaign=holiday sale won't work
- **Don't change params mid-campaign**—breaks continuity
- **Test first**: Click your link, verify in Google Analytics

## Related
- [Process: Campaign Launch](../processes/process-campaign-launch.md)
- [Tools: UTM Generator](../../shared/tools-and-links.md#utm-tools)
