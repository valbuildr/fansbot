# BBC Fans Bot Outage Tracking Style Guide

Last updated: 24 July 2025

## Follow the [BBC News style guide](https://www.bbc.co.uk/newsstyleguide/) whenever possible.

Here's the two most relevant parts:

> **Dates**: Put the day before the month (eg: 12 April 2001). Avoid the 12/04/2012 formulation in alt tags or anywhere else, as this will be understood in the US as 4 December. Do **not** include suffixes after the day (eg "20th").

> **Hours**: We use the 24-hour clock (with a colon) in all circumstances (including streaming), labelled GMT or BST as appropriate.

It’s recommended to put a callout at the start of an outage tracking page with what timezone updates are in. Below are some example callouts.

---

> All times are in BST. (GMT +01:00)

```
> All times are in BST. (GMT +01:00)
```

---

> All times are in GMT.

```
> All times are in GMT.
```

---

## Outage or not?

A lot of things can be considered outages, but a few things should never be considered an outage.

- Simple updates that require less than a minute or downtime
- Discord outages

## Name

When an outage occurs, create a page as soon as humanly possible to make sure users aren’t confused on why the bot isn’t working.

Use a generic name like ‘20 June 2025 Outage’ until more information is known.

Once more information is known, update the name of the page.

When updating the name of an outage, make sure the date is in the title.

## Type

Minor outages are usually fixed relatively quickly. Start by classifying any outage as a minor outage. If an outage takes more than 90 minutes to resolve, it should then be classified as a major outage.

Exceptions are made for situations where an outage will likely take longer than 90 minutes, like maintenance by the hosting platform.

## Impact

It should be pretty simple to gauge which parts of the bot work and which parts don’t.

If the bot is completely offline, the impact should be considered as ‘Full’.

If the bot is still online but some features aren’t working, then it should be considered as ‘Partial’.

## Status

It should also be quite simple to give statuses to outages.

Planned outages usually have an announcement at least 30 minutes before they happen.

## Assigned People

Only assign people who agree to work on resolving the outage. This might be just you.

The people assigned are considered the **resolution team**.

## Providing Updates

Below are some basic rules to follow when providing updates to outages.

### Be quick.

To provide transparency to users, updates to outages should be made as soon as humanly possible.

### Be concise.

To make it as easy as possible to know what’s going on, try to keep each update under 100 characters.

If an update needs to exceed 100 characters, try and create a TL;DR with the basic information.

### Be truthful.

To provide transparency to users, updates should be as truthful as humanly possible.

Don’t put blame on others as a way out of a simple mistake you or another team member may have made.

### Use BST or GMT.

Depending on what time the UK is using, provide updates in that timezone.

If an outage occurs between the switchover, use whichever timezone the outage began in.

#### Switchover Example

| Time (BST) | Time (GMT) | Event |
| :-- | :-- | :-- |
| **26 Oct 2025 @ 23:45** | 26 Oct 2025 @ 22:45 | Outage begins |
| 27 Oct 2025 @ 00:00 | **26 Oct 2025 @ 23:00** | BST ends, GMT starts |
| 27 Oct 2025 @ 00:45 | **27 Oct 2025 @ 23:45** | Outage ends |

In this example, the outage would be considered to be from 23:45 (26 Oct 2025) to 00:45 (27 Oct 2025) since the outage started in BST.

### Use a coloured circle to signify status.

Use the following emojis to signify the status of each update.

- 🔴 Red: Getting worse/New issue
  - This should also be used for starting updates.
- 🟡 Yellow: Issue fixed/Monitoring performance
- 🟢 Green: Outage resolved
  - This should **ONLY** be used when an outage is resolved.

### Sign updates that you write.

When writing an update, you should add a signature at the end of the update.

## Providing updates to Discord

To provide transparency, outage updates should be sent in Github and Discord.

When getting started on resolving an outage, use a webhook to send a message in the announcements channel following this template:

```
# <:bbc_fans_bot:1384148690893279374> {outage_name}
- :red_circle: <t:{start_timestamp}:f>: {starting_update} - {mention_user}
```

Make sure to mention the user who wrote the starting update. In most cases, this should be the person who sends the message.

For timestamps, use [Hammertime](https://hammertime.cyou/). Make sure to use the `<t:{}:f>`  format.

When an outage is resolved, add ‘(Resolved)’ to the announcement’s title, after the emoji but before the title.
