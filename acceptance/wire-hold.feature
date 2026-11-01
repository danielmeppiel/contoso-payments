Feature: Hold large wires to new payees
  Contoso Bank holds an outgoing wire of $10,000.00 (1000000 cents) or more
  to a payee the account has never paid before, until a second person
  approves it. Wires to known payees, and smaller wires, are released as
  before. Amounts are integer cents.

  Background:
    Given account "ACC-001" has already paid "Northwind Traders"

  Scenario: Just below $10,000 to a new payee is released
    When account "ACC-001" wires 999999 cents to "Fabrikam"
    Then the wire is RELEASED
    And nothing is waiting for approval

  Scenario: $10,000 to a new payee is held for a second approval
    When account "ACC-001" wires 1000000 cents to "Fabrikam"
    Then the wire is HELD
    And the wire is waiting for approval
    And the wire is not in the ledger

  Scenario: $50,000 to a known payee is released
    When account "ACC-001" wires 5000000 cents to "Northwind Traders"
    Then the wire is RELEASED
    And nothing is waiting for approval

  Scenario: A payee known to another account is still new
    When account "ACC-002" wires 1000000 cents to "Northwind Traders"
    Then the wire is HELD
    And the wire is waiting for approval

  Scenario Outline: Invalid amounts are rejected
    When account "ACC-001" submits an amount of <amount> to "Fabrikam"
    Then the wire is rejected with <error>
    And nothing is waiting for approval

    Examples:
      | amount    | error      |
      | -1        | ValueError |
      | 0         | ValueError |
      | true      | TypeError  |
      | 1000000.0 | TypeError  |
      | "1000000" | TypeError  |
