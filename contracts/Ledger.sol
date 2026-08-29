// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./ProtocolStorage.sol";
import "./CircuitBreaker.sol";

/*
Ledger
======
Tracks:
- Trade execution
- Portfolio state
- PnL calculation
- Full audit trail

Aligned with:
- Eq. 3.3 (PnL, Portfolio Value)
*/

contract Ledger is ProtocolStorage {

    // --------------------------------------------------
    // STRUCTS
    // --------------------------------------------------

    struct Trade {
        uint256 id;
        address user;
        string symbol;
        bool isBuy;
        uint256 price;
        uint256 quantity;
        uint256 timestamp;
        uint256 confidence;
    }

    // ⚠️ RENAMED to avoid conflict with ProtocolStorage.Position
    struct AssetPosition {
        uint256 quantity;
        uint256 avgEntryPrice;
    }

    // --------------------------------------------------
    // STORAGE
    // --------------------------------------------------

    uint256 public nextTradeId;

    mapping(uint256 => Trade) public trades;
    mapping(address => uint256[]) public userTrades;

    // ⚠️ RENAMED mapping (DO NOT use "positions")
    mapping(address => mapping(string => AssetPosition)) public assetPositions;

    mapping(address => int256) public userPnL;

    // ❌ REMOVED duplicate circuitBreaker declaration
    // Using address from ProtocolStorage instead

    // --------------------------------------------------
    // EVENTS
    // --------------------------------------------------

    event TradeExecuted(
        uint256 id,
        address user,
        string symbol,
        bool isBuy,
        uint256 price,
        uint256 quantity,
        uint256 confidence
    );

    event PositionUpdated(
        address user,
        string symbol,
        uint256 quantity,
        uint256 avgPrice
    );

    event PnLUpdated(address user, int256 pnl);

    // --------------------------------------------------
    // EXECUTE TRADE
    // --------------------------------------------------

    function recordTrade(
        address user,
        string calldata symbol,
        bool isBuy,
        uint256 price,
        uint256 quantity,
        uint256 confidence
    )
        external
    {
        // ✅ FIX: use storage address
        require(
            !CircuitBreaker(circuitBreaker).paused(),
            "Trading Paused"
        );

        trades[nextTradeId] = Trade({
            id: nextTradeId,
            user: user,
            symbol: symbol,
            isBuy: isBuy,
            price: price,
            quantity: quantity,
            timestamp: block.timestamp,
            confidence: confidence
        });

        userTrades[user].push(nextTradeId);

        _updatePosition(user, symbol, isBuy, price, quantity);

        emit TradeExecuted(
            nextTradeId,
            user,
            symbol,
            isBuy,
            price,
            quantity,
            confidence
        );

        nextTradeId++;
    }

    // --------------------------------------------------
    // POSITION + PnL (Eq. 3.3)
    // --------------------------------------------------

    function _updatePosition(
        address user,
        string memory symbol,
        bool isBuy,
        uint256 price,
        uint256 quantity
    )
        internal
    {
        AssetPosition storage pos = assetPositions[user][symbol];

        if (isBuy) {

            uint256 totalCost =
                (pos.avgEntryPrice * pos.quantity) +
                (price * quantity);

            uint256 newQty = pos.quantity + quantity;

            pos.quantity = newQty;
            pos.avgEntryPrice = totalCost / newQty;

        } else {

            require(pos.quantity >= quantity, "Not enough shares");

            int256 pnl =
                int256(price - pos.avgEntryPrice) *
                int256(quantity);

            userPnL[user] += pnl;

            pos.quantity -= quantity;

            emit PnLUpdated(user, userPnL[user]);
        }

        emit PositionUpdated(
            user,
            symbol,
            pos.quantity,
            pos.avgEntryPrice
        );
    }

    // --------------------------------------------------
    // VIEW FUNCTIONS
    // --------------------------------------------------

    function getUserTrades(address user)
        external
        view
        returns (uint256[] memory)
    {
        return userTrades[user];
    }

    function getPosition(address user, string calldata symbol)
        external
        view
        returns (uint256 quantity, uint256 avgPrice)
    {
        AssetPosition memory p = assetPositions[user][symbol];
        return (p.quantity, p.avgEntryPrice);
    }

    function getPnL(address user)
        external
        view
        returns (int256)
    {
        return userPnL[user];
    }

    // --------------------------------------------------
    // VALUE CALCULATION
    // --------------------------------------------------

    function computePositionValue(
        address user,
        string calldata symbol,
        uint256 currentPrice
    )
        external
        view
        returns (uint256)
    {
        AssetPosition memory p = assetPositions[user][symbol];
        return p.quantity * currentPrice;
    }
}