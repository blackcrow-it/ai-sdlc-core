# When to mock

Mock at **system boundaries** only:

- external APIs (payments, e-mail, SMS, third-party SaaS);
- databases, sometimes: prefer a real test database or an embedded stand-in;
- time and randomness;
- the file system, sometimes.

Do not mock:

- your own classes and modules;
- internal collaborators;
- anything you control.

## Designing for mockability

At system boundaries, design interfaces that are easy to replace.

**1. Inject dependencies**

```typescript
// Easy to mock
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// Hard to mock
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

**2. Prefer SDK-style interfaces over generic fetchers**

```typescript
// GOOD: each operation is independently mockable
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch("/orders", { method: "POST", body: data }),
};

// BAD: the mock needs conditional logic
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

The SDK shape means each mock returns one specific shape, test setup has no conditionals, it is obvious which
operations a test exercises, and types hold per operation.

## Secrets in tests

Tests never read real credentials. Use obviously fake values (`"test-key"`) and inject them; a test that needs a real
secret to pass belongs to a human-run environment, not to the agent's loop.
