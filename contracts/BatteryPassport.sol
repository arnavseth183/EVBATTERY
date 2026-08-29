// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title BatteryPassport
 * @dev Main contract for EV Battery Passport management
 * Stores battery lifecycle data and provides query functionality
 */
contract BatteryPassport {

    // --------------------------------------------------
    // STRUCTS
    // --------------------------------------------------

    struct BatteryData {
        string passportId;
        string manufacturer;
        string batteryType;
        uint256 capacityKwh;
        string productionDate;
        uint256 soh; // State of Health (0-100)
        uint256 soc; // State of Charge (0-100)
        uint256 totalCycles;
        uint256 temperatureCelsius;
        string healthStatus;
        string temperatureStatus;
        uint256 degradationPerCycle;
        string dataSource;
        address owner;
        uint256 createdAt;
        uint256 updatedAt;
        bool isActive;
        bool blockchainRegistered;
    }

    struct HealthRecord {
        string passportId;
        uint256 soh;
        uint256 soc;
        uint256 temperatureCelsius;
        uint256 timestamp;
        address recordedBy;
    }

    // --------------------------------------------------
    // STORAGE
    // --------------------------------------------------

    mapping(string => BatteryData) public batteries;
    mapping(string => HealthRecord[]) public healthHistory;
    
    string[] public passportIds;
    
    address public userRegistry;
    address public admin;

    // --------------------------------------------------
    // EVENTS
    // --------------------------------------------------

    event BatteryRegistered(
        string indexed passportId,
        address indexed owner,
        string manufacturer,
        string batteryType
    );
    
    event BatteryUpdated(
        string indexed passportId,
        address indexed owner,
        uint256 timestamp
    );
    
    event HealthRecorded(
        string indexed passportId,
        uint256 soh,
        uint256 soc,
        uint256 timestamp
    );
    
    event BatteryDeactivated(
        string indexed passportId,
        address indexed owner
    );

    // --------------------------------------------------
    // MODIFIERS
    // --------------------------------------------------

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin");
        _;
    }

    modifier onlyOwner(string memory passportId) {
        require(batteries[passportId].owner == msg.sender, "Not owner");
        _;
    }

    modifier onlyRegisteredUser() {
        // This would check with UserRegistry
        _;
    }

    // --------------------------------------------------
    // CONSTRUCTOR
    // --------------------------------------------------

    constructor(address _userRegistry) {
        admin = msg.sender;
        userRegistry = _userRegistry;
    }

    // --------------------------------------------------
    // ADMIN FUNCTIONS
    // --------------------------------------------------

    function setUserRegistry(address _userRegistry) external onlyAdmin {
        userRegistry = _userRegistry;
    }

    function updateAdmin(address newAdmin) external onlyAdmin {
        admin = newAdmin;
    }

    // --------------------------------------------------
    // BATTERY REGISTRATION
    // --------------------------------------------------

    function registerBattery(
        string calldata passportId,
        string calldata manufacturer,
        string calldata batteryType,
        uint256 capacityKwh,
        string calldata productionDate,
        uint256 soh,
        uint256 soc,
        uint256 totalCycles,
        uint256 temperatureCelsius,
        string calldata dataSource
    ) external onlyRegisteredUser returns (bool) {
        require(bytes(passportId).length > 0, "Invalid passport ID");
        require(!batteries[passportId].isActive, "Battery already registered");

        // Calculate health status
        string memory healthStatus = _calculateHealthStatus(soh);
        string memory temperatureStatus = _calculateTemperatureStatus(temperatureCelsius);
        
        // Calculate degradation rate
        uint256 degradationRate = totalCycles > 0 ? (100 - soh) * 100 / totalCycles : 0;

        batteries[passportId] = BatteryData({
            passportId: passportId,
            manufacturer: manufacturer,
            batteryType: batteryType,
            capacityKwh: capacityKwh,
            productionDate: productionDate,
            soh: soh,
            soc: soc,
            totalCycles: totalCycles,
            temperatureCelsius: temperatureCelsius,
            healthStatus: healthStatus,
            temperatureStatus: temperatureStatus,
            degradationPerCycle: degradationRate,
            dataSource: dataSource,
            owner: msg.sender,
            createdAt: block.timestamp,
            updatedAt: block.timestamp,
            isActive: true,
            blockchainRegistered: true
        });

        passportIds.push(passportId);

        emit BatteryRegistered(passportId, msg.sender, manufacturer, batteryType);

        return true;
    }

    // --------------------------------------------------
    // BATTERY UPDATE
    // --------------------------------------------------

    function updateBatteryHealth(
        string calldata passportId,
        uint256 soh,
        uint256 soc,
        uint256 totalCycles,
        uint256 temperatureCelsius
    ) external onlyOwner(passportId) returns (bool) {
        require(batteries[passportId].isActive, "Battery not active");

        BatteryData storage battery = batteries[passportId];

        // Update health data
        battery.soh = soh;
        battery.soc = soc;
        battery.totalCycles = totalCycles;
        battery.temperatureCelsius = temperatureCelsius;
        battery.healthStatus = _calculateHealthStatus(soh);
        battery.temperatureStatus = _calculateTemperatureStatus(temperatureCelsius);
        battery.degradationPerCycle = totalCycles > 0 ? (100 - soh) * 100 / totalCycles : 0;
        battery.updatedAt = block.timestamp;

        // Record health history
        healthHistory[passportId].push(HealthRecord({
            passportId: passportId,
            soh: soh,
            soc: soc,
            temperatureCelsius: temperatureCelsius,
            timestamp: block.timestamp,
            recordedBy: msg.sender
        }));

        emit BatteryUpdated(passportId, msg.sender, block.timestamp);
        emit HealthRecorded(passportId, soh, soc, block.timestamp);

        return true;
    }

    // --------------------------------------------------
    // BATTERY QUERY
    // --------------------------------------------------

    function getBattery(string calldata passportId) 
        external 
        view 
        returns (BatteryData memory) 
    {
        require(batteries[passportId].isActive, "Battery not found");
        return batteries[passportId];
    }

    function getBatteryByOwner(address owner) 
        external 
        view 
        returns (BatteryData[] memory) 
    {
        uint256 count = 0;
        
        // First count
        for (uint256 i = 0; i < passportIds.length; i++) {
            if (batteries[passportIds[i]].owner == owner && batteries[passportIds[i]].isActive) {
                count++;
            }
        }
        
        // Then collect
        BatteryData[] memory ownerBatteries = new BatteryData[](count);
        uint256 index = 0;
        
        for (uint256 i = 0; i < passportIds.length; i++) {
            if (batteries[passportIds[i]].owner == owner && batteries[passportIds[i]].isActive) {
                ownerBatteries[index] = batteries[passportIds[i]];
                index++;
            }
        }
        
        return ownerBatteries;
    }

    function getAllBatteries() external view returns (BatteryData[] memory) {
        BatteryData[] memory allBatteries = new BatteryData[](passportIds.length);
        
        for (uint256 i = 0; i < passportIds.length; i++) {
            allBatteries[i] = batteries[passportIds[i]];
        }
        
        return allBatteries;
    }

    function getHealthHistory(string calldata passportId) 
        external 
        view 
        returns (HealthRecord[] memory) 
    {
        return healthHistory[passportId];
    }

    // --------------------------------------------------
    // BATTERY DEACTIVATION
    // --------------------------------------------------

    function deactivateBattery(string calldata passportId) external onlyOwner(passportId) {
        require(batteries[passportId].isActive, "Battery not active");
        
        batteries[passportId].isActive = false;
        batteries[passportId].updatedAt = block.timestamp;
        
        emit BatteryDeactivated(passportId, msg.sender);
    }

    // --------------------------------------------------
    // UTILITY FUNCTIONS
    // --------------------------------------------------

    function _calculateHealthStatus(uint256 soh) internal pure returns (string memory) {
        if (soh >= 90) return "EXCELLENT";
        if (soh >= 80) return "GOOD";
        if (soh >= 70) return "FAIR";
        if (soh >= 60) return "DEGRADED";
        return "POOR";
    }

    function _calculateTemperatureStatus(uint256 temperature) internal pure returns (string memory) {
        if (temperature >= 15 && temperature <= 35) return "OPTIMAL";
        if (temperature <= 50) return "WARNING";
        return "CRITICAL";
    }

    function getBatteryCount() external view returns (uint256) {
        return passportIds.length;
    }

    function getActiveBatteryCount() external view returns (uint256) {
        uint256 count = 0;
        for (uint256 i = 0; i < passportIds.length; i++) {
            if (batteries[passportIds[i]].isActive) {
                count++;
            }
        }
        return count;
    }
}
