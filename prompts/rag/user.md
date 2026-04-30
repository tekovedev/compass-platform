### MESSAGE HISTORY ###
{{{json conversation}}}

{{#if location}}
---

### LOCATION ###
{{{json location}}}

{{/if}}
---

### BASE KNOWLEDGE ###
{{{json knowledge}}}

---

# Task
Generate a precise legal answer to the user's inquiry.

## 1. Structure
- **Table Trigger:** Use tables ONLY for comparisons.
- **Prose:** {{#unless expand}}**Answer within a maximum of 60 words total.**{{else}}**Answer within a maximum of 150 words total.**{{/unless}}
- **Style:** Use bullets, lists, bold and italics for easier scanning.
- **Hierarchy:** Use `##` and `###`.
- **Citations:** <sup>article</sup> after every claim.
