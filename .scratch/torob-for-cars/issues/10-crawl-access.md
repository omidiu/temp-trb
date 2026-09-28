# Crawl access and terms of service

Type: grilling
Status: resolved
Blocked by: 01

## Question

Given that Divar's and Bama's terms prohibit automated copying, how do we gather Listings for the snapshot? Options include the Kenar partner API for Divar, the internal JSON endpoints used for a small one-off private snapshot, asking Bama for permission, or leaning on Sheypoor. Decide the access method per Source, the snapshot volume, request pacing, and how the demo video presents where the data came from.

## Answer

Decided autonomously (the user asked for details to be decided by Claude, with only the final spec reviewed). A one-off private snapshot from the Sources' public web JSON endpoints, at most 1 request every 2 seconds, about 3k Divar and 1.5k Bama Listings, no login, phones or captcha bypass, raw responses stored; the video names Kenar as the production route. Sheypoor dropped. Needs the user's explicit acceptance at review.

Full rules, reasons and worked examples: [spec.md](../spec.md) §4.
