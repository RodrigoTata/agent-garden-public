---
name: quotation-for
description: Search the web to find quotations and prices for physical items, products, or services. Use when the user wants to buy something, asks for a budget, or needs to compare market options (defaulting to Chile).
disable-model-invocation: false
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# quotation-for

Run a comprehensive market search to build a structured quotation for items requested by the user.

## Steps

### Step 1 — Item definition
Identify the items, products, or services the user wants to quote. Assume the target market is **Chile** unless specified otherwise. Write a **short detail** summarizing exactly what the item is and what technical requirements or constraints apply.

**Completion criterion:** Every requested item has a clear definition and scope.

### Step 2 — Web search
Use the `search_web` tool to find at least **3 distinct options** for each item. 
- Prioritize local options (Chilean stores, MercadoLibre) for speed.
- Include **international options** (Amazon, AliExpress) if they offer a significant price or availability advantage.

**Completion criterion:** You have secured at least 3 real, priced options for *every* item. Do not proceed until you have 3 options per item.

### Step 3 — Present the Quotation
Deliver the findings directly to the user (or as an artifact if the list is extensive). Format the output rigidly:

For each item:
1. **Item Detail:** A brief description of what was searched.
2. **Options:** Present exactly 3 options. For each option, list:
   - **Store/Brand:** Where to buy it and what brand it is.
   - **Price:** In local currency (e.g., CLP).
   - **Detail:** Key specs or shipping info.
   - **Reason:** Why this option made the list (e.g., "Cheapest", "Premium Quality", "International alternative").
3. **Recommendation:** You must explicitly recommend **one** of the 3 options and explain *why* it is the best overall choice (balancing cost, speed, and quality).

**Completion criterion:** The response contains 3 options per item, a reason for each, and a final recommendation.
