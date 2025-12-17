---
title: "Campaign Launch Process"
description: "Step-by-step process for planning, executing, and measuring marketing campaigns"
department: "growth"
doc_type: "process"
owner_team: "Growth & Marketing"
maintainer: "Growth Lead"
visibility: "internal"
keywords: ["campaign", "launch", "marketing", "analytics", "utm-tracking", "measurement"]
last_updated: "2025-12-17"
---

## Purpose
Campaigns drive awareness and conversions. This process ensures we launch consistently, track results, and learn what works.

## Scope
- Applies to: All marketing campaigns (email, social, paid ads, partnerships)
- Doesn't apply to: One-off tweets, organic social posts (minimal lift)

## Steps / Content

### 1. Planning Phase (2 weeks before launch)
- [ ] Define campaign goal (awareness? signups? trial activation?)
- [ ] Identify target audience (persona, size, where to find them)
- [ ] Write campaign brief: headline, CTA, value prop
- [ ] Create assets (landing page, emails, ad copy)
- [ ] Set KPIs: traffic, CTR, conversion rate, cost per acquisition

### 2. UTM Tagging (1 week before launch)
- Use [UTM Tracker Tool](../guides/guide-utm-tracking.md) to generate tags:
  - `utm_source`: Where traffic comes from (email, twitter, paid_linkedin)
  - `utm_medium`: Type of traffic (email, cpc, organic)
  - `utm_campaign`: Campaign name (holiday_sale_2025, webinar_dec)
  - `utm_content`: Ad variant (blue_button_v1, headline_a)

**Example**: `https://example.com/?utm_source=email&utm_medium=newsletter&utm_campaign=holiday_2025`

### 3. Launch Phase
- [ ] QA all links (test UTM params in analytics)
- [ ] Schedule emails (Mailchimp)
- [ ] Launch ads (Google Ads, LinkedIn, etc.)
- [ ] Post on social (pin post, set reminders)
- [ ] Brief support team (expect surge in signups/questions)

### 4. Monitoring Phase (During campaign)
- [ ] Daily check-in on analytics dashboard
- [ ] Monitor social mentions (Slack alerts)
- [ ] Respond to comments/questions
- [ ] Adjust bids or timing if underperforming

### 5. Post-Campaign Analysis (1 week after)
- [ ] Pull final numbers: traffic, conversions, CAC
- [ ] Compare vs. targets
- [ ] Write summary: what worked? what didn't?
- [ ] Archive assets & report in `campaigns/` folder

## Notes / Gotchas
- **Always use UTM tags**—otherwise we can't attribute signups
- **Don't launch on Friday**—you won't be around if something breaks
- **Double-check landing pages**—broken forms = wasted money

## Related
- [Guide: UTM Tracking Best Practices](../guides/guide-utm-tracking.md)
- [Tools: Analytics Dashboard](../../shared/tools-and-links.md#analytics)
