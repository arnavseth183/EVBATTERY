// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title BatteryUserRegistry
 * @dev Registry for EV Battery Passport system users
 * Manages user accounts for battery passport operations
 */
contract BatteryUserRegistry {

    // --------------------------------------------------
    // STRUCT
    // --------------------------------------------------

    struct BatteryUser {
        address wallet;
        bytes32 usernameHash;
        bytes32 privateKeyHash;
        
        uint256 createdAt;
        uint256 lastActive;
        
        uint256 totalBatteries;
        uint256 activeBatteries;
        
        bool exists;
        bool isActive;
    }

    // --------------------------------------------------
    // STORAGE
    // --------------------------------------------------

    mapping(address => BatteryUser) public users;
    mapping(bytes32 => address) public usernameToWallet;
    
    address public batteryPassportContract;
    address public admin;

    // --------------------------------------------------
    // EVENTS
    // --------------------------------------------------

    event UserRegistered(address indexed user, string username);
    event UserActivityUpdated(address indexed user, uint256 timestamp);
    event BatteryRegistered(address indexed user, string passportId);
    event RecoveryValidated(address indexed user);
    event AdminUpdated(address indexed oldAdmin, address indexed newAdmin);

    // --------------------------------------------------
    // MODIFIER
    // --------------------------------------------------

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin");
        _;
    }

    modifier onlyAuthorized() {
        require(
            msg.sender == admin || 
            msg.sender == batteryPassportContract,
            "Unauthorized"
        );
        _;
    }

    // --------------------------------------------------
    // CONSTRUCTOR
    // --------------------------------------------------

    constructor() {
        admin = msg.sender;
    }

    // --------------------------------------------------
    // ADMIN FUNCTIONS
    // --------------------------------------------------

    function setBatteryPassportContract(address _batteryPassportContract) external onlyAdmin {
        batteryPassportContract = _batteryPassportContract;
    }

    function updateAdmin(address newAdmin) external onlyAdmin {
        address oldAdmin = admin;
        admin = newAdmin;
        emit AdminUpdated(oldAdmin, newAdmin);
    }

    // --------------------------------------------------
    // USER REGISTRATION
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

        users[msg.sender] = BatteryUser({
            wallet: msg.sender,
            usernameHash: unameHash,
            privateKeyHash: privateKeyHash,
            createdAt: block.timestamp,
            lastActive: block.timestamp,
            totalBatteries: 0,
            activeBatteries: 0,
            exists: true,
            isActive: true
        });

        usernameToWallet[unameHash] = msg.sender;

        emit UserRegistered(msg.sender, username);
    }

    // --------------------------------------------------
    // USER LOOKUP
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
        returns (BatteryUser memory)
    {
        require(users[user].exists, "User not found");
        return users[user];
    }

    // --------------------------------------------------
    // ACTIVITY TRACKING
    // --------------------------------------------------

    function updateActivity(address user) external onlyAuthorized {
        require(users[user].exists, "User not found");
        users[user].lastActive = block.timestamp;
        emit UserActivityUpdated(user, block.timestamp);
    }

    function recordBatteryRegistration(address user, string calldata passportId) external {
        require(users[user].exists, "User not found");
        require(msg.sender == batteryPassportContract, "Only battery passport contract");

        users[user].totalBatteries++;
        users[user].activeBatteries++;
        users[user].lastActive = block.timestamp;

        emit BatteryRegistered(user, passportId);
    }

    function recordBatteryDeactivation(address user) external {
        require(users[user].exists, "User not found");
        require(msg.sender == batteryPassportContract, "Only battery passport contract");
        require(users[user].activeBatteries > 0, "No active batteries");

        users[user].activeBatteries--;
        users[user].lastActive = block.timestamp;
    }

    // --------------------------------------------------
    // USER METRICS
    // --------------------------------------------------

    function getUserBatteryCount(address user)
        external
        view
        returns (uint256 total, uint256 active)
    {
        require(users[user].exists, "User not found");
        return (users[user].totalBatteries, users[user].activeBatteries);
    }

    function getUserStats(address user)
        external
        view
        returns (
            uint256 totalBatteries,
            uint256 activeBatteries,
            uint256 accountAge,
            uint256 lastActive
        )
    {
        require(users[user].exists, "User not found");
        
        BatteryUser memory u = users[user];
        
        return (
            u.totalBatteries,
            u.activeBatteries,
            block.timestamp - u.createdAt,
            u.lastActive
        );
    }

    // --------------------------------------------------
    // ACCOUNT RECOVERY
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

        BatteryUser storage user = users[userAddr];

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

    // --------------------------------------------------
    // ADMIN USER MANAGEMENT
    // --------------------------------------------------

    function forceDeactivateUser(address user) external onlyAdmin {
        require(users[user].exists, "User not found");
        users[user].isActive = false;
    }

    function forceActivateUser(address user) external onlyAdmin {
        require(users[user].exists, "User not found");
        users[user].isActive = true;
    }
}
