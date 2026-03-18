# On the map, can you show country full name as well?

**Session ID:** `acb4fc44-34d3-4fec-878f-2f599983bfff`  
**Started:** 2026-03-16 00:25 UTC  
**Ended:** 2026-03-16 00:32 UTC  
**Source:** Claude Code (local session log)

---

## **Human** _2026-03-16 00:25 UTC_

On the map, can you show country full name as well?

---

## **Assistant** _2026-03-16 00:25 UTC_

*[Tool call: `Agent`]*

---

## **Assistant** _2026-03-16 00:27 UTC_

*[Tool call: `Read` — `/Users/andy/Library/CloudStorage/OneDrive-UniversityofLeeds/Years/202526/2. COMP3011 Web Services and Web Data/Coursework 1/COMP3011-Coursework-1/frontend/src/components/ChoroplethMap.tsx`]*

---

## **Assistant** _2026-03-16 00:27 UTC_

*[Tool call: `Bash` — `head -c 2000 "/Users/andy/Library/CloudStorage/OneDrive-UniversityofLeeds/Years/202526/2. COMP3011 Web Services and Web `]*

---

## **Assistant** _2026-03-16 00:29 UTC_

*[Tool call: `Bash` — `python3 -c "
import json
with open('/Users/andy/Library/CloudStorage/OneDrive-UniversityofLeeds/Years/202526/2. COMP3011`]*

---

## **Assistant** _2026-03-16 00:29 UTC_

The GeoJSON has a `name` property. I'll extract it in `onEachFeature` and use it in tooltips.

---

## **Assistant** _2026-03-16 00:29 UTC_

*[Tool call: `Edit` — `/Users/andy/Library/CloudStorage/OneDrive-UniversityofLeeds/Years/202526/2. COMP3011 Web Services and Web Data/Coursework 1/COMP3011-Coursework-1/frontend/src/components/ChoroplethMap.tsx`]*

---

## **Assistant** _2026-03-16 00:29 UTC_

*[Tool call: `Read` — `/Users/andy/Library/CloudStorage/OneDrive-UniversityofLeeds/Years/202526/2. COMP3011 Web Services and Web Data/Coursework 1/COMP3011-Coursework-1/frontend/src/components/ChoroplethMap.tsx`]*

---

## **Assistant** _2026-03-16 00:30 UTC_

*[Tool call: `Edit` — `/Users/andy/Library/CloudStorage/OneDrive-UniversityofLeeds/Years/202526/2. COMP3011 Web Services and Web Data/Coursework 1/COMP3011-Coursework-1/frontend/src/components/ChoroplethMap.tsx`]*

---

## **Assistant** _2026-03-16 00:30 UTC_

The map tooltip now shows the full country name in bold followed by the ISO3 code in parentheses — e.g., **Indonesia** (IDN) — on both countries with and without WFP data.

---

## **Human** _2026-03-16 00:31 UTC_

commit

---

## **Assistant** _2026-03-16 00:31 UTC_

*[Tool call: `Skill`]*

---

## **Assistant** _2026-03-16 00:31 UTC_

*[Tool call: `Bash` — `cd "/Users/andy/Library/CloudStorage/OneDrive-UniversityofLeeds/Years/202526/2. COMP3011 Web Services and Web Data/Cours`]*

---

## **Assistant** _2026-03-16 00:31 UTC_

*[Tool call: `Bash` — `cd "/Users/andy/Library/CloudStorage/OneDrive-UniversityofLeeds/Years/202526/2. COMP3011 Web Services and Web Data/Cours`]*

---

## **Assistant** _2026-03-16 00:32 UTC_

Committed as `93fab1b`.

---
