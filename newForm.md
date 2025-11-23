I want you to redesign complete ordering form for customer 
A robust laundry ordering form should feel like a guided flow, but still be one compact screen (or 2–3 logical collapsible sections) with smart defaults and conditional fields. Below is a complete, production‑grade field list you can directly translate into UI (web or app).[1][2]


## Section 1: Customer & Order Basics


- Customer full name (required).[3](import from login user details)
- Mobile number with country code (required, OTP optional).(import from login user details)  
- Email (optional but recommended for receipts).[4](import from login user details)
- Order type:  
  - New order  
  - Repeat last order (auto‑fill from history to reduce friction).[5]
- Preferred communication: WhatsApp / SMS / Call / Email.  


### Pickup & delivery


- Service mode (radio):  
  - Pickup & delivery  
  - Drop‑off at store  
  - In‑store only (no logistics)  
- Pickup address (autocomplete + save as “Home”, “Office”, etc.).[4]
- Pickup date picker (disable past dates + holidays).[6]
- Pickup time slot (e.g., 8–10 AM, 10–12 AM).  
- Delivery address (checkbox “Same as pickup”; if unchecked, show address fields).[3]
- Delivery date (auto‑suggest based on SLA & workload, but editable within allowed range).[7]
- Delivery time slot.  
- Notes for driver (gate code, pet, etc.).[3]


## Section 2: Service Selection (by Category)


Use a tabbed or accordion layout: “Clothes”, “Household”, “Special fabrics”, “Others”, so user never scrolls huge lists.[8][1]


### Global service options


- Service package (multi‑select or per‑item):  
  - Wash & fold  
  - Wash & iron  
  - Iron only  
  - Dry clean  
  - Stain treatment / Spot cleaning  
  - Premium care (delicate, hand wash, etc.)[9][7]
- Speed:  
  - Standard (default)  
  - Express (X hours)  
  - Super express (same day)  
- Fragrance: Regular / Mild / Fragrance‑free.  
- Detergent preference: Regular / Hypoallergenic / Customer‑provided.  
- Water temperature: Cold / Warm / Hot (with sensible defaults).  


### Clothes tab (per‑item matrix)


Show as table or cards with quantity steppers and per‑item service selection.[10][11]


- Tops:  
  - Shirt (formal) – quantity, service (dropdown), fabric (cotton, linen, silk, synthetic).  
  - T‑shirt  
  - Blouse / Kurti  
  - Sweater / Hoodie  
  - Jacket / Coat  


- Bottoms:  
  - Trousers / Formal pants  
  - Jeans  
  - Shorts  
  - Skirt (mini / knee / long)[10]


- Full outfits:  
  - Suit (2‑piece, 3‑piece)  
  - Dress (casual / evening)  
  - Saree / Lehenga / Ethnic set (if relevant to region).  


- Others:  
  - Innerwear (bundle count, e.g., “pack of 10”)  
  - Socks (pair count)  
  - Tie, scarf, shawl, dupatta, belt, cap, gloves.[10]


For each item row:


- Quantity (stepper).  
- Service type (wash & fold / dry clean / iron only, etc.).  
- Fabric type (dropdown).  
- Color category (light / dark / mixed; warning if “mixed” with note).[7]
- Stain present? (Yes/No → if Yes, show “Stain type” chips: oil, ink, food, blood, unknown).  
- Special instructions (short text: “button loose”, “do not starch”, etc.).  


### Household tab


- Bedding: Comforter (twin/queen/king), duvet cover, blanket, bedsheet, pillow, bed skirt.[10]
- Curtains & drapes (per panel, length option).[10]
- Table linens: tablecloth, runners, napkins.  
- Rugs / mats (size selection).  


Same per‑item structure: quantity, service type, fabric, stain, notes.


### Special fabrics tab


- Silk items  
- Wool / cashmere  
- Leather / suede (bags, jackets, shoes for polishing)[10]
- Bridal / designer wear  


Each with mandatory “Service type” (always dry clean / specialist) and “Item value range” (for liability).  


### Other items tab


- Custom text field: “Other item description” + quantity + service type.  


## Section 3: Pricing, Discounts, and Summary


- Real‑time summary panel (sticky on side or top):  
  - Item count by category.  
  - Estimated total price (with tax and per‑line subtotals).[12][9]
  - Estimated delivery date range and SLA (“Ready by Tue, 6–8 PM”).[7]


- Promo code / referral code (apply + validation message).[12]
- Tip (optional): none / fixed amounts / custom.  
- Minimum order rule display (e.g., “Minimum ₹300 for pickup” with validation).[10]


## Section 4: Payment & Confirmation


- Payment method:  
  - Online now: UPI / Card / Wallet / Net banking  
  - Pay at delivery: Cash / Card on delivery (if allowed).[8][4]
- Billing address (if different from pickup, conditional).  
- GST / Tax ID (optional, for business invoices).  


- Order review (readonly list):  
  - Collapsible groups by category with total items per group.  
  - Edit buttons to jump back to section or row.  


- Consent & policies (checkboxes):  
  - Terms & conditions.  
  - Damage/loss policy.  
  - Opt‑in for marketing offers (optional).[5]


- Place order button (primary CTA) with microcopy (“Confirm & schedule pickup”).  


## Section 5: UX & Logic Enhancements


These are not visible “fields” but crucial behaviors that make it feel compact and non‑boring.[2][1][8]


- Saved preferences: last used options (service package, fragrance, payment method, addresses).  
- “Repeat last order” and “Order from history” shortcuts.  
- Per‑category quick bundles (e.g., “Office wear pack: 5 shirts + 3 pants wash & iron”).  
- Hard validations:  
  - At least one item required.  
  - Time slots and minimum order amounts enforced.  
- Soft warnings only (non‑blocking):  
  - “Mixed light and dark items may cause color bleeding.”  
- Progress indicator (3–4 steps max: Details → Services → Summary → Payment).  


update backend as follows so that each and every thing works in flow 
**I need a Django model, form, and view logic for a robust laundry order system covering:**  
- Service mode (pickup & delivery, dropoff at store, in-store only)  
- Pickup & delivery address, date, time slot, notes  
- Delivery address (option "Same as pickup"), date, time slot  
- For each item in the order, allow selection of:
  - Category (clothes, household, special, others)
  - Item type (e.g., shirt, jeans, saree, bedsheet—allow dynamic/expandable choices)
  - Quantity
  - Service type (wash & fold, wash & iron, iron only, dry clean, stain removal, premium care)
  - Fabric type
  - Color category (light/dark/mixed)
  - Stain present (yes/no, if yes, stain type with options)
  - Special instructions per item
- Per-order options:
  - Service package (multi-select if needed)
  - Speed (standard/express/super express)
  - Fragrance preference
  - Detergent option
  - Minimum order validation
- Order-level notes for driver/care
- Promo code/referral field
- Tip field (optional)
- Order price calculation at summary
- Payment method (online/cash/card-on-delivery, make options easy to extend)
- Per-order status (pending, in process, ready, delivered)
- Allow editing/changing order until it reaches a certain status (e.g., "picked up")
- Follow Django and modern UX best practices: formsets for items, sticky summary, validation, and error reporting.

**Generate:**
- Django models for orders and items (with enums, choices, and relations)
- Model forms/formsets, with clean() validation for logic like address sync, minimum items, and required slot details
- Serializer snippets if any parts are best handled via DRF for AJAX frontend
- Django views (function-based or CBV) for order create and update, suitable for use with a React/HTMx/AJAX frontend
- Sample template or JSON structure for one order with multiple items, showing how the item matrix fits into the overall structure.

Keep code well-structured and explain any non-obvious logic with in-line comments. Do not include authentication logic or basic user fields.




