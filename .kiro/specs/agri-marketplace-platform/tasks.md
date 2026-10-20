# Implementation Plan: AgroConnect Agri-Marketplace Platform

## Overview

Build the AgroConnect Django 4.2 / Python 3.11 platform in the `agroconnect/` directory at the workspace root. The implementation follows a foundation-first order: project scaffold → data models → service layer → views/URLs → templates → frontend assets → background tasks → tests. All 10 Django apps are built incrementally; each app is wired into the project before moving to the next.

Tech stack: Django 4.2, Python 3.11, SQLite3, Bootstrap 3.4.1, Paystack API. Colour scheme: green (#2E7D32), yellow (#F9A825), white (#FFFFFF).

---

## Tasks

- [x] 1. Bootstrap project scaffold and dependencies
  - Create the `agroconnect/` directory at the workspace root with the full directory structure described in the design:
    ```
    agroconnect/
    ├── agroconnect/         # Django project package
    ├── apps/                # All 10 app packages
    ├── templates/           # Global templates
    ├── static/css|js|img/
    ├── media/
    ├── tests/unit|properties|integration/
    └── manage.py
    ```
  - Create `requirements.txt` with pinned versions: Django==4.2.*, Pillow==10.*, hypothesis==6.*, pytest==8.*, pytest-django==4.*, africastalking==1.*
  - Run `django-admin startproject agroconnect agroconnect/` (or write `manage.py`, `settings.py`, `wsgi.py`, `asgi.py` directly)
  - Create all 10 app packages under `apps/`: `accounts`, `listings`, `negotiations`, `orders`, `notifications`, `broadcasts`, `groupbuy`, `seasonal`, `stories`, `admin_panel` — each with `__init__.py`, `models.py`, `views.py`, `urls.py`, `services.py`, `apps.py`
  - Configure `settings.py`: `INSTALLED_APPS`, `DATABASES` (SQLite3 + WAL mode), `MEDIA_ROOT`/`MEDIA_URL`, `STATIC_ROOT`/`STATIC_URL`, `AUTH_USER_MODEL = 'accounts.Customer'`, `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `DEFAULT_AUTO_FIELD`, `SMS_BACKEND = 'console'`, `DB_BACKUP_DIR`
  - Configure root `agroconnect/urls.py` with all 11 `include()` entries as specified in the design
  - Create `pytest.ini` / `conftest.py` with `DJANGO_SETTINGS_MODULE` and Hypothesis CI profile
  - _Requirements: 14.1 (Bootstrap 3 layout foundation), 15.2 (HTTPS settings stubs)_

- [ ] 2. Implement `apps/accounts` — Customer model and authentication
  - [ ] 2.1 Create `Customer` model extending `AbstractUser` with `phone`, `state`, `email_verified`, `is_locked`, `locked_until`, `failed_login_attempts` fields as defined in the design
    - Register `Customer` in `accounts/admin.py`
    - Create and run migrations: `python manage.py makemigrations accounts && python manage.py migrate`
    - _Requirements: 2.1, 2.6, 15.1_

  - [ ] 2.2 Implement `accounts/services.py` with all five functions: `create_customer`, `send_verification_email`, `verify_email_token`, `lock_account`, `is_account_locked`
    - `create_customer` uses Django's password hashing; never stores plaintext
    - `send_verification_email` generates a signed token (use `django.core.signing`) and sends via `django.core.mail`
    - `verify_email_token` validates the token with a 60-minute expiry; sets `email_verified = True` on success
    - `lock_account` sets `is_locked=True`, `locked_until = now + 15 min`, resets `failed_login_attempts`
    - `is_account_locked` checks `is_locked` and whether `locked_until` is still in the future
    - _Requirements: 2.2, 2.3, 2.4, 2.6, 2.7, 15.1_

  - [ ] 2.3 Implement `accounts/views.py`: `RegisterView`, `LoginView` (with lockout logic on 5 failures), `LogoutView`, `VerifyEmailView`, `DashboardView`, `PasswordResetView`
    - `LoginView` increments `failed_login_attempts` on each bad attempt; calls `lock_account` at threshold 5; always redirects to dashboard on success
    - `DashboardView` requires `LoginRequiredMixin`; shows summary of Customer's offers, orders, and unread notifications
    - Wire `accounts/urls.py` with all patterns listed in the design URL table
    - _Requirements: 2.4, 2.5, 2.6, 2.7, 2.8_

  - [ ]* 2.4 Write unit tests for `accounts/services.py`
    - Test `create_customer` happy path and duplicate email rejection
    - Test token expiry in `verify_email_token`
    - Test account lockout after 5 failed attempts and unlock after 15 minutes
    - _Requirements: 2.3, 2.6, 2.7_

  - [ ]* 2.5 Write property test — password hashing (Property 29)
    - **Property 29: Password Hashing**
    - **Validates: Requirements 15.1**
    - Use `hypothesis.strategies.text()` to generate arbitrary passwords, create Customer records, and assert `customer.password != plaintext_password`

- [ ] 3. Implement `apps/listings` — Listing model, images, reference codes, freshness scores
  - [ ] 3.1 Create `Listing`, `ListingImage`, and `FreshnessScore` models as specified in the design
    - `Listing`: all fields including group-buy fields, nullable `farmer` FK to `accounts.Customer`
    - `ListingImage`: `ImageField` with `upload_to='listings/%Y/%m/'`
    - `FreshnessScore`: `OneToOneField` on `Order`, `farmer_phone` indexed
    - Run `makemigrations listings && migrate`
    - _Requirements: 1.2, 1.8, 7.1_

  - [ ] 3.2 Implement `listings/services.py` with six functions: `create_listing`, `generate_reference_code`, `create_unique_reference_code`, `verify_listing_access`, `get_catalogue`, `search_listings`, `deactivate_listing`
    - `generate_reference_code` uses `secrets.choice` over uppercase+digits, formatted as `XXXX-XXXX-XXXX-XXXX`
    - `create_unique_reference_code` retries up to 10 times on collision
    - `verify_listing_access` uses `hmac.compare_digest` for constant-time phone comparison (dummy comparison on miss to equalise timing)
    - `get_catalogue` returns a Django `Paginator` page (20 per page), ordered by `-created_at`; annotates each listing with `season_status` and freshness display
    - `search_listings` performs case-insensitive `icontains` match on `produce_name`, `description`, and `category`
    - `deactivate_listing` sets `is_active=False` and saves
    - _Requirements: 1.3, 1.4, 1.5, 1.6, 1.7, 3.1, 3.4, 3.8, 13.3, 15.5_

  - [ ] 3.3 Implement `listings/views.py`: `CatalogueView`, `CreateListingView`, `ListingDetailView`, `EditListingView`, `DeleteListingView`, `SearchView`
    - `CreateListingView`: rate-limited (10/hour/IP via `@rate_limit` decorator); handles optional up to 5 image uploads; validates image size ≤ 5 MB and format (JPG/PNG/WEBP); displays reference code after creation
    - `EditListingView` / `DeleteListingView`: require reference code + phone (custom `GuestListingAccessMixin`); use `verify_listing_access`
    - `CatalogueView`: renders filter sidebar (category, state, price range, in-season toggle); passes paginated listings to template
    - `SearchView`: reads `?q=` param; calls `search_listings`; shows "No listings found" with suggestions when empty
    - Wire `listings/urls.py` with all patterns from the design URL table
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.9, 1.10, 3.1, 3.2, 3.3, 3.5, 3.7, 3.8, 15.6_

  - [ ]* 3.4 Write property tests for listings (Properties 1, 2, 3, 24, 25, 26, 27, 31)
    - **Property 1: Reference Code Uniqueness** — generate 100 codes, assert all distinct. **Validates: Requirements 1.5**
    - **Property 2: Listing Validation Rejects Incomplete Submissions** — `fixed_dictionaries` with random missing required fields, assert service raises `ValidationError`. **Validates: Requirements 1.4**
    - **Property 3: Listing Access Control** — correct code + correct phone returns Listing; correct code + wrong phone returns None; wrong code + any phone returns None. **Validates: Requirements 1.6, 1.7, 15.5**
    - **Property 24: Catalogue Ordering (Newest First)** — create N listings with distinct `created_at`, assert catalogue queryset returns descending order. **Validates: Requirements 3.1**
    - **Property 25: Catalogue Pagination** — for any N listings, page p returns exactly `min(20, max(0, N − (p−1)*20))` items, union of all pages has no duplicates. **Validates: Requirements 3.8**
    - **Property 26: Search Filter Correctness** — apply random filter combos, every returned listing satisfies all filters. **Validates: Requirements 3.2, 3.4**
    - **Property 27: Admin Deactivation Removes Listing from Public Catalogue** — deactivate any active listing, assert it no longer appears in catalogue or search. **Validates: Requirements 13.3**
    - **Property 31: Search Result Keyword Relevance** — for any keyword query, every returned listing contains that keyword in `produce_name`, `description`, or `category`. **Validates: Requirements 3.4**

- [ ] 4. Checkpoint — Ensure all tests pass
  - Run `pytest tests/` and fix any failures before proceeding.
  - Ensure migrations are clean: `python manage.py migrate --check`

- [ ] 5. Implement `apps/seasonal` — Harvest Season Signals and Availability Calendar
  - [ ] 5.1 Create `HarvestSeasonSignal` and `AvailabilityCalendar` models with `unique_together` constraints; run migrations
    - Add `STATE_TO_AGRO_ZONE` dict constant (all 36 Nigerian states + FCT) in `seasonal/constants.py`
    - _Requirements: 6.1, 10.1_

  - [ ] 5.2 Implement `seasonal/services.py` with `evaluate_season_signal(produce_category, listing_state) -> str` exactly as specified in the design
    - Returns `'in_season'` or `'off_season'`; defaults to `'off_season'` for unknown zones or missing signals
    - _Requirements: 6.2, 6.4_

  - [ ] 5.3 Implement `seasonal/views.py`: `SeasonalGuideView` and `AvailabilityCalendarView`
    - `SeasonalGuideView` lists all `HarvestSeasonSignal` entries with current-month evaluation badges
    - `AvailabilityCalendarView` renders the 12-month grid, filterable by geo zone; sources data from `AvailabilityCalendar`
    - Wire `seasonal/urls.py`
    - _Requirements: 6.3, 10.1, 10.2, 10.3, 10.4_

  - [ ]* 5.4 Write property tests for seasonal signals (Properties 7, 32)
    - **Property 7: Harvest Season Signal Evaluation** — for any (category, zone, month), `evaluate_season_signal` returns `'in_season'` iff month is in `peak_months`. **Validates: Requirements 6.2, 6.4**
    - **Property 32: Availability Calendar Zone Filter Correctness** — for any zone filter, every returned entry has `geo_zone` equal to the selected zone. **Validates: Requirements 10.4**

- [ ] 6. Implement `apps/negotiations` — Offer, CounterOffer, Deal models and negotiation flow
  - [ ] 6.1 Create `Offer`, `CounterOffer`, and `Deal` models with all status choices; run migrations
    - `Offer.expires_at` is set to `created_at + 48h` in the service layer (not at DB level)
    - _Requirements: 4.1, 4.6_

  - [ ] 6.2 Implement `negotiations/services.py` with all seven functions: `submit_offer`, `submit_counter_offer`, `accept_offer`, `accept_counter_offer`, `reject_offer`, `get_negotiation_thread`, `expire_stale_offers`
    - `submit_offer` validates max 3 rounds per listing per customer; sets `expires_at = now + 48h`; calls `notifications.services.notify` for the farmer
    - `submit_counter_offer` enforces the 3-round cap by counting existing `CounterOffer` records; raises `ValidationError` on overflow; calls `notify` for the customer
    - `accept_offer` uses `@transaction.atomic`; creates `Deal`; sets `offer.status = 'accepted'`; reduces `listing.quantity` by `agreed_quantity`; calls `notify`; triggers `orders.services.create_order_from_deal`
    - `accept_counter_offer` sets `counter_offer.status = 'accepted'`; calls `accept_offer` on the parent offer using the counter-offer price
    - `reject_offer` and implicit rejection on `CounterOffer` set appropriate statuses and call `notify`
    - `get_negotiation_thread` returns chronological list of offers and counter-offers for a (listing, customer) pair
    - `expire_stale_offers` queries `status='pending'` offers where `expires_at < now()`; sets status to `'expired'`; calls `notify`; returns count
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9_

  - [ ] 6.3 Implement `negotiations/views.py`: `SubmitOfferView` (rate-limited 20/hour/user), `CounterOfferView`, `AcceptOfferView`, `RejectOfferView`, `NegotiationThreadView`
    - All offer-modifying views require login; thread view enforces customer-only visibility
    - Wire `negotiations/urls.py`
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.7, 4.8, 15.7_

  - [ ]* 6.4 Write property tests for negotiations (Properties 8, 9, 10, 11)
    - **Property 8: Counter-Offer Round Limit** — build up exactly 3 counter-offers on one offer, assert 4th `submit_counter_offer` raises `ValidationError`. **Validates: Requirements 4.5**
    - **Property 9: Offer Expiry** — for any offer with `expires_at` in the past and status `'pending'`, `expire_stale_offers()` sets status to `'expired'`. **Validates: Requirements 4.6**
    - **Property 10: Deal Creation from Accepted Offer** — for any pending offer, `accept_offer` creates exactly one Deal with matching price/quantity and sets offer status to `'accepted'`. **Validates: Requirements 4.4, 4.7**
    - **Property 11: Listing Quantity Reduction on Deal** — for any Listing with quantity Q and deal with quantity D, post-deal Listing quantity equals Q − D. **Validates: Requirements 4.9**

- [ ] 7. Implement `apps/orders` — Order lifecycle and FreshnessScore
  - [ ] 7.1 Create `Order` model with all status and delivery method choices; run migrations
    - Use `on_delete=models.PROTECT` on `deal` and `customer` FKs
    - _Requirements: 5.1, 5.2_

  - [ ] 7.2 Implement `orders/services.py`: `create_order_from_deal`, `confirm_order`, `mark_in_transit`, `mark_delivered`, `cancel_order`, `auto_close_stale_orders`
    - `create_order_from_deal` uses `@transaction.atomic`; creates `Order` with `status='pending_confirmation'`; copies `farmer_phone` from the listing
    - `confirm_order` transitions `pending_confirmation` → `confirmed`; calls `notify`
    - `mark_in_transit` transitions `confirmed`/`ready` → `in_transit`; calls `notify`
    - `mark_delivered` transitions `in_transit` → `delivered`; calls `notify`; prompts freshness score
    - `cancel_order` permits cancellation for statuses in `['pending_confirmation', 'confirmed', 'ready']`; for `'in_transit'` creates a cancellation request notification to farmer instead of cancelling immediately
    - `auto_close_stale_orders` closes orders stuck at `'delivered'` for more than 7 days (`5 + 2` days per requirement 5.6); returns count
    - Implement `submit_freshness_score(order, customer, stars, review_text)`: enforces one-per-order (raises `ValidationError` on duplicate)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 7.1, 7.5_

  - [ ] 7.3 Implement `orders/views.py`: `OrderListView`, `OrderDetailView` (with POD instructions), `ConfirmOrderView`, `CancelOrderView`, `MarkDeliveredView`; all require login
    - Wire `orders/urls.py`
    - _Requirements: 5.2, 5.4, 5.7, 5.8, 5.9_

  - [ ] 7.4 Add freshness score calculation to `listings/services.py`: `get_farmer_freshness_score(farmer_phone)` using `Avg` + `Count` aggregation; returns `'Not yet rated'` when count < 3
    - _Requirements: 7.2, 7.3_

  - [ ]* 7.5 Write property tests for freshness scores (Properties 4, 5, 6)
    - **Property 4: Freshness Score Aggregation** — for any list of star ratings (1–5) sharing a `farmer_phone`, `get_farmer_freshness_score` returns the correct average and count; display is `'Not yet rated'` when count < 3. **Validates: Requirements 7.2, 7.3**
    - **Property 5: No Duplicate Freshness Score per Order** — second `submit_freshness_score` call on same order raises `ValidationError` and leaves original unchanged. **Validates: Requirements 7.5**
    - **Property 6: Higher Freshness Score Ranks First Within Category** — in same category, listing with higher average freshness score appears before lower-scored listing. **Validates: Requirements 7.4**

  - [ ]* 7.6 Write property test for order status lifecycle (Property 12)
    - **Property 12: Order Status Lifecycle Invariants** — `create_order_from_deal` produces `'pending_confirmation'`; `confirm_order` transitions to `'confirmed'`; `cancel_order` on `['pending_confirmation','confirmed','ready']` sets `'cancelled'`; `cancel_order` on `'in_transit'` does NOT cancel but creates a notification. **Validates: Requirements 5.1, 5.3, 5.8**

- [ ] 8. Checkpoint — Ensure all tests pass
  - Run `pytest tests/` and resolve any failures.

- [ ] 9. Implement `apps/notifications` — In-platform and SMS notifications
  - [ ] 9.1 Create `Notification` model with all `EVENT_TYPES` choices; run migrations
    - _Requirements: 12.1_

  - [ ] 9.2 Implement `notifications/sms.py` with `SMSAdapter` class as specified in the design
    - Supports `'africastalking'`, `'console'`, and `'dummy'` backends via `settings.SMS_BACKEND`
    - SMS failure is logged but non-fatal (does not raise)
    - _Requirements: 12.3_

  - [ ] 9.3 Implement `notifications/services.py`: `notify`, `send_sms`, `mark_read`, `get_unread_count`, `purge_old_notifications`
    - `notify` persists a `Notification` record; if the event type warrants SMS (new offer, deal accepted, order confirmed, order in transit), calls `send_sms` via `SMSAdapter`
    - `get_unread_count` queries `Notification.objects.filter(customer=user, is_read=False).count()`
    - `purge_old_notifications` deletes `is_read=True` notifications older than 90 days; returns count
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

  - [ ] 9.4 Implement `notifications/views.py`: `NotificationListView`, `MarkReadView` (POST, returns JSON `{"count": N}` for AJAX), and `/notifications/unread-count/` JSON endpoint polled every 30 s
    - Wire `notifications/urls.py`
    - _Requirements: 12.2, 12.4_

  - [ ]* 9.5 Write property tests for notifications (Properties 20, 21)
    - **Property 20: Notification Unread Count Accuracy** — for any customer with N unread notifications, `get_unread_count` returns N; after `mark_read` on one, returns N − 1. **Validates: Requirements 12.1, 12.2, 12.4**
    - **Property 21: Notification Purge Respects Retention Period** — `purge_old_notifications` deletes all read notifications older than 90 days; leaves unread and recent-read notifications intact. **Validates: Requirements 12.5**

- [ ] 10. Implement `apps/broadcasts` — Price Broadcast feed
  - [ ] 10.1 Create `PriceBroadcast` and `BroadcastInterest` models; run migrations
    - `PriceBroadcast.reference_code` generated by `create_unique_reference_code(PriceBroadcast)` at creation
    - _Requirements: 9.1_

  - [ ] 10.2 Implement `broadcasts/services.py`: `create_broadcast`, `get_active_broadcasts`, `record_interest`, `expire_stale_broadcasts`
    - `get_active_broadcasts` filters `is_expired=False` and `expires_at > now()`
    - `record_interest` creates `BroadcastInterest`; raises `ValidationError` on duplicate; calls `notify` for the broadcaster (via phone if guest)
    - `expire_stale_broadcasts` sets `is_expired=True` for all broadcasts past `expires_at`; returns count
    - _Requirements: 9.2, 9.3, 9.4, 9.5, 9.6_

  - [ ] 10.3 Implement `broadcasts/views.py`: `BroadcastFeedView` (public), `CreateBroadcastView` (guest or registered), `BroadcastInterestView` (login required)
    - Wire `broadcasts/urls.py`
    - _Requirements: 9.1, 9.2, 9.5, 9.6_

  - [ ]* 10.4 Write property tests for broadcasts (Properties 16, 17)
    - **Property 16: Price Broadcast Active/Expired Visibility** — broadcasts with future `expires_at` and `is_expired=False` appear in active feed; those with past `expires_at` or `is_expired=True` do not. **Validates: Requirements 9.2, 9.4**
    - **Property 17: Broadcast Interest Count** — for any broadcast with N `BroadcastInterest` records, the interest count equals N. **Validates: Requirements 9.5, 9.6**

- [ ] 11. Implement `apps/groupbuy` — Group-Buy pooling
  - [ ] 11.1 Create `GroupBuy` and `GroupBuyParticipant` models with `unique_together`; run migrations
    - _Requirements: 8.1_

  - [ ] 11.2 Implement `groupbuy/services.py`: `join_group_buy`, `leave_group_buy`, `get_group_buy_progress`, `expire_stale_groupbuys`
    - `join_group_buy` uses `@transaction.atomic` and `F()` expressions as shown in the design; detects threshold crossing and calls `_apply_bulk_price_to_all` + `_notify_all_participants`
    - `get_group_buy_progress` returns `{'progress_percent': min(100.0, current/threshold*100), 'current_quantity': ..., 'quantity_remaining': ..., 'participant_count': ...}`
    - `expire_stale_groupbuys` handles groups past 7-day expiry: if threshold not reached, creates notifications for each active participant offering standard-price or cancel option; returns count
    - _Requirements: 8.2, 8.3, 8.4, 8.5, 8.6_

  - [ ] 11.3 Implement `groupbuy/views.py`: `JoinGroupBuyView` (login required); wire `groupbuy/urls.py`
    - _Requirements: 8.2, 8.3, 8.6_

  - [ ]* 11.4 Write property tests for group-buy (Properties 13, 14, 15)
    - **Property 13: Group-Buy Progression and Threshold Activation** — after `join_group_buy`, `current_quantity` increases by exactly `quantity` and `participant_count` by 1; when threshold first crossed, `threshold_reached=True` and all participants have bulk price applied. **Validates: Requirements 8.3, 8.4**
    - **Property 14: Group-Buy Progress Bar Accuracy** — for any (current_quantity C, threshold T), `progress_percent = min(100.0, C/T*100)`. **Validates: Requirements 8.2**
    - **Property 15: Group-Buy Expiry Notifications** — for any expired group-buy that didn't reach threshold, expiry task creates a Notification for each active participant. **Validates: Requirements 8.5**

- [ ] 12. Implement `apps/stories` — Farm Story Cards and Likes
  - [ ] 12.1 Create `FarmStory` and `FarmStoryLike` models; run migrations
    - _Requirements: 11.1_

  - [ ] 12.2 Implement `stories/services.py`: `create_story`, `like_story`, `validate_farm_story_text`
    - `validate_farm_story_text` uses regex patterns from the design to detect URLs, phone-number sequences, and social handles; returns list of violation descriptions
    - `like_story` creates `FarmStoryLike`; raises `ValidationError` on duplicate; increments `like_count` via `F()` expression
    - _Requirements: 11.1, 11.4, 11.5_

  - [ ] 12.3 Implement `stories/views.py` for like endpoint; wire `stories/urls.py`
    - _Requirements: 11.5_

  - [ ]* 12.4 Write property tests for stories (Properties 22, 23)
    - **Property 22: Farm Story Content Validation** — any text with ≥1 prohibited pattern returns non-empty violations list; any clean text with len ≤ 500 returns empty list. **Validates: Requirements 11.4, 11.1**
    - **Property 23: Farm Story Like Idempotence** — first like increments `like_count` by 1; second like attempt raises `ValidationError` and leaves count unchanged. **Validates: Requirements 11.5**

- [ ] 12.5 Implement `apps/payments` — Paystack online payment integration
  - [ ] 12.5.1 Create `payments/` app package with `__init__.py`, `models.py`, `views.py`, `urls.py`, `services.py`, `apps.py`; register in `INSTALLED_APPS`
    - Create `PaystackTransaction` and `RefundRequest` models as specified in the design
    - Run `makemigrations payments && migrate`
    - _Requirements: 16.1, 16.6_

  - [ ] 12.5.2 Implement `payments/services.py`: `initiate_paystack_payment`, `verify_paystack_payment`, `handle_paystack_webhook`, `record_refund_request`, `get_payment_summary_stats`
    - `initiate_paystack_payment`: calls Paystack Initialize Transaction API; generates unique reference `AGRO-{order.id}-{hex}`; persists `PaystackTransaction`; sets Order status to `'pending_payment'`; returns `authorisation_url`
    - `verify_paystack_payment`: calls Paystack Verify Transaction API; returns response data dict
    - `handle_paystack_webhook`: validates HMAC-SHA512 signature; idempotent — skips terminal-status transactions; updates Order to `'confirmed'` on `charge.success`; updates to `'pending_payment'` on `transfer.failed`
    - `record_refund_request`: creates `RefundRequest` record; notifies Admin
    - `get_payment_summary_stats`: returns counts and totals for Paystack orders, POD orders, and pending refunds
    - `PAYSTACK_SECRET_KEY` loaded exclusively from `os.environ.get('PAYSTACK_SECRET_KEY')` — never hardcoded
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8, 16.9, 16.10, 16.11_

  - [ ] 12.5.3 Implement `payments/views.py`: `InitiatePaymentView`, `PaystackCallbackView` (verifies payment on return), `PaystackWebhookView` (CSRF-exempt, validates signature)
    - `InitiatePaymentView`: requires login; calls `initiate_paystack_payment`; redirects to Paystack `authorisation_url`
    - `PaystackCallbackView`: reads `reference` from query params; calls `verify_paystack_payment`; updates Order status; redirects to Order detail page
    - `PaystackWebhookView`: `@csrf_exempt`; validates `X-Paystack-Signature` header; calls `handle_paystack_webhook`; returns HTTP 200 always
    - Wire `payments/urls.py` with three patterns: `initiate/<order_id>/`, `callback/`, `webhook/`
    - Add `path('payments/', include('apps.payments.urls', namespace='payments'))` to root `urls.py`
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.7, 16.8_

  - [ ] 12.5.4 Update `orders/views.py` `ConfirmOrderView` to render the payment method selection UI
    - Show POD vs Paystack radio buttons as specified in the design's Payment Method Selection UI
    - On form submit: if `payment_method == 'pod'` → confirm order normally; if `payment_method == 'paystack'` → redirect to `payments:initiate`
    - _Requirements: 5.7, 5.8, 5.9_

  - [ ]* 12.5.5 Write property tests for payments (Properties 33, 34, 36)
    - **Property 33: Paystack Transaction Initialisation** — after `initiate_paystack_payment`, a `PaystackTransaction` exists with status `'initiated'` and Order status is `'pending_payment'`. **Validates: Requirements 16.1, 16.6**
    - **Property 34: Paystack Webhook Idempotency** — for any transaction in `'success'` or `'failed'` status, calling `handle_paystack_webhook` with same reference returns True and does not change status. **Validates: Requirements 16.8**
    - **Property 36: Payment Method Gates Order Confirmation** — Order with `payment_method='paystack'` SHALL NOT reach `'confirmed'` unless `PaystackTransaction.paystack_status='success'`. **Validates: Requirements 5.9, 16.4**

- [ ] 13. Implement `apps/admin_panel` — Custom admin dashboard and audit log
  - [ ] 13.1 Create `AdminAuditLog` model; run migrations
    - Add `log_admin_action(admin_user, entity_type, entity_id, action, detail)` helper in `admin_panel/services.py` that creates `AdminAuditLog` records; never updates/deletes existing records (enforced at service layer)
    - _Requirements: 13.5_

  - [ ] 13.2 Implement `admin_panel/views.py`: `AdminDashboardView`, `AuditLogView`, `ModerationQueueView`
    - All views enforce `is_staff` check (raise `PermissionDenied` otherwise)
    - `AdminDashboardView` renders KPI widgets: total active listings, total customers, orders by status, group-buys in progress, active broadcasts
    - `AuditLogView` shows paginated `AdminAuditLog` entries ordered by `-timestamp`
    - `ModerationQueueView` shows flagged listings/reviews (add a `is_flagged` boolean to `Listing` and `FreshnessScore` models via additional migration)
    - Wire `admin_panel/urls.py`
    - _Requirements: 13.1, 13.2, 13.5, 13.6, 13.7_

  - [ ] 13.3 Extend admin panel with moderation actions: deactivate listing (calls `listings.services.deactivate_listing` + logs audit), remove freshness score review (deletes + logs audit), and edit/view/delete Customer/Order/Offer via Django's built-in admin with audit hooks
    - _Requirements: 13.2, 13.3, 13.4_

  - [ ]* 13.4 Write property tests for admin actions (Properties 27, 28)
    - **Property 27: Admin Deactivation Removes Listing from Public Catalogue** — after `deactivate_listing`, assert listing absent from all public catalogue and search querysets. **Validates: Requirements 13.3**
    - **Property 28: Audit Log Completeness** — for any admin action taken via the service layer, an `AdminAuditLog` record is created containing all required fields; records cannot be modified through the application layer. **Validates: Requirements 13.5**

- [ ] 14. Checkpoint — Ensure all tests pass
  - Run `pytest tests/` and resolve all failures.

- [ ] 15. Implement background task management commands
  - [ ] 15.1 Create `apps/listings/management/commands/expire_offers.py`
    - Calls `negotiations.services.expire_stale_offers()`; logs count; schedule: every 15 min via cron
    - _Requirements: 4.6_

  - [ ] 15.2 Create `apps/broadcasts/management/commands/expire_broadcasts.py`
    - Calls `broadcasts.services.expire_stale_broadcasts()`; schedule: every 5 min
    - _Requirements: 9.4_

  - [ ] 15.3 Create `apps/groupbuy/management/commands/expire_groupbuys.py`
    - Calls `groupbuy.services.expire_stale_groupbuys()`; schedule: every hour
    - _Requirements: 8.5_

  - [ ] 15.4 Create `apps/orders/management/commands/autoclose_orders.py`
    - Calls `orders.services.auto_close_stale_orders()`; schedule: daily
    - _Requirements: 5.6_

  - [ ] 15.5 Create `apps/notifications/management/commands/purge_notifications.py`
    - Calls `notifications.services.purge_old_notifications()`; schedule: daily
    - _Requirements: 12.5_

  - [ ] 15.6 Create `apps/admin_panel/management/commands/backup_database.py`
    - Copies `settings.DATABASES['default']['NAME']` to `settings.DB_BACKUP_DIR/db_YYYYMMDD_HHMMSS.sqlite3`; prunes backups older than 30 days; schedule: daily
    - _Requirements: 15.8_

- [ ] 16. Implement rate limiting decorator and security middleware
  - [ ] 16.1 Create `apps/listings/decorators.py` with `rate_limit(key_prefix, limit, window_seconds)` decorator as specified in the design
    - Uses Django's cache backend for counter storage
    - Returns HTTP 429 on limit exceeded
    - Apply `@rate_limit('listing_create', 10, 3600)` to `CreateListingView.post`
    - Apply `@rate_limit('offer_submit', 20, 3600)` to `SubmitOfferView.post`
    - _Requirements: 15.6, 15.7_

  - [ ] 16.2 Configure production security settings in `settings.py`: `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` (enabled when `DEBUG=False`)
    - Add `X-Content-Type-Options: nosniff` and `X-Frame-Options: DENY` headers via `SECURE_CONTENT_TYPE_NOSNIFF` and `X_FRAME_OPTIONS`
    - _Requirements: 15.2, 15.3_

  - [ ]* 16.3 Write property tests for rate limiting and security (Properties 18, 19, 29, 30)
    - **Property 18: Rate Limiting — Listing Creation** — after exactly 10 successful listing creation requests from the same IP within 1 hour, the 11th returns HTTP 429. **Validates: Requirements 15.6**
    - **Property 19: Rate Limiting — Offer Submission** — after exactly 20 successful offer submissions by the same customer within 1 hour, the 21st returns HTTP 429. **Validates: Requirements 15.7**
    - **Property 29: Password Hashing** (covered in task 2.5 — no duplicate needed)
    - **Property 30: CSRF Protection** — for any state-mutating POST endpoint, request without valid CSRF token returns HTTP 403 and does not mutate state. **Validates: Requirements 15.3**

- [ ] 17. Build global templates and Bootstrap 3 frontend
  - [ ] 17.1 Create `templates/base.html` with full Bootstrap 3.4.1 layout as specified in the design
    - Bootstrap 3 CDN links, jQuery 1.12.4 CDN, `{% static %}` tags for custom CSS/JS
    - `<meta name="csrf-token" content="{{ csrf_token }}">` in `<head>`
    - `{% include "partials/navbar.html" %}` and `{% include "partials/footer.html" %}`
    - Fixed-top navbar with green background, hamburger toggle for mobile
    - _Requirements: 14.1, 14.4, 14.6_

  - [ ] 17.2 Create `templates/partials/navbar.html` with full markup from the design
    - Logo, Browse / Live Broadcasts / Season Calendar links (white text), conditional login/register or Dashboard/notifications for authenticated users
    - Inline search form with yellow button
    - _Requirements: 14.6_

  - [ ] 17.3 Create `templates/partials/notification_bell.html`
    - Bell icon with unread badge (updated via AJAX every 30 s using `/notifications/unread-count/` endpoint)
    - _Requirements: 12.2_

  - [ ] 17.4 Create `templates/partials/footer.html` with green background, white text, basic platform links

  - [ ] 17.5 Create `templates/errors/404.html` and `templates/errors/500.html` extending `base.html` with branded error pages (no stack traces)
    - Register `handler404` and `handler500` in root `urls.py`
    - _Requirements: 14.2_

- [ ] 18. Build all app-specific templates
  - [ ] 18.1 Create `templates/listings/catalogue.html`
    - Filter sidebar (category, state, price range, in-season toggle), listing card grid using the exact Bootstrap 3 panel markup from the design (`col-xs-12 col-sm-6 col-md-4`), pagination controls
    - In-Season badge: green `label-success`; Off-Season: `label-default`
    - Yellow CTA "View & Negotiate" button on each card
    - _Requirements: 3.1, 3.2, 3.6, 3.8, 14.2, 14.3_

  - [ ] 18.2 Create `templates/listings/create_listing.html` and `templates/listings/edit_listing.html`
    - Bootstrap 3 form with `has-error` / `help-block` field-level validation pattern from the design
    - Image upload field with 5-file limit and size/format guidance text
    - Reference code display panel shown after successful creation
    - _Requirements: 1.1, 1.2, 1.4, 1.5, 1.9, 1.10, 14.3_

  - [ ] 18.3 Create `templates/listings/listing_detail.html`
    - Photo carousel/gallery, full description, farmer phone-reputation score, season badge
    - Embedded `{% include "stories/story_card.html" %}` when farm story exists
    - Group-Buy widget (`templates/groupbuy/progress_widget.html`) when eligible
    - Negotiation thread panel (visible only to authenticated participating customer)
    - Offer submission form at bottom
    - Freshness score reviews list
    - Availability Calendar snippet
    - _Requirements: 3.7, 4.8, 7.6, 8.6, 11.2, 14.2_

  - [ ] 18.4 Create `templates/accounts/register.html`, `login.html`, `dashboard.html`, `verify_email.html`, `password_reset.html`
    - Dashboard shows My Offers, My Orders (with status badges), and unread notification count
    - _Requirements: 2.1, 2.4, 2.5, 2.7, 14.2_

  - [ ] 18.5 Create `templates/negotiations/offer_form.html`, `counter_offer_form.html`, `thread.html`
    - Thread view uses the exact panel/media markup from the design with right-aligned customer entries and left-aligned farmer entries
    - Status labels coloured by offer status
    - _Requirements: 4.3, 4.8, 14.2_

  - [ ] 18.6 Create `templates/orders/order_list.html` and `order_detail.html`
    - Order detail includes POD instructions panel (yellow border, clearly stating payment is physical on delivery)
    - Status badge coloured to reflect current lifecycle stage
    - Freshness score prompt shown when status is `'completed'` and score not yet submitted
    - _Requirements: 5.2, 5.5, 5.7, 14.2_

  - [ ] 18.7 Create `templates/broadcasts/feed.html` and `create_broadcast.html`
    - Feed shows broadcast cards with live countdown timers (`.countdown` elements driven by `agroconnect.js`)
    - "I'm Interested" button on each card; interest count displayed
    - _Requirements: 9.2, 9.3, 9.5, 9.6, 14.2_

  - [ ] 18.8 Create `templates/groupbuy/join.html` with progress bar widget using exact Bootstrap 3 markup from the design
    - Progress bar green (`#2E7D32`), header yellow (`#F9A825`)
    - Countdown timer using `.countdown` class
    - _Requirements: 8.2, 8.6, 14.2_

  - [ ] 18.9 Create `templates/seasonal/guide.html` and `calendar.html`
    - Guide shows table of produce categories with season badges
    - Calendar shows 12-month grid with `calendar-available` CSS class for available months; zone filter dropdown
    - _Requirements: 6.3, 10.1, 10.3, 10.4, 14.2_

  - [ ] 18.10 Create `templates/stories/story_card.html`
    - Yellow left-border card (`farm-story-card` CSS class from design), story text, optional photo, like count, Like button
    - _Requirements: 11.2, 11.3, 11.5, 14.2_

  - [ ] 18.11 Create `templates/notifications/list.html`
    - List of notifications with unread bold styling, mark-read buttons
    - _Requirements: 12.2, 12.4_

  - [ ] 18.12 Create `templates/admin_panel/dashboard.html`, `audit_log.html`, `moderation_queue.html`
    - Dashboard: Bootstrap 3 KPI stat panels for each metric
    - Audit log: paginated table with entity type, action, admin user, timestamp
    - Moderation queue: flagged content cards with deactivate/remove actions
    - _Requirements: 13.1, 13.5, 13.6, 13.7, 14.2_

- [ ] 19. Build static assets — custom CSS, JavaScript, and logo
  - [ ] 19.1 Create `static/css/agroconnect.css` with all CSS rules from the design
    - CSS custom properties (`--color-primary`, `--color-accent`, `--color-surface`)
    - `.calendar-available`, `.listing-thumb`, `.navbar-default`, `.btn-primary`, `.btn-accent`, `.farm-story-card` classes
    - Ensure `body { padding-top: 70px; }` to compensate for fixed-top navbar
    - _Requirements: 14.2, 14.3_

  - [ ] 19.2 Create `static/js/agroconnect.js` with:
    - jQuery AJAX CSRF setup (`$.ajaxSetup` with `X-CSRFToken` header from `<meta name="csrf-token">`)
    - `updateCountdowns()` function for `.countdown` elements (runs on `setInterval(1000)`)
    - AJAX notification bell refresh (polls `/notifications/unread-count/` every 30 s, updates badge DOM)
    - _Requirements: 14.6, 12.2_

  - [ ] 19.3 Create `static/img/logo.svg` — a minimal SVG green leaf logo (inline SVG or simple path) with "AgroConnect" wordmark
    - _Requirements: 14.6_

- [ ] 20. Checkpoint — Full integration smoke test
  - Run `python manage.py migrate` to apply all migrations
  - Run `python manage.py collectstatic --noinput`
  - Run `python manage.py check` — no errors expected
  - Run `pytest tests/` — all tests must pass
  - Fix any import errors, missing URL names, or template tag errors

- [ ] 21. Write unit tests for all service modules
  - [ ]* 21.1 Write unit tests for `listings/services.py`
    - Happy path: create listing, search, catalogue pagination
    - Error path: missing required field, image too large, image wrong format
    - `verify_listing_access` with correct and incorrect combinations
    - _Requirements: 1.3, 1.4, 1.9, 1.10_

  - [ ]* 21.2 Write unit tests for `negotiations/services.py`
    - Happy path: full offer → counter → accept → deal → order flow
    - Error: offer on inactive listing, counter beyond round 3, accept already-accepted offer
    - `expire_stale_offers` with mix of pending/non-pending offers
    - _Requirements: 4.1–4.9_

  - [ ]* 21.3 Write unit tests for `orders/services.py`
    - Happy path: deal → order → confirm → in-transit → delivered → completed
    - Cancellation at each valid state; cancellation request on in-transit
    - `auto_close_stale_orders` with 7-day-old delivered orders
    - Freshness score submission, duplicate rejection
    - _Requirements: 5.1–5.9, 7.1, 7.5_

  - [ ]* 21.4 Write unit tests for `groupbuy/services.py`
    - Join adds to quantity and count; duplicate join raises error
    - Threshold activation: bulk price applied to all participants
    - `expire_stale_groupbuys` with expired groups
    - _Requirements: 8.1–8.6_

  - [ ]* 21.5 Write unit tests for `broadcasts/services.py`
    - Create broadcast with valid expiry; `get_active_broadcasts` returns only non-expired
    - `record_interest` deduplication; `expire_stale_broadcasts`
    - _Requirements: 9.1–9.6_

  - [ ]* 21.6 Write unit tests for `seasonal/services.py`
    - `evaluate_season_signal` with known fixtures for each agro zone
    - Unknown zone / missing signal → `'off_season'`
    - _Requirements: 6.1, 6.2, 6.4_

  - [ ]* 21.7 Write unit tests for `notifications/services.py`
    - `notify` persists record and triggers SMS for qualifying event types
    - `mark_read`, `get_unread_count`, `purge_old_notifications`
    - SMS failure does not raise (is logged only)
    - _Requirements: 12.1–12.5_

  - [ ]* 21.8 Write unit tests for `stories/services.py`
    - Valid story creation; story with URL rejected; story with phone number rejected
    - Like increments count; duplicate like raises error
    - _Requirements: 11.1, 11.4, 11.5_

  - [ ]* 21.9 Write unit tests for `admin_panel/services.py`
    - `log_admin_action` creates audit log record with all required fields
    - Attempt to update or delete audit log record at service layer is rejected
    - _Requirements: 13.5_

- [ ] 22. Write integration tests
  - [ ]* 22.1 Write integration tests for catalogue and listing views (`tests/integration/test_catalogue_views.py`)
    - Test full catalogue page renders with listed products
    - Test create listing as guest (form submit → reference code display)
    - Test edit/delete with correct and incorrect reference code + phone
    - _Requirements: 1.1–1.7, 3.1–3.8_

  - [ ]* 22.2 Write integration tests for negotiation views (`tests/integration/test_negotiation_views.py`)
    - Offer submission requires login; counter-offer round enforcement; accept flow creates order
    - Thread only visible to participating customer
    - _Requirements: 4.1–4.9_

  - [ ]* 22.3 Write integration tests for order views (`tests/integration/test_order_views.py`)
    - Full deal-to-completed-order lifecycle via test client
    - POD instructions present on order detail page
    - _Requirements: 5.1–5.9_

  - [ ]* 22.4 Write integration tests for admin views (`tests/integration/test_admin_views.py`)
    - Non-admin cannot access admin panel (403)
    - Admin can deactivate listing, remove review, view audit log
    - _Requirements: 13.1–13.7_

  - [ ]* 22.5 Write integration tests for SMS dispatch (`tests/integration/test_sms_dispatch.py`)
    - Use `DummySMSAdapter` (set `SMS_BACKEND='dummy'` in test settings) to record calls
    - Assert SMS sent on new offer, deal accepted, order confirmed, order in transit
    - _Requirements: 12.3_

- [ ] 23. Final checkpoint — All tests pass and project is complete
  - Run `python manage.py migrate` and `python manage.py check`
  - Run `pytest tests/ -v` — all tests must pass
  - Ensure all management commands run without errors: `python manage.py expire_offers`, `expire_broadcasts`, `expire_groupbuys`, `autoclose_orders`, `purge_notifications`, `backup_database`
  - Confirm all URL namespaces resolve: `python manage.py show_urls` (or manually verify each namespace)
  - Ensure all tests pass, ask the user if questions arise.

---

## Notes

- Tasks marked with `*` are optional testing sub-tasks and can be skipped for a faster MVP build
- Every task references specific requirements for full traceability to the 15 requirements and their acceptance criteria
- Checkpoints at tasks 4, 8, 14, 20, and 23 ensure incremental validation throughout the build
- Property tests cover all 32 correctness properties from the design document using Hypothesis
- Background tasks are Django management commands (no Celery required) — wire to cron in production
- SMS backend defaults to `'console'` in development; switch to `'africastalking'` in production via environment variable
