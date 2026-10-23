# Good and bad tests

Examples are TypeScript and Python; the rules hold in any language.

## Good tests

**Integration-style**: exercise real interfaces, not mocks of internal parts.

```typescript
// GOOD: tests observable behaviour
test("user can checkout with valid cart", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

Characteristics:

- tests behaviour that users or callers care about;
- uses the public interface only;
- survives internal refactors;
- describes WHAT, not HOW;
- one logical assertion per test.

## Bad tests

**Implementation-detail tests** are coupled to internal structure.

```typescript
// BAD: tests implementation details
test("checkout calls paymentService.process", async () => {
  const mockPayment = jest.mock(paymentService);
  await checkout(cart, payment);
  expect(mockPayment.process).toHaveBeenCalledWith(cart.total);
});
```

Red flags:

- mocking internal collaborators;
- testing private methods;
- asserting on call counts or call order;
- the test breaks on a refactor without a behaviour change;
- the test name describes HOW, not WHAT;
- verifying through external means instead of the interface.

```python
# BAD: bypasses the interface to verify
def test_create_user_saves_to_database(db):
    create_user(name="Alice")
    assert db.execute("SELECT * FROM users WHERE name = ?", ("Alice",)).fetchone()

# GOOD: verifies through the interface
def test_created_user_is_retrievable():
    user = create_user(name="Alice")
    assert get_user(user.id).name == "Alice"
```

**Tautological tests** restate the implementation, so they pass by construction.

```typescript
// BAD: expected value recomputed the way the code computes it
test("calculateTotal sums line items", () => {
  const items = [{ price: 10 }, { price: 5 }];
  const expected = items.reduce((sum, i) => sum + i.price, 0);
  expect(calculateTotal(items)).toBe(expected);
});

// GOOD: expected value is an independent, known literal
test("calculateTotal sums line items", () => {
  expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
});
```

## Naming from acceptance criteria

Name tests after the behaviour in the task's acceptance criterion, in the glossary's words:
`"rejected credentials do not reveal whether the account exists"`, not `"test_login_2"`.
