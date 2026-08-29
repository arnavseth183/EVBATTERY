// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/*
Oracle Interface
================
External AI / price oracle interface

Aligned with:
- Eq. 3.1 (Circuit Breaker Logic)
- Eq. 3.2 (AI Decision Model)
- Eq. 5.1 (Log Return)
- Risk Metrics (VaR, CVaR, Volatility)

Purpose:
- Bridge off-chain AI + market data → on-chain execution
*/

interface OracleInterface {

    // --------------------------------------------------
    // CORE MARKET DATA
    // --------------------------------------------------

    function getPrice(address asset) external view returns (uint256);

    // Reference price used for circuit breaker comparison (Pref)
    function getReferencePrice(address asset) external view returns (uint256);

    // Volatility (σ)
    function getVolatility(address asset) external view returns (uint256);

    // Log return (Eq. 5.1)
    function getLogReturn(address asset) external view returns (int256);

    // --------------------------------------------------
    // AI MODEL OUTPUT (Eq. 3.2)
    // --------------------------------------------------

    // Probability p(c | xt)
    function getConfidenceScore(address asset) external view returns (uint256);

    // Predicted class (0 = DOWN, 1 = UP)
    function getPrediction(address asset) external view returns (uint8);

    // Final signal
    // 0 = HOLD, 1 = BUY, 2 = SELL
    function getSignal(address asset) external view returns (uint8);

    // Decision threshold τ (governance controlled)
    function getThreshold() external view returns (uint256);

    // --------------------------------------------------
    // RISK METRICS
    // --------------------------------------------------

    function getRiskScore(address user) external view returns (uint256);

    function getVaR(address asset) external view returns (uint256);

    function getCVaR(address asset) external view returns (uint256);

    // --------------------------------------------------
    // MARKET CONDITIONS
    // --------------------------------------------------

    function isMarketOpen() external view returns (bool);

    // Circuit breaker status based on Eq. 3.1
    function isCircuitBreakerTriggered(address asset) external view returns (bool);

    // --------------------------------------------------
    // DASHBOARD OPTIMIZATION (BATCH FETCH)
    // --------------------------------------------------

    function getBatchData(address asset)
        external
        view
        returns (
            uint256 price,
            uint256 referencePrice,
            uint256 volatility,
            uint256 confidence,
            uint8 signal
        );
}