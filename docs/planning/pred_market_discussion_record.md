# Pred-Market V1 Discussion Record

This document summarizes the prediction market concepts discussed so far, excluding the separate AI testing platform architecture.

## 1. Basic Prediction Market Model

Pred-Market V1 is being thought of as a Kalshi/Polymarket-style prediction market.

A market asks an objective question:

```text
Will India win the 2026 World Cup?
```

The market has two possible trading sides:

```text
YES
NO
```

Each side is represented as a contract/share. If the user is correct, the contract pays a fixed payout. If the user is wrong, it pays zero.

Example:

```text
Payout per winning contract = ₹100

YES wins -> YES contract pays ₹100, NO pays ₹0
NO wins  -> NO contract pays ₹100, YES pays ₹0
```

## 2. Who Creates The Contract?

In a Kalshi-style system, the user does not create the contract just by placing a bet.

The platform creates/lists the market and defines the contract.

The platform decides:

```text
- market question
- YES condition
- NO condition
- closing time
- settlement source
- payout amount
- tick size
- allowed order size
- market rules
```

Users may suggest markets, but the platform still reviews, approves, and lists them.

## 3. Market vs Contract vs Order Book

These are different layers.

```text
Market
  -> Contract
      -> Order book
          -> Orders
              -> Trades
```

Example:

```text
Market:
Will India win the 2026 World Cup?

Contract:
YES pays ₹100 if India wins.
NO pays ₹100 if India does not win.

Order book:
John wants to buy YES at ₹40.
Mary wants to buy NO at ₹60.
Alex wants to sell YES at ₹45.
```

## 4. Who Decides The Price?

The platform decides the payout amount.

The traders decide the price through orders and trades.

Example:

```text
Payout = ₹100
YES trades at ₹30
NO trades at ₹70
```

This roughly means:

```text
YES implied probability = 30%
NO implied probability = 70%
```

Prices are volatile. They move when traders change their beliefs based on new information.

## 5. Why YES + NO Equals The Payout

For a fully collateralized binary contract:

```text
YES price + NO price = payout
```

Example:

```text
Payout = ₹100

YES price = ₹30
NO price = ₹70

₹30 + ₹70 = ₹100
```

This matters because the platform must have enough locked money to pay the winner.

If YES wins:

```text
YES holder receives ₹100
NO holder receives ₹0
```

If NO wins:

```text
NO holder receives ₹100
YES holder receives ₹0
```

## 6. What Happens When Orders Do Not Match?

Orders only trade when the prices are compatible.

Example:

```text
Payout = ₹73

A wants to buy YES at ₹30
B wants to buy NO at ₹25

₹30 + ₹25 = ₹55
```

This does not match because the payout is ₹73.

Missing amount:

```text
₹73 - ₹55 = ₹18
```

So no trade happens. Both orders wait in the order book.

For A's YES order at ₹30 to match, someone must take the NO side at:

```text
₹73 - ₹30 = ₹43
```

## 7. One Trader vs Many Traders

A single trader can be matched against many traders.

Example:

```text
Payout = ₹73

A wants to buy 10 YES at ₹30
```

The matching NO price must be:

```text
₹73 - ₹30 = ₹43
```

Now:

```text
C buys 3 NO at ₹43
D buys 5 NO at ₹43
E buys 2 NO at ₹43
```

Together they fill A's full order.

Final:

```text
A gets 10 YES
C gets 3 NO
D gets 5 NO
E gets 2 NO
```

Trader B might have wanted:

```text
B buys 2 NO at ₹25
```

But B does not match A because:

```text
₹30 + ₹25 = ₹55
```

B remains unmatched until a YES trader arrives at:

```text
₹73 - ₹25 = ₹48
```

## 8. Many Traders vs Many Traders

Trades can be:

```text
1 vs 1
1 vs many
many vs 1
many vs many
```

The exchange does not care how many people are on each side. It only cares that each matched contract is fully funded.

Rule:

```text
executed YES price + executed NO price = payout
```

## 9. Liquidity

A good liquid market is a market where traders can buy or sell meaningful quantity quickly, at prices close to the current fair market price, without causing a large price movement.

In simple words:

```text
A liquid market has enough buyers and sellers, at close prices, so users can enter or exit easily.
```

Good liquidity usually means:

```text
- tight spread
- good depth
- frequent trades
- low slippage
- easy exit
```

Example of a liquid market:

```text
Best YES buyer: ₹30
Best YES seller: ₹31
Spread: ₹1
```

Example of low liquidity:

```text
Best YES buyer: ₹20
Best YES seller: ₹45
Spread: ₹25
```

The earlier examples with only a few traders were low-liquidity examples.

## 10. Sportsbook Odds vs Prediction Exchange

A simpler-looking system would be:

```text
India wins: 1.5x
India loses: 3.0x
```

User bets:

```text
₹100 on India wins at 1.5x
If India wins, user receives ₹150 total
```

This is easier for users, but it is a sportsbook/bookmaker model.

In that model:

```text
User bets against the platform.
Platform takes the opposite risk.
```

Problem:

```text
If too many users bet on the winning side,
the platform may lose money.
```

In a prediction exchange:

```text
Users trade against other users.
The platform matches orders.
The platform does not need to take directional risk.
```

The frontend can still show simple odds, but internally the system can store contract prices.

Example:

```text
Payout = ₹100
YES price = ₹66.67
NO price = ₹33.33
```

This can be displayed as:

```text
YES odds ≈ 1.5x
NO odds ≈ 3.0x
```

## 11. Kalshi vs Polymarket

Both follow a similar economic idea:

```text
YES/NO contracts
prices set by users
order book based trading
winning side receives fixed payout
losing side receives zero
```

Main difference:

```text
Kalshi:
Regulated event-contract exchange.

Polymarket:
Crypto/onchain prediction market using outcome tokens.
```

## 12. Pred-Market V1 Architecture Created

A system architecture SVG was created for the whole Pred-Market V1 concept:

```text
../architecture/pred_market_v1_architecture.svg
```

It includes:

```text
- clients and access
- API and identity edge
- market lifecycle
- market approval
- contract definition
- order API
- order book
- matching engine
- collateral lock
- wallet
- escrow
- settlement
- oracle source
- risk controls
- liquidity monitoring
- analytics
- observability
- storage
```

Core V1 boundary:

```text
Pred-Market V1 should behave like an exchange-style matcher and ledger,
not like a bookmaker taking directional risk against users.
```
