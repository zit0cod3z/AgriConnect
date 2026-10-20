# Requirements Document

## Introduction

AgroConnect is a full-stack web-based agricultural marketplace that directly links Nigerian/African farmers to customers at farm-gate prices, eliminating middlemen. Inspired by the gig-economy model (Fiverr/Upwork), farmers can post produce listings anonymously (no account required) while customers can browse, negotiate, order, and track deliveries. The platform targets produce such as tomatoes, rice, garri, yam, pepper, onions, and other Nigerian/African agricultural goods. At order confirmation, customers choose their preferred payment method: Payment on Delivery (POD), where payment is settled physically upon delivery, or online payment via Paystack, where payment is processed securely before the order is confirmed. The tech stack is Django (backend), SQLite3 (database), Python, HTML/CSS/Bootstrap 3 (frontend), with a green, yellow, and white colour scheme.

---

## Research Findings: Existing Platforms & Gaps

### Common features found on existing platforms (AgroStar, Ninjacart, Twiga Foods, WeFarm, AgroWorld, FarmX, Terrakru, myOGF, AgriMarket Nigeria)
- Verified farmer/buyer accounts required to list or purchase
- Product catalogue with category browsing
- Fixed-price listings only (no negotiation)
- Online payment gateways (card, bank transfer)
- Basic order tracking
- Mobile-first apps (Android/iOS)
- Logistics coordination by platform

### Gaps and unique features NOT available on most existing platforms
1. **Anonymous/guest farmer listings** — all known Nigerian platforms require farmer registration
2. **Price negotiation (offer/counter-offer)** — most are fixed-price storefronts
3. **Harvest Season Signals** — real-time indicators showing which produce is in peak harvest season
4. **Freshness Score** — transparent, community-driven produce quality rating
5. **Bulk Group-Buy by Customers** — customers pool orders to unlock farm-gate pricing tiers
6. **Farmer Reputation Without Account** — phone-based reputation linked to anonymous listings
7. **Produce Availability Calendar** — seasonal availability predictions per crop per region
8. **Open Price Broadcast** — farmers broadcast a price, buyers compete (reverse auction for buyers)
9. **Farm-to-Table Story Cards** — narrative content about where produce comes from
10. **SMS Fallback Notifications** — for farmers without smartphones

---

## Glossary

- **Platform**: The AgroConnect web application
- **Farmer**: A person or cooperative posting agricultural produce for sale; may be anonymous (guest) or registered
- **Customer**: A registered user who browses, negotiates, orders, and receives produce
- **Guest_Farmer**: A Farmer who lists produce without creating an account, identified by a contact phone number
- **Listing**: A product posting created by a Farmer or Guest_Farmer containing produce details, quantity, price, and location
- **Offer**: A price proposal submitted by a Customer in response to a Listing
- **Counter_Offer**: A revised price proposal submitted by a Farmer in response to a Customer's Offer
- **Deal**: A mutually accepted Offer or Counter_Offer that transitions to an Order
- **Order**: A confirmed transaction between a Customer and a Farmer following an accepted Deal
- **POD**: Payment on Delivery — payment settled when goods are physically delivered to the Customer
- **Paystack**: A third-party Nigerian payment gateway that processes card payments, bank transfers, USSD, and other online payment methods
- **Paystack_Transaction**: A single online payment session initiated by the Platform via the Paystack API, identified by a unique reference string
- **Paystack_Webhook**: An HTTP callback sent by Paystack to the Platform to report the final status of a Paystack_Transaction
- **Payment_Method**: The payment option selected by a Customer at order confirmation — either POD or Paystack online payment
- **Refund_Request**: A Customer-initiated request to reverse a completed Paystack online payment for a cancelled or disputed Order
- **Harvest_Season_Signal**: A system-generated indicator showing whether a produce category is currently in peak harvest season
- **Freshness_Score**: A 1–5 star community rating for produce quality assigned by Customers who have received Orders
- **Group_Buy**: A mechanism allowing multiple Customers to pool demand for a single Listing to unlock bulk pricing
- **Availability_Calendar**: A produce-specific seasonal schedule predicting when a crop will be abundant in a given region
- **Price_Broadcast**: A Farmer-initiated broadcast announcing produce at a specific price to all interested Customers
- **Admin**: A platform administrator with full moderation and management access
- **Notification**: An in-platform or SMS alert sent to a Farmer or Customer
- **Search_Filter**: A UI control for filtering Listings by category, location, price range, or harvest status
- **Category**: A classification for produce (e.g., Grains, Tubers, Vegetables, Spices, Fruits)

---

## Requirements

---

### Requirement 1: Anonymous Farmer Product Listings

**User Story:** As a farmer, I want to post my produce for sale without creating an account, so that I can quickly connect with buyers without a registration barrier.

#### Acceptance Criteria

1. THE Platform SHALL provide a listing creation form accessible to unauthenticated users (Guest_Farmers).
2. WHEN a Guest_Farmer submits a Listing, THE Platform SHALL require only: produce name, category, quantity (with unit), price per unit, farm location (state/LGA), contact phone number, and an optional description.
3. WHEN a Guest_Farmer submits a Listing with all required fields completed, THE Platform SHALL create and publish the Listing within 5 seconds.
4. IF a Guest_Farmer submits a Listing with any required field missing, THEN THE Platform SHALL display a field-level validation error identifying each missing field and SHALL NOT create the Listing.
5. WHEN a Listing is created by a Guest_Farmer, THE Platform SHALL generate a unique Listing reference code and display it to the Guest_Farmer for future reference.
6. THE Platform SHALL allow a Guest_Farmer to edit or delete their Listing by providing the Listing reference code and the registered contact phone number.
7. WHEN a Guest_Farmer provides a valid Listing reference code and matching phone number, THE Platform SHALL grant edit/delete access to that Listing only.
8. THE Platform SHALL associate the contact phone number with a cumulative Freshness_Score history, so that repeat Guest_Farmers build a phone-based reputation over time.
9. WHERE a Guest_Farmer provides an optional photo upload, THE Platform SHALL accept images in JPG, PNG, or WEBP format not exceeding 5 MB per image, with a maximum of 5 images per Listing.
10. IF an uploaded image exceeds 5 MB, THEN THE Platform SHALL reject the image and display an error message stating the file size limit.

---

### Requirement 2: Customer Account Registration and Authentication

**User Story:** As a customer, I want to create an account, so that I can browse listings, make offers, place orders, and track deliveries.

#### Acceptance Criteria

1. THE Platform SHALL provide a registration form requiring: full name, email address, phone number, state, and password.
2. WHEN a Customer submits a registration form with all required fields, THE Platform SHALL create the account and send a verification email within 60 seconds.
3. IF a Customer attempts to register with an email address already in the system, THEN THE Platform SHALL display an error message and SHALL NOT create a duplicate account.
4. WHEN a Customer verifies their email address, THE Platform SHALL activate the account and redirect the Customer to their dashboard.
5. WHEN a registered Customer submits valid login credentials, THE Platform SHALL authenticate the session and redirect to the Customer dashboard within 3 seconds.
6. IF a Customer submits incorrect login credentials 5 consecutive times, THEN THE Platform SHALL lock the account for 15 minutes and display a lockout notice.
7. WHEN a Customer requests a password reset, THE Platform SHALL send a reset link to their registered email address valid for 30 minutes.
8. THE Platform SHALL allow Customers to browse Listings without logging in, but SHALL require login before submitting an Offer or placing an Order.

---

### Requirement 3: Product Catalogue and Search

**User Story:** As a customer, I want to search and browse agricultural produce listings by category, location, and price, so that I can find the best farm-gate deals quickly.

#### Acceptance Criteria

1. THE Platform SHALL display all active Listings on a public catalogue page, ordered by most recently posted by default.
2. THE Platform SHALL provide a Search_Filter panel allowing Customers to filter Listings by: produce category, Nigerian state/LGA, price range (min/max per unit), and Harvest_Season_Signal status (in-season / off-season).
3. WHEN a Customer applies one or more Search_Filters, THE Platform SHALL update the Listing results within 2 seconds without a full page reload.
4. THE Platform SHALL provide a full-text keyword search bar that matches produce name, description, and category, returning results ranked by relevance.
5. WHEN a search query returns no results, THE Platform SHALL display a "No listings found" message and suggest similar produce categories or nearby listings.
6. THE Platform SHALL display on each Listing card: produce name, category, quantity available, price per unit, farm location (state), Harvest_Season_Signal badge, and Freshness_Score (if available).
7. WHEN a Customer clicks a Listing card, THE Platform SHALL display the full Listing detail page including all photos, description, Farmer phone-reputation score, Availability_Calendar snippet, and an Offer submission form.
8. THE Platform SHALL paginate Listing results, displaying 20 Listings per page, with navigation controls for previous and next pages.

---

### Requirement 4: Price Negotiation (Offer / Counter-Offer System)

**User Story:** As a customer, I want to make a price offer on a listing, and as a farmer, I want to accept, reject, or counter that offer, so that we can agree on a fair farm-gate price like a marketplace negotiation.

#### Acceptance Criteria

1. WHEN a logged-in Customer submits an Offer on a Listing, THE Platform SHALL record the Offer with: Customer ID, Listing ID, proposed price per unit, proposed quantity, timestamp, and an optional message.
2. THE Platform SHALL notify the Farmer (via on-platform notification and SMS if phone is provided) within 60 seconds of a new Offer being submitted.
3. WHEN a Farmer receives an Offer, THE Platform SHALL present three options: Accept Offer, Reject Offer, or Submit Counter_Offer.
4. WHEN a Farmer accepts an Offer, THE Platform SHALL convert the Offer to a Deal and notify the Customer within 60 seconds.
5. WHEN a Farmer submits a Counter_Offer, THE Platform SHALL present the Counter_Offer to the Customer with Accept and Reject options, and SHALL NOT allow further counter-offers beyond 3 rounds per Listing per Customer.
6. IF a Customer's Offer remains unanswered by the Farmer for 48 hours, THEN THE Platform SHALL automatically expire the Offer, notify the Customer, and update the Offer status to "Expired".
7. WHEN a Customer accepts a Counter_Offer, THE Platform SHALL convert it to a Deal and create a pending Order.
8. THE Platform SHALL maintain a visible negotiation thread on the Listing detail page, showing all Offers and Counter_Offers in chronological order, visible only to the participating Customer and Farmer.
9. WHEN a Deal is created, THE Platform SHALL lock the agreed price and quantity on the associated Listing for the duration of the Order, reducing available quantity by the Deal amount.

---

### Requirement 5: Order Management and Payment Method Selection

**User Story:** As a customer, I want to place an order and choose to either pay on delivery or pay securely online, so that I have the flexibility to pick the payment method that suits me while farmers are always guaranteed payment.

#### Acceptance Criteria

1. WHEN a Deal is created, THE Platform SHALL generate an Order with status "Pending Confirmation", referencing the Deal, Listing, Customer, and Farmer.
2. THE Platform SHALL display Orders on the Customer's dashboard with statuses: Pending Confirmation, Confirmed, Ready for Pickup/Delivery, In Transit, Delivered, Completed, and Cancelled.
3. WHEN a Farmer confirms an Order, THE Platform SHALL update the Order status to "Confirmed" and notify the Customer within 60 seconds.
4. THE Platform SHALL record the agreed delivery method (Farmer delivers or Customer picks up) and the expected delivery date on every Order.
5. WHEN a Customer marks an Order as "Delivered" and confirms receipt, THE Platform SHALL update the Order status to "Completed" and prompt the Customer to submit a Freshness_Score rating.
6. IF a Customer does not confirm delivery within 5 days of the expected delivery date, THEN THE Platform SHALL send a reminder notification and, after a further 2 days of no response, automatically close the Order as "Completed".
7. WHEN a Customer proceeds to order confirmation, THE Platform SHALL present two payment method options: "Payment on Delivery (POD)" and "Pay Online via Paystack", and SHALL require the Customer to select one before the Order is submitted.
8. WHERE a Customer selects Payment on Delivery, THE Platform SHALL present POD instructions to both Customer and Farmer on the Order detail page, clearly stating that payment is made physically upon delivery.
9. WHERE a Customer selects Pay Online via Paystack, THE Platform SHALL initiate a Paystack payment session as defined in Requirement 16, and SHALL NOT set the Order status to "Confirmed" until payment is verified as successful.
10. WHEN a Customer requests an Order cancellation before the Order status reaches "In Transit", THE Platform SHALL allow cancellation and notify the Farmer within 60 seconds.
11. IF an Order cancellation is requested after the status is "In Transit", THEN THE Platform SHALL display a notice that cancellation must be agreed by the Farmer and SHALL present a cancellation request to the Farmer.

---

### Requirement 6: Harvest Season Signals

**User Story:** As a customer, I want to know which produce is currently in peak harvest season, so that I can buy the freshest goods at the lowest farm-gate prices.

#### Acceptance Criteria

1. THE Platform SHALL maintain a Harvest_Season_Signal data table mapping each produce category to expected peak harvest months per Nigerian agro-ecological zone.
2. WHEN a Listing is created or viewed, THE Platform SHALL evaluate the current month against the Harvest_Season_Signal data and attach an "In Season" or "Off Season" badge to the Listing.
3. THE Platform SHALL display a "Seasonal Produce Guide" page listing all supported produce categories with their peak harvest months and current season status.
4. WHEN a Customer applies the "In Season" Search_Filter, THE Platform SHALL return only Listings whose produce category is currently flagged as "In Season".
5. THE Admin SHALL be able to update Harvest_Season_Signal entries via the admin panel, with changes reflected across all affected Listings within 5 minutes.

---

### Requirement 7: Freshness Score and Community Rating

**User Story:** As a customer, I want to rate the quality of produce I received, so that future buyers can make informed decisions, and honest farmers are rewarded with higher visibility.

#### Acceptance Criteria

1. WHEN an Order reaches "Completed" status, THE Platform SHALL present the Customer with a Freshness_Score form rating produce quality on a 1–5 star scale with an optional written review.
2. THE Platform SHALL calculate and display a Farmer's average Freshness_Score on all their Listings, based on all completed Orders linked to their phone number or account.
3. WHEN a Listing has fewer than 3 completed Freshness_Score ratings, THE Platform SHALL display "Not yet rated" instead of a numeric score.
4. THE Platform SHALL rank Listings with higher Freshness_Scores above lower-scored Listings within the same category and Search_Filter combination, all other factors equal.
5. IF a Customer submits more than one Freshness_Score for a single Order, THEN THE Platform SHALL reject the duplicate and display a message stating that the Order has already been rated.
6. THE Platform SHALL display individual Freshness_Score reviews (star rating, review text, reviewer first name, and date) on each Listing detail page.
7. THE Admin SHALL be able to remove a Freshness_Score review that violates the platform's content policy, with the removal logged in the admin audit trail.

---

### Requirement 8: Bulk Group-Buy

**User Story:** As a customer, I want to join other buyers in pooling demand for a single listing, so that we collectively unlock farm-gate bulk pricing I could not access alone.

#### Acceptance Criteria

1. THE Platform SHALL allow Farmers to mark a Listing as "Group-Buy Eligible" and define tiered pricing: a standard unit price and a bulk unit price triggered when total ordered quantity crosses a defined threshold.
2. WHEN a Listing is marked as Group-Buy Eligible, THE Platform SHALL display a Group-Buy progress bar showing current pooled quantity versus the bulk threshold.
3. WHEN a Customer joins a Group-Buy, THE Platform SHALL record the Customer's quantity contribution and update the progress bar in real time.
4. WHEN the pooled quantity reaches or exceeds the bulk threshold, THE Platform SHALL automatically apply the bulk unit price to all participating Customer Orders and notify each participating Customer.
5. IF the Group-Buy threshold is not reached within 7 days of the Listing creation date, THEN THE Platform SHALL notify all participating Customers that the bulk price was not unlocked, and SHALL offer each Customer the option to proceed at the standard price or cancel.
6. THE Platform SHALL display on the Group-Buy Listing: current participant count, total pooled quantity, quantity needed to reach the bulk threshold, and a countdown timer to the 7-day expiry.

---

### Requirement 9: Price Broadcast

**User Story:** As a farmer, I want to broadcast my available produce and price to all interested customers at once, so that I can quickly attract multiple buyers when I have a large harvest ready.

#### Acceptance Criteria

1. THE Platform SHALL provide a Price_Broadcast feature that allows any Farmer (guest or registered) to submit a broadcast with: produce name, quantity available, price per unit, location, contact phone, and an expiry time (1–72 hours).
2. WHEN a Price_Broadcast is submitted, THE Platform SHALL publish it to a dedicated "Live Broadcasts" feed visible to all platform visitors.
3. THE Platform SHALL display each Price_Broadcast with a live countdown timer showing time remaining until expiry.
4. WHEN a Price_Broadcast expires, THE Platform SHALL remove it from the Live Broadcasts feed and mark it as "Expired" in the Farmer's broadcast history (if accessible via reference code).
5. WHEN a Customer clicks "I'm Interested" on a Price_Broadcast, THE Platform SHALL record the Customer's interest and display a contact-ready page showing the Farmer's phone number and an option to submit an Offer.
6. THE Platform SHALL display the count of interested Customers on each Price_Broadcast to indicate demand level.

---

### Requirement 10: Availability Calendar

**User Story:** As a customer, I want to see a seasonal availability calendar for produce, so that I can plan purchases around peak harvest periods for freshness and cost savings.

#### Acceptance Criteria

1. THE Platform SHALL display an Availability_Calendar page showing a 12-month calendar grid with produce availability highlighted per month for each crop category.
2. THE Platform SHALL source Availability_Calendar data from the Harvest_Season_Signal data table and regional agricultural records maintained by the Admin.
3. WHEN a Customer selects a specific produce category on the Availability_Calendar, THE Platform SHALL highlight the peak harvest months and display expected price trend indicators (lower during peak, higher during off-season).
4. THE Availability_Calendar SHALL be filterable by Nigerian geopolitical zone (North-West, North-East, North-Central, South-West, South-East, South-South) to reflect regional variation in harvest seasons.
5. THE Admin SHALL be able to update Availability_Calendar entries via the admin panel, with changes reflected on the public calendar within 5 minutes.

---

### Requirement 11: Farm-to-Table Story Cards

**User Story:** As a farmer, I want to share a brief story about my farm with my listing, so that customers feel a personal connection to where their food comes from and trust my produce.

#### Acceptance Criteria

1. WHERE a Farmer (guest or registered) opts to add a Farm Story to a Listing, THE Platform SHALL provide a text field accepting up to 500 characters of narrative content.
2. WHEN a Listing includes a Farm Story, THE Platform SHALL render it as a distinct "Farm Story" card on the Listing detail page, styled to stand out from product specifications.
3. THE Platform SHALL allow Farmers to include a single optional farm photo (distinct from product photos) in the Farm Story card.
4. IF a Farm Story text contains prohibited content (spam, contact details, external URLs), THEN THE Platform SHALL reject the submission and display a validation message listing the detected violations.
5. THE Platform SHALL allow Customers to "Like" a Farm Story, with the total Like count displayed on the card and contributing to the Farmer's reputation score.

---

### Requirement 12: Notification System

**User Story:** As a user, I want to receive timely notifications about my listings, offers, orders, and broadcasts, so that I can respond quickly and not miss opportunities.

#### Acceptance Criteria

1. THE Platform SHALL deliver in-platform notifications to registered Customers and Farmers for the following events: new Offer received, Counter_Offer received, Deal accepted, Order status change, Group-Buy threshold reached, Group-Buy expiry warning (24 hours prior), Price_Broadcast interest received, and Freshness_Score review received.
2. WHEN a platform notification is generated, THE Platform SHALL display it in the user's notification bell with an unread badge count within 60 seconds.
3. THE Platform SHALL send an SMS notification to the contact phone number registered on a Listing for the following events: new Offer received, Deal accepted, Order confirmed, and Order in transit.
4. WHEN a user marks a notification as read, THE Platform SHALL remove the unread badge count for that notification within 2 seconds.
5. THE Platform SHALL retain notification history for 90 days, after which read notifications SHALL be automatically deleted.

---

### Requirement 13: Admin Panel and Moderation

**User Story:** As an admin, I want to manage all listings, users, reviews, and seasonal data, so that the platform remains trustworthy, accurate, and free from abuse.

#### Acceptance Criteria

1. THE Platform SHALL provide a Django admin panel accessible only to authenticated Admin users via a distinct admin URL path.
2. THE Admin SHALL be able to view, edit, deactivate, or permanently delete any Listing, Order, Offer, Customer account, or Freshness_Score review.
3. WHEN an Admin deactivates a Listing, THE Platform SHALL immediately remove it from all public catalogue and search views and notify the Farmer via SMS if a phone number is on record.
4. THE Admin SHALL be able to create, update, and delete Harvest_Season_Signal entries and Availability_Calendar data.
5. THE Platform SHALL log every Admin action (entity type, entity ID, action taken, Admin user ID, timestamp) to an immutable audit log viewable only by Admin users.
6. THE Platform SHALL provide an Admin dashboard displaying: total active Listings, total registered Customers, total Orders by status, total Group-Buys in progress, and total Price_Broadcasts active.
7. WHEN an Admin receives a flagged content report submitted by a Customer, THE Platform SHALL display the report in a moderation queue with the flagged Listing or review and the reporting Customer's details.

---

### Requirement 14: Responsive UI (Bootstrap 3, Green/Yellow/White Theme)

**User Story:** As a user, I want to use a visually appealing, mobile-friendly web application, so that I can access the marketplace comfortably on any device.

#### Acceptance Criteria

1. THE Platform SHALL implement all frontend pages using Bootstrap 3 grid system, ensuring responsive layout across desktop (≥992px), tablet (768–991px), and mobile (<768px) viewports.
2. THE Platform SHALL apply a consistent colour scheme: primary green (#2E7D32 or equivalent), accent yellow (#F9A825 or equivalent), and background/surface white (#FFFFFF), with colour choices applied consistently across navigation, buttons, badges, and cards.
3. THE Platform SHALL render primary action buttons (Post Listing, Submit Offer, Join Group-Buy, Broadcast Price) in accent yellow with green text, and secondary action buttons in green with white text.
4. WHEN a page is loaded on a mobile viewport, THE Platform SHALL collapse the navigation bar into a Bootstrap 3 hamburger toggle menu.
5. THE Platform SHALL achieve a Lighthouse accessibility score of at least 80 on all primary pages (home, catalogue, listing detail, order dashboard).
6. THE Platform SHALL display a branded top navigation bar containing: the AgroConnect logo (green leaf motif), primary navigation links, a search bar, and a notification bell (for logged-in users).
7. THE Platform SHALL load all primary pages (home, catalogue, listing detail) within 3 seconds on a standard broadband connection with no more than 20 HTTP requests per page.

---

### Requirement 15: Platform Security and Data Integrity

**User Story:** As any user of the platform, I want my data and interactions to be secure, so that I can trust the platform with my personal and transaction information.

#### Acceptance Criteria

1. THE Platform SHALL store all Customer passwords as salted cryptographic hashes using Django's default PBKDF2 algorithm, and SHALL NOT store plaintext passwords.
2. THE Platform SHALL enforce HTTPS for all pages and API endpoints, redirecting any HTTP request to HTTPS.
3. THE Platform SHALL protect all forms against Cross-Site Request Forgery (CSRF) using Django's built-in CSRF token mechanism.
4. THE Platform SHALL sanitise and validate all user-supplied input on the server side before persisting to the database, to prevent SQL injection and XSS attacks.
5. WHEN a Guest_Farmer's Listing reference code is used for edit/delete access, THE Platform SHALL verify the reference code against the associated phone number using constant-time comparison to prevent timing attacks.
6. THE Platform SHALL rate-limit the Listing creation endpoint to a maximum of 10 submissions per IP address per hour to prevent spam.
7. THE Platform SHALL rate-limit the Offer submission endpoint to a maximum of 20 Offers per Customer account per hour.
8. THE Platform SHALL back up the SQLite3 database file to a configurable local directory daily, retaining backups for 30 days.

---

### Requirement 16: Paystack Online Payment Integration

**User Story:** As a customer, I want to pay for my order securely online via Paystack, so that I can complete my purchase without needing to have cash ready at delivery.

#### Acceptance Criteria

1. WHEN a Customer selects "Pay Online via Paystack" at order confirmation, THE Platform SHALL initiate a Paystack_Transaction by calling Paystack's Initialize Transaction API with the Order amount in kobo, the Customer's email address, and a unique payment reference string generated by the Platform.
2. WHEN a Paystack_Transaction is successfully initialised, THE Platform SHALL redirect the Customer to Paystack's hosted payment page using the authorisation URL returned by the Paystack API.
3. WHEN Paystack redirects the Customer back to the Platform's callback URL after a payment attempt, THE Platform SHALL call Paystack's Verify Transaction API using the payment reference to confirm the transaction status before taking any Order action.
4. WHEN Paystack's Verify Transaction API returns a "success" status, THE Platform SHALL update the Order status to "Confirmed", store the verified paystack_reference and paystack_status on the Order, and notify the Customer and Farmer within 60 seconds.
5. IF a Paystack payment fails, is declined, or is abandoned by the Customer, THEN THE Platform SHALL set the Order status to "Pending Payment" and notify the Customer that payment was not completed, with options to retry the Paystack payment or switch to Payment on Delivery.
6. THE Platform SHALL store the following Paystack payment fields on every Order that uses online payment: paystack_reference (unique reference string), paystack_status (one of: initiated, success, failed, abandoned), and payment_amount (total amount charged in kobo).
7. THE Platform SHALL listen for incoming Paystack_Webhook events and SHALL update the corresponding Order's paystack_status when a charge.success or transfer.failed event is received.
8. WHEN the Platform receives a Paystack_Webhook event for a paystack_reference that has already been processed to a terminal status (success or failed), THE Platform SHALL acknowledge the webhook with an HTTP 200 response and SHALL NOT apply the update a second time, ensuring idempotent handling of duplicate webhook deliveries.
9. THE Platform SHALL store the Paystack secret key exclusively in server-side environment variables and SHALL NOT include it in source code, version control, or any client-facing response.
10. IF a Customer requests cancellation of a Paystack-paid Order before the Order status reaches "In Transit", THEN THE Platform SHALL record a Refund_Request linked to the Order and notify the Admin, who SHALL process the refund manually via the Paystack merchant dashboard.
11. THE Admin dashboard SHALL display the following Paystack payment summary metrics: total count and value of Orders paid online via Paystack, total count of Orders using Payment on Delivery, and total count of pending Refund_Requests awaiting Admin action.
