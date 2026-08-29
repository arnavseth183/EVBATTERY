// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./RiskManager.sol";
import "./PortfolioManager.sol";
import "./OracleInterface.sol";
import "./CircuitBreaker.sol";
import "./ProtocolStorage.sol";

contract UserRegistry is ProtocolStorage {

    // --------------------------------------------------
    // STRUCT
    // --------------------------------------------------

    struct User {
        address wallet;
        bytes32 usernameHash;
        bytes32 privateKeyHash;

        uint256 createdAt;
        uint256 lastActive;

        uint256 totalTrades;
        uint256 successfulTrades;

        bool exists;
        bool isActive;
    }

    // --------------------------------------------------
    // STORAGE
    // --------------------------------------------------

    mapping(address => User) public users;
    mapping(bytes32 => address) public usernameToWallet;

    // --------------------------------------------------
    // EVENTS
    // --------------------------------------------------

    event UserRegistered(address indexed user, string username);
    event UserActivityUpdated(address indexed user, uint256 timestamp);
    event TradeRecorded(address indexed user, bool success);
    event RecoveryValidated(address indexed user);

    // --------------------------------------------------
    // REGISTER
    // --------------------------------------------------

    function registerUser(
        string calldata username,
        bytes32 privateKeyHash
    ) external {

        require(bytes(username).length > 0, "Invalid username");
        require(privateKeyHash != bytes32(0), "Invalid key");

        require(!users[msg.sender].exists, "Already registered");

        bytes32 unameHash = keccak256(abi.encodePacked(username));
        require(usernameToWallet[unameHash] == address(0), "Username taken");

        users[msg.sender] = User({
            wallet: msg.sender,
            usernameHash: unameHash,
            privateKeyHash: privateKeyHash,
            createdAt: block.timestamp,
            lastActive: block.timestamp,
            totalTrades: 0,
            successfulTrades: 0,
            exists: true,
            isActive: true
        });

        usernameToWallet[unameHash] = msg.sender;

        emit UserRegistered(msg.sender, username);
    }

    // --------------------------------------------------
    // LOOKUP
    // --------------------------------------------------

    function getWalletByUsername(string calldata username)
        external
        view
        returns (address)
    {
        return usernameToWallet[keccak256(abi.encodePacked(username))];
    }

    function getUser(address user)
        external
        view
        returns (User memory)
    {
        require(users[user].exists, "User not found");
        return users[user];
    }

    // --------------------------------------------------
    // ACTIVITY
    // --------------------------------------------------

    function updateActivity(address user) external {

        require(users[user].exists, "User not found");

        require(
            msg.sender == user ||
            msg.sender == tradingProtocol ||
            msg.sender == portfolioManager,
            "Unauthorized"
        );

        users[user].lastActive = block.timestamp;

        emit UserActivityUpdated(user, block.timestamp);
    }

    function recordTrade(address user, bool success) external {

        require(users[user].exists, "User not found");
        require(msg.sender == tradingProtocol, "Only protocol");

        users[user].totalTrades++;

        if (success) {
            users[user].successfulTrades++;
        }

        emit TradeRecorded(user, success);
    }

    // --------------------------------------------------
    // METRICS
    // --------------------------------------------------

    function _getWinRate(address user)
        internal
        view
        returns (uint256)
    {
        User memory u = users[user];

        if (u.totalTrades == 0) return 0;

        return (u.successfulTrades * 100) / u.totalTrades;
    }

    function getWinRate(address user)
        external
        view
        returns (uint256)
    {
        return _getWinRate(user);
    }

    function getUserMetrics(address user)
        external
        view
        returns (
            uint256 portfolioValue,
            int256 pnl,
            uint256 riskScore,
            uint256 winRate
        )
    {
        require(users[user].exists, "User not found");

        Portfolio memory p = portfolios[user];

        portfolioValue = p.totalValue;
        pnl = p.pnl;              // ✅ Correct field
        riskScore = p.riskScore;
        winRate = _getWinRate(user);  // ✅ No external call
    }

    // --------------------------------------------------
    // RECOVERY (STRICT)
    // --------------------------------------------------

    function verifyRecovery(
        string calldata username,
        bytes32 privateKeyHash
    )
        external
        returns (bool)
    {
        bytes32 unameHash = keccak256(abi.encodePacked(username));
        address userAddr = usernameToWallet[unameHash];

        require(userAddr != address(0), "User not found");

        User storage user = users[userAddr];

        bool valid = (user.privateKeyHash == privateKeyHash);

        if (valid) {
            user.lastActive = block.timestamp;
            emit RecoveryValidated(userAddr);
        }

        return valid;
    }

    // --------------------------------------------------
    // ACCOUNT CONTROL
    // --------------------------------------------------

    function deactivateAccount() external {
        require(users[msg.sender].exists, "Not registered");
        users[msg.sender].isActive = false;
    }

    function activateAccount() external {
        require(users[msg.sender].exists, "Not registered");
        users[msg.sender].isActive = true;
    }
}