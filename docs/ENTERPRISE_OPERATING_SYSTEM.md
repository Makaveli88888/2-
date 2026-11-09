# JOKER Enterprise Operating System — Portfolio & Deployment Blueprint

**Status:** architecture baseline / implementation plan  
**Owner:** JOKER programme leadership  
**Scope:** international project portfolio, AI/data-centre infrastructure, EU funding, tenders, partners, procurement, finance and delivery  
**Rule:** this document is a plan, not evidence of a registered group, awarded grants, secured land, grid connection, permits, financing or signed partners.

## 1. Executive operating model

JOKER is to be managed as a portfolio of legally and financially separated projects, coordinated by one operating system. The platform should provide a single source of truth for decisions, documents, budgets, risks, deadlines, partners, tenders and delivery status.

The system must never confuse:
- idea / lead / draft / submitted / evaluated / awarded / contracted / paid;
- indicative budget with a funded budget;
- a partner lead with an executed agreement;
- a site concept with land title, planning permission or grid capacity;
- an AI-generated draft with an approved submission.

Every material fact has an owner, source, date, confidence and verification state.

## 2. Project portfolio

### Infrastructure and energy
- JOKER DATA CENTER / JOKER EUROPEAN AI GRID: Polish AI compute and data-centre campus; target 100 MW+; complete power, cooling, fibre, security and operations stack.
- JOKER ENERGY: grid capacity, energy sourcing, PPAs, backup, storage, heat recovery, water and efficiency.
- JOKER COMPUTE: GPU clusters, storage, high-speed network, orchestration, cloud and compute services.
- JOKER AI RESEARCH: model evaluation, applied research, industrial use cases and sovereign AI services.

### Software and security
- JOKER GOD MODE / JokerGodAI: multi-agent operating platform and enterprise automation.
- Guardian Angel: policy enforcement, data protection, tool-call authorization, immutable/tamper-evident audit and incident response.
- JOKER TENDER ENGINE: TED and national procurement discovery, qualification, bid/no-bid, consortium and supplier sourcing.
- JOKER REVENUE ENGINE: sales pipeline, offers, CRM, subscriptions and revenue reporting.

### Commercial and logistics
- JOKER AUTO GLOBAL: sourcing and brokerage on buyer and seller sides, verified counterparties, vehicle due diligence and logistics.
- JOKER FREIGHT DESK: freight leads, carrier and shipper qualification, route and margin estimates, document control.
- FOLLOW THE RABBIT: curated strategic partner network across AI, infrastructure, energy, vendors, construction, capital, logistics and sales.
- JokerAl Hub / PATRYSJOKER: digital products, AI assistant, audience, subscriptions and distribution.

Projects can share services, but must have separate budgets, contracts, owners, risk registers and evidence trails.

## 3. Enterprise platform modules

1. **Portfolio PMO** — project charter, stage gates, owner, milestones, dependencies, RAG status, decisions and change control.
2. **Funding & Grants Engine** — call database, eligibility rules, deadline calendar, funding-rate calculator, partner roles, application checklist, submission evidence, reporting and audit.
3. **Tender Engine** — TED/national tender ingestion, CPV classification, qualification, bid/no-bid, compliance matrix, consortium map, supplier quotes and bid-room.
4. **Partner CRM** — legal entity verification, beneficial ownership/KYC where appropriate, sanctions screening, references, NDA, MoU, scope, capacity and relationship history.
5. **Procurement & Supply Chain** — RFQ, technical compliance, three-way quote comparison, lead times, warranties, logistics, supplier risk and purchase approvals.
6. **Finance & FP&A** — project-level CAPEX/OPEX, cash flow, VAT/tax assumptions, FX, contingencies, financing sources, drawdown conditions, runway and sensitivity cases.
7. **Data Room & Document Control** — versioned evidence, access permissions, retention, signatures, source citations and immutable event history.
8. **Risk, Legal & Compliance** — risk register, permit tracker, state-aid analysis, procurement rules, GDPR, cybersecurity, export controls, insurance and contract obligations.
9. **Delivery & Operations** — engineering work packages, design reviews, construction progress, commissioning, SLA, maintenance, incident and ESG reporting.
10. **Global Intelligence** — country-specific market, regulatory, partner, energy, construction, procurement and funding intelligence, with source/date and local legal review.

## 4. Agent architecture and permission model

- **Orchestrator:** routes tasks, creates work plans, assigns deadlines and tracks dependencies.
- **Research Agent:** gathers public evidence and cites every material claim.
- **Funding Agent:** checks eligibility and drafts grant/tender matrices; cannot submit.
- **Tender Agent:** scores opportunities and prepares bid/no-bid recommendations.
- **Technical Agent:** develops requirements, capacity models, design options and acceptance tests.
- **Finance Agent:** prepares scenarios, cash-flow and financing models; cannot approve payments.
- **Partner Agent:** builds a qualified partner pipeline; cannot sign agreements or make binding offers.
- **Sceptyk / Risk Agent:** independently challenges assumptions, source quality, eligibility, budget and risk.
- **Executor:** performs only allow-listed reversible tasks.
- **Guardian Angel:** policy enforcement before every external tool call, data export, communication or write action.

### Mandatory approval gates
Human approval is required before:
- sending an external email or proposal;
- submitting a grant application or tender;
- signing, accepting or amending a contract / NDA / MoU;
- making a purchase, payment, transfer or binding commitment;
- changing production infrastructure, access rights or security policies;
- publishing sensitive company or project information.

Default deny. Every action must have an actor, purpose, permission, input hash, output, timestamp and approval record.

## 5. Data model — minimum records

- Organisation, legal_entity, beneficial_owner, user, role, permission
- Project, work_package, milestone, dependency, decision, change_request
- Site, parcel, title_evidence, zoning, permit, grid_connection, utility_capacity
- Funding_call, eligibility_rule, application, consortium, partner_commitment, submission_receipt, award, payment_claim
- Tender, buyer, lot, CPV, qualification, bid_decision, bid_submission, supplier, quotation
- Contract, obligation, invoice, payment, budget_line, forecast, financing_facility
- Risk, issue, control, incident, audit_event, evidence_document
- Asset, equipment, GPU_cluster, power_system, cooling_system, network_link, SLA

All records require IDs, project ownership, timestamps, source/evidence links and status history.

## 6. JOKER DATA CENTER — investment workstream

Working target carried forward from the current project brief:
- compute campus target: 100 MW+;
- modelled construction employment: about 1,500 during construction;
- modelled permanent employment: about 600 at full operation;
- location described by the owner as land in possession, but exact parcel, title, area and planning status still require documentary verification.

A previous financial scenario used 100 MW IT load and PUE 1.25 (about 125 MW facility demand), with a modelled CAPEX of PLN 28 billion. These are scenario assumptions, not quotations, a bankable feasibility study, a funding award or a validated engineering design.

### Critical path / stage gates
1. **Site proof:** parcel IDs, title register, encumbrances, cadastral area, zoning/land-use, access and environmental constraints.
2. **Power proof:** formal grid-connection application, available capacity, connection conditions, delivery schedule, cost and redundancy.
3. **Engineering basis:** IT load vs facility load, phased capacity, PUE/WUE, cooling architecture, water, fibre routes, backup power, fire and physical security.
4. **Commercial proof:** GPU/OEM quotes, EPC/MEP bids, network/fibre offers, energy term sheets, anchor tenants and compute off-take commitments.
5. **Bankability:** independent feasibility study, CAPEX/OPEX, 36-month construction cash flow, contingencies, debt/equity, DSCR, downside cases and sensitivity.
6. **Permits and ESG:** planning, building, environmental, water, grid, fire, construction and operating permits as applicable.
7. **Consortium and financing:** lead entity, partner roles, national commitments, state-aid treatment, equity, debt, guarantees and public support.
8. **Procurement and delivery:** tender strategy, EPC packages, long-lead equipment, construction controls, commissioning and operating model.

No construction mobilisation should be represented as ready until the critical permits, grid, financing and EPC path are evidenced.

## 7. Funding and procurement radar — verified 9 November 2026

### Priority A — EuroHPC AI Gigafactories
Reference: EUROHPC-2026-CEI-AIGF-01.
- Lot 1 deadline was extended on 5 November 2026 to **4 February 2027, 17:00 CET**.
- Lot 2 deadline remains **3 December 2026, 17:00 CET**.
- The authority says current draft and submitted tenders in the portal will not be considered; tenders must be recreated and resubmitted using new submission links, which are to be announced.
- The programme seeks consortia to establish and operate sovereign AI compute infrastructure, with energy-efficient data centres, large-scale compute, energy and water efficiency, and circularity.

**JOKER action:** urgently map the consortium route and distinguish (a) becoming a consortium member / site / infrastructure partner from (b) leading a full AIGF tender. Obtain official new links and full tender documents before preparing or submitting anything.

### Priority B — Chips JU AI compute infrastructure calls
- DIGITAL-JU-CHIPS-2026-AI1-SG: €10m indicative budget; 50% funding rate; deadline **1 December 2026**.
- DIGITAL-JU-CHIPS-2026-AI-GFP: €70m indicative budget; 50% funding rate; deadline **1 December 2026**.
- These are specialised AI-chip demonstrator / compute evaluation and deployment opportunities. They are not a generic subsidy for building any data centre. Eligibility, consortium composition, security restrictions and work programme rules must be checked against the call documents.

### Priority C — Polish FENG instruments
- FENG 01.01 Ścieżka SMART B+R: listed deadline **29 December 2026**; potentially relevant to eligible R&D work packages, not automatically to the full civil construction CAPEX.
- FENG 02.14 Horizon Bridge: advisory support up to PLN 66,000; listed deadline **15 December 2026**; useful for Horizon Europe preparation, not data-centre construction finance.
- FENG 01.02 digital/green transformation loans: listed through **31 March 2029**; debt instrument, not a grant.

### Procurement opportunities to qualify
- EUROHPC/2026/OP/0012 PIAST AI-Optimised Supercomputer: estimated €59.5m, deadline 10 December 2026. Potential supplier/consortium opportunity for qualified hardware, integration, energy, cooling, network and service firms.
- EUROHPC/2026/OP/0010 INNOVATE industrial supercomputer: estimated €11.615m, deadline 25 November 2026. Potential supply-chain opportunity, subject to tender qualification.

A call appearing open is not proof that JOKER is eligible or that an application has been submitted. The system must store the official call documents and an eligibility decision before creating a bid pack.

## 8. Global operating rules

- Maintain a country matrix: company establishment, tax, labour, construction, energy, data protection, sanctions, export controls, state aid and procurement law.
- Use local counsel and qualified engineering advisers for each jurisdiction.
- Store currency, FX source/date, tax basis and local time zone with every financial or deadline record.
- Separate public facts, partner claims, estimates, owner-provided facts and verified documentary evidence.
- No agent may invent permits, land rights, funding, partner commitments, references, prices or customer demand.
- Do not use one country’s legal or grant assumptions in another country without validation.

## 9. Implementation roadmap

### Sprint 0 — repository quality gate
- run all tests on a clean Python 3.12 environment;
- fix failing tests and pin reproducible dependency versions;
- add API auth tests, rate limiting, structured logging and secret scanning;
- produce a security review and SBOM;
- do not merge to main until CI is green.

### Sprint 1 — enterprise core
- project registry, legal entity registry, role-based access, approvals, audit events;
- project-level budgets, milestone and risk registers;
- secure document/evidence vault with versioning.

### Sprint 2 — grants and tender engine
- call/tender ingestion, eligibility matrix, deadlines, bid/no-bid scoring;
- consortium and supplier CRM, evidence checklist, submission receipt tracking.

### Sprint 3 — data-centre investment room
- site, grid, energy, engineering, permits, EPC, GPU and anchor-tenant workstreams;
- CAPEX/OPEX/cash flow model with scenarios and traceable assumptions;
- lender/investor data room and due-diligence checklist.

### Sprint 4 — global commercial operations
- Auto Global, Freight Desk, Revenue Engine, partner network and customer CRM;
- country and language packs, sales approvals, margin controls and reporting.

### Sprint 5 — controlled agent autonomy
- agents may research, classify, draft, compare, forecast and monitor;
- external communications and commitments remain approval-gated;
- continuous security, red-team, disaster-recovery and audit testing.

## 10. Go-live acceptance criteria

- clean install and repeatable test pass on supported Python version;
- no critical/high security findings unresolved;
- authentication, tenant/project isolation and least privilege tested;
- backups and restore drill completed;
- audit trail and approval evidence verified;
- every grant/tender status backed by official source and submission receipt;
- financial model reviewed by independent finance and engineering specialists;
- production monitoring, incident response and named accountable owners in place.
