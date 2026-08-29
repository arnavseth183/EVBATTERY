// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./RiskManager.sol";
import "./PortfolioManager.sol";
import "./OracleInterface.sol";
import "./CircuitBreaker.sol";

/*
ProtocolStorage
===============
Central storage layer for upgradeable architecture.

Aligned with:
- Eq. 3.1 (Circuit Breaker)
- Eq. 3.2 (AI Threshold τ)
- Eq. 3.3 (PnL + Portfolio Value)
- Execution Cost Model
*/

contract ProtocolStorage {

    /* ========== STRUCTS ========== */

    struct Position {
        address trader;
        address asset;
        uint256 size;
        uint256 entryPrice;
        uint256 timestamp;
        bool isLong;
        bool isOpen;
    }

    struct Portfolio {
        uint256 totalValue;   // V = Σ(Q × P)
        int256 pnl;           // PnL = (Pexit - Pentry) × Q
        uint256 openPositions;
        uint256 riskScore;
    }

    struct RiskParameters {
        uint256 maxLeverage;
        uint256 maxPositionSize;
        uint256 liquidationThreshold;
        uint256 maxDrawdown;
    }

    /* ========== CORE ADDRESSES ========== */

    address public owner;
    address public governance;

    address public oracle;
    address public riskManager;
    address public portfolioManager;
    address public tradingProtocol;   // ✅ FIXED (MISSING BEFORE)
    address public circuitBreaker;

    /* ========== SYSTEM PARAMETERS ========== */

    uint256 public confidenceThreshold = 65;
    uint256 public transactionCost = 10;
    uint256 public slippage = 5;
    uint256 public circuitBreakerThreshold = 40;
    uint256 public riskFreeRate = 5;

    /* ========== PROTOCOL METRICS ========== */

    uint256 public protocolFee;
    uint256 public totalOpenInterest;

    /* ========== STORAGE ========== */

    mapping(uint256 => Position) internal positions;
    mapping(address => Portfolio) internal portfolios;
    mapping(address => uint256[]) internal userPositions;

    RiskParameters public riskParams;

    uint256 internal nextPositionId;

    /* ========== EVENTS ========== */

    event OwnershipTransferred(address indexed oldOwner, address indexed newOwner);
    event GovernanceUpdated(address indexed newGov);
    event OracleUpdated(address indexed newOracle);
    event RiskManagerUpdated(address indexed newRiskManager);
    event PortfolioManagerUpdated(address indexed newPM);
    event TradingProtocolUpdated(address indexed newTP); // ✅ NEW
    event CircuitBreakerUpdated(address indexed newCB);

    event ParameterUpdated(string parameter, uint256 value);

    /* ========== MODIFIERS ========== */

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier onlyGovernance() {
        require(msg.sender == governance, "Not governance");
        _;
    }

    /* ========== CONSTRUCTOR ========== */

    constructor() {
        owner = msg.sender;
        nextPositionId = 1;
        protocolFee = 20;
    }

    /* ========== ADMIN SETTERS ========== */

    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Zero address");
        emit OwnershipTransferred(owner, newOwner);
        owner = newOwner;
    }

    function setGovernance(address _gov) external onlyOwner {
        governance = _gov;
        emit GovernanceUpdated(_gov);
    }

    function setOracle(address _oracle) external onlyOwner {
        oracle = _oracle;
        emit OracleUpdated(_oracle);
    }

    function setRiskManager(address _risk) external onlyOwner {
        riskManager = _risk;
        emit RiskManagerUpdated(_risk);
    }

    function setPortfolioManager(address _pm) external onlyOwner {
        portfolioManager = _pm;
        emit PortfolioManagerUpdated(_pm);
    }

    function setTradingProtocol(address _tp) external onlyOwner {
        tradingProtocol = _tp;
        emit TradingProtocolUpdated(_tp);
    }

    function setCircuitBreaker(address _cb) external onlyOwner {
        circuitBreaker = _cb;
        emit CircuitBreakerUpdated(_cb);
    }

    /* ========== GOVERNANCE CONTROL ========== */

    function updateConfidenceThreshold(uint256 value) external onlyGovernance {
        confidenceThreshold = value;
        emit ParameterUpdated("CONFIDENCE_THRESHOLD", value);
    }

    function updateTransactionCost(uint256 value) external onlyGovernance {
        transactionCost = value;
        emit ParameterUpdated("TRANSACTION_COST", value);
    }

    function updateSlippage(uint256 value) external onlyGovernance {
        slippage = value;
        emit ParameterUpdated("SLIPPAGE", value);
    }

    function updateCircuitBreakerThreshold(uint256 value) external onlyGovernance {
        circuitBreakerThreshold = value;
        emit ParameterUpdated("CIRCUIT_BREAKER_THRESHOLD", value);
    }

    function updateRiskFreeRate(uint256 value) external onlyGovernance {
        riskFreeRate = value;
        emit ParameterUpdated("RISK_FREE_RATE", value);
    }
}