# Manna Snips Launch Plan

## Goal

Get the first small wave of real users without turning `Manna Snips` into a spam project.

Target:

- clearer public explanation on GitHub
- a handful of honest early users
- feedback from people who actually take and share screenshots often

## Positioning

Lead with the problem, not the feature list.

Best one-line pitch:

`Manna Snips is a copy-first Windows screenshot tool for people who want to snip, mark up, and paste fast without filling their drive with throwaway PNGs.`

Best short contrast:

`It is closer to a better Snipping Tool than a full image editor.`

## Best First Channels

### 1. GitHub

Make the repo page do the first explanation work:

- clear description
- good screenshots
- obvious installer path
- short explanation of `copy first` vs `download explicitly`

This is the landing page every other channel will send people to.

### 2. Reddit

Reddit is worth using, but only if the post feels like a useful story or a useful tool share, not a drive-by launch.

Best fits:

- `r/sideprojects`
- `r/software`
- `r/opensource`

Avoid treating `r/windows` like a default launch channel. Their rules say you must request permission from the moderators before promoting an app or website.

### 3. Package and Discovery Surfaces

These are quieter than social posts, but often better for long-tail discovery:

- submit to `winget`
- add the app to AlternativeTo

## Reddit Notes

### `r/sideprojects`

This is a reasonable first post target.

The current rules say:

- project posts must include details beyond just the link
- no spam or excessive self-promotion
- no funnelling people into DMs
- no astroturfing
- use the right flair

So the post should explain:

- what problem led to the app
- why `copy first` matters
- how it differs from the default flow
- what kind of feedback you actually want

### `r/software`

This is stricter, but still viable because `Manna Snips` is open source.

The current rules say:

- do not promote your own software unless it is open source
- the exception is sharing on Wednesdays
- use the appropriate flair
- provide value beyond just the software link
- they also have a karma threshold for submissions

That means this post should be:

- a Wednesday post
- clearly open source
- more thoughtful than "I made a screenshot app"

### `r/opensource`

This is good if the post is framed as a genuine open-source utility share and you stay present in the thread.

The current rules say:

- no spam or excessive self-promotion
- do not use the sub as a link farm
- engage beyond drive-by posting
- use the `Promotional` flair when sharing a project
- linked repositories must have an OSI-listed license

### `r/windows`

This is not the first stop.

Their current rules say app or website promotion requires moderator permission first. If you want to post there later, send modmail before posting.

## Suggested Posting Order

1. Tighten the GitHub page first.
2. Make one `r/sideprojects` post.
3. Reply to every real comment for a few days.
4. If the response is healthy, do one `r/software` post on a Wednesday.
5. Add the app to `winget` and AlternativeTo for slower discovery.
6. Use problem-solving comments in relevant threads instead of repeating launch posts.

## Draft: `r/sideprojects`

Title:

`I built a copy-first Windows screenshot tool because I got tired of filling my drive with throwaway snips`

Body:

`I kept running into the same annoying loop on Windows: take a screenshot, maybe mark it up, then end up with another random PNG I did not actually want to keep.`

`So I built Manna Snips, a small open-source screenshot tool for one fast path: snip -> mark up -> copy -> paste. Downloading is explicit, but copy stays temporary.`

`Main idea: if I am just trying to show a bug, a log snippet, or a UI issue in chat or a ticket, I should not have to manage files afterward.`

`It has:`

- global hotkey while the app is running
- drag-to-select overlay
- lightweight editor with pen, highlight, rectangle, and arrow
- explicit PNG download only when you actually want a file

`Would especially love feedback from people who share lots of screenshots for support, docs, or debugging.`

`Repo and installer are here: https://github.com/manna-core/manna-snips`

## Draft: `r/software` Wednesday

Title:

`[Open Source] Manna Snips - a copy-first Windows screenshot tool with lightweight markup`

Body:

`Built this because I wanted a Windows snipping workflow that is honest about copy vs save.`

`The default path is: capture a region, add a quick annotation, copy it back to the clipboard, and paste it wherever you need it. Downloading a PNG is explicit and separate.`

`It is open source, Windows-focused, and intentionally small.`

`Useful if you share lots of screenshots in bug reports, chats, tickets, or documentation and do not want a folder full of throwaway image files.`

`GitHub: https://github.com/manna-core/manna-snips`

## Draft: Short Social Blurb

`Built a tiny Windows screenshot tool called Manna Snips. It is copy-first: snip, mark up, copy, paste. Download is explicit, so you do not end up with a pile of throwaway PNGs. Open source: https://github.com/manna-core/manna-snips`

## Low-Noise Promotion Rules

- do not shotgun the same post into a dozen places
- do not hide that you built it
- do not ask people to DM you for the link or details
- do not argue with moderators about house rules
- do not post again unless there is a meaningful update or a different audience fit
- do spend time replying thoughtfully in the thread after posting

## Good Next Discovery Work

- submit `Manna Snips` to the Windows Package Manager community repository
- add a small demo GIF to the GitHub page
- add the project to AlternativeTo
- watch for Reddit threads where people are already asking for a better Windows screenshot workflow

## Source Notes

- Reddit SMB guidance: be human first, salesperson second; build credibility before promoting; respect each subreddit's rules
  - https://www.business.reddit.com/learning-hub/articles/smb-how-to-use-reddit
- Reddit SMB customer-finding guidance: use subreddits to listen first, comment rarely, and save overt promo for ads
  - https://www.business.reddit.com/learning-hub/articles/how-to-find-customers-on-reddit
- `r/sideprojects` current rules JSON
  - https://www.reddit.com/r/sideprojects/about/rules.json
- `r/software` current rules JSON
  - https://www.reddit.com/r/software/about/rules.json
- `r/opensource` current rules JSON
  - https://www.reddit.com/r/opensource/about/rules.json
- `r/windows` current rules JSON
  - https://www.reddit.com/r/windows/about/rules.json
- `winget` submission docs
  - https://learn.microsoft.com/en-us/windows/package-manager/package/repository
