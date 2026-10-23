# GLOSSARY.md format

## Structure

```md
# {Context name}

{One or two sentences: what this context is and why it exists.}

## Language

**Order**:
A customer's request to buy one or more products, from placement until fulfilment or cancellation.
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organisation that places orders.
_Avoid_: Client, buyer, account
```

## Rules

- **Be opinionated.** When several words exist for one concept, pick the best and list the others under `_Avoid_`.
- **Keep definitions tight.** One or two sentences: what the term IS, not what it does.
- **Only project-specific terms.** General programming concepts (timeouts, retries, error types) do not belong, however often the project uses them. Before adding a term ask: is this unique to this domain, or general engineering vocabulary?
- **Group terms under subheadings** when natural clusters appear; a flat list is fine for one cohesive area.
- **Write the glossary in the language the team speaks about the domain.** If the business speaks Vietnamese, the terms may be Vietnamese with the English identifier used in code in parentheses, e.g. `**Đơn hàng** (Order)`.

## Several contexts

A root `GLOSSARY-MAP.md` lists the contexts, where they live and how they relate:

```md
# Glossary map

## Contexts

- [Ordering](./src/ordering/GLOSSARY.md): receives and tracks customer orders
- [Billing](./src/billing/GLOSSARY.md): generates invoices and processes payments

## Relationships

- **Ordering → Billing**: Ordering emits `OrderPlaced`; Billing consumes it to create an Invoice
- **Ordering ↔ Billing**: shared `CustomerId` and `Money` types
```

Which structure applies:

- `GLOSSARY-MAP.md` exists → read it to find the contexts.
- Only a root `GLOSSARY.md` → single context.
- Neither → create a root `GLOSSARY.md` lazily when the first term is resolved.
